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

# The Aria Studio Apartments Data (from liveatarianyc.com)
# IMPORTANT: The Aria is at 90-100 John Street, Financial District, Manhattan
# This is DIFFERENT from the 123 Linden Blvd Brooklyn listing

aria_studios = [
    {
        "id": str(uuid.uuid4()),
        "title": "Luxury Studio at The Aria - Unit 1408",
        "address": "90-100 John Street #1408",
        "neighborhood": "Financial District",
        "borough": "Manhattan",
        "location": {
            "type": "Point",
            "coordinates": [-74.0060, 40.7080]  # Financial District coordinates
        },
        "price": 5135,
        "bedrooms": 0,  # Studio
        "bathrooms": 1,
        "sqft": None,
        "floor": 14,
        "unit_number": "1408",
        "building_name": "The Aria",
        "description": "Discover ARIA—luxury apartments in the heart of Manhattan's Financial District. Thoughtfully designed homes, premium amenities, and a lifestyle unlike any other. ARIA blends the authenticity of historic conversion with modern-day luxury, creating a one-of-a-kind residential experience. From sunrise views over the skyline to quiet evenings in your refined retreat, ARIA offers a home that inspires with modern kitchens featuring sleek quartz countertops, in-unit washer/dryer, and expansive layouts with high ceilings.",
        "amenities": [
            "24/7 Doorman & Concierge",
            "Resident Lounge",
            "In-Unit Washer/Dryer",
            "On-Site Laundry Facilities",
            "Valet Services",
            "Modern Kitchen",
            "Quartz Countertops",
            "Stainless Steel Appliances",
            "High Ceilings",
            "Dishwasher",
            "Microwave",
            "Historic Building Conversion",
            "Elevator Building",
            "Package Service",
            "Central Air Conditioning",
            "Hardwood Floors"
        ],
        "images": [
            "https://resource.rentcafe.com/image/upload/q_auto,f_auto,c_limit,w_1920/s3/2/206960/1.jpg",
            "https://resource.rentcafe.com/image/upload/q_auto,f_auto,c_limit,w_1920/s3/2/206960/2.jpg",
            "https://resource.rentcafe.com/image/upload/q_auto,f_auto,c_limit,w_1920/s3/2/206960/3.jpg",
            "https://resource.rentcafe.com/image/upload/q_auto,f_auto,c_limit,w_1920/s3/2/206960/90john-510-kitchen1_final%20(1)%20copy%20(2).jpg",
            "https://resource.rentcafe.com/image/upload/q_auto,f_auto,c_limit,w_1920/s3/2/206960/john-608-studio2%20final%20cc1%20(1)%20copy%20(1).jpg",
            "https://resource.rentcafe.com/image/upload/q_auto,f_auto,c_limit,w_1920/s3/2/206960/6.jpg"
        ],
        "contact_info": {
            "email": "placesfirm@gmail.com",
            "phone": "+1-917-727-5250",
            "broker_name": "The Aria Leasing"
        },
        "broker_fee": "No Fee",
        "available": True,
        "available_date": "Immediately",
        "move_in_date": "Immediately",
        "lease_terms": "12 months minimum",
        "pet_policy": "Pets Allowed - Pet-Friendly Building",
        "utilities": "Tenant pays electric and gas",
        "is_verified": True,
        "is_real": True,
        "verification_status": "Verified Real Listing - NoFeePlaces LLC",
        "data_source": "The Aria Official Website",
        "source_url": "https://www.liveatarianyc.com/",
        "quality_score": 98,
        "featured": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "views": 0,
        "source_database": "nofeeplaces_database"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Luxury Studio at The Aria - Unit 1604",
        "address": "90-100 John Street #1604",
        "neighborhood": "Financial District",
        "borough": "Manhattan",
        "location": {
            "type": "Point",
            "coordinates": [-74.0060, 40.7080]
        },
        "price": 5082,
        "bedrooms": 0,
        "bathrooms": 1,
        "sqft": None,
        "floor": 16,
        "unit_number": "1604",
        "building_name": "The Aria",
        "description": "Discover ARIA—luxury apartments in the heart of Manhattan's Financial District. Thoughtfully designed homes, premium amenities, and a lifestyle unlike any other. ARIA blends the authenticity of historic conversion with modern-day luxury, creating a one-of-a-kind residential experience. From sunrise views over the skyline to quiet evenings in your refined retreat, ARIA offers a home that inspires with modern kitchens featuring sleek quartz countertops, in-unit washer/dryer, and expansive layouts with high ceilings.",
        "amenities": [
            "24/7 Doorman & Concierge",
            "Resident Lounge",
            "In-Unit Washer/Dryer",
            "On-Site Laundry Facilities",
            "Valet Services",
            "Modern Kitchen",
            "Quartz Countertops",
            "Stainless Steel Appliances",
            "High Ceilings",
            "Dishwasher",
            "Microwave",
            "Historic Building Conversion",
            "Elevator Building",
            "Package Service",
            "Central Air Conditioning",
            "Hardwood Floors"
        ],
        "images": [
            "https://resource.rentcafe.com/image/upload/q_auto,f_auto,c_limit,w_1920/s3/2/206960/1.jpg",
            "https://resource.rentcafe.com/image/upload/q_auto,f_auto,c_limit,w_1920/s3/2/206960/2.jpg",
            "https://resource.rentcafe.com/image/upload/q_auto,f_auto,c_limit,w_1920/s3/2/206960/3.jpg",
            "https://resource.rentcafe.com/image/upload/q_auto,f_auto,c_limit,w_1920/s3/2/206960/90john-510-kitchen1_final%20(1)%20copy%20(2).jpg",
            "https://resource.rentcafe.com/image/upload/q_auto,f_auto,c_limit,w_1920/s3/2/206960/john-608-studio2%20final%20cc1%20(1)%20copy%20(1).jpg",
            "https://resource.rentcafe.com/image/upload/q_auto,f_auto,c_limit,w_1920/s3/2/206960/6.jpg"
        ],
        "contact_info": {
            "email": "placesfirm@gmail.com",
            "phone": "+1-917-727-5250",
            "broker_name": "The Aria Leasing"
        },
        "broker_fee": "No Fee",
        "available": True,
        "available_date": "Immediately",
        "move_in_date": "Immediately",
        "lease_terms": "12 months minimum",
        "pet_policy": "Pets Allowed - Pet-Friendly Building",
        "utilities": "Tenant pays electric and gas",
        "is_verified": True,
        "is_real": True,
        "verification_status": "Verified Real Listing - NoFeePlaces LLC",
        "data_source": "The Aria Official Website",
        "source_url": "https://www.liveatarianyc.com/",
        "quality_score": 98,
        "featured": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "views": 0,
        "source_database": "nofeeplaces_database"
    }
]

