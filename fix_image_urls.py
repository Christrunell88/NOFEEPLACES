#!/usr/bin/env python3
"""
Fix Image URLs - Convert Relative Paths to Absolute URLs
Make all image URLs absolute so they load properly in the frontend
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')
BACKEND_URL = "https://fee-free-homes.preview.emergentagent.com"


async def fix_image_urls():
    """Fix all relative image URLs to absolute"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n" + "="*70)
    print("🔧 FIXING IMAGE URLS")
    print("="*70)
    
    apartments = await db.apartments.find({}).to_list(length=None)
    
    print(f"\nTotal apartments: {len(apartments)}")
    
    updated_count = 0
    
    for apt in apartments:
        images = apt.get('images', [])
        updated_images = []
        needs_update = False
        
        for img in images:
            # If relative path, make it absolute
            if img.startswith('/uploads/'):
                updated_images.append(f"{BACKEND_URL}{img}")
                needs_update = True
            elif img.startswith('http://') or img.startswith('https://'):
                # Already absolute
                updated_images.append(img)
            else:
                # Unknown format, try to fix
                if not img.startswith('http'):
                    updated_images.append(f"{BACKEND_URL}/{img.lstrip('/')}")
                    needs_update = True
                else:
                    updated_images.append(img)
        
        if needs_update:
            await db.apartments.update_one(
                {'id': apt['id']},
                {'$set': {'images': updated_images}}
            )
            updated_count += 1
            print(f"  ✓ Updated: {apt.get('title', 'N/A')[:50]}")
    
    print(f"\n✅ Updated {updated_count} apartments")
    
    # Verify
    print("\n" + "="*70)
    print("📸 VERIFICATION - Sample Image URLs")
    print("="*70)
    
    sample_apts = await db.apartments.find({}).limit(3).to_list(length=3)
    
    for i, apt in enumerate(sample_apts, 1):
        print(f"\n{i}. {apt.get('title', 'N/A')[:50]}")
        images = apt.get('images', [])
        for img in images[:2]:
            if img.startswith('http'):
                print(f"   ✅ {img[:80]}...")
            else:
                print(f"   ⚠️  {img[:80]}...")
    
    client.close()
    
    print("\n✅ All image URLs are now absolute")


if __name__ == "__main__":
    asyncio.run(fix_image_urls())
