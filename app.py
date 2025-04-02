from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import datetime
import os # For secret key
import json
from pathlib import Path

app = Flask(__name__)
# Set a secret key for session management.
# Use environment variable in production, fallback for local dev.
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# --- Meal Data ---
PROTEIN_AND_CHACH = ["Protein Shake", "Chach"]

# Base meal options that come with the app
BASE_MEALS = sorted([
    "Poha", "Upma", 
    "Dalia", 
    "Paneer Butter Masala", "Mix Veg", 
    #"Rajasthani Gatte ki Sabji", 
    "Ker Sangri", "Sev Tamatar", 
    "Malai Kofta", "Palak Paneer", "Kadhi Pakora", "Veg Pulao", #"Mango Shake", 
    "Daal", 
    "Kadi", "Bharwa Shima Mirch", "Loki", "Daal Dhokli", "Gatte", "Stuff Tomato",
    "Fried Rice", "Aalo Pyaaz", "Pao Bhaaji", 
    "Aaloo Tamatar", "Idli Shambar", "Malaai Pyaaz", "Sahi Paneer", "Loki ke Kofte",
    "Aaloo Bhuna", "Chole",
    "Chawal", 
    "Panchmel Dal", "Papad ki Sabji", "Govind Gatta", #"Aamras", 
    #"Moong Dal Halwa", "Malpua", "Ghevar"
])

STAPLES = sorted([
    "Roti", 
    "Salad", 
    "Aloo Paratha", "Methi Paratha", "Moong Dal Cheela", "Besan Chilaa", 
    "Aalo Sandwich",
    "Vegetable Sandwich", "Papaya", "Orange", "Kharbooza/Muskmelon", 
    "Watermelon", "Baati",
    "Churma", "Bajra Roti", "Makki ki Roti",
    # Newly added/moved
    "Bhatoora", "Mango Shake"
])

# File to store user suggestions
SUGGESTIONS_FILE = "user_suggestions.json"

