import os
import glob
import json
import pandas as pd
from flask import Flask, render_template, request, make_response
from weasyprint import HTML

app = Flask(__name__)

# --- Pricing Reference Logic ---
# This dictionary will store your fallback estimates from pricing_reference.csv
PRICING_REF = {}

def load_pricing_reference():
    """Loads fallback pricing data from a CSV to prevent hardcoded defaults."""
    ref_file = "data/pricing_reference.csv"
    if os.path.exists(ref_file):
        try:
            df = pd.read_csv(ref_file)
            for _, row in df.iterrows():
                item_name = str(row['item_name']).lower().strip()
                PRICING_REF[item_name] = {
                    "min_mat": float(row['min_mat']), "avg_mat": float(row['avg_mat']), "max_mat": float(row['max_mat']),
                    "min_lab": float(row['min_lab']), "avg_lab": float(row['avg_lab']), "max_lab": float(row['max_lab'])
                }
        except Exception as e:
            print(f"Error loading pricing_reference.csv: {e}")

def get_ai_estimate(item_name):
    """Searches for a keyword match in the reference data, else returns a base fallback."""
    item_key = item_name.lower()
    for ref_key, values in PRICING_REF.items():
        if ref_key in item_key:
            return values
    # Global fallback if no keyword match is found
    return {"min_mat": 10.0, "avg_mat": 15.0, "max_mat": 20.0, 
            "min_lab": 10.0, "avg_lab": 15.0, "max_lab": 20.0}

# --- Main Data Loading ---
def load_master_data():
    load_pricing_reference()
    raw_master_data = {}
    csv_files = glob.glob(os.path.join("data", "*.csv"))
    
    for file_path in csv_files:
        # Skip the reference file so it isn't treated as a category
        if "pricing_reference" in file_path: continue
        
        filename = os.path.basename(file_path)
        category_name = filename.replace("Building Materials Spreadsheet-05.16.2026.xlsx - ", "").replace(".csv", "")
        
        try:
            df = pd.read_csv(file_path)
            # Ensure headers are standard
            df.columns = [str(c).strip().lower() for c in df.columns]
            name_col = df.columns[0]
            items_dictionary = {}
            
            for _, row in df.iterrows():
                item_name = str(row[name_col]).strip()
                if not item_name or item_name.lower() == "nan": continue
                
                try:
                    # Attempt to extract exact pricing from the category CSV
                    items_dictionary[item_name] = {
                        "min_mat": float(row['min_mat']), "avg_mat": float(row['avg_mat']), "max_mat": float(row['max_mat']),
                        "min_lab": float(row['min_lab']), "avg_lab": float(row['avg_lab']), "max_lab": float(row['max_lab'])
                    }
                except (ValueError, KeyError):
                    # Fallback to the reference file or AI estimate
                    items_dictionary[item_name] = get_ai_estimate(item_name)
            
            raw_master_data[category_name] = {"items": items_dictionary}
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    return raw_master_data

# Load data into memory once on startup
MASTER_DATA_CACHE = load_master_data()

@app.route('/')
def index():
    return render_template('index.html', master_data=MASTER_DATA_CACHE)

@app.route('/generate', methods=['POST'])
def generate_pdf():
    try:
        raw_payload = request.form.get('payload')
        data = json.loads(raw_payload)
        line_items = data.get('line_items', [])
        
        html_content = "<html><body><h1>Project Report</h1><table border='1'><tr><th>Description</th><th>Qty</th><th>Material</th><th>Labor</th></tr>"
        for item in line_items:
            mat = float(item.get('avg_mat', 0))
            lab = float(item.get('avg_lab', 0))
            html_content += f"<tr><td>{item.get('subcategory')}</td><td>{item.get('qty')}</td><td>${mat:.2f}</td><td>${lab:.2f}</td></tr>"
        html_content += "</table></body></html>"
        
        pdf_file = HTML(string=html_content).write_pdf()
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=Report.pdf'
        return response
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
