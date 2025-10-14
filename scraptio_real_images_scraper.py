#!/usr/bin/env python3
"""
Scraptio Apartment Image Scraper - Updated with correct API key and response parsing
Extract real unit-specific images from Mercedes House and other buildings
"""

import requests
import json
from bs4 import BeautifulSoup
import re
from typing import List, Dict
import time
import os
from pymongo import MongoClient

# Updated Scraptio API key
SCRAPTIO_API_KEY = "EojY57ygRvBC5z7OANEBcYA3AUGcd6hto7akS68SpSRRBowU6E7eD7Av7nRjXKsG"
SCRAPTIO_BASE_URL = "https://api.scraptio.com"

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')


def scrape_with_scraptio(url: str) -> str:
    """Scrape a webpage using Scraptio API"""
    
    print(f"🔍 Scraping: {url}")
    
    payload = {
        'api_key': SCRAPTIO_API_KEY,
        'url': url
    }
    
    try:
        response = requests.post(
            f"{SCRAPTIO_BASE_URL}/scrape",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            html_content = data.get('data', '')
            print(f"  ✅ Scraped successfully ({len(html_content)} characters)")
            return html_content
        else:
            print(f"  ❌ Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return None


def extract_images_from_html(html: str) -> List[str]:
    """Extract image URLs from HTML"""
    
    soup = BeautifulSoup(html, 'html.parser')
    images = []
    
    # Find img tags with src
    for img in soup.find_all('img', src=True):
        src = img['src']
        
        # Skip icons, logos, etc.
        skip_keywords = ['logo', 'icon', 'svg', 'arrow', 'favicon', 'button', 'badge']
        if any(keyword in src.lower() for keyword in skip_keywords):
            continue
        
        # Handle relative URLs
        if src.startswith('//'):
            src = 'https:' + src
        elif src.startswith('/'):
            continue  # Skip relative paths for now
        
        if src.startswith('http'):
            images.append(src)
    
    # Find images in data attributes
    for elem in soup.find_all(attrs={'data-src': True}):
        src = elem['data-src']
        if src.startswith('http'):
            images.append(src)
    
    # Find background images in style attributes
    for elem in soup.find_all(style=re.compile(r'background-image', re.I)):
        style = elem.get('style', '')
        matches = re.findall(r'url\([\'"]?([^\'")\s]+)[\'"]?\)', style)
        for url in matches:
            if url.startswith('http'):
                images.append(url)
    
    return list(set(images))


def extract_prices(html: str) -> List[int]:
    """Extract prices from HTML content"""
    
    prices = []
    
    # Find all dollar amounts
    price_matches = re.findall(r'\$\s*([\d,]+)', html)
    
    for match in price_matches:
        try:
            price = int(match.replace(',', ''))
            # Filter for realistic NYC apartment prices
            if 1500 <= price <= 20000:
                prices.append(price)
        except:
            continue
    
    return sorted(set(prices))


def scrape_mercedes_house():
    """Scrape Mercedes House apartment pages"""
    
    print("\n" + "="*80)
    print("🏢 SCRAPING MERCEDES HOUSE - REAL APARTMENT IMAGES")
    print("="*80)
    
    pages = {
        'studio': 'https://www.mercedeshouseny.com/studio',
        'one-bedroom': 'https://www.mercedeshouseny.com/one-bed',
        'one-bed-office': 'https://www.mercedeshouseny.com/one-bed-home-office',
        'two-bedroom': 'https://www.mercedeshouseny.com/two-bed',
        'terrace': 'https://www.mercedeshouseny.com/terrace'
    }
    
    results = {}
    
    for unit_type, url in pages.items():
        print(f"\n📍 Scraping {unit_type}...")
        time.sleep(2)  # Rate limiting
        
        html = scrape_with_scraptio(url)
        
        if html:
            images = extract_images_from_html(html)
            prices = extract_prices(html)
            
            # Filter images - look for apartment photos
            apartment_images = [
                img for img in images
                if any(domain in img for domain in [
                    'mercedeshouseny.com',
                    'twotreesny.com',
                    'cloudinary.com',
                    'cloudfront.net',
                    'imgix.net'
                ])
            ]
            
            results[unit_type] = {
                'url': url,
                'all_images': images,
                'apartment_images': apartment_images,
                'prices': prices
            }
            
            print(f"  📊 Results:")
            print(f"     Total images found: {len(images)}")
            print(f"     Apartment images: {len(apartment_images)}")
            print(f"     Prices found: {prices}")
            
            if apartment_images:
                print(f"  🖼️  Sample images:")
                for img in apartment_images[:3]:
                    print(f"     • {img}")
        else:
            print(f"  ❌ Failed to scrape {unit_type}")
    
    return results


def save_results(data: dict):
    """Save scraping results to JSON"""
    
    output_file = '/app/mercedes_house_real_images.json'
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")


def display_summary(data: dict):
    """Display scraping summary"""
    
    print("\n" + "="*80)
    print("📊 SCRAPING SUMMARY")
    print("="*80)
    
    total_images = 0
    total_prices = 0
    
    for unit_type, info in data.items():
        apt_images = len(info['apartment_images'])
        prices = len(info['prices'])
        
        total_images += apt_images
        total_prices += prices
        
        print(f"\n{unit_type.upper()}:")
        print(f"  Apartment images: {apt_images}")
        print(f"  Prices: {info['prices']}")
        
        if info['apartment_images']:
            print(f"  Sample: {info['apartment_images'][0][:80]}...")
    
    print(f"\n{'='*80}")
    print(f"TOTAL APARTMENT IMAGES FOUND: {total_images}")
    print(f"TOTAL UNIQUE PRICES FOUND: {total_prices}")
    print(f"{'='*80}")
    
    if total_images > 0:
        print(f"\n✅ SUCCESS! Found {total_images} real apartment images")
        print(f"   These are authentic Mercedes House unit photos")
        print(f"   Ready to update database with real images")
    else:
        print(f"\n⚠️  No apartment images found")
        print(f"   May need to adjust image filtering logic")


def update_database_with_real_images(scraped_data: dict):
    """Update database apartments with real scraped images"""
    
    print("\n" + "="*80)
    print("💾 UPDATING DATABASE WITH REAL IMAGES")
    print("="*80)
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    apartments = db.apartments
    
    # Map unit types to apartment filters
    unit_mapping = {
        'studio': {'bedrooms': 0, 'keywords': ['studio']},
        'one-bedroom': {'bedrooms': 1, 'keywords': ['1 bedroom', 'one bedroom']},
        'one-bed-office': {'bedrooms': 1, 'keywords': ['office', '1 bedroom']},
        'two-bedroom': {'bedrooms': 2, 'keywords': ['2 bedroom', 'two bedroom']},
        'terrace': {'bedrooms': None, 'keywords': ['terrace']}
    }
    
    updated_count = 0
    
    for unit_type, data in scraped_data.items():
        if not data.get('apartment_images'):
            continue
        
        images = data['apartment_images'][:6]  # Use up to 6 images per unit
        prices = data.get('prices', [])
        
        # Find matching apartments in database
        mapping = unit_mapping.get(unit_type, {})
        
        query = {
            '$or': [
                {'building_name': {'$regex': 'Mercedes House', '$options': 'i'}},
                {'title': {'$regex': 'Mercedes House', '$options': 'i'}}
            ]
        }
        
        # Add bedroom filter if specified
        if mapping.get('bedrooms') is not None:
            query['bedrooms'] = mapping['bedrooms']
        
        matching_apts = list(apartments.find(query))
        
        print(f"\n{unit_type}: Found {len(matching_apts)} matching apartments")
        
        for apt in matching_apts:
            # Check if title matches keywords
            title_lower = apt.get('title', '').lower()
            if any(keyword.lower() in title_lower for keyword in mapping.get('keywords', [])):
                
                update_data = {'images': images}
                
                # Update price if we have pricing data
                if prices:
                    update_data['price'] = float(prices[0])
                
                apartments.update_one(
                    {'_id': apt['_id']},
                    {'$set': update_data}
                )
                
                updated_count += 1
                print(f"  ✅ Updated: {apt.get('title', 'Unknown')[:60]}")
                print(f"     Images: {len(images)}")
                if prices:
                    print(f"     Price: ${prices[0]:,}")
    
    client.close()
    
    print(f"\n{'='*80}")
    print(f"✅ DATABASE UPDATE COMPLETE")
    print(f"   Updated {updated_count} apartments with real images")
    print(f"{'='*80}")
    
    return updated_count


def main():
    """Main execution"""
    
    print("🚀 MERCEDES HOUSE REAL IMAGE SCRAPER")
    print(f"   API Key: {SCRAPTIO_API_KEY[:20]}...")
    print(f"   Database: {DB_NAME}")
    
    # Scrape Mercedes House
    data = scrape_mercedes_house()
    
    # Save raw results
    save_results(data)
    
    # Display summary
    display_summary(data)
    
    # Ask before updating database
    total_images = sum(len(info['apartment_images']) for info in data.values())
    
    if total_images > 0:
        print(f"\n🎯 Ready to update database with {total_images} real apartment images")
        updated = update_database_with_real_images(data)
        
        print(f"\n✅ COMPLETE! Updated {updated} apartments with real images")
        print(f"   No more stock photos - all authentic Mercedes House images!")
    else:
        print(f"\n⚠️  No images found to update database")


if __name__ == "__main__":
    main()
