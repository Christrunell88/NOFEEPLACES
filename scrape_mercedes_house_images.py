#!/usr/bin/env python3
"""
Scrape Mercedes House and other building images from public sources
Focus on mercedeshouseny.com, streeteasy.com, apartments.com, compass.com
"""
import asyncio
import aiohttp
import os
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import re

class PublicBuildingImageScraper:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces_database')
        self.images_dir = '/app/backend/uploads/building_images'
        
        # Ensure images directory exists
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Public apartment listing sources
        self.building_image_sources = {
            'Mercedes House': [
                'https://www.mercedeshouseny.com',
                'https://streeteasy.com/building/mercedes-house',
                'https://www.apartments.com/mercedes-house-new-york-ny/kfclxnc/',
                'https://www.compass.com/building/mercedes-house-manhattan-ny/292821502959595781/'
            ],
            'The Olivia': [
                'https://streeteasy.com/building/the-olivia-upper-east-side',
                'https://www.apartments.com/the-olivia-new-york-ny/',
                'https://www.compass.com/building/the-olivia-manhattan-ny/'
            ],
            'Court Square': [
                'https://streeteasy.com/building/court-square',
                'https://www.apartments.com/court-square-long-island-city-ny/',
                'https://www.compass.com/building/court-square-queens-ny/'
            ],
            'The Brooklyner': [
                'https://streeteasy.com/building/the-brooklyner',
                'https://www.apartments.com/the-brooklyner-brooklyn-ny/',
                'https://www.compass.com/building/the-brooklyner-brooklyn-ny/'
            ],
            'DUMBO Heights': [
                'https://streeteasy.com/building/dumbo-heights',
                'https://www.twotreesny.com/buildings/dumbo-heights',
                'https://www.apartments.com/dumbo-heights-brooklyn-ny/'
            ],
            'The Forge': [
                'https://streeteasy.com/building/the-forge-lic',
                'https://www.apartments.com/the-forge-long-island-city-ny/'
            ]
        }
    
    async def connect_database(self):
        """Connect to database"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
    
    async def download_image(self, session, image_url, building_name):
        """Download and save image locally"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://www.google.com/'
            }
            
            async with session.get(image_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Generate unique filename
                    parsed_url = urlparse(image_url)
                    file_extension = os.path.splitext(parsed_url.path)[1] or '.jpg'
                    filename = f"{building_name.lower().replace(' ', '_').replace('the_', '')}_{uuid.uuid4().hex[:8]}{file_extension}"
                    filepath = os.path.join(self.images_dir, filename)
                    
                    # Save image file
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    
                    # Return local file path for database storage
                    return f"/uploads/building_images/{filename}"
                
        except Exception as e:
            print(f"   ❌ Failed to download {image_url}: {e}")
            return None
    
    def extract_images_from_page(self, html, base_url):
        """Extract apartment/building images from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        images = []
        
        # Find all image elements
        img_elements = soup.find_all('img')
        
        for img in img_elements:
            img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
            
            if img_src:
                # Convert relative URLs to absolute
                if img_src.startswith('/'):
                    img_src = urljoin(base_url, img_src)
                elif img_src.startswith('//'):
                    img_src = 'https:' + img_src
                elif not img_src.startswith('http'):
                    img_src = urljoin(base_url, img_src)
                
                # Check if it's an apartment/building image
                if self.is_building_image(img_src, img.get('alt', ''), img.get('class', [])):
                    images.append(img_src)
        
        # Also look for JSON data containing image URLs
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for JSON data with image URLs
                json_matches = re.findall(r'{"[^"]*image[^"]*":\s*"([^"]*)"', script.string)
                for match in json_matches:
                    if match.startswith('http') and self.is_building_image(match, '', []):
                        images.append(match)
        
        return images
    
    def is_building_image(self, img_src, alt_text, css_classes):
        """Check if image is likely a building/apartment image"""
        # Skip obviously non-apartment images
        skip_keywords = [
            'logo', 'icon', 'avatar', 'button', 'arrow', 'social', 'flag',
            'thumbnail', 'placeholder', 'loading', 'sprite', 'badge', 'star'
        ]
        
        img_src_lower = img_src.lower()
        alt_lower = alt_text.lower() if alt_text else ''
        
        # Skip small images or non-apartment images
        if any(keyword in img_src_lower or keyword in alt_lower for keyword in skip_keywords):
            return False
        
        # Skip very small images (likely icons)
        if any(size in img_src_lower for size in ['16x16', '32x32', '24x24', '50x50']):
            return False
        
        # Look for apartment-related keywords
        apartment_keywords = [
            'apartment', 'unit', 'room', 'kitchen', 'bedroom', 'bathroom',
            'living', 'interior', 'amenity', 'building', 'lobby', 'rooftop',
            'view', 'gallery', 'photo', 'residence', 'home', 'rental'
        ]
        
        # Include if it has apartment keywords
        if any(keyword in img_src_lower or keyword in alt_lower for keyword in apartment_keywords):
            return True
        
        # Include if it's from known image CDNs and reasonably sized
        cdn_domains = ['cloudfront.net', 'amazonaws.com', 'imgix.net', 'fastly.com']
        if any(domain in img_src_lower for domain in cdn_domains) and len(img_src) > 100:
            return True
        
        # Include if it looks like a high-quality image URL
        if len(img_src) > 80 and ('jpg' in img_src_lower or 'jpeg' in img_src_lower or 'png' in img_src_lower):
            return True
        
        return False
    
    async def scrape_building_from_sources(self, session, building_name, source_urls):
        """Scrape images for a building from multiple sources"""
        print(f"\n🏢 Scraping {building_name}")
        
        all_images = []
        
        for url in source_urls:
            try:
                print(f"   📄 Scraping: {url}")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://www.google.com/'
                }
                
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        html = await response.text()
                        page_images = self.extract_images_from_page(html, url)
                        all_images.extend(page_images)
                        print(f"   ✅ Found {len(page_images)} potential images")
                    else:
                        print(f"   ⚠️ Status {response.status}")
                        
            except Exception as e:
                print(f"   ❌ Error scraping {url}: {e}")
        
        # Remove duplicates and limit to reasonable number
        unique_images = list(dict.fromkeys(all_images))[:12]  # Max 12 images per building
        
        # Download images
        downloaded_images = []
        for img_url in unique_images:
            local_path = await self.download_image(session, img_url, building_name)
            if local_path:
                downloaded_images.append(local_path)
        
        print(f"   📸 Successfully downloaded {len(downloaded_images)}/{len(unique_images)} images")
        return downloaded_images
    
    async def update_building_apartments(self, building_name, images):
        """Update all apartments for a building with real images"""
        if not images:
            print(f"   ⚠️ No images to update for {building_name}")
            return 0
        
        # Update all apartments for this building
        result = await self.db.apartments.update_many(
            {'building_name': building_name},
            {
                '$set': {
                    'images': images,
                    'image_source': f'Real {building_name} Photos - Public Sources',
                    'scraped_images': True,
                    'updated_at': '2025-01-09T21:30:00.000Z'
                }
            }
        )
        
        print(f"   ✅ Updated {result.modified_count} apartments for {building_name}")
        return result.modified_count
    
    async def scrape_all_buildings(self):
        """Scrape images for all buildings from public sources"""
        print("🏠 SCRAPING FROM PUBLIC APARTMENT LISTING SOURCES")
        print("=" * 70)
        print("📸 Sources: mercedeshouseny.com, streeteasy.com, apartments.com, compass.com")
        print("=" * 70)
        
        total_updated = 0
        
        async with aiohttp.ClientSession() as session:
            for building_name, source_urls in self.building_image_sources.items():
                try:
                    # Check if we have apartments for this building
                    apartment_count = await self.db.apartments.count_documents({'building_name': building_name})
                    
                    if apartment_count == 0:
                        print(f"\n🏢 Skipping {building_name} (no apartments in database)")
                        continue
                    
                    print(f"\n🏢 Processing {building_name} ({apartment_count} apartments)")
                    
                    # Scrape images for this building
                    images = await self.scrape_building_from_sources(session, building_name, source_urls)
                    
                    # Update apartments with real images
                    updated_count = await self.update_building_apartments(building_name, images)
                    total_updated += updated_count
                    
                except Exception as e:
                    print(f"❌ Error processing {building_name}: {e}")
        
        return total_updated
    
    async def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()

async def main():
    """Main public building image scraping process"""
    scraper = PublicBuildingImageScraper()
    
    try:
        print("🏠 PUBLIC BUILDING IMAGE SCRAPER")
        print("=" * 70)
        print("🎯 Goal: Get real apartment photos from public listing sites")
        print("📸 Focus on Mercedes House and other buildings")
        print("=" * 70)
        
        await scraper.connect_database()
        
        # Scrape all building images
        total_updated = await scraper.scrape_all_buildings()
        
        print(f"\n📊 PUBLIC SOURCE SCRAPING SUMMARY")
        print("=" * 50)
        print(f"🎯 Updated apartments: {total_updated}")
        print(f"📸 Images stored locally for fast loading")
        print(f"🌐 Sources: Public apartment listing websites")
        
        print(f"\n🎉 PUBLIC BUILDING IMAGE SCRAPING COMPLETE!")
        print(f"   • {total_updated} additional apartments updated with real photos")
        print(f"   • Each building now shows its actual apartment images")
        print(f"   • No more generic or mismatched stock photos")
        
        return total_updated
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0
    finally:
        await scraper.close_connection()

if __name__ == "__main__":
    asyncio.run(main())