#!/usr/bin/env python3
"""
Consolidate ALL apartments from both databases into 'nofeeplaces_database'
- Migrate from 'nofeeplaces' database
- Keep existing apartments in 'nofeeplaces_database'
- Add proper labeling: source database, verified status
- Remove duplicates based on address + price
- Sort by price (ascending)
"""

from pymongo import MongoClient
import os
import uuid
from datetime import datetime

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')

client = MongoClient(MONGO_URL)
nofeeplaces_db = client['nofeeplaces']
target_db = client['nofeeplaces_database']

def consolidate_apartments():
    """Consolidate all apartments with proper labeling"""
    
    print("="*80)
    print("📦 CONSOLIDATING ALL APARTMENTS INTO 'nofeeplaces_database'")
    print("="*80)
    
    # Get apartments from both databases
    source_apts = list(nofeeplaces_db.apartments.find({}))
    existing_apts = list(target_db.apartments.find({}))
    
    print(f"\n📊 Source ('nofeeplaces'): {len(source_apts)} apartments")
    print(f"📊 Target ('nofeeplaces_database'): {len(existing_apts)} apartments")
    
    # Create a dictionary to track unique apartments (by address + price)
    all_apartments = {}
    
    # Process existing apartments first (keep them with their current labels)
    for apt in existing_apts:
        key = (apt.get('address', ''), apt.get('price', 0))
        if key not in all_apartments:
            # Add source label if not present
            if 'source_database' not in apt:
                apt['source_database'] = 'nofeeplaces_database'
            all_apartments[key] = apt
    
    # Process source apartments
    for apt in source_apts:
        key = (apt.get('address', ''), apt.get('price', 0))
        if key not in all_apartments:
            # Add source label
            apt['source_database'] = 'nofeeplaces'
            # Ensure proper fields
            if 'id' not in apt or not apt['id']:
                apt['id'] = str(uuid.uuid4())
            if 'broker_fee' not in apt:
                apt['broker_fee'] = 'No fee'
            if 'available' not in apt:
                apt['available'] = True
            if 'is_verified' not in apt:
                apt['is_verified'] = True
            if 'is_real' not in apt:
                apt['is_real'] = True
            if 'created_at' not in apt:
                apt['created_at'] = datetime.utcnow()
            if 'updated_at' not in apt:
                apt['updated_at'] = datetime.utcnow()
            
            all_apartments[key] = apt
    
    print(f"\n📋 Total unique apartments: {len(all_apartments)}")
    
    # Clear and repopulate target database
    target_db.apartments.delete_many({})
    print(f"✅ Cleared target database")
    
    # Sort by price and insert
    sorted_apts = sorted(all_apartments.values(), key=lambda x: x.get('price', 0))
    
    imported_count = 0
    for apt in sorted_apts:
        # Remove MongoDB _id if present to avoid conflicts
        if '_id' in apt:
            del apt['_id']
        
        target_db.apartments.insert_one(apt)
        imported_count += 1
        
        source_label = apt.get('source_database', 'unknown')
        print(f"\n✅ ${apt['price']:,.0f} - {apt['bedrooms']}BR - {apt.get('neighborhood', 'N/A')}")
        print(f"   {apt.get('title', 'No title')[:60]}")
        print(f"   Images: {len(apt.get('images', []))} | Source: {source_label}")
    
    return imported_count

def verify_consolidation():
    """Verify all apartments consolidated correctly"""
    
    print(f"\n{'='*80}")
    print(f"✅ CONSOLIDATION VERIFICATION")
    print(f"{'='*80}")
    
    apartments = target_db.apartments
    all_apts = list(apartments.find({}).sort('price', 1))
    
    print(f"\nTotal apartments: {len(all_apts)}")
    if all_apts:
        print(f"Price range: ${all_apts[0]['price']:,.0f} - ${all_apts[-1]['price']:,.0f}")
    
    # Check source labels
    print(f"\n📊 SOURCE DISTRIBUTION:")
    sources = {}
    for apt in all_apts:
        source = apt.get('source_database', 'unlabeled')
        sources[source] = sources.get(source, 0) + 1
    
    for source, count in sources.items():
        print(f"   {source}: {count} apartments")
    
    print(f"\n📊 PRICE DISTRIBUTION:")
    ranges = {
        '$1,500-$3,000': 0,
        '$3,001-$5,000': 0,
        '$5,001-$8,000': 0,
        '$8,001-$12,000': 0,
        '$12,001-$25,000': 0
    }
    
    for apt in all_apts:
        price = apt['price']
        if price <= 3000:
            ranges['$1,500-$3,000'] += 1
        elif price <= 5000:
            ranges['$3,001-$5,000'] += 1
        elif price <= 8000:
            ranges['$5,001-$8,000'] += 1
        elif price <= 12000:
            ranges['$8,001-$12,000'] += 1
        else:
            ranges['$12,001-$25,000'] += 1
    
    for range_name, count in ranges.items():
        print(f"   {range_name}: {count} apartments")
    
    print(f"\n📋 BEDROOM DISTRIBUTION:")
    bedrooms = {}
    for apt in all_apts:
        br = f"{apt['bedrooms']}BR" if apt['bedrooms'] > 0 else "Studio"
        bedrooms[br] = bedrooms.get(br, 0) + 1
    
    for br, count in sorted(bedrooms.items()):
        print(f"   {br}: {count} apartments")
    
    print(f"\n🖼️  IMAGE VERIFICATION:")
    all_have_images = all(len(apt.get('images', [])) > 0 for apt in all_apts)
    if all_have_images:
        print(f"   ✅ All apartments have images")
    else:
        no_images = [apt for apt in all_apts if len(apt.get('images', [])) == 0]
        print(f"   ⚠️  {len(no_images)} apartments missing images")

def main():
    print("🏠 CONSOLIDATING APARTMENT DATABASES")
    print("   Merging: 'nofeeplaces' + 'nofeeplaces_database'")
    print("   Target: 'nofeeplaces_database' (active)")
    print("   Features: Proper labeling, deduplication, price sorting")
    
    # Consolidate all apartments
    imported = consolidate_apartments()
    
    # Verify
    verify_consolidation()
    
    print(f"\n{'='*80}")
    print(f"✅ CONSOLIDATION COMPLETE")
    print(f"{'='*80}")
    print(f"   Total apartments: {imported}")
    print(f"   All properly labeled with source database ✅")
    print(f"   Duplicates removed ✅")
    print(f"   Sorted by price (cheapest first) ✅")
    
    client.close()
    
    print(f"\n✅ Restart backend to see consolidated inventory!")

if __name__ == "__main__":
    main()
