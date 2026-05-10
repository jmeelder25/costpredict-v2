import asyncio
from playwright.async_api import async_playwright
import csv
import datetime
import os

# CONFIGURATION: Add the specific URLs you want to track here
# Note: Selectors must be updated if the website design changes
materials_to_track = [
    {
        "name": "Steel Beam", 
        "url": "https://www.metalsdepot.com/steel-products/steel-beams", 
        "selector": ".price"
    },
    {
        "name": "OSB Sheathing", 
        "url": "https://www.homedepot.com/p/OSB-Sheathing-7-16-in-x-4-ft-x-8-ft/202106230", 
        "selector": ".price-format__main-price"
    }
]

async def run_scraper():
    async with async_playwright() as p:
        # Launch browser with settings for cloud environments
        browser = await p.chromium.launch(headless=True)
        
        # Set a User-Agent so the website thinks you are a real person
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        results = []
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")

        for material in materials_to_track:
            try:
                print(f"Analyzing {material['name']}...")
                # Wait for the network to be quiet before looking for the price
                await page.goto(material['url'], wait_until="networkidle", timeout=60000)
                
                # Look for the price element
                price_element = await page.wait_for_selector(material['selector'], timeout=10000)
                price_text = await price_element.inner_text()
                
                # Clean up the text (remove symbols/whitespace)
                clean_price = price_text.replace('\n', '').strip()
                results.append([timestamp, material['name'], clean_price])
                print(f"Found: {clean_price}")
                
            except Exception as e:
                print(f"Error scraping {material['name']}: {str(e)}")

        await browser.close()

        # Write results to the CSV
        file_exists = os.path.isfile('price_history.csv')
        with open('price_history.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Add header only if the file is being created for the first time
            if not file_exists:
                writer.writerow(['Date', 'Material', 'Price'])
            writer.writerows(results)
        
        print("Scrape cycle complete.")

if __name__ == "__main__":
    asyncio.run(run_scraper())
