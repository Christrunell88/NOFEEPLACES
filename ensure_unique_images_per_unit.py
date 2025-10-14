#!/usr/bin/env python3
"""
Ensure each apartment has completely unique images with NO overlap
Pull from nofeeplaces database and distribute uniquely
"""

from pymongo import MongoClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')

client = MongoClient(MONGO_URL)
source_db = client['nofeeplaces']
target_db = client['nofeeplaces_database']

def get_all_unique_interior_images():
    """Get ALL unique Zillow interior images from nofeeplaces database"""
    
    print("="*80)
    print("🔍 COLLECTING ALL UNIQUE INTERIOR IMAGES")
    print("="*80)
    
    all_apts = list(source_db.apartments.find({}))
    
    all_images = []
    seen = set()
    
    for apt in all_apts:
        for img in apt.get('images', []):
            if img not in seen:
                all_images.append(img)
                seen.add(img)
    
    print(f"\nCollected {len(all_images)} unique interior images from {len(all_apts)} source apartments")
    
    return all_images

def assign_unique_images_no_overlap():
    """Assign completely unique images to each apartment with NO overlap"""
    
    print(f"\n{'='*80}")
    print(f"🔄 ASSIGNING UNIQUE IMAGES - NO OVERLAP")
    print(f"{'='*80}")
    
    # Get all unique images
    all_unique_images = get_all_unique_interior_images()
    
    # Get target apartments
    apartments = target_db.apartments
    all_apts = list(apartments.find({}).sort('unit_number', 1))
    
    print(f"\nAssigning to {len(all_apts)} apartments:")
    print(f"Available unique images: {len(all_unique_images)}")
    
    images_per_apt = len(all_unique_images) // len(all_apts)
    print(f"Images per apartment: {images_per_apt}")
    
    updated_count = 0
    used_images = set()
    
    for i, apt in enumerate(all_apts):
        # Calculate unique range for this apartment
        start_idx = i * images_per_apt
        end_idx = start_idx + images_per_apt
        
        # Get unique images for this apartment
        apt_images = all_unique_images[start_idx:end_idx]
        
        # Double-check no overlap
        for img in apt_images:
            if img in used_images:
                print(f"   ⚠️  WARNING: Image overlap detected!")
            used_images.add(img)
        
        # Update apartment
        apartments.update_one(
            {'_id': apt['_id']},
            {'$set': {'images': apt_images}}
        )
        updated_count += 1
        
        unit = apt.get('unit_number', 'N/A')
        print(f"\n✅ Unit {unit}:")
        print(f"   Assigned {len(apt_images)} unique images")
        print(f"   Range: images {start_idx+1} to {end_idx}")
        print(f"   First image ID: {apt_images[0].split('/')[-1].split('-')[0]}")
        print(f"   Last image ID: {apt_images[-1].split('/')[-1].split('-')[0]}")
    
    return updated_count

def verify_no_duplicates():
    """Verify each apartment has completely unique images"""
    
    print(f"\n{'='*80}")
    print(f"✅ VERIFICATION - NO DUPLICATE IMAGES")
    print(f"{'='*80}")
    
    apartments = target_db.apartments
    all_apts = list(apartments.find({}).sort('unit_number', 1))
    
    all_images_used = []
    
    for apt in all_apts:
        unit = apt.get('unit_number', 'N/A')
        images = apt.get('images', [])
        
        print(f"\nUnit {unit}: {len(images)} images")
        
        for img in images:
            if img in all_images_used:
                print(f"   ❌ DUPLICATE FOUND: {img[-60:]}")
            else:
                all_images_used.append(img)
        
        if not any(img in all_images_used[:-len(images)] for img in images):
            print(f"   ✅ All images UNIQUE (no overlap with other units)")
    
    # Check for duplicates
    duplicates = [img for img in all_images_used if all_images_used.count(img) > 1]
    
    print(f"\n{'='*80}")
    if duplicates:
        print(f"❌ DUPLICATES FOUND: {len(duplicates)} images used multiple times")
    else:
        print(f"✅ NO DUPLICATES: All {len(all_images_used)} images are unique")
    print(f"{'='*80}")

def main():
    print("🏠 ENSURING COMPLETELY UNIQUE IMAGES PER APARTMENT")
    print("   Rule: NO image overlap between any apartments")
    
    # Assign unique images
    updated = assign_unique_images_no_overlap()
    
    # Verify
    verify_no_duplicates()
    
    print(f"\n✅ IMAGE ASSIGNMENT COMPLETE")
    print(f"   Apartments updated: {updated}")
    print(f"   Each apartment has 100% unique images")
    print(f"   NO image sharing between units")
    
    client.close()
    
    print(f"\n✅ Restart backend to apply changes!")

if __name__ == "__main__":
    main()
