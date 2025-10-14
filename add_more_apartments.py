#!/usr/bin/env python3
"""
Add multiple diverse apartment listings to NoFeePlaces database
"""

import asyncio
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/nofeeplaces_db")
DB_NAME = os.getenv("DB_NAME", "nofeeplaces_database")

# Additional apartment listings from various NYC neighborhoods
APARTMENTS = [
    {
        "title": "Sunny 1BR in Murray Hill - Walk to Grand Central",
        "address": "140 East 34th Street, New York, NY 10016",
        "location": "140 East 34th Street, Murray Hill, Manhattan",
        "neighborhood": "Murray Hill",
        "borough": "Manhattan",
        "price": 4200,
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": 650,
        "description": "Bright one bedroom apartment featuring oversized windows, hardwood floors, and a renovated kitchen with stainless steel appliances. Located in a full-service building with 24/7 doorman, fitness center, and rooftop terrace. Just steps from Grand Central and multiple subway lines.",
        "amenities": ["24/7 Doorman", "Fitness Center", "Rooftop Terrace", "Elevator", "Laundry in Building", "Package Room"],
        "building_name": "Murray Hill Tower",
        "utilities_included": ["Heat", "Hot Water"],
        "images": [
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=600&fit=crop"
        ],
        "unit_features": ["Hardwood Floors", "Oversized Windows", "Renovated Kitchen", "Stainless Steel Appliances", "High Ceilings"],
        "transportation": ["4, 5, 6, 7, S Trains - Grand Central (3 min walk)", "N, Q, R, W Trains - 34th St Herald Sq (8 min walk)"],
        "contact_phone": "(212) 555-0199",
        "priority": 2
    },
    {
        "title": "Spacious 2BR/2BA in Upper East Side - Pre-War Charm",
        "address": "1245 Lexington Avenue, New York, NY 10028",
        "location": "1245 Lexington Avenue, Upper East Side, Manhattan",
        "neighborhood": "Upper East Side",
        "borough": "Manhattan", 
        "price": 5800,
        "bedrooms": 2,
        "bathrooms": 2,
        "sqft": 1100,
        "description": "Elegant pre-war two bedroom with original details including crown molding, hardwood floors, and decorative fireplace. Master bedroom with en-suite bathroom and walk-in closet. Located on tree-lined street near Central Park and Museum Mile.",
        "amenities": ["Doorman", "Elevator", "Storage Available", "Bike Room", "Courtyard Garden", "Pet Friendly"],
        "building_name": "The Lexington",
        "utilities_included": ["Heat", "Hot Water", "Gas"],
        "images": [
            "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop"
        ],
        "unit_features": ["Pre-War Details", "Crown Molding", "Decorative Fireplace", "Walk-in Closet", "En-suite Master Bath", "Tree-lined Street"],
        "transportation": ["4, 5, 6 Trains - 86th St (2 min walk)", "Q Train - 86th St (4 min walk)"],
        "contact_phone": "(212) 555-0288",
        "priority": 1
    },
    {
        "title": "Modern Studio in Hell's Kitchen - Theater District",
        "address": "455 West 42nd Street, New York, NY 10036",
        "location": "455 West 42nd Street, Hell's Kitchen, Manhattan",
        "neighborhood": "Hell's Kitchen",
        "borough": "Manhattan",
        "price": 3200,
        "bedrooms": "Studio",
        "bathrooms": 1,
        "sqft": 450,
        "description": "Contemporary studio apartment in the heart of Hell's Kitchen with floor-to-ceiling windows, modern fixtures, and open layout. Building features concierge services and is surrounded by restaurants, theaters, and nightlife. Perfect for young professionals.",
        "amenities": ["Concierge", "Fitness Center", "Roof Deck", "Package Room", "Elevator", "Laundry in Building"],
        "building_name": "Theater District Residences",
        "utilities_included": ["Heat", "Hot Water"],
        "images": [
            "https://images.unsplash.com/photo-1560449752-270fa7881c71?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1574362848149-11496d93a7c7?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1556020685-ae41abfc9365?w=800&h=600&fit=crop"
        ],
        "unit_features": ["Floor-to-Ceiling Windows", "Modern Fixtures", "Open Layout", "City Views", "Hardwood Floors"],
        "transportation": ["A, C, E Trains - 42nd St Port Authority (3 min walk)", "N, Q, R, W, S, 1, 2, 3, 7 Trains - Times Sq (5 min walk)"],
        "contact_phone": "(212) 555-0377",
        "priority": 3
    },
    {
        "title": "Luxury 1BR in Financial District - Harbor Views",
        "address": "85 Broad Street, New York, NY 10004",
        "location": "85 Broad Street, Financial District, Manhattan",
        "neighborhood": "Financial District",
        "borough": "Manhattan",
        "price": 4800,
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": 750,
        "description": "Stunning one bedroom with floor-to-ceiling windows and breathtaking harbor views. Features gourmet kitchen with granite countertops, spa-like bathroom with soaking tub, and in-unit washer/dryer. Luxury building with full amenities package.",
        "amenities": ["24/7 Concierge", "Fitness Center", "Pool", "Roof Deck", "Business Center", "Valet Parking", "Pet Spa"],
        "building_name": "Harbor Point Tower",
        "utilities_included": ["Heat", "Hot Water", "Air Conditioning"],
        "images": [
            "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1567767292278-a4f21aa2d36e?w=800&h=600&fit=crop"
        ],
        "unit_features": ["Harbor Views", "Floor-to-Ceiling Windows", "Gourmet Kitchen", "Granite Countertops", "Soaking Tub", "In-Unit Laundry"],
        "transportation": ["R, W Trains - Whitehall St (2 min walk)", "1 Train - South Ferry (3 min walk)", "4, 5 Trains - Bowling Green (4 min walk)"],
        "contact_phone": "(212) 555-0455",
        "priority": 1
    },
    {
        "title": "Charming 1BR in West Village - Historic Brownstone",
        "address": "75 Jane Street, New York, NY 10014",
        "location": "75 Jane Street, West Village, Manhattan", 
        "neighborhood": "West Village",
        "borough": "Manhattan",
        "price": 5200,
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": 600,
        "description": "Quaint one bedroom in a historic West Village brownstone featuring exposed brick walls, original hardwood floors, and a working fireplace. High ceilings and south-facing windows provide abundant natural light. Located on a quiet, tree-lined street.",
        "amenities": ["Historic Building", "Garden Access", "Bike Storage", "Pet Friendly"],
        "building_name": "Jane Street Brownstone",
        "utilities_included": ["Heat", "Hot Water"],
        "images": [
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&h=600&fit=crop"
        ],
        "unit_features": ["Exposed Brick Walls", "Working Fireplace", "High Ceilings", "South-Facing Windows", "Historic Details", "Quiet Street"],
        "transportation": ["A, C, E Trains - 14th St (5 min walk)", "1, 2, 3 Trains - 14th St (7 min walk)", "L Train - 8th Ave (8 min walk)"],
        "contact_phone": "(212) 555-0566",
        "priority": 2
    }
]