def load_user_suggestions():
    """Load user suggestions from JSON file."""
    if os.path.exists(SUGGESTIONS_FILE):
        with open(SUGGESTIONS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                 return {"meals": [], "portions": {}} # Return empty if file is corrupted
    return {"meals": [], "portions": {}}

def save_user_suggestions(suggestions):
    """Save user suggestions to JSON file."""
    with open(SUGGESTIONS_FILE, 'w') as f:
        json.dump(suggestions, f)

def get_all_meal_options():
    """Get all meal options including user suggestions."""
    suggestions = load_user_suggestions()
    invalid_suggestions = set(STAPLES + PROTEIN_AND_CHACH)
    filtered_suggestions = [m for m in suggestions.get("meals", []) if m not in invalid_suggestions]
    all_meals = sorted(list(set(BASE_MEALS + filtered_suggestions)))
    return all_meals

def format_quantity(quantity, item):
    """Format quantity based on item type, removing .0 for integers."""
    try:
        qty = float(quantity)
        if qty == int(qty):
            qty_str = str(int(qty))
        else:
            qty_str = "1/2" if qty == 0.5 else str(qty)

        # Define formats for different categories
        total_format_items = ["Roti", "Aloo Paratha", "Methi Paratha", "Moong Dal Cheela", 
                              "Besan Chilaa", "Aalo Sandwich", "Vegetable Sandwich", 
                              "Baati", "Bajra Roti", "Makki ki Roti", "Bhatoora"]
        plate_portion_items = ["Papaya", "Orange", "Kharbooza/Muskmelon", "Watermelon"]
        glass_items = ["Protein Shake", "Chach", "Mango Shake"]

        if item in glass_items:
            return f"{qty_str} glass"
        elif item == "Chawal" or item in get_all_meal_options(): # Main dishes + Chawal
            return f"{qty_str} log ke liye"
        elif item in total_format_items:
            return f"({qty_str} Total)"
        elif item == "Churma":
             return f"{qty_str} serving"
        elif item in plate_portion_items:
            return f"{qty_str} plate/portion"
        elif item == "Salad":
            return "" # No quantity for salad
        else: # Default/Fallback for any other staples
            return f"{qty_str} plate/portion"
    except (ValueError, TypeError):
        return quantity # Return original if conversion fails

# --- Flask Routes ---

@app.route('/')
def index():
    """Displays the initial choice page."""
    return render_template('index.html')

@app.route('/plan', methods=['GET', 'POST'])
def plan_meal():
    """Shows the planning form."""
    options = get_all_meal_options()
    return render_template('plan.html', 
                         title="Aaj Kya Banega?",
                         options=options, 
                         staples=STAPLES, 
                         protein_and_chach=PROTEIN_AND_CHACH)

@app.route('/generate', methods=['POST'])
def generate_message():
    """Generates the meal message based on form submission."""
    selected_mains = request.form.getlist('main_dish')
    selected_staples = request.form.getlist('staple')
    selected_protein_chach = request.form.getlist('protein_chach')
    custom_request = request.form.get('custom_request', '').strip()
    meal_type = request.form.get('meal_type', 'lunch')
    
    main_dish_portions = {}
    staple_quantities = {}
    protein_chach_quantities = {}

    suggestions = load_user_suggestions()
    for dish in selected_mains:
        portion = request.form.get(f'portion_{dish}', '1')
        main_dish_portions[dish] = portion
        if dish in BASE_MEALS or dish in suggestions.get("meals", []):
             suggestions.setdefault("portions", {})[dish] = portion 
    save_user_suggestions(suggestions)
    
    for staple in STAPLES:
        if staple in selected_staples:
            qty = request.form.get(f'staple_qty_{staple}', '1')
            staple_quantities[staple] = qty
            
    for item in PROTEIN_AND_CHACH:
        if item in selected_protein_chach:
            qty = request.form.get(f'protein_chach_qty_{item}', '1')
            protein_chach_quantities[item] = qty
    
    # --- Combine and Generate Message ---
    all_selected_items = selected_protein_chach + selected_mains + selected_staples
    unique_ordered_items = list(dict.fromkeys(all_selected_items)) 

    message_lines = []
    message_lines.append("Namaste Bhaiya!")
    message_lines.append(f"\nKripya {meal_type.capitalize()} ke liye yeh tayyar kar dijiye:")

    if not unique_ordered_items: 
        message_lines.append("- Kuch bhi nahi!") 
    else:
        for item in unique_ordered_items:
            if item in selected_protein_chach:
                qty_str = format_quantity(protein_chach_quantities.get(item, '1'), item)
                message_lines.append(f"- {item} ({qty_str})")
            elif item in selected_mains:
                qty_str = format_quantity(main_dish_portions.get(item, '1'), item)
                message_lines.append(f"- {item} ({qty_str})")
            elif item in selected_staples:
                if item == "Salad":
                     message_lines.append(f"- {item}")
                elif item in staple_quantities:
                    qty_str = format_quantity(staple_quantities[item], item)
                    # Use specific format based on item type
                    if item in ["Roti", "Aloo Paratha", "Methi Paratha", "Moong Dal Cheela", 
                                "Besan Chilaa", "Aalo Sandwich", "Vegetable Sandwich", 
                                "Baati", "Bajra Roti", "Makki ki Roti", "Bhatoora"]:
                         message_lines.append(f"- {item} {qty_str}")
                    elif item in ["Mango Shake"]:
                         message_lines.append(f"- {item} ({qty_str})") # Use glass format
                    else:
                         message_lines.append(f"- {item} ({qty_str})") # Default staple format (plate/portion, serving)

    if custom_request:
        message_lines.append("\nEk aur baat:") 
        message_lines.append(custom_request)

    message_lines.append("\nShukriya!")
    final_message = "\n".join(message_lines)

    return render_template('result.html', meal_message=final_message)

@app.route('/add_suggestion', methods=['POST'])
def add_suggestion():
    """Add a new meal suggestion."""
    new_meal = request.form.get('new_meal', '').strip()
    if new_meal:
        suggestions = load_user_suggestions()
        invalid_new_meal = set(BASE_MEALS + STAPLES + PROTEIN_AND_CHACH)
        if new_meal not in invalid_new_meal and new_meal not in suggestions.get("meals", []):
            suggestions.setdefault("meals", []).append(new_meal)
            save_user_suggestions(suggestions)
    return redirect(url_for('plan_meal'))

if __name__ == '__main__':
    # Debug mode should be off in production (handled by WSGI server)
    # Use host='0.0.0.0' to be accessible externally if needed locally
    # Port is often set by host environment variable
    port = int(os.environ.get('PORT', 5000))
    # Use waitress or gunicorn in production, not app.run()
    # For local testing:
    app.run(host='0.0.0.0', port=port, debug=False) # Set debug=False when testing production-like setup 