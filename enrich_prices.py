import pandas as pd
import os

def enrich_and_save():
    # 1. Load your raw data
    raw_file = 'raw_scraped_data.csv'
    if not os.path.exists(raw_file):
        print(f"Error: '{raw_file}' not found. Please make sure your scraper generated this file first.")
        return

    try:
        df = pd.read_csv(raw_file)
    except Exception as e:
        print(f"Error reading raw file: {e}")
        return

    # 2. Cleanup: Truncate to the first 7 columns to remove ghost empty columns
    df = df.iloc[:, :7]

    # 3. Rename columns to exactly match what the new main.py engine uses
    df.columns = ['item_name', 'min_mat', 'avg_mat', 'max_mat', 'min_lab', 'avg_lab', 'max_lab']

    # 4. Data Validation: Force prices to be numbers so we don't get $NaN
    pricing_cols = ['min_mat', 'avg_mat', 'max_mat', 'min_lab', 'avg_lab', 'max_lab']
    for col in pricing_cols:
        # Clean up any currency symbols or commas if they exist
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    # 5. Ensure the 'data/' directory exists for main.py
    os.makedirs('data', exist_ok=True)

    # 6. Save as a standardized category file for main.py
    # Since the raw file has everything lumped together, we will save it as 'Catalog Materials.csv'
    output_path = os.path.join('data', 'Catalog Materials.csv')
    df.to_csv(output_path, index=False)
    
    print(f"Success! Saved cleaned data to: {output_path}")
    print("You can now run main.py and your prices will populate perfectly.")

if __name__ == "__main__":
    enrich_and_save()
