#!/usr/bin/env python3
"""
Mercedes House Scraper
Scrapes apartment listings from https://www.mercedeshouseny.com
Extracts: title, address, price, bedrooms, bathrooms, sqft, images, and listing URLs
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import List, Dict, Any
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MercedesHouseScraper:
    """Scraper for Mercedes House NYC apartment listings"""
    
    def __init__(self):
        self.base_url = "https://www.mercedeshouseny.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.mercedeshouseny.com/'
        })
        self.listings = []
    
    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch page content"""
        try:
            logger.info(f"Fetching: {url}")
            time.sleep(2)  # Respectful delay
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Status {response.status_code} for {url}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_price(self, text: str) -> str:
        """Extract price from text"""
        if not text:
            return None
        
        # Look for price patterns
        price_pattern = r'\$[\d,]+(?:\.\d{2})?'
        matches = re.findall(price_pattern, text)
        
        if matches:
            return matches[0]
        
        return None
    
    def extract_number(self, text: str) -> int:
        """Extract first number from text"""
        if not text:
            return None
        
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        return None
    
    def scrape_floorplan_page(self, url: str) -> List[Dict[str, Any]]:
        """Scrape a specific floorplan page"""
        listings = []
        
        soup = self.fetch_page(url)
        if not soup:
            return listings
        
        # Extract the floorplan type from title or heading
        page_title = soup.find('title')
        plan_type = page_title.get_text() if page_title else "Mercedes House Unit"
        
        # Look for main heading
        main_heading = soup.find(['h1', 'h2'], class_=re.compile(r'heading|title', re.I))
        if main_heading:
            plan_type = main_heading.get_text(strip=True)
        
        # Extract all images from the page
        images = []
        img_tags = soup.find_all('img', src=True)
        for img in img_tags:
            img_url = img['src']
            if not img_url.startswith('http'):
                img_url = urljoin(self.base_url, img_url)
            # Filter out small icons/logos
            if all(x not in img_url.lower() for x in ['logo', 'icon', 'svg', 'arrow', 'marker']):
                # Only include content/upload images (actual apartment photos)
                if any(x in img_url.lower() for x in ['upload', 'content', 'image', 'photo', 'wp-content']):
                    images.append(img_url)
        
        # Extract specifications
        specs = {}
        
        # Look for spec items
        spec_elements = soup.find_all(['div', 'span', 'p'], class_=re.compile(r'spec|detail|info', re.I))
        spec_elements += soup.find_all(['div', 'span', 'p'], string=re.compile(r'(sqft|sq\. ft|bedroom|bathroom|bath)', re.I))
        
        for elem in spec_elements:
            text = elem.get_text(strip=True)
            
            # Extract sqft
            sqft_match = re.search(r'([\d,]+)\s*(?:sq\.?\s?ft|sqft)', text, re.I)
            if sqft_match and 'sqft' not in specs:
                specs['sqft'] = int(sqft_match.group(1).replace(',', ''))
            
            # Extract bedrooms
            bed_match = re.search(r'(\d+)\s*bedroom', text, re.I)
            if bed_match and 'bedrooms' not in specs:
                specs['bedrooms'] = int(bed_match.group(1))
            
            # Extract bathrooms
            bath_match = re.search(r'([\d\.]+)\s*bathroom', text, re.I)
            if bath_match and 'bathrooms' not in specs:
                specs['bathrooms'] = float(bath_match.group(1))
        
        # Check if it's a studio from title
        if 'studio' in plan_type.lower():
            specs['bedrooms'] = 0
        
        # Extract price if available
        price_elem = soup.find(['span', 'div', 'p'], string=re.compile(r'\$[\d,]+'))
        price = None
        if price_elem:
            price = self.extract_price(price_elem.get_text())
        
        # Create listing
        listing = {
            'title': plan_type,
            'address': '550 W 54th St, New York, NY 10019',
            'neighborhood': "Hell's Kitchen",
            'borough': 'Manhattan',
            'price': price or 'Contact for Price',
            'bedrooms': specs.get('bedrooms'),
            'bathrooms': specs.get('bathrooms'),
            'sqft': specs.get('sqft'),
            'images': images[:10],  # Limit to 10 images
            'url': url,
            'source': 'Mercedes House NYC',
            'building_name': 'Mercedes House'
        }
        
        if images:  # Only add if we found images
            listings.append(listing)
            logger.info(f"    ✓ {plan_type} - {len(images)} images")
        
        return listings
    
    def scrape_availabilities(self) -> List[Dict[str, Any]]:
        """Scrape the availabilities and floorplans pages"""
        logger.info("\n" + "="*60)
        logger.info("🏢 SCRAPING MERCEDES HOUSE")
        logger.info("="*60)
        
        all_listings = []
        
        # First, get the floorplans index page
        logger.info(f"\nStep 1: Finding floorplan links...")
        soup = self.fetch_page(f"{self.base_url}/floorplans")
        
        if not soup:
            logger.warning("Could not fetch floorplans page")
            return []
        
        # Find all floorplan links
        floorplan_links = set()
        mosaic_items = soup.find_all(['div', 'a'], class_=re.compile(r'mosaic', re.I))
        
        for item in mosaic_items:
            link = item.find('a', href=True)
            if link:
                href = link['href']
                # Filter relevant links
                if any(term in href.lower() for term in ['studio', 'bed', 'terrace', 'floor']):
                    full_url = urljoin(self.base_url, href)
                    floorplan_links.add(full_url)
        
        logger.info(f"  Found {len(floorplan_links)} floorplan pages to scrape")
        
        # Scrape each floorplan page
        logger.info(f"\nStep 2: Scraping individual floorplan pages...")
        for i, url in enumerate(sorted(floorplan_links), 1):
            logger.info(f"\n  [{i}/{len(floorplan_links)}] {url}")
            listings = self.scrape_floorplan_page(url)
            all_listings.extend(listings)
        
        logger.info(f"\n✅ Extracted {len(all_listings)} unique listings from Mercedes House")
        
        self.listings = all_listings
        return all_listings
    
    def check_for_api_endpoints(self):
        """Check for potential API endpoints or data feeds"""
        logger.info("\n🔍 Checking for API endpoints...")
        
        # Common API patterns for apartment listings
        potential_apis = [
            f"{self.base_url}/api/units",
            f"{self.base_url}/api/availability",
            f"{self.base_url}/api/apartments",
            f"{self.base_url}/availabilities.json",
            f"{self.base_url}/units.json",
        ]
        
        for api_url in potential_apis:
            try:
                response = self.session.get(api_url, timeout=5)
                if response.status_code == 200:
                    logger.info(f"  ✅ Found API: {api_url}")
                    try:
                        data = response.json()
                        logger.info(f"     Data structure: {list(data.keys())[:5] if isinstance(data, dict) else f'Array with {len(data)} items'}")
                    except:
                        logger.info(f"     Response is not JSON")
            except:
                pass
    
    def save_to_json(self, filename: str = "mercedes_house_listings.json") -> bool:
        """Save listings to JSON file"""
        try:
            if len(self.listings) == 0:
                logger.warning(f"\n⚠️  No listings to save")
                return False
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.listings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"\n💾 Saved {len(self.listings)} listings to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving to JSON: {e}")
            return False
    
    def print_summary(self):
        """Print summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 SCRAPING SUMMARY - Mercedes House")
        logger.info("="*60)
        
        if len(self.listings) == 0:
            logger.info("  ⚠️  No listings extracted")
        else:
            logger.info(f"  ✅ Total listings: {len(self.listings)}")
            
            # Count listings with images
            with_images = sum(1 for l in self.listings if l.get('images'))
            logger.info(f"  📸 Listings with images: {with_images}")
            
            # Price range
            prices = [l.get('price', '') for l in self.listings if l.get('price') and '$' in str(l.get('price'))]
            if prices:
                logger.info(f"  💰 Sample prices: {', '.join(prices[:3])}")
        
        logger.info("="*60 + "\n")


def main():
    """Main execution"""
    logger.info("🚀 Starting Mercedes House Scraper")
    
    scraper = MercedesHouseScraper()
    
    # Check for API endpoints first
    scraper.check_for_api_endpoints()
    
    # Scrape availabilities
    listings = scraper.scrape_availabilities()
    
    # Save to JSON
    if listings:
        scraper.save_to_json()
    
    # Print summary
    scraper.print_summary()
    
    # Print sample listings
    if listings:
        logger.info("📋 Sample Listings:\n")
        for i, listing in enumerate(listings[:3], 1):
            logger.info(f"{i}. {listing['title']}")
            logger.info(f"   Price: {listing['price']}")
            logger.info(f"   Bedrooms: {listing.get('bedrooms', 'N/A')}")
            logger.info(f"   Bathrooms: {listing.get('bathrooms', 'N/A')}")
            logger.info(f"   Sqft: {listing.get('sqft', 'N/A')}")
            logger.info(f"   Images: {len(listing.get('images', []))}")
            logger.info(f"   URL: {listing['url']}\n")
    
    logger.info("✅ Scraping complete!")
    
    return listings


if __name__ == "__main__":
    main()
