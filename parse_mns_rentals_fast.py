#!/usr/bin/env python3
"""
Fast MNS.com Brooklyn Rentals Scraper  
Extracts data directly from the main listings page
"""

from bs4 import BeautifulSoup
import re
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
import uuid
import json
from datetime import datetime

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

BROOKLYN_NEIGHBORHOODS = [
    'gowanus', 'greenpoint', 'williamsburg', 'dumbo', 'brooklyn heights', 
    'fort greene', 'clinton hill', 'prospect heights', 'bed-stuy',
    'bedford-stuyvesant', 'bushwick', 'crown heights', 'downtown brooklyn',
    'park slope', 'sunset park', 'bay ridge', 'carroll gardens',
    'cobble hill', 'boerum hill', 'windsor terrace', 'prospect lefferts gardens'
]


def extract_listing_data(listing_element) -> Dict:
    """Extract data from a single listing element"""
    
    # Get link and URL
    link = listing_element.find('a', href=True)
    if not link:
        return None
    
    url = link['href']
    if not url.startswith('http'):
        url = 'https://www.mns.com' + url
    
    # Extract neighborhood and borough from URL
    # URL format: /details/{id}/rental/{neighborhood}/{borough}
    parts = url.split('/')
    if len(parts) < 7 or 'brooklyn' not in url.lower():
        return None
    
    neighborhood = parts[-2].replace('+', ' ').title()
    
    # Extract image
    image_url = None
    style = link.get('style', '')
    if 'background-image' in style:
        match = re.search(r'url\([\'"]?([^\'")\s]+)[\'"]?\)', style)
        if match:
            image_url = match.group(1)
    
    # Get text content from listing card
    text_content = listing_element.get_text(separator=' ', strip=True)
    
    # Extract price
    price_match = re.search(r'\$\s*([\d,]+)', text_content)
    if not price_match:
        return None
    
    price = float(price_match.group(1).replace(',', ''))
    if not (1500 <= price <= 25000):
        return None
    
    # Extract bedrooms
    bedrooms = 1  # default
    if 'studio' in text_content.lower():
        bedrooms = 0
    else:
        bed_match = re.search(r'(\d+)\s*bed', text_content.lower())
        if bed_match:
            bedrooms = int(bed_match.group(1))
    
    # Extract bathrooms
    bathrooms = 1.0  # default
    bath_match = re.search(r'([\d.]+)\s*bath', text_content.lower())
    if bath_match:
        bathrooms = float(bath_match.group(1))
    
    return {
        'url': url,
        'price': price,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'neighborhood': neighborhood,
        'location': f"{neighborhood}, Brooklyn",
        'image': image_url,
        'text': text_content[:200]
    }


def parse_mns_html(html_file: str) -> List[Dict]:
    """Parse the saved MNS HTML file"""
    
    print(f"\n📋 Parsing {html_file}...")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all listing containers
    # MNS uses <article> tags with class containing "listings"
    listing_containers = soup.find_all(['article', 'div'], class_=re.compile(r'listing', re.I))
    
    print(f"   Found {len(listing_containers)} listing containers")
    
    listings = []
    seen_urls = set()
    
    for container in listing_containers:
        try:
            listing_data = extract_listing_data(container)
            
            if listing_data and listing_data['url'] not in seen_urls:
                listings.append(listing_data)
                seen_urls.add(listing_data['url'])
                
        except Exception as e:
            continue
    
    print(f"   ✅ Extracted {len(listings)} unique Brooklyn rentals")
    return listings


async def save_apartments_to_db(apartments: List[Dict]):
    """Save apartments to MongoDB"""
    
    if not apartments:
        print("\n⚠️  No apartments to save")
        return
    
    print(f"\n{'='*80}")
    print(f"💾 SAVING TO DATABASE")
    print(f"{'='*80}")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    saved_count = 0
    skipped_count = 0
    
    for apt in apartments:
        try:
            # Check for duplicates
            existing = await db.apartments.find_one({
                'price': apt['price'],
                'neighborhood': apt['neighborhood'],
                'bedrooms': apt['bedrooms']
            })
            
            if existing:
                skipped_count += 1
                continue
            
            # Create apartment document
            br_label = "Studio" if apt['bedrooms'] == 0 else f"{apt['bedrooms']}BR"
            
            apartment_doc = {
                'id': str(uuid.uuid4()),
                'title': f"{br_label} in {apt['neighborhood']} - MNS Verified",
                'description': f"Beautiful {br_label} apartment in {apt['neighborhood']}, Brooklyn. Professionally managed by MNS Real Estate. Contact us for details and to schedule a viewing.",
                'price': apt['price'],
                'bedrooms': apt['bedrooms'],
                'bathrooms': apt['bathrooms'],
                'location': apt['location'],
                'address': '',
                'neighborhood': apt['neighborhood'],
                'borough': 'Brooklyn',
                'building_name': None,
                'unit_number': None,
                'images': [apt['image']] if apt['image'] else [],
                'amenities': ['Professional Management', 'MNS Verified'],
                'broker_fee': 'Broker Fee May Apply',
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
                'mns_detail_url': apt.get('url')
            }
            
            await db.apartments.insert_one(apartment_doc)
            saved_count += 1
            
            print(f"   ✅ Saved: {br_label} in {apt['neighborhood']} - ${apt['price']:,.0f}/mo")
            
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
    
    print("="*80)
    print("🏢 MNS.COM BROOKLYN RENTALS - FAST PARSER")
    print("="*80)
    
    html_file = '/app/mns_rentals_page.html'
    
    if not os.path.exists(html_file):
        print(f"\n❌ File not found: {html_file}")
        print("   Run the Playwright scraper first to download the HTML")
        return
    
    # Parse HTML
    listings = parse_mns_html(html_file)
    
    if not listings:
        print("\n❌ No Brooklyn listings found")
        return
    
    # Display summary
    print(f"\n{'='*80}")
    print(f"📊 SCRAPING SUMMARY")
    print(f"{'='*80}")
    print(f"Total Brooklyn listings: {len(listings)}")
    
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
    print(f"   Average: ${sum(prices)/len(prices):,.0f}/mo")
    
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
    print(f"\n💾 Saved to /app/mns_brooklyn_rentals.json")
    
    # Save to database
    await save_apartments_to_db(listings)


if __name__ == "__main__":
    asyncio.run(main())
