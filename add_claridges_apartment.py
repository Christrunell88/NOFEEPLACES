#!/usr/bin/env python3
"""
Script to add Claridge's apartment to NoFeePlaces database at the top of listings
"""

import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime, timezone
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Database configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

async def add_claridges_apartment():
    """Add the Claridge's apartment from manhattanskyline.com"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Apartment data from the scraped listing
    apartment_data = {
        "id": str(uuid.uuid4()),
        "title": "Luxury No Fee 1-Bedroom at Claridge's® - Midtown West",
        "address": "101 West 55 Street, New York, NY 10019",
        "neighborhood": "Midtown West",
        "borough": "Manhattan",
        "price": 5995,
        "bedrooms": 1,
        "bathrooms": 1,
        "sqft": 650,  # Estimated based on description "large one-bedroom"
        "description": "SHOWINGS BY APPOINTMENT ONLY. East facing large one-bedroom one-bath home. Pass thru kitchen with custom cabinetry, stainless steel appliances, and granite countertops. The home offers five large closets including two walk-in closets. Claridge's is a full-service, white-glove doorman building with elevator, laundry, valet, fitness center, and in-house Resident Manager.",
        "amenities": [
            "Doorman",
            "Elevator", 
            "Fitness Center",
            "Laundry in Building",
            "Pet Friendly",
            "Granite Countertops",
            "Stainless Steel Appliances",
            "Dishwasher",
            "Modern floors",
            "Icemaker",
            "Microwave",
            "Walk-in Closets",
            "Valet Service"
        ],
        "images": [
            "https://manhattanskyline.com/storage/_styles/multi-hero/unit/RFOBc2W2KeTIFIK6ZUKmnXQpfKorvNESdNx6amL3.jpg",
            "https://manhattanskyline.com/storage/_styles/multi-hero/unit/L6zWekBc4UuwRs8WaN8sVCQ48fXS8On5B31btLnG.jpg",
            "https://manhattanskyline.com/storage/_styles/multi-hero/unit/r2KP2N4WGykvV2KTSSnZp3UHqIpdRSLmVNfgrCKd.jpg",
            "https://manhattanskyline.com/storage/_styles/multi-hero/unit/27GyadMWCjPDdpcn9dLCFGZEQTChAB4wN4efjjY4.jpg"
        ],
        "location": {
            "lat": 40.7614,
            "lng": -73.9776
        },
        "is_no_fee": True,
        "available": True,
        "lease_term": "12+ months",
        "pet_policy": "Pet Friendly",
        "contact_info": {
            "phone": "646-408-8048",
            "email": "placesfirm@gmail.com",
            "broker": "Licensed Agent"
        },
        "building_features": [
            "Full-Service Doorman",
            "White-Glove Service", 
            "Elevator",
            "Fitness Center",
            "Laundry Room",
            "Valet Service",
            "In-House Resident Manager"
        ],
        "transportation": [
            "F Train (57th St/6th Ave) - 1 min walk",
            "N,Q,R,W Trains (57th St/7th Ave) - 3 min walk", 
            "B,D,E Trains (53rd St/7th Ave) - 5 min walk",
            "E,M Trains (53rd St/5th Ave) - 6 min walk"
        ],
        "nearby": [
            "Central Park - 2 blocks north",
            "5th Avenue Shopping - 2 blocks east",
            "Radio City Music Hall - 3 blocks south",
            "Rockefeller Center - 4 blocks south",
            "Theater District - 5 blocks south",
            "Museum of Modern Art - 4 blocks east"
        ],
        "source": "Manhattan Skyline",
        "source_url": "https://manhattanskyline.com/buildings/midtown-west/claridges/apartment-jrdzvt1q",
        "created_at": datetime.now(timezone.utc),  # Current time to place at top
        "updated_at": datetime.now(timezone.utc),
        "featured": True,  # Mark as featured to ensure top placement
        "priority": 1  # Highest priority for sorting
    }
    
    try:
        # Insert the apartment
        result = await db.apartments.insert_one(apartment_data)
        print(f"✅ Successfully added Claridge's apartment with ID: {result.inserted_id}")
        print(f"📍 Address: {apartment_data['address']}")
        print(f"💰 Price: ${apartment_data['price']:,}/month")
        print(f"🏠 {apartment_data['bedrooms']} bed, {apartment_data['bathrooms']} bath")
        print(f"🌟 Featured: {apartment_data['featured']}")
        print(f"📅 Created: {apartment_data['created_at']}")
        
        # Verify it was added by checking total count
        total_apartments = await db.apartments.count_documents({})
        print(f"📊 Total apartments in database: {total_apartments}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding apartment: {e}")
        return False
    
    finally:
        client.close()

async def main():
    """Main function"""
    print("🏢 Adding Claridge's Apartment to NoFeePlaces Database...")
    print("=" * 60)
    
    success = await add_claridges_apartment()
    
    if success:
        print("=" * 60)
        print("🎉 Apartment successfully added and will appear at the top of listings!")
        print("🔗 Source: https://manhattanskyline.com/buildings/midtown-west/claridges/apartment-jrdzvt1q")
    else:
        print("❌ Failed to add apartment")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())