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
BASE_MEALS = [
    "Poha", "Upma", "Aloo Paratha", "Methi Paratha", "Moong Dal Cheela",
    "Dalia", "Vegetable Sandwich", "Paneer Butter Masala", "Mix Veg", 
    "Chole Bhature", "Rajasthani Gatte ki Sabji", "Ker Sangri", "Sev Tamatar", 
    "Malai Kofta", "Palak Paneer", "Kadhi Pakora", "Veg Pulao", "Mango Shake", 
    "Papaya", "Orange", "Kharbooza/Muskmelon", "Watermelon", "Daal", "Baati",
    "Kadi", "Bharwa Shima Mirch", "Loki", "Daal Dhokli", "Gatte", "Stuff Tomato",
    "Fried Rice", "Aalo Pyaaz", "Pao Bhaaji", "Veg and Aalo Sandwich", "Besan Chilaa",
    "Aaloo Tamatar", "Idli Shambar", "Malaai Pyaaz", "Sahi Paneer", "Loki ke Kofte",
    "Aaloo Bhuna", "Chole"
]

STAPLES = ["Roti", "Chawal", "Salad"]

# File to store user suggestions
SUGGESTIONS_FILE = "user_suggestions.json"

def load_user_suggestions():
    """Load user suggestions from JSON file."""
    if os.path.exists(SUGGESTIONS_FILE):
        with open(SUGGESTIONS_FILE, 'r') as f:
            return json.load(f)
    return {"meals": [], "portions": {}}

def save_user_suggestions(suggestions):
    """Save user suggestions to JSON file."""
    with open(SUGGESTIONS_FILE, 'w') as f:
        json.dump(suggestions, f)

def get_all_meal_options():
    """Get all meal options including user suggestions."""
    suggestions = load_user_suggestions()
    all_meals = sorted(list(set(BASE_MEALS + suggestions["meals"])))
    return all_meals

def format_quantity(quantity, item):
    """Format quantity based on item type, removing .0 for integers."""
    try:
        qty = float(quantity)
        # Format whole numbers as integers
        if qty == int(qty):
            qty_str = str(int(qty))
        else:
            qty_str = str(qty)

        if item == "Protein Shake" or item == "Chach":
            return f"{qty_str} glass"
        elif item == "Chawal":
            return f"{qty_str} log ke liye"
        elif item == "Roti":
            return f"({qty_str} Total)"
        elif item == "Salad":
            return "" # No quantity for salad
        elif item in get_all_meal_options(): # Assume it's a main dish
             return f"{qty_str} log ke liye"
        else: # Default/Fallback for staples or others not explicitly handled
            return f"{qty_str} plate/portion"
    except ValueError:
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
    
    # Get quantities/portions
    main_dish_portions = {}
    staple_quantities = {}
    protein_chach_quantities = {}

    suggestions = load_user_suggestions()
    for dish in selected_mains:
        portion = request.form.get(f'portion_{dish}', '1') # Get portion for this specific dish
        main_dish_portions[dish] = portion
        suggestions["portions"][dish] = portion # Save portion per dish
    save_user_suggestions(suggestions)
    
    for staple in STAPLES:
        # Only get quantity if staple is selected
        if staple in selected_staples:
            qty = request.form.get(f'staple_qty_{staple}', '1')
            staple_quantities[staple] = qty
            
    for item in PROTEIN_AND_CHACH:
        # Only get quantity if item is selected
        if item in selected_protein_chach:
            qty = request.form.get(f'protein_chach_qty_{item}', '1')
            protein_chach_quantities[item] = qty
    
    # --- Combine and Generate Message ---
    final_meal_list = []
    
    # Add protein and chach if selected
    final_meal_list.extend(selected_protein_chach)
    
    # Add main dishes and staples
    final_meal_list.extend(sorted(selected_mains))
    final_meal_list.extend(sorted(selected_staples))

    message_lines = []
    message_lines.append("Namaste Bhaiya!")
    message_lines.append(f"\nKripya {meal_type.capitalize()} ke liye yeh tayyar kar dijiye:")

    if not final_meal_list: 
        message_lines.append("- Kuch bhi nahi!") 
    else:
        processed_items = set() # To avoid duplicates if an item is in multiple lists
        for item in final_meal_list:
            if item in processed_items:
                continue
                
            if item in selected_mains:
                qty = format_quantity(main_dish_portions.get(item, '1'), item)
                message_lines.append(f"- {item} ({qty})")
            elif item in selected_staples:
                # Get quantity only if staple was selected and has quantity
                if item in staple_quantities:
                    qty = format_quantity(staple_quantities[item], item)
                    if qty: # Format Roti correctly, handle Salad
                       message_lines.append(f"- {item} {qty if item == 'Roti' else '('+qty+')'}")
                    else:
                       message_lines.append(f"- {item}")
                else: # Handle Salad (no quantity)
                    message_lines.append(f"- {item}")
            elif item in selected_protein_chach:
                qty = format_quantity(protein_chach_quantities.get(item, '1'), item)
                message_lines.append(f"- {item} ({qty})")
            
            processed_items.add(item)

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
        if new_meal not in suggestions["meals"]:
            suggestions["meals"].append(new_meal)
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