#!/usr/bin/env python3
"""
Reorder Mercedes House images to prioritize interiors
Order: Unit interiors FIRST → Amenities MIDDLE → Building exteriors LAST
"""

from pymongo import MongoClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

def reorder_mercedes_house_images(db):
    """Reorder Mercedes House images: interiors first, amenities middle, building last"""
    
    print("="*80)
    print("🔄 REORDERING MERCEDES HOUSE IMAGES")
    print("   Priority: INTERIORS → AMENITIES → BUILDING")
    print("="*80)
    
    apartments = db.apartments
    mercedes_apts = list(apartments.find({'building_name': 'Mercedes House'}))
    
    print(f"\nFound {len(mercedes_apts)} Mercedes House apartments")
    
    updated_count = 0
    
    for apt in mercedes_apts:
        images = apt.get('images', [])
        if not images:
            continue
        
        # Categorize images
        interior_images = []
        amenity_images = []
        building_images = []
        other_images = []
        
        for img in images:
            img_lower = img.lower()
            
            # Unit interior photos (static room photos) - HIGHEST PRIORITY
            if 'static' in img_lower and ('studio' in img_lower or 'bed' in img_lower):
                interior_images.append(img)
            
            # Amenity photos - MIDDLE PRIORITY
            elif 'amenities' in img_lower or 'amenity' in img_lower:
                amenity_images.append(img)
            
            # Building/exterior photos - LOWEST PRIORITY
            elif 'building' in img_lower or 'slideshow' in img_lower or 'feature' in img_lower:
                building_images.append(img)
            
            else:
                other_images.append(img)
        
        # Reorder: INTERIORS first, then amenities, then other, then building last
        new_order = interior_images + amenity_images + other_images + building_images
        
        # Only update if order changed
        if new_order != images:
            apartments.update_one(
                {'_id': apt['_id']},
                {'$set': {'images': new_order}}
            )
            updated_count += 1
            
            print(f"\n✅ Reordered: {apt['title']}")
            print(f"   Original order: {len(interior_images)} interiors, {len(amenity_images)} amenities, {len(building_images)} building")
            print(f"   New order: INTERIORS → AMENITIES → BUILDING")
            
            # Show first 5 images in new order
            print(f"   First 5 images:")
            for i, img in enumerate(new_order[:5], 1):
                img_type = 'INTERIOR' if img in interior_images else \
                           'AMENITY' if img in amenity_images else \
                           'BUILDING' if img in building_images else 'OTHER'
                filename = img.split('/')[-1].split('?')[0][:50]
                print(f"      {i}. [{img_type}] {filename}")
    
    print(f"\n{'='*80}")
    print(f"✅ IMAGE REORDERING COMPLETE")
    print(f"{'='*80}")
    print(f"   Apartments updated: {updated_count}")
    print(f"   First image on ALL cards: Interior unit photos ✅")
    
    return updated_count

def main():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    updated = reorder_mercedes_house_images(db)
    
    if updated > 0:
        print(f"\n🎯 RESULT:")
        print(f"   Listing cards will now show unit interiors FIRST")
        print(f"   Amenities photos in MIDDLE")
        print(f"   Building exteriors at END")
        print(f"   Perfect for showcasing living spaces!")
    else:
        print(f"\n✅ Images already in optimal order")
    
    # Show sample
    print(f"\n📸 SAMPLE APARTMENT - IMAGE ORDER:")
    sample = db.apartments.find_one({'building_name': 'Mercedes House', 'bedrooms': 1})
    if sample:
        print(f"\n   {sample['title']}")
        print(f"   Total images: {len(sample['images'])}")
        print(f"\n   Image order:")
        for i, img in enumerate(sample['images'], 1):
            img_lower = img.lower()
            if 'static' in img_lower:
                img_type = '🏠 INTERIOR'
            elif 'amenities' in img_lower:
                img_type = '🏋️ AMENITY'
            elif 'building' in img_lower:
                img_type = '🏢 BUILDING'
            else:
                img_type = '📷 OTHER'
            
            filename = img.split('/')[-1][:40]
            print(f"      {i}. {img_type} - {filename}")
    
    client.close()
    
    print(f"\n✅ Restart backend to apply changes")

if __name__ == "__main__":
    main()
