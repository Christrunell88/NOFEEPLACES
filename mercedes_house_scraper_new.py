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
    
    def scrape_availabilities(self) -> List[Dict[str, Any]]:
        """Scrape the availabilities and floorplans pages"""
        logger.info("\n" + "="*60)
        logger.info("🏢 SCRAPING MERCEDES HOUSE")
        logger.info("="*60)
        
        all_listings = []
        
        # Scrape both pages
        pages_to_scrape = [
            f"{self.base_url}/availabilities",
            f"{self.base_url}/floorplans",
            f"{self.base_url}/residences"
        ]
        
        for page_url in pages_to_scrape:
            logger.info(f"\nScraping: {page_url}")
            soup = self.fetch_page(page_url)
            
            if not soup:
                logger.warning(f"  Could not fetch {page_url}")
                continue
            
            # Extract all images from the page (for apartments)
            all_images = soup.find_all('img', src=True)
            apartment_images = []
            for img in all_images:
                img_url = img['src']
                if not img_url.startswith('http'):
                    img_url = urljoin(self.base_url, img_url)
                # Filter out small icons/logos and keep apartment photos
                if all(x not in img_url.lower() for x in ['logo', 'icon', 'svg', 'arrow']):
                    # Check if image is large enough (apartment photos)
                    if 'upload' in img_url or 'content' in img_url or 'image' in img_url:
                        apartment_images.append(img_url)
            
            logger.info(f"  Found {len(apartment_images)} potential apartment images")
            
            # Look for apartment/floorplan cards
            cards = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'(floor|plan|unit|apartment|mosaic|tile)', re.I))
            logger.info(f"  Found {len(cards)} potential listing cards")
            
            for card in cards[:30]:
                try:
                    # Extract title/unit type
                    title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'a'], class_=re.compile(r'(title|heading|name)', re.I))
                    if not title_elem:
                        title_elem = card.find(['h1', 'h2', 'h3', 'h4'])
                    title = title_elem.get_text(strip=True) if title_elem else None
                    
                    # Skip if no meaningful title
                    if not title or len(title) < 3:
                        continue
                    
                    # Extract link
                    link_elem = card.find('a', href=True)
                    listing_url = urljoin(self.base_url, link_elem['href']) if link_elem else page_url
                    
                    # Extract price
                    price_elem = card.find(['span', 'div', 'p'], string=re.compile(r'\$[\d,]+', re.I))
                    if not price_elem:
                        price_elem = card.find(['span', 'div', 'p'], class_=re.compile(r'price|rent', re.I))
                    price = self.extract_price(price_elem.get_text() if price_elem else None)
                    
                    # Extract bedrooms from title or separate element
                    bedrooms = None
                    if title:
                        if 'studio' in title.lower():
                            bedrooms = 0
                        else:
                            bed_match = re.search(r'(\d+)\s*bed', title, re.I)
                            if bed_match:
                                bedrooms = int(bed_match.group(1))
                    
                    # Extract bathrooms
                    bath_elem = card.find(['span', 'div'], string=re.compile(r'\d+\.?\d*\s*bath', re.I))
                    bathrooms = None
                    if bath_elem:
                        bath_match = re.search(r'([\d\.]+)', bath_elem.get_text())
                        if bath_match:
                            bathrooms = float(bath_match.group(1))
                    
                    # Extract sqft
                    sqft_elem = card.find(['span', 'div'], string=re.compile(r'\d+\s*sq', re.I))
                    sqft = None
                    if sqft_elem:
                        sqft_match = re.search(r'(\d[\d,]*)', sqft_elem.get_text())
                        if sqft_match:
                            sqft = int(sqft_match.group(1).replace(',', ''))
                    
                    # Extract images from this card
                    card_images = []
                    img_tags = card.find_all('img', src=True)
                    for img in img_tags:
                        img_url = img['src']
                        if not img_url.startswith('http'):
                            img_url = urljoin(self.base_url, img_url)
                        if all(x not in img_url.lower() for x in ['logo', 'icon', 'svg']):
                            card_images.append(img_url)
                    
                    # If card has no images, use some from the general pool
                    if not card_images and apartment_images:
                        card_images = apartment_images[:5]
                    
                    # Create listing
                    listing = {
                        'title': title,
                        'address': '550 W 54th St, New York, NY 10019',
                        'neighborhood': "Hell's Kitchen",
                        'borough': 'Manhattan',
                        'price': price or 'Contact for Price',
                        'bedrooms': bedrooms,
                        'bathrooms': bathrooms,
                        'sqft': sqft,
                        'images': card_images,
                        'url': listing_url,
                        'source': 'Mercedes House NYC',
                        'building_name': 'Mercedes House'
                    }
                    
                    # Only add if we have title and it's not a duplicate
                    if title and not any(l['title'] == title for l in all_listings):
                        all_listings.append(listing)
                        logger.info(f"    ✓ {title} - {price or 'N/A'} - {len(card_images)} images")
                
                except Exception as e:
                    logger.debug(f"  Error parsing card: {e}")
                    continue
        
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
