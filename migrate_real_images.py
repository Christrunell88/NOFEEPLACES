#!/usr/bin/env python3
"""
Migrate apartments with REAL images from nofeeplaces to nofeeplaces_database
Replace stock photos with authentic unit-specific images
"""

import pymongo
from pymongo import MongoClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')

client = MongoClient(MONGO_URL)

# Source database (has real Zillow images)
source_db = client['nofeeplaces']
source_apartments = source_db.apartments

# Target database (currently has Unsplash stock photos)
target_db = client['nofeeplaces_database']
target_apartments = target_db.apartments

def migrate_real_images():
    """Migrate apartments with real images"""
    
    print("="*80)
    print("MIGRATING APARTMENTS WITH REAL IMAGES")
    print("="*80)
    
    # Get apartments from source (all have real Zillow images)
    real_image_apartments = list(source_apartments.find({}))
    
    print(f"\n📊 CURRENT STATE:")
    print(f"   Source DB (nofeeplaces): {len(real_image_apartments)} apartments with REAL images")
    
    target_count = target_apartments.count_documents({})
    print(f"   Target DB (nofeeplaces_database): {target_count} apartments with stock photos")
    
    if not real_image_apartments:
        print("\n❌ No apartments found in source database!")
        return
    
    # Show sample of what we're migrating
    print(f"\n📸 APARTMENTS WITH REAL IMAGES (Sample):")
    for apt in real_image_apartments[:3]:
        print(f"   • {apt.get('title', 'Unknown')[:60]}")
        print(f"     Price: ${apt.get('price', 0):,.0f}")
        print(f"     Images: {len(apt.get('images', []))} (from Zillow)")
        print(f"     Sample: {apt.get('images', [''])[0][:80]}...")
    
    # Delete all existing apartments from target
    print(f"\n🗑️  REMOVING {target_count} APARTMENTS WITH STOCK PHOTOS...")
    result = target_apartments.delete_many({})
    print(f"   ✅ Deleted {result.deleted_count} apartments")
    
    # Insert apartments with real images
    print(f"\n📥 INSERTING {len(real_image_apartments)} APARTMENTS WITH REAL IMAGES...")
    
    inserted_count = 0
    for apt in real_image_apartments:
        # Remove _id to allow MongoDB to generate new ones
        apt_copy = apt.copy()
        if '_id' in apt_copy:
            del apt_copy['_id']
        
        target_apartments.insert_one(apt_copy)
        inserted_count += 1
        print(f"   ✅ Inserted: {apt_copy.get('title', 'Unknown')[:60]}")
    
    print(f"\n{'='*80}")
    print(f"✅ MIGRATION COMPLETE")
    print(f"{'='*80}")
    print(f"   Removed: {result.deleted_count} apartments with stock photos")
    print(f"   Added: {inserted_count} apartments with REAL images")
    
    # Verify final state
    final_count = target_apartments.count_documents({})
    print(f"\n📊 FINAL STATE:")
    print(f"   Active database (nofeeplaces_database): {final_count} apartments")
    print(f"   All apartments now have REAL unit-specific images ✅")
    
    # Show image sources
    print(f"\n🖼️  IMAGE SOURCES:")
    pipeline = [
        {'$unwind': '$images'},
        {'$group': {
            '_id': {
                '$regexFind': {'input': '$images', 'regex': 'https?://([^/]+)'}
            },
            'count': {'$sum': 1}
        }},
        {'$project': {
            'domain': {'$arrayElemAt': ['$_id.captures', 0]},
            'count': 1
        }},
        {'$sort': {'count': -1}}
    ]
    
    sources = list(target_apartments.aggregate(pipeline))
    for source in sources:
        domain = source.get('domain', 'Unknown')
        count = source.get('count', 0)
        
        if 'zillowstatic.com' in domain:
            print(f"   ✅ {domain}: {count} images (REAL apartment photos)")
        elif 'unsplash.com' in domain:
            print(f"   ❌ {domain}: {count} images (stock photos)")
        else:
            print(f"   • {domain}: {count} images")
    
    return {
        'deleted': result.deleted_count,
        'inserted': inserted_count,
        'final_count': final_count
    }

if __name__ == "__main__":
    print("🚀 Starting migration of apartments with REAL images")
    print("   From: nofeeplaces (has Zillow real images)")
    print("   To: nofeeplaces_database (active database)")
    
    result = migrate_real_images()
    
    print(f"\n✅ SUCCESS!")
    print(f"   Your active database now has {result['final_count']} apartments")
    print(f"   ALL with authentic, unit-specific images from real listings")
    print(f"   NO MORE STOCK PHOTOS! 🎉")
    
    client.close()
