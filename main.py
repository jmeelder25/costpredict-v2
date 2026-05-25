import os
import json
import requests
import pandas as pd
from flask import Flask, render_template, request, make_response, jsonify

app = Flask(__name__)

# --- AUTOMATED CATALOG SCANNER ---
def refresh_catalog():
    """Scans the /data folder and generates a fresh categories.json in /static."""
    catalog = {}
    data_dir = "data"
    
    if os.path.exists(data_dir):
        for category in os.listdir(data_dir):
            cat_path = os.path.join(data_dir, category)
            if os.path.isdir(cat_path):
                catalog[category] = [f.replace(".csv", "") for f in os.listdir(cat_path) if f.endswith(".csv")]
    
    static_dir = "static"
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        
    with open(os.path.join(static_dir, "categories.json"), "w") as f:
        json.dump(catalog, f, indent=2)
    print("Catalog refreshed from /data directory.")

# Run catalog refresh once at startup
refresh_catalog()

# --- GITHUB TRIGGER LOGIC ---
def trigger_github_action(category, subcategory, zip_code):
    """Triggers the GitHub workflow to generate pricing data."""
    repo = os.environ.get('GITHUB_REPO')
    token = os.environ.get('GITHUB_TOKEN')
    url = f"https://api.github.com/repos/{repo}/actions/workflows/monthly_scrape.yml/dispatches"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    data = {"ref": "main", "inputs": {"category": category, "subcategory": subcategory, "zip_code": zip_code}}
    try:
        requests.post(url, json=data, headers=headers)
    except Exception as e:
        print(f"Failed to trigger GitHub Action: {e}")

# --- API ENDPOINTS ---
@app.route('/api/pricing')
def api_pricing():
    category = request.args.get('category')
    subcategory = request.args.get('subcategory')
    zip_code = request.args.get('zip')
    file_path = os.path.join("data", category, f"{subcategory}.csv")
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return jsonify(df.to_dict(orient='records')[0])
    else:
        trigger_github_action(category, subcategory, zip_code)
        return {"status": "building"}, 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_pdf():
    from weasyprint import HTML
    try:
        raw_payload = request.form.get('payload')
        data = json.loads(raw_payload)
        line_items = data.get('line_items', [])
        
        html_content = "<html><body><h1>Project Estimate Report</h1><table border='1' width='100%'><tr><th>Subcategory</th><th>Qty</th><th>Material</th><th>Labor</th></tr>"
        for item in line_items:
            html_content += f"<tr><td>{item.get('subcategory')}</td><td>{item.get('qty')}</td><td>${float(item.get('avg_mat',0)):.2f}</td><td>${float(item.get('avg_lab',0) if item.get('includeLabor') else 0):.2f}</td></tr>"
        html_content += "</table></body></html>"
        
        pdf_file = HTML(string=html_content).write_pdf()
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=CostPredict_Report.pdf'
        return response
    except Exception as e:
        return f"Error generating PDF: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
