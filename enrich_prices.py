import pandas as pd
import os
import json
import time
from google import genai

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def standardize_existing_items(category_name, item_names):
    """Standardizes and prices EXISTING items."""
    prompt = f"""
    You are an expert construction estimator.
    I have a rough list of subcategories for '{category_name}': {', '.join(item_names)}
    
    1. Standardize and rename each to professional construction industry norms.
    2. Provide realistic current market pricing.
    
    Return ONLY a raw JSON array of objects. Do not include markdown formatting.
    Keys must be: "original_name", "standardized_name", "min_mat", "avg_mat", "max_mat", "min_lab", "avg_lab", "max_lab"
    """
    try:
        response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"DEBUG: Failed to standardize {category_name}. Error: {e}")
        return []

def generate_new_catalog(category_name):
    """Generates an exhaustive, professional catalog for a new category."""
    prompt = f"""
    You are an expert construction estimator.
    Create an exhaustive list of standard construction materials/subcategories for the category '{category_name}'.
    
    Guidelines:
    1. Include every standard material, fixture, or component typical for a professional estimation.
    2. Use professional industry terminology.
    3. Include varied grades, sizes, and common variations.
    4. Provide realistic current market pricing.
    
    Return ONLY a raw JSON array of objects. Do not include markdown formatting.
    Keys must be: "item_name", "min_mat", "avg_mat", "max_mat", "min_lab", "avg_lab", "max_lab"
    """
    try:
        response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"DEBUG: Failed to generate full catalog for {category_name}. Error: {e}")
        return []

def enrich_and_save():
    os.makedirs('data', exist_ok=True)
    
    # Get the category from the environment variable (Matrix Strategy)
    category = os.environ.get("CURRENT_CATEGORY")
    if not category:
        print("Error: No CURRENT_CATEGORY set.")
        return
    
    filename = os.path.join('data', f"{category}.csv")
    
    # SCENARIO A: File exists (Standardize it)
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            if 'item_name' not in df.columns or df.empty:
                return
            
            item_list = df['item_name'].dropna().tolist()
            print(f"Standardizing {len(item_list)} existing items for: {category}...")
            
            priced_data = standardize_existing_items(category, item_list)
            
            if priced_data:
                priced_df = pd.DataFrame(priced_data)
                for index, row in priced_df.iterrows():
                    mask = df['item_name'] == row.get('original_name', '')
                    if mask.any():
                        for col in ['min_mat', 'avg_mat', 'max_mat', 'min_lab', 'avg_lab', 'max_lab']:
                            if col in row: df.loc[mask, col] = row[col]
                        if 'standardized_name' in row:
                            df.loc[mask, 'item_name'] = row['standardized_name']
                            
                df.to_csv(filename, index=False)
                print(f"Success! Standardized {category}")
        except Exception as e:
            print(f"Error processing {category}: {e}")
            
    # SCENARIO B: File is missing (Invent it)
    else:
        print(f"New category detected! Generating full catalog for: {category}...")
        new_data = generate_new_catalog(category)
        
        if new_data and len(new_data) > 0:
            df = pd.DataFrame(new_data)
            df = df[['item_name', 'min_mat', 'avg_mat', 'max_mat', 'min_lab', 'avg_lab', 'max_lab']]
            df.to_csv(filename, index=False)
            print(f"Success! Created new file for {category}")
        else:
            print(f"Warning: Failed to generate data for {category}")

if __name__ == "__main__":
    enrich_and_save()
