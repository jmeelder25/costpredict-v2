import pandas as pd
import os
import json
import time
from google import genai

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_pricing_from_ai(category, items, zip_code, is_new=False):
    """Asks Gemini to standardize and price items based on a specific zip code."""
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
        print(f"DEBUG: AI Error: {e}")
        return []

def enrich_and_save():
    os.makedirs('data', exist_ok=True)
    
    category = os.environ.get("CURRENT_CATEGORY")
    zip_code = os.environ.get("TARGET_ZIP", "60601") # Default to Chicago
    
    if not category: return
    
    filename = os.path.join('data', f"{category}.csv")
    
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        item_list = df['item_name'].dropna().tolist()
        print(f"Standardizing {len(item_list)} items for {category} in {zip_code}...")
        
        data = get_pricing_from_ai(category, item_list, zip_code, is_new=False)
        if data:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            print(f"Success! Updated {category}")
    else:
        print(f"Generating new catalog for {category} in {zip_code}...")
        data = get_pricing_from_ai(category, [], zip_code, is_new=True)
        if data:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            print(f"Success! Created {category}")

if __name__ == "__main__":
    enrich_and_save()
