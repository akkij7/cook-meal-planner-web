from flask import Flask, render_template, request, session, redirect, url_for
import datetime
import os # For secret key

app = Flask(__name__)
# Set a secret key for session management.
# Use environment variable in production, fallback for local dev.
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# --- Meal Data (Copied from Tkinter version) ---
meal_history_text = """
Mor: Protein Shake, Chach, Watermellon
Eve: Daal, baati
Mor: Protein Shake, Chach, Kadi, chawal, roti
Eve: Bharwa Shima Mirch, roti
Mor: Protein Shake, Chach, Loki, roti
Eve: Daal dhokli
Mor: Protein Shake, Chach, gatte, roti
Eve: Daal, chaaval
Mor: Protein Shake, Chach, stuff tomato, roti
Eve: fried rice
Mor: Protein Shake, Chach, daal, roti
Eve: aalo pyaaz, roti
Mor: Protein Shake, Chach, pao bhaaji
Eve: veg and aalo sandwich
Mor: Protein Shake, Chach, besan chilaa
Eve: aaloo tamatar, roti
Mor: Protein Shake, Chach, idli shambar
Eve: malaai pyaaz, roti
Mor: Protein Shake, Chach, sahi paneer, roti
Eve: Loki ke kofte, roti
Mor: Protein Shake, Chach, aaloo bhuna, roti
Eve: chole, roti
"""

MANDATORY_LUNCH = ["Protein Shake", "Chach"]
STAPLES = ["Roti", "Chawal", "Salad"]
NEW_OPTIONS = ["Mango Shake", "Papaya", "Orange", "Kharbooza/Muskmelon"]

def parse_meals(history_text):
    """Parses the meal history text into separate lists of unique main dishes for lunch and dinner."""
    lunch_meals_history = set()
    dinner_meals_history = set()
    mandatory_lower = {item.lower() for item in MANDATORY_LUNCH}
    staples_lower = {item.lower() for item in STAPLES}

    lines = history_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        
        time_marker = ""
        if line.startswith("Mor:"):
            time_marker = "Lunch"
        elif line.startswith("Eve:"):
            time_marker = "Dinner"
        else:
            continue

        original_marker = "Mor:" if time_marker == "Lunch" else "Eve:"
        raw_dishes = [d.strip() for d in line.replace(original_marker, "").strip().split(',')]
        
        for dish in raw_dishes:
            if not dish: continue
            dish_lower = dish.lower()
            is_mandatory = time_marker == "Lunch" and dish_lower in mandatory_lower
            is_staple = dish_lower in staples_lower
            
            if not is_mandatory and not is_staple:
                capitalized_dish = ' '.join(word.capitalize() for word in dish.split())
                if time_marker == "Lunch":
                    lunch_meals_history.add(capitalized_dish)
                else:
                    dinner_meals_history.add(capitalized_dish)
                
    return sorted(list(lunch_meals_history)), sorted(list(dinner_meals_history))

# --- Generate Meal Lists ---
historical_lunch_mains, historical_dinner_mains = parse_meals(meal_history_text)

suggested_lunch_mains = [
    "Poha", "Upma", "Aloo Paratha", "Methi Paratha", "Moong Dal Cheela",
    "Dalia", "Vegetable Sandwich"
] + NEW_OPTIONS

suggested_dinner_mains = [
    "Paneer Butter Masala", "Mix Veg", "Chole Bhature", 
    "Rajasthani Gatte ki Sabji", "Ker Sangri", "Sev Tamatar", 
    "Malai Kofta", "Palak Paneer", "Kadhi Pakora", "Veg Pulao"
] + NEW_OPTIONS

all_lunch_options = sorted(list(set(suggested_lunch_mains + historical_lunch_mains)))
all_dinner_options = sorted(list(set(suggested_dinner_mains + historical_dinner_mains)))

# --- Flask Routes ---

@app.route('/')
def index():
    """Displays the initial choice page."""
    # Clear any previous meal mode from session
    session.pop('meal_mode', None) 
    return render_template('index.html')

@app.route('/plan', methods=['POST'])
def plan_meal():
    """Sets the meal mode (Lunch/Dinner) and shows the planning form."""
    meal_mode = request.form.get('meal_mode') # Should be 'Lunch' or 'Dinner'
    if meal_mode not in ['Lunch', 'Dinner']:
        # Handle invalid mode - redirect back to index or show error
        return redirect(url_for('index')) 

    session['meal_mode'] = meal_mode # Store mode in session

    if meal_mode == 'Lunch':
        options = all_lunch_options
        title = "Aaj Lunch Mein Kya Banega?"
        mandatory = MANDATORY_LUNCH
    else: # Dinner
        options = all_dinner_options
        title = "Aaj Dinner Mein Kya Banega?"
        mandatory = [] # No mandatory items for dinner

    return render_template('plan.html', 
                           title=title, 
                           options=options, 
                           staples=STAPLES, 
                           mandatory=mandatory,
                           meal_mode=meal_mode) # Pass mode for context if needed in template

@app.route('/generate', methods=['POST'])
def generate_message():
    """Generates the meal message based on form submission."""
    meal_mode = session.get('meal_mode')
    if not meal_mode:
         # If session expired or invalid access, redirect home
         return redirect(url_for('index'))

    selected_mains = request.form.getlist('main_dish') # Checkboxes with same name come as list
    selected_staples = request.form.getlist('staple')
    custom_request = request.form.get('custom_request', '').strip()

    # --- Combine and Generate Message ---
    final_meal_list = []
    if meal_mode == 'Lunch':
        final_meal_list.extend(MANDATORY_LUNCH)
            
    final_meal_list.extend(sorted(selected_mains))
    final_meal_list.extend(sorted(selected_staples))

    # Basic validation: Ensure at least one main dish selected if not Lunch mode with only mandatory
    if not selected_mains and meal_mode == 'Dinner':
         # You might want to redirect back with an error message instead
         # For simplicity, just generate a message indicating nothing was chosen
         final_meal_list = ["(Koi main dish nahi chuna gaya)"] # Placeholder
    elif not selected_mains and not selected_staples and meal_mode == 'Lunch':
         # Only mandatory items if nothing else selected for lunch
         pass # final_meal_list already has mandatory items

    message_lines = []
    if meal_mode == 'Lunch':
        message_lines.append("Namaste Bhaiya!")
        message_lines.append("\nAaj lunch mein, kripya yeh bana dijiye:")
    else: # Dinner
        message_lines.append("Namaste Bhaiya!")
        message_lines.append("\nKripya aaj Dinner ke liye yeh tayyar kar dijiye:")

    if not final_meal_list: 
         message_lines.append("- Kuch bhi nahi!") 
    else:
        for item in final_meal_list:
             message_lines.append(f"- {item}")

    if custom_request:
        message_lines.append("\nEk aur baat:") 
        message_lines.append(custom_request)

    message_lines.append("\nShukriya!")
    final_message = "\n".join(message_lines)

    # Clear the mode from session after generating message
    # session.pop('meal_mode', None) 
    # Keep mode in session for now, in case user wants to go back/refresh result

    return render_template('result.html', meal_message=final_message)


if __name__ == '__main__':
    # Debug mode should be off in production (handled by WSGI server)
    # Use host='0.0.0.0' to be accessible externally if needed locally
    # Port is often set by host environment variable
    port = int(os.environ.get('PORT', 5000))
    # Use waitress or gunicorn in production, not app.run()
    # For local testing:
    app.run(host='0.0.0.0', port=port, debug=False) # Set debug=False when testing production-like setup 