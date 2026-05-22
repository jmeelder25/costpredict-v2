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
    csv_files = glob.glob(os.path.join("data", "*.csv"))
    
    csi_codes = {
        "Concrete": "03 30 00", "Cabinets": "06 41 16", "Vanities": "06 41 20",
        "Countertops": "12 36 00", "Toilets": "22 41 00", "Flooring": "09 65 19",
        "Drywall": "09 29 00", "Doors": "08 14 16", "Windows": "08 51 13", "Paint": "09 91 00"
    }

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        category_name = filename.replace("Building Materials Spreadsheet.xlsx - ", "").replace(".csv", "")
        
        if category_name in ["Stores", "Summary"]: continue
            
        try:
            df = pd.read_csv(file_path)
            if df.empty: continue
            
            # Normalize column names to lowercase/stripped
            df.columns = [str(c).strip().lower() for c in df.columns]
            name_col = df.columns[0]
            
            items_dictionary = {}
            for _, row in df.iterrows():
                row_data = {str(k).strip().lower(): v for k, v in row.items()}
                item_name = str(row[name_col]).strip()
                if not item_name or item_name == "nan" or item_name == category_name: continue
                
                # Robust lookup helper
                def get_val(keys, default):
                    for k in keys:
                        if k in row_data:
                            try: return float(row_data[k])
                            except: continue
                    return float(default)

                items_dictionary[item_name] = {
                    "min_mat": get_val(['min_mat', 'material_min', 'mat_min'], 35.00),
                    "avg_mat": get_val(['avg_mat', 'material_avg', 'mat_avg'], 45.00),
                    "max_mat": get_val(['max_mat', 'material_max', 'mat_max'], 60.00),
                    "min_lab": get_val(['min_lab', 'labor_min', 'lab_min'], 25.00),
                    "avg_lab": get_val(['avg_lab', 'labor_avg', 'lab_avg'], 35.00),
                    "max_lab": get_val(['max_lab', 'labor_max', 'lab_max'], 45.00)
                }
            
            if items_dictionary:
                raw_master_data[category_name] = {
                    "code": csi_codes.get(category_name, "09 00 00"),
                    "unit": "SF" if category_name in ["Flooring", "Drywall", "Countertops", "Concrete"] else "PCS",
                    "items": items_dictionary
                }
        except Exception as e:
            print(f"[ERROR] Failed parsing {filename}: {e}")
            
    return {k: raw_master_data[k] for k in sorted(raw_master_data.keys())}

MASTER_DATA_CACHE = load_master_data()

@app.route('/')
def index():
    return render_template('index.html', master_data=json.dumps(MASTER_DATA_CACHE))

# --- PDF Generation ---
@app.route('/generate', methods=['POST'])
def generate_pdf():
    try:
        raw_payload = request.form.get('payload')
        data = json.loads(raw_payload)
        metadata = data.get('metadata', {})
        line_items = data.get('line_items', [])
        totals = data.get('totals', {})
        
        logo_base64 = ""
        logo_path = os.path.join("static", "logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; padding: 40px; color: #1e293b; }}
                h1 {{ color: #23408A; font-size: 24pt; border-bottom: 2px solid #23408A; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ background-color: #23408A; color: white; padding: 10px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; }}
            </style>
        </head>
        <body>
            <img src='data:image/png;base64,{logo_base64}' style='width: 150px;'>
            <h1>CostPredict Project Report</h1>
            <table class="items-table">
                <thead>
                    <tr><th>Description</th><th>Qty</th><th>Material</th><th>Labor</th></tr>
                </thead>
                <tbody>
        """
        for item in line_items:
            html_content += f"""
                <tr>
                    <td><strong>{item.get('desc')}</strong></td>
                    <td>{item.get('qty')} {item.get('unit')}</td>
                    <td>${item.get('mat_avg', 0):,.2f}</td>
                    <td>${item.get('lab_avg', 0):,.2f}</td>
                </tr>
            """
        html_content += "</tbody></table></body></html>"

        pdf_file = HTML(string=html_content).write_pdf()
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=CostPredict_Project_Report.pdf'
        return response
    except Exception as e:
        return f"PDF Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
