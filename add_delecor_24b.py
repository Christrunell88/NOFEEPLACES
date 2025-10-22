import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# Listing data for The Delecor 24B
listing_data = {
    "id": str(uuid.uuid4()),
    "title": "1 Bedroom in Upper East Side - The Delecor",
    "price": 8400,
    "bedrooms": 1,
    "bathrooms": 1,
    "square_feet": None,  # Not specified in listing
    "address": "250 East 83rd Street, Unit 24B",
    "full_address": "250 East 83rd Street, Unit 24B, New York, NY 10028",
    "neighborhood": "Upper East Side",
    "location": "Upper East Side",
    "borough": "Manhattan",
    "zipcode": "10028",
    "building_name": "The Delecor",
    "floor": "24",
    "unit": "24B",
    "broker_fee": "No Fee",
    "available_date": "Now",
    "description": "Grand spaces, exquisite detailing and contemporary finishes - this light-filled 1-bedroom, 1-bathroom residence at The Delecor is a celebration of fine design. Unit 24B features high ceilings, custom Italian kitchens with Thermador, Gaggenau and Bosch appliances including a wine cooler, custom walk-in closets, in-unit washer/dryer, and beautiful marble-clad bathrooms with heated floors. Experience luxury living in this Art Deco-inspired building with stunning views over the skyline, Central Park and the river. Enjoy white-glove concierge service, rooftop lounge 31 floors above the city, year-round indoor pool, state-of-the-art fitness center, yoga studio, children's playroom, multi-sport entertainment system, and surround sound theatre. Located in the heart of the Upper East Side, close to museums, galleries, restaurants, shopping, and Central Park.",
    "amenities": [
        "24/7 Concierge",
        "Rooftop Lounge",
        "Indoor Swimming Pool",
        "Fitness Center",
        "Yoga Studio",
        "Children's Playroom",
        "Media Room/Theatre",
        "Multi-Sport Entertainment System",
        "Bike Storage",
        "Package Room",
        "Elevator",
        "In-Unit Washer/Dryer",
        "Dishwasher",
        "Refrigerator",
        "Wine Cooler",
        "Custom Walk-In Closets",
        "Heated Bathroom Floors",
        "Marble Bathrooms",
        "Italian Kitchen Cabinets",
        "European Oak Floors",
        "Smart Climate Control",
        "High Ceilings",
        "Pet Friendly"
    ],
    "images": [
        "https://cdn.sanity.io/images/1lkfaskc/production/75b3d8f63dad5d3b41249a41ef268e3ff81d6587-2000x2667.jpg",
        "https://cdn.sanity.io/images/1lkfaskc/production/e5931448bb9c1637e5846e0e1c430697578d0872-3556x2000.jpg",
        "https://cdn.sanity.io/images/1lkfaskc/production/53fccb817adb5622c7aab3eac2794caa4b92fc43-5552x4362.tif",
        "https://cdn.sanity.io/images/1lkfaskc/production/abc59cdeb8aadee3fd498356aee0d9190d9477c4-2000x2667.jpg",
        "https://cdn.sanity.io/images/1lkfaskc/production/c635e183a001ee7e8437ec9aa9dc7dbbc7124ef8-3556x2000.jpg",
        "https://cdn.sanity.io/images/1lkfaskc/production/be5d92e8c11b26bbc5caa5ee2d6d74782b5e465e-3556x2000.jpg"
    ],
    "contact_name": "NoFeePlaces",
    "contact_email": "placesfirm@gmail.com",
    "contact_phone": "+1-646-408-8048",
    "source": "The Delecor Official Website",
    "listing_url": "https://www.thedelecor.com/availability/24B",
    "pets_allowed": True,
    "laundry": "In-Unit",
    "parking": "Available",
    "utilities_included": False,
    "lease_terms": "12 months",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "verified": True,
    "featured": True,
    "price_category": "Sky's the Limit",
    "price_category_label": "Sky's the Limit 💎",
    "best_value": False,
    "landlord_paid_broker_fee": True,
    "listing_type": "rental",
    "status": "active"
}

async def add_listing():
    """Add The Delecor 24B listing to the database"""
    try:
        # Connect to MongoDB
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client['nofeeplaces_database']
        
        # Check if listing already exists
        existing = await db.apartments.find_one({'address': listing_data['address'], 'unit': '24B'})
        
        if existing:
            print(f"⚠️  Listing already exists with ID: {existing.get('id')}")
            print(f"Updating existing listing...")
            result = await db.apartments.update_one(
                {'id': existing['id']},
                {'$set': listing_data}
            )
            print(f"✅ Listing updated successfully!")
        else:
            # Insert new listing
            result = await db.apartments.insert_one(listing_data)
            print(f"✅ New listing added successfully!")
            print(f"   Listing ID: {listing_data['id']}")
        
        # Verify the listing
        verify = await db.apartments.find_one({'id': listing_data['id']})
        if verify:
            print(f"\n📋 Listing Details:")
            print(f"   Title: {verify['title']}")
            print(f"   Address: {verify['full_address']}")
            print(f"   Price: ${verify['price']:,}/month")
            print(f"   Bedrooms: {verify['bedrooms']}")
            print(f"   Bathrooms: {verify['bathrooms']}")
            print(f"   Building: {verify['building_name']}")
            print(f"   Amenities: {len(verify['amenities'])} amenities")
            print(f"   Images: {len(verify['images'])} images")
            print(f"   Price Category: {verify['price_category']}")
        
        # Get total apartment count
        total = await db.apartments.count_documents({})
        print(f"\n📊 Total apartments in database: {total}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding listing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏢 Adding The Delecor 24B listing to NoFeePlaces database...")
    print("=" * 60)
    success = asyncio.run(add_listing())
    print("=" * 60)
    if success:
        print("✅ Script completed successfully!")
    else:
        print("❌ Script failed!")
