import os
import json
import requests
import pandas as pd
from flask import Flask, render_template, request, make_response, jsonify

app = Flask(__name__)

# --- SYSTEM BOOTSTRAP: GENERATES THE CATALOG ---
def bootstrap_system():
    """Generates categories with high-value subcategories, ensuring no illegal characters in filenames."""
    catalog = {
        "01-General": ["Permits", "Dumpster", "Cleaning", "Temp Power", "Safety Signs", "Storage", "Testing", "Inspections", "Jobsite Trailer", "Water Service"],
        "03-Concrete": ["Ready Mix", "Rebar", "Anchor Bolts", "Expansion Joint", "Vapor Barrier", "Curing Compound", "Release Agent", "Form Ties", "Wire Mesh", "Sona Tubes"],
        "06-Rough-Carpentry": ["2x4 Studs", "2x6 Joists", "4x8 Plywood", "OSB Sheathing", "LVL Beams", "Rim Board", "Joist Hangers", "Hurricane Ties", "Blocking", "Shim Stock"],
        # Updated "Fire-Rated 5/8" to "Fire-Rated 5-8" to prevent directory errors
        "09-Drywall": ["Standard 4x8", "Fire-Rated 5-8", "Greenboard", "Joint Tape", "Joint Compound", "Corner Bead", "Drywall Screws", "Sandpaper", "Primer", "Texture"],
        "22-Plumbing": ["PEX Tubing", "PVC Pipe", "Copper Pipe", "Toilet", "Shower Valve", "Supply Lines", "Drain Fittings", "Water Heater", "Sink", "Faucets"],
        "26-Electrical": ["12-2 Romex", "14-2 Romex", "Main Panel", "Breakers", "Outlets", "Light Switches", "Can Lights", "Junction Boxes", "Conduit", "Wire Nuts"],
        "31-Earthwork": ["Excavation", "Grading", "Gravel", "Trenching", "Compaction", "Backfill", "Topsoil", "Sod Prep", "Boulder Removal", "Finish Grade"],
    }
    
    for cat, subs in catalog.items():
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

# Run setup
bootstrap_system()
refresh_catalog()

# --- ROUTES ---
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

@app.route('/generate', methods=['POST'])
def generate_pdf():
    from weasyprint import HTML
    data = json.loads(request.form.get('payload'))
    items = data.get('line_items', [])
    html = f"<h1>Estimate</h1><table border='1'><tr><th>Sub</th><th>Mat</th><th>Lab</th></tr>"
    for i in items:
        html += f"<tr><td>{i['subcategory']}</td><td>{i['avg_mat']}</td><td>{i['avg_lab']}</td></tr>"
    html += "</table>"
    pdf = HTML(string=html).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    return response

if __name__ == '__main__':
    # Fix: Corrected port binding for Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
