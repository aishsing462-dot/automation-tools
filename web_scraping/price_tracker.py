import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
TRACKING_FILE = os.path.expanduser("~/Documents/price_tracking_list.json")
LOG_FILE = os.path.expanduser("~/Documents/price_history.csv")

# Sample data structure if file doesn't exist
DEFAULT_TRACKING = [
    {
        "name": "Sample Product",
        "url": "https://www.example.com",
        "selector": ".price",
        "target_price": 100.0
    }
]

async def get_price(page, url, selector):
    try:
        await page.goto(url, wait_until="networkidle", timeout=60000)
        # Wait for the selector to appear
        await page.wait_for_selector(selector, timeout=10000)
        price_text = await page.inner_text(selector)

        # Clean the price string (remove currency symbols, commas, etc.)
        # This is a simple regex-like approach
        price_digits = ''.join(c for c in price_text if c.isdigit() or c == '.')
        return float(price_digits)
    except Exception as e:
        print(f"Error fetching price for {url}: {e}")
        return None

async def track_prices():
    if not os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "w") as f:
            json.dump(DEFAULT_TRACKING, f, indent=4)
        print(f"Created sample tracking file at {TRACKING_FILE}")

    with open(TRACKING_FILE, "r") as f:
        items = json.load(f)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("Timestamp,Product,Price,TargetReached\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use a real-looking user agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        results = []
        for item in items:
            print(f"Checking price for: {item['name']}...")
            price = await get_price(page, item['url'], item['selector'])

            if price is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                target_reached = price <= item['target_price']

                with open(LOG_FILE, "a") as f:
                    f.write(f"{timestamp},{item['name']},{price},{target_reached}\n")

                results.append({
                    "name": item['name'],
                    "price": price,
                    "target_reached": target_reached
                })
                print(f"Current price for {item['name']}: {price} (Target: {item['target_price']})")
            else:
                print(f"Failed to get price for {item['name']}")

        await browser.close()
    return results

if __name__ == "__main__":
    asyncio.run(track_prices())
