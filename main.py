import os
import glob
import json
import base64
import pandas as pd
from flask import Flask, render_template, request, make_response
from weasyprint import HTML

app = Flask(__name__)

# --- Market Estimation Logic (Used when data is missing) ---
def get_ai_estimate(item_name, cost_type):
    """
    Provides a market-based estimate when CSV data is missing.
    Adjust these values to reflect your actual market pricing.
    """
    item = item_name.lower()
    # Simple logic-based estimation
    if "bracket" in item: return 12.50 if cost_type == "mat" else 15.00
    if "hanger" in item: return 5.75 if cost_type == "mat" else 10.00
    if "tile" in item: return 2.80 if cost_type == "mat" else 5.00
    return 15.00 if cost_type == "mat" else 15.00

# --- Data Loading Logic ---
def load_master_data():
    raw_master_data = {}
    csv_files = glob.glob(os.path.join("data", "*.csv"))
    
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        category_name = filename.replace("Building Materials Spreadsheet-05.16.2026.xlsx - ", "").replace(".csv", "")
        
        if category_name in ["Stores", "Summary"]: continue
            
        try:
            df = pd.read_csv(file_path)
            if df.empty: continue
            
            df.columns = [str(c).strip().lower().replace('ï»¿', '') for c in df.columns]
            name_col = df.columns[0]
            
            items_dictionary = {}
            for _, row in df.iterrows():
                row_data = {str(k).strip().lower(): v for k, v in row.items()}
                item_name = str(row[name_col]).strip()
                
                if not item_name or item_name.lower() in ["nan", ""]: continue
                
                # Pricing retrieval with AI Estimate fallback
                def get_price(keys, cost_type):
                    for k in keys:
                        if k in row_data and pd.notna(row_data[k]):
                            try:
                                return float(str(row_data[k]).replace('$', '').replace(',', '').strip())
                            except: continue
                    return get_ai_estimate(item_name, cost_type)

                items_dictionary[item_name] = {
                    "min_mat": get_price(['min_mat', 'material_min', 'mat_min'], "mat"),
                    "avg_mat": get_price(['avg_mat', 'material_avg', 'mat_avg'], "mat"),
                    "max_mat": get_price(['max_mat', 'material_max', 'mat_max'], "mat"),
                    "min_lab": get_price(['min_lab', 'labor_min', 'lab_min'], "lab"),
                    "avg_lab": get_price(['avg_lab', 'labor_avg', 'lab_avg'], "lab"),
                    "max_lab": get_price(['max_lab', 'labor_max', 'lab_max'], "lab")
                }
            
            raw_master_data[category_name] = {"items": items_dictionary}
        except Exception as e:
            print(f"[ERROR] Failed parsing {filename}: {e}")
            
    return raw_master_data

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
