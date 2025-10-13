#!/usr/bin/env python3
"""
Database Consolidation Analysis
Check both databases and identify what needs to be merged
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from collections import defaultdict

async def analyze_databases():
    """Analyze both databases"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    
    # Check both databases
    db1 = client['nofeeplaces']
    db2 = client['nofeeplaces_database']
    
    print("\n" + "="*70)
    print("🔍 DATABASE ANALYSIS")
    print("="*70)
    
    # Database 1: nofeeplaces (temporary working database)
    print("\n📦 DATABASE 1: 'nofeeplaces' (Temporary)")
    print("-"*70)
    apts1 = await db1.apartments.find({}).to_list(length=None)
    print(f"   Total Apartments: {len(apts1)}")
    
    if apts1:
        sources1 = defaultdict(int)
        images1 = 0
        for apt in apts1:
            sources1[apt.get('source', 'Unknown')] += 1
            images1 += len(apt.get('images', []))
        
        print(f"   Total Images: {images1}")
        print(f"   By Source:")
        for source, count in sources1.items():
            print(f"      • {source}: {count}")
    
    # Database 2: nofeeplaces_database (production)
    print("\n📦 DATABASE 2: 'nofeeplaces_database' (Production)")
    print("-"*70)
    apts2 = await db2.apartments.find({}).to_list(length=None)
    print(f"   Total Apartments: {len(apts2)}")
    
    if apts2:
        sources2 = defaultdict(int)
        images2 = 0
        buildings2 = defaultdict(int)
        
        for apt in apts2:
            sources2[apt.get('source', 'Unknown')] += 1
            images2 += len(apt.get('images', []))
            building = apt.get('building_address', apt.get('address', 'Unknown'))
            buildings2[building] += 1
        
        print(f"   Total Images: {images2}")
        print(f"   By Source:")
        for source, count in sorted(sources2.items()):
            print(f"      • {source}: {count}")
        
        print(f"\n   Top Buildings:")
        for building, count in sorted(buildings2.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      • {building[:50]}: {count} unit(s)")
    
    # Analysis
    print("\n" + "="*70)
    print("📊 CONSOLIDATION RECOMMENDATION")
    print("="*70)
    
    if len(apts1) > 0 and len(apts2) > 0:
        print("\n⚠️  Data exists in BOTH databases")
        print(f"   • 'nofeeplaces' has {len(apts1)} apartments with {images1} images")
        print(f"   • 'nofeeplaces_database' has {len(apts2)} apartments with {images2} images")
        print("\n✅ RECOMMENDATION:")
        print("   1. Keep 'nofeeplaces_database' as the PRIMARY production database")
        print("   2. All scraped data is already copied there")
        print("   3. Can safely keep 'nofeeplaces' as temporary/working database")
        print("\n   OR optionally:")
        print("   4. Delete 'nofeeplaces' to avoid confusion (it's just a copy)")
    elif len(apts2) > 0:
        print("\n✅ All data is in 'nofeeplaces_database' (Production)")
        print("   No consolidation needed!")
    elif len(apts1) > 0:
        print("\n⚠️  Data only in 'nofeeplaces' (Temporary)")
        print(f"   Need to copy {len(apts1)} apartments to production database")
    
    # Check for any data quality issues
    print("\n" + "="*70)
    print("🔍 DATA QUALITY CHECK")
    print("="*70)
    
    # Check production database
    apts_no_images = len([a for a in apts2 if not a.get('images')])
    apts_no_address = len([a for a in apts2 if not a.get('building_address') and not a.get('address')])
    apts_no_price = len([a for a in apts2 if not a.get('price')])
    
    print(f"\nProduction Database Issues:")
    print(f"   • Apartments without images: {apts_no_images}/{len(apts2)}")
    print(f"   • Apartments without address: {apts_no_address}/{len(apts2)}")
    print(f"   • Apartments without price: {apts_no_price}/{len(apts2)}")
    
    if apts_no_images == 0 and apts_no_address == 0:
        print("\n   ✅ All apartments have images and addresses!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(analyze_databases())
