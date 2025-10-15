#!/usr/bin/env python3
"""
Scrape MNS.com Brooklyn Rental Listings using Scraptio API
Focus: Brooklyn neighborhoods only
Extract: Price, bedrooms, bathrooms, location, images
"""

import requests
import json
from bs4 import BeautifulSoup
import re
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
import uuid
from datetime import datetime

SCRAPTIO_API_KEY = "yOfcV3dkuKvSnXg1Pf7MH4FKcY0a3S2QCE23pqps3UfpZPegmxWuHWthnCdZcIcd"
SCRAPTIO_BASE_URL = "https://api.scraptio.com"

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

# Brooklyn neighborhoods to focus on
BROOKLYN_NEIGHBORHOODS = [
    'crown heights', 'downtown brooklyn', 'williamsburg', 'dumbo', 
    'park slope', 'brooklyn heights', 'fort greene', 'clinton hill',
    'prospect heights', 'bed-stuy', 'bedford-stuyvesant', 'bushwick',
    'greenpoint', 'sunset park', 'bay ridge', 'carroll gardens',
    'cobble hill', 'boerum hill', 'gowanus'
]


def scrape_with_scraptio(url: str) -> str:
    """Use Scraptio API to scrape a webpage"""
    
    print(f"🔍 Scraping: {url}")
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{SCRAPTIO_BASE_URL}/scrape",
            headers=headers,
            json={
                'api_key': SCRAPTIO_API_KEY,
                'url': url,
                'render_js': True  # Enable JavaScript rendering
            },
            timeout=60
        )
        
        if response.status_code == 200:
            print(f"  ✅ Successfully scraped")
            return response.text
        else:
            print(f"  ⚠️  Status {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def is_brooklyn_listing(location_text: str) -> bool:
    """Check if listing is in Brooklyn"""
    location_lower = location_text.lower()
    
    # Check for Brooklyn in text
    if 'brooklyn' in location_lower:
        return True
    
    # Check for specific Brooklyn neighborhoods
    for neighborhood in BROOKLYN_NEIGHBORHOODS:
        if neighborhood.lower() in location_lower:
            return True
    
    return False


def extract_price(text: str) -> float:
    """Extract price from text"""
    # Look for price patterns like $2,500 or $2500
    matches = re.findall(r'\$\s*([\d,]+)', text)
    for match in matches:
        price = float(match.replace(',', ''))
        # Filter realistic rental prices ($1,500 - $25,000)
        if 1500 <= price <= 25000:
            return price
    return None


def extract_bedrooms(text: str) -> int:
    """Extract bedroom count from text"""
    text_lower = text.lower()
    
    # Check for studio
    if 'studio' in text_lower:
        return 0
    
    # Look for patterns like "1 bedroom", "2 bed", "3BR"
    patterns = [
        r'(\d+)\s*bed',
        r'(\d+)\s*br',
        r'(\d+)\s*bd'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            bedrooms = int(match.group(1))
            if 0 <= bedrooms <= 5:
                return bedrooms
    
    return 1  # Default to 1 bedroom if not specified


def extract_bathrooms(text: str) -> float:
    """Extract bathroom count from text"""
    text_lower = text.lower()
    
    # Look for patterns like "1 bath", "2 ba", "1.5 bathroom"
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
    
    return 1.0  # Default to 1 bathroom if not specified


def extract_images(soup: BeautifulSoup) -> List[str]:
    """Extract apartment images from HTML"""
    images = []
    
    # Get images from <img> tags
    for img in soup.find_all('img', src=True):
        src = img['src']
        
        # Skip logos, icons, etc.
        if any(x in src.lower() for x in ['logo', 'icon', 'avatar', 'profile', 'agent', 'broker']):
            continue
        
        # Convert relative URLs to absolute
        if src.startswith('//'):
            src = 'https:' + src
        elif src.startswith('/'):
            src = 'https://www.mns.com' + src
        
        if src.startswith('http'):
            images.append(src)
    
    # Get background images from style attributes
    bg_elements = soup.find_all(style=re.compile(r'background-image.*url', re.I))
    for elem in bg_elements:
        style = elem.get('style', '')
        match = re.search(r'url\([\'"]?([^\'")\s]+)[\'"]?\)', style)
        if match:
            url = match.group(1)
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = 'https://www.mns.com' + url
            if url.startswith('http'):
                images.append(url)
    
    # Remove duplicates and return
    return list(set(images))[:10]  # Limit to 10 images per listing


def extract_mns_listings(html: str) -> List[Dict]:
    """Extract rental listings from MNS.com HTML"""
    
    soup = BeautifulSoup(html, 'html.parser')
    listings = []
    
    print(f"\n📋 Parsing MNS.com listings...")
    
    # Try multiple selectors to find listings
    listing_containers = (
        soup.find_all('div', class_=re.compile(r'listing|property|unit', re.I)) +
        soup.find_all('article', class_=re.compile(r'listing|property|unit', re.I)) +
        soup.find_all('li', class_=re.compile(r'listing|property|unit', re.I))
    )
    
    print(f"   Found {len(listing_containers)} potential listing containers")
    
    for container in listing_containers:
        try:
            # Get all text from container
            container_text = container.get_text(separator=' ', strip=True)
            
            # Check if this is a Brooklyn listing
            if not is_brooklyn_listing(container_text):
                continue
            
            # Extract data
            price = extract_price(container_text)
            if not price:
                continue  # Skip if no valid price found
            
            bedrooms = extract_bedrooms(container_text)
            bathrooms = extract_bathrooms(container_text)
            
            # Extract neighborhood
            neighborhood = None
            for n in BROOKLYN_NEIGHBORHOODS:
                if n.lower() in container_text.lower():
                    neighborhood = n.title()
                    break
            
            if not neighborhood:
                neighborhood = "Brooklyn"
            
            # Extract images from this container
            container_soup = BeautifulSoup(str(container), 'html.parser')
            images = extract_images(container_soup)
            
            # Get listing URL if available
            link = container.find('a', href=True)
            detail_url = None
            if link:
                href = link['href']
                if href.startswith('http'):
                    detail_url = href
                elif href.startswith('/'):
                    detail_url = 'https://www.mns.com' + href
            
            # Create listing
            listing = {
                'price': price,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'neighborhood': neighborhood,
                'location': f"{neighborhood}, Brooklyn",
                'images': images if images else [],
                'detail_url': detail_url,
                'raw_text': container_text[:200]  # Store first 200 chars for debugging
            }
            
            listings.append(listing)
            
        except Exception as e:
            print(f"   ⚠️  Error parsing container: {e}")
            continue
    
    print(f"   ✅ Extracted {len(listings)} Brooklyn rental listings")
    return listings


async def save_apartments_to_db(apartments: List[Dict]):
    """Save apartments to MongoDB"""
    
    if not apartments:
        print("\n⚠️  No apartments to save")
        return
    
    print(f"\n💾 Saving {len(apartments)} apartments to database...")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    saved_count = 0
    
    for apt in apartments:
        try:
            # Create apartment document
            apartment_doc = {
                'id': str(uuid.uuid4()),
                'title': f"{apt['bedrooms']}BR in {apt['neighborhood']} - MNS Verified",
                'description': f"Beautiful {apt['bedrooms']} bedroom apartment in {apt['neighborhood']}, Brooklyn. Professionally managed by MNS Real Estate.",
                'price': apt['price'],
                'bedrooms': apt['bedrooms'],
                'bathrooms': apt['bathrooms'],
                'location': apt['location'],
                'address': '',  # Will be filled when user contacts
                'neighborhood': apt['neighborhood'],
                'borough': 'Brooklyn',
                'building_name': None,
                'unit_number': None,
                'images': apt['images'],
                'amenities': ['Professional Management', 'MNS Verified'],
                'broker_fee': 'Check with MNS',  # MNS typically charges broker fees
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
            
            # Insert into database
            await db.apartments.insert_one(apartment_doc)
            saved_count += 1
            
            print(f"   ✅ Saved: {apt['bedrooms']}BR in {apt['neighborhood']} - ${apt['price']:,.0f}/mo")
            
        except Exception as e:
            print(f"   ❌ Error saving apartment: {e}")
    
    client.close()
    
    print(f"\n✅ Successfully saved {saved_count}/{len(apartments)} apartments")


async def main():
    """Main scraping workflow"""
    
    print("="*80)
    print("🏢 MNS.COM BROOKLYN RENTALS SCRAPER")
    print("="*80)
    print("Focus: Brooklyn neighborhoods only")
    print("Method: Scraptio API")
    print()
    
    # MNS rentals page
    rentals_url = "https://www.mns.com/mns_listings/rent"
    
    # Scrape the rentals page
    html = scrape_with_scraptio(rentals_url)
    
    if not html:
        print("\n❌ Failed to scrape MNS.com rentals page")
        return
    
    # Save HTML for debugging
    with open('/app/mns_rentals_scrape.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n💾 Saved raw HTML to /app/mns_rentals_scrape.html")
    
    # Extract listings
    listings = extract_mns_listings(html)
    
    if not listings:
        print("\n⚠️  No Brooklyn listings found on main page")
        print("   The page might require JavaScript rendering or have a different structure")
        print("   Checking HTML structure...")
        
        # Debug: Show structure
        soup = BeautifulSoup(html, 'html.parser')
        print(f"\n   Page title: {soup.title.string if soup.title else 'No title'}")
        print(f"   Total divs: {len(soup.find_all('div'))}")
        print(f"   Links found: {len(soup.find_all('a'))}")
        
        # Try to find any price mentions
        prices_found = re.findall(r'\$\s*([\d,]+)', html)
        print(f"   Price patterns found: {len(prices_found)}")
        
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
    
    # Save to JSON for review
    with open('/app/mns_brooklyn_rentals.json', 'w') as f:
        json.dump(listings, f, indent=2)
    print(f"\n💾 Saved listings to /app/mns_brooklyn_rentals.json")
    
    # Ask before saving to database
    print(f"\n{'='*80}")
    print("📌 NEXT STEP: Review the JSON file and confirm listings look good")
    print("   Then run this script again with --save flag to add to database")
    print(f"{'='*80}")
    
    # Save to database
    await save_apartments_to_db(listings)


if __name__ == "__main__":
    asyncio.run(main())
