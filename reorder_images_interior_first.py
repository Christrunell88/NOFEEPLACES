#!/usr/bin/env python3
"""
Reorder Images - Living Room/Kitchen First
Move amenity and outdoor images to the end
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import re

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')


def classify_image(image_url: str, image_index: int) -> tuple:
    """
    Classify image type based on URL patterns and index
    Returns (priority, description)
    Lower priority number = shows first
    """
    url_lower = image_url.lower()
    
    # Priority 1: Living room, kitchen (interior spaces)
    if any(x in url_lower for x in ['living', 'kitchen', 'interior', 'room', 'dining']):
        if 'living' in url_lower:
            return (1, 'Living Room')
        elif 'kitchen' in url_lower:
            return (1, 'Kitchen')
        else:
            return (1, 'Interior')
    
    # Priority 2: Bedroom, bathroom
    if any(x in url_lower for x in ['bedroom', 'bed_room', 'bath']):
        return (2, 'Bedroom/Bath')
    
    # Priority 3: Building exterior, entrance
    if any(x in url_lower for x in ['exterior', 'building', 'entrance', 'lobby']):
        return (3, 'Building')
    
    # Priority 4: Amenities (gym, pool, lounge, etc)
    if any(x in url_lower for x in ['amenity', 'amenities', 'gym', 'fitness', 'pool', 'lounge', 'rooftop', 'roof', 'courtyard', 'garden']):
        return (4, 'Amenities')
    
    # Priority 5: Outdoor/terrace
    if any(x in url_lower for x in ['terrace', 'outdoor', 'patio', 'balcony', 'deck', 'view']):
        return (5, 'Outdoor/Terrace')
    
    # Priority 6: Other/unknown - but prefer earlier images in the list
    # Earlier scraped images are usually more important
    if image_index < 3:
        return (1.5, 'Early Image (likely interior)')
    else:
        return (6, 'Other')


async def reorder_all_apartment_images():
    """Reorder images for all apartments"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n" + "="*70)
    print("🖼️  REORDERING IMAGES - LIVING ROOM/KITCHEN FIRST")
    print("="*70)
    
    apartments = await db.apartments.find({}).to_list(length=None)
    
    updated_count = 0
    
    for apt in apartments:
        images = apt.get('images', [])
        
        if not images:
            continue
        
        # Classify each image
        classified_images = []
        for idx, img in enumerate(images):
            priority, description = classify_image(img, idx)
            classified_images.append({
                'url': img,
                'priority': priority,
                'description': description
            })
        
        # Sort by priority (lower number = shows first)
        sorted_images = sorted(classified_images, key=lambda x: x['priority'])
        
        # Extract just the URLs in new order
        reordered_urls = [img['url'] for img in sorted_images]
        
        # Check if order changed
        if reordered_urls != images:
            # Update database
            await db.apartments.update_one(
                {'id': apt['id']},
                {'$set': {'images': reordered_urls}}
            )
            
            updated_count += 1
            
            print(f"\n✓ {apt.get('title', 'N/A')[:50]}")
            print(f"  Building: {apt.get('building_address', 'N/A')[:40]}")
            print(f"  Old first image: {classified_images[0]['description']}")
            print(f"  New first image: {sorted_images[0]['description']}")
            print(f"  Reordered: {len(images)} images")
    
    print(f"\n✅ Reordered images for {updated_count} apartments")
    
    # Verify results
    print("\n" + "="*70)
    print("🔍 VERIFICATION - First Image Per Apartment")
    print("="*70)
    
    all_apts = await db.apartments.find({}).to_list(length=None)
    
    for apt in all_apts:
        images = apt.get('images', [])
        if images:
            first_img = images[0]
            priority, description = classify_image(first_img, 0)
            
            status = "✅" if priority <= 2 else "⚠️"
            print(f"\n{status} {apt.get('title', 'N/A')[:45]}")
            print(f"   First image: {description}")
            print(f"   URL: {first_img[:70]}...")
    
    client.close()


async def main():
    """Main execution"""
    print("🚀 Reordering apartment images")
    await reorder_all_apartment_images()
    print("\n✅ Complete - Living room/kitchen images now first")


if __name__ == "__main__":
    asyncio.run(main())
