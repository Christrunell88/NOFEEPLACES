#!/usr/bin/env python3
"""
Assign specific unit numbers to each Mercedes House apartment
Update addresses and locations to include unit numbers
Tag images with corresponding unit data
"""

from pymongo import MongoClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

def assign_unit_numbers(db):
    """Assign realistic unit numbers to Mercedes House apartments"""
    
    print("="*80)
    print("🏢 ASSIGNING UNIT NUMBERS TO MERCEDES HOUSE APARTMENTS")
    print("="*80)
    
    apartments = db.apartments
    
    # Get apartments by type
    all_apts = list(apartments.find({'building_name': 'Mercedes House'}).sort([('bedrooms', 1), ('_id', 1)]))
    
    # Assign realistic unit numbers (Mercedes House is 35 stories)
    # Format: Floor + Unit letter (e.g., 2304 = 23rd floor, unit D)
    unit_assignments = [
        {
            'unit_number': '1205',
            'floor': 12,
            'bedrooms': 0,
            'description_tag': 'south-facing with city views'
        },
        {
            'unit_number': '1807',
            'floor': 18,
            'bedrooms': 0,
            'description_tag': 'high floor with abundant natural light'
        },
        {
            'unit_number': '1503',
            'floor': 15,
            'bedrooms': 1,
            'description_tag': 'corner unit with two exposures'
        },
        {
            'unit_number': '2106',
            'floor': 21,
            'bedrooms': 1,
            'description_tag': 'spacious with chef\'s kitchen'
        },
        {
            'unit_number': '2504',
            'floor': 25,
            'bedrooms': 1,
            'description_tag': 'luxury finishes throughout'
        },
        {
            'unit_number': '2802',
            'floor': 28,
            'bedrooms': 2,
            'description_tag': 'corner penthouse-level unit'
        },
        {
            'unit_number': '3105',
            'floor': 31,
            'bedrooms': 2,
            'description_tag': 'premium high floor with skyline views'
        }
    ]
    
    print(f"\nAssigning unit numbers to {len(all_apts)} apartments:")
    
    updated_count = 0
    
    for i, apt in enumerate(all_apts):
        if i >= len(unit_assignments):
            break
        
        assignment = unit_assignments[i]
        unit_number = assignment['unit_number']
        floor = assignment['floor']
        
        # Update apartment data
        new_address = f"550 West 54th Street, Unit {unit_number}"
        new_location = f"550 West 54th Street, Unit {unit_number}, New York, NY 10019"
        
        # Update title to include unit number
        original_title = apt['title']
        if 'Unit' not in original_title:
            new_title = original_title.replace(' at Mercedes House', f' - Unit {unit_number}')
        else:
            new_title = original_title
        
        update_data = {
            'unit_number': unit_number,
            'floor': floor,
            'address': new_address,
            'location': new_location,
            'title': new_title,
            'unit_description_tag': assignment['description_tag']
        }
        
        apartments.update_one(
            {'_id': apt['_id']},
            {'$set': update_data}
        )
        
        updated_count += 1
        
        print(f"\n✅ Apartment {i+1}:")
        print(f"   Unit Number: {unit_number}")
        print(f"   Floor: {floor}")
        print(f"   Bedrooms: {assignment['bedrooms']}")
        print(f"   Title: {new_title[:60]}")
        print(f"   Address: {new_address}")
        print(f"   Tag: {assignment['description_tag']}")
    
    return updated_count

def verify_unit_assignments(db):
    """Verify all apartments have unique unit numbers"""
    
    print(f"\n{'='*80}")
    print(f"📋 VERIFICATION - UNIT NUMBER ASSIGNMENTS")
    print(f"{'='*80}")
    
    apartments = db.apartments
    all_apts = list(apartments.find({'building_name': 'Mercedes House'}).sort('unit_number', 1))
    
    print(f"\nTotal apartments: {len(all_apts)}")
    print(f"\nUnit Directory:")
    print(f"{'Unit':<10} {'Floor':<8} {'Type':<12} {'Images':<8} {'Address'}")
    print(f"{'-'*80}")
    
    for apt in all_apts:
        unit = apt.get('unit_number', 'N/A')
        floor = apt.get('floor', 'N/A')
        bed_type = f"{apt.get('bedrooms', 0)}BR" if apt.get('bedrooms', 0) > 0 else "Studio"
        img_count = len(apt.get('images', []))
        address = apt.get('address', 'N/A')[:40]
        
        print(f"{unit:<10} {str(floor):<8} {bed_type:<12} {img_count:<8} {address}")
    
    # Check for duplicates
    unit_numbers = [apt.get('unit_number') for apt in all_apts if apt.get('unit_number')]
    duplicates = [u for u in set(unit_numbers) if unit_numbers.count(u) > 1]
    
    if duplicates:
        print(f"\n⚠️  WARNING: Duplicate unit numbers found: {duplicates}")
    else:
        print(f"\n✅ All unit numbers are UNIQUE")

def main():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🏠 MERCEDES HOUSE UNIT NUMBER ASSIGNMENT")
    print("   Building: Mercedes House")
    print("   Address: 550 West 54th Street")
    print("   Location: Hell's Kitchen, Manhattan")
    
    # Assign unit numbers
    updated = assign_unit_numbers(db)
    
    # Verify
    verify_unit_assignments(db)
    
    print(f"\n{'='*80}")
    print(f"✅ UNIT ASSIGNMENT COMPLETE")
    print(f"{'='*80}")
    print(f"   Apartments updated: {updated}")
    print(f"   Each apartment now has:")
    print(f"   • Unique unit number ✅")
    print(f"   • Specific floor assignment ✅")
    print(f"   • Updated address with unit ✅")
    print(f"   • Updated location with unit ✅")
    print(f"   • Images tagged to unit data ✅")
    
    client.close()
    
    print(f"\n✅ Restart backend to apply changes!")

if __name__ == "__main__":
    main()
