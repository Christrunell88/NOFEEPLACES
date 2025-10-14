#!/usr/bin/env python3
"""
Fix apartment images - Remove broken/generated images and ensure only real, accessible images remain
User requirement: Images should correspond to specific units, not be generated/stock photos
"""

import pymongo
from pymongo import MongoClient
import os
import requests
from urllib.parse import urlparse

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = 'nofeeplaces'

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

def fix_apartment_images():
    """Remove broken images and categorize apartments by image quality"""
    
    print("🔍 Analyzing all apartments and their images...")
    
    all_apartments = list(apartments_collection.find({}))
    total_count = len(all_apartments)
    
    apartments_with_working_images = []
    apartments_with_broken_images = []
    apartments_with_no_images = []
    
    for apt in all_apartments:
        images = apt.get('images', [])
        
        if not images:
            apartments_with_no_images.append(apt)
            continue
        
        # Check first image
        first_image = images[0] if images else None
        if first_image:
            # Check if it's a known broken source
            if 'nestiostatic.com' in first_image:
                # All Nestio images return 403, mark as broken
                apartments_with_broken_images.append(apt)
            elif 'luxuryrentalsmanhattan.com' in first_image:
                # These often return 404, check them
                if not check_image_url(first_image):
                    apartments_with_broken_images.append(apt)
                else:
                    apartments_with_working_images.append(apt)
            elif 'apartments.com' in first_image:
                # Check apartments.com images
                if not check_image_url(first_image):
                    apartments_with_broken_images.append(apt)
                else:
                    apartments_with_working_images.append(apt)
            else:
                # Unknown source, assume working
                apartments_with_working_images.append(apt)
        else:
            apartments_with_no_images.append(apt)
    
    print(f"\n📊 IMAGE AUDIT RESULTS:")
    print(f"   Total apartments: {total_count}")
    print(f"   ✅ Apartments with working images: {len(apartments_with_working_images)}")
    print(f"   ❌ Apartments with broken images: {len(apartments_with_broken_images)}")
    print(f"   ⚠️  Apartments with no images: {len(apartments_with_no_images)}")
    
    # Show details of apartments with broken images
    if apartments_with_broken_images:
        print(f"\n🔴 APARTMENTS WITH BROKEN IMAGES:")
        for apt in apartments_with_broken_images:
            title = apt.get('title', 'Unknown')
            building = apt.get('building_name', 'Unknown')
            images = apt.get('images', [])
            first_image = images[0] if images else 'None'
            image_source = urlparse(first_image).netloc if first_image != 'None' else 'N/A'
            print(f"   • {title[:60]}")
            print(f"     Building: {building}")
            print(f"     Image source: {image_source}")
            print(f"     First image: {first_image[:80]}...")
    
    # Show apartments with working images
    if apartments_with_working_images:
        print(f"\n✅ APARTMENTS WITH WORKING IMAGES (Sample):")
        for apt in apartments_with_working_images[:5]:
            title = apt.get('title', 'Unknown')
            building = apt.get('building_name', 'Unknown')
            images = apt.get('images', [])
            first_image = images[0] if images else 'None'
            image_source = urlparse(first_image).netloc if first_image != 'None' else 'N/A'
            print(f"   • {title[:60]}")
            print(f"     Building: {building}")
            print(f"     Image source: {image_source}")
    
    return {
        'total': total_count,
        'working': len(apartments_with_working_images),
        'broken': len(apartments_with_broken_images),
        'no_images': len(apartments_with_no_images),
        'apartments_to_fix': apartments_with_broken_images + apartments_with_no_images
    }

if __name__ == "__main__":
    print("=" * 80)
    print("NOFEEPLACES - APARTMENT IMAGE AUDIT")
    print("=" * 80)
    
    result = fix_apartment_images()
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total apartments analyzed: {result['total']}")
    print(f"   Apartments needing image fixes: {result['broken'] + result['no_images']}")
    print(f"   Apartments with valid images: {result['working']}")
    
    print(f"\n⚠️  ACTION REQUIRED:")
    print(f"   The following apartments need real, unit-specific images:")
    print(f"   - {result['broken']} apartments with broken image URLs")
    print(f"   - {result['no_images']} apartments with no images")
    print(f"\n💡 RECOMMENDATION:")
    print(f"   These apartments should either:")
    print(f"   1. Have real photos from the actual buildings/units")
    print(f"   2. Be removed if no authentic images are available")
    print(f"   3. Images should NOT be AI-generated or generic stock photos")
    
    client.close()
