#!/usr/bin/env python3
"""
Reorder apartment images to prioritize unit interiors over building exteriors
Put interior photos first, amenities second, building exteriors last
"""

from pymongo import MongoClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

def reorder_apartment_images(db):
    """Reorder images to show interiors first, building exteriors last"""
    
    print("="*80)
    print("🔄 REORDERING IMAGES - INTERIORS FIRST, EXTERIORS LAST")
    print("="*80)
    
    apartments = db.apartments
    all_apts = list(apartments.find({}))
    
    updated_count = 0
    
    for apt in all_apts:
        images = apt.get('images', [])
        if not images:
            continue
        
        # Categorize images
        interior_unit_images = []
        amenity_images = []
        building_exterior_images = []
        other_images = []
        
        for img in images:
            img_lower = img.lower()
            
            # Unit interior photos (static room photos)
            if 'static' in img_lower and ('studio' in img_lower or 'bed' in img_lower):
                interior_unit_images.append(img)
            
            # Amenity photos
            elif 'amenities' in img_lower or 'amenity' in img_lower:
                amenity_images.append(img)
            
            # Building/exterior photos
            elif 'building' in img_lower or 'slideshow' in img_lower or 'feature' in img_lower:
                building_exterior_images.append(img)
            
            # Manhattan Skyline - categorize by URL pattern
            elif 'manhattanskyline.com' in img:
                if '/unit/' in img:
                    interior_unit_images.append(img)
                elif '/building/' in img:
                    building_exterior_images.append(img)
                else:
                    other_images.append(img)
            
            else:
                other_images.append(img)
        
        # Reorder: interiors first, then amenities, then building exteriors
        new_order = interior_unit_images + amenity_images + other_images + building_exterior_images
        
        # Only update if order changed
        if new_order != images:
            apartments.update_one(
                {'_id': apt['_id']},
                {'$set': {'images': new_order}}
            )
            updated_count += 1
            
            print(f"\n✅ Reordered: {apt['title']}")
            print(f"   Before: {len(interior_unit_images)} interiors, {len(amenity_images)} amenities, {len(building_exterior_images)} building")
            print(f"   New order: Interiors → Amenities → Building")
            
            # Show first 3 images
            print(f"   First 3 images:")
            for i, img in enumerate(new_order[:3], 1):
                img_type = 'INTERIOR' if img in interior_unit_images else \
                           'AMENITY' if img in amenity_images else \
                           'BUILDING' if img in building_exterior_images else 'OTHER'
                filename = img.split('/')[-1][:50]
                print(f"      {i}. [{img_type}] {filename}")
    
    print(f"\n{'='*80}")
    print(f"✅ IMAGE REORDERING COMPLETE")
    print(f"{'='*80}")
    print(f"   Apartments updated: {updated_count}")
    print(f"   Priority order: INTERIORS → AMENITIES → BUILDING EXTERIORS")
    
    return updated_count

def main():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    updated = reorder_apartment_images(db)
    
    if updated > 0:
        print(f"\n🎯 RESULT:")
        print(f"   Users will now see unit interiors FIRST")
        print(f"   Building exteriors moved to END of gallery")
        print(f"   Better showcase of actual living spaces")
    else:
        print(f"\n✅ Images already in optimal order")
    
    client.close()
    
    print(f"\n✅ Restart backend to see changes")

if __name__ == "__main__":
    main()
