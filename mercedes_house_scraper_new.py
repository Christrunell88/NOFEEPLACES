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
        """Scrape the availabilities section"""
        logger.info("\n" + "="*60)
        logger.info("🏢 SCRAPING MERCEDES HOUSE")
        logger.info("="*60)
        
        # Try the main availabilities page
        url = f"{self.base_url}/#availabilities"
        soup = self.fetch_page(self.base_url)
        
        if not soup:
            logger.error("Could not fetch Mercedes House homepage")
            return []
        
        # Look for apartment/unit listings
        # Common patterns for luxury apartment websites
        listings_found = []
        
        # Strategy 1: Look for availability/apartment cards
        apartment_cards = soup.find_all(['div', 'article'], class_=re.compile(r'(apartment|unit|availability|listing|floorplan)', re.I))
        logger.info(f"Found {len(apartment_cards)} potential apartment cards")
        
        # Strategy 2: Look for table rows with apartment data
        availability_tables = soup.find_all('table')
        logger.info(f"Found {len(availability_tables)} tables")
        
        # Strategy 3: Look for script tags with JSON data (many sites embed data this way)
        scripts = soup.find_all('script', type='application/json')
        logger.info(f"Found {len(scripts)} JSON scripts")
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                logger.info(f"Found JSON data: {list(data.keys())[:5] if isinstance(data, dict) else 'array'}")
            except:
                pass
        
        # Strategy 4: Look for iframe (many availability widgets use iframes)
        iframes = soup.find_all('iframe')
        logger.info(f"Found {len(iframes)} iframes")
        
        for iframe in iframes:
            src = iframe.get('src', '')
            if 'apartment' in src.lower() or 'availability' in src.lower() or 'floorplan' in src.lower():
                logger.info(f"  Potential availability iframe: {src}")
        
        # Try to extract from cards
        for card in apartment_cards[:20]:  # Limit to first 20
            try:
                # Extract basic info
                title_elem = card.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'(title|name|unit)', re.I))
                title = title_elem.get_text(strip=True) if title_elem else None
                
                # Extract link
                link_elem = card.find('a', href=True)
                listing_url = urljoin(self.base_url, link_elem['href']) if link_elem else None
                
                # Extract price
                price_elem = card.find(['span', 'div', 'p'], class_=re.compile(r'price|rent', re.I))
                price_text = price_elem.get_text(strip=True) if price_elem else None
                price = self.extract_price(price_text)
                
                # Extract bedrooms
                bed_elem = card.find(['span', 'div'], string=re.compile(r'bed|br', re.I))
                bedrooms = self.extract_number(bed_elem.get_text() if bed_elem else None)
                
                # Extract bathrooms
                bath_elem = card.find(['span', 'div'], string=re.compile(r'bath|ba', re.I))
                bathrooms = self.extract_number(bath_elem.get_text() if bath_elem else None)
                
                # Extract sqft
                sqft_elem = card.find(['span', 'div'], string=re.compile(r'sq\.?\s?ft|sqft', re.I))
                sqft = self.extract_number(sqft_elem.get_text() if sqft_elem else None)
                
                # Extract images
                images = []
                img_tags = card.find_all('img', src=True)
                for img in img_tags:
                    img_url = img['src']
                    if not img_url.startswith('http'):
                        img_url = urljoin(self.base_url, img_url)
                    # Filter out small icons/logos
                    if 'logo' not in img_url.lower() and 'icon' not in img_url.lower():
                        images.append(img_url)
                
                if title or price:
                    listing = {
                        'title': title or 'Mercedes House Apartment',
                        'address': '550 W 54th St, New York, NY 10019',
                        'price': price or 'Contact for Price',
                        'bedrooms': bedrooms,
                        'bathrooms': bathrooms,
                        'sqft': sqft,
                        'images': images,
                        'url': listing_url or self.base_url,
                        'source': 'Mercedes House NYC'
                    }
                    listings_found.append(listing)
                    logger.info(f"  ✓ {listing['title']} - {listing['price']}")
            
            except Exception as e:
                logger.debug(f"Error parsing card: {e}")
                continue
        
        # Try to extract from tables
        if len(listings_found) == 0:
            logger.info("\nTrying table extraction...")
            for table in availability_tables:
                rows = table.find_all('tr')[1:]  # Skip header
                logger.info(f"  Processing table with {len(rows)} rows")
                
                for row in rows[:10]:  # Limit to first 10
                    try:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) < 3:
                            continue
                        
                        # Try to extract data from cells
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        
                        # Look for price in any cell
                        price = None
                        for cell_text in row_data:
                            price = self.extract_price(cell_text)
                            if price:
                                break
                        
                        if price:
                            listing = {
                                'title': f"Mercedes House Unit - {row_data[0]}" if row_data else "Mercedes House Apartment",
                                'address': '550 W 54th St, New York, NY 10019',
                                'price': price,
                                'bedrooms': None,
                                'bathrooms': None,
                                'sqft': None,
                                'images': [],
                                'url': self.base_url,
                                'source': 'Mercedes House NYC',
                                'raw_data': ' | '.join(row_data[:5])  # Include raw data for reference
                            }
                            listings_found.append(listing)
                            logger.info(f"  ✓ Found listing: {price}")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing table row: {e}")
                        continue
        
        logger.info(f"\n✅ Extracted {len(listings_found)} listings from Mercedes House")
        
        self.listings = listings_found
        return listings_found
    
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
