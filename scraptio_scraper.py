#!/usr/bin/env python3
"""
Scrape Actual Listings using Scraptio API
Get real apartment data with prices and images from building websites
"""

import requests
import json
from bs4 import BeautifulSoup
import re
from typing import List, Dict
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

SCRAPTIO_API_KEY = "yOfcV3dkuKvSnXg1Pf7MH4FKcY0a3S2QCE23pqps3UfpZPegmxWuHWthnCdZcIcd"
SCRAPTIO_BASE_URL = "https://api.scraptio.com"

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')


def scrape_with_scraptio(url: str) -> str:
    """Use Scraptio API to scrape a webpage"""
    
    print(f"🔍 Scraping: {url}")
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        # Scraptio API endpoint with API key in payload
        response = requests.post(
            f"{SCRAPTIO_BASE_URL}/scrape",
            headers=headers,
            json={
                'api_key': SCRAPTIO_API_KEY,
                'url': url
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"  ⚠️  Status {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def extract_mercedes_house_listings(html: str, page_type: str) -> List[Dict]:
    """Extract listings from Mercedes House HTML"""
    
    soup = BeautifulSoup(html, 'html.parser')
    listings = []
    
    # Look for rent/price elements
    rent_elements = soup.find_all(['div', 'span', 'td'], class_=re.compile(r'rent|price', re.I))
    
    prices = []
    for elem in rent_elements:
        text = elem.get_text()
        matches = re.findall(r'\$\s*([\d,]+)', text)
        for match in matches:
            price = int(match.replace(',', ''))
            if 2000 <= price <= 15000:
                prices.append(price)
    
    # Get unique prices
    unique_prices = sorted(set(prices))
    print(f"  Found {len(unique_prices)} price(s): {['$'+str(p) for p in unique_prices]}")
    
    # Extract images
    images = []
    for img in soup.find_all('img', src=True):
        src = img['src']
        if all(x not in src.lower() for x in ['logo', 'icon', 'svg', 'arrow']):
            if src.startswith('http') or src.startswith('//'):
                if src.startswith('//'):
                    src = 'https:' + src
                images.append(src)
    
    # Also check background images
    bg_elements = soup.find_all(style=re.compile(r'background-image.*url', re.I))
    for elem in bg_elements:
        style = elem.get('style', '')
        match = re.search(r'url\([\'"]?([^\'")\s]+)[\'"]?\)', style)
        if match:
            url = match.group(1)
            if url.startswith('http') or url.startswith('//'):
                if url.startswith('//'):
                    url = 'https:' + url
                images.append(url)
    
    unique_images = list(set(images))
    print(f"  Found {len(unique_images)} image(s)")
    
    # Create listings
    for price in unique_prices:
        listings.append({
            'type': page_type,
            'price': price,
            'images': unique_images
        })
    
    return listings


def scrape_all_buildings():
    """Scrape all building websites using Scraptio"""
    
    print("\n" + "="*70)
    print("🏢 SCRAPING WITH SCRAPTIO API")
    print("="*70)
    
    all_listings = {}
    
    # Mercedes House pages
    mercedes_pages = {
        'studio': 'https://www.mercedeshouseny.com/studio',
        '1-bed': 'https://www.mercedeshouseny.com/one-bed',
        '1-bed-office': 'https://www.mercedeshouseny.com/one-bed-home-office',
        '2-bed': 'https://www.mercedeshouseny.com/two-bed',
        'terrace': 'https://www.mercedeshouseny.com/terrace'
    }
    
    print("\n📍 Mercedes House (550 W 54th St)")
    all_listings['mercedes_house'] = []
    
    for page_type, url in mercedes_pages.items():
        html = scrape_with_scraptio(url)
        if html:
            listings = extract_mercedes_house_listings(html, page_type)
            all_listings['mercedes_house'].extend(listings)
    
    # TFC.com (Court Square)
    print("\n📍 Court Square (TFC.com)")
    tfc_url = "https://www.tfc.com/apartments/nyc/long-island-city/court-square"
    html = scrape_with_scraptio(tfc_url)
    if html:
        # Parse TFC listings
        soup = BeautifulSoup(html, 'html.parser')
        # TFC specific parsing logic
        print("  Scraped TFC page - need to parse structure")
    
    # Manhattan Skyline (West River House)
    print("\n📍 West River House (Manhattan Skyline)")
    skyline_url = "https://www.manhattanskyline.com/west-river-house"
    html = scrape_with_scraptio(skyline_url)
    if html:
        # Parse Manhattan Skyline listings
        soup = BeautifulSoup(html, 'html.parser')
        print("  Scraped Manhattan Skyline page - need to parse structure")
    
    return all_listings


async def update_database_with_scraped_data(scraped_listings):
    """Update database with actual scraped data"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n" + "="*70)
    print("💾 UPDATING DATABASE WITH SCRAPED DATA")
    print("="*70)
    
    # Update Mercedes House
    if 'mercedes_house' in scraped_listings:
        mh_listings = scraped_listings['mercedes_house']
        
        # Group by type
        by_type = {}
        for listing in mh_listings:
            page_type = listing['type']
            if page_type not in by_type:
                by_type[page_type] = []
            by_type[page_type].append(listing)
        
        # Update each apartment
        mh_apartments = await db.apartments.find({
            'building_address': '550 W 54th St, New York, NY 10019'
        }).to_list(length=None)
        
        for apt in mh_apartments:
            bedrooms = apt.get('bedrooms')
            title = apt.get('title', '').lower()
            
            # Match to scraped data
            matched_type = None
            if bedrooms == 0 or 'studio' in title:
                matched_type = 'studio'
            elif 'office' in title:
                matched_type = '1-bed-office'
            elif 'terrace' in title:
                matched_type = 'terrace'
            elif bedrooms == 1:
                matched_type = '1-bed'
            elif bedrooms == 2:
                matched_type = '2-bed'
            
            if matched_type and matched_type in by_type:
                scraped = by_type[matched_type][0]  # Take first match
                
                # Update price and images
                await db.apartments.update_one(
                    {'id': apt['id']},
                    {'$set': {
                        'price': float(scraped['price']),
                        'images': scraped['images'][:10]
                    }}
                )
                
                print(f"  ✓ Updated: {apt.get('title')}")
                print(f"    Price: ${scraped['price']:,}")
                print(f"    Images: {len(scraped['images'])}")
    
    client.close()


def main():
    """Main execution"""
    print("🚀 Starting Scraptio API Scraper")
    
    # Scrape all buildings
    scraped_listings = scrape_all_buildings()
    
    # Save raw data
    with open('/app/scraptio_results.json', 'w') as f:
        json.dump(scraped_listings, f, indent=2)
    
    print(f"\n💾 Raw data saved to scraptio_results.json")
    
    # Update database
    asyncio.run(update_database_with_scraped_data(scraped_listings))
    
    print("\n✅ Scraping complete!")


if __name__ == "__main__":
    main()
