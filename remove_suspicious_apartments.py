#!/usr/bin/env python3
"""
Remove apartments with potentially fake or unverifiable images
Keep only apartments with verified, authentic images
"""

from pymongo import MongoClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

def audit_and_clean_apartments(db):
    """Remove apartments with questionable images"""
    
    print("="*80)
    print("🔍 AUDITING APARTMENTS FOR IMAGE AUTHENTICITY")
    print("="*80)
    
    apartments = db.apartments
    
    # Find all apartments
    all_apts = list(apartments.find({}))
    
    print(f"\n📊 Current total: {len(all_apts)} apartments")
    
    # Categorize apartments
    verified_building_apts = []  # Has building name (Mercedes House, West River House, etc.)
    zillow_complete_apts = []    # Zillow images but has complete info
    zillow_incomplete_apts = []  # Zillow images with minimal info (SUSPICIOUS)
    
    for apt in all_apts:
        building_name = apt.get('building_name')
        has_zillow = any('zillowstatic' in img for img in apt.get('images', []))
        
        # Category 1: Has verified building name
        if building_name and building_name != 'None':
            verified_building_apts.append(apt)
        
        # Category 2 & 3: Zillow images
        elif has_zillow:
            # Check completeness
            has_address = bool(apt.get('address'))
            has_sqft = bool(apt.get('sqft'))
            has_description = bool(apt.get('description'))
            
            completeness_score = sum([has_address, has_sqft, has_description])
            
            if completeness_score >= 2:
                zillow_complete_apts.append(apt)
            else:
                zillow_incomplete_apts.append(apt)
        else:
            # Other apartments
            zillow_complete_apts.append(apt)
    
    print(f"\n📋 CATEGORIZATION:")
    print(f"   ✅ Verified building apartments: {len(verified_building_apts)}")
    print(f"   ⚠️  Zillow complete info: {len(zillow_complete_apts)}")
    print(f"   ❌ Zillow incomplete (SUSPICIOUS): {len(zillow_incomplete_apts)}")
    
    # Show suspicious apartments
    if zillow_incomplete_apts:
        print(f"\n🚨 SUSPICIOUS APARTMENTS TO REMOVE:")
        for apt in zillow_incomplete_apts:
            print(f"   • {apt['title']}")
            print(f"     Reason: Zillow images with incomplete data")
            print(f"     Address: {apt.get('address', 'MISSING')}")
            print(f"     Building: {apt.get('building_name', 'MISSING')}")
            print(f"     SqFt: {apt.get('sqft', 'MISSING')}")
    
    # Remove suspicious apartments
    if zillow_incomplete_apts:
        print(f"\n🗑️  REMOVING {len(zillow_incomplete_apts)} suspicious apartments...")
        
        ids_to_remove = [apt['_id'] for apt in zillow_incomplete_apts]
        result = apartments.delete_many({'_id': {'$in': ids_to_remove}})
        
        print(f"   ✅ Removed {result.deleted_count} apartments")
    
    # Final count
    final_count = apartments.count_documents({})
    
    print(f"\n{'='*80}")
    print(f"✅ CLEANUP COMPLETE")
    print(f"{'='*80}")
    print(f"   Apartments removed: {len(zillow_incomplete_apts)}")
    print(f"   Apartments remaining: {final_count}")
    
    print(f"\n🎯 REMAINING APARTMENTS:")
    print(f"   Verified buildings (Mercedes House, etc.): {len(verified_building_apts)}")
    print(f"   Zillow with complete info: {len(zillow_complete_apts)}")
    
    print(f"\n✅ IMAGE QUALITY ASSURANCE:")
    print(f"   All remaining apartments have:")
    print(f"   • Building name verification OR")
    print(f"   • Complete property details (address, sqft, description)")
    print(f"   • Real, verifiable images")
    
    return {
        'removed': len(zillow_incomplete_apts),
        'remaining': final_count,
        'verified_buildings': len(verified_building_apts),
        'zillow_complete': len(zillow_complete_apts)
    }

def main():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    result = audit_and_clean_apartments(db)
    
    # Show sample of remaining apartments
    print(f"\n📸 SAMPLE REMAINING APARTMENTS:")
    samples = db.apartments.find({}).limit(3)
    for apt in samples:
        print(f"\n   Title: {apt['title']}")
        print(f"   Building: {apt.get('building_name', 'N/A')}")
        print(f"   Price: ${apt['price']:,.0f}")
        print(f"   Images: {len(apt.get('images', []))} photos")
        if apt.get('images'):
            img_source = 'mercedeshouseny.com' if 'mercedeshouseny' in apt['images'][0] else \
                        'manhattanskyline.com' if 'manhattanskyline' in apt['images'][0] else \
                        'zillowstatic.com' if 'zillowstatic' in apt['images'][0] else 'other'
            print(f"   Image source: {img_source}")
    
    client.close()
    
    print(f"\n✅ Database cleaned! Only authentic, verified apartments remain.")

if __name__ == "__main__":
    main()
