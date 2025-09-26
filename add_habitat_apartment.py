#!/usr/bin/env python3
"""
Add The Habitat apartment listing to NoFeePlaces database
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

async def add_habitat_apartment():
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    apartments_collection = db.apartments
    
    # Create apartment data based on extracted information
    apartment_data = {
        "id": str(uuid.uuid4()),
        "title": "Large Studio with Great Layout - The Habitat",
        "address": "154 East 29th Street, New York, NY 10016",
        "location": "154 East 29th Street, Kips Bay, Manhattan",
        "neighborhood": "Kips Bay",
        "borough": "Manhattan",
        "price": 3595,
        "bedrooms": "Studio",
        "bathrooms": 1,
        "sqft": None,  # Not specified in listing
        "available_date": datetime.now(timezone.utc).isoformat(),
        "description": "SHOWINGS BY APPOINTMENT ONLY. This large studio has a great layout and gets abundant sunlight. Windowed kitchen is separate from the large living room and comes with custom solid wood cabinetry, dishwasher, stainless steel appliances, and stone countertops. Bathroom features ceramic tile and tri-view medicine cabinet. In addition, this home has ample closet space.",
        "amenities": [
            "Doorman (Part-time)",
            "Elevator", 
            "Fitness Center",
            "Landscaped and Furnished Roof Deck",
            "Laundry in Building",
            "Pet Friendly",
            "Resident Manager",
            "Concierge Services",
            "Rooftop Deck"
        ],
        "building_name": "The Habitat",
        "utilities_included": [
            "Heat",
            "Hot Water"
        ],
        "images": [
            "https://manhattanskyline.com/storage/_styles/gallery/building/i1WJQJUfW0igwCP1VM71hYIaZ7YlmMBgPo5al6I9.jpg",
            "https://manhattanskyline.com/storage/_styles/gallery/unit/rjfAMRyPiKtdG1IqAhfhzMozkuWm49ByOIgE2TKU.jpg",
            "https://manhattanskyline.com/storage/_styles/gallery/unit/5TJF1B6T7KI6NgskKqSUCo1efpgT2wxw0MLlcgEO.jpg",
            "https://manhattanskyline.com/storage/_styles/gallery/unit/4Sfa0jKmAZjvFGgx33d6RMDTUOWiKsG3p3a5nhai.jpg",
            "https://manhattanskyline.com/storage/_styles/gallery/building/N0Bo4x4hzCqPCelOwRMzyWG1lQrlZf3UiyXv4nZe.jpg"
        ],
        "unit_features": [
            "Microwave",
            "Stainless Steel Amenities", 
            "Dishwasher",
            "Icemaker",
            "Custom Solid Wood Cabinetry",
            "Stone Countertops",
            "Windowed Kitchen",
            "Ceramic Tile Bathroom",
            "Tri-view Medicine Cabinet",
            "Ample Closet Space",
            "Abundant Sunlight"
        ],
        "transportation": [
            "6 Train - 28th St/Park Ave South (4 min walk)",
            "R, W Trains - 28th St/Broadway (10 min walk)",
            "Multiple Bus Lines - M101, M102, M103, M9, M15"
        ],
        "contact_email": "leasing@manhattanskyline.com",
        "contact_phone": "(347) 728-0333",
        "broker_fee": False,
        "no_fee": True,
        "featured": True,
        "priority": 1,
        "source": "Manhattan Skyline",
        "listing_url": "https://manhattanskyline.com/buildings/kips-bay/the-habitat/apartment-lukzclk6",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "lease_guarantors": [
            "Insurent",
            "The Guarantors"
        ],
        "nearby_shops": [
            "Whole Foods"
        ],
        "security_deposit_alternative": "The Guarantors - Pay monthly fee instead of security deposit"
    }
    
    try:
        # Insert the apartment
        result = await apartments_collection.insert_one(apartment_data)
        print(f"✅ Successfully added The Habitat apartment!")
        print(f"   - Apartment ID: {apartment_data['id']}")
        print(f"   - MongoDB ID: {result.inserted_id}")
        print(f"   - Address: {apartment_data['address']}")
        print(f"   - Price: ${apartment_data['price']}/month")
        print(f"   - Type: {apartment_data['bedrooms']}, {apartment_data['bathrooms']} Bath")
        print(f"   - Building: {apartment_data['building_name']}")
        print(f"   - Neighborhood: {apartment_data['neighborhood']}")
        print(f"   - No Fee: {apartment_data['no_fee']}")
        print(f"   - Featured: {apartment_data['featured']}")
        
        # Verify the apartment was added
        count = await apartments_collection.count_documents({})
        print(f"\n📊 Total apartments in database: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding apartment: {e}")
        return False
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_habitat_apartment())