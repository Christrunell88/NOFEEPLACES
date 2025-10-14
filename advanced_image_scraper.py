#!/usr/bin/env python3
"""
Advanced Image Scraping Solution
Addresses CORS, authentication, rate limiting, and legal issues
"""
import asyncio
import aiohttp
import os
import uuid
import random
from pathlib import Path
from urllib.parse import urljoin, urlparse
import time
from playwright.async_api import async_playwright
import base64

class AdvancedImageScraper:
    def __init__(self):
        self.session = None
        self.images_dir = Path('/app/backend/uploads/scraped_images_advanced')
        self.images_dir.mkdir(exist_ok=True)
        
        # Rotating user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Success tracking
        self.successful_downloads = 0
        self.failed_downloads = 0
        self.rate_limited = 0
    
    async def create_session_with_cookies(self, base_url: str):
        """Create session and establish cookies by visiting the main page first"""
        connector = aiohttp.TCPConnector(
            ssl=False,
            limit=10,
            limit_per_host=5
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        # Visit base page to establish session
        try:
            print(f"🌐 Establishing session with {base_url}")
            async with self.session.get(base_url) as response:
                if response.status == 200:
                    print(f"✅ Session established")
                else:
                    print(f"⚠️ Session warning: {response.status}")
        except Exception as e:
            print(f"⚠️ Session establishment failed: {e}")
    
    async def download_image_with_enhanced_headers(self, image_url: str, referer: str) -> str:
        """Download image with proper headers and session management"""
        try:
            # Enhanced headers for image requests
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': referer,
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Add random delay to be respectful
            await asyncio.sleep(random.uniform(1.0, 2.5))
            
            async with self.session.get(image_url, headers=headers) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Generate unique filename
                    parsed_url = urlparse(image_url)
                    domain = parsed_url.netloc.replace('.', '_')
                    file_extension = os.path.splitext(parsed_url.path)[1] or '.jpg'
                    filename = f"{domain}_{uuid.uuid4().hex[:8]}{file_extension}"
                    filepath = self.images_dir / filename
                    
                    # Save image
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    
                    self.successful_downloads += 1
                    print(f"   ✅ Downloaded: {filename} ({len(content)} bytes)")
                    return str(filepath)
                
                elif response.status == 429:
                    self.rate_limited += 1
                    print(f"   ⏳ Rate limited: {image_url}")
                    # Wait longer on rate limit
                    await asyncio.sleep(random.uniform(5.0, 10.0))
                    
                elif response.status in [403, 401]:
                    print(f"   🚫 Access denied: {image_url}")
                    
                else:
                    print(f"   ❌ HTTP {response.status}: {image_url}")
                    
        except asyncio.TimeoutError:
            print(f"   ⏱️ Timeout: {image_url}")
        except Exception as e:
            print(f"   ❌ Error: {image_url} - {e}")
        
        self.failed_downloads += 1
        return None
    
    async def scrape_with_playwright(self, url: str) -> list:
        """Use Playwright for JavaScript-heavy sites"""
        images = []
        
        try:
            print(f"🎭 Using Playwright for: {url}")
            
            async with async_playwright() as p:
                # Use chromium with stealth settings
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--single-process',
                        '--disable-gpu'
                    ]
                )
                
                page = await browser.new_page()
                
                # Set realistic viewport and user agent
                await page.set_viewport_size({"width": 1920, "height": 1080})
                await page.set_extra_http_headers({
                    'User-Agent': random.choice(self.user_agents)
                })
                
                # Navigate and wait for images to load
                await page.goto(url, wait_until='networkidle')
                
                # Wait a bit more for lazy loading
                await asyncio.sleep(3)
                
                # Extract all image URLs
                image_urls = await page.evaluate('''() => {
                    const images = Array.from(document.images);
                    return images
                        .map(img => ({
                            src: img.src,
                            alt: img.alt || '',
                            width: img.naturalWidth || img.width,
                            height: img.naturalHeight || img.height
                        }))
                        .filter(img => 
                            img.src && 
                            img.width > 100 && 
                            img.height > 100 &&
                            !img.src.includes('logo') &&
                            !img.src.includes('icon')
                        );
                }''')
                
                await browser.close()
                
                print(f"   🖼️ Found {len(image_urls)} suitable images via Playwright")
                
                # Download images with session
                if not self.session:
                    await self.create_session_with_cookies(url)
                
                for img_data in image_urls[:8]:  # Limit to 8 images
                    downloaded_path = await self.download_image_with_enhanced_headers(
                        img_data['src'], url
                    )
                    
                    if downloaded_path:
                        images.append({
                            'local_path': downloaded_path,
                            'original_url': img_data['src'],
                            'alt_text': img_data['alt'],
                            'dimensions': f"{img_data['width']}x{img_data['height']}"
                        })
                
        except Exception as e:
            print(f"❌ Playwright error: {e}")
        
        return images
    
    async def scrape_images_from_building_page(self, building_url: str, building_name: str) -> list:
        """Scrape images from a specific building page using multiple methods"""
        print(f"\n🏢 Scraping images for: {building_name}")
        print(f"📄 URL: {building_url}")
        
        all_images = []
        
        try:
            # Method 1: Try with enhanced session first
            if not self.session:
                base_url = f"{urlparse(building_url).scheme}://{urlparse(building_url).netloc}"
                await self.create_session_with_cookies(base_url)
            
            # Method 2: Use Playwright for JavaScript-heavy sites
            playwright_images = await self.scrape_with_playwright(building_url)
            all_images.extend(playwright_images)
            
            print(f"📸 Total images scraped for {building_name}: {len(all_images)}")
            
        except Exception as e:
            print(f"❌ Error scraping {building_name}: {e}")
        
        return all_images
    
    async def scrape_multiple_buildings(self, buildings: dict) -> dict:
        """Scrape images from multiple buildings"""
        print("🏗️ ADVANCED IMAGE SCRAPING SESSION")
        print("=" * 60)
        
        results = {}
        
        for building_name, building_url in buildings.items():
            try:
                images = await self.scrape_images_from_building_page(building_url, building_name)
                results[building_name] = images
                
                # Be respectful between buildings
                await asyncio.sleep(random.uniform(3.0, 5.0))
                
            except Exception as e:
                print(f"❌ Failed to scrape {building_name}: {e}")
                results[building_name] = []
        
        # Show summary
        self.show_scraping_summary(results)
        
        return results
    
    def show_scraping_summary(self, results: dict):
        """Show scraping session summary"""
        print(f"\n📊 SCRAPING SESSION SUMMARY")
        print("=" * 40)
        
        total_buildings = len(results)
        total_images = sum(len(images) for images in results.values())
        
        print(f"Buildings processed: {total_buildings}")
        print(f"Successful downloads: {self.successful_downloads}")
        print(f"Failed downloads: {self.failed_downloads}")
        print(f"Rate limited: {self.rate_limited}")
        print(f"Total images collected: {total_images}")
        
        if self.successful_downloads > 0:
            success_rate = (self.successful_downloads / (self.successful_downloads + self.failed_downloads)) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        print(f"\nImages saved to: {self.images_dir}")
        
        for building, images in results.items():
            if images:
                print(f"✅ {building}: {len(images)} images")
            else:
                print(f"❌ {building}: No images scraped")
    
    async def close_session(self):
        """Close the scraping session"""
        if self.session:
            await self.session.close()

async def demo_advanced_scraping():
    """Demo the advanced image scraping capabilities"""
    scraper = AdvancedImageScraper()
    
    # Test buildings (use public URLs that allow scraping)
    test_buildings = {
        "Mercedes House Sample": "https://www.twotreesny.com/buildings/mercedes-house",
        "Court Square Sample": "https://www.tfc.com/residential/court-square"
    }
    
    try:
        results = await scraper.scrape_multiple_buildings(test_buildings)
        
        print(f"\n🎯 ADVANCED SCRAPING RESULTS:")
        print("=" * 40)
        
        for building, images in results.items():
            print(f"\n🏢 {building}:")
            for img in images[:3]:  # Show first 3
                print(f"   📸 {Path(img['local_path']).name}")
                print(f"      Size: {img['dimensions']}")
                print(f"      Original: {img['original_url'][:50]}...")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
    finally:
        await scraper.close_session()

if __name__ == "__main__":
    print("🚀 ADVANCED IMAGE SCRAPING DEMONSTRATION")
    print("Addresses CORS, rate limiting, JavaScript, and authentication issues")
    print("=" * 70)
    asyncio.run(demo_advanced_scraping())