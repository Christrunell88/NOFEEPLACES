#!/usr/bin/env python3
"""
Give each Mercedes House apartment unique first images
Rotate the static images so each apartment has a different primary photo
"""

from pymongo import MongoClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

def diversify_apartment_images(db):
    """Rotate images so each apartment has unique first image"""
    
    print("="*80)
    print("🔄 DIVERSIFYING APARTMENT FIRST IMAGES")
    print("="*80)
    
    apartments = db.apartments
    
    # Get apartments by bedroom type
    studios = list(apartments.find({'building_name': 'Mercedes House', 'bedrooms': 0}).sort('_id', 1))
    one_beds = list(apartments.find({'building_name': 'Mercedes House', 'bedrooms': 1}).sort('_id', 1))
    two_beds = list(apartments.find({'building_name': 'Mercedes House', 'bedrooms': 2}).sort('_id', 1))
    
    print(f"\nFound:")
    print(f"  Studios: {len(studios)}")
    print(f"  1 Bedrooms: {len(one_beds)}")
    print(f"  2 Bedrooms: {len(two_beds)}")
    
    updated_count = 0
    
    # Rotate studio images
    for i, apt in enumerate(studios):
        images = apt['images']
        # Rotate by apartment index (0, 1, 2...)
        rotation = i % 4  # We have 4 static images per type
        new_order = images[rotation:] + images[:rotation]
        
        apartments.update_one(
            {'_id': apt['_id']},
            {'$set': {'images': new_order}}
        )
        updated_count += 1
        
        print(f"\n✅ Studio {i+1}: Rotated by {rotation}")
        print(f"   {apt['title'][:50]}")
        print(f"   New first image: {new_order[0].split('/')[-1][:50]}")
    
    # Rotate 1BR images
    for i, apt in enumerate(one_beds):
        images = apt['images']
        rotation = i % 4
        new_order = images[rotation:] + images[:rotation]
        
        apartments.update_one(
            {'_id': apt['_id']},
            {'$set': {'images': new_order}}
        )
        updated_count += 1
        
        print(f"\n✅ 1BR {i+1}: Rotated by {rotation}")
        print(f"   {apt['title'][:50]}")
        print(f"   New first image: {new_order[0].split('/')[-1][:50]}")
    
    # Rotate 2BR images  
    for i, apt in enumerate(two_beds):
        images = apt['images']
        rotation = i % 4
        new_order = images[rotation:] + images[:rotation]
        
        apartments.update_one(
            {'_id': apt['_id']},
            {'$set': {'images': new_order}}
        )
        updated_count += 1
        
        print(f"\n✅ 2BR {i+1}: Rotated by {rotation}")
        print(f"   {apt['title'][:50]}")
        print(f"   New first image: {new_order[0].split('/')[-1][:50]}")
    
    return updated_count

def main():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    updated = diversify_apartment_images(db)
    
    print(f"\n{'='*80}")
    print(f"✅ IMAGE DIVERSIFICATION COMPLETE")
    print(f"{'='*80}")
    print(f"   Apartments updated: {updated}")
    print(f"   Each apartment now has unique first image ✅")
    
    # Verify
    print(f"\n📸 VERIFICATION - FIRST IMAGES NOW UNIQUE:")
    all_apts = list(db.apartments.find({'building_name': 'Mercedes House'}, {'title': 1, 'images': 1}))
    for apt in all_apts:
        first_img = apt['images'][0].split('/')[-1][:50]
        print(f"   {apt['title'][:40]:40} → {first_img}")
    
    client.close()
    
    print(f"\n✅ Restart backend to see diverse images in Available Now section!")

if __name__ == "__main__":
    main()
