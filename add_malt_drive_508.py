#!/usr/bin/env python3
"""
Add Malt Drive Apartment 508 (Studio 1 Bath)
Source: https://maltdrive.com/listing/2-21-malt-drive_508/
"""
import os
import sys
import uuid
from pymongo import MongoClient
from datetime import datetime, timezone

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_database')
client = MongoClient(MONGO_URL)
db = client["nofeeplaces_database"]
apartments_collection = db['apartments']
buildings_collection = db['buildings']

# Building ID for Malt Drive 2-21
BUILDING_ID = 'ec2ae99d-4083-44b1-81ec-0241cf5d54a6'

# Unit data for Apartment 508
unit_data = {
    'unit_number': '508',
    'title': 'Studio 1 Bath at Malt Drive 2-21',
    'bedrooms': 0,  # Studio
    'bathrooms': 1,
    'price': 3685,  # Gross rent
    'sqft': None,  # Not specified on listing
    'description': 'Incredible Studio, 1 Bath Apartment Featuring a Beautiful Open Kitchen, Spacious Living/Dining Area, In-Home Washer/Dryer, Walk-in Closet, and Northern Exposure. Gross Rent $3685. Up To 3 Months Free + 1 Month OP – Limited Time Offer on 24-month lease.',
    'amenities': [
        'Northern Exposure',
        'Open Kitchen',
        'Walk-In Closet',
        'In-Unit Washer/Dryer',
        'Solar Shades',
        'Doorman',
        'Elevator',
        'Fitness Center',
        'Rooftop Pool',
        'Sundeck',
        'Lounge/Party Room',
        'Package Room',
        'Bike Storage',
        'Pet Friendly'
    ],
    'images': [
        'https://maltdrive.com/wp-content/uploads/2025/07/2-21-malt-800x600-2.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-110.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-117.avif',
        'https://maltdrive.com/wp-content/uploads/2025/07/2-21-malt-800x600-22.avif',
        'https://maltdrive.com/wp-content/uploads/2025/07/2-21-malt-800x600-23.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-14.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-118.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-111.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-15.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-12.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-13.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-17.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-16.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-1.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-112.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-114.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-115.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-113.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-19.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-116.avif',
        'https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-119.avif'
    ],
    'contact_email': 'placesfirm@gmail.com',
    'contact_phone': '+1-646-408-8048',
    'source_url': 'https://maltdrive.com/listing/2-21-malt-drive_508/',
    'featured': False,
    'is_verified': True,
    'priority': 5,
    'broker_fee': 0,  # No fee
    'no_fee': True
}

def add_unit_to_building(building_id, unit_data):
    """Add a new unit to an existing building"""
    
    # Verify building exists
    building = buildings_collection.find_one({'building_id': building_id})
    if not building:
        print(f"❌ Building {building_id} not found!")
        return False
    
    print(f"\n🏢 Adding unit to: {building['building_name']}")
    print(f"   Address: {building['address']}")
    print(f"   Location: {building['neighborhood']}, {building['borough']}")
    
    # Check if unit already exists
    existing = apartments_collection.find_one({
        'building_id': building_id,
        'unit_number': unit_data['unit_number']
    })
    
    if existing:
        print(f"\n⚠️  Unit {unit_data['unit_number']} already exists!")
        print(f"   Existing Unit ID: {existing['id']}")
        print(f"   Existing images: {len(existing.get('images', []))}")
        print(f"   New images: {len(unit_data['images'])}")
        print(f"   Auto-updating with improved data...")
        
        # Update existing unit
        apartment_data = {
            **unit_data,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        apartments_collection.update_one(
            {'id': existing['id']},
            {'$set': apartment_data}
        )
        print(f"\n✅ Unit updated successfully!")
        print(f"   Unit ID: {existing['id']}")
    else:
        # Create new apartment document
        apartment_data = {
            'id': str(uuid.uuid4()),
            'building_id': building_id,
            'building_name': building['building_name'],
            'address': building['address'],
            'neighborhood': building['neighborhood'],
            'borough': building['borough'],
            **unit_data,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'available': True
        }
        
        # Insert apartment
        result = apartments_collection.insert_one(apartment_data)
        print(f"\n✅ Unit added successfully!")
        print(f"   Unit ID: {apartment_data['id']}")
    
    print(f"   Unit Number: {unit_data['unit_number']}")
    print(f"   Title: {unit_data['title']}")
    print(f"   Price: ${unit_data['price']:,.0f}/mo")
    print(f"   Bedrooms: {unit_data['bedrooms']} (Studio)")
    print(f"   Bathrooms: {unit_data['bathrooms']}")
    print(f"   Images: {len(unit_data['images'])}")
    
    # Update building stats
    all_units = list(apartments_collection.find({'building_id': building_id}))
    available_units = [u for u in all_units if u.get('available', True)]
    all_prices = [u['price'] for u in all_units if u.get('price')]
    bedroom_types = list(set([u.get('bedrooms') for u in all_units if u.get('bedrooms') is not None]))
    
    buildings_collection.update_one(
        {'building_id': building_id},
        {'$set': {
            'total_units': len(all_units),
            'available_units': len(available_units),
            'price_range': {
                'min': min(all_prices) if all_prices else 0,
                'max': max(all_prices) if all_prices else 0,
                'avg': sum(all_prices) / len(all_prices) if all_prices else 0
            },
            'bedroom_types': sorted(bedroom_types),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }}
    )
    
    print(f"\n📊 Updated building stats:")
    print(f"   Total units: {len(all_units)}")
    print(f"   Available units: {len(available_units)}")
    print(f"   Price range: ${min(all_prices):,.0f} - ${max(all_prices):,.0f}")
    print(f"   Bedroom types: {sorted(bedroom_types)}")
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("ADD MALT DRIVE APARTMENT 508")
    print("=" * 70)
    
    success = add_unit_to_building(BUILDING_ID, unit_data)
    
    if success:
        print("\n" + "=" * 70)
        print("✅ MALT DRIVE APARTMENT 508 ADDED SUCCESSFULLY!")
        print("=" * 70)
    
    client.close()
