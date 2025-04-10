from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import datetime
import os # For secret key
import json
from pathlib import Path

app = Flask(__name__)
# Set a secret key for session management.
# Use environment variable in production, fallback for local dev.
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# --- Translation Dictionary ---
TRANSLATIONS = {
    "Protein Shake": "প্রোটিন শেক (प्रोटीन शेक)",
    "Chach": "ছাঁচ (छाछ)",
    "Poha": "পোহা (पोहा)",
    "Upma": "উপমা (उपमा)", 
    "Dalia": "দালিয়া (दलिया)", 
    "Paneer Butter Masala": "পনির বাটার মসলা (पनीर बटर मसाला)", 
    "Mix Veg": "মিক্স ভেজ (मिक्स वेज)",
    "Ker Sangri": "কের সাঙরি (केर सांगरी)", 
    "Sev Tamatar": "সেভ টমেটো (सेव टमाटर)", 
    "Malai Kofta": "মালাই কোফতা (मलाई कोफ्ता)", 
    "Palak Paneer": "পালক পনির (पालक पनीर)", 
    "Kadhi Pakora": "কড়ি পকোড়া (कढ़ी पकोड़ा)", 
    "Veg Pulao": "ভেজ পুলাও (वेज पुलाव)", 
    "Daal": "ডাল (दाल)", 
    "Kadi": "কড়ি (कड़ी)", 
    "Bharwa Shima Mirch": "ভরওয়া শিমলা মির্চ (भरवा शिमला मिर्च)", 
    "Loki": "লাউ (लौकी)", 
    "Daal Dhokli": "ডাল ঢোকলি (दाल ढोकली)", 
    "Gatte": "গট্টে (गट्टे)", 
    "Stuff Tomato": "স্টাফড টমেটো (स्टफ्ड टमाटर)",
    "Fried Rice": "ফ্রাইড রাইস (फ्राइड राइस)", 
    "Aalo Pyaaz": "আলু পেঁয়াজ (आलू प्याज़)", 
    "Pao Bhaaji": "পাও ভাজি (पाव भाजी)", 
    "Aaloo Tamatar": "আলু টমেটো (आलू टमाटर)", 
    "Idli Shambar": "ইডলি সাম্বার (इडली सांबर)", 
    "Malaai Pyaaz": "মালাই পেঁয়াজ (मलाई प्याज़)", 
    "Sahi Paneer": "শাহী পনির (शाही पनीर)", 
    "Loki ke Kofte": "লাউয়ের কোফতা (लौकी के कोफ्ते)",
    "Aaloo Bhuna": "আলু ভুনা (आलू भुना)", 
    "Chole": "ছোলে (छोले)",
    "Chawal": "চাওয়াল (चावल)", 
    "Panchmel Dal": "পঞ্চমেল ডাল (पंचमेल दाल)", 
    "Papad ki Sabji": "পাপড়ের সবজি (पापड़ की सब्ज़ी)", 
    "Govind Gatta": "গোবিন্দ গট্টে (गोविंद गट्टे)",
    "Roti": "রুটি (रोटी)", 
    "Salad": "সালাদ (सलाद)", 
    "Aloo Paratha": "আলু পরোটা (आलू पराठा)", 
    "Methi Paratha": "মেথি পরোটা (मेथी पराठा)", 
    "Moong Dal Cheela": "মুগ ডাল চিলা (मूंग दाल चीला)", 
    "Besan Chilaa": "বেসন চিলা (बेसन चीला)", 
    "Aalo Sandwich": "আলু স্যান্ডউইচ (आलू सैंडविच)",
    "Vegetable Sandwich": "ভেজিটেবল স্যান্ডউইচ (वेजिटेबल सैंडविच)", 
    "Papaya": "পেঁপে (पपीता)", 
    "Orange": "কমলা (संतरा)", 
    "Kharbooza/Muskmelon": "খারবুজা (खरबूजा)", 
    "Watermelon": "তরমুজ (तरबूज)", 
    "Baati": "বাতি (बाटी)",
    "Churma": "চুরমা (चूरमा)", 
    "Bajra Roti": "বাজরা রুটি (बाजरा रोटी)", 
    "Makki ki Roti": "ভূট্টার রুটি (मक्की की रोटी)",
    "Bhatoora": "ভাটুরা (भटूरा)", 
    "Mango Shake": "আম শেক (आम शेक)",
    "Chana Mix Ubaal Dena & Pyaaz Tamatar Cut Kr dena": "ছোলা মিক্স সেদ্ধ করে পেঁয়াজ ও টমেটো কেটে দিন (छोला मिक्स उबाल कर प्याज़ और टमाटर काट दीजिए)",
    "Jeera Rice": "জিরা রাইস (जीरा राइस)",
    "Daal Makhani": "ডাল মাখনি (दाल मखनी)",
    "Besan Mirch": "বেসন মির্চ (बेसन मिर्च)",
    "Stuffed Shimla Mirch": "স্টাফড শিমলা মির্চ (स्टफ्ड शिमला मिर्च)"
}

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
    #"Moong Dal Halwa", "Malpua", "Ghevar",
    # Adding missing items
    "Jeera Rice", "Daal Makhani", "Besan Mirch", "Stuffed Shimla Mirch"
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
    "Bhatoora", "Mango Shake", "Chana Mix Ubaal Dena & Pyaaz Tamatar Cut Kr dena"
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
    """Format quantity based on item type, removing .0 for integers and bolding for WhatsApp."""
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
        prep_items = ["Chana Mix Ubaal Dena & Pyaaz Tamatar Cut Kr dena"]

        # Bold the quantity for WhatsApp using asterisks
        if item in glass_items:
            return f"*{qty_str}* গ্লাস (*{qty_str}* गिलास)"
        elif item in prep_items:
            qty_disp = "১/২" if qty == 0.5 else qty_str
            return f"*{qty_disp}* বার (*{qty_disp}* बार)"
        elif item == "Chawal" or item in get_all_meal_options(): # Main dishes + Chawal
            return f"*{qty_str}* জনের জন্য (*{qty_str}* लोगों के लिए)"
        elif item in total_format_items:
            return f"(*{qty_str}* মোট) (*{qty_str}* कुल)"
        elif item == "Churma":
            return f"*{qty_str}* পরিবেশন (*{qty_str}* सर्विंग)"
        elif item in plate_portion_items:
            return f"*{qty_str}* প্লেট/অংশ (*{qty_str}* प्लेट/हिस्सा)"
        elif item == "Salad":
            return "" # No quantity for salad
        else: # Default/Fallback for any other staples
            return f"*{qty_str}* প্লেট/অংশ (*{qty_str}* प्लेट/हिस्सा)"
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
                         title="আজ কি বানাবেন? (आज क्या बनेगा?)",
                         options=options, 
                         staples=STAPLES, 
                         protein_and_chach=PROTEIN_AND_CHACH,
                         translations=TRANSLATIONS)

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
    
    # --- Combine and Prepare Items by Category ---
    protein_chach_items = []
    main_items = []
    staple_items = []
    
    # Bengali messages with Hindi translations in brackets
    meal_type_bengali = "লাঞ্চ" if meal_type == "lunch" else "ডিনার"
    meal_type_hindi = "लंच" if meal_type == "lunch" else "डिनर"

    # Process protein and chach items
    for item in selected_protein_chach:
        item_name = TRANSLATIONS.get(item, item)
        qty_str = format_quantity(protein_chach_quantities.get(item, '1'), item)
        protein_chach_items.append(f"- *{item_name}* {qty_str}")
    
    # Process main dishes
    for item in selected_mains:
        item_name = TRANSLATIONS.get(item, item)
        qty_str = format_quantity(main_dish_portions.get(item, '1'), item)
        main_items.append(f"- *{item_name}* {qty_str}")
    
    # Process staples
    for item in selected_staples:
        item_name = TRANSLATIONS.get(item, item)
        if item == "Salad":
            staple_items.append(f"- *{item_name}*")
        else:
            qty_str = format_quantity(staple_quantities.get(item, '1'), item)
            if item in ["Roti", "Aloo Paratha", "Methi Paratha", "Moong Dal Cheela", 
                        "Besan Chilaa", "Aalo Sandwich", "Vegetable Sandwich", 
                        "Baati", "Bajra Roti", "Makki ki Roti", "Bhatoora"]:
                staple_items.append(f"- *{item_name}* {qty_str}")
            else:
                staple_items.append(f"- *{item_name}* {qty_str}")
    
    # --- Generate Final Message ---
    message_lines = []
    
    # ===== SECTION 1: GREETING =====
    message_lines.append("*নমস্কার ভাইয়া!* (*नमस्कार भैया!*)")
    message_lines.append("")
    message_lines.append("----------------------------------------")
    message_lines.append("")
    
    # ===== SECTION 2: MEAL ITEMS =====
    message_lines.append(f"দয়া করে {meal_type_bengali}-এর জন্য এইগুলি তৈরি করুন: ({meal_type_hindi} के लिए कृपया यह तैयार कर दीजिए:)")
    message_lines.append("")
    
    # Add protein and chach items without header
    if protein_chach_items:
        message_lines.extend(protein_chach_items)
        message_lines.append("")  # Add space between categories
    
    # Add main items without header
    if main_items:
        message_lines.extend(main_items)
        message_lines.append("")  # Add space between categories
    
    # Add staples without header
    if staple_items:
        message_lines.extend(staple_items)
    
    # Add custom request if any
    if custom_request:
        message_lines.append("")
        message_lines.append("*আরেকটি জিনিস:* (*एक और बात:*)")
        message_lines.append(custom_request)

    # Add separator before closing
    message_lines.append("")
    message_lines.append("----------------------------------------")
    message_lines.append("")
    
    # ===== SECTION 3: CLOSING =====
    message_lines.append("*ধন্যবাদ!* (*धन्यवाद!*)")
    
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