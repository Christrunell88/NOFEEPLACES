#!/usr/bin/env python3
"""
Database Reorganization Script - Building-Centric Structure
Creates a buildings collection and reorganizes apartments to reference buildings
"""
import os
import uuid
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime, timezone

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_database')
client = MongoClient(MONGO_URL)
db = client["nofeeplaces_database"]
apartments_collection = db['apartments']
buildings_collection = db['buildings']

def reorganize_database(dry_run=True):
    """
    Reorganize database into building-centric structure
    """
    
    print("=" * 70)
    print(f"DATABASE REORGANIZATION - Building-Centric Structure")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will create buildings)'}")
    print("=" * 70)
    
    # Group apartments by building
    buildings_data = defaultdict(lambda: {
        'units': [],
        'amenities': set(),
        'images': [],
        'neighborhoods': set(),
        'boroughs': set(),
        'building_names': set()
    })
    
    apartments = list(apartments_collection.find())
    
    # Group by address (primary key for building)
    for apt in apartments:
        address = apt.get('address') or apt.get('location', 'Unknown Address')
        
        # Clean up address
        if not address or address == 'Unknown Address' or address == '':
            # Use neighborhood as fallback
            neighborhood = apt.get('neighborhood', 'Unknown')
            borough = apt.get('borough', 'Unknown')
            address = f"{neighborhood}, {borough}"
        
        buildings_data[address]['units'].append(apt)
        buildings_data[address]['neighborhoods'].add(apt.get('neighborhood', 'Unknown'))
        buildings_data[address]['boroughs'].add(apt.get('borough', 'Unknown'))
        
        # Collect building-level data
        if apt.get('building_name'):
            buildings_data[address]['building_names'].add(apt.get('building_name'))
        
        # Collect amenities (unique across all units)
        if apt.get('amenities'):
            for amenity in apt['amenities']:
                buildings_data[address]['amenities'].add(amenity)
        
        # Collect images (prefer unit images, but include building exteriors)
        if apt.get('images'):
            buildings_data[address]['images'].extend(apt['images'])
    
    print(f"\n📊 Analysis:")
    print(f"Total apartments: {len(apartments)}")
    print(f"Buildings identified: {len(buildings_data)}")
    
    # Create buildings
    buildings_created = []
    
    for address, data in buildings_data.items():
        # Determine building name
        if data['building_names']:
            building_name = list(data['building_names'])[0]
        else:
            # Use address as name
            building_name = address.split(',')[0] if ',' in address else address
        
        # Calculate stats
        available_units = [u for u in data['units'] if u.get('available', True)]
        all_prices = [u['price'] for u in data['units'] if u.get('price')]
        
        building_doc = {
            'building_id': str(uuid.uuid4()),
            'building_name': building_name,
            'address': address,
            'neighborhood': list(data['neighborhoods'])[0] if data['neighborhoods'] else 'Unknown',
            'borough': list(data['boroughs'])[0] if data['boroughs'] else 'Unknown',
            'amenities': list(data['amenities']),
            'images': list(set(data['images']))[:5],  # Keep up to 5 unique images
            'total_units': len(data['units']),
            'available_units': len(available_units),
            'price_range': {
                'min': min(all_prices) if all_prices else 0,
                'max': max(all_prices) if all_prices else 0,
                'avg': sum(all_prices) / len(all_prices) if all_prices else 0
            },
            'bedroom_types': list(set([u.get('bedrooms') for u in data['units'] if u.get('bedrooms') is not None])),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        buildings_created.append(building_doc)
        
        print(f"\n🏢 {building_name}")
        print(f"   Address: {address}")
        print(f"   Units: {building_doc['available_units']} available / {building_doc['total_units']} total")
        print(f"   Price: ${building_doc['price_range']['min']:,.0f} - ${building_doc['price_range']['max']:,.0f}")
        print(f"   Bedroom types: {building_doc['bedroom_types']}")
    
    if not dry_run:
        print("\n⚠️  CREATING BUILDINGS COLLECTION...")
        
        # Drop existing buildings collection
        buildings_collection.drop()
        
        # Insert buildings
        if buildings_created:
            result = buildings_collection.insert_many(buildings_created)
            print(f"✅ Created {len(result.inserted_ids)} buildings")
        
        # Update apartments with building_id reference
        print("\n⚠️  UPDATING APARTMENTS WITH BUILDING REFERENCES...")
        
        updated_count = 0
        for building in buildings_created:
            address = building['address']
            building_id = building['building_id']
            
            # Update all apartments at this address
            result = apartments_collection.update_many(
                {'$or': [
                    {'address': address},
                    {'location': address}
                ]},
                {'$set': {
                    'building_id': building_id,
                    'building_name': building['building_name']
                }}
            )
            updated_count += result.modified_count
        
        print(f"✅ Updated {updated_count} apartments with building references")
        
        # Create indexes
        print("\n⚠️  CREATING DATABASE INDEXES...")
        buildings_collection.create_index('building_id', unique=True)
        buildings_collection.create_index('address')
        buildings_collection.create_index('neighborhood')
        apartments_collection.create_index('building_id')
        print("✅ Indexes created")
        
    else:
        print("\n💡 This was a DRY RUN. No changes made.")
        print("   Run with dry_run=False to apply changes.")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Buildings to create: {len(buildings_created)}")
    print(f"Apartments to update: {len(apartments)}")
    print(f"\nNew collections:")
    print(f"  - buildings: {len(buildings_created)} documents")
    print(f"  - apartments: {len(apartments)} documents (with building_id references)")
    
    client.close()
    return buildings_created

if __name__ == "__main__":
    import sys
    
    dry_run = sys.argv[1].lower() != 'false' if len(sys.argv) > 1 else True
    reorganize_database(dry_run=dry_run)
