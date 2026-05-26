import os
import json
import requests
import pandas as pd
from flask import Flask, render_template, request, make_response, jsonify

app = Flask(__name__)

# --- SYSTEM BOOTSTRAP: GENERATES THE "GOLDEN 50" CATALOG ---
def bootstrap_system():
    catalog = {
        "03-Concrete": ["Ready Mix", "Rebar", "Anchor Bolts", "Expansion Joint", "Vapor Barrier", "Curing Comp", "Release Agent", "Form Ties", "Wire Mesh", "Sona Tubes", "Sealer", "Additives"],
        "04-Masonry": ["Brick", "Block", "Mortar", "Stone Veneer", "Wall Ties", "Flashing", "Sealant", "Cleaners", "Sand", "Rebar", "Grout", "Tools"],
        "05-Metals": ["Steel Beam", "Column", "Angle Iron", "Plate", "Gusset", "Joist", "Decking", "Metal Stud", "Track", "Fasteners", "Soffit", "Corner Bead"],
        "06-Rough-Carpentry": ["2x4 Studs", "2x6 Joists", "4x8 Plywood", "OSB", "LVL Beams", "Rim Board", "Joist Hangers", "Hurricane Ties", "Blocking", "Shim Stock", "Sills", "Headers"],
        "07-Thermal": ["R-13 Batt", "R-30 Batt", "Rigid Foam", "Spray Foam", "House Wrap", "Vapor Barrier", "Roofing Shingles", "Drip Edge", "Ventilation", "Ice Shield", "Roof Felt", "Sealant"],
        "08-Doors": ["Interior Door", "Exterior Door", "Door Frame", "Hinges", "Knob Set", "Deadbolt", "Threshold", "Weatherstrip", "Window Pane", "Shim", "Casing", "Stop"],
        "09-Drywall": ["Panel 4x8", "Fire-Rated 5-8", "Greenboard", "Tape", "Compound", "Corner Bead", "Screws", "Sandpaper", "Primer", "Texture", "Joint Mesh", "Patch Kit"],
        "10-Flooring": ["Hardwood", "LVP", "Tile", "Laminate", "Underlayment", "Transition", "Grout", "Thinset", "Spacers", "Sealer", "Baseboard", "Shoe Mold"],
        "11-Equipment": ["Refrigerator", "Dishwasher", "Range", "Microwave", "Hood", "Washer", "Dryer", "Garbage Disp", "Freezer", "Compactor", "Ice Maker", "Wine Cooler"],
        "12-Cabinets": ["Wall 30in", "Wall 36in", "Base 30in", "Base 36in", "Pantry", "Drawer Bank", "Filler", "Toe Kick", "Crown", "Cabinet Screw", "Handle", "Hinge"],
        "13-Countertops": ["Granite", "Quartz", "Laminate", "Butcher Block", "Backsplash", "Under-mount Sink", "Side-splash", "Epoxy", "Sealer", "Adhesive", "Caulk", "Support"],
        "21-Fire-Suppression": ["Sprinkler Head", "Piping", "Control Valve", "Extinguisher", "Cabinet", "Alarm Sensor", "Backflow", "Gauge", "Drain", "Escutcheon", "Bracket", "Strap"],
        "22-Plumbing": ["PEX Tubing", "PVC Pipe", "Copper Pipe", "Toilet", "Shower Valve", "Supply Line", "Drain Fitting", "Water Heater", "Sink", "Faucet", "P-Trap", "Shutoff"],
        "23-HVAC": ["Condenser", "Air Handler", "Thermostat", "Ductwork", "Return Grille", "Supply Register", "Filter", "Drain Line", "Insulation", "Control Board", "Mount", "Vents"],
        "25-Automation": ["Controller", "Sensor", "Hub", "Thermostat", "Switch", "Relay", "Power Supply", "Cable", "Connector", "Mount", "Battery", "Panel"],
        "26-Electrical": ["12-2 Romex", "14-2 Romex", "Main Panel", "Breakers", "Outlets", "Switches", "Can Lights", "Junction Box", "Conduit", "Wire Nuts", "Boxes", "Tape"],
        "27-Communications": ["Cat6 Cable", "Coax Cable", "Router", "Wall Plate", "Jack", "Switch", "Patch Panel", "Mount", "Cable Tie", "Label", "Box", "Splitter"],
        "31-Earthwork": ["Excavation", "Grading", "Gravel", "Trenching", "Compaction", "Backfill", "Topsoil", "Sod Prep", "Boulder Removal", "Finish Grade", "Drainage", "Berms"],
        "32-Exterior": ["Asphalt", "Pavers", "Concrete Path", "Sod", "Mulch", "Shrubs", "Trees", "Irrigation", "Valve", "Controller", "Edging", "Stones"],
        "33-Utilities": ["Water Pipe", "Sewer Pipe", "Drain Pipe", "Manhole", "Catch Basin", "Valve Box", "Cleanout", "Fittings", "Joint Seal", "Marking", "Locator", "Backflow"],
        "34-Transportation": ["Signs", "Bollards", "Ramps", "Railings", "Parking Stop", "Striping", "Paint", "Hardware", "Anchors", "Post", "Reflectors", "Barriers"],
        "40-Process": ["Pump", "Motor", "Filter", "Valve", "Sensor", "Switch", "Conduit", "Cable", "Seal", "Lubricant", "Gasket", "Fitting"],
        "41-Material-Handling": ["Dolly", "Cart", "Hoist", "Forklift", "Ramp", "Straps", "Gloves", "Vest", "Helmet", "Brace", "Padding", "Crate"],
        "42-Process-Heating": ["Boiler", "Burner", "Piping", "Insulation", "Valve", "Gauge", "Control", "Sensor", "Vent", "Fuel Line", "Bracket", "Strap"],
        "43-Gas-Liquid": ["Compressor", "Tank", "Filter", "Regulator", "Gauge", "Fitting", "Hose", "Lubricant", "Seal", "Valve", "Coupling", "Bracket"],
        "44-Pollution-Control": ["Filter", "Media", "Pump", "Monitor", "Sensor", "Chemical", "Seal", "Vent", "Fitting", "Duct", "Brace", "Strap"],
        "45-Industrial": ["Machine", "Conveyor", "Drive", "Motor", "Gear", "Bearing", "Lubricant", "Seal", "Sensor", "Controller", "Harness", "Mount"],
        "46-Water-Systems": ["Pump", "Filter", "Media", "Valve", "Piping", "Sensor", "Monitor", "Chemical", "Fitting", "Seal", "Gasket", "Gauge"],
        "48-Electrical-Power": ["Transformer", "Switchgear", "Panel", "Breaker", "Fuse", "Cable", "Conduit", "Ground", "Support", "Mount", "Box", "Strap"],
        "50-Roofing": ["Shingle", "Underlay", "Drip Edge", "Vent", "Starter", "Flashing", "Nails", "Ridge Cap", "Ice Shield", "Sealant", "Valley", "Ventilation"],
        "51-Siding": ["Vinyl Panel", "Stone", "Channel", "Starter", "Corner", "Screws", "Mortar", "Wrap", "Flasher", "Caulk", "Trim", "Nails"],
        "52-Windows": ["Double Hung", "Slider", "Casement", "Awning", "Frame", "Glazing", "Shim", "Stop", "Sealant", "Trim", "Lock", "Crank"],
        "53-Insulation": ["Batt R13", "Batt R30", "Rigid", "Spray", "Housewrap", "Vapor", "Tape", "Caulk", "Mask", "Gloves", "Baffle", "Staples"],
        "54-Ceilings": ["Drop Tile", "Grid", "Angle", "Runner", "Tee", "Canopy", "Panel", "Adhesive", "Medallion", "Paint", "Fasteners", "Lights"],
        "55-Columns": ["Fiberglass", "Aluminum", "Wood", "Wrap", "Cap", "Load Plate", "Mount", "Adhesive", "Flashing", "Paint", "Screws", "Bracket"],
        "56-Molding": ["Crown", "Chair Rail", "Shoe", "Casing", "Stop", "Panel", "Cap", "Cove", "Corner", "Flex", "Nails", "Glue"],
        "57-Fencing": ["Cedar", "Vinyl", "Post", "Hinge", "Latch", "Cap", "Concrete", "Bracket", "Rail", "Hardware", "Screws", "Mesh"],
        "58-Gutters": ["K-Style", "Downspout", "Elbow", "Hanger", "End Cap", "Outlet", "Sealant", "Strap", "Splash", "Screws", "Brackets", "GutterGuard"],
        "59-Ladders": ["Extension", "Step", "Multi", "Hook", "Leveler", "Platform", "Stabilizer", "Caddy", "Feet", "Pad", "Safety", "Lock"],
        "60-Fasteners": ["Nails", "Screws", "Deck", "Tapcon", "Finish", "Roofing", "Washers", "Bolts", "Anchor", "Collated", "Clips", "Straps"],
        "61-Mirrors": ["Wall", "Vanity", "Frame", "Clip", "Adhesive", "Cleaner", "Spacer", "Bracket", "Leveler", "Film", "Level", "Screws"],
        "62-Stairs": ["Tread", "Riser", "Baluster", "Post", "Handrail", "Bracket", "Stringer", "Landing", "Hardware", "Filler", "Newel", "Screws"],
        "63-Toilets": ["Bowl", "Tank", "Wax", "Bolt", "Seat", "Supply", "Flapper", "Valve", "Handle", "Caulk", "Shim", "Pipe"],
        "64-Tools": ["Hammer", "Tape", "Level", "Drill", "Saw", "Knife", "Pliers", "Wrench", "Safety", "Case", "Battery", "Charger"],
        "65-Vanities": ["24in", "36in", "Counter", "Sink", "Hardware", "Legs", "Mirror", "Backsplash", "Filler", "Screw", "Faucets", "Drain"],
        "66-Ventilation": ["Hood", "Fan", "Duct", "Roof Vent", "Soffit", "Grille", "Filter", "Damper", "Tape", "Clamp", "Hose", "Switch"],
        "67-Painting": ["Primer", "Interior", "Exterior", "Ceiling", "Tape", "Roller", "Brush", "Tray", "Patch", "Dropcloth", "Sandpaper", "Mask"],
        "68-Scaffolding": ["Frame", "Brace", "Platform", "Caster", "Jack", "Rail", "Toeboard", "Lock", "Base", "Clamp", "Safety", "Plank"],
        "69-Specialties": ["Sign", "Extinguisher", "Accessory", "Locker", "Partition", "Mat", "Dock", "Bumper", "Corner", "Guard", "Rack", "Shelving"]
    }
    
    for cat, subs in catalog.items():
        path = os.path.join("data", cat)
        os.makedirs(path, exist_ok=True)
        for sub in subs:
            file_path = os.path.join(path, f"{sub}.csv")
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    f.write("item,avg_mat,avg_lab\n")

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/pricing')
def api_pricing():
    sub = request.args.get('subcategory')
    for root, dirs, files in os.walk("data"):
        if f"{sub}.csv" in files:
            df = pd.read_csv(os.path.join(root, f"{sub}.csv"))
            return jsonify(df.to_dict(orient='records')[0] if not df.empty else {"avg_mat": 0, "avg_lab": 0})
    return {"status": "request_sent"}, 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
