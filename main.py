import os
import json
import requests
import pandas as pd
from flask import Flask, render_template, request, make_response, jsonify

app = Flask(__name__)

# --- SYSTEM BOOTSTRAP: CREATES 37 FOLDERS & 370 CSV FILES ---
def bootstrap_system():
    """Generates the folder structure for your 37 categories and 10 subcategories each."""
    category_map = {
        "Baseboard": ["MDF 3-inch", "MDF 5-inch", "Pine 3-inch", "Pine 5-inch", "Corner Block", "Shoe Molding", "Casing Set", "Base Cap", "Quarter Round", "End Caps"],
        "Bathtubs and Showers": ["Acrylic Tub", "Cast Iron Tub", "Shower Pan", "Glass Door", "Shower Valve", "Drain Kit", "Surround Wall", "Faucet Trim", "Grab Bar", "Caulk"],
        "Builders Hardware": ["Door Hinges", "Cabinet Pulls", "Deadbolt", "Passage Knob", "Privacy Knob", "Door Stop", "Strike Plate", "Window Lock", "House Numbers", "Mailbox"],
        "Cabinets": ["Upper Wall 30-in", "Upper Wall 36-in", "Base 30-in", "Base 36-in", "Pantry Unit", "Drawer Bank", "Filler Strip", "Toe Kick", "Crown Molding", "Cabinet Screws"],
        "Ceilings": ["Drop Ceiling Tile", "Suspension Grid", "Wall Angle", "Main Runner", "Cross Tee", "Canopy", "Acoustic Panel", "Tile Adhesive", "Ceiling Medallion", "Paint"],
        "Columns": ["Fiberglass Porch", "Aluminum Round", "Wood Square", "Column Wrap", "Cap/Base Set", "Load Bearing Plate", "Mounting Kit", "Adhesive", "Flashing", "Paint"],
        "Concrete and Cement and Masonry": ["Ready Mix", "CMU 8x8x16", "Rebar #4", "Mortar Mix", "Portland Cement", "Anchor Bolts", "Expansion Joint", "Vapor Barrier", "Curing Comp", "Ties"],
        "Countertops": ["Granite Slab", "Quartz Slab", "Laminate Top", "Butcher Block", "Backsplash", "Under-mount Sink", "Side-splash", "Epoxy", "Sealer", "Adhesive"],
        "Decking": ["Pressure Treated 5/4x6", "Composite Plank", "Railings", "Balusters", "Post Sleeve", "Joist Hanger", "Deck Screws", "Ledger Board", "Stair Stringer", "Cap Rail"],
        "Doors": ["Interior 30-in", "Interior 32-in", "Exterior 36-in", "Bifold 36-in", "Frame Kit", "Hinges", "Weatherstrip", "Threshold", "Casing", "Handle"],
        "Drywall": ["4x8 Panel", "4x12 Panel", "Tape", "Compound", "Corner Bead", "Screws", "Sandpaper", "Primer", "Patch Kit", "Texture"],
        "Erosion Control": ["Silt Fence", "Straw Wattle", "Erosion Blanket", "Stakes", "Filter Sock", "Turf Reinforce", "Seed Mat", "Geo-Grid", "Catch Basin", "Drain Pipe"],
        "Fans": ["Ceiling Fan 52-in", "Exhaust Bath Fan", "Light Kit", "Wall Control", "Downrod", "Blade Set", "Mounting Kit", "Motor", "Remote", "Housing"],
        "Fasteners": ["Framing Nails", "Drywall Screws", "Deck Screws", "Tapcon", "Finish Nails", "Roofing Nails", "Washers", "Nuts/Bolts", "Anchor", "Collated Nails"],
        "Faucets": ["Kitchen Pull-Down", "Bath Widespread", "Single Handle", "Shower Head", "Handheld Spray", "Supply Lines", "Escutcheon", "Drain Stopper", "Aerator", "Gasket"],
        "Fencing and Gates": ["Cedar Picket", "Vinyl Panel", "Post 4x4", "Gate Hinge", "Latch", "Post Cap", "Concrete Mix", "Brackets", "Rail", "Hardware"],
        "Flooring": ["Hardwood", "LVP", "Tile", "Laminate", "Underlayment", "Transition Strip", "Grout", "Thin-set", "Spacers", "Sealer"],
        "Glass and Acrylic": ["Window Pane", "Mirror Panel", "Acrylic Sheet", "Tempered Glass", "Glazing Tape", "Silicone", "Shim", "Stop", "Clip", "Cleaner"],
        "Gutters": ["K-Style Gutter", "Downspout", "Elbow", "Hanger", "End Cap", "Outlet", "Sealant", "Strap", "Splash Block", "Screws"],
        "Insulation": ["R-13 Batt", "R-30 Batt", "Rigid Foam", "Spray Foam", "House Wrap", "Vapor Barrier", "Tape", "Caulk", "Mask", "Gloves"],
        "Jack Posts": ["Adjustable 3-ft", "Adjustable 7-ft", "Floor Plate", "Mounting Bolt", "Stabilizer", "Steel Plate", "Spacer", "Lock Pin", "Paint", "Lubricant"],
        "Ladders": ["Extension 24-ft", "Step Ladder 6-ft", "Multi-Position", "Roof Hook", "Leveler", "Platform", "Stabilizer", "Caddy", "Feet", "Padding"],
        "Lumber and Composites": ["2x4x8", "2x6x10", "4x8 Plywood", "OSB", "LVL", "Rim Board", "Blocking", "Pressure Treated", "Shims", "Trim"],
        "Material Handling Equipment": ["Dolly", "Wheelbarrow", "Cart", "Hoist", "Ramp", "Straps", "Gloves", "Safety Vest", "Helmet", "Back Brace"],
        "Metals": ["Steel Stud", "Track", "Flashing", "Angle Iron", "Plate", "Rebar", "Wire Mesh", "Soffit", "Corner Bead", "Gusset"],
        "Mirrors": ["Wall Mirror", "Vanity Mirror", "Frame", "Mounting Clip", "Adhesive", "Cleaner", "Spacer", "Corner Bracket", "Leveler", "Safety Film"],
        "Molding": ["Crown", "Chair Rail", "Shoe", "Casing", "Stop", "Panel Mold", "Base Cap", "Cove", "Corner Mold", "Flex Mold"],
        "Paint": ["Primer", "Interior Semi-Gloss", "Exterior Satin", "Ceiling Flat", "Painter Tape", "Roller Kit", "Brushes", "Tray", "Patch", "Drop Cloth"],
        "Roofing": ["Shingle Bundle", "Underlayment", "Drip Edge", "Vent", "Starter Strip", "Flashing", "Nails", "Ridge Cap", "Ice Shield", "Sealant"],
        "Scaffolding": ["Frame", "Brace", "Platform", "Caster", "Leveling Jack", "Guard Rail", "Toeboard", "Lock Pin", "Base Plate", "Clamp"],
        "Siding and Stone Veneer": ["Vinyl Panel", "Stone Veneer", "J-Channel", "Starter Strip", "Corner Trim", "Screws", "Mortar", "House Wrap", "Flasher", "Caulk"],
        "Sinks": ["Kitchen Under-mount", "Drop-in", "Pedestal", "Vessel", "P-Trap", "Drain", "Supply Lines", "Mounting Clips", "Silicone", "Faucets"],
        "Stairs and Railings": ["Tread", "Riser", "Baluster", "Newel Post", "Handrail", "Bracket", "Stringer", "Landing", "Hardware", "Filler"],
        "Toilets": ["Elongated Bowl", "Tank", "Wax Ring", "Bolt Kit", "Seat", "Supply Line", "Flapper", "Fill Valve", "Handle", "Caulk"],
        "Tools": ["Hammer", "Tape Measure", "Level", "Drill", "Saw", "Utility Knife", "Pliers", "Wrench", "Safety Gear", "Cases"],
        "Vanities": ["24-in Vanity", "36-in Vanity", "Countertop", "Sink", "Hardware", "Legs", "Mirror", "Backsplash", "Filler", "Mounting Screw"],
        "Ventilation": ["Range Hood", "Bath Fan", "Ducting", "Roof Vent", "Soffit Vent", "Grille", "Filter", "Damper", "Tape", "Clamp"]
    }
    
    for cat, subs in category_map.items():
        path = os.path.join("data", cat)
        os.makedirs(path, exist_ok=True)
        for sub in subs:
            file_path = os.path.join(path, f"{sub}.csv")
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    f.write("item,avg_mat,avg_lab\n")

# --- CATALOG SCANNER ---
def refresh_catalog():
    catalog = {}
    if os.path.exists("data"):
        for cat in os.listdir("data"):
            cat_path = os.path.join("data", cat)
            if os.path.isdir(cat_path):
                catalog[cat] = [f.replace(".csv", "") for f in os.listdir(cat_path) if f.endswith(".csv")]
    os.makedirs("static", exist_ok=True)
    with open(os.path.join("static", "categories.json"), "w") as f:
        json.dump(catalog, f, indent=2)

bootstrap_system()
refresh_catalog()

# --- ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/pricing')
def api_pricing():
    cat = request.args.get('category')
    sub = request.args.get('subcategory')
    for root, dirs, files in os.walk("data"):
        if f"{sub}.csv" in files:
            df = pd.read_csv(os.path.join(root, f"{sub}.csv"))
            return jsonify(df.to_dict(orient='records')[0] if not df.empty else {"avg_mat": 0, "avg_lab": 0})
    return {"status": "request_sent"}, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
