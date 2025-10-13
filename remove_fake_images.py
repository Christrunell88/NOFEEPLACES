#!/usr/bin/env python3
"""
Remove Generated/Stock Images - Keep Only Real Scraped Data
Deletes apartments with Unsplash, generic stock photos, or AI-generated images
Preserves only apartments with real scraped images from actual building websites
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

# Real/legitimate image sources (actual building websites)
REAL_IMAGE_SOURCES = [
    'nestiostatic.com',          # Nestio real estate platform
    'mercedeshouseny.com',       # Mercedes House building
    'tfc.com',                    # TF Cornerstone (real estate)
    'twotreesny.com',            # Two Trees Management
    'manhattanskyline.com',      # Manhattan Skyline buildings
    'assets-img.nestiostatic',   # Nestio CDN
    '/uploads/diverse_scraped',  # Our locally scraped images
]

# Fake/generated image sources to remove
FAKE_IMAGE_SOURCES = [
    'unsplash.com',              # Stock photos
    'pexels.com',                # Stock photos
    'pixabay.com',               # Stock photos
    'freepik.com',               # Stock photos
    'shutterstock.com',          # Stock photos
    'generated',                 # AI generated
    'placeholder',               # Placeholder images
]


async def analyze_image_sources():
    """Analyze all image sources in the database"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n" + "="*70)
    print("🔍 ANALYZING IMAGE SOURCES")
    print("="*70)
    
    apartments = await db.apartments.find({}).to_list(length=None)
    
    print(f"\nTotal apartments: {len(apartments)}")
    
    # Categorize by image source
    real_scraped = []
    fake_generated = []
    no_images = []
    
    for apt in apartments:
        images = apt.get('images', [])
        
        if not images:
            no_images.append(apt)
            continue
        
        # Check if any image is from a real source
        has_real_images = False
        has_fake_images = False
        
        for img in images:
            img_str = str(img).lower()
            
            # Check for real sources
            if any(source in img_str for source in REAL_IMAGE_SOURCES):
                has_real_images = True
            
            # Check for fake sources
            if any(source in img_str for source in FAKE_IMAGE_SOURCES):
                has_fake_images = True
        
        if has_real_images:
            real_scraped.append(apt)
        elif has_fake_images:
            fake_generated.append(apt)
        else:
            # Unknown source - treat as generated
            fake_generated.append(apt)
    
    print(f"\n📊 Breakdown:")
    print(f"   ✅ Real Scraped Images: {len(real_scraped)} apartments")
    print(f"   ❌ Fake/Generated Images: {len(fake_generated)} apartments")
    print(f"   ⚠️  No Images: {len(no_images)} apartments")
    
    # Show sample fake apartments
    print(f"\n❌ Apartments to DELETE (fake/generated images):")
    for apt in fake_generated[:10]:
        title = apt.get('title', 'N/A')[:60]
        images = apt.get('images', [])
        sample_img = images[0][:80] if images else 'N/A'
        print(f"   • {title}")
        print(f"     Sample image: {sample_img}...")
    
    if len(fake_generated) > 10:
        print(f"   ... and {len(fake_generated) - 10} more")
    
    # Show sample real apartments
    print(f"\n✅ Apartments to KEEP (real scraped images):")
    for apt in real_scraped[:10]:
        title = apt.get('title', 'N/A')[:60]
        images = apt.get('images', [])
        img_count = len(images)
        sample_img = images[0][:80] if images else 'N/A'
        print(f"   • {title}")
        print(f"     {img_count} images - Sample: {sample_img}...")
    
    if len(real_scraped) > 10:
        print(f"   ... and {len(real_scraped) - 10} more")
    
    client.close()
    
    return {
        'real_scraped': real_scraped,
        'fake_generated': fake_generated,
        'no_images': no_images
    }


async def remove_fake_images():
    """Remove apartments with fake/generated images"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n" + "="*70)
    print("🗑️  REMOVING FAKE/GENERATED IMAGE APARTMENTS")
    print("="*70)
    
    apartments = await db.apartments.find({}).to_list(length=None)
    
    ids_to_delete = []
    
    for apt in apartments:
        images = apt.get('images', [])
        
        if not images:
            # Remove apartments with no images
            ids_to_delete.append(apt['id'])
            continue
        
        # Check if ALL images are from real sources
        has_only_real_images = True
        
        for img in images:
            img_str = str(img).lower()
            
            # Check if image is fake
            if any(source in img_str for source in FAKE_IMAGE_SOURCES):
                has_only_real_images = False
                break
            
            # If not from known real source, treat as fake
            if not any(source in img_str for source in REAL_IMAGE_SOURCES):
                has_only_real_images = False
                break
        
        if not has_only_real_images:
            ids_to_delete.append(apt['id'])
    
    print(f"\n🗑️  Deleting {len(ids_to_delete)} apartments with fake/generated images...")
    
    if ids_to_delete:
        result = await db.apartments.delete_many({'id': {'$in': ids_to_delete}})
        print(f"   ✅ Deleted {result.deleted_count} apartments")
    else:
        print(f"   ℹ️  No apartments to delete")
    
    # Count remaining
    remaining = await db.apartments.count_documents({})
    print(f"\n✅ Remaining apartments with REAL images: {remaining}")
    
    # Show what's left
    remaining_apts = await db.apartments.find({}).to_list(length=None)
    
    if remaining_apts:
        print(f"\n📋 Remaining Apartments (Real Scraped Data Only):")
        
        # Group by building
        buildings = {}
        for apt in remaining_apts:
            addr = apt.get('building_address', apt.get('address', 'Unknown'))
            if addr not in buildings:
                buildings[addr] = []
            buildings[addr].append(apt)
        
        for building, units in buildings.items():
            total_images = sum(len(u.get('images', [])) for u in units)
            print(f"\n   🏢 {building}")
            print(f"      Units: {len(units)}")
            print(f"      Total Images: {total_images}")
            
            for unit in units[:3]:
                print(f"      • {unit.get('title', 'N/A')[:50]} - {len(unit.get('images', []))} images")
    
    client.close()
    
    return remaining


async def main():
    """Main execution"""
    print("🚀 Starting Fake Image Removal Process")
    
    # First, analyze what we have
    analysis = await analyze_image_sources()
    
    print("\n" + "="*70)
    print("⚠️  CONFIRMATION REQUIRED")
    print("="*70)
    print(f"\nThis will DELETE {len(analysis['fake_generated']) + len(analysis['no_images'])} apartments")
    print(f"and KEEP {len(analysis['real_scraped'])} apartments with real scraped images.")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        return
    
    # Remove fake images
    remaining = await remove_fake_images()
    
    print("\n" + "="*70)
    print("✅ CLEANUP COMPLETE")
    print("="*70)
    print(f"   All fake/generated images removed")
    print(f"   Only REAL scraped apartment data remains")
    print(f"   Total apartments: {remaining}")


if __name__ == "__main__":
    asyncio.run(main())
