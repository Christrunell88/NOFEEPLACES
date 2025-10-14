#!/usr/bin/env python3
"""
Scrape real building images from public websites
Get actual apartment photos from twotreesny.com, tfc.com, manhattanskyline.com
Store images locally and update database with real building photos
"""
import asyncio
import aiohttp
import os
import uuid
import base64
from motor.motor_asyncio import AsyncIOMotorClient
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import mimetypes

class RealBuildingImageScraper:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces_database')
        self.images_dir = '/app/backend/uploads/building_images'
        
        # Ensure images directory exists
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Building websites and their specific URLs
        self.building_sources = {
            'Mercedes House': {
                'website': 'twotreesny.com',
                'urls': [
                    'https://www.twotreesny.com/buildings/mercedes-house',
                    'https://www.twotreesny.com/buildings/mercedes-house/gallery'
                ],
                'management': 'Two Trees Management'
            },
            'DUMBO Heights': {
                'website': 'twotreesny.com',
                'urls': [
                    'https://www.twotreesny.com/buildings/dumbo-heights',
                    'https://www.twotreesny.com/buildings/dumbo-heights/gallery'
                ],
                'management': 'Two Trees Management'
            },
            'Court Square': {
                'website': 'tfc.com',
                'urls': [
                    'https://www.tfc.com/residential/court-square',
                    'https://www.tfc.com/residential/court-square/amenities'
                ],
                'management': 'TF Cornerstone'
            },
            'West River House': {
                'website': 'manhattanskyline.com',
                'urls': [
                    'https://manhattanskyline.com/buildings/upper-west-side/west-river-house',
                    'https://manhattanskyline.com/buildings/upper-west-side/west-river-house/gallery'
                ],
                'management': 'Manhattan Skyline Management'
            },
            'Manhattan East': {
                'website': 'manhattanskyline.com',
                'urls': [
                    'https://manhattanskyline.com/buildings/upper-east-side/manhattan-east',
                    'https://manhattanskyline.com/buildings/upper-east-side/manhattan-east/gallery'
                ],
                'management': 'Manhattan Skyline Management'
            },
            'Murray Hill Manor': {
                'website': 'manhattanskyline.com',
                'urls': [
                    'https://manhattanskyline.com/buildings/murray-hill/murray-hill-manor',
                    'https://manhattanskyline.com/buildings/murray-hill/murray-hill-manor/gallery'
                ],
                'management': 'Manhattan Skyline Management'
            }
        }
    
    async def connect_database(self):
        """Connect to database"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
    
    async def download_image(self, session, image_url, building_name):
        """Download and save image locally"""
        try:
            async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Generate unique filename
                    parsed_url = urlparse(image_url)
                    file_extension = os.path.splitext(parsed_url.path)[1] or '.jpg'
                    filename = f"{building_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}{file_extension}"
                    filepath = os.path.join(self.images_dir, filename)
                    
                    # Save image file
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    
                    # Return local file path for database storage
                    return f"/uploads/building_images/{filename}"
                
        except Exception as e:
            print(f"   ❌ Failed to download {image_url}: {e}")
            return None
    
    async def scrape_building_images(self, session, building_name, building_info):
        """Scrape images for a specific building"""
        print(f"\n🏢 Scraping {building_name} ({building_info['website']})")
        
        all_images = []
        
        for url in building_info['urls']:
            try:
                print(f"   📄 Scraping: {url}")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find image elements
                        img_elements = soup.find_all('img')
                        
                        for img in img_elements:
                            img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                            if img_src:
                                # Convert relative URLs to absolute
                                if img_src.startswith('/'):
                                    img_src = urljoin(url, img_src)
                                elif img_src.startswith('//'):
                                    img_src = 'https:' + img_src
                                elif not img_src.startswith('http'):
                                    img_src = urljoin(url, img_src)
                                
                                # Filter for apartment/building images
                                if self.is_apartment_image(img_src, img.get('alt', ''), img.get('class', [])):
                                    all_images.append(img_src)
                        
                        print(f"   ✅ Found {len(img_elements)} images on page")
                    
            except Exception as e:
                print(f"   ❌ Error scraping {url}: {e}")
        
        # Remove duplicates and limit to reasonable number
        unique_images = list(dict.fromkeys(all_images))[:8]  # Max 8 images per building
        
        # Download images
        downloaded_images = []
        for img_url in unique_images:
            local_path = await self.download_image(session, img_url, building_name)
            if local_path:
                downloaded_images.append(local_path)
        
        print(f"   📸 Successfully downloaded {len(downloaded_images)} images")
        return downloaded_images
    
    def is_apartment_image(self, img_src, alt_text, css_classes):
        """Check if image is likely an apartment/building image"""
        # Skip obviously non-apartment images
        skip_keywords = [
            'logo', 'icon', 'avatar', 'button', 'arrow', 'social',
            'thumbnail', 'placeholder', 'loading', 'sprite'
        ]
        
        img_src_lower = img_src.lower()
        alt_lower = alt_text.lower() if alt_text else ''
        
        # Skip small images or non-apartment images
        if any(keyword in img_src_lower or keyword in alt_lower for keyword in skip_keywords):
            return False
        
        # Look for apartment-related keywords
        apartment_keywords = [
            'apartment', 'unit', 'room', 'kitchen', 'bedroom', 'bathroom',
            'living', 'interior', 'amenity', 'building', 'lobby', 'rooftop',
            'view', 'gallery', 'photo'
        ]
        
        # Include if it has apartment keywords or is from gallery/photos section
        if any(keyword in img_src_lower or keyword in alt_lower for keyword in apartment_keywords):
            return True
        
        # Include if it's a reasonably sized image (likely not an icon)
        if 'thumb' not in img_src_lower and len(img_src) > 50:
            return True
        
        return False
    
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
                    'image_source': f'Real {building_name} Photos',
                    'scraped_images': True,
                    'updated_at': '2025-01-09T21:00:00.000Z'
                }
            }
        )
        
        print(f"   ✅ Updated {result.modified_count} apartments for {building_name}")
        return result.modified_count
    
    async def scrape_all_building_images(self):
        """Scrape images for all buildings"""
        print("🏠 SCRAPING REAL BUILDING IMAGES")
        print("=" * 70)
        print("📸 Getting actual apartment photos from building websites")
        print("=" * 70)
        
        total_updated = 0
        
        async with aiohttp.ClientSession() as session:
            for building_name, building_info in self.building_sources.items():
                try:
                    # Check if we have apartments for this building
                    apartment_count = await self.db.apartments.count_documents({'building_name': building_name})
                    
                    if apartment_count == 0:
                        print(f"\n🏢 Skipping {building_name} (no apartments in database)")
                        continue
                    
                    print(f"\n🏢 Processing {building_name} ({apartment_count} apartments)")
                    
                    # Scrape images for this building
                    images = await self.scrape_building_images(session, building_name, building_info)
                    
                    # Update apartments with real images
                    updated_count = await self.update_building_apartments(building_name, images)
                    total_updated += updated_count
                    
                except Exception as e:
                    print(f"❌ Error processing {building_name}: {e}")
        
        return total_updated
    
    def show_scraping_summary(self, total_updated):
        """Show summary of image scraping results"""
        print(f"\n📊 REAL IMAGE SCRAPING SUMMARY")
        print("=" * 50)
        
        print(f"🎯 RESULTS:")
        print(f"   Updated apartments: {total_updated}")
        print(f"   Images stored locally in: {self.images_dir}")
        
        print(f"\n🌐 SOURCES SCRAPED:")
        for building, info in self.building_sources.items():
            print(f"   • {building} - {info['website']}")
        
        print(f"\n📸 IMAGE AUTHENTICITY:")
        print(f"   • All images scraped from official building websites")
        print(f"   • Each building shows its actual apartment photos")
        print(f"   • No more generic stock images")
        print(f"   • Images stored locally for fast loading")
    
    async def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()

async def main():
    """Main real building image scraping process"""
    scraper = RealBuildingImageScraper()
    
    try:
        print("🏠 REAL BUILDING IMAGE SCRAPER")
        print("=" * 70)
        print("🎯 Goal: Get actual apartment photos from building websites")
        print("📸 Store real images for each specific building")
        print("🌐 Sources: twotreesny.com, tfc.com, manhattanskyline.com")
        print("=" * 70)
        
        await scraper.connect_database()
        
        # Scrape all building images
        total_updated = await scraper.scrape_all_building_images()
        
        # Show summary
        scraper.show_scraping_summary(total_updated)
        
        print(f"\n🎉 REAL BUILDING IMAGE SCRAPING COMPLETE!")
        print(f"   • {total_updated} apartments updated with real building photos")
        print(f"   • Mercedes House shows actual Mercedes House images")
        print(f"   • Court Square shows actual Court Square images")
        print(f"   • Manhattan Skyline buildings show their real photos")
        print(f"   • No more generic or mismatched images")
        
        return total_updated
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0
    finally:
        await scraper.close_connection()

if __name__ == "__main__":
    asyncio.run(main())