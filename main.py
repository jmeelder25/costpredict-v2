import os
import datetime
from flask import Flask, render_template, request, jsonify, make_response
from weasyprint import HTML

app = Flask(__name__)

# --- THE GOLDEN 50 CATALOG ENGINE ---
def get_golden_catalog():
    return {
        "01-General-Requirements": [
            {"name": "Dumpster Rental (30 Yd)", "unit": "Weeks", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Site Protection / Ram Board", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "Low"},
            {"name": "Temporary Fencing", "unit": "Linear Ft.", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Scaffold Rental", "unit": "Days", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "03-Concrete": [
            {"name": "Ready Mix", "unit": "Cu. Yards", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Rebar", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Anchor Bolts", "unit": "Count", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Wire Mesh", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "Medium"}
        ],
        "04-Masonry": [
            {"name": "Brick", "unit": "Count", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "Block", "unit": "Count", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Mortar", "unit": "Bags", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "Stone Veneer", "unit": "Sq. Ft.", "default_waste": 12, "labor_difficulty": "High"}
        ],
        "05-Metals": [
            {"name": "Steel Beam", "unit": "Linear Ft.", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Metal Stud", "unit": "Count", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Track", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Decking", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "High"}
        ],
        "06-Rough-Carpentry": [
            {"name": "2x4 Studs", "unit": "Count", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "2x6 Joists", "unit": "Count", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "4x8 Plywood", "unit": "Sheets", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "OSB", "unit": "Sheets", "default_waste": 10, "labor_difficulty": "Medium"}
        ],
        "07-Thermal": [
            {"name": "R-13 Batt", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "R-30 Batt", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Rigid Foam", "unit": "Sheets", "default_waste": 8, "labor_difficulty": "Medium"},
            {"name": "Spray Foam", "unit": "Board Ft.", "default_waste": 10, "labor_difficulty": "High"}
        ],
        "08-Doors": [
            {"name": "Interior Door", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Exterior Door", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Door Frame", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Hinges", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "09-Drywall": [
            {"name": "Panel 4x8", "unit": "Sheets", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "Fire-Rated 5-8", "unit": "Sheets", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "Tape", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Compound", "unit": "Boxes", "default_waste": 10, "labor_difficulty": "Medium"}
        ],
        "10-Flooring": [
            {"name": "Hardwood", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "LVP", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Tile", "unit": "Sq. Ft.", "default_waste": 12, "labor_difficulty": "High"},
            {"name": "Laminate", "unit": "Sq. Ft.", "default_waste": 7, "labor_difficulty": "Medium"}
        ],
        "11-Equipment": [
            {"name": "Refrigerator", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Dishwasher", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Range", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Microwave", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "12-Cabinets": [
            {"name": "Wall 30in", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Base 36in", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Pantry", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Crown Molding", "unit": "Linear Ft.", "default_waste": 15, "labor_difficulty": "High"}
        ],
        "13-Countertops": [
            {"name": "Granite", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Quartz", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Laminate", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Butcher Block", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "High"}
        ],
        "21-Fire-Suppression": [
            {"name": "Sprinkler Head", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Piping", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "Control Valve", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Extinguisher", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "22-Plumbing": [
            {"name": "PEX Tubing", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "PVC Pipe", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Toilet", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Shower Valve", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"}
        ],
        "23-HVAC": [
            {"name": "Condenser", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Air Handler", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Thermostat", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Ductwork", "unit": "Linear Ft.", "default_waste": 12, "labor_difficulty": "High"}
        ],
        "25-Automation": [
            {"name": "Controller", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Sensor", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Hub", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Cable", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"}
        ],
        "26-Electrical": [
            {"name": "12-2 Romex", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Main Panel", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Outlets", "unit": "Count", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Can Lights", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "27-Communications": [
            {"name": "Cat6 Cable", "unit": "Linear Ft.", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "Coax Cable", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Router", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Patch Panel", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "31-Earthwork": [
            {"name": "Excavation", "unit": "Hours", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Grading", "unit": "Sq. Ft.", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Gravel", "unit": "Tons", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Trenching", "unit": "Linear Ft.", "default_waste": 0, "labor_difficulty": "High"}
        ],
        "32-Exterior": [
            {"name": "Asphalt", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Pavers", "unit": "Sq. Ft.", "default_waste": 12, "labor_difficulty": "High"},
            {"name": "Sod", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Mulch", "unit": "Cu. Yards", "default_waste": 5, "labor_difficulty": "Low"}
        ],
        "33-Utilities": [
            {"name": "Water Main Pipe", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Sewer Pipe", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Catch Basin", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Backflow Preventer", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"}
        ],
        "34-Transportation": [
            {"name": "Traffic Signs", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Bollards", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Parking Stops", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Striping Paint", "unit": "Gallons", "default_waste": 5, "labor_difficulty": "Medium"}
        ],
        "40-Process": [
            {"name": "Industrial Pump", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Process Motor", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Inline Filter", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Control Valve", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"}
        ],
        "41-Material-Handling": [
            {"name": "Hoist", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Dock Leveler", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Straps", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Safety Netting", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Low"}
        ],
        "42-Process-Heating": [
            {"name": "Industrial Boiler", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Burner Assembly", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "High-Temp Piping", "unit": "Linear Ft.", "default_waste": 8, "labor_difficulty": "High"},
            {"name": "Steam Vent", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"}
        ],
        "43-Gas-Liquid": [
            {"name": "Compressor", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Pressure Tank", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Gas Regulator", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "High-Pressure Hose", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"}
        ],
        "44-Pollution-Control": [
            {"name": "Air Scrubber Media", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Exhaust Ducting", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "Emissions Monitor", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Neutralizing Chemical", "unit": "Gallons", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "45-Industrial": [
            {"name": "Conveyor Section", "unit": "Linear Ft.", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Gearbox Drive", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Heavy Machine Mount", "unit": "Count", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Proximity Sensor", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "46-Water-Systems": [
            {"name": "Filtration Pump", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Filter Media", "unit": "Bags", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Water Treatment Pipe", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Chemical Feed Valve", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"}
        ],
        "48-Electrical-Power": [
            {"name": "Step-Down Transformer", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Industrial Switchgear", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "High-Voltage Cable", "unit": "Linear Ft.", "default_waste": 8, "labor_difficulty": "High"},
            {"name": "Heavy Grounding Rod", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"}
        ],
        "50-Roofing": [
            {"name": "Architectural Shingles", "unit": "Squares", "default_waste": 12, "labor_difficulty": "High"},
            {"name": "Underlayment", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Drip Edge", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Ice & Water Shield", "unit": "Rolls", "default_waste": 7, "labor_difficulty": "Medium"}
        ],
        "51-Siding": [
            {"name": "Vinyl Panel", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Fiber Cement Board", "unit": "Sq. Ft.", "default_waste": 12, "labor_difficulty": "High"},
            {"name": "Starter Strip", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "House Wrap", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Medium"}
        ],
        "52-Windows": [
            {"name": "Double Hung", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Slider", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Casement", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Flashing Tape", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Low"}
        ],
        "53-Insulation": [
            {"name": "Blown Cellulose", "unit": "Bags", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Foil Radiant Barrier", "unit": "Sq. Ft.", "default_waste": 8, "labor_difficulty": "Medium"},
            {"name": "Acoustic Insulation", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Insulation Staples", "unit": "Boxes", "default_waste": 10, "labor_difficulty": "Low"}
        ],
        "54-Ceilings": [
            {"name": "Drop Ceiling Tile", "unit": "Count", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Main Grid Runner", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Cross Tee", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Ceiling Wire", "unit": "Rolls", "default_waste": 10, "labor_difficulty": "Medium"}
        ],
        "55-Columns": [
            {"name": "Structural Fiberglass", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Aluminum Fluted Wrap", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Load Bearing Wood Post", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Base/Cap Trim Hardware", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "56-Molding": [
            {"name": "Baseboard (MDF)", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Chair Rail (Pine)", "unit": "Linear Ft.", "default_waste": 12, "labor_difficulty": "Medium"},
            {"name": "Shoe Molding", "unit": "Linear Ft.", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "Door Casing Matched Set", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"}
        ],
        "57-Fencing": [
            {"name": "Cedar Fence Pickets", "unit": "Count", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Vinyl Fence Panel", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Pressure Treated Post", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Quick-Set Concrete", "unit": "Bags", "default_waste": 5, "labor_difficulty": "Medium"}
        ],
        "58-Gutters": [
            {"name": "K-Style Aluminum Gutter", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "Downspout Section", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Gutter Hanger Bracket", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Gutter Leaf Guard", "unit": "Linear Ft.", "default_waste": 7, "labor_difficulty": "Medium"}
        ],
        "59-Ladders": [
            {"name": "Fiberglass Extension 28ft", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "A-Frame Step 8ft", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Multi-Position Ladder", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Ladder Stabilizer Arms", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "60-Fasteners": [
            {"name": "Framing Nails (Collated)", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Deck Screws (Exterior)", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Tapcon Concrete Anchor", "unit": "Count", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Drywall Screws (Fine)", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"}
        ],
        "61-Mirrors": [
            {"name": "Frameless Vanity Mirror", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Polished Edge Wall Mirror", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Mirror Mounting J-Clips", "unit": "Count", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Mirror Mastic Adhesive", "unit": "Tubes", "default_waste": 10, "labor_difficulty": "Low"}
        ],
        "62-Stairs": [
            {"name": "Oak Stair Tread", "unit": "Count", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Primed Stair Riser", "unit": "Count", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Iron Baluster Spindle", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Pre-Cut Stair Stringer", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"}
        ],
        "63-Toilets": [
            {"name": "Elongated Toilet Bowl", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Matching Toilet Tank", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Reinforced Wax Ring Kit", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Braided Supply Line", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "64-Tools": [
            {"name": "Rotary Hammer Drill", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Laser Level (Self-Leveling)", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Miter Saw Blade", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Lithium-Ion Battery Pack", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"}
        ],
        "65-Vanities": [
            {"name": "Single Sink Vanity 36in", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Double Sink Vanity 60in", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Integrated Vanity Counter top", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Widespread Basin Faucet", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "66-Ventilation": [
            {"name": "Bathroom Exhaust Fan", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Flexible Aluminum Ducting", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Soffit Vent Intake Panel", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Automated Dampers", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"}
        ],
        "67-Painting": [
            {"name": "Interior Acrylic Latex", "unit": "Gallons", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Drywall Interior Primer", "unit": "Gallons", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Premium Painter's Tape", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Heavy Canvas Drop Cloth", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"}
        ],
        "68-Scaffolding": [
            {"name": "Scaffold Main Welded Frame", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Galvanized Cross Brace", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Locking Caster Wheels", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Aluminum Scaffolding Plank", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "69-Specialties": [
            {"name": "Surface Mounting Fire Cabinet", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Heavy Duty Storage Rack", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Corner Wall Guard Profiles", "unit": "Count", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "ADA Restroom Signage", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ]
    }

def get_logistics_modifier(zip_code):
    zip_str = str(zip_code).strip()
    if zip_str.startswith("606"): return 1.25 
    if zip_str.startswith("100"): return 1.40 
    if zip_str.startswith("900"): return 1.30 
    return 1.0 

@app.route('/')
def index():
    return render_template('index.html')

# NEW ROUTE: Serve the Golden Catalog to the Frontend
@app.route('/api/catalog', methods=['GET'])
def serve_catalog():
    return jsonify(get_golden_catalog())

@app.route('/api/report', methods=['POST'])
def generate_report():
    payload = request.json
    
    project_info = payload.get('project_info', {})
    materials = payload.get('materials', [])
    delay_months = int(payload.get('delay_months', 0))

    zip_code = project_info.get('zipCode', '00000')
    logistics_mult = get_logistics_modifier(zip_code)
    escalation_mult = 1.0 + (delay_months * 0.0083) 

    catalog = get_golden_catalog()
    processed_items = []
    total_avg = 0

    for item in materials:
        cat = item.get('category', '').strip()
        sub = item.get('subcategory', '').strip()
        qty = float(item.get('quantity', 0))
        waste_pct = float(item.get('waste', 0))
        labor_req = item.get('labor', False)

        # 1. Search the Golden Catalog for the subcategory
        category_list = catalog.get(cat, [])
        catalog_item = next((x for x in category_list if x["name"] == sub), None)

        # 2. Extract Data from Catalog Engine
        if catalog_item:
            labor_diff = catalog_item.get('labor_difficulty', 'Low')
        else:
            labor_diff = 'Medium' # Fallback for unknown inputs

        # 3. Dynamic Base Pricing based on Labor Difficulty
        # (Since the catalog doesn't contain explicit prices, we assign base unit costs dynamically)
        if labor_diff == 'High':
            base_rate = 25.00
        elif labor_diff == 'Medium':
            base_rate = 15.00
        elif labor_diff == 'Low':
            base_rate = 8.00
        else:
            base_rate = 2.00 # 'None' difficulty (e.g. rentals or pre-made tools)

        # 4. Calculate Quantities with Waste
        final_qty = qty * (1 + (waste_pct / 100.0))

        # 5. Base Cost calculation
        material_cost = final_qty * base_rate
        # Add a 60% premium if labor is required and the item has labor complexity
        labor_cost = (material_cost * 0.6) if labor_req and labor_diff != 'None' else 0

        # Apply Modifiers
        subtotal = (material_cost + labor_cost) * logistics_mult * escalation_mult
        
        min_cost = subtotal * 0.85
        max_cost = subtotal * 1.25
        total_avg += subtotal

        confidence = "High (92%)" if catalog_item else "Low (50%) - Custom Entry"

        processed_items.append({
            "name": f"{cat} - {sub}",
            "confidence": confidence,
            "min": round(min_cost, 2),
            "avg": round(subtotal, 2),
            "max": round(max_cost, 2)
        })

    report_data = {
        "date": datetime.datetime.now().strftime("%B %d, %Y"),
        "project_type": project_info.get('projectType', 'Unknown'),
        "zip_code": zip_code,
        "start_date": project_info.get('startDate', 'N/A'),
        "escalation_applied": f"+{delay_months} Months",
        "items": processed_items,
        "total_min": round(total_avg * 0.85, 2),
        "total_avg": round(total_avg, 2),
        "total_max": round(total_avg * 1.25, 2)
    }

    rendered_html = render_template('report/report.html', data=report_data)
    pdf = HTML(string=rendered_html).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=CostPredict_Estimate.pdf'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
