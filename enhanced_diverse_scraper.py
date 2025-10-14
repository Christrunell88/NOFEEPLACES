#!/usr/bin/env python3
"""
Enhanced Diverse Image Scraper
Test advanced scraping with multiple buildings and ensure diverse images
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
import hashlib

class EnhancedDiverseScraper:
    def __init__(self):
        self.session = None
        self.images_dir = Path('/app/backend/uploads/diverse_scraped_images')
        self.images_dir.mkdir(exist_ok=True)
        
        # Clear previous images for fresh test
        for old_image in self.images_dir.glob('*'):
            old_image.unlink()
        
        # More diverse building sources
        self.diverse_buildings = {
            'Mercedes House - Two Trees': {
                'url': 'https://www.twotreesny.com/buildings/mercedes-house',
                'gallery_selectors': [
                    'img[src*="apartment"]',
                    'img[src*="unit"]', 
                    'img[src*="interior"]',
                    'img[src*="kitchen"]',
                    'img[src*="bedroom"]',
                    'img[src*="living"]'
                ]
            },
            'DUMBO Heights - Two Trees': {
                'url': 'https://www.twotreesny.com/buildings/dumbo-heights',
                'gallery_selectors': [
                    'img[src*="apartment"]',
                    'img[src*="unit"]',
                    'img[src*="view"]'
                ]
            },
            'Court Square - TFC': {
                'url': 'https://www.tfc.com/residential/court-square',
                'gallery_selectors': [
                    'img[src*="apartment"]',
                    'img[src*="interior"]',
                    'img[src*="amenity"]'
                ]
            },
            'West River House - Manhattan Skyline': {
                'url': 'https://manhattanskyline.com/buildings/upper-west-side/west-river-house',
                'gallery_selectors': [
                    'img[src*="apartment"]',
                    'img[src*="unit"]',
                    'img[src*="interior"]'
                ]
            }
        }
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Track image diversity
        self.image_hashes = set()
        self.successful_downloads = 0
        self.duplicate_skips = 0
        self.failed_downloads = 0
    
    def get_image_hash(self, image_data: bytes) -> str:
        """Get hash of image to detect duplicates"""
        return hashlib.md5(image_data).hexdigest()
    
    async def create_enhanced_session(self, base_url: str):
        """Create enhanced session with better headers"""
        connector = aiohttp.TCPConnector(
            ssl=False,
            limit=15,
            limit_per_host=8,
            keepalive_timeout=30
        )
        
        timeout = aiohttp.ClientTimeout(total=45, connect=15)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/avif,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            }
        )
        
        # Establish session
        try:
            print(f"🌐 Establishing enhanced session with {base_url}")
            async with self.session.get(base_url) as response:
                print(f"   Session status: {response.status}")
        except Exception as e:
            print(f"   Session warning: {e}")
    
    async def download_diverse_image(self, image_url: str, referer: str, building_name: str) -> str:
        """Download image with diversity checking"""
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'image/webp,image/apng,image/jpeg,image/png,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': referer,
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
                'Cache-Control': 'no-cache'
            }
            
            # Respectful delay
            await asyncio.sleep(random.uniform(1.5, 3.0))
            
            async with self.session.get(image_url, headers=headers) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Check for duplicate content
                    image_hash = self.get_image_hash(content)
                    if image_hash in self.image_hashes:
                        print(f"   🔄 Skipping duplicate: {image_url}")
                        self.duplicate_skips += 1
                        return None
                    
                    self.image_hashes.add(image_hash)
                    
                    # Create descriptive filename
                    parsed_url = urlparse(image_url)
                    domain = parsed_url.netloc.replace('.', '_')
                    building_clean = building_name.lower().replace(' ', '_').replace('-', '_')
                    file_extension = os.path.splitext(parsed_url.path)[1] or '.jpg'
                    filename = f"{building_clean}_{domain}_{uuid.uuid4().hex[:8]}{file_extension}"
                    filepath = self.images_dir / filename
                    
                    # Save image
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    
                    self.successful_downloads += 1
                    print(f"   ✅ Downloaded: {filename} ({len(content)} bytes)")
                    return str(filepath)
                
                else:
                    print(f"   ❌ HTTP {response.status}: {image_url}")
                    
        except Exception as e:
            print(f"   ❌ Error: {image_url} - {e}")
        
        self.failed_downloads += 1
        return None
    
    async def scrape_building_with_playwright(self, building_name: str, building_data: dict) -> list:
        """Enhanced Playwright scraping with specific selectors"""
        images = []
        url = building_data['url']
        
        try:
            print(f"\n🏢 Enhanced scraping: {building_name}")
            print(f"📄 URL: {url}")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=random.choice(self.user_agents)
                )
                
                page = await context.new_page()
                
                # Navigate and wait for content
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(4)  # Extra wait for lazy loading
                
                # Try scrolling to load more images
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')
                await asyncio.sleep(2)
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(3)
                
                # Extract images with multiple strategies
                print("   🔍 Extracting images with enhanced selectors...")
                
                # Strategy 1: Use specific selectors
                for selector in building_data['gallery_selectors']:
                    try:
                        elements = await page.locator(selector).all()
                        print(f"      Found {len(elements)} images with selector: {selector}")
                    except:
                        continue
                
                # Strategy 2: Get all high-quality images
                image_data = await page.evaluate('''() => {
                    const images = Array.from(document.images);
                    return images
                        .map(img => ({
                            src: img.src,
                            alt: img.alt || '',
                            width: img.naturalWidth || img.width || 0,
                            height: img.naturalHeight || img.height || 0,
                            className: img.className || '',
                            parent: img.parentElement?.tagName || ''
                        }))
                        .filter(img => {
                            // Filter for apartment/interior images
                            const src = img.src.toLowerCase();
                            const alt = img.alt.toLowerCase();
                            const className = img.className.toLowerCase();
                            
                            // Include apartment-related images
                            const apartmentKeywords = [
                                'apartment', 'unit', 'interior', 'kitchen', 'bedroom', 
                                'living', 'bathroom', 'amenity', 'view', 'room'
                            ];
                            
                            const hasApartmentKeyword = apartmentKeywords.some(keyword => 
                                src.includes(keyword) || alt.includes(keyword) || className.includes(keyword)
                            );
                            
                            // Exclude logos, icons, etc.
                            const excludeKeywords = ['logo', 'icon', 'nav', 'menu', 'button'];
                            const hasExcludeKeyword = excludeKeywords.some(keyword => 
                                src.includes(keyword) || alt.includes(keyword) || className.includes(keyword)
                            );
                            
                            return img.src && 
                                   img.width >= 200 && 
                                   img.height >= 150 && 
                                   (hasApartmentKeyword || img.width > 800) &&
                                   !hasExcludeKeyword;
                        })
                        .sort((a, b) => (b.width * b.height) - (a.width * a.height)); // Sort by size
                }''')
                
                await browser.close()
                
                print(f"   📸 Found {len(image_data)} diverse images")
                
                # Download diverse images
                if not self.session:
                    await self.create_enhanced_session(url)
                
                for img in image_data[:12]:  # Increased limit for diversity
                    downloaded_path = await self.download_diverse_image(
                        img['src'], url, building_name
                    )
                    
                    if downloaded_path:
                        images.append({
                            'local_path': downloaded_path,
                            'original_url': img['src'],
                            'alt_text': img['alt'],
                            'dimensions': f"{img['width']}x{img['height']}",
                            'building': building_name
                        })
                
        except Exception as e:
            print(f"❌ Playwright error for {building_name}: {e}")
        
        return images
    
    async def test_diverse_scraping(self):
        """Test enhanced diverse scraping across multiple buildings"""
        print("🚀 TESTING ENHANCED DIVERSE IMAGE SCRAPER")
        print("=" * 70)
        print("🎯 Goal: Get diverse, unique apartment images from multiple buildings")
        print("=" * 70)
        
        all_results = {}
        
        for building_name, building_data in self.diverse_buildings.items():
            try:
                images = await self.scrape_building_with_playwright(building_name, building_data)
                all_results[building_name] = images
                
                # Respectful delay between buildings
                await asyncio.sleep(random.uniform(4.0, 7.0))
                
            except Exception as e:
                print(f"❌ Failed {building_name}: {e}")
                all_results[building_name] = []
        
        # Show comprehensive results
        self.show_diversity_results(all_results)
        
        return all_results
    
    def show_diversity_results(self, results: dict):
        """Show detailed diversity analysis"""
        print(f"\n📊 ENHANCED SCRAPING DIVERSITY ANALYSIS")
        print("=" * 60)
        
        total_buildings = len(results)
        total_unique_images = len(self.image_hashes)
        
        print(f"Buildings processed: {total_buildings}")
        print(f"Unique images downloaded: {total_unique_images}")
        print(f"Successful downloads: {self.successful_downloads}")
        print(f"Duplicates skipped: {self.duplicate_skips}")
        print(f"Failed downloads: {self.failed_downloads}")
        
        if self.successful_downloads > 0:
            success_rate = (self.successful_downloads / (self.successful_downloads + self.failed_downloads)) * 100
            uniqueness_rate = (total_unique_images / self.successful_downloads) * 100 if self.successful_downloads > 0 else 0
            print(f"Success rate: {success_rate:.1f}%")
            print(f"Uniqueness rate: {uniqueness_rate:.1f}%")
        
        print(f"\n🏢 BUILDING-SPECIFIC RESULTS:")
        for building, images in results.items():
            if images:
                print(f"✅ {building}: {len(images)} unique images")
                # Show sample image info
                if images:
                    sample = images[0]
                    print(f"      Sample: {Path(sample['local_path']).name}")
                    print(f"      Size: {sample['dimensions']}")
            else:
                print(f"❌ {building}: No images scraped")
        
        print(f"\n💾 Images saved to: {self.images_dir}")
    
    async def close_session(self):
        """Close session"""
        if self.session:
            await self.session.close()

async def main():
    """Run enhanced diverse scraping test"""
    scraper = EnhancedDiverseScraper()
    
    try:
        results = await scraper.test_diverse_scraping()
        
        # Count actual files created
        image_files = list(scraper.images_dir.glob('*'))
        
        print(f"\n🎯 FINAL DIVERSITY TEST RESULTS:")
        print("=" * 50)
        print(f"✅ Unique image files created: {len(image_files)}")
        print(f"✅ Different image hashes: {len(scraper.image_hashes)}")
        print(f"✅ Buildings with images: {sum(1 for images in results.values() if images)}")
        
        if len(image_files) > len(scraper.image_hashes):
            print("⚠️ Warning: More files than unique hashes (possible issue)")
        elif len(image_files) == len(scraper.image_hashes):
            print("🎉 Perfect: All images are unique!")
        
        # Show sample filenames for verification
        print(f"\n📂 Sample diverse images created:")
        for i, img_file in enumerate(image_files[:8]):
            size_mb = img_file.stat().st_size / 1024 / 1024
            print(f"   {i+1}. {img_file.name} ({size_mb:.2f} MB)")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        await scraper.close_session()

if __name__ == "__main__":
    asyncio.run(main())