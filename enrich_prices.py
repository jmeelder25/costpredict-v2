import pandas as pd
import os
import json
import sys
from google import genai

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_pricing_for_zip(category, zip_code):
    """Enriches data for a specific category and zip code."""
    prompt = f"""
    You are an expert construction estimator.
    Provide current market pricing for '{category}' in Zip Code: {zip_code}.
    Return ONLY a raw JSON array of objects.
    Keys: "item_name", "min_mat", "avg_mat", "max_mat", "min_lab", "avg_lab", "max_lab"
    """
    try:
        response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    if len(sys.argv) < 3:
        print("Usage: python enrich_prices.py <category> <zip_code>")
        return
    
    category, zip_code = sys.argv[1], sys.argv[2]
    output_dir = os.path.join('data', zip_code)
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{category}.csv")
    
    print(f"Generating data for {category} in {zip_code}...")
    data = get_pricing_for_zip(category, zip_code)
    
    if data:
        pd.DataFrame(data).to_csv(filename, index=False)
        print(f"Successfully saved to {filename}")

if __name__ == "__main__":
    main()
