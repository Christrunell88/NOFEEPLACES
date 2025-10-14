#!/usr/bin/env python3
"""
Mercedes House Scraper with Playwright
Scrapes apartment listings with REAL images from https://www.mercedeshouseny.com
Uses browser automation to access JavaScript-rendered content
"""

import asyncio
import json
import re
import logging
from typing import List, Dict, Any
from urllib.parse import urljoin
from playwright.async_api import async_playwright, Page

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MercedesHousePlaywrightScraper:
    """Scraper for Mercedes House using Playwright for JavaScript rendering"""
    
    def __init__(self):
        self.base_url = "https://www.mercedeshouseny.com"
        self.listings = []
    
    async def scrape_floorplan_page(self, page: Page, url: str) -> Dict[str, Any]:
        """Scrape a specific floorplan page with Playwright"""
        try:
            logger.info(f"  Navigating to: {url}")
            
            # Navigate to the page
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for images to load
            await page.wait_for_timeout(3000)
            
            # Extract title
            title_elem = await page.query_selector('h1, h2.body-heading')
            title = await title_elem.inner_text() if title_elem else "Mercedes House Unit"
            title = title.strip()
            
            # Extract all images (both img tags and background images)
            images = []
            
            # Method 1: Get img tags
            img_elements = await page.query_selector_all('img[src]')
            for img in img_elements:
                src = await img.get_attribute('src')
                if src and all(x not in src.lower() for x in ['logo', 'icon', 'svg', 'arrow', 'marker', 'ajax-loader']):
                    if not src.startswith('http'):
                        src = urljoin(self.base_url, src)
                    if any(x in src.lower() for x in ['upload', 'content', 'image', 'photo', 'wp-content', 'jpg', 'jpeg', 'png']):
                        if src not in images:
                            images.append(src)
            
            # Method 2: Get background images from CSS (MAIN SOURCE for Mercedes House)
            elements_with_bg = await page.query_selector_all('[style*="background-image"]')
            for elem in elements_with_bg:
                style = await elem.get_attribute('style')
                if style and 'url' in style:
                    # Extract URL from background-image: url('...')
                    url_match = re.search(r'url\([\'"]?([^\'")]+)[\'"]?\)', style)
                    if url_match:
                        bg_url = url_match.group(1)
                        if bg_url not in images:
                            images.append(bg_url)
            
            # Extract specifications from page text
            page_content = await page.content()
            
            # Extract bedrooms
            bedrooms = None
            if 'studio' in title.lower():
                bedrooms = 0
            else:
                bed_match = re.search(r'(\d+)\s*bed', title, re.I)
                if bed_match:
                    bedrooms = int(bed_match.group(1))
            
            # Extract bathrooms
            bathrooms = None
            bath_match = re.search(r'([\d\.]+)\s*bath', page_content, re.I)
            if bath_match:
                bathrooms = float(bath_match.group(1))
            
            # Extract sqft
            sqft = None
            sqft_match = re.search(r'([\d,]+)\s*(?:sq\.?\s?ft|square feet)', page_content, re.I)
            if sqft_match:
                sqft = int(sqft_match.group(1).replace(',', ''))
            
            # Extract price
            price = None
            price_match = re.search(r'\$[\d,]+', page_content)
            if price_match:
                price = price_match.group(0)
            
            # Extract amenities if present
            amenities = []
            amenity_elements = await page.query_selector_all('[class*="amenity"], [class*="feature"]')
            for elem in amenity_elements[:10]:
                text = await elem.inner_text()
                if text and len(text) > 2 and len(text) < 50:
                    amenities.append(text.strip())
            
            listing = {
                'title': title,
                'address': '550 W 54th St, New York, NY 10019',
                'neighborhood': "Hell's Kitchen",
                'borough': 'Manhattan',
                'price': price or 'Contact for Price',
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'sqft': sqft,
                'images': images[:15],  # Limit to 15 best images
                'amenities': amenities,
                'url': url,
                'source': 'Mercedes House NYC',
                'building_name': 'Mercedes House'
            }
            
            logger.info(f"    ✓ {title} - {price or 'N/A'} - {len(images)} images")
            
            return listing
            
        except Exception as e:
            logger.error(f"    ❌ Error scraping {url}: {e}")
            return None
    
    async def scrape_all(self) -> List[Dict[str, Any]]:
        """Scrape all Mercedes House listings"""
        logger.info("\n" + "="*60)
        logger.info("🏢 SCRAPING MERCEDES HOUSE WITH PLAYWRIGHT")
        logger.info("="*60)
        
        async with async_playwright() as p:
            # Launch browser
            logger.info("\n🌐 Launching browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Get floorplan links
            logger.info("\n📋 Step 1: Finding floorplan pages...")
            await page.goto(f"{self.base_url}/floorplans", wait_until='networkidle')
            
            # Wait for content to load
            await page.wait_for_timeout(2000)
            
            # Find all floorplan links
            links = await page.query_selector_all('a[href*="/studio"], a[href*="/one-bed"], a[href*="/two-bed"], a[href*="/terrace"]')
            
            floorplan_urls = set()
            for link in links:
                href = await link.get_attribute('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    if any(term in full_url for term in ['/studio', '/one-bed', '/two-bed', '/terrace']):
                        floorplan_urls.add(full_url)
            
            logger.info(f"  ✅ Found {len(floorplan_urls)} floorplan pages")
            
            # Scrape each floorplan page
            logger.info("\n📸 Step 2: Scraping pages with images...")
            all_listings = []
            
            for i, url in enumerate(sorted(floorplan_urls), 1):
                logger.info(f"\n  [{i}/{len(floorplan_urls)}] {url.split('/')[-1]}")
                listing = await self.scrape_floorplan_page(page, url)
                if listing and listing.get('images'):
                    all_listings.append(listing)
            
            # Close browser
            await browser.close()
        
        logger.info(f"\n✅ Successfully scraped {len(all_listings)} listings with images")
        
        self.listings = all_listings
        return all_listings
    
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
            
            # Count images
            total_images = sum(len(l.get('images', [])) for l in self.listings)
            logger.info(f"  📸 Total images collected: {total_images}")
            
            # Show listings
            for listing in self.listings:
                logger.info(f"\n  • {listing['title']}")
                logger.info(f"    Price: {listing['price']}")
                logger.info(f"    Bedrooms: {listing.get('bedrooms', 'N/A')}")
                logger.info(f"    Bathrooms: {listing.get('bathrooms', 'N/A')}")
                logger.info(f"    Sqft: {listing.get('sqft', 'N/A')}")
                logger.info(f"    Images: {len(listing.get('images', []))}")
        
        logger.info("="*60 + "\n")


async def main():
    """Main execution"""
    logger.info("🚀 Starting Mercedes House Playwright Scraper")
    
    scraper = MercedesHousePlaywrightScraper()
    
    # Scrape all listings
    listings = await scraper.scrape_all()
    
    # Save to JSON
    if listings:
        scraper.save_to_json()
    
    # Print summary
    scraper.print_summary()
    
    logger.info("✅ Scraping complete!")
    
    return listings


if __name__ == "__main__":
    asyncio.run(main())
