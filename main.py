import os
import glob
import json
import base64
import pandas as pd
from flask import Flask, render_template, request, make_response, jsonify
from weasyprint import HTML

app = Flask(__name__)

MASTER_DATA_CACHE = {}

def load_master_data():
    """
    Scans the data directory, parses all 38 category CSV spreadsheets,
    extracts dynamic pricing columns, and indexes them alphabetically.
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
            
            # Clean up column headers to ensure uniform casing lookups
            df.columns = [str(c).strip().lower() for c in df.columns]
            name_col = df.columns[0]
            
            items_dictionary = {}
            
            for _, row in df.iterrows():
                item_name = str(row[name_col]).strip()
                if not item_name or item_name == "nan" or item_name == category_name:
                    continue
                
                # Extract columns or default cleanly if the spreadsheet lacks specific tiers
                items_dictionary[item_name] = {
                    "min_mat": float(row.get('min_mat', row.get('material_min', 35.00))),
                    "avg_mat": float(row.get('avg_mat', row.get('material_avg', 45.00))),
                    "max_mat": float(row.get('max_mat', row.get('material_max', 60.00))),
                    "min_lab": float(row.get('min_lab', row.get('labor_min', 25.00))),
                    "avg_lab": float(row.get('avg_lab', row.get('labor_avg', 35.00))),
                    "max_lab": float(row.get('max_lab', row.get('labor_max', 45.00)))
                }
            
            if items_dictionary:
                raw_master_data[category_name] = {
                    "code": csi_codes.get(category_name, "09 00 00"),
                    "unit": "SF" if category_name in ["Flooring", "Drywall", "Countertops", "Concrete"] else "PCS",
                    "items": items_dictionary  # Now passes a rich lookup schema object
                }
        except Exception as e:
            print(f"[ERROR] Failed parsing spreadsheet file {filename}: {e}")
            
    alphabetized_master_data = {k: raw_master_data[k] for k in sorted(raw_master_data.keys())}
    return alphabetized_master_data


MASTER_DATA_CACHE = load_master_data()

@app.route('/')
def index():
    return render_template('index.html', master_data=json.dumps(MASTER_DATA_CACHE))


@app.route('/generate', methods=['POST'])
def generate_pdf():
    """
    Generates a polished CostPredict Project Report matching professional commercial aesthetics.
    Embeds the logo asset cleanly and handles granular item range matrices.
    """
    try:
        raw_payload = request.form.get('payload')
        if not raw_payload:
            return "Missing project configuration payload parameters.", 400
            
        data = json.loads(raw_payload)
        metadata = data.get('metadata', {})
        line_items = data.get('line_items', [])
        totals = data.get('totals', {})
        
        # Safe base64 conversion for your logo asset to bypass local container threading paths
        logo_base64 = ""
        logo_path = os.path.join("static", "logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        # Highly styled HTML print layout utilizing Weasyprint Paged CSS rules
        html_content = f"""
        <html>
        <head>
            <style>
                @page {{
                    size: A4;
                    margin: 20mm 15mm 20mm 15mm;
                    @bottom-right {{
                        content: "Page " counter(page) " of " counter(pages);
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        font-size: 8pt;
                        color: #94a3b8;
                    }}
                }}
                body {{
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    color: #1e293b;
                    margin: 0;
                    padding: 0;
                    line-height: 1.5;
                }}
                .header-container {{
                    border-bottom: 3px solid #23408A;
                    padding-bottom: 16px;
                    margin-bottom: 25px;
                }}
                .logo-slot {{
                    height: 45px;
                    margin-bottom: 10px;
                }}
                .logo-slot img {{
                    height: 100%;
                    width: auto;
                }}
                .doc-title {{
                    color: #23408A;
                    font-size: 24pt;
                    font-weight: 800;
                    letter-spacing: -0.5px;
                    margin: 0;
                }}
                .meta-grid {{
                    width: 100%;
                    margin-bottom: 30px;
                    background-color: #f8fafc;
                    border-radius: 8px;
                    padding: 12px 16px;
                    font-size: 10pt;
                }}
                .meta-grid td {{
                    padding: 4px 0;
                }}
                .section-heading {{
                    font-size: 13pt;
                    font-weight: 700;
                    color: #23408A;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 12px;
                    border-bottom: 1px solid #e2e8f0;
                    padding-bottom: 4px;
                }}
                .items-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 30px;
                }}
                .items-table th {{
                    background-color: #23408A;
                    color: #ffffff;
                    font-weight: 600;
                    font-size: 9pt;
                    text-transform: uppercase;
                    padding: 10px 12px;
                    text-align: left;
                }}
                .items-table td {{
                    padding: 12px;
                    font-size: 9.5pt;
                    border-bottom: 1px solid #e2e8f0;
                    vertical-align: top;
                }}
                .csi-cell {{
                    font-family: monospace;
                    color: #64748b;
                    font-size: 8.5pt;
                }}
                .price-range-text {{
                    font-family: monospace;
                    font-size: 9pt;
                    color: #334155;
                    white-space: nowrap;
                }}
                .checkout-wrapper {{
                    width: 100%;
                    margin-top: 20px;
                    page-break-inside: avoid;
                }}
                .totals-box {{
                    float: right;
                    width: 320px;
                    background-color: #ffffff;
                    border: 1px solid #cbd5e1;
                    border-radius: 8px;
                    padding: 14px;
                }}
                .totals-row {{
                    display: flex;
                    justify-content: space-between;
                    font-size: 9.5pt;
                    padding: 5px 0;
                    color: #475569;
                }}
                .totals-row.grand-heading {{
                    font-size: 12pt;
                    font-weight: 700;
                    color: #23408A;
                    border-top: 2px solid #23408A;
                    margin-top: 8px;
                    padding-top: 8px;
                }}
                .totals-matrix {{
                    font-family: monospace;
                    text-align: right;
                    font-weight: 600;
                }}
                .footer {{
                    clear: both;
                    margin-top: 60px;
                    font-size: 8pt;
                    color: #94a3b8;
                    text-align: justify;
                    line-height: 1.4;
                    border-top: 1px solid #e2e8f0;
                    padding-top: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header-container">
                <div class="logo-slot">
                    {"<img src='data:image/png;base64," + logo_base64 + "' />" if logo_base64 else ""}
                </div>
                <h1 class="doc-title">CostPredict Project Report</h1>
            </div>

            <table class="meta-grid">
                <tr>
                    <td style="width: 50%;"><strong>Project Configuration Type:</strong> {metadata.get('project_type')}</td>
                    <td style="width: 50%;"><strong>Target Geographical Zip Code:</strong> {metadata.get('location')}</td>
                </tr>
                <tr>
                    <td><strong>Estimated Purchase Date Window:</strong> {metadata.get('start_date')}</td>
                    <td></td>
                </tr>
            </table>

            <h2 class="section-heading">Predictive Material & Labor Bill of Quantities</h2>
            <table class="items-table">
                <thead>
                    <tr>
                        <th style="width: 12%;">CSI Code</th>
                        <th style="width: 38%;">Description & Scope Sizing</th>
                        <th style="width: 25%;">Material Range (Min/Avg/Max)</th>
                        <th style="width: 25%;">Labor Range (Min/Avg/Max)</th>
                    </tr>
                </thead>
                <tbody>
        """

        for item in line_items:
            html_content += f"""
                <tr>
                    <td class="csi-cell">{item.get('code')}</td>
                    <td>
                        <strong style="color: #23408A;">{item.get('desc')}</strong>
                        <div style="font-size: 8.5pt; color: #64748b; margin-top: 2px;">
                            Calculated Volume: {item.get('qty', 0):,} {item.get('unit')}
                        </div>
                        <div style="font-size: 8.5pt; color: #475569; margin-top: 2px; font-weight: 500;">
                            Confidence Matrix Rank: <span style="font-family: monospace; font-weight: bold;">{item.get('confidence_str')}</span>
                        </div>
                    </td>
                    <td class="price-range-text">
                        ${item.get('mat_min',0):,.0f} /<br/>
                        <strong>${item.get('mat_avg',0):,.0f}</strong> /<br/>
                        ${item.get('mat_max',0):,.0f}
                    </td>
                    <td class="price-range-text">
                        ${item.get('lab_min',0):,.0f} / <br/>
                        <strong>${item.get('lab_avg',0):,.0f}</strong> / <br/>
                        ${item.get('lab_max',0):,.0f}
                    </td>
                </tr>
            """

        html_content += f"""
                </tbody>
            </table>

            <div class="checkout-wrapper">
                <div class="totals-box">
                    <h3 style="margin: 0 0 10px 0; font-size: 10.5pt; color: #23408A; text-transform: uppercase; border-bottom: 1px dashed #cbd5e1; padding-bottom: 4px;">Predictive Project Aggregates</h3>
                    
                    <div class="totals-row">
                        <span>Material Subtotals (Min/Avg/Max):</span>
                        <span class="totals-matrix">${totals.get('mat_min', 0):,.0f} / ${totals.get('mat_avg', 0):,.0f} / ${totals.get('mat_max', 0):,.0f}</span>
                    </div>
                    <div class="totals-row">
                        <span>Labor Subtotals (Min/Avg/Max):</span>
                        <span class="totals-matrix">${totals.get('lab_min', 0):,.0f} / ${totals.get('lab_avg', 0):,.0f} / ${totals.get('lab_max', 0):,.0f}</span>
                    </div>
                    <div class="totals-row">
                        <span>Regional Sales Tax (Min/Avg/Max):</span>
                        <span class="totals-matrix">${totals.get('tax_min', 0):,.0f} / ${totals.get('tax_avg', 0):,.0f} / ${totals.get('tax_max', 0):,.0f}</span>
                    </div>
                    
                    <div class="totals-row grand-heading">
                        <span>Pricing Prediction:</span>
                    </div>
                    <div style="text-align: right; font-family: monospace; font-size: 13pt; font-weight: 800; color: #23408A; margin-top: 4px;">
                        ${totals.get('grand_min', 0):,.0f} / ${totals.get('grand_avg', 0):,.0f} / ${totals.get('grand_max', 0):,.0f}
                    </div>
                </div>
            </div>

            <div style="clear: both;"></div>

            <div class="footer">
                <strong>LEGAL LIABILITY DISCLAIMER:</strong> All cost evaluations, asset measurements, and predictive material output parameters generated by CostPredict are automated configurations provided solely for baseline budgeting and scoping evaluations. These values do not constitute structural advice, architectural blueprints, or binding contractual pricing guarantees. Actual regional material rates, labor availability, and construction engineering demands will vary by project conditions. Users must independently verify all bills of quantities with a licensed professional contractor prior to project execution.
            </div>
        </body>
        </html>
        """

        pdf_file = HTML(string=html_content).write_pdf()
        
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=CostPredict_Project_Report.pdf'
        return response

    except Exception as e:
        print(f"[ERROR] PDF generation failed: {e}")
        return f"Error executing calculation compilation pipeline script: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
