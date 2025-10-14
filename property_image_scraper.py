#!/usr/bin/env python3
"""
Property Image Scraper - Real Estate Listings
Scrapes property images from Zumper, Trulia, RentHop
Organizes by source domain and listing ID
"""

import asyncio
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import hashlib
from pathlib import Path
import time
import random

# Output directories
BASE_DIR = '/app/scraped_property_images'
ZUMPER_DIR = f'{BASE_DIR}/zumper.com'
TRULIA_DIR = f'{BASE_DIR}/trulia.com'
RENTHOP_DIR = f'{BASE_DIR}/renthop.com'


class PropertyImageScraper:
    """Scrape property images from real estate websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.downloaded_hashes = set()  # Track duplicates
        
        # Create directories
        for directory in [ZUMPER_DIR, TRULIA_DIR, RENTHOP_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed per robots.txt"""
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            rp = RobotFileParser()
            rp.set_url(f"{base_url}/robots.txt")
            rp.read()
            
            is_allowed = rp.can_fetch(self.session.headers['User-Agent'], url)
            
            if not is_allowed:
                print(f"  ⛔ Blocked by robots.txt: {url}")
            
            return is_allowed
        except:
            return True  # Allow if can't check
    
    def extract_listing_id(self, url: str) -> str:
        """Extract listing ID from URL"""
        # Common patterns: /apartment/123456 or listing-id-123456 or ?id=123456
        patterns = [
            r'/(\d{6,})',
            r'listing[_-]?(\d+)',
            r'apartment[_-]?(\d+)',
            r'id=(\d+)',
            r'/([a-z0-9\-]{8,})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Fallback: use hash of URL
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def download_image(self, img_url: str, save_dir: str, listing_id: str, img_index: int) -> bool:
        """Download a single image"""
        try:
            # Check if duplicate
            img_hash = hashlib.md5(img_url.encode()).hexdigest()
            if img_hash in self.downloaded_hashes:
                return False
            
            # Download image
            response = self.session.get(img_url, timeout=15)
            if response.status_code == 200:
                # Get file extension
                ext = 'jpg'
                if '.png' in img_url.lower():
                    ext = 'png'
                elif '.webp' in img_url.lower():
                    ext = 'webp'
                
                # Save with listing ID and index
                filename = f"{listing_id}_{img_index}.{ext}"
                filepath = os.path.join(save_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                self.downloaded_hashes.add(img_hash)
                return True
        except Exception as e:
            print(f"    Error downloading image: {e}")
        
        return False
    
    async def scrape_zumper_listings(self, location: str = "new-york-ny") -> dict:
        """Scrape Zumper property images"""
        
        print("\n" + "="*70)
        print("🏢 SCRAPING ZUMPER.COM")
        print("="*70)
        
        results = {'listings': 0, 'images': 0, 'urls': []}
        
        base_url = "https://www.zumper.com"
        search_url = f"{base_url}/apartments-for-rent/{location}"
        
        if not self.check_robots_txt(search_url):
            return results
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                print(f"\n🔍 {search_url}")
                await page.goto(search_url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(3000)
                
                # Find listing links
                listing_links = await page.query_selector_all('a[href*="/apartment/"], a[href*="/building/"]')
                
                unique_urls = set()
                for link in listing_links:
                    href = await link.get_attribute('href')
                    if href:
                        full_url = urljoin(base_url, href)
                        if '/apartment/' in full_url or '/building/' in full_url:
                            unique_urls.add(full_url)
                
                print(f"  Found {len(unique_urls)} listing URLs")
                
                # Scrape each listing
                for i, listing_url in enumerate(list(unique_urls)[:5], 1):  # Limit to 5
                    print(f"\n  [{i}/5] {listing_url[:60]}...")
                    
                    listing_id = self.extract_listing_id(listing_url)
                    
                    try:
                        await page.goto(listing_url, wait_until='networkidle', timeout=20000)
                        await page.wait_for_timeout(2000)
                        
                        # Find property images
                        img_elements = await page.query_selector_all('img[src*="zumper"], img[src*="cloudfront"]')
                        
                        img_count = 0
                        for idx, img in enumerate(img_elements[:10], 1):
                            src = await img.get_attribute('src')
                            if src and all(x not in src.lower() for x in ['logo', 'icon', 'avatar', 'user']):
                                if src.startswith('//'):
                                    src = 'https:' + src
                                
                                if self.download_image(src, ZUMPER_DIR, listing_id, idx):
                                    img_count += 1
                        
                        if img_count > 0:
                            results['listings'] += 1
                            results['images'] += img_count
                            results['urls'].append(listing_url)
                            print(f"    ✅ Downloaded {img_count} images")
                    
                    except Exception as e:
                        print(f"    ⚠️ Error: {e}")
                    
                    time.sleep(random.uniform(2, 4))  # Respectful delay
            
            finally:
                await browser.close()
        
        return results
    
    async def scrape_trulia_listings(self, location: str = "New_York,NY") -> dict:
        """Scrape Trulia property images"""
        
        print("\n" + "="*70)
        print("🏢 SCRAPING TRULIA.COM")
        print("="*70)
        
        results = {'listings': 0, 'images': 0, 'urls': []}
        
        base_url = "https://www.trulia.com"
        search_url = f"{base_url}/for_rent/{location}"
        
        if not self.check_robots_txt(search_url):
            return results
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                print(f"\n🔍 {search_url}")
                await page.goto(search_url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(3000)
                
                # Find listing links
                listing_links = await page.query_selector_all('a[href*="/c/"]')
                
                unique_urls = set()
                for link in listing_links:
                    href = await link.get_attribute('href')
                    if href and '/c/' in href:
                        full_url = urljoin(base_url, href)
                        unique_urls.add(full_url)
                
                print(f"  Found {len(unique_urls)} listing URLs")
                
                # Scrape each listing
                for i, listing_url in enumerate(list(unique_urls)[:5], 1):  # Limit to 5
                    print(f"\n  [{i}/5] {listing_url[:60]}...")
                    
                    listing_id = self.extract_listing_id(listing_url)
                    
                    try:
                        await page.goto(listing_url, wait_until='networkidle', timeout=20000)
                        await page.wait_for_timeout(2000)
                        
                        # Find property images
                        img_elements = await page.query_selector_all('img[src]')
                        
                        img_count = 0
                        for idx, img in enumerate(img_elements[:10], 1):
                            src = await img.get_attribute('src')
                            if src and all(x not in src.lower() for x in ['logo', 'icon', 'avatar']):
                                if src.startswith('//'):
                                    src = 'https:' + src
                                
                                # Only property images
                                if any(x in src.lower() for x in ['property', 'listing', 'photo', 'image']):
                                    if self.download_image(src, TRULIA_DIR, listing_id, idx):
                                        img_count += 1
                        
                        if img_count > 0:
                            results['listings'] += 1
                            results['images'] += img_count
                            results['urls'].append(listing_url)
                            print(f"    ✅ Downloaded {img_count} images")
                    
                    except Exception as e:
                        print(f"    ⚠️ Error: {e}")
                    
                    time.sleep(random.uniform(2, 4))  # Respectful delay
            
            finally:
                await browser.close()
        
        return results
    
    async def scrape_renthop_listings(self, location: str = "nyc") -> dict:
        """Scrape RentHop property images"""
        
        print("\n" + "="*70)
        print("🏢 SCRAPING RENTHOP.COM")
        print("="*70)
        
        results = {'listings': 0, 'images': 0, 'urls': []}
        
        base_url = "https://www.renthop.com"
        search_url = f"{base_url}/search/{location}"
        
        if not self.check_robots_txt(search_url):
            return results
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                print(f"\n🔍 {search_url}")
                await page.goto(search_url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(3000)
                
                # Find listing links
                listing_links = await page.query_selector_all('a[href*="/listings/"]')
                
                unique_urls = set()
                for link in listing_links:
                    href = await link.get_attribute('href')
                    if href and '/listings/' in href:
                        full_url = urljoin(base_url, href)
                        unique_urls.add(full_url)
                
                print(f"  Found {len(unique_urls)} listing URLs")
                
                # Scrape each listing
                for i, listing_url in enumerate(list(unique_urls)[:5], 1):  # Limit to 5
                    print(f"\n  [{i}/5] {listing_url[:60]}...")
                    
                    listing_id = self.extract_listing_id(listing_url)
                    
                    try:
                        await page.goto(listing_url, wait_until='networkidle', timeout=20000)
                        await page.wait_for_timeout(2000)
                        
                        # Find property images
                        img_elements = await page.query_selector_all('img[src]')
                        
                        img_count = 0
                        for idx, img in enumerate(img_elements[:10], 1):
                            src = await img.get_attribute('src')
                            if src and all(x not in src.lower() for x in ['logo', 'icon', 'avatar']):
                                if src.startswith('//'):
                                    src = 'https:' + src
                                
                                if self.download_image(src, RENTHOP_DIR, listing_id, idx):
                                    img_count += 1
                        
                        if img_count > 0:
                            results['listings'] += 1
                            results['images'] += img_count
                            results['urls'].append(listing_url)
                            print(f"    ✅ Downloaded {img_count} images")
                    
                    except Exception as e:
                        print(f"    ⚠️ Error: {e}")
                    
                    time.sleep(random.uniform(2, 4))  # Respectful delay
            
            finally:
                await browser.close()
        
        return results


async def main():
    """Main execution"""
    print("🚀 Property Image Scraper - Real Estate Listings")
    print("Respects robots.txt and avoids login")
    
    scraper = PropertyImageScraper()
    
    # Scrape all sites
    zumper_results = await scraper.scrape_zumper_listings()
    trulia_results = await scraper.scrape_trulia_listings()
    renthop_results = await scraper.scrape_renthop_listings()
    
    # Summary
    print("\n" + "="*70)
    print("📊 SCRAPING SUMMARY")
    print("="*70)
    
    print(f"\n🏢 Zumper.com:")
    print(f"   Listings: {zumper_results['listings']}")
    print(f"   Images: {zumper_results['images']}")
    print(f"   Saved to: {ZUMPER_DIR}")
    
    print(f"\n🏢 Trulia.com:")
    print(f"   Listings: {trulia_results['listings']}")
    print(f"   Images: {trulia_results['images']}")
    print(f"   Saved to: {TRULIA_DIR}")
    
    print(f"\n🏢 RentHop.com:")
    print(f"   Listings: {renthop_results['listings']}")
    print(f"   Images: {renthop_results['images']}")
    print(f"   Saved to: {RENTHOP_DIR}")
    
    total_listings = zumper_results['listings'] + trulia_results['listings'] + renthop_results['listings']
    total_images = zumper_results['images'] + trulia_results['images'] + renthop_results['images']
    
    print(f"\n📦 TOTAL:")
    print(f"   Listings scraped: {total_listings}")
    print(f"   Images downloaded: {total_images}")
    print(f"   Duplicates skipped: {len(scraper.downloaded_hashes) - total_images}")
    
    print("\n✅ Scraping complete!")


if __name__ == "__main__":
    asyncio.run(main())
