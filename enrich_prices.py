import pandas as pd
import os

def enrich_and_save():
    # 1. Load your raw data
    # Change 'raw_scraped_data.csv' to the actual name of your scraped file
    try:
        df = pd.read_csv('raw_scraped_data.csv')
    except FileNotFoundError:
        print("Error: Raw source file not found.")
        return

    # 2. Cleanup: Truncate to the first 7 columns to remove all the 'ghost' empty columns
    # This keeps: [Item, min_mat, avg_mat, max_mat, min_lab, avg_lab, max_lab]
    df = df.iloc[:, :7]

    # 3. Rename columns to match what the frontend expects
    df.columns = ['Subcategory', 'min_mat', 'avg_mat', 'max_mat', 'min_lab', 'avg_lab', 'max_lab']

    # 4. Insert a 'Category' column so the frontend dropdown has a parent
    # You can change 'Catalog Materials' to a more specific name if needed
    df.insert(0, 'Category', 'Catalog Materials')

    # 5. Data Validation: Ensure numeric types for pricing
    pricing_cols = ['min_mat', 'avg_mat', 'max_mat', 'min_lab', 'avg_lab', 'max_lab']
    for col in pricing_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 6. Save to master_data.csv (The file your app reads)
    # index=False is critical to prevent the random '0, 1, 2' index column
    df.to_csv('master_data.csv', index=False)
    
    print("Success: master_data.csv has been cleaned and synced.")

if __name__ == "__main__":
    enrich_and_save()
