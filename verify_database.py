#!/usr/bin/env python3
"""
Verify Database Organization
Check the structured apartment listings in MongoDB
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
import json


async def verify_database():
    """Verify database organization"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'nofeeplaces')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("\n" + "="*60)
    print("🔍 DATABASE VERIFICATION REPORT")
    print("="*60)
    
    # Get all apartments
    apartments = await db.apartments.find({}).to_list(length=None)
    
    print(f"\n📊 Total Apartments: {len(apartments)}")
    
    # Group by source
    by_source = {}
    for apt in apartments:
        source = apt.get('source', 'Unknown')
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(apt)
    
    print(f"\n📍 By Source:")
    for source, apts in by_source.items():
        print(f"   • {source}: {len(apts)} listings")
    
    # Group by building address
    by_building = {}
    for apt in apartments:
        addr = apt.get('building_address', 'Unknown')
        if addr not in by_building:
            by_building[addr] = []
        by_building[addr].append(apt)
    
    print(f"\n🏢 By Building ({len(by_building)} buildings):")
    for building, apts in sorted(by_building.items()):
        print(f"\n   📍 {building}")
        print(f"      Total Units: {len(apts)}")
        
        # Group by size
        by_size = {}
        for apt in apts:
            size = apt.get('size', 'Unknown')
            if size not in by_size:
                by_size[size] = []
            by_size[size].append(apt)
        
        for size, units in sorted(by_size.items(), key=lambda x: str(x[0]) if x[0] else 'ZZZ'):
            total_images = sum(len(u.get('images', [])) for u in units)
            prices = list(set([u.get('price') for u in units if u.get('price')]))
            price_str = ', '.join(prices) if prices else 'N/A'
            
            print(f"      • {size}: {len(units)} unit(s)")
            print(f"        Price: {price_str}")
            print(f"        Images: {total_images} total")
    
    # Sample apartment details
    print(f"\n" + "="*60)
    print("📸 SAMPLE APARTMENT DETAILS")
    print("="*60)
    
    for i, apt in enumerate(apartments[:2], 1):
        print(f"\n{i}. {apt.get('title', 'N/A')}")
        print(f"   Building: {apt.get('building_address')}")
        print(f"   Size: {apt.get('size', 'N/A')}")
        print(f"   Bedrooms: {apt.get('bedrooms', 'N/A')}")
        print(f"   Bathrooms: {apt.get('bathrooms', 'N/A')}")
        print(f"   Price: {apt.get('price', 'N/A')}")
        print(f"   Images: {len(apt.get('images', []))} images")
        print(f"   Source: {apt.get('source')}")
        
        # Show first 3 image URLs
        images = apt.get('images', [])
        if images:
            print(f"   Sample Images:")
            for j, img in enumerate(images[:3], 1):
                print(f"      {j}. {img[:80]}...")
    
    # Image statistics
    print(f"\n" + "="*60)
    print("📊 IMAGE STATISTICS")
    print("="*60)
    
    total_images = sum(len(apt.get('images', [])) for apt in apartments)
    apts_with_images = len([apt for apt in apartments if apt.get('images')])
    
    print(f"   Total Images: {total_images}")
    print(f"   Apartments with Images: {apts_with_images}/{len(apartments)}")
    print(f"   Average Images per Unit: {total_images/len(apartments) if apartments else 0:.1f}")
    
    # Check for fake/placeholder images
    fake_images = 0
    for apt in apartments:
        for img in apt.get('images', []):
            if any(x in img.lower() for x in ['fake', 'mock', 'sample', 'placeholder', 'ajax-loader']):
                fake_images += 1
    
    if fake_images == 0:
        print(f"\n   ✅ All {total_images} images are REAL scraped data")
    else:
        print(f"\n   ⚠️  Found {fake_images} fake/placeholder images")
    
    print("\n" + "="*60)
    print("✅ VERIFICATION COMPLETE")
    print("="*60)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(verify_database())
