import os
import glob
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify

# Note: Your requirements.txt libraries (weasyprint, pydyf, fonttools, Pillow, python-dotenv) 
# are fully supported and ready to be utilized alongside this core engine structure.

app = Flask(__name__)

# Global memory cache to serve the dynamic search engine instantly
MASTER_DATA_CACHE = {}

def load_master_data():
    """
    Scans the data directory, parses all 38 category CSV spreadsheets, 
    and packages them into a structured object for the frontend search bar.
    """
    master_data = {}
    
    # Locate all exported CSV sheets inside the data folder
    csv_files = glob.glob(os.path.join("data", "*.csv"))
    
    # Standard Master Division CSI Code mappings for construction structural accuracy
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
        
        # Parse the raw sheet filename back into a clean primary category name
        # Handles both clean names ('Windows.csv') and workbook exports ('Building Materials Spreadsheet.xlsx - Windows.csv')
        category_name = filename.replace("Building Materials Spreadsheet.xlsx - ", "").replace(".csv", "")
        
        # Omit internal metadata sheets or retail store configurations
        if category_name in ["Stores", "Summary"]:
            continue
            
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                continue
                
            # Read the first column containing item/subcategory string structures
            first_column = df.columns[0]
            items_list = df[first_column].dropna().unique().tolist()
            
            # Formatting sanitation: strip extra spaces and drop row matching the header itself
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

def append_to_category_sheet(category_name, new_item_name):
    """
    Appends a uniquely crawled search engine scrape or manual user override line item
    safely to the correct corresponding master file spreadsheet column.
    """
    category_clean = category_name.strip()
    item_clean = new_item_name.strip()
    
    if not category_clean or not item_clean:
        return False, "Category or item field parameters are invalid."

    possible_filenames = [
        f"{category_clean}.csv",
        f"Building Materials Spreadsheet.xlsx - {category_clean}.csv"
    ]
    
    file_path = None
    for fname in possible_filenames:
        target = os.path.join("data", fname)
        if os.path.exists(target):
            file_path = target
            break
            
    # Fallback: Create a clean category file structure if it doesn't exist
    if not file_path:
        file_path = os.path.join("data", f"{category_clean}.csv")
        df = pd.DataFrame(columns=[category_clean])
        df.to_csv(file_path, index=False)

    try:
        # Load existing spreadsheet
        df = pd.read_csv(file_path)
        first_column = df.columns[0]
        
        # De-duplication filter evaluation running in lowercase comparison
        existing_items = df[first_column].dropna().astype(str).str.lower().str.strip().tolist()
        if item_clean.lower() in existing_items:
            return True, "Item already indexed in the master data directory."
            
        # Append the refinement data row cleanly to the dataframe
        new_row = pd.DataFrame([{first_column: item_clean}])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Overwrite back out to disc safely
        df.to_csv(file_path, index=False)
        print(f"[REFINEMENT PIPELINE] Added '{item_clean}' to {file_path}")
        
        # Hot-reload the core data cache instantly for live search querying
        global MASTER_DATA_CACHE
        MASTER_DATA_CACHE = load_master_data()
        
        return True, "Spreadsheet successfully updated and re-compiled."
        
    except Exception as e:
        return False, f"Failed updating file row: {str(e)}"


# --- SERVER RUNTIME INITIALIZATION ---

# Pre-compile the spreadsheet structures when the server boots
MASTER_DATA_CACHE = load_master_data()


@app.route('/')
def index():
    """
    Serves the primary mobile scope-builder page, passing down 
    the active Master Data cache payload as safe JSON text.
    """
    return render_template('index.html', master_data=json.dumps(MASTER_DATA_CACHE))


@app.route('/api/refine', methods=['POST'])
def refine_master_file():
    """
    API Receiver Hook endpoint. Receives payloads from automated search engine web-scrapes
    or manual user layout overrides to push items down into the dataset sheets.
    """
    payload = request.get_json() or {}
    category = payload.get('category')
    item_name = payload.get('item_name')
    
    if not category or not item_name:
        return jsonify({"status": "error", "message": "Missing category or item_name string values."}), 400
        
    success, message = append_to_category_sheet(category, item_name)
    
    if success:
        return jsonify({"status": "success", "message": message}), 200
    return jsonify({"status": "error", "message": message}), 500


@app.route('/generate', methods=['POST'])
def generate_pdf():
    """
    Placeholder for your existing PDF generation payload. Connects 
    directly to your front end's 'Export Verified PDF Report' button submission.
    """
    # Your active WeasyPrint / pydyf layout generation code goes right here
    payload_data = request.form.get('payload')
    print(f"[PDF ENGINE] Received compilation scope: {payload_data}")
    
    # Replace this placeholder return with your actual PDF binary attachment stream response
    return jsonify({"status": "success", "message": "PDF layout received by engine."}), 200


if __name__ == '__main__':
    # Render assigns a dynamic port variable automatically; defaults to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
