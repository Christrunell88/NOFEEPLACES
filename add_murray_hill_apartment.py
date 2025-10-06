#!/usr/bin/env python3
"""
Add The Murray Hill apartment to NoFeePlaces.com database
Apartment: 115 East 34 Street, Murray Hill - $4,975/month - 1BR/1BA
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone
import uuid

# Load environment variables
load_dotenv('/app/backend/.env')

async def add_murray_hill_apartment():
    """Add The Murray Hill luxury apartment to the database"""
    
    # Get MongoDB connection
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.nofeeplaces_database
    
    # Extract images from the scraped data
    apartment_images = [
        'https://manhattanskyline.com/storage/_styles/multi-hero/unit/3JCNFYDhJceQa3neOV2zv9nPrDxVy5WLDuLMYs2s.jpeg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/unit/wzuXQIVFpC4CfimLkHVatQLuwF7QCB7sPUacBTma.jpg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/unit/bpr4taeqPJpYODgciEWie1S8dd7YZqSzUtOfgq5x.jpg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/unit/sPfCOGiCqiLsyKk1cQ6UDd4zfYUaYkTEEqAwoQLV.jpg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/building/Z2zNY9M1TLSaPUejWGUGMgjVNDqrBxsEiuQvlewT.jpg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/building/vNrHaoEOl9Fwgo1CcpTM9KaHfVBvivL9HUOAUk2m.jpeg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/building/UJs13pXCjv6bxE4XPCaXlRBCUiYlpqjgCNeiiImk.jpeg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/building/DNYPgFQXGmakkKyBkyiSUiEw6t6KNsf5UaxDyJEj.jpeg'
    ]
    
    # Create apartment data
    murray_hill_apartment = {
        "id": str(uuid.uuid4()),
        "title": "No Fee 1BR at The Murray Hill - Luxury Building in Murray Hill",
        "description": "This spacious one-bedroom has great light and open views. The galley kitchen is off the large living room leaving a large open space, expansive enough to flex to a two-bedroom. The kitchen features custom solid wood cabinetry, stainless steel appliances, and granite countertops. Bathroom features ceramic tile and tri-view medicine cabinet. This home comes with abundant closet space in a 24-hour doorman building with fantastic staff, Resident Manager, and a landscaped furnished roof deck. Complimentary amenity package includes membership to fully-equipped fitness center, tenant lounge and bicycle storage.",
        "price": 4975.0,
        "location": "Murray Hill, Manhattan",
        "neighborhood": "Murray Hill",
        "bedrooms": 1,
        "bathrooms": 1.0,
        "sqft": 850,  # Estimated based on description
        "amenities": [
            "Doorman 24-Hour", "Elevator", "Fitness Center", "Rooftop Deck", 
            "Tenant Lounge", "Bicycle Storage", "Laundry in Building", 
            "Pet Friendly", "Resident Manager", "Courtyard",
            "Dishwasher", "Granite Countertops", "Stainless Steel Appliances",
            "Microwave", "Icemaker", "Breakfast Bar"
        ],
        "images": apartment_images,
        "contact_email": "placesfirm@gmail.com",
        "contact_phone": "+1-646-408-8048",
        "available": True,
        "lease_terms": "12 months",
        "pet_policy": "Pet-friendly",
        "utilities": "Not included",
        "move_in_date": "Immediate",
        "deposit": "$4,975 - $9,950",
        "broker_fee": "No fee",
        "address": "115 East 34 Street, New York, NY 10016",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "Manhattan Skyline - The Murray Hill",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "is_verified": True,
        "is_real": True,
        "verification_status": "Verified Real Listing - NoFeePlaces LLC",
        "views": 0,
        "inquiries": 0,
        "is_featured": True,  # This is a premium listing
        "building_name": "The Murray Hill",
        "building_amenities": [
            "24-Hour Doorman", "Elevator", "Fitness Center", 
            "Landscaped Roof Deck", "Resident Lounge", "Bicycle Storage",
            "Laundry in Building", "Pet Friendly", "Resident Manager", "Courtyard"
        ],
        "unit_features": [
            "Breakfast Bar", "Dishwasher", "Granite Countertops", "Microwave",
            "Convert to 2BR", "Icemaker", "Stainless Steel Appliances",
            "Custom Wood Cabinetry", "Ceramic Tile Bathroom", "Abundant Closet Space"
        ],
        "transportation": [
            "33rd St/Park Ave South (6 train) - 2 min walk",
            "Grand Central Station (4,5,6,7,S) - 8 min walk", 
            "34th St/Herald Square (N,Q,R,W,B,D,F,M,PATH) - 9 min walk"
        ],
        "neighborhood_highlights": [
            "Murray Hill Nightlife", "Grand Central Proximity", 
            "Midtown East Offices", "Restaurants & Bars", "Shopping"
        ],
        "original_listing_url": "https://manhattanskyline.com/buildings/murray-hill/the-murray-hill/apartment-7neqg4t3",
        "luxury_building": True,
        "concierge_services": True
    }
    
    try:
        # Check if apartment already exists
        existing = await db.apartments.find_one({"address": "115 East 34 Street, New York, NY 10016"})
        
        if existing:
            print("⚠️  Apartment at this address already exists. Updating instead...")
            # Update existing apartment
            result = await db.apartments.update_one(
                {"address": "115 East 34 Street, New York, NY 10016"},
                {"$set": murray_hill_apartment}
            )
            print(f"✅ Updated existing Murray Hill apartment")
        else:
            # Insert new apartment
            result = await db.apartments.insert_one(murray_hill_apartment)
            print(f"✅ Successfully added Murray Hill apartment with ID: {murray_hill_apartment['id']}")
        
        # Get updated apartment count
        total_apartments = await db.apartments.count_documents({})
        print(f"📊 Total apartments now in database: {total_apartments}")
        
        # Show apartment details
        print(f"\n🏢 APARTMENT DETAILS:")
        print(f"   Title: {murray_hill_apartment['title']}")
        print(f"   Address: {murray_hill_apartment['address']}")
        print(f"   Price: ${murray_hill_apartment['price']:,.0f}/month")
        print(f"   Size: {murray_hill_apartment['bedrooms']} bed, {murray_hill_apartment['bathrooms']} bath")
        print(f"   Building: {murray_hill_apartment['building_name']}")
        print(f"   Amenities: {len(murray_hill_apartment['amenities'])} total")
        print(f"   Images: {len(murray_hill_apartment['images'])} photos")
        print(f"   Featured: {murray_hill_apartment['is_featured']}")
        print(f"   Contact: {murray_hill_apartment['contact_email']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding Murray Hill apartment: {str(e)}")
        return False
        
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(add_murray_hill_apartment())
    if success:
        print(f"\n🎉 Murray Hill luxury apartment successfully added to NoFeePlaces.com!")
        print(f"🔍 Users can now search for and view this premium listing")
        print(f"📧 All inquiries will be sent to placesfirm@gmail.com")
    else:
        print(f"\n❌ Failed to add Murray Hill apartment")