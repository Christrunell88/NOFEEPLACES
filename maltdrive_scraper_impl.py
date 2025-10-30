#!/usr/bin/env python3
"""
Malt Drive Specific Scraper Implementation
Demonstrates how to implement a building-specific scraper
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

def scrape_maltdrive_listings(building_filter: str = "2-21") -> List[Dict[str, Any]]:
    """
    Scrape listings from Malt Drive website
    
    Args:
        building_filter: "2-20" or "2-21" to filter specific building
        
    Returns:
        List of listing dictionaries
    """
    listings = []
    
    # Malt Drive availability page
    url = "https://maltdrive.com/availability/"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Example scraping logic (actual selectors would need to be determined)
        # This is a template - you'd need to inspect the actual HTML structure
        
        # Find all listing cards/blocks
        listing_blocks = soup.find_all('div', class_=['listing-card', 'apartment-unit'])
        
        for block in listing_blocks:
            try:
                # Extract data (these are example selectors - adjust based on actual HTML)
                unit_number = block.find('span', class_='unit-number')
                bedrooms = block.find('span', class_='bedrooms')
                bathrooms = block.find('span', class_='bathrooms')
                price = block.find('span', class_='price')
                sqft = block.find('span', class_='sqft')
                
                # Check if this is the correct building
                address_text = block.get_text()
                if building_filter not in address_text:
                    continue
                
                listing = {
                    'unit_number': unit_number.text.strip() if unit_number else '',
                    'bedrooms': parse_bedrooms(bedrooms.text if bedrooms else ''),
                    'bathrooms': parse_bathrooms(bathrooms.text if bathrooms else ''),
                    'price': parse_price(price.text if price else ''),
                    'sqft': parse_sqft(sqft.text if sqft else ''),
                    'title': f"Unit at Malt Drive {building_filter}",
                    'description': '',
                    'images': [],
                    'amenities': [],
                    'source_url': f"https://maltdrive.com/listing/{building_filter}-malt-drive_{unit_number.text.strip() if unit_number else ''}/".lower()
                }
                
                listings.append(listing)
                
            except Exception as e:
                print(f"Error parsing listing block: {e}")
                continue
        
    except Exception as e:
        print(f"Error scraping Malt Drive: {e}")
    
    return listings


def parse_bedrooms(text: str) -> int:
    """Parse bedroom count from text"""
    text = text.lower()
    if 'studio' in text:
        return 0
    match = re.search(r'(\d+)', text)
    return int(match.group(1)) if match else 1


def parse_bathrooms(text: str) -> float:
    """Parse bathroom count from text"""
    match = re.search(r'(\d+\.?\d*)', text)
    return float(match.group(1)) if match else 1.0


def parse_price(text: str) -> float:
    """Parse price from text"""
    # Remove $ and commas, extract number
    match = re.search(r'[\$]?([\d,]+)', text)
    if match:
        return float(match.group(1).replace(',', ''))
    return 0.0


def parse_sqft(text: str) -> int:
    """Parse square feet from text"""
    match = re.search(r'([\d,]+)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return None


def scrape_maltdrive_unit_details(unit_url: str) -> Dict[str, Any]:
    """
    Scrape detailed information for a specific unit
    
    Args:
        unit_url: URL to specific unit listing
        
    Returns:
        Dictionary with unit details
    """
    details = {
        'description': '',
        'images': [],
        'amenities': []
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(unit_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract description
        description_block = soup.find('div', class_='unit-description')
        if description_block:
            details['description'] = description_block.get_text(strip=True)
        
        # Extract images
        image_tags = soup.find_all('img', class_='unit-image')
        details['images'] = [img['src'] for img in image_tags if img.get('src')]
        
        # Extract amenities
        amenities_list = soup.find('ul', class_='amenities')
        if amenities_list:
            details['amenities'] = [li.get_text(strip=True) for li in amenities_list.find_all('li')]
        
    except Exception as e:
        print(f"Error scraping unit details: {e}")
    
    return details


if __name__ == "__main__":
    # Test the scraper
    print("Testing Malt Drive Scraper")
    print("=" * 70)
    
    # Test scraping for 2-21 building
    listings = scrape_maltdrive_listings("2-21")
    print(f"\nFound {len(listings)} listings for Malt Drive 2-21")
    
    for i, listing in enumerate(listings[:3], 1):  # Show first 3
        print(f"\n{i}. Unit {listing['unit_number']}")
        print(f"   Price: ${listing['price']}/mo")
        print(f"   Beds: {listing['bedrooms']} | Baths: {listing['bathrooms']}")
        if listing['sqft']:
            print(f"   Sqft: {listing['sqft']}")
