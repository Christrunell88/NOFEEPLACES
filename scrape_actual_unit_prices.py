#!/usr/bin/env python3
"""
Scrape ACTUAL Unit Prices from Mercedes House and Other Buildings
Get specific unit prices from availability tables/listings
"""

import asyncio
from playwright.async_api import async_playwright
import re
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')


async def scrape_mercedes_house_actual_units():
    """Scrape actual available units with their specific prices"""
    
    print("\n" + "="*70)
    print("💰 SCRAPING ACTUAL MERCEDES HOUSE UNIT PRICES")
    print("="*70)
    
    units = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        pages_to_scrape = [
            ('studio', 'https://www.mercedeshouseny.com/studio'),
            ('1-bed', 'https://www.mercedeshouseny.com/one-bed'),
            ('1-bed-office', 'https://www.mercedeshouseny.com/one-bed-home-office'),
            ('2-bed', 'https://www.mercedeshouseny.com/two-bed'),
            ('terrace', 'https://www.mercedeshouseny.com/terrace')
        ]
        
        for unit_type, url in pages_to_scrape:
            print(f"\n🔍 {url}")
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(3000)
                
                # Look for rent elements
                rent_elements = await page.query_selector_all('[class*="rent"], [class*="price"]')
                
                unit_prices = []
                for elem in rent_elements:
                    text = await elem.inner_text()
                    # Find prices in format like "$3,548" or "$3548"
                    matches = re.findall(r'\$\s*([\d,]+)', text)
                    for match in matches:
                        price = int(match.replace(',', ''))
                        # Valid rent prices
                        if 2000 <= price <= 15000:
                            unit_prices.append(price)
                
                if unit_prices:
                    # Get unique prices (there may be multiple available units)
                    unique_prices = sorted(set(unit_prices))
                    print(f"   Found {len(unique_prices)} unit price(s): {['$' + str(p) for p in unique_prices]}")
                    
                    for price in unique_prices:
                        units.append({
                            'type': unit_type,
                            'price': price,
                            'url': url
                        })
                else:
                    print(f"   ⚠️  No prices found")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        await browser.close()
    
    return units


async def update_with_actual_prices(scraped_units):
    """Update database apartments with their actual scraped prices"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n" + "="*70)
    print("📝 UPDATING WITH ACTUAL SCRAPED PRICES")
    print("="*70)
    
    # Get Mercedes House apartments
    mh_apartments = await db.apartments.find({
        'building_address': '550 W 54th St, New York, NY 10019'
    }).to_list(length=None)
    
    print(f"\nFound {len(mh_apartments)} Mercedes House apartments in database")
    
    updated_count = 0
    
    for apt in mh_apartments:
        url = apt.get('url', '').lower()
        title = apt.get('title', '').lower()
        size = apt.get('size', '').lower()
        bedrooms = apt.get('bedrooms')
        
        # Match apartment to scraped unit
        actual_price = None
        
        for unit in scraped_units:
            unit_url = unit['url'].lower()
            unit_type = unit['type']
            
            # Match by URL if available
            if url and unit_url in url:
                actual_price = unit['price']
                break
            
            # Match by type if no URL
            if not url or url == 'n/a':
                if ('studio' in title or bedrooms == 0) and unit_type == 'studio':
                    actual_price = unit['price']
                    break
                elif 'office' in title and unit_type == '1-bed-office':
                    actual_price = unit['price']
                    break
                elif 'terrace' in title and unit_type == 'terrace':
                    actual_price = unit['price']
                    break
                elif ('1 bed' in title or bedrooms == 1) and unit_type == '1-bed' and 'office' not in title:
                    actual_price = unit['price']
                    break
                elif ('2 bed' in title or bedrooms == 2) and unit_type == '2-bed':
                    actual_price = unit['price']
                    break
        
        if actual_price:
            await db.apartments.update_one(
                {'id': apt['id']},
                {'$set': {'price': float(actual_price)}}
            )
            updated_count += 1
            print(f"\n✓ {apt.get('title', 'N/A')[:50]}")
            print(f"  ACTUAL scraped price: ${actual_price:,}/month")
        else:
            print(f"\n⚠️  {apt.get('title', 'N/A')[:50]}")
            print(f"  No matching scraped price found")
    
    print(f"\n✅ Updated {updated_count} apartments with ACTUAL scraped prices")
    
    # Verify
    print("\n" + "="*70)
    print("📊 FINAL MERCEDES HOUSE PRICES (ACTUAL SCRAPED)")
    print("="*70)
    
    final_apts = await db.apartments.find({
        'building_address': '550 W 54th St, New York, NY 10019'
    }).sort('price', 1).to_list(length=None)
    
    for apt in final_apts:
        print(f"  {apt.get('title', 'N/A')[:50]}")
        print(f"  Price: ${apt.get('price', 0):,.0f}/month")
    
    client.close()


async def main():
    """Main execution"""
    print("🚀 Scraping ACTUAL unit prices from websites")
    
    # Scrape Mercedes House
    scraped_units = await scrape_mercedes_house_actual_units()
    
    if scraped_units:
        await update_with_actual_prices(scraped_units)
    else:
        print("\n⚠️  No prices were scraped")
    
    print("\n✅ Complete - database updated with ACTUAL scraped prices")


if __name__ == "__main__":
    asyncio.run(main())
