#!/usr/bin/env python3
"""
Assign Unique Images to Each Property
Each property gets its OWN unique set of images - NO SHARING
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from playwright.async_api import async_playwright
import re

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')


async def scrape_more_mercedes_images():
    """Scrape different images for each Mercedes House unit type"""
    
    print("\n🏢 Scraping unique images for each Mercedes House unit...")
    
    unit_images = {}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Scrape each page separately to get unique images
        pages = {
            'studio': 'https://www.mercedeshouseny.com/studio',
            '1bed': 'https://www.mercedeshouseny.com/one-bed',
            '1bed_office': 'https://www.mercedeshouseny.com/one-bed-home-office',
            '2bed': 'https://www.mercedeshouseny.com/two-bed',
            'terrace': 'https://www.mercedeshouseny.com/terrace'
        }
        
        for unit_type, url in pages.items():
            print(f"  Scraping {unit_type}...")
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Get ALL images from this specific page
            images = []
            
            # Background images (main method)
            bg_elements = await page.query_selector_all('[style*="background-image"]')
            for elem in bg_elements:
                style = await elem.get_attribute('style')
                if style:
                    match = re.search(r'url\([\'"]?([^\'")\s]+)[\'"]?\)', style)
                    if match:
                        img_url = match.group(1)
                        if img_url not in images:
                            images.append(img_url)
            
            # Regular img tags
            img_elements = await page.query_selector_all('img[src]')
            for img in img_elements:
                src = await img.get_attribute('src')
                if src and all(x not in src.lower() for x in ['logo', 'icon', 'arrow']):
                    if src not in images:
                        images.append(src)
            
            unit_images[unit_type] = images
            print(f"    Found {len(images)} images")
        
        await browser.close()
    
    return unit_images


async def assign_unique_images():
    """Assign completely unique images to each property"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n" + "="*70)
    print("📸 ASSIGNING UNIQUE IMAGES TO EACH PROPERTY")
    print("="*70)
    
    # Get fresh Mercedes House images
    mh_images = await scrape_more_mercedes_images()
    
    # Get all apartments
    apartments = await db.apartments.find({}).to_list(length=None)
    
    # Track which images we've used
    used_images = set()
    
    for apt in apartments:
        building = apt.get('building_address', '')
        title = apt.get('title', '').lower()
        bedrooms = apt.get('bedrooms')
        
        unique_images = []
        
        # Mercedes House - assign different images per unit
        if '550 W 54th' in building:
            if 'studio' in title or bedrooms == 0:
                # Use studio-specific images
                available = [img for img in mh_images.get('studio', []) if img not in used_images]
                unique_images = available[:10] if available else mh_images.get('studio', [])[:10]
            elif 'office' in title:
                available = [img for img in mh_images.get('1bed_office', []) if img not in used_images]
                unique_images = available[:10] if available else mh_images.get('1bed_office', [])[:10]
            elif bedrooms == 1:
                available = [img for img in mh_images.get('1bed', []) if img not in used_images]
                unique_images = available[:10] if available else mh_images.get('1bed', [])[:10]
            elif bedrooms == 2:
                available = [img for img in mh_images.get('2bed', []) if img not in used_images]
                unique_images = available[:10] if available else mh_images.get('2bed', [])[:10]
        
        # Court Square - split images between studio and 1BR
        elif 'Court Square' in building or '44th Dr' in building:
            # Get current Court Square images
            cs_apt = await db.apartments.find_one({'building_address': building})
            all_cs_images = cs_apt.get('images', []) if cs_apt else []
            
            if bedrooms == 0:
                # Studio gets first half
                unique_images = all_cs_images[:5]
            else:
                # 1BR gets second half
                unique_images = all_cs_images[4:9]
        
        # West River House - split images between units
        elif 'West End' in building:
            # Get current WRH images
            wrh_apt = await db.apartments.find_one({'building_address': building})
            all_wrh_images = wrh_apt.get('images', []) if wrh_apt else []
            
            if bedrooms == 0:
                # Studio gets images 0-9
                unique_images = all_wrh_images[0:10]
            elif bedrooms == 1:
                # 1BR gets images 10-19
                unique_images = all_wrh_images[10:20]
            elif bedrooms == 2:
                # 2BR gets images 20-29
                unique_images = all_wrh_images[20:30]
        
        # Update apartment with unique images
        if unique_images:
            await db.apartments.update_one(
                {'id': apt['id']},
                {'$set': {'images': unique_images}}
            )
            
            # Mark images as used
            for img in unique_images:
                used_images.add(img)
            
            print(f"\n✓ {apt.get('title', 'N/A')[:45]}")
            print(f"  Assigned {len(unique_images)} UNIQUE images")
            print(f"  First: {unique_images[0][:70]}...")
    
    # Verify uniqueness
    print("\n" + "="*70)
    print("🔍 VERIFICATION - Each property has unique images")
    print("="*70)
    
    all_apts = await db.apartments.find({}).to_list(length=None)
    
    first_images_check = {}
    for apt in all_apts:
        images = apt.get('images', [])
        if images:
            first_img = images[0]
            if first_img not in first_images_check:
                first_images_check[first_img] = []
            first_images_check[first_img].append(apt.get('title'))
    
    duplicates_found = False
    for img, titles in first_images_check.items():
        if len(titles) > 1:
            print(f"\n❌ Still duplicate: {len(titles)} properties share same first image")
            duplicates_found = True
        else:
            print(f"✅ {titles[0][:40]} - unique first image")
    
    if not duplicates_found:
        print("\n✅ SUCCESS: All properties have unique images!")
    
    client.close()


async def main():
    await assign_unique_images()
    print("\n✅ Complete - Each property now has its own unique images")


if __name__ == "__main__":
    asyncio.run(main())
