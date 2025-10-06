#!/usr/bin/env python3
"""
Add Saranac Tribeca apartment to NoFeePlaces.com database
Apartment: 95 Worth Street, Tribeca - $4,800/month - 1BR/1BA
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone
import uuid

# Load environment variables
load_dotenv('/app/backend/.env')

async def add_tribeca_saranac_apartment():
    """Add the Saranac luxury Tribeca apartment to the database"""
    
    # Get MongoDB connection
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.nofeeplaces_database
    
    # Extract images from the scraped data
    apartment_images = [
        'https://manhattanskyline.com/storage/_styles/multi-hero/unit/t4UtDLzOEmAcrHBhRxHZFpoKcbgyYrDUAqIkJU2K.jpg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/unit/iFWkIDhLKcJP8X4Gyv2GTOEBTxx2ugjX4yLZmsrL.jpg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/unit/Sw4cV2tvP90rTwki2joAthhltYZc7unQ7DI33Zoc.jpg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/unit/rDGN4ntzwmbhFvnMyHuHnkG129XUJzU0qpS0aBmj.jpg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/building/Bdd8shFAJRhNrxX9vJMkAbt9aJz0snR8CAx9MAHH.jpeg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/building/b8loil8TllESKF5HuvvLxvMQv8cPd0Q7agPcFJnX.jpeg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/building/Q4Jue9RRtu6tYE9qy025L6kDxngy4liTnKfjke51.jpeg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/building/wjaJSghNypQGnDCviNNruhazFk6O0t1iBBcP6SCn.jpeg',
        'https://manhattanskyline.com/storage/_styles/multi-hero/building/5G4aEh4NcfRr1oRwOhklvfktpDa5QvMLcqYcDtH3.jpeg'
    ]
    
    # Create apartment data
    tribeca_saranac_apartment = {
        "id": str(uuid.uuid4()),
        "title": "No Fee 1BR at Saranac - Luxury Tribeca Building with Rooftop Deck",
        "description": "Renovated north facing spacious one-bedroom with breakfast bar, granite countertops, custom cabinetry, and stainless steel appliances. With an efficient layout, great closet space and quiet exposure, this one-bedroom home is both comfortable and convenient. Saranac is a post war 24-hour doorman building with two roof terraces, fitness center, laundry, and in-house Resident Manager. Located in the heart of Tribeca with proximity to every major subway line, making it easy to commute to any neighborhood in Manhattan and Brooklyn.",
        "price": 4800.0,
        "location": "Tribeca, Manhattan",
        "neighborhood": "Tribeca",
        "bedrooms": 1,
        "bathrooms": 1.0,
        "sqft": 750,  # Estimated based on description and layout
        "amenities": [
            "Doorman 24-Hour", "Elevator", "Fitness Center", "Landscaped Roof Deck", 
            "Furnished Roof Deck", "Laundry on Floor", "Pet Friendly", "Resident Manager",
            "Garage", "Breakfast Bar", "Granite Countertops", "Icemaker", 
            "Microwave", "Stainless Steel Appliances", "Dishwasher", "Renovated"
        ],
        "images": apartment_images,
        "contact_email": "placesfirm@gmail.com",
        "contact_phone": "+1-646-408-8048",
        "available": True,
        "lease_terms": "12 months",
        "pet_policy": "Pet-friendly",
        "utilities": "Not included",
        "move_in_date": "By appointment",
        "deposit": "Security deposit alternatives available",
        "broker_fee": "No fee",
        "address": "95 Worth Street, New York, NY 10013",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "Manhattan Skyline - Saranac",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "is_verified": True,
        "is_real": True,
        "verification_status": "Verified Real Listing - NoFeePlaces LLC",
        "views": 0,
        "inquiries": 0,
        "is_featured": True,  # Premium Tribeca listing
        "building_name": "Saranac",
        "building_amenities": [
            "24-Hour Doorman", "Elevator", "Fitness Center", "Two Landscaped Roof Terraces",
            "Laundry on Floor", "Pet Friendly", "Resident Manager", "Garage",
            "Sky's the Limit Concierge Services"
        ],
        "unit_features": [
            "Breakfast Bar", "Granite Countertops", "Icemaker", "Microwave",
            "Stainless Steel Appliances", "Renovated", "Dishwasher",
            "Custom Cabinetry", "Great Closet Space", "Quiet North Exposure"
        ],
        "transportation": [
            "Chambers St (4,5,6,J,Z) - 4 min walk",
            "Brooklyn Bridge/City Hall (4,5,6) - 4 min walk",
            "City Hall (R,W) - 5 min walk",
            "Canal St (N,Q,R,W,6,J,Z) - 6 min walk",
            "Chambers St/Broadway (1,2,3) - 7 min walk"
        ],
        "neighborhood_highlights": [
            "Chic Tribeca Prewar Lofts", "Sophisticated Dining Scene", 
            "Financial District Proximity", "Washington Market Park",
            "Every Major Subway Line Within Blocks"
        ],
        "nearby_attractions": [
            "Duane Park", "Thomas Paine Park", "Washington Market Park",
            "Whole Foods", "Landmarc Restaurant", "Locanda Verde",
            "Tribeca Film Institute", "Tribeca Performing Arts Center"
        ],
        "concierge_services": [
            "Move-in Services", "Restaurant Reservations", "Dog Walking Services",
            "Exclusive Resident Events", "Special Discounts", "Personal Assistance"
        ],
        "original_listing_url": "https://manhattanskyline.com/buildings/tribeca/saranac/apartment-a0cesybm",
        "luxury_building": True,
        "concierge_services_available": True,
        "building_year": "Post-war",
        "showing_policy": "By appointment only",
        "lease_guarantors": "Insurent and The Guarantors available"
    }
    
    try:
        # Check if apartment already exists at this address
        existing = await db.apartments.find_one({"address": "95 Worth Street, New York, NY 10013"})
        
        if existing:
            print("⚠️  Apartment at this address already exists. Updating instead...")
            # Update existing apartment
            result = await db.apartments.update_one(
                {"address": "95 Worth Street, New York, NY 10013"},
                {"$set": tribeca_saranac_apartment}
            )
            print(f"✅ Updated existing Tribeca Saranac apartment")
        else:
            # Insert new apartment
            result = await db.apartments.insert_one(tribeca_saranac_apartment)
            print(f"✅ Successfully added Tribeca Saranac apartment with ID: {tribeca_saranac_apartment['id']}")
        
        # Get updated apartment count
        total_apartments = await db.apartments.count_documents({})
        print(f"📊 Total apartments now in database: {total_apartments}")
        
        # Show apartment details
        print(f"\n🏢 APARTMENT DETAILS:")
        print(f"   Title: {tribeca_saranac_apartment['title']}")
        print(f"   Address: {tribeca_saranac_apartment['address']}")
        print(f"   Price: ${tribeca_saranac_apartment['price']:,.0f}/month")
        print(f"   Size: {tribeca_saranac_apartment['bedrooms']} bed, {tribeca_saranac_apartment['bathrooms']} bath")
        print(f"   Building: {tribeca_saranac_apartment['building_name']}")
        print(f"   Neighborhood: {tribeca_saranac_apartment['neighborhood']}")
        print(f"   Amenities: {len(tribeca_saranac_apartment['amenities'])} total")
        print(f"   Images: {len(tribeca_saranac_apartment['images'])} photos")
        print(f"   Transportation: {len(tribeca_saranac_apartment['transportation'])} subway options")
        print(f"   Featured: {tribeca_saranac_apartment['is_featured']}")
        print(f"   Contact: {tribeca_saranac_apartment['contact_email']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding Tribeca Saranac apartment: {str(e)}")
        return False
        
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(add_tribeca_saranac_apartment())
    if success:
        print(f"\n🎉 Tribeca Saranac luxury apartment successfully added to NoFeePlaces.com!")
        print(f"🏙️  Premium Tribeca location with 24-hour doorman and rooftop terraces")
        print(f"🚇 Excellent transportation - every major subway line within blocks")
        print(f"📧 All inquiries will be sent to placesfirm@gmail.com")
    else:
        print(f"\n❌ Failed to add Tribeca Saranac apartment")