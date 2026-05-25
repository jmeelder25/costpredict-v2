import pandas as pd
import os
import json
from google import genai

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Mapping logic to place items into their correct files
def get_category(item_name):
    # This acts as a simple router for your 30+ files
    item = item_name.lower()
    if 'drywall' in item: return 'Drywall'
    if 'lumber' in item or 'pine' in item: return 'Lumber and Composites'
    if 'steel' in item or 'metal' in item: return 'Metals'
    if 'concrete' in item: return 'Concrete and Cement and Masonry'
    return 'Builders Hardware' # Default fallback

def get_ai_pricing_estimate(item_name):
    prompt = f"""
    Provide realistic current market pricing for a construction material called '{item_name}'.
    Return ONLY a raw JSON object with these keys: 
    "min_mat", "avg_mat", "max_mat", "min_lab", "avg_lab", "max_lab".
    Do not include markdown code blocks or any other text.
    """
    response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
    text = response.text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except:
        return {"min_mat": 0.0, "avg_mat": 0.0, "max_mat": 0.0, "min_lab": 0.0, "avg_lab": 0.0, "max_lab": 0.0}

def enrich_and_save():
    raw_file = 'raw_scraped_data.csv'
    
    # 1. Gather Data
    if not os.path.exists(raw_file):
        items = ["steel angle", "aluminum sheet", "pine lumber", "drywall", "concrete mix"]
        data = []
        for item in items:
            row = get_ai_pricing_estimate(item)
            row['item_name'] = item
            row['category'] = get_category(item)
            data.append(row)
        df = pd.DataFrame(data)
    else:
        df = pd.read_csv(raw_file)
        # Ensure category exists
        if 'category' not in df.columns:
            df['category'] = df['item_name'].apply(get_category)

    # 2. Cleanup and Save per Category
    os.makedirs('data', exist_ok=True)
    
    # Group by category and save individual files
    for category, group in df.groupby('category'):
        filename = f"{category}.csv"
        # Force column order
        group = group[['item_name', 'min_mat', 'avg_mat', 'max_mat', 'min_lab', 'avg_lab', 'max_lab']]
        group.to_csv(os.path.join('data', filename), index=False)
        print(f"Generated: {filename}")

if __name__ == "__main__":
    enrich_and_save()
