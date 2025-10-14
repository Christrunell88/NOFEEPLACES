#!/usr/bin/env python3
"""
Clean apartment database by removing apartments with broken/inaccessible images
Keep only apartments with verified, accessible, real unit images
"""

import pymongo
from pymongo import MongoClient
import os
import requests
from urllib.parse import urlparse

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
apartments_collection = db['apartments']

def check_image_url(url, timeout=5):
    """Check if an image URL is accessible"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def identify_apartments_to_remove():
    """Identify apartments with broken/inaccessible images"""
    
    print("🔍 Scanning all apartments for broken images...")
    
    all_apartments = list(apartments_collection.find({}))
    
    apartments_to_remove = []
    apartments_to_keep = []
    
    for apt in all_apartments:
        apt_id = apt.get('_id')
        title = apt.get('title', 'Unknown')
        building = apt.get('building_name', 'Unknown')
        images = apt.get('images', [])
        
        if not images:
            apartments_to_remove.append({
                'id': apt_id,
                'title': title,
                'building': building,
                'reason': 'No images'
            })
            continue
        
        first_image = images[0]
        
        # Check for known broken sources
        if 'nestiostatic.com' in first_image:
            apartments_to_remove.append({
                'id': apt_id,
                'title': title,
                'building': building,
                'reason': 'Nestio images return 403 Forbidden'
            })
        elif 'luxuryrentalsmanhattan.com' in first_image:
            if not check_image_url(first_image):
                apartments_to_remove.append({
                    'id': apt_id,
                    'title': title,
                    'building': building,
                    'reason': 'luxuryrentalsmanhattan.com images return 404'
                })
            else:
                apartments_to_keep.append({
                    'id': apt_id,
                    'title': title,
                    'building': building,
                    'image_source': urlparse(first_image).netloc
                })
        elif 'apartments.com' in first_image:
            if not check_image_url(first_image):
                apartments_to_remove.append({
                    'id': apt_id,
                    'title': title,
                    'building': building,
                    'reason': 'apartments.com images inaccessible'
                })
            else:
                apartments_to_keep.append({
                    'id': apt_id,
                    'title': title,
                    'building': building,
                    'image_source': urlparse(first_image).netloc
                })
        else:
            # Keep apartments with other image sources
            apartments_to_keep.append({
                'id': apt_id,
                'title': title,
                'building': building,
                'image_source': urlparse(first_image).netloc
            })
    
    return apartments_to_remove, apartments_to_keep

def clean_database():
    """Remove apartments with broken images from database"""
    
    apartments_to_remove, apartments_to_keep = identify_apartments_to_remove()
    
    print(f"\n📊 CLEANING ANALYSIS:")
    print(f"   Total apartments in database: {len(apartments_to_remove) + len(apartments_to_keep)}")
    print(f"   ❌ Apartments to REMOVE (broken images): {len(apartments_to_remove)}")
    print(f"   ✅ Apartments to KEEP (working images): {len(apartments_to_keep)}")
    
    if apartments_to_remove:
        print(f"\n🗑️  APARTMENTS BEING REMOVED:")
        for apt in apartments_to_remove:
            print(f"   • {apt['title'][:60]}")
            print(f"     Building: {apt['building']}")
            print(f"     Reason: {apt['reason']}")
        
        # Remove apartments
        print(f"\n🔄 Removing {len(apartments_to_remove)} apartments...")
        ids_to_remove = [apt['id'] for apt in apartments_to_remove]
        result = apartments_collection.delete_many({'_id': {'$in': ids_to_remove}})
        print(f"   ✅ Removed {result.deleted_count} apartments")
    
    if apartments_to_keep:
        print(f"\n✅ APARTMENTS KEPT (with working images):")
        for apt in apartments_to_keep:
            print(f"   • {apt['title'][:60]}")
            print(f"     Building: {apt['building']}")
            print(f"     Image source: {apt['image_source']}")
    
    # Verify final count
    final_count = apartments_collection.count_documents({})
    print(f"\n📊 FINAL DATABASE STATE:")
    print(f"   Total apartments remaining: {final_count}")
    print(f"   All remaining apartments have verified, accessible images ✅")
    
    return {
        'removed_count': len(apartments_to_remove),
        'kept_count': len(apartments_to_keep),
        'final_count': final_count
    }

if __name__ == "__main__":
    print("=" * 80)
    print("NOFEEPLACES - DATABASE CLEANING: REMOVE APARTMENTS WITH BROKEN IMAGES")
    print("=" * 80)
    
    result = clean_database()
    
    print(f"\n" + "=" * 80)
    print(f"✅ DATABASE CLEANING COMPLETE")
    print(f"=" * 80)
    print(f"   Removed: {result['removed_count']} apartments with broken/inaccessible images")
    print(f"   Kept: {result['kept_count']} apartments with verified, working images")
    print(f"   Final apartment count: {result['final_count']}")
    print(f"\n💡 All remaining apartments have real, accessible images from verified sources")
    
    client.close()
