import os
import glob
import json
import requests
import pandas as pd
from flask import Flask, render_template, request, make_response, jsonify
from weasyprint import HTML

app = Flask(__name__)

# --- GITHUB TRIGGER LOGIC ---
def trigger_github_action(category, zip_code):
    """Triggers the GitHub workflow to generate pricing data."""
    # Ensure you set these in your Render Environment Variables
    repo = os.environ.get('GITHUB_REPO') # e.g., 'username/repo'
    token = os.environ.get('GITHUB_TOKEN')
    
    url = f"https://api.github.com/repos/{repo}/actions/workflows/monthly_scrape.yml/dispatches"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"ref": "main", "inputs": {"category": category, "zip_code": zip_code}}
    try:
        requests.post(url, json=data, headers=headers)
        print(f"Triggered build for {category} in {zip_code}")
    except Exception as e:
        print(f"Failed to trigger GitHub Action: {e}")

# --- PRICING & DATA LOGIC ---
@app.route('/api/pricing')
def api_pricing():
    category = request.args.get('category')
    zip_code = request.args.get('zip')
    file_path = os.path.join("data", zip_code, f"{category}.csv")
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Assuming the CSV contains the item, return the first matching row
        return jsonify(df.to_dict(orient='records')[0])
    else:
        trigger_github_action(category, zip_code)
        return {"status": "building"}, 404

@app.route('/')
def index():
    return render_template('index.html')

# --- PDF GENERATION LOGIC ---
@app.route('/generate', methods=['POST'])
def generate_pdf():
    try:
        raw_payload = request.form.get('payload')
        data = json.loads(raw_payload)
        line_items = data.get('line_items', [])
        
        # Build HTML for the PDF report
        html_content = "<html><body><h1>Project Estimate Report</h1><table border='1' width='100%'><tr><th>Item</th><th>Qty</th><th>Material</th><th>Labor</th></tr>"
        for item in line_items:
            # Use safe get to avoid errors if fields are missing
            sub = item.get('subcategory', 'N/A')
            qty = item.get('qty', 0)
            mat = float(item.get('avg_mat', 0))
            lab = float(item.get('avg_lab', 0)) if item.get('includeLabor', True) else 0
            html_content += f"<tr><td>{sub}</td><td>{qty}</td><td>${mat:.2f}</td><td>${lab:.2f}</td></tr>"
        
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
