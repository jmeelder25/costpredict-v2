import os
import glob
import json
import pandas as pd
from flask import Flask, render_template, request, make_response, jsonify
from weasyprint import HTML

app = Flask(__name__)

MASTER_DATA_CACHE = {}

def load_master_data():
    """
    Scans the data directory, parses all 38 category CSV spreadsheets, 
    and packages them alphabetically into an indexed map dictionary structure.
    """
    raw_master_data = {}
    csv_files = glob.glob(os.path.join("data", "*.csv"))
    
    csi_codes = {
        "Concrete": "03 30 00",
        "Cabinets": "06 41 16",
        "Vanities": "06 41 20",
        "Countertops": "12 36 00",
        "Toilets": "22 41 00",
        "Flooring": "09 65 19",
        "Drywall": "09 29 00",
        "Doors": "08 14 16",
        "Windows": "08 51 13",
        "Paint": "09 91 00"
    }

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        category_name = filename.replace("Building Materials Spreadsheet.xlsx - ", "").replace(".csv", "")
        
        if category_name in ["Stores", "Summary"]:
            continue
            
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                continue
                
            first_column = df.columns[0]
            items_list = df[first_column].dropna().unique().tolist()
            clean_items = [str(i).strip() for i in items_list if str(i).strip() and str(i).strip() != category_name]
            
            if clean_items:
                raw_master_data[category_name] = {
                    "code": csi_codes.get(category_name, "09 00 00"),
                    "unit": "SF" if category_name in ["Flooring", "Drywall", "Countertops", "Concrete"] else "PCS",
                    "items": sorted(clean_items)
                }
        except Exception as e:
            print(f"[ERROR] Failed parsing spreadsheet file {filename}: {e}")
            
    # Alphabetize the final Main Material Category layout by key sorting transformations
    alphabetized_master_data = {k: raw_master_data[k] for k in sorted(raw_master_data.keys())}
    return alphabetized_master_data


# --- SERVER RUNTIME INITIALIZATION ---

MASTER_DATA_CACHE = load_master_data()

@app.route('/')
def index():
    return render_template('index.html', master_data=json.dumps(MASTER_DATA_CACHE))


@app.route('/generate', methods=['POST'])
def generate_pdf():
    """
    Intercepts form array data blocks to process the new min/avg/max tiered arrays
    and compiles a finalized project summary report PDF using WeasyPrint.
    """
    try:
        raw_payload = request.form.get('payload')
        if not raw_payload:
            return "Missing project configuration payload data parameters.", 400
            
        data = json.loads(raw_payload)
        metadata = data.get('metadata', {})
        line_items = data.get('line_items', [])
        totals = data.get('totals', {})
        
        # Pull the new confidence calculation metadata parameter
        confidence_score = metadata.get('confidence_score', 'N/A')

        # Build structural HTML template for WeasyPrint PDF conversion
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; color: #334155; }}
                .header {{ border-bottom: 3px solid #23408A; padding-bottom: 10px; margin-bottom: 20px; }}
                .title {{ color: #23408A; font-size: 24px; font-weight: bold; }}
                .meta-table {{ width: 100%; margin-bottom: 20px; font-size: 13px; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 11px; }}
                .items-table th {{ background-color: #23408A; color: white; padding: 8px; text-align: left; }}
                .items-table td {{ padding: 8px; border-bottom: 1px solid #e2e8f0; }}
                .totals-section {{ margin-top: 20px; float: right; width: 350px; font-size: 13px; }}
                .totals-row {{ display: flex; justify-content: space-between; padding: 6px 0; }}
                .grand-total {{ font-weight: bold; color: #23408A; font-size: 15px; border-top: 2px solid #23408A; padding-top: 6px; }}
                .confidence-box {{ margin-top: 15px; padding: 8px; background-color: #f8fafc; border: 1px solid #cbd5e1; font-weight: bold; border-radius: 4px; font-size: 12px; text-align: center; }}
                .footer {{ margin-top: 50px; font-size: 9px; color: #94a3b8; text-align: justify; line-height: 1.3; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">CostPredict Project Scope Report</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Generated Predictive Summary Engine v2.5</div>
            </div>

            <table class="meta-table">
                <tr>
                    <td><strong>Project Type:</strong> {metadata.get('project_type')}</td>
                    <td><strong>Project Zip Code:</strong> {metadata.get('location')}</td>
                </tr>
                <tr>
                    <td><strong>Estimated Purchase Date:</strong> {metadata.get('start_date')}</td>
                    <td></td>
                </tr>
            </table>

            <h3>Scope Bill of Quantities Matrix</h3>
            <table class="items-table">
                <thead>
                    <tr>
                        <th>CSI Code</th>
                        <th>Material Description</th>
                        <th>Calculated Qty</th>
                        <th>Mat (Min / Avg / Max)</th>
                        <th>Lab (Min / Avg / Max)</th>
                    </tr>
                </thead>
                <tbody>
        """

        for item in line_items:
            html_content += f"""
                <tr>
                    <td style="font-family: monospace;">{item.get('code')}</td>
                    <td><strong>{item.get('desc')}</strong></td>
                    <td>{item.get('qty')} {item.get('unit')}</td>
                    <td style="font-family: monospace;">${item.get('mat_min',0):,.2f} / ${item.get('mat_avg',0):,.2f} / ${item.get('mat_max',0):,.2f}</td>
                    <td style="font-family: monospace;">${item.get('lab_min',0):,.2f} / ${item.get('lab_avg',0):,.2f} / ${item.get('lab_max',0):,.2f}</td>
                </tr>
            """

        html_content += f"""
                </tbody>
            </table>

            <div class="totals-section">
                <div class="totals-row"><span>Material Base Subtotal (Avg):</span><span>${totals.get('mat', 0):,.2f}</span></div>
                <div class="totals-row"><span>Labor Assembly Subtotal (Avg):</span><span>${totals.get('lab', 0):,.2f}</span></div>
                <div class="totals-row"><span>Regional Sales Tax:</span><span>${totals.get('tax', 0):,.2f}</span></div>
                <div class="totals-row grand-total"><span>Project Estimation (Avg Total):</span><span>${totals.get('grand', 0):,.2f}</span></div>
                
                <div class="confidence-box">
                    Confidence Score: {confidence_score}
                </div>
            </div>

            <div style="clear: both;"></div>

            <div class="footer">
                <strong>LEGAL LIABILITY DISCLAIMER:</strong> All cost evaluations, asset measurements, and predictive material output parameters generated by CostPredict are automated configurations provided solely for baseline budgeting and scoping evaluations. These values do not constitute structural advice, architectural blueprints, or binding contractual pricing guarantees. Actual regional material rates, labor availability, and construction engineering demands will vary by project conditions. Users must independently verify all bills of quantities with a licensed professional contractor prior to project execution.
            </div>
        </body>
        </html>
        """

        # Generate the PDF binary via WeasyPrint
        pdf_file = HTML(string=html_content).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=CostPredict_Project_Report.pdf'
        return response

    except Exception as e:
        print(f"[ERROR] PDF generation failed: {e}")
        return f"Error executing calculation compilation pipeline script: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
