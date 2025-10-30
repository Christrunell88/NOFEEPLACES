#!/usr/bin/env python3
"""
Add New Unit to Existing Building
Makes it easy to add apartments to pre-existing buildings
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

def list_buildings(search_term=None):
    """List all buildings, optionally filtered by search term"""
    query = {}
    if search_term:
        query = {
            '$or': [
                {'building_name': {'$regex': search_term, '$options': 'i'}},
                {'address': {'$regex': search_term, '$options': 'i'}},
                {'neighborhood': {'$regex': search_term, '$options': 'i'}}
            ]
        }
    
    buildings = list(buildings_collection.find(query).sort('building_name', 1))
    
    print("=" * 70)
    print(f"AVAILABLE BUILDINGS{' (filtered)' if search_term else ''}")
    print("=" * 70)
    
    for i, building in enumerate(buildings, 1):
        print(f"\n{i}. {building['building_name']}")
        print(f"   ID: {building['building_id']}")
        print(f"   Address: {building['address']}")
        print(f"   {building['neighborhood']}, {building['borough']}")
        print(f"   Units: {building['available_units']} available / {building['total_units']} total")
        print(f"   Price range: ${building['price_range']['min']:,.0f} - ${building['price_range']['max']:,.0f}")
        print(f"   Bedroom types: {building['bedroom_types']}")
    
    print(f"\nTotal: {len(buildings)} buildings")
    return buildings

def add_unit_to_building(building_id, unit_data):
    """Add a new unit to an existing building"""
    
    # Verify building exists
    building = buildings_collection.find_one({'building_id': building_id})
    if not building:
        print(f"❌ Building {building_id} not found!")
        return False
    
    print(f"\n🏢 Adding unit to: {building['building_name']}")
    print(f"   Address: {building['address']}")
    
    # Create apartment document
    apartment_data = {
        'id': str(uuid.uuid4()),
        'building_id': building_id,
        'building_name': building['building_name'],
        'address': building['address'],
        'neighborhood': building['neighborhood'],
        'borough': building['borough'],
        **unit_data,  # User-provided unit-specific data
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'available': True
    }
    
    # Insert apartment
    result = apartments_collection.insert_one(apartment_data)
    
    # Update building stats
    all_units = list(apartments_collection.find({'building_id': building_id}))
    available_units = [u for u in all_units if u.get('available', True)]
    all_prices = [u['price'] for u in all_units if u.get('price')]
    
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
            'bedroom_types': list(set([u.get('bedrooms') for u in all_units if u.get('bedrooms') is not None])),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }}
    )
    
    print(f"\n✅ Unit added successfully!")
    print(f"   Unit ID: {apartment_data['id']}")
    print(f"   Unit Number: {unit_data.get('unit_number', 'N/A')}")
    print(f"   Price: ${unit_data.get('price', 0):,.0f}/mo")
    print(f"   Bedrooms: {unit_data.get('bedrooms', 0)}")
    print(f"\n📊 Updated building stats:")
    print(f"   Total units: {len(all_units)}")
    print(f"   Available units: {len(available_units)}")
    
    client.close()
    return True

def interactive_add_unit():
    """Interactive mode for adding a unit"""
    print("=" * 70)
    print("ADD NEW UNIT TO EXISTING BUILDING")
    print("=" * 70)
    
    # Search for building
    search = input("\nSearch for building (name/address/neighborhood): ").strip()
    buildings = list_buildings(search if search else None)
    
    if not buildings:
        print("No buildings found!")
        return
    
    # Select building
    selection = input(f"\nSelect building number (1-{len(buildings)}) or 'q' to quit: ").strip()
    if selection.lower() == 'q':
        return
    
    try:
        idx = int(selection) - 1
        if idx < 0 or idx >= len(buildings):
            print("Invalid selection!")
            return
        
        building = buildings[idx]
    except ValueError:
        print("Invalid input!")
        return
    
    # Get unit details
    print(f"\n📝 Enter unit details for {building['building_name']}:")
    
    unit_data = {}
    
    unit_data['unit_number'] = input("Unit Number (e.g., 2A, 1405): ").strip()
    unit_data['title'] = input(f"Title (default: '{unit_data['unit_number']}BR at {building['building_name']}'): ").strip()
    
    if not unit_data['title']:
        bedrooms = input("Bedrooms (0 for studio): ").strip()
        unit_data['bedrooms'] = int(bedrooms) if bedrooms else 1
        unit_data['title'] = f"{unit_data['bedrooms']}BR at {building['building_name']}"
    else:
        bedrooms = input("Bedrooms (0 for studio): ").strip()
        unit_data['bedrooms'] = int(bedrooms) if bedrooms else 1
    
    unit_data['bathrooms'] = float(input("Bathrooms: ").strip() or "1")
    unit_data['price'] = float(input("Price (monthly rent): ").strip() or "0")
    unit_data['sqft'] = int(input("Square feet (optional): ").strip() or "0") or None
    
    description = input("Description (optional): ").strip()
    if description:
        unit_data['description'] = description
    else:
        unit_data['description'] = f"Unit {unit_data['unit_number']} at {building['building_name']}"
    
    # Amenities (inherit from building)
    unit_data['amenities'] = building.get('amenities', [])
    
    # Images
    print("\nImage URLs (comma-separated, or press Enter to skip): ")
    images_input = input().strip()
    if images_input:
        unit_data['images'] = [img.strip() for img in images_input.split(',')]
    else:
        unit_data['images'] = []
    
    # Contact info
    unit_data['contact_email'] = 'placesfirm@gmail.com'
    unit_data['contact_phone'] = '+1-646-408-8048'
    
    # Additional fields
    unit_data['featured'] = False
    unit_data['is_verified'] = True
    unit_data['priority'] = 5
    
    # Confirm
    print("\n" + "=" * 70)
    print("CONFIRM NEW UNIT:")
    print("=" * 70)
    print(f"Building: {building['building_name']}")
    print(f"Unit Number: {unit_data['unit_number']}")
    print(f"Title: {unit_data['title']}")
    print(f"Price: ${unit_data['price']:,.0f}/mo")
    print(f"Bedrooms: {unit_data['bedrooms']} | Bathrooms: {unit_data['bathrooms']}")
    if unit_data['sqft']:
        print(f"Square feet: {unit_data['sqft']}")
    
    confirm = input("\nAdd this unit? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        add_unit_to_building(building['building_id'], unit_data)
    else:
        print("Cancelled.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        # List mode
        search_term = sys.argv[2] if len(sys.argv) > 2 else None
        list_buildings(search_term)
    else:
        # Interactive mode
        interactive_add_unit()
    
    client.close()
