import pandas as pd
import os
import json
from google import genai

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_ai_pricing_estimate(item_name):
    """Generates synthetic pricing with a stricter prompt and parsing logic."""
    prompt = f"""
    Provide realistic current market pricing for a construction material called '{item_name}'.
    Return ONLY a raw JSON object with exactly these keys: 
    "min_mat", "avg_mat", "max_mat", "min_lab", "avg_lab", "max_lab".
    Do not include markdown code blocks, do not include prefixes or suffixes.
    Example: {{"min_mat": 10.0, "avg_mat": 12.0, "max_mat": 15.0, "min_lab": 5.0, "avg_lab": 7.0, "max_lab": 10.0}}
    """
    
    # FIX: Using the currently active and supported model endpoint
    response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
    
    # Strip markdown and whitespace
    text = response.text.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"DEBUG: Failed to parse JSON from Gemini. Raw response was: {response.text}")
        # Return default values so the pipeline survives
        return {"min_mat": 0.0, "avg_mat": 0.0, "max_mat": 0.0, "min_lab": 0.0, "avg_lab": 0.0, "max_lab": 0.0}

def enrich_and_save():
    raw_file = 'raw_scraped_data.csv'
    
    # 1. Load Data or Generate Synthetic Data
    if not os.path.exists(raw_file):
        print("Warning: 'raw_scraped_data.csv' not found. Generating synthetic data via Gemini...")
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

    # 2. Cleanup and Validation
    pricing_cols = ['min_mat', 'avg_mat', 'max_mat', 'min_lab', 'avg_lab', 'max_lab']
    for col in pricing_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    # 3. Save as standardized CSV
    os.makedirs('data', exist_ok=True)
    output_path = os.path.join('data', 'Catalog Materials.csv')
    df.to_csv(output_path, index=False)
    
    print(f"Success! Saved data to: {output_path}")

if __name__ == "__main__":
    enrich_and_save()
