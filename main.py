import os
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
    """Safely encodes logo for PDF embedding."""
    if os.path.exists(LOGO_FILE):
        try:
            with open(LOGO_FILE, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception:
            return ""
    return ""

# --- 3. THE ANTI-OVERRUN ENGINE (LOGIC) ---
def calculate_project_assembly(sq_ft, material_price, labor_price):
    """Calculates main materials + automated incidentals."""
    # Main Material (with 10% waste buffer)
    items = [{
        "code": "09 65 19",
        "description": "Luxury Vinyl Plank (Waterproof)",
        "qty": int(sq_ft * 1.1),
        "unit": "SF",
        "mat_unit": material_price,
        "lab_unit": labor_price
    }]
    
    # Incidental: Transition Strips (1 per 300 SF)
    items.append({
        "code": "09 65 13",
        "description": "Matching Transition Strips",
        "qty": max(1, int(sq_ft / 300)),
        "unit": "PCS",
        "mat_unit": 45.00,
        "lab_unit": 25.00
    })
    
    # Incidental: Quarter Round Molding (Estimated Perimeter + 15% Waste)
    perimeter_lf = int((sq_ft ** 0.5) * 4 * 1.15)
    items.append({
        "code": "06 20 00",
        "description": "Quarter Round Molding - White",
        "qty": perimeter_lf,
        "unit": "LF",
        "mat_unit": 1.25,
        "lab_unit": 2.50
    })
    
    return items

# --- 4. PDF GENERATION ENGINE ---
def generate_predictive_report(project_data, output_path):
    logo_b64 = get_base64_logo()
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:50px;">' if logo_b64 else '<h1>CostPredict</h1>'
    
    line_items = calculate_project_assembly(
        project_data['sq_ft'], 
        project_data['mat_rate'], 
        project_data['lab_rate']
    )
    
    subtotal_mat = sum(i['qty'] * i['mat_unit'] for i in line_items)
    subtotal_lab = sum(i['qty'] * i['lab_unit'] for i in line_items)
    tax = subtotal_mat * 0.1025
    grand_total = subtotal_mat + subtotal_lab + tax

    item_rows = ""
    for item in line_items:
        item_rows += f"""
        <div style="border-bottom: 1px solid #e2e8f0; padding: 12px 0;">
            <div style="display:flex; justify-content:space-between; font-weight:bold;">
                <span>{item['description']}</span>
                <span>{item['code']}</span>
            </div>
            <div style="font-size: 9pt; color: #4a5568; margin-top: 4px;">
                Qty: {item['qty']} {item['unit']} | 
                Mat: ${item['qty']*item['mat_unit']:,.2f} | 
                Lab: ${item['qty']*item['lab_unit']:,.2f}
            </div>
        </div>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 0; }}
            body {{ font-family: 'Helvetica', sans-serif; margin: 0; padding: 0; color: #333; }}
            .header {{ background: {CP_BLUE}; color: white; padding: 30px; border-bottom: 8px solid {CP_YELLOW}; }}
            .content {{ padding: 30px; }}
            .total-box {{ width: 300px; margin-left: auto; margin-top: 20px; border-top: 3px solid {CP_BLUE}; padding-top: 10px; }}
            .notice-box {{ background: #fef2f2; border: 1px solid #fee2e2; padding: 15px; margin-top: 30px; font-size: 8.5pt; color: #991b1b; }}
        </style>
    </head>
    <body>
        <div class="header">{logo_html}</div>
        <div class="content">
            <h2 style="color:{CP_BLUE};">Predictive Pricing Report</h2>
            <div style="margin-bottom: 20px; font-size: 10pt;">
                <strong>Project:</strong> {project_data['name']} | <strong>Location:</strong> {project_data['location']}
            </div>
            {item_rows}
            <div class="total-box">
                <div style="display:flex; justify-content:space-between;"><span>Material:</span><span>${subtotal_mat:,.2f}</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Labor:</span><span>${subtotal_lab:,.2f}</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Tax:</span><span>${tax:,.2f}</span></div>
                <div style="display:flex; justify-content:space-between; font-weight:bold; color:{CP_BLUE}; font-size:14pt; margin-top:10px;">
                    <span>Total:</span><span>${grand_total:,.2f}</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    HTML(string=html_template).write_pdf(output_path)

# --- 5. WEB ROUTES ---
@app.route('/')
def index():
    """Shows the input form to the user."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Processes form data and returns the PDF."""
    output_file = "/tmp/CostPredict_Report.pdf"
    
    # Extract data from the index.html form
    project_data = {
        "name": request.form.get('name'),
        "location": "Chicago, IL",
        "sq_ft": float(request.form.get('sq_ft', 0)),
        "mat_rate": float(request.form.get('mat_rate', 0)),
        "lab_rate": float(request.form.get('lab_rate', 0))
    }
    
    try:
        generate_predictive_report(project_data, output_file)
        return send_file(output_file, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

# --- 6. RUNNER ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
