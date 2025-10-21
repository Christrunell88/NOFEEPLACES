import os
import sys
from pymongo import MongoClient
from datetime import datetime
import uuid

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
apartments_collection = db['apartments']

# The Greenpoint data from thegreenpoint.nyc
# Address: 21 India Street, Greenpoint, Brooklyn
# 40-story luxury high-rise on East River waterfront
# Pet-Friendly, 1 Month Free promotion

# All 21 available units
greenpoint_listings = [
    # STUDIOS (5 units)
    {
        "unit_number": "T.1107",
        "bedrooms": 0,
        "bathrooms": 1,
        "sqft": 492,
        "price": 3272,  # Net effective rent
        "floor": 11,
        "availability": "12/7/2025"
    },
    {
        "unit_number": "T.1707",
        "bedrooms": 0,
        "bathrooms": 1,
        "sqft": 492,
        "price": 3285,
        "floor": 17,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.2605",
        "bedrooms": 0,
        "bathrooms": 1,
        "sqft": 505,
        "price": 3597,
        "floor": 26,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.2705",
        "bedrooms": 0,
        "bathrooms": 1,
        "sqft": 505,
        "price": 3692,
        "floor": 27,
        "availability": "Immediately"
    },
    {
        "unit_number": "N.0311",
        "bedrooms": 0,
        "bathrooms": 1,
        "sqft": 577,
        "price": 3997,
        "floor": 3,
        "availability": "11/2/2025"
    },
    
    # 1 BEDROOMS (8 units)
    {
        "unit_number": "N.0504",
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": 660,
        "price": 4548,
        "floor": 5,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.1609",
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": 676,
        "price": 4843,
        "floor": 16,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.1909",
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": 676,
        "price": 5059,
        "floor": 19,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.2404",
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": 676,
        "price": 5070,
        "floor": 24,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.2504",
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": 676,
        "price": 5201,
        "floor": 25,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.2610",
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": 676,
        "price": 5346,
        "floor": 26,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.2009",
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": 676,
        "price": 5399,
        "floor": 20,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.2704",
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": 676,
        "price": 5467,
        "floor": 27,
        "availability": "Immediately"
    },
    
    # 2 BEDROOMS (8 units)
    {
        "unit_number": "T.1002",
        "bedrooms": 2,
        "bathrooms": 2,
        "sqft": 924,
        "price": 5787,
        "floor": 10,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.0404",
        "bedrooms": 2,
        "bathrooms": 2,
        "sqft": 991,
        "price": 5880,
        "floor": 4,
        "availability": "Immediately"
    },
    {
        "unit_number": "N.0501",
        "bedrooms": 2,
        "bathrooms": 2,
        "sqft": 967,
        "price": 6228,
        "floor": 5,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.2511",
        "bedrooms": 2,
        "bathrooms": 2,
        "sqft": 924,
        "price": 6327,
        "floor": 25,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.2012",
        "bedrooms": 2,
        "bathrooms": 2,
        "sqft": 922,
        "price": 6424,
        "floor": 20,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.2711",
        "bedrooms": 2,
        "bathrooms": 2,
        "sqft": 924,
        "price": 6481,
        "floor": 27,
        "availability": "Immediately"
    },
    {
        "unit_number": "S.0505",
        "bedrooms": 2,
        "bathrooms": 2,
        "sqft": 1014,
        "price": 6582,
        "floor": 5,
        "availability": "Immediately"
    },
    {
        "unit_number": "T.2602",
        "bedrooms": 2,
        "bathrooms": 2,
        "sqft": 924,
        "price": 6636,
        "floor": 26,
        "availability": "Immediately"
    }
]

# Common amenities for all units
common_amenities = [
    "24-Hour Attended Lobby",
    "24-Hour Onsite Parking Garage",
    "India St. Gym with Pelotons & Squat Racks",
    "Heron Basketball Court",
    "Sunset Yoga/Training Studio",
    "Co-Work Lounge",
    "The Hideaway Lounge & Pool Hall",
    "Children's Play Room",
    "The Grand Club Room",
    "The Greenpoint Gardens",
    "Sun Deck",
    "NYC Ferry Access",
    "Waterfront Porte Cochére",
    "Bicycle Storage",
    "On-site Community Laundry Rooms",
    "Stainless Steel Appliances",
    "Gas Cooktop",
    "Dishwasher",
    "White Stone Countertops",
    "Herringbone Tile Backsplash",
    "Bosch Washer and Dryer In-Unit",
    "Wide Plank Hardwood Flooring",
    "Floor-To-Ceiling Windows",
    "Manhattan Skyline Views",
    "Pet-Friendly Building"
]

