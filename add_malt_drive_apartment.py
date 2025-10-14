#!/usr/bin/env python3
"""
Add Malt Drive apartment listing to NoFeePlaces database
"""

import asyncio
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/nofeeplaces_db")
DB_NAME = os.getenv("DB_NAME", "nofeeplaces_database")

async def add_malt_drive_apartment():
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    apartments_collection = db.apartments
    
    # Create apartment data based on extracted information
    apartment_data = {
        "id": str(uuid.uuid4()),
        "title": "Stunning Corner 1BR with Creek Views - Malt Drive",
        "address": "2-20 Malt Drive, Unit 3001, Long Island City, NY 11101",
        "location": "2-20 Malt Drive, Hunter's Point South, Long Island City, Queens",
        "neighborhood": "Hunter's Point South",
        "borough": "Queens",
        "price": 5820,
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": None,  # Not specified in listing
        "available_date": datetime.now(timezone.utc).isoformat(),
        "description": "Stunning Corner 1 Bed, 1 Bath Apartment featuring high ceilings, flexible windowed alcove, windowed kitchen, in-home washer/dryer, and northeast exposure overlooking The Creek and Long Island City and Brooklyn. Modern luxury living in Hunter's Point South.",
        "amenities": [
            "Rooftop Pool and Sundeck",
            "Fitness Center",
            "Resident Lounge", 
            "Dog Grooming Facility",
            "Club220 Amenity Space",
            "Concierge Services",
            "Package Room",
            "Bike Storage",
            "24/7 Security"
        ],
        "building_name": "Malt Drive Modern Apartments",
        "utilities_included": [
            "Heat",
            "Hot Water"
        ],
        "images": [
            "https://maltdrive.com/wp-content/uploads/2024/10/04-20240822_DSC6013-HDR-Edit_Malt-Dr_South-Tower_Aff_433-jpg.avif",
            "https://maltdrive.com/wp-content/uploads/2024/10/02-20240926_DSC9604-1_2-20-Malt-Dr_430-jpg.avif",
            "https://maltdrive.com/wp-content/uploads/2024/10/20240822_DSC6063-HDR-Edit_Malt-Dr_South-Tower_South-Tower_Aff_433-jpg.avif",
            "https://maltdrive.com/wp-content/uploads/2024/10/06-20240822_DSC6073-HDR-Edit_Malt-Dr_South-Tower_South-Tower_Aff_433-jpg.avif",
            "https://maltdrive.com/wp-content/uploads/2024/10/20240909_DSC7731-Edit_2-20-Malt-Dr_425_Bathroom-jpg.avif",
            "https://maltdrive.com/wp-content/uploads/2024/10/05-20240926_DSC9655-1_2-20-Malt-Dr_430-jpg.avif"
        ],
        "unit_features": [
            "Corner Unit",
            "High Ceilings",
            "Flexible Windowed Alcove", 
            "Windowed Kitchen",
            "In-Unit Washer/Dryer",
            "Walk-In Closet",
            "Solar Shades",
            "Northeast Exposure",
            "Creek and City Views",
            "Northern Exposure",
            "Eastern Exposure"
        ],
        "transportation": [
            "7 Train - Vernon Blvd-Jackson Ave (8 min walk)",
            "G Train - 21st St (12 min walk)",
            "NYC Ferry - Long Island City (5 min walk)",
            "Multiple Bus Lines"
        ],
        "contact_email": "MaltDriveLeasing@tfc.com",
        "contact_phone": "(718) 220-2222",
        "broker_fee": False,
        "no_fee": True,
        "featured": True,
        "priority": 1,
        "source": "Malt Drive Official",
        "listing_url": "https://maltdrive.com/listing/2-20-malt-drive_3001/",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "lease_terms": {
            "gross_rent": 5820,
            "net_rent": 5093,
            "special_offers": [
                "Up to 3 months free on 24-month lease",
                "1 month OP (Owner Pays)",
                "1/2 month security deposit for qualified applicants"
            ],
            "application_fee": 20,
            "security_deposit": "Equivalent to 1 month rent (or 1/2 month for qualified)",
            "community_fee": 75
        },
        "building_features": [
            "Modern High-Rise",
            "Waterfront Location",
            "Luxury Finishes",
            "Energy Efficient",
            "Pet-Friendly with Dog Amenities"
        ],
        "nearby_attractions": [
            "Hunter's Point South Park",
            "Gantry Plaza State Park", 
            "Long Island City Waterfront",
            "MoMA PS1",
            "Queens Plaza Shopping"
        ]
    }
    
    try:
        # Insert the apartment
        result = await apartments_collection.insert_one(apartment_data)
        print(f"✅ Successfully added Malt Drive apartment!")
        print(f"   - Apartment ID: {apartment_data['id']}")
        print(f"   - MongoDB ID: {result.inserted_id}")
        print(f"   - Address: {apartment_data['address']}")
        print(f"   - Price: ${apartment_data['price']}/month (Gross Rent)")
        print(f"   - Net Rent: ${apartment_data['lease_terms']['net_rent']}/month")
        print(f"   - Type: {apartment_data['bedrooms']} Bedroom, {apartment_data['bathrooms']} Bathroom")
        print(f"   - Building: {apartment_data['building_name']}")
        print(f"   - Neighborhood: {apartment_data['neighborhood']}")
        print(f"   - Borough: {apartment_data['borough']}")
        print(f"   - No Fee: {apartment_data['no_fee']}")
        print(f"   - Featured: {apartment_data['featured']}")
        print(f"   - Contact: {apartment_data['contact_phone']}")
        print(f"   - Email: {apartment_data['contact_email']}")
        print(f"   - Special Offers: {len(apartment_data['lease_terms']['special_offers'])} available")
        print(f"   - Images: {len(apartment_data['images'])} high-quality photos")
        
        # Verify the apartment was added
        count = await apartments_collection.count_documents({})
        print(f"\n📊 Total apartments in database: {count}")
        
        # Show Queens breakdown
        queens_count = await apartments_collection.count_documents({"borough": "Queens"})
        print(f"📍 Queens apartments: {queens_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding apartment: {e}")
        return False
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_malt_drive_apartment())