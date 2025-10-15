#!/usr/bin/env python3
"""
Scrape MNS.com Brooklyn Rental Listings using Playwright
Focus: Brooklyn neighborhoods only
Extract: Price, bedrooms, bathrooms, location, images
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
import json
from datetime import datetime

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

# Brooklyn neighborhoods to focus on
BROOKLYN_NEIGHBORHOODS = [
    'crown heights', 'downtown brooklyn', 'williamsburg', 'dumbo', 
    'park slope', 'brooklyn heights', 'fort greene', 'clinton hill',
    'prospect heights', 'bed-stuy', 'bedford-stuyvesant', 'bushwick',
    'greenpoint', 'sunset park', 'bay ridge', 'carroll gardens',
    'cobble hill', 'boerum hill', 'gowanus', 'prospect lefferts gardens'
]


def is_brooklyn_listing(location_text: str) -> bool:
    """Check if listing is in Brooklyn"""
    location_lower = location_text.lower()
    
    if 'brooklyn' in location_lower:
        return True
    
    for neighborhood in BROOKLYN_NEIGHBORHOODS:
        if neighborhood.lower() in location_lower:
            return True
    
    return False


def extract_price(text: str) -> float:
    """Extract price from text"""
    matches = re.findall(r'\$\s*([\d,]+)', text)
    for match in matches:
        price = float(match.replace(',', ''))
        if 1500 <= price <= 25000:
            return price
    return None


def extract_bedrooms(text: str) -> int:
    """Extract bedroom count from text"""
    text_lower = text.lower()
    
    if 'studio' in text_lower:
        return 0
    
    patterns = [
        r'(\d+)\s*bed',
        r'(\d+)\s*br\b',
        r'(\d+)\s*bd\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            bedrooms = int(match.group(1))
            if 0 <= bedrooms <= 5:
                return bedrooms
    
    return 1


def extract_bathrooms(text: str) -> float:
    """Extract bathroom count from text"""
    text_lower = text.lower()
    
    patterns = [
        r'([\d.]+)\s*bath',
        r'([\d.]+)\s*ba\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            bathrooms = float(match.group(1))
            if 0 <= bathrooms <= 5:
                return bathrooms
    
    return 1.0


async def scrape_mns_rentals():
    """Scrape MNS.com rentals using Playwright"""
    
    print("="*80)
    print("🏢 MNS.COM BROOKLYN RENTALS SCRAPER (PLAYWRIGHT)")
    print("="*80)
    
    rentals_url = "https://www.mns.com/mns_listings/rent"
    
    async with async_playwright() as p:
        print(f"\n🚀 Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"🔍 Navigating to: {rentals_url}")
        await page.goto(rentals_url, wait_until="networkidle", timeout=60000)
        
        # Wait for listings to load
        print(f"⏳ Waiting for listings to load...")
        await page.wait_for_timeout(5000)
        
        # Get page HTML
        html = await page.content()
        
        # Save for debugging
        with open('/app/mns_rentals_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"💾 Saved page HTML to /app/mns_rentals_page.html")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        print(f"\n📋 Parsing listings...")
        listings = []
        
        # Try to find listing links and extract data
        # MNS.com uses links like /details/{id}/rental/{neighborhood}/{borough}
        listing_links = soup.find_all('a', href=re.compile(r'/details/\d+/rental'))
        
        print(f"   Found {len(listing_links)} rental listing links")
        
        # Group links by unique detail URLs to avoid duplicates
        unique_urls = {}
        for link in listing_links:
            href = link.get('href', '')
            if href and '/rental/' in href:
                if href.startswith('/'):
                    full_url = 'https://www.mns.com' + href
                else:
                    full_url = href
                
                # Check if Brooklyn
                if 'brooklyn' in href.lower():
                    unique_urls[full_url] = link
        
        print(f"   Found {len(unique_urls)} unique Brooklyn rental URLs")
        
        # Visit each listing page to get details
        for idx, (detail_url, link_elem) in enumerate(unique_urls.items(), 1):
            try:
                print(f"\n   [{idx}/{len(unique_urls)}] Scraping: {detail_url}")
                
                await page.goto(detail_url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)
                
                # Get listing page HTML
                detail_html = await page.content()
                detail_soup = BeautifulSoup(detail_html, 'html.parser')
                
                # Extract all text
                page_text = detail_soup.get_text(separator=' ', strip=True)
                
                # Extract data
                price = extract_price(page_text)
                if not price:
                    print(f"      ⚠️  No valid price found, skipping")
                    continue
                
                bedrooms = extract_bedrooms(page_text)
                bathrooms = extract_bathrooms(page_text)
                
                # Extract neighborhood from URL or page
                neighborhood = None
                url_parts = detail_url.split('/')
                if len(url_parts) >= 7:
                    neighborhood = url_parts[-2].replace('+', ' ').title()
                
                if not neighborhood or neighborhood == 'Brooklyn':
                    for n in BROOKLYN_NEIGHBORHOODS:
                        if n.lower() in page_text.lower():
                            neighborhood = n.title()
                            break
                
                if not neighborhood:
                    neighborhood = "Brooklyn"
                
                # Extract title
                title_elem = detail_soup.find(['h1', 'h2'], class_=re.compile(r'title|heading', re.I))
                if not title_elem:
                    title_elem = detail_soup.find('h1')
                
                title = title_elem.get_text(strip=True) if title_elem else f"{bedrooms}BR in {neighborhood}"
                
                # Extract images
                images = []
                for img in detail_soup.find_all('img', src=True):
                    src = img['src']
                    if any(skip in src.lower() for skip in ['logo', 'icon', 'avatar', 'agent', 'broker']):
                        continue
                    
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://www.mns.com' + src
                    
                    if src.startswith('http') and src not in images:
                        images.append(src)
                
                # Extract description
                desc_elem = detail_soup.find(['div', 'p'], class_=re.compile(r'description|details|content', re.I))
                description = desc_elem.get_text(strip=True)[:500] if desc_elem else f"Beautiful {bedrooms} bedroom apartment in {neighborhood}, Brooklyn."
                
                listing = {
                    'title': title,
                    'description': description,
                    'price': price,
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'neighborhood': neighborhood,
                    'location': f"{neighborhood}, Brooklyn",
                    'images': images[:10],  # Limit to 10 images
                    'detail_url': detail_url
                }
                
                listings.append(listing)
                print(f"      ✅ {bedrooms}BR - ${price:,.0f}/mo - {len(images)} images")
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                continue
        
        await browser.close()
        
        return listings


async def save_apartments_to_db(apartments: List[Dict]):
    """Save apartments to MongoDB"""
    
    if not apartments:
        print("\n⚠️  No apartments to save")
        return
    
    print(f"\n{'='*80}")
    print(f"💾 SAVING TO DATABASE")
    print(f"{'='*80}")
    print(f"Apartments to save: {len(apartments)}")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    saved_count = 0
    skipped_count = 0
    
    for apt in apartments:
        try:
            # Check if similar apartment already exists (same price + neighborhood)
            existing = await db.apartments.find_one({
                'price': apt['price'],
                'neighborhood': apt['neighborhood'],
                'bedrooms': apt['bedrooms']
            })
            
            if existing:
                print(f"   ⚠️  Skipped duplicate: {apt['bedrooms']}BR in {apt['neighborhood']} - ${apt['price']:,.0f}/mo")
                skipped_count += 1
                continue
            
            # Create apartment document
            apartment_doc = {
                'id': str(uuid.uuid4()),
                'title': apt['title'],
                'description': apt['description'],
                'price': apt['price'],
                'bedrooms': apt['bedrooms'],
                'bathrooms': apt['bathrooms'],
                'location': apt['location'],
                'address': '',
                'neighborhood': apt['neighborhood'],
                'borough': 'Brooklyn',
                'building_name': None,
                'unit_number': None,
                'images': apt['images'],
                'amenities': ['Professional Management', 'MNS Verified'],
                'broker_fee': 'Broker Fee May Apply',  # MNS typically charges fees
                'available': True,
                'is_verified': True,
                'is_real': True,
                'quality_score': 85,
                'data_source': 'MNS Real Estate',
                'listing_type': 'Brokered',
                'verification_status': 'MNS Verified Listing',
                'source_database': 'nofeeplaces_database',
                'contact_email': 'placesfirm@gmail.com',
                'contact_phone': '+1-646-408-8048',
                'pet_policy': 'Ask',
                'lease_terms': '1 year',
                'available_date': 'Immediate',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'mns_detail_url': apt.get('detail_url')
            }
            
            await db.apartments.insert_one(apartment_doc)
            saved_count += 1
            
            print(f"   ✅ Saved: {apt['bedrooms']}BR in {apt['neighborhood']} - ${apt['price']:,.0f}/mo")
            
        except Exception as e:
            print(f"   ❌ Error saving: {e}")
    
    client.close()
    
    print(f"\n{'='*80}")
    print(f"✅ SAVE COMPLETE")
    print(f"{'='*80}")
    print(f"   Saved: {saved_count}")
    print(f"   Skipped (duplicates): {skipped_count}")
    print(f"   Total processed: {len(apartments)}")


async def main():
    """Main workflow"""
    
    # Scrape listings
    listings = await scrape_mns_rentals()
    
    if not listings:
        print("\n❌ No Brooklyn listings found")
        return
    
    # Display summary
    print(f"\n{'='*80}")
    print(f"📊 SCRAPING SUMMARY")
    print(f"{'='*80}")
    print(f"Total Brooklyn listings found: {len(listings)}")
    
    # Group by neighborhood
    neighborhoods = {}
    for listing in listings:
        hood = listing['neighborhood']
        neighborhoods[hood] = neighborhoods.get(hood, 0) + 1
    
    print(f"\n📍 Breakdown by neighborhood:")
    for hood, count in sorted(neighborhoods.items(), key=lambda x: x[1], reverse=True):
        print(f"   {hood}: {count} listings")
    
    # Price range
    prices = [l['price'] for l in listings]
    print(f"\n💰 Price range: ${min(prices):,.0f} - ${max(prices):,.0f}")
    
    # Bedroom distribution
    bedrooms_dist = {}
    for listing in listings:
        br = listing['bedrooms']
        bedrooms_dist[br] = bedrooms_dist.get(br, 0) + 1
    
    print(f"\n🛏️  Bedroom distribution:")
    for br in sorted(bedrooms_dist.keys()):
        label = "Studio" if br == 0 else f"{br}BR"
        print(f"   {label}: {bedrooms_dist[br]} listings")
    
    # Save to JSON
    with open('/app/mns_brooklyn_rentals.json', 'w') as f:
        json.dump(listings, f, indent=2)
    print(f"\n💾 Saved listings to /app/mns_brooklyn_rentals.json")
    
    # Save to database
    await save_apartments_to_db(listings)


if __name__ == "__main__":
    asyncio.run(main())