# Also need to FIX the Brooklyn listing - change it back to PLG
print("=" * 60)
print("CORRECTING DATABASE:")
print("=" * 60)

# Fix: Change The Aria back to PLG for the Brooklyn listing
brooklyn_listing = apartments_collection.find_one({'address': {'$regex': '123 Linden'}})
if brooklyn_listing:
    apartments_collection.update_one(
        {'_id': brooklyn_listing['_id']},
        {'$set': {
            'building_name': 'PLG',
            'title': 'Luxury Studio at PLG - Unit 10N',
            'updated_at': datetime.utcnow()
        }}
    )
    print(f"✅ Fixed Brooklyn listing: Changed back to 'PLG' at 123 Linden Blvd, Brooklyn")

print("\n" + "=" * 60)
print("ADDING THE ARIA STUDIOS (Manhattan Financial District):")
print("=" * 60)

# Insert The Aria studios
for idx, studio in enumerate(aria_studios, 1):
    # Check if already exists
    existing = apartments_collection.find_one({
        "address": studio["address"],
        "unit_number": studio["unit_number"]
    })
    
    if existing:
        print(f"\n⚠️ Studio #{idx} already exists: {studio['address']}")
        # Update it
        apartments_collection.update_one(
            {"_id": existing["_id"]},
            {"$set": studio}
        )
        print(f"   ✅ Updated existing listing")
    else:
        result = apartments_collection.insert_one(studio)
        print(f"\n✅ Studio #{idx} Added Successfully!")
        print(f"   - Address: {studio['address']}")
        print(f"   - Unit: {studio['unit_number']}")
        print(f"   - Floor: {studio['floor']}")
        print(f"   - Price: ${studio['price']}/month (No Fee)")
        print(f"   - Building: {studio['building_name']}")
        print(f"   - Neighborhood: {studio['neighborhood']}, {studio['borough']}")
        print(f"   - Amenities: {len(studio['amenities'])} luxury amenities")
        print(f"   - Images: {len(studio['images'])} professional photos")

# Show summary
total_count = apartments_collection.count_documents({})
aria_count = apartments_collection.count_documents({"building_name": "The Aria"})
plg_count = apartments_collection.count_documents({"building_name": "PLG"})

print("\n" + "=" * 60)
print("DATABASE SUMMARY:")
print("=" * 60)
print(f"📊 Total apartments: {total_count}")
print(f"🏢 The Aria (Manhattan FiDi): {aria_count} studios")
print(f"🏢 PLG (Brooklyn): {plg_count} unit(s)")
print("=" * 60)

client.close()
print("\n✅ Database operations completed successfully!")