# Simple modern apartment images
apartment_images = [
    "https://thegreenpoint.nyc/assets/images/cache/rotator_3_the_greenpoint_1588-0a011828fb19a00007702580bd9c25d8.jpg",
    "https://thegreenpoint.nyc/assets/images/cache/gallery_28_the_greenpoint_1588-9f83c2a3eb6479ed82b7af229db6b518.jpg",
    "https://thegreenpoint.nyc/assets/images/cache/gallery_22_the_greenpoint_1588-8fb0f9893314db78510a02742b21b662.jpg",
    "https://thegreenpoint.nyc/assets/images/cache/app-amen-26bed13e61d66648f43d2cef4351c62b.jpg"
]

print("=" * 70)
print("ADDING THE GREENPOINT APARTMENTS - BROOKLYN WATERFRONT")
print("=" * 70)

added_count = 0
updated_count = 0

for listing_data in greenpoint_listings:
    bedroom_type = "Studio" if listing_data["bedrooms"] == 0 else f"{listing_data['bedrooms']}BR"
    
    apartment = {
        "id": str(uuid.uuid4()),
        "title": f"{bedroom_type} at The Greenpoint - Unit {listing_data['unit_number']}",
        "address": f"21 India Street #{listing_data['unit_number']}",
        "neighborhood": "Greenpoint",
        "borough": "Brooklyn",
        "location": {
            "type": "Point",
            "coordinates": [-73.9569, 40.7340]  # Greenpoint waterfront coordinates
        },
        "price": listing_data["price"],
        "bedrooms": listing_data["bedrooms"],
        "bathrooms": listing_data["bathrooms"],
        "sqft": listing_data["sqft"],
        "floor": listing_data["floor"],
        "unit_number": listing_data["unit_number"],
        "building_name": "The Greenpoint",
        "description": "Elevate your lifestyle at The Greenpoint, Brooklyn's sensational luxury residences located on the East River waterfront. Our stunning 40-story high-rise community offers unparalleled views of the Manhattan Skyline. Each apartment boasts abundant natural light, breathtaking views, towering ceilings up to 11', and tasteful accents. Features include striking matte black fixtures, wide-plank hardwood flooring, gourmet kitchen with gas cooktop, stainless steel appliances, white stone countertops, herringbone tile backsplash, and Bosch washer/dryer. SPECIAL OFFER: 1 Month Free + Broker OP (Must apply by 10/31/25).",
        "amenities": common_amenities,
        "images": apartment_images,
        "contact_info": {
            "email": "placesfirm@gmail.com",
            "phone": "+1-646-408-8048",
            "broker_name": "The Greenpoint Leasing"
        },
        "broker_fee": "No Fee - Broker OP (1 Month Free Promotion)",
        "available": True,
        "available_date": listing_data["availability"],
        "move_in_date": listing_data["availability"],
        "lease_terms": "13 months (includes 1 month free)",
        "pet_policy": "Pets Allowed - Pet-Friendly Community",
        "utilities": "Tenant pays electric and gas",
        "is_verified": True,
        "is_real": True,
        "verification_status": "Verified Real Listing - NoFeePlaces LLC",
        "data_source": "The Greenpoint Official Website",
        "source_url": "https://thegreenpoint.nyc/",
        "quality_score": 97,
        "featured": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "views": 0,
        "source_database": "nofeeplaces_database"
    }
    
    # Check if already exists
    existing = apartments_collection.find_one({
        "address": apartment["address"],
        "unit_number": apartment["unit_number"]
    })
    
    if existing:
        apartments_collection.update_one(
            {"_id": existing["_id"]},
            {"$set": apartment}
        )
        updated_count += 1
        print(f"✅ Updated: Unit {listing_data['unit_number']} - {bedroom_type} - ${listing_data['price']}/mo")
    else:
        apartments_collection.insert_one(apartment)
        added_count += 1
        print(f"✅ Added: Unit {listing_data['unit_number']} - {bedroom_type} - ${listing_data['price']}/mo - Floor {listing_data['floor']}")

# Summary
total_count = apartments_collection.count_documents({})
greenpoint_count = apartments_collection.count_documents({"building_name": "The Greenpoint"})

print("\n" + "=" * 70)
print("GREENPOINT APARTMENTS SUMMARY:")
print("=" * 70)
print(f"📊 New listings added: {added_count}")
print(f"📊 Listings updated: {updated_count}")
print(f"🏢 The Greenpoint total units: {greenpoint_count}")
print(f"📊 Total apartments in database: {total_count}")
print(f"\n📍 Location: 21 India Street, Greenpoint, Brooklyn")
print(f"🏗️ Building: 40-story luxury waterfront high-rise")
print(f"💰 Price Range: $3,272 - $6,636/month (net effective)")
print(f"🎁 Special Offer: 1 Month Free + Broker OP")
print(f"🐾 Pet Policy: Pet-Friendly Community")
print(f"🎯 Amenities: {len(common_amenities)} luxury features")
print("=" * 70)

client.close()
print("\n✅ Database operations completed successfully!")
