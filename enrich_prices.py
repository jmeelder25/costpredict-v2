import pandas as pd
import os
import json
from google import genai

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_ai_pricing_estimate(item_name):
    """Generates synthetic pricing via Gemini when scraping fails."""
    prompt = f"""
    Provide realistic current market pricing for a construction material called '{item_name}'.
    Return ONLY a valid JSON object with keys: 
    "min_mat", "avg_mat", "max_mat", "min_lab", "avg_lab", "max_lab".
    Use float values only.
    """
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return json.loads(response.text)

def enrich_and_save():
    raw_file = 'raw_scraped_data.csv'
    
    # 1. Handle Missing Raw Data with AI Fallback
    if not os.path.exists(raw_file):
        print(f"Warning: '{raw_file}' not found. Generating synthetic data via Gemini...")
        # Define a list of items you want in your catalog
        items = ["steel angle", "aluminum sheet", "pine lumber", "drywall", "concrete mix"]
        data = []
        for item in items:
            estimate = get_ai_pricing_estimate(item)
            estimate['item_name'] = item
            data.append(estimate)
        df = pd.DataFrame(data)
    else:
        try:
            df = pd.read_csv(raw_file)
            df = df.iloc[:, :7]
            df.columns = ['item_name', 'min_mat', 'avg_mat', 'max_mat', 'min_lab', 'avg_lab', 'max_lab']
        except Exception as e:
            print(f"Error reading raw file: {e}")
            return

    # 2. Data Validation
    pricing_cols = ['min_mat', 'avg_mat', 'max_mat', 'min_lab', 'avg_lab', 'max_lab']
    for col in pricing_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    # 3. Save Output
    os.makedirs('data', exist_ok=True)
    output_path = os.path.join('data', 'Catalog Materials.csv')
    df.to_csv(output_path, index=False)
    
    print(f"Success! Saved data to: {output_path}")

if __name__ == "__main__":
    enrich_and_save()
