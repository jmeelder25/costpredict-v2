import asyncio
from playwright.async_api import async_playwright
import csv
import datetime

# Example list of URLs to track (You would populate this from your CSV)
materials_to_track = [
    {"name": "OSB Sheathing", "url": "https://www.example-supplier.com/p/osb-sheathing/12345", "selector": ".price-value"},
    {"name": "2x4 Stud", "url": "https://www.example-supplier.com/p/2x4-stud/67890", "selector": "[data-automation-id='price']"}
]

async def scrape_material_prices():
    async with async_playwright() as p:
        # Launch browser (headless=True means it runs in the background)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        results = []
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")

        for material in materials_to_track:
            try:
                print(f"Fetching price for: {material['name']}...")
                await page.goto(material['url'], wait_until="networkidle")
                
                # Find the price using the CSS selector
                price_element = await page.wait_for_selector(material['selector'])
                price_text = await price_element.inner_text()
                
                results.append([timestamp, material['name'], price_text.strip()])
            except Exception as e:
                print(f"Failed to scrape {material['name']}: {e}")

        await browser.close()

        # Save results to a CSV for your records
        with open('price_history.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(results)
        
        print("Scrape complete. Data saved to price_history.csv")

if __name__ == "__main__":
    asyncio.run(scrape_material_prices())
