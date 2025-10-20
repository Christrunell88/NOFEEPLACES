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

# PLG Apartment Listing Data
apartment_data = {
    "id": str(uuid.uuid4()),
    "title": "Luxury Studio at PLG - Unit 10N",
    "address": "123 Linden Blvd #10N",
    "neighborhood": "Prospect Lefferts Gardens",
    "borough": "Brooklyn",
    "location": {
        "type": "Point",
        "coordinates": [-73.9542, 40.6615]  # Approximate coordinates for PLG area
    },
    "price": 2631,  # Net effective rent
    "bedrooms": 0,  # Studio
    "bathrooms": 1,
    "sqft": None,  # Not specified in listing
    "floor": 10,
    "unit_number": "10N",
    "building_name": "PLG",
    "description": "PLG stands as a striking 26-story luxury rental building, offering a range of studio to three-bedroom residences in the heart of Prospect Lefferts Gardens. As the tallest building in the neighborhood, it boasts expansive, oversized windows in every home, flooding interiors with natural light and offering breathtaking views of Prospect Park, the New York City skyline, and beyond. Each residence is designed with modern elegance, featuring Caesarstone quartz countertops, stainless steel appliances, in-home washers and dryers, spacious bathrooms, generous closets, and smart home technology, including keyless entry.",
    "amenities": [
        "Rooftop Swimming Pool",
        "Indoor Swimming Pool",
        "Outdoor BBQ Grills",
        "Resident Lounge",
        "Media Room",
        "State-of-the-Art Fitness Center",
        "Event Space",
        "TULU Service",
        "Outdoor Half-Basketball Court",
        "Dog Run",
        "Sauna",
        "Full-Time Doorman",
        "Garage",
        "In-Unit Washer/Dryer",
        "Dishwasher",
        "Microwave",
        "Smart Home Technology",
        "Keyless Entry",
        "Caesarstone Quartz Countertops",
        "Stainless Steel Appliances",
        "Oversized Windows",
        "Views of Prospect Park"
    ],
    "images": [
        "https://assets-img.nestiostatic.com/unit_photos/originals/49719869911d38d481a115c8bd8e7dc4.jpg",
        "https://assets-img.nestiostatic.com/unit_photos/originals/6d7e56e83cada076b148e9fa3f1bac11.jpg",
        "https://assets-img.nestiostatic.com/unit_photos/originals/a51e91a7864ee4b9fd979a226585a550.jpg",
        "https://assets-img.nestiostatic.com/unit_photos/originals/d4257d238f5407aa77f61b478abea91c.jpg"
    ],
    "contact_info": {
        "email": "placesfirm@gmail.com",
        "phone": "+1-646-408-8048",
        "broker_name": "NoFeePlaces LLC"
    },
    "broker_fee": "No Fee",
    "available": True,
    "available_date": "Immediately",
    "move_in_date": "Immediately",
    "lease_terms": "12 months minimum",
    "pet_policy": "Pets Allowed",
    "utilities": "Tenant pays electric and gas",
    "is_verified": True,
    "is_real": True,
    "verification_status": "Verified Real Listing - NoFeePlaces LLC",
    "data_source": "Moinian Properties",
    "source_url": "https://www.moinian.com/listings/123-linden-blvd-10n-brooklyn-ny/3075925/",
    "quality_score": 95,
    "featured": False,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "views": 0,
    "source_database": "nofeeplaces_database"
}

# Insert the apartment
try:
    # Check if listing already exists (by address and unit)
    existing = apartments_collection.find_one({
        "address": apartment_data["address"],
        "unit_number": apartment_data["unit_number"]
    })
    
    if existing:
        print(f"⚠️ Listing already exists: {apartment_data['address']} {apartment_data['unit_number']}")
        print(f"Existing ID: {existing.get('id')}")
        
        # Update the existing listing
        result = apartments_collection.update_one(
            {"_id": existing["_id"]},
            {"$set": apartment_data}
        )
        print(f"✅ Updated existing listing: {result.modified_count} document modified")
    else:
        # Insert new listing
        result = apartments_collection.insert_one(apartment_data)
        print(f"✅ Successfully added PLG listing!")
        print(f"   - Address: {apartment_data['address']}")
        print(f"   - Unit: {apartment_data['unit_number']}")
        print(f"   - Price: ${apartment_data['price']}/month")
        print(f"   - Bedrooms: Studio")
        print(f"   - Neighborhood: {apartment_data['neighborhood']}, {apartment_data['borough']}")
        print(f"   - Building: {apartment_data['building_name']}")
        print(f"   - Amenities: {len(apartment_data['amenities'])} amenities")
        print(f"   - Images: {len(apartment_data['images'])} images")
        print(f"   - Document ID: {result.inserted_id}")
    
    # Show total apartment count
    total_count = apartments_collection.count_documents({})
    print(f"\n📊 Total apartments in database: {total_count}")
    
except Exception as e:
    print(f"❌ Error adding listing: {str(e)}")
    sys.exit(1)

client.close()
print("\n✅ Database connection closed")
