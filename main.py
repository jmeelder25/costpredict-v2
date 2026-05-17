import os
import glob
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Global runtime container cache
MASTER_DATA_CACHE = {}

def load_master_data():
    """
    Scans the data directory, parses all 38 category CSV spreadsheets, 
    and packages them into a structured object for the frontend autocomplete engines.
    """
    master_data = {}
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
                master_data[category_name] = {
                    "code": csi_codes.get(category_name, "09 00 00"),
                    "unit": "SF" if category_name in ["Flooring", "Drywall", "Countertops", "Concrete"] else "PCS",
                    "items": sorted(clean_items)
                }
        except Exception as e:
            print(f"[ERROR] Failed parsing spreadsheet file {filename}: {e}")
            
    return master_data


# --- SERVER RUNTIME INITIALIZATION ---

MASTER_DATA_CACHE = load_master_data()

@app.route('/')
def index():
    """
    Serves the scope builder page, passing down the compiled spreadsheet object.
    """
    return render_template('index.html', master_data=json.dumps(MASTER_DATA_CACHE))


@app.route('/generate', methods=['POST'])
def generate_pdf():
    """
    Receives evaluation parameters for document printing generation.
    """
    payload_data = request.form.get('payload')
    print(f"[PDF ENGINE] Compilation target payload received: {payload_data}")
    return jsonify({"status": "success", "message": "PDF layout received by engine."}), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
