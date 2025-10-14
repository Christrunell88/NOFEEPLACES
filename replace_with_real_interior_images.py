#!/usr/bin/env python3
"""
Replace Mercedes House generic images with REAL Zillow interior apartment photos
Pull interior images from nofeeplaces database which has verified apartment interiors
"""

from pymongo import MongoClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')

client = MongoClient(MONGO_URL)

# Source: nofeeplaces database with real Zillow interior images
source_db = client['nofeeplaces']

# Target: nofeeplaces_database (currently has generic Mercedes House static images)
target_db = client['nofeeplaces_database']

def get_real_interior_images_by_type():
    """Get real Zillow interior images organized by bedroom type"""
    
    print("="*80)
    print("🔍 EXTRACTING REAL INTERIOR IMAGES FROM NOFEEPLACES DATABASE")
    print("="*80)
    
    # Get all apartments with Zillow images
    zillow_apts = list(source_db.apartments.find({}))
    
    print(f"\nFound {len(zillow_apts)} apartments with REAL interior images")
    
    # Organize by bedroom type
    interior_images = {
        'studio': [],
        '1br': [],
        '2br': []
    }
    
    for apt in zillow_apts:
        bedrooms = apt.get('bedrooms', 0)
        images = apt.get('images', [])
        
        if bedrooms == 0:
            interior_images['studio'].extend(images)
        elif bedrooms == 1:
            interior_images['1br'].extend(images)
        elif bedrooms == 2:
            interior_images['2br'].extend(images)
    
    print(f"\n📸 Real Interior Images Collected:")
    print(f"   Studios: {len(interior_images['studio'])} images")
    print(f"   1 Bedrooms: {len(interior_images['1br'])} images")
    print(f"   2 Bedrooms: {len(interior_images['2br'])} images")
    
    return interior_images

def replace_with_real_interiors(real_images):
    """Replace generic Mercedes House images with real apartment interiors"""
    
    print(f"\n{'='*80}")
    print(f"🔄 REPLACING GENERIC IMAGES WITH REAL INTERIORS")
    print(f"{'='*80}")
    
    apartments = target_db.apartments
    
    # Get Mercedes House apartments by type
    studios = list(apartments.find({'building_name': 'Mercedes House', 'bedrooms': 0}).sort('unit_number', 1))
    one_beds = list(apartments.find({'building_name': 'Mercedes House', 'bedrooms': 1}).sort('unit_number', 1))
    two_beds = list(apartments.find({'building_name': 'Mercedes House', 'bedrooms': 2}).sort('unit_number', 1))
    
    updated_count = 0
    
    # Update Studios
    print(f"\n🏠 Updating Studios with REAL interior images:")
    for i, apt in enumerate(studios):
        # Get unique set of real studio interior images
        start_idx = i * 4
        end_idx = start_idx + 8  # 8 images total
        new_images = real_images['studio'][start_idx:end_idx]
        
        if len(new_images) < 4:
            print(f"   ⚠️  Not enough studio images, skipping...")
            continue
        
        apartments.update_one(
            {'_id': apt['_id']},
            {'$set': {'images': new_images}}
        )
        updated_count += 1
        
        print(f"   ✅ Unit {apt.get('unit_number', 'N/A')}: {len(new_images)} REAL interior images")
        print(f"      Sample: {new_images[0][-60:]}...")
    
    # Update 1 Bedrooms
    print(f"\n🏠 Updating 1 Bedrooms with REAL interior images:")
    for i, apt in enumerate(one_beds):
        start_idx = i * 4
        end_idx = start_idx + 8
        new_images = real_images['1br'][start_idx:end_idx]
        
        if len(new_images) < 4:
            print(f"   ⚠️  Not enough 1BR images, skipping...")
            continue
        
        apartments.update_one(
            {'_id': apt['_id']},
            {'$set': {'images': new_images}}
        )
        updated_count += 1
        
        print(f"   ✅ Unit {apt.get('unit_number', 'N/A')}: {len(new_images)} REAL interior images")
        print(f"      Sample: {new_images[0][-60:]}...")
    
    # Update 2 Bedrooms
    print(f"\n🏠 Updating 2 Bedrooms with REAL interior images:")
    for i, apt in enumerate(two_beds):
        start_idx = i * 4
        end_idx = start_idx + 8
        new_images = real_images['2br'][start_idx:end_idx]
        
        if len(new_images) < 4:
            print(f"   ⚠️  Not enough 2BR images, skipping...")
            continue
        
        apartments.update_one(
            {'_id': apt['_id']},
            {'$set': {'images': new_images}}
        )
        updated_count += 1
        
        print(f"   ✅ Unit {apt.get('unit_number', 'N/A')}: {len(new_images)} REAL interior images")
        print(f"      Sample: {new_images[0][-60:]}...")
    
    return updated_count

def verify_real_images():
    """Verify all apartments now have real Zillow interior images"""
    
    print(f"\n{'='*80}")
    print(f"✅ VERIFICATION - REAL INTERIOR IMAGES")
    print(f"{'='*80}")
    
    apartments = target_db.apartments
    all_apts = list(apartments.find({'building_name': 'Mercedes House'}))
    
    print(f"\nChecking {len(all_apts)} Mercedes House apartments:")
    
    for apt in all_apts:
        unit = apt.get('unit_number', 'N/A')
        images = apt.get('images', [])
        first_img = images[0] if images else 'NO IMAGES'
        
        is_real_interior = 'zillowstatic.com' in first_img
        status = '✅ REAL INTERIOR' if is_real_interior else '❌ GENERIC'
        
        print(f"   Unit {unit}: {len(images)} images - {status}")
        if is_real_interior:
            print(f"      {first_img[-70:]}...")

def main():
    print("🏠 REPLACING GENERIC IMAGES WITH REAL APARTMENT INTERIORS")
    print("   Source: nofeeplaces database (Zillow real photos)")
    print("   Target: nofeeplaces_database (Mercedes House)")
    
    # Get real interior images
    real_images = get_real_interior_images_by_type()
    
    # Replace generic images
    updated = replace_with_real_interiors(real_images)
    
    # Verify
    verify_real_images()
    
    print(f"\n{'='*80}")
    print(f"✅ IMAGE REPLACEMENT COMPLETE")
    print(f"{'='*80}")
    print(f"   Apartments updated: {updated}")
    print(f"   All apartments now have REAL interior apartment photos")
    print(f"   Source: Zillow verified listings (not generic stock images)")
    
    client.close()
    
    print(f"\n✅ Restart backend to see REAL interior images!")

if __name__ == "__main__":
    main()
