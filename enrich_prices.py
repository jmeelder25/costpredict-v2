import asyncio
import csv
import datetime
import os
import re
import glob  # Added to read all files in the directory
from playwright.async_api import async_playwright
import pandas as pd

# CONFIGURATION
DATA_FOLDER = "data"       # The folder containing all your category CSVs
OUTPUT_CSV = "master_data.csv"

# Map your CSV item names to their online tracking URLs and specific CSS selectors
SCRAPER_TARGETS = {
    "Steel Beam": {
        "url": "https://www.metalsdepot.com/steel-products/steel-beams", 
        "selector": ".price"
    },
    "OSB Sheathing": {
        "url": "https://www.homedepot.com/p/OSB-Sheathing-7-16-in-x-4-ft-x-8-ft/202106230", 
        "selector": ".price-format__main-price"
    }
    # Add your other monthly lookup mappings here...
}

def clean_and_parse_price(price_text):
    if not price_text:
        return 0.0
    clean_str = price_text.replace('\n', '').strip()
    numbers_only = re.sub(r'[^\d.]', '', clean_str)
    try:
        return float(numbers_only)
    except ValueError:
        return 0.0

def calculate_pricing_ranges(base_price):
    return {
        "min_mat": round(base_price * 0.85, 2),
        "avg_mat": round(base_price, 2),
        "max_mat": round(base_price * 1.20, 2),
        "min_lab": round(base_price * 0.40, 2),
        "avg_lab": round(base_price * 0.65, 2),
        "max_lab": round(base_price * 0.90, 2)
    }

async def run_enrichment_pipeline():
    if not os.path.exists(DATA_FOLDER):
        print(f"❌ Error: Data folder '{DATA_FOLDER}' not found.")
        return

    # Find all CSV files inside the data directory
    csv_files = glob.glob(os.path.join(DATA_FOLDER, "*.csv"))
    if not csv_files:
        print(f"❌ Error: No CSV files found inside '{DATA_FOLDER}'.")
        return

    print(f"📚 Found {len(csv_files)} category files inside '{DATA_FOLDER}'.")
    
    # This list will hold the processed dataframes from each file
    all_categories_data = []

    # Initialize Playwright Browser
    async with async_playwright() as p:
        print("🌐 Launching headless browser environment...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Loop through each category CSV file
        for file_path in csv_files:
            print(f"📖 Processing Category File: {os.path.basename(file_path)}")
            df = pd.read_csv(file_path)
            
            # Ensure target destination columns exist in this specific DataFrame
            target_columns = ['min_mat', 'avg_mat', 'max_mat', 'min_lab', 'avg_lab', 'max_lab']
            for col in target_columns:
                if col not in df.columns:
                    df[col] = None

            name_col = df.columns[0]

            # Loop over every line item inside this specific category file
            for index, row in df.iterrows():
                item_name = str(row[name_col]).strip()
                
                if not item_name or item_name.lower() in ["nan", ""]:
                    continue
                
                # Check if we have an active tracking rule set up for this specific item name
                if item_name in SCRAPER_TARGETS:
                    target = SCRAPER_TARGETS[item_name]
                    try:
                        print(f"  🔍 Scraping market rate for: {item_name}")
                        await page.goto(target['url'], wait_until="networkidle", timeout=60000)
                        
                        price_element = await page.wait_for_selector(target['selector'], timeout=15000)
                        raw_text = await price_element.inner_text()
                        
                        base_price = clean_and_parse_price(raw_text)
                        print(f"     ↳ Extracted: ${base_price}")
                        
                        if base_price == 0.0:
                            raise ValueError("Parsed numerical total yielded $0.00")

                    except Exception as e:
                        print(f"  ⚠️ Scraping failed for {item_name}: {str(e)}. Using fallback baseline.")
                        base_price = 50.00  
                else:
                    # Fallback baseline for items not yet explicitly mapped in SCRAPER_TARGETS
                    base_price = 45.00

                # Calculate metrics
                ranges = calculate_pricing_ranges(base_price)
                
                # Write back into the dataframe row
                df.at[index, 'min_mat'] = ranges['min_mat']
                df.at[index, 'avg_mat'] = ranges['avg_mat']
                df.at[index, 'max_mat'] = ranges['max_mat']
                df.at[index, 'min_lab'] = ranges['min_lab']
                df.at[index, 'avg_lab'] = ranges['avg_lab']
                df.at[index, 'max_lab'] = ranges['max_lab']
                
                await asyncio.sleep(1.0)
            
            # Add this fully processed category data to our list
            all_categories_data.append(df)

        await browser.close()

    # Concatenate all individual categories into one master dataframe matrix
    print("🔄 Combining all category sheets into a single master file...")
    master_df = pd.concat(all_categories_data, ignore_index=True)
    
    # Save out the compiled sheet next to main.py
    master_df.to_csv(OUTPUT_CSV, index=False)
    print(f"🎉 Pipeline Complete! Combined enriched dataset successfully exported to '{OUTPUT_CSV}'.")

if __name__ == "__main__":
    asyncio.run(run_enrichment_pipeline())
