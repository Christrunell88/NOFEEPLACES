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

# Simple studio apartment images
studio_images = [
    "https://images.unsplash.com/photo-1633505765486-e404bbbec654?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBzdHVkaW8lMjBhcGFydG1lbnQlMjBpbnRlcmlvcnxlbnwwfHx8fDE3NjA5OTYwNzh8MA&ixlib=rb-4.1.0&q=85",
    "https://images.unsplash.com/photo-1610123172763-1f587473048f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwyfHxtb2Rlcm4lMjBzdHVkaW8lMjBhcGFydG1lbnQlMjBpbnRlcmlvcnxlbnwwfHx8fDE3NjA5OTYwNzh8MA&ixlib=rb-4.1.0&q=85",
    "https://images.unsplash.com/photo-1745488018261-13afb4842790?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwzfHxtb2Rlcm4lMjBzdHVkaW8lMjBhcGFydG1lbnQlMjBpbnRlcmlvcnxlbnwwfHx8fDE3NjA5OTYwNzh8MA&ixlib=rb-4.1.0&q=85",
    "https://images.unsplash.com/photo-1698870157085-11632d2ddef8?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHw0fHxtb2Rlcm4lMjBzdHVkaW8lMjBhcGFydG1lbnQlMjBpbnRlcmlvcnxlbnwwfHx8fDE3NjA5OTYwNzh8MA&ixlib=rb-4.1.0&q=85",
    "https://images.pexels.com/photos/6373487/pexels-photo-6373487.jpeg",
    "https://images.pexels.com/photos/6044926/pexels-photo-6044926.jpeg"
]

# Two new Aria studios with prices between $5,082-$5,135
new_aria_studios = [
    {
        "id": str(uuid.uuid4()),
        "title": "Luxury Studio at The Aria - Unit 1208",
        "address": "90-100 John Street #1208",
        "neighborhood": "Financial District",
        "borough": "Manhattan",
        "location": {
            "type": "Point",
            "coordinates": [-74.0060, 40.7080]
        },
        "price": 5095,  # Between $5,082-$5,135
        "bedrooms": 0,
        "bathrooms": 1,
        "sqft": None,
        "floor": 12,
        "unit_number": "1208",
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
        "images": studio_images,
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
        "title": "Luxury Studio at The Aria - Unit 1508",
        "address": "90-100 John Street #1508",
        "neighborhood": "Financial District",
        "borough": "Manhattan",
        "location": {
            "type": "Point",
            "coordinates": [-74.0060, 40.7080]
        },
        "price": 5120,  # Between $5,082-$5,135
        "bedrooms": 0,
        "bathrooms": 1,
        "sqft": None,
        "floor": 15,
        "unit_number": "1508",
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
        "images": studio_images,
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

print("=" * 60)
print("ADDING 2 MORE ARIA STUDIOS:")
print("=" * 60)

# Insert the studios
for idx, studio in enumerate(new_aria_studios, 1):
    # Check if already exists
    existing = apartments_collection.find_one({
        "address": studio["address"],
        "unit_number": studio["unit_number"]
    })
    
    if existing:
        print(f"\n⚠️ Studio #{idx} already exists: {studio['address']}")
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
        print(f"   - Images: {len(studio['images'])} simple studio images")

# Show summary
total_count = apartments_collection.count_documents({})
aria_count = apartments_collection.count_documents({"building_name": "The Aria"})

print("\n" + "=" * 60)
print("DATABASE SUMMARY:")
print("=" * 60)
print(f"📊 Total apartments: {total_count}")
print(f"🏢 The Aria (Manhattan FiDi): {aria_count} studios")
print(f"\n💰 Price Range: $5,082 - $5,135/month")
print(f"📍 Location: 90-100 John Street, Financial District")
print("=" * 60)

client.close()
print("\n✅ Database operations completed successfully!")