async def add_apartments():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    apartments_collection = db.apartments
    
    added_count = 0
    
    for apt_data in APARTMENTS:
        try:
            # Add common fields to each apartment
            apartment = {
                **apt_data,
                "id": str(uuid.uuid4()),
                "available_date": datetime.now(timezone.utc).isoformat(),
                "contact_email": "leasing@nofeeplaces.com",
                "broker_fee": False,
                "no_fee": True,
                "featured": apt_data.get("priority", 3) <= 2,
                "source": "NoFeePlaces Curated",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Insert apartment
            result = await apartments_collection.insert_one(apartment)
            added_count += 1
            
            print(f"✅ Added: {apartment['title']}")
            print(f"   📍 {apartment['neighborhood']} - ${apartment['price']}/month")
            print(f"   🏠 {apartment['bedrooms']}BR, {apartment['bathrooms']}BA")
            print(f"   🆔 {apartment['id']}")
            print("")
            
        except Exception as e:
            print(f"❌ Error adding {apt_data['title']}: {e}")
    
    # Check total count
    total_count = await apartments_collection.count_documents({})
    
    print(f"\n🎉 Successfully added {added_count} new apartments!")
    print(f"📊 Total apartments in database: {total_count}")
    
    client.close()
    return added_count

if __name__ == "__main__":
    asyncio.run(add_apartments())