import asyncio
import csv
import datetime
import os
import re
from playwright.async_api import async_playwright
import pandas as pd

# CONFIGURATION
INPUT_CSV = "master_data_blank.csv"
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
    """Extracts a clean numerical float value from dirty scraper strings."""
    if not price_text:
        return 0.0
    # Strip whitespace, newlines, and extract numbers/decimals only (handles $ or formatting)
    clean_str = price_text.replace('\n', '').strip()
    numbers_only = re.sub(r'[^\d.]', '', clean_str)
    try:
        return float(numbers_only)
    except ValueError:
        return 0.0

def calculate_pricing_ranges(base_price):
    """Derives structural min/avg/max intervals for both material and labor."""
    return {
        "min_mat": round(base_price * 0.85, 2),
        "avg_mat": round(base_price, 2),
        "max_mat": round(base_price * 1.20, 2),
        "min_lab": round(base_price * 0.40, 2),
        "avg_lab": round(base_price * 0.65, 2),
        "max_lab": round(base_price * 0.90, 2)
    }

async def run_enrichment_pipeline():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ Error: Base file '{INPUT_CSV}' not found.")
        return

    print(f"📖 Loading base sheet: {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV)
    
    # Ensure target destination columns exist in the DataFrame
    target_columns = ['min_mat', 'avg_mat', 'max_mat', 'min_lab', 'avg_lab', 'max_lab']
    for col in target_columns:
        if col not in df.columns:
            df[col] = None

    name_col = df.columns[0]

    # Initialize Playwright Browser
    async with async_playwright() as p:
        print("🌐 Launching headless browser environment...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Loop over every line item inside your CSV
        for index, row in df.iterrows():
            item_name = str(row[name_col]).strip()
            
            if not item_name or item_name.lower() in ["nan", ""]:
                continue
            
            # Check if we have an active tracking rule set up for this specific item name
            if item_name in SCRAPER_TARGETS:
                target = SCRAPER_TARGETS[item_name]
                try:
                    print(f"🔍 Scraping market rate for: {item_name}")
                    await page.goto(target['url'], wait_until="networkidle", timeout=60000)
                    
                    price_element = await page.wait_for_selector(target['selector'], timeout=15000)
                    raw_text = await price_element.inner_text()
                    
                    base_price = clean_and_parse_price(raw_text)
                    print(f"   ↳ Extracted Raw Value: '{raw_text.strip()}' -> Parsed: ${base_price}")
                    
                    if base_price == 0.0:
                        raise ValueError("Parsed numerical total yielded $0.00")

                except Exception as e:
                    print(f"⚠️ Scraping failed for {item_name}: {str(e)}. Using fallback baseline.")
                    base_price = 50.00  # Set standard backup price if a vendor site blocks the request
            else:
                # Fallback baseline for items in your CSV not yet mapped in SCRAPER_TARGETS
                base_price = 45.00

            # Calculate metrics
            ranges = calculate_pricing_ranges(base_price)
            
            # Write directly to our Pandas row iteration pointer
            df.at[index, 'min_mat'] = ranges['min_mat']
            df.at[index, 'avg_mat'] = ranges['avg_mat']
            df.at[index, 'max_mat'] = ranges['max_mat']
            df
