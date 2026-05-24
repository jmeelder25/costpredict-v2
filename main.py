import os
import glob
import json
import base64
import pandas as pd
from flask import Flask, render_template, request, make_response
from weasyprint import HTML

app = Flask(__name__)

# --- Data Loading Logic ---
def load_master_data():
    raw_master_data = {}
    
    # Scanning directory for CSV files
    csv_files = glob.glob(os.path.join("data", "*.csv"))
    
    # CSI Codes mapping
    csi_codes = {
        "Concrete": "03 30 00", "Cabinets": "06 41 16", "Vanities": "06 41 20",
        "Countertops": "12 36 00", "Toilets": "22 41 00", "Flooring": "09 65 19",
        "Drywall": "09 29 00", "Doors": "08 14 16", "Windows": "08 51 13", "Paint": "09 91 00"
    }

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        # Extract category name from filename
        category_name = filename.replace("Building Materials Spreadsheet-05.16.2026.xlsx - ", "").replace(".csv", "")
        
        if category_name in ["Stores", "Summary"]: continue
            
        try:
            df = pd.read_csv(file_path)
            if df.empty: continue
            
            # Clean headers
            df.columns = [str(c).strip().lower().replace('ï»¿', '') for c in df.columns]
            name_col = df.columns[0]
            
            items_dictionary = {}
            for _, row in df.iterrows():
                row_data = {str(k).strip().lower(): v for k, v in row.items()}
                item_name = str(row[name_col]).strip()
                
                if not item_name or item_name.lower() in ["nan", ""] or item_name == category_name: continue
                
                # Pricing helper
                def get_val(keys, default):
                    for k in keys:
                        if k in row_data and pd.notna(row_data[k]):
                            try:
                                clean_val = float(str(row_data[k]).replace('$', '').replace(',', '').strip())
                                return clean_val if clean_val > 0 else float(default)
                            except: continue
                    return float(default)

                items_dictionary[item_name] = {
                    "avg_mat": get_val(['avg_mat', 'material_avg', 'mat_avg'], 45.00),
                    "avg_lab": get_val(['avg_lab', 'labor_avg', 'lab_avg'], 35.00)
                }
            
            raw_master_data[category_name] = {
                "code": csi_codes.get(category_name, "09 00 00"),
                "items": items_dictionary
            }
        except Exception as e:
            print(f"[ERROR] Failed parsing {filename}: {e}")
            
    return raw_master_data

MASTER_DATA_CACHE = load_master_data()

@app.route('/')
def index():
    return render_template('index.html', master_data=MASTER_DATA_CACHE)

@app.route('/generate', methods=['POST'])
def generate_pdf():
    # PDF generation logic remains largely the same, now reading from line_items
    try:
        raw_payload = request.form.get('payload')
        data = json.loads(raw_payload)
        line_items = data.get('line_items', [])
        
        html_content = "<html><body><h1>Project Report</h1><table border='1'><tr><th>Item</th><th>Qty</th><th>Mat</th><th>Lab</th></tr>"
        for item in line_items:
            html_content += f"<tr><td>{item.get('subcategory')}</td><td>{item.get('qty')}</td><td>${float(item.get('avg_mat', 0)):.2f}</td><td>${float(item.get('avg_lab', 0)):.2f}</td></tr>"
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
