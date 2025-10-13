#!/usr/bin/env python3
"""
Restructure Database by Property
Each property = unique combination of: Address + Size + Bathrooms + Price + Images
Remove duplicates and organize cleanly
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from collections import defaultdict
import uuid

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

# ACTUAL SCRAPED PRICES from Mercedes House website
MERCEDES_HOUSE_PROPERTIES = [
    {
        'address': '550 W 54th St, New York, NY 10019',
        'building_name': 'Mercedes House',
        'size': 'Studio',
        'bedrooms': 0,
        'bathrooms': 1.0,
        'price': 2500,  # Actual scraped
        'url': 'https://www.mercedeshouseny.com/studio'
    },
    {
        'address': '550 W 54th St, New York, NY 10019',
        'building_name': 'Mercedes House',
        'size': 'Studio',
        'bedrooms': 0,
        'bathrooms': 1.0,
        'price': 3548,  # Actual scraped
        'url': 'https://www.mercedeshouseny.com/studio'
    },
    {
        'address': '550 W 54th St, New York, NY 10019',
        'building_name': 'Mercedes House',
        'size': '1 Bedroom',
        'bedrooms': 1,
        'bathrooms': 1.0,
        'price': 2500,  # Actual scraped (rent-stabilized)
        'url': 'https://www.mercedeshouseny.com/one-bed'
    },
    {
        'address': '550 W 54th St, New York, NY 10019',
        'building_name': 'Mercedes House',
        'size': '1 Bedroom',
        'bedrooms': 1,
        'bathrooms': 1.0,
        'price': 5065,  # Actual scraped
        'url': 'https://www.mercedeshouseny.com/one-bed'
    },
    {
        'address': '550 W 54th St, New York, NY 10019',
        'building_name': 'Mercedes House',
        'size': '2 Bedroom',
        'bedrooms': 2,
        'bathrooms': 1.0,
        'price': 5585,  # Actual scraped
        'url': 'https://www.mercedeshouseny.com/two-bed'
    },
]

# Other buildings (need to scrape these too, but using existing data for now)
OTHER_PROPERTIES = [
    {
        'address': '23-01 44th Dr, Long Island City, NY 11101',
        'building_name': 'Court Square',
        'size': 'Studio',
        'bedrooms': 0,
        'bathrooms': 1.0,
        'price': 2850,  # From TFC.com (need to verify)
    },
    {
        'address': '23-01 44th Dr, Long Island City, NY 11101',
        'building_name': 'Court Square',
        'size': '1 Bedroom',
        'bedrooms': 1,
        'bathrooms': 1.0,
        'price': 3650,  # From TFC.com (need to verify)
    },
    {
        'address': '424 West End Avenue, New York, NY 10024',
        'building_name': 'West River House',
        'size': 'Studio',
        'bedrooms': 0,
        'bathrooms': 1.0,
        'price': 3995,  # From Manhattan Skyline (need to verify)
    },
    {
        'address': '424 West End Avenue, New York, NY 10024',
        'building_name': 'West River House',
        'size': '1 Bedroom',
        'bedrooms': 1,
        'bathrooms': 1.0,
        'price': 5450,  # From Manhattan Skyline (need to verify)
    },
    {
        'address': '424 West End Avenue, New York, NY 10024',
        'building_name': 'West River House',
        'size': '2 Bedroom',
        'bedrooms': 2,
        'bathrooms': 2.0,
        'price': 8995,  # From Manhattan Skyline (need to verify)
    },
]


async def restructure_database():
    """Restructure database with clean property listings"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n" + "="*70)
    print("🏢 RESTRUCTURING DATABASE BY PROPERTY")
    print("="*70)
    
    # Get all current apartments and their images
    current_apartments = await db.apartments.find({}).to_list(length=None)
    
    print(f"\nCurrent apartments: {len(current_apartments)}")
    
    # Collect images by building
    images_by_building = defaultdict(list)
    for apt in current_apartments:
        building = apt.get('building_address', '')
        images = apt.get('images', [])
        if images:
            images_by_building[building].extend(images)
    
    # Deduplicate images
    for building in images_by_building:
        images_by_building[building] = list(set(images_by_building[building]))
    
    print("\nImages collected by building:")
    for building, imgs in images_by_building.items():
        print(f"  {building[:50]}: {len(imgs)} images")
    
    # Clear database
    print("\n🗑️  Clearing existing apartments...")
    result = await db.apartments.delete_many({})
    print(f"   Deleted {result.deleted_count} old entries")
    
    # Create clean property listings
    print("\n✨ Creating clean property listings...")
    
    all_properties = MERCEDES_HOUSE_PROPERTIES + OTHER_PROPERTIES
    
    for prop in all_properties:
        # Get images for this building
        building_images = images_by_building.get(prop['address'], [])
        
        # Create clean listing
        listing = {
            'id': str(uuid.uuid4()),
            'building_address': prop['address'],
            'building_name': prop.get('building_name', ''),
            'neighborhood': 'Hell\'s Kitchen' if 'W 54th' in prop['address'] else
                           'Long Island City' if 'Long Island City' in prop['address'] else
                           'Upper West Side',
            'borough': 'Manhattan' if 'Manhattan' in prop['address'] or 'W 54th' in prop['address'] or 'West End' in prop['address'] else 'Queens',
            'size': prop['size'],
            'bedrooms': prop['bedrooms'],
            'bathrooms': prop['bathrooms'],
            'price': float(prop['price']),
            'images': building_images[:10],  # Limit 10 images per listing
            'title': f"{prop['size']} at {prop.get('building_name', 'Building')}",
            'url': prop.get('url', ''),
            'source': 'Mercedes House NYC' if 'W 54th' in prop['address'] else
                     'TF Cornerstone' if 'Court Square' in prop.get('building_name', '') else
                     'Manhattan Skyline Buildings',
            'available': True,
            'broker_fee': 'No fee',
            'contact_email': 'placesfirm@gmail.com',
            'contact_phone': '+1-646-408-8048',
            'featured': prop['price'] <= 3500,  # Feature affordable units
            'priority': 10 if prop['price'] <= 3000 else 5,
            'sqft': None,  # Need to scrape
            'amenities': [],  # Need to scrape
        }
        
        await db.apartments.insert_one(listing)
        
        print(f"  ✓ {prop['address'][:45]}")
        print(f"    {prop['size']} | {prop['bathrooms']} bath | ${prop['price']:,}/mo | {len(listing['images'])} images")
    
    # Verify
    print("\n" + "="*70)
    print("📊 FINAL DATABASE STRUCTURE")
    print("="*70)
    
    final_apartments = await db.apartments.find({}).sort('price', 1).to_list(length=None)
    
    print(f"\nTotal Properties: {len(final_apartments)}\n")
    
    # Group by building
    by_building = defaultdict(list)
    for apt in final_apartments:
        by_building[apt['building_address']].append(apt)
    
    for building, units in sorted(by_building.items()):
        print(f"\n🏢 {building}")
        print(f"   Building: {units[0].get('building_name', 'N/A')}")
        print(f"   Total Units: {len(units)}")
        print(f"   Total Images: {sum(len(u['images']) for u in units)}")
        print(f"   Properties:")
        for unit in sorted(units, key=lambda x: x['price']):
            print(f"      • {unit['size']} | {unit['bathrooms']} bath | ${unit['price']:,.0f}/mo")
    
    print(f"\n✅ Database restructured: {len(final_apartments)} unique properties")
    
    client.close()
    
    return final_apartments


if __name__ == "__main__":
    asyncio.run(restructure_database())
