import pandas as pd
import os
import json
from google import genai
from datetime import datetime

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_pricing_from_ai(category, items, zip_code, is_new=False):
    """Standardizes or generates items localized to a specific Zip Code."""
    action = "generate a comprehensive catalog" if is_new else "standardize and price"
    prompt = f"""
    You are an expert construction estimator.
    Task: {action} for the category '{category}' in Zip Code: {zip_code}.
    
    Guidelines:
    1. Adjust costs (material and labor) to reflect the local market conditions for {zip_code}.
    2. Use professional industry terminology.
    3. Include varied grades/sizes.
    4. {'Input list: ' + ', '.join(items) if not is_new else 'Provide an exhaustive list.'}
    
    Return ONLY a raw JSON array of objects. Do not include markdown.
    Keys: "item_name", "min_mat", "avg_mat", "max_mat", "min_lab", "avg_lab", "max_lab"
    """
    try:
        response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"DEBUG: AI Error for {category}: {e}")
        return []

def enrich_and_save():
    category = os.environ.get("CURRENT_CATEGORY")
    zip_code = os.environ.get("TARGET_ZIP", "60601")
    
    if not category: return
    
    # Organize data by zip code folder
    output_dir = os.path.join('data', zip_code)
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{category}.csv")
    
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        item_list = df['item_name'].dropna().tolist()
        data = get_pricing_from_ai(category, item_list, zip_code, is_new=False)
    else:
        data = get_pricing_from_ai(category, [], zip_code, is_new=True)
        
    if data:
        pd.DataFrame(data).to_csv(filename, index=False)
        print(f"Success! Saved {category} for {zip_code}")

if __name__ == "__main__":
    enrich_and_save()
