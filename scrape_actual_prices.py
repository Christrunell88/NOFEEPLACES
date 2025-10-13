#!/usr/bin/env python3
"""
Scrape ACTUAL Prices from Building Websites
Get the real listed prices, not estimates
"""

import asyncio
from playwright.async_api import async_playwright
import re
import json
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')


async def scrape_actual_prices():
    """Scrape actual prices from building websites"""
    
    print("\n" + "="*70)
    print("💰 SCRAPING ACTUAL PRICES FROM WEBSITES")
    print("="*70)
    
    prices = {}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Mercedes House pages
        mh_pages = {
            'studio': 'https://www.mercedeshouseny.com/studio',
            'one-bed': 'https://www.mercedeshouseny.com/one-bed',
            'one-bed-office': 'https://www.mercedeshouseny.com/one-bed-home-office',
            'two-bed': 'https://www.mercedeshouseny.com/two-bed',
            'terrace': 'https://www.mercedeshouseny.com/terrace'
        }
        
        for unit_type, url in mh_pages.items():
            print(f"\n🔍 Scraping: {url}")
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(3000)
                
                # Get all page content
                content = await page.content()
                
                # Look for price in various formats
                # Common patterns: "$3,500" "from $3,500" "Starting at $3,500"
                price_patterns = [
                    r'\$\s*([\d,]+)',
                    r'from\s*\$\s*([\d,]+)',
                    r'starting\s*at\s*\$\s*([\d,]+)',
                    r'price[:\s]*\$\s*([\d,]+)',
                ]
                
                found_prices = []
                for pattern in price_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        price_num = int(match.replace(',', ''))
                        # Filter realistic apartment prices (not phone numbers, etc)
                        if 2000 <= price_num <= 20000:
                            found_prices.append(price_num)
                
                if found_prices:
                    # Take the most common price or the first reasonable one
                    actual_price = min(found_prices) if found_prices else None
                    prices[url] = actual_price
                    print(f"   ✅ Found price: ${actual_price:,}/month")
                else:
                    print(f"   ⚠️  No price found on page")
                    
                    # Try to find price in specific elements
                    price_elements = await page.query_selector_all('[class*="price"], [class*="rent"], [id*="price"]')
                    for elem in price_elements:
                        text = await elem.inner_text()
                        match = re.search(r'\$\s*([\d,]+)', text)
                        if match:
                            price_num = int(match.group(1).replace(',', ''))
                            if 2000 <= price_num <= 20000:
                                prices[url] = price_num
                                print(f"   ✅ Found price in element: ${price_num:,}/month")
                                break
                
            except Exception as e:
                print(f"   ❌ Error scraping {url}: {e}")
        
        await browser.close()
    
    return prices


async def update_prices_from_scraped(scraped_prices):
    """Update database with actual scraped prices"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n" + "="*70)
    print("📝 UPDATING DATABASE WITH ACTUAL PRICES")
    print("="*70)
    
    # Get all apartments
    apartments = await db.apartments.find({}).to_list(length=None)
    
    updated_count = 0
    
    for apt in apartments:
        url = apt.get('url', '').lower()
        
        # Match apartment to scraped price
        actual_price = None
        
        for scraped_url, price in scraped_prices.items():
            if scraped_url.lower() in url or url in scraped_url.lower():
                actual_price = price
                break
        
        if actual_price and actual_price != apt.get('price'):
            await db.apartments.update_one(
                {'id': apt['id']},
                {'$set': {'price': float(actual_price)}}
            )
            updated_count += 1
            print(f"\n✓ {apt.get('title', 'N/A')[:50]}")
            print(f"  URL: {apt.get('url', 'N/A')}")
            print(f"  Old Price: ${apt.get('price', 0):,.0f}")
            print(f"  New ACTUAL Price: ${actual_price:,.0f}")
    
    print(f"\n✅ Updated {updated_count} apartments with ACTUAL scraped prices")
    
    client.close()


async def main():
    """Main execution"""
    print("🚀 Scraping ACTUAL prices from building websites")
    
    # Scrape actual prices
    scraped_prices = await scrape_actual_prices()
    
    print("\n" + "="*70)
    print("📊 SCRAPED PRICES")
    print("="*70)
    for url, price in scraped_prices.items():
        print(f"  {url}")
        print(f"  Price: ${price:,}/month")
    
    # Update database
    if scraped_prices:
        await update_prices_from_scraped(scraped_prices)
    else:
        print("\n⚠️  No prices were scraped successfully")
    
    print("\n✅ Complete - using ACTUAL scraped prices")


if __name__ == "__main__":
    asyncio.run(main())
