import os
import json
import base64
from flask import Flask, render_template, request, send_file
from weasyprint import HTML

# --- 1. INITIALIZE FLASK ---
app = Flask(__name__)

# --- 2. CONFIGURATION & BRANDING ---
CP_BLUE = "#23408A"
CP_YELLOW = "#FFC113"
LOGO_FILE = "CostPredict_Logo_White.png"

def get_base64_logo():
    """Safely encodes the company logo to embed directly into the PDF."""
    if os.path.exists(LOGO_FILE):
        try:
            with open(LOGO_FILE, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception:
            return ""
    return ""

# --- 3. WEB INTERFACE ROUTE ---
@app.route('/')
def index():
    """Renders the interactive dynamic scoping form."""
    return render_template('index.html')

# --- 4. PDF GENERATION CONTROLLER ---
@app.route('/generate', methods=['POST'])
def generate():
    """
    Accepts the compiled project scope JSON from the frontend cart,
    builds the professional invoice layout, and returns a printable PDF.
    """
    # /tmp is the only writable directory on Render's ephemeral container disk
    output_file = "/tmp/CostPredict_Multi_Report.pdf"
    
    # Extract the full project payload built by the JavaScript cart
    raw_payload = request.form.get('payload')
    if not raw_payload:
        return "Error: Project scope state is completely empty.", 400
        
    try:
        data = json.loads(raw_payload)
    except Exception as e:
        return f"Error parsing scope data: {str(e)}", 400
    
    # Setup logo asset or fallback text header
    logo_b64 = get_base64_logo()
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:50px;">' if logo_b64 else '<h1>CostPredict</h1>'
    
    # Build the HTML table rows dynamically based on what was calculated on-screen
    item_rows = ""
    for item in data['line_items']:
        lab_str = f"| Lab: ${item['lab_cost']:,.2f}" if item['lab_cost'] > 0 else "| Labor: Excluded"
        item_rows += f"""
        <div style="border-bottom: 1px solid #e2e8f0; padding: 12px 0; font-size: 9.5pt;">
            <div style="display: flex; justify-content: space-between; font-weight: bold;">
                <span>{item['desc']}</span>
                <span style="font-family: monospace; color: #64748b;">{item['code']}</span>
            </div>
            <div style="font-size: 8.5pt; color: #4a5568; margin-top: 4px;">
                Quantity Structure: {item['qty']} {item['unit']} | Mat: ${item['mat_cost']:,.2f} {lab_str}
            </div>
        </div>
        """

    # Executive-level PDF template matching corporate colors exactly
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 0; }}
            body {{ font-family: 'Helvetica', sans-serif; margin: 0; padding: 0; color: #0f172a; }}
            .header {{ background: {CP_BLUE}; color: white; padding: 25px; border-bottom: 6px solid {CP_YELLOW}; }}
            .content {{ padding: 35px; }}
            .meta-grid {{ display: flex; flex-wrap: wrap; background: #f8fafc; padding: 12px; border-radius: 6px; margin-bottom: 25px; font-size: 9pt; gap: 20px; border: 1px solid #e2e8f0; }}
            .total-box {{ width: 320px; margin-left: auto; margin-top: 25px; border-top: 3px solid {CP_BLUE}; padding-top: 10px; font-size: 10pt; }}
            .notice-box {{ background: #fffbeb; border: 1px solid #fef3c7; padding: 15px; margin-top: 40px; font-size: 8.5pt; color: #92400e; line-height: 1.4; }}
        </style>
    </head>
    <body>
        <div class="header">{logo_html}</div>
        <div class="content">
            <h2 style="color: {CP_BLUE}; margin-top: 0; margin-bottom: 15px; font-size: 16pt;">Scope Alignment & Predictive Cost Report</h2>
            
            <div class="meta-grid">
                <div><strong>Sector Classification:</strong> {data['metadata']['project_type']}</div>
                <div><strong>Target Market:</strong> {data['metadata']['location']}</div>
                <div><strong>Planned Mobilization:</strong> {data['metadata']['start_date'] if data['metadata']['start_date'] else 'Not Specified'}</div>
            </div>

            <h3 style="color: {CP_BLUE}; border-bottom: 2px solid #cbd5e1; padding-bottom: 4px; font-size: 11pt; margin-bottom: 10px;">Itemized Project Assembly Scope</h3>
            {item_rows}
            
            <div class="total-box
