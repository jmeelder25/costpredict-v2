print("--- APP STARTING ---")
import os
from flask import Flask, request, make_response, render_template, jsonify, render_template_string
from weasyprint import HTML
import datetime

app = Flask(__name__)

# Embedded PDF Template to guarantee it generates without missing file errors
PDF_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; font-size: 12px; }
        .header { text-align: center; border-bottom: 2px solid #23408A; padding-bottom: 10px; margin-bottom: 20px; }
        .header h1 { color: #23408A; margin: 0; }
        .info-grid { display: block; margin-bottom: 20px; }
        .info-grid p { margin: 2px 0; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th { background-color: #f3f4f6; color: #23408A; padding: 8px; text-align: left; border-bottom: 2px solid #ddd; }
        td { padding: 8px; border-bottom: 1px solid #ddd; text-align: left; }
        .right { text-align: right; }
        .totals { font-weight: bold; }
        .footer { margin-top: 40px; font-size: 9px; color: #666; text-align: center; border-top: 1px solid #ddd; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Predictive Pricing Estimate</h1>
        <p>Generated on {{ data.date }}</p>
    </div>
    
    <div class="info-grid">
        <p><strong>Project Type:</strong> {{ data.project_type }}</p>
        <p><strong>Quality Level:</strong> {{ data.quality_level }}</p>
        <p><strong>Target Zip Code:</strong> {{ data.zip_code }}</p>
        <p><strong>Estimated Tax Rate:</strong> {{ data.tax_rate_display }}</p>
    </div>

    <table>
        <thead>
            <tr>
                <th>Item / Task Details</th>
                <th>Confidence</th>
                <th class="right">Unit Cost</th>
                <th class="right">Min Cost</th>
                <th class="right">Avg Cost</th>
                <th class="right">Max Cost</th>
            </tr>
        </thead>
        <tbody>
            {% for item in data.items %}
            <tr>
                <td>{{ item.name }}</td>
                <td>{{ item.confidence }}</td>
                <td class="right">{% if item.unit_cost %}${{ item.unit_cost }}{% else %}-{% endif %}</td>
                <td class="right">${{ item.min }}</td>
                <td class="right">${{ item.avg }}</td>
                <td class="right">${{ item.max }}</td>
            </tr>
            {% endfor %}
        </tbody>
        <tfoot>
            <tr class="totals">
                <td colspan="3">Subtotals</td>
                <td class="right">${{ data.subtotal_min }}</td>
                <td class="right">${{ data.subtotal_avg }}</td>
                <td class="right">${{ data.subtotal_max }}</td>
            </tr>
            <tr>
                <td colspan="3">Estimated Sales Tax</td>
                <td class="right">${{ data.tax_min }}</td>
                <td class="right">${{ data.tax_avg }}</td>
                <td class="right">${{ data.tax_max }}</td>
            </tr>
            <tr class="totals" style="font-size: 14px; background-color: #f9f9f9;">
                <td colspan="3">PROJECT TOTAL</td>
                <td class="right">${{ data.grand_total_min }}</td>
                <td class="right">${{ data.grand_total_avg }}</td>
                <td class="right">${{ data.grand_total_max }}</td>
            </tr>
        </tfoot>
    </table>

    <div class="footer">
        LEGAL DISCLAIMER: This predictive pricing tool provides estimates based on historical and predictive market data. 
        Actual costs may vary based on specific site conditions, exact material selections, localized contractor demand, and final scopes of work. 
        This document is not a binding financial offer or finalized contract.
    </div>
</body>
</html>
"""

# --- 1. HELPER FUNCTIONS ---

def get_logistics_modifier(zip_code):
    return 1.0 

def get_tax_rate(zip_code):
    zip_str = str(zip_code).strip()
    if zip_str.startswith('606'): return 0.1025
    elif zip_str.startswith('902'): return 0.0950
    elif zip_str.startswith('100'): return 0.08875
    elif zip_str.startswith('770'): return 0.0825
    else: return 0.0750

def get_golden_catalog():
    return {
        "01-General-Requirements": [
            {"name": "Dumpster Rental (30 Yd)", "unit": "Weeks", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Site Protection / Ram Board", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "Low"},
            {"name": "Temporary Fencing", "unit": "Linear Ft.", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Scaffold Rental", "unit": "Days", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Portable Toilet", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Jobsite Office Trailer", "unit": "Months", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Safety Signage", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Fire Extinguisher", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Temporary Power Pole", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Water Tank (250 Gal)", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "03-Concrete": [
            {"name": "Ready Mix", "unit": "Cu. Yards", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Rebar", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Anchor Bolts", "unit": "Count", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Wire Mesh", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Concrete Curing Compound", "unit": "Gallons", "default_waste": 2, "labor_difficulty": "Low"},
            {"name": "Expansion Joint Filler", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Form Release Agent", "unit": "Gallons", "default_waste": 2, "labor_difficulty": "Low"},
            {"name": "Concrete Nails", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Vapor Barrier", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Fiber Reinforcement", "unit": "Bags", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Concrete Pigment", "unit": "Bags", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Styrofoam Void Forms", "unit": "Count", "default_waste": 5, "labor_difficulty": "Low"}
        ],
        "04-Masonry": [
            {"name": "Brick", "unit": "Count", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "Block", "unit": "Count", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Mortar", "unit": "Bags", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "Stone Veneer", "unit": "Sq. Ft.", "default_waste": 12, "labor_difficulty": "High"},
            {"name": "Weep Vents", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Wall Ties", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Lintels", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Glass Block", "unit": "Count", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Masonry Cleaner", "unit": "Gallons", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Water Repellent Sealer", "unit": "Gallons", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Flashing", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Backer Rod", "unit": "Linear Ft.", "default_waste": 2, "labor_difficulty": "Low"}
        ],
        "05-Metals": [
            {"name": "Steel Beam", "unit": "Linear Ft.", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Metal Stud", "unit": "Count", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Track", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Decking", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Steel Plates", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Structural Tubing", "unit": "Linear Ft.", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Bolts/Nuts", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Welding Rods", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Metal Primer", "unit": "Gallons", "default_waste": 2, "labor_difficulty": "Low"},
            {"name": "Handrails", "unit": "Linear Ft.", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Metal Lath", "unit": "Sheets", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Fasteners (Self-Tapping)", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"}
        ],
        "06-Rough-Carpentry": [
            {"name": "2x4 Studs", "unit": "Count", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "2x6 Joists", "unit": "Count", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "4x8 Plywood", "unit": "Sheets", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "OSB", "unit": "Sheets", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "LVL Beams", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Framing Nails (Collated)", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Construction Adhesive", "unit": "Tubes", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Joist Hangers", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Hurricane Ties", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Sill Plate Anchor Bolts", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Tyvek House Wrap", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Flashing Tape", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Low"}
        ],
        "07-Thermal": [
            {"name": "R-13 Batt", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "R-30 Batt", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Rigid Foam", "unit": "Sheets", "default_waste": 8, "labor_difficulty": "Medium"},
            {"name": "Spray Foam", "unit": "Board Ft.", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "Mineral Wool", "unit": "Bags", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Vapor Retarder", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Acoustic Sealant", "unit": "Tubes", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Insulation Staples", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Reflective Foil", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Foundation Insulation", "unit": "Sheets", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Pipe Insulation", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Expansion Foam", "unit": "Cans", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "08-Doors": [
            {"name": "Interior Door", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Exterior Door", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Door Frame", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Hinges", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Door Handle/Lockset", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Threshold", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Weatherstripping", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Door Closer", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Kick Plate", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Door Stop", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Shims", "unit": "Bundles", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Casing (Trim)", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"}
        ],
        "09-Drywall": [
            {"name": "Panel 4x8", "unit": "Sheets", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "Fire-Rated 5-8", "unit": "Sheets", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "Tape", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Compound", "unit": "Boxes", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Corner Bead", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Drywall Screws", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Backer Board (Cement)", "unit": "Sheets", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Sanding Mesh", "unit": "Packs", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Primer", "unit": "Gallons", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Access Panel", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Shims/Spacers", "unit": "Packs", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Texture Spray", "unit": "Cans", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "10-Flooring": [
            {"name": "Hardwood", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "LVP", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Tile", "unit": "Sq. Ft.", "default_waste": 12, "labor_difficulty": "High"},
            {"name": "Laminate", "unit": "Sq. Ft.", "default_waste": 7, "labor_difficulty": "Medium"},
            {"name": "Underlayment", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Thin-set Mortar", "unit": "Bags", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "Grout", "unit": "Bags", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Transition Strips", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Shoe Molding", "unit": "Linear Ft.", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "Self-Leveling Compound", "unit": "Bags", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Adhesive", "unit": "Buckets", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Carpet Tiles", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Low"}
        ],
        "11-Equipment": [
            {"name": "Refrigerator", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Dishwasher", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Range", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Microwave", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Washer", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Dryer", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Range Hood", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Garbage Disposal", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Water Heater", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Wine Cooler", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Wall Oven", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Trash Compactor", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "12-Cabinets": [
            {"name": "Wall 30in", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Base 36in", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Pantry", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Crown Molding", "unit": "Linear Ft.", "default_waste": 15, "labor_difficulty": "High"},
            {"name": "Cabinet Hardware (Knobs)", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Cabinet Hardware (Pulls)", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Drawer Slides", "unit": "Pairs", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Hinge Sets", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Filler Strips", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Toe Kick Molding", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Under-Cabinet Lighting", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Mounting Screws", "unit": "Boxes", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "13-Countertops": [
            {"name": "Granite", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Quartz", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Laminate", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Butcher Block", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "Marble Slab", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Backsplash Tile", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Silicone Caulk", "unit": "Tubes", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Epoxy Adhesive", "unit": "Kits", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Support Brackets", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Sealer", "unit": "Bottles", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Sink Cut-out Template", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Edge Trim", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"}
        ],
        "21-Fire-Suppression": [
            {"name": "Sprinkler Head", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Piping", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "Control Valve", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Extinguisher", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Smoke Detector", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Heat Detector", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Alarm Bell", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Flow Switch", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Gauge", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Hanger/Bracket", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Fire-Rated Caulk", "unit": "Tubes", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Exit Signage", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "22-Plumbing": [
            {"name": "PEX Tubing", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "PVC Pipe", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Toilet", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Shower Valve", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Kitchen Faucet", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Drain Trap (P-Trap)", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Supply Line", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Shut-off Valve", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Pipe Hangers", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "PVC Glue/Primer", "unit": "Kits", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Wax Ring", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Pipe Insulation", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Low"}
        ],
        "23-HVAC": [
            {"name": "Condenser", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Air Handler", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Thermostat", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Ductwork", "unit": "Linear Ft.", "default_waste": 12, "labor_difficulty": "High"},
            {"name": "Vent Cover/Grille", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Refrigerant Lines", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Air Filter", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Flexible Duct Connectors", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Duct Tape (Foil)", "unit": "Rolls", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Drain Pan", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Condensate Pump", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Hanging Straps", "unit": "Rolls", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "26-Electrical": [
            {"name": "12-2 Romex", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Main Panel", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Outlets", "unit": "Count", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Can Lights", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Electrical Boxes", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Wire Nuts", "unit": "Boxes", "default_waste": 2, "labor_difficulty": "Low"},
            {"name": "Conduit Pipe (PVC)", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Light Switches", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Grounding Rod", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Breakers", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Ceiling Fan Rough-in", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Electrical Tape", "unit": "Rolls", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "27-Communications": [
            {"name": "Cat6 Cable", "unit": "Linear Ft.", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "Coax Cable", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Router", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Patch Panel", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Wall Plate (Data)", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "RJ45 Connectors", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Cable Ties", "unit": "Packs", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "J-Hooks", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Fiber Optic Cable", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "Switch Hub", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Cable Conduit", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Labeling Kit", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "31-Earthwork": [
            {"name": "Excavation", "unit": "Hours", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Grading", "unit": "Sq. Ft.", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Gravel", "unit": "Tons", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Trenching", "unit": "Linear Ft.", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Fill Dirt", "unit": "Cu. Yards", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Silt Fence", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Low"},
            {"name": "Geotextile Fabric", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Compaction Testing", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Rip Rap", "unit": "Tons", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Backfill Material", "unit": "Cu. Yards", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Survey Stakes", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Dewatering Pump Rental", "unit": "Days", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "32-Exterior": [
            {"name": "Asphalt", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Pavers", "unit": "Sq. Ft.", "default_waste": 12, "labor_difficulty": "High"},
            {"name": "Sod", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Mulch", "unit": "Cu. Yards", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Concrete Curbing", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Landscape Lighting", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Sprinkler Head (Lawn)", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Topsoil", "unit": "Cu. Yards", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Edging Material", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Retaining Wall Block", "unit": "Count", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Drainage Pipe", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Planting Soil", "unit": "Bags", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "33-Utilities": [
            {"name": "Water Main Pipe", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Sewer Pipe", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Catch Basin", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Backflow Preventer", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Manhole Cover", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Water Meter", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Cleanout Access", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Gas Shut-off Valve", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Electric Conduit (Large)", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Transformer Pad", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Pull Box", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Warning Tape", "unit": "Rolls", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "34-Transportation": [
            {"name": "Traffic Signs", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Bollards", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Parking Stops", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Striping Paint", "unit": "Gallons", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Speed Bumps", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Reflector Studs", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Guard Rail Sections", "unit": "Linear Ft.", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Directional Arrows", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Ticket Dispenser", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Gate Arm", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Curb Ramps", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Wheel Stops", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "40-Process": [
            {"name": "Industrial Pump", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Process Motor", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Inline Filter", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Control Valve", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Pressure Gauge", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Flow Meter", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Seals/Gaskets", "unit": "Kits", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Stainless Steel Pipe", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Pipe Hangers (Heavy Duty)", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Vibration Isolators", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Insulation Jacket", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Thermal Sensor", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "41-Material-Handling": [
            {"name": "Hoist", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Dock Leveler", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Straps", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Safety Netting", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Conveyor Rollers", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Pallet Racking Upright", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Pallet Racking Beam", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Safety Bollards", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Floor Anchors", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Guide Rails", "unit": "Linear Ft.", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Chain Hoist", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Identification Signage", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "42-Process-Heating": [
            {"name": "Industrial Boiler", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Burner Assembly", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "High-Temp Piping", "unit": "Linear Ft.", "default_waste": 8, "labor_difficulty": "High"},
            {"name": "Steam Vent", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Heat Exchanger", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Control Panel", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Refractory Brick", "unit": "Count", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Insulation Blanket", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Temperature Probe", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Expansion Tank", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Fuel Line", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Draft Inducer", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "43-Gas-Liquid": [
            {"name": "Compressor", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Pressure Tank", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Gas Regulator", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "High-Pressure Hose", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Pressure Relief Valve", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Quick-Connect Fitting", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Filter Dryer", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Sight Glass", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Leak Detection Sensor", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Mounting Base", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Liquid Level Switch", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Hydraulic Fluid", "unit": "Gallons", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "44-Pollution-Control": [
            {"name": "Air Scrubber Media", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Exhaust Ducting", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "Emissions Monitor", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Neutralizing Chemical", "unit": "Gallons", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Activated Carbon Filter", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "HEPA Filter Element", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Containment Berm", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Oil-Water Separator", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Sample Port", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Exhaust Stack", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Fan/Blower Motor", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Vibration Dampener", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "45-Industrial": [
            {"name": "Conveyor Section", "unit": "Linear Ft.", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Gearbox Drive", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Heavy Machine Mount", "unit": "Count", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Proximity Sensor", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Emergency Stop Button", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "PLC Module", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Cable Tray", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Motor Starter", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Safety Guarding", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Warning Strobe", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Coupling Element", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Grease Fitting", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"}
        ],
        "46-Water-Systems": [
            {"name": "Filtration Pump", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Filter Media", "unit": "Bags", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Water Treatment Pipe", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Chemical Feed Valve", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "UV Sterilizer", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Reverse Osmosis Membrane", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Backwash Controller", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Storage Tank", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Chemical Storage Drum", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Pipe Union", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Pressure Transducer", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Sampling Faucet", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "48-Electrical-Power": [
            {"name": "Step-Down Transformer", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Industrial Switchgear", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "High-Voltage Cable", "unit": "Linear Ft.", "default_waste": 8, "labor_difficulty": "High"},
            {"name": "Heavy Grounding Rod", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Bus Bar", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Circuit Breaker (Large)", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Surge Protector", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Cable Lug", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Terminal Block", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Disconnect Switch", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Phase Monitor", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "High-Voltage Warning Sign", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "50-Roofing": [
            {"name": "Architectural Shingles", "unit": "Squares", "default_waste": 12, "labor_difficulty": "High"},
            {"name": "Underlayment", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Drip Edge", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Ice & Water Shield", "unit": "Rolls", "default_waste": 7, "labor_difficulty": "Medium"},
            {"name": "Roofing Nails", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Ridge Vent", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Flashing (Valley)", "unit": "Rolls", "default_waste": 10, "labor_difficulty": "High"},
            {"name": "Pipe Boot", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Roof Cement", "unit": "Tubes", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Starter Shingles", "unit": "Bundles", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Step Flashing", "unit": "Count", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Ridge Caps", "unit": "Bundles", "default_waste": 5, "labor_difficulty": "Medium"}
        ],
        "51-Siding": [
            {"name": "Vinyl Panel", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Fiber Cement Board", "unit": "Sq. Ft.", "default_waste": 12, "labor_difficulty": "High"},
            {"name": "Starter Strip", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "House Wrap", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "J-Channel", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Corner Posts", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Siding Nails", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Window/Door Trim", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "F-Channel", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Caulk", "unit": "Tubes", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Soffit Panel", "unit": "Sq. Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Fascia Board", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"}
        ],
        "52-Windows": [
            {"name": "Double Hung", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Slider", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Casement", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Flashing Tape", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Shim Kit", "unit": "Packs", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Low-Expansion Foam", "unit": "Cans", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Exterior Trim Coil", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Interior Casing", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Window Sill", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Caulk", "unit": "Tubes", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Screen Mesh", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Safety Glass Film", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Medium"}
        ],
        "53-Insulation": [
            {"name": "Blown Cellulose", "unit": "Bags", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Foil Radiant Barrier", "unit": "Sq. Ft.", "default_waste": 8, "labor_difficulty": "Medium"},
            {"name": "Acoustic Insulation", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Insulation Staples", "unit": "Boxes", "default_waste": 10, "labor_difficulty": "Low"},
            {"name": "Spray Foam Kit", "unit": "Kits", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Vapor Barrier Tape", "unit": "Rolls", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Rigid Foam Board", "unit": "Sheets", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Mineral Wool Batts", "unit": "Sq. Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Attic Baffles", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Insulation Knives", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Protective Mask", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Wall Cavity Sealant", "unit": "Tubes", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "54-Ceilings": [
            {"name": "Drop Ceiling Tile", "unit": "Count", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Main Grid Runner", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Cross Tee", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Ceiling Wire", "unit": "Rolls", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Wall Molding", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Hanger Eyelet", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Acoustic Sealant", "unit": "Tubes", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Grid Splices", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Toggle Bolts", "unit": "Boxes", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Ceiling Paint", "unit": "Gallons", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Patch Plaster", "unit": "Tubs", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Access Door", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "55-Columns": [
            {"name": "Fiberglass Column", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Wood Wrap Column", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Column Base/Capital", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Structural Steel Post", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Shim Plates", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Adhesive (Heavy Duty)", "unit": "Tubes", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Anchor Bolts", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Primer", "unit": "Quarts", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Exterior Paint", "unit": "Gallons", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Fasteners (Screws)", "unit": "Boxes", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Column Plinth", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Caulk", "unit": "Tubes", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "56-Molding": [
            {"name": "Baseboard", "unit": "Linear Ft.", "default_waste": 15, "labor_difficulty": "Medium"},
            {"name": "Crown Molding", "unit": "Linear Ft.", "default_waste": 20, "labor_difficulty": "High"},
            {"name": "Door/Window Casing", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Chair Rail", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Quarter Round", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Low"},
            {"name": "Finish Nails", "unit": "Boxes", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Wood Filler", "unit": "Tubs", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Paintable Caulk", "unit": "Tubes", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Mitre Saw Blades", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Glue", "unit": "Bottles", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Corner Blocks", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Sandpaper", "unit": "Packs", "default_waste": 0, "labor_difficulty": "None"}
        ],
        "57-Fencing": [
            {"name": "Wood Picket", "unit": "Count", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Fence Post (4x4)", "unit": "Count", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Rail/Stringer", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Concrete Mix (Post)", "unit": "Bags", "default_waste": 5, "labor_difficulty": "High"},
            {"name": "Gate Hardware", "unit": "Kits", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Chain Link Mesh", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Tension Bar", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Post Cap", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Gate Hinges", "unit": "Pairs", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Fence Stain", "unit": "Gallons", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Bracing/Bracket", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Gravel (Base)", "unit": "Bags", "default_waste": 0, "labor_difficulty": "Medium"}
        ],
        "58-Specialties": [
            {"name": "Signage", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Lockers", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Toilet Partitions", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Fire Extinguisher Cabinet", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Wall Guards", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Corner Guards", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Projection Screen", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Flagpole", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Postal Specialties", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Storage Shelving", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Safety Mirrors", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Entrance Mats", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"}
        ],
        "59-Furnishings": [
            {"name": "Window Blinds", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Curtain Tracks", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Waste Receptacles", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Wall Clocks", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Bench Seating", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Art/Wall Decor", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Cubicle Panels", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Desk Hardware", "unit": "Kits", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Coat Racks", "unit": "Count", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Floor Mats", "unit": "Count", "default_waste": 0, "labor_difficulty": "None"},
            {"name": "Mirrors", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Furniture Glides", "unit": "Packs", "default_waste": 0, "labor_difficulty": "Low"}
        ],
        "60-Landscaping": [
            {"name": "Shrubs", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Trees", "unit": "Count", "default_waste": 0, "labor_difficulty": "High"},
            {"name": "Flower Bed Border", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Irrigation Tubing", "unit": "Linear Ft.", "default_waste": 10, "labor_difficulty": "Medium"},
            {"name": "Sprinkler Controller", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"},
            {"name": "Landscape Fabric", "unit": "Rolls", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Decorative Stone", "unit": "Tons", "default_waste": 5, "labor_difficulty": "Medium"},
            {"name": "Bark/Mulch", "unit": "Cu. Yards", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Garden Edging", "unit": "Linear Ft.", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Fertilizer", "unit": "Bags", "default_waste": 0, "labor_difficulty": "Low"},
            {"name": "Grass Seed", "unit": "Bags", "default_waste": 5, "labor_difficulty": "Low"},
            {"name": "Tree Stakes", "unit": "Count", "default_waste": 0, "labor_difficulty": "Medium"}
        ]
    }

def calculate_estimate_data(payload):
    project_info = payload.get('project_info', {})
    materials = payload.get('materials', [])
    zip_code = project_info.get('zipCode', '00000')
    q_level = project_info.get('qualityLevel', 'Standard Grade')
    
    # 2. Quality Level Multiplier logic updated to match new naming
    if q_level == 'Budget Grade': quality_mult = 0.85
    elif q_level == 'Luxury Grade': quality_mult = 1.3
    else: quality_mult = 1.0 # Standard Grade

    market_activity_index = 1.05
    
    logistics_mult = get_logistics_modifier(zip_code)
    tax_rate = get_tax_rate(zip_code)
    
    risk_months = int(payload.get('risk_months', 0))
    inflation_mult = 1.0 + (risk_months * 0.0075) 
    
    catalog = get_golden_catalog()
    processed_items = []
    
    total_min = 0
    total_avg = 0
    total_max = 0
    
    conversions = {"Cu. Yards": 27, "sqyd": 9, "sqft": 1, "linear foot": 1, "each": 1}

    for item in materials:
        cat = item.get('category', '').strip()
        sub = item.get('subcategory', '').strip()
        qty = float(item.get('quantity', 0))
        waste_pct = float(item.get('waste', 0))
        labor_req = item.get('labor', False)

        category_list = catalog.get(cat, [])
        catalog_item = next((x for x in category_list if x["name"] == sub), None)

        labor_diff = catalog_item.get('labor_difficulty', 'Low') if catalog_item else 'Medium'
        if labor_diff == 'High': base_rate = 25.00
        elif labor_diff == 'Medium': base_rate = 15.00
        elif labor_diff == 'Low': base_rate = 8.00
        else: base_rate = 2.00

        effective_rate = base_rate * quality_mult * market_activity_index
        unit = catalog_item.get('unit', 'sqft') if catalog_item else 'sqft'
        multiplier = conversions.get(unit, 1)
        
        final_qty = (qty * multiplier) * (1 + (waste_pct / 100.0))
        
        # 7. Split Material and Labor Costs
        material_cost_base = final_qty * effective_rate
        labor_cost_base = (material_cost_base * 0.6) if labor_req and labor_diff != 'None' else 0

        # Apply macro modifiers
        material_subtotal_avg = material_cost_base * logistics_mult * inflation_mult
        labor_subtotal_avg = labor_cost_base * logistics_mult * inflation_mult
        
        # Unit cost for material
        unit_cost = material_subtotal_avg / final_qty if final_qty > 0 else 0
        conf_score = "96%" if catalog_item and labor_diff == 'Low' else ("91%" if catalog_item else "50% (Custom)")

        # Append Material Row
        mat_min = material_subtotal_avg * 0.85
        mat_max = material_subtotal_avg * 1.25
        
        total_min += mat_min
        total_avg += material_subtotal_avg
        total_max += mat_max

        processed_items.append({
            "name": f"Material: {cat} - {sub}",
            "confidence": conf_score,
            "unit_cost": f"{unit_cost:,.2f} /{unit}",
            "min": f"{mat_min:,.2f}",
            "avg": f"{material_subtotal_avg:,.2f}",
            "max": f"{mat_max:,.2f}"
        })

        # Append Labor Row if selected
        if labor_req:
            lab_min = labor_subtotal_avg * 0.85
            lab_max = labor_subtotal_avg * 1.25
            
            total_min += lab_min
            total_avg += labor_subtotal_avg
            total_max += lab_max
            
            processed_items.append({
                "name": f"Labor: {sub} Installation",
                "confidence": "88%" if catalog_item else "50% (Custom)",
                "unit_cost": None,
                "min": f"{lab_min:,.2f}",
                "avg": f"{labor_subtotal_avg:,.2f}",
                "max": f"{lab_max:,.2f}"
            })

    return {
        "date": datetime.datetime.now().strftime("%B %d, %Y"),
        "project_type": project_info.get('projectType', 'Unknown'),
        "quality_level": q_level,
        "zip_code": zip_code,
        "tax_rate_display": f"{round(tax_rate * 100, 2)}%",
        "items": processed_items,
        "subtotal_min": f"{total_min:,.2f}",
        "subtotal_avg": f"{total_avg:,.2f}",
        "subtotal_max": f"{total_max:,.2f}",
        "tax_min": f"{(total_min * tax_rate):,.2f}",
        "tax_avg": f"{(total_avg * tax_rate):,.2f}",
        "tax_max": f"{(total_max * tax_rate):,.2f}",
        "grand_total_min": f"{(total_min * (1 + tax_rate)):,.2f}",
        "grand_total_avg": f"{(total_avg * (1 + tax_rate)):,.2f}",
        "grand_total_max": f"{(total_max * (1 + tax_rate)):,.2f}"
    }

# --- 2. ROUTES ---

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api/catalog', methods=['GET'])
def get_catalog():
    return jsonify(get_golden_catalog())

@app.route('/api/calculate', methods=['POST'])
def calculate_totals():
    try:
        return jsonify(calculate_estimate_data(request.get_json()))
    except Exception as e:
        print(f"CRITICAL ERROR: {e}") 
        return "Internal Server Error", 500

@app.route('/api/report', methods=['POST'])
def generate_report():
    try:
        report_data = calculate_estimate_data(request.get_json())
        # Uses the embedded PDF string instead of an external file
        rendered_html = render_template_string(PDF_TEMPLATE, data=report_data)
        pdf = HTML(string=rendered_html).write_pdf()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=Predictive_Pricing_Report.pdf'
        return response
    except Exception as e:
        print(f"CRITICAL ERROR PDF: {e}") 
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run()
