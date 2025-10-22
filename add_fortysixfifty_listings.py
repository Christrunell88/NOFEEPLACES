import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# Building information
BUILDING_INFO = {
    "building_name": "Forty Six Fifty",
    "address_base": "4650 Broadway",
    "full_address_base": "4650 Broadway, New York, NY 10040",
    "neighborhood": "Hudson Heights",
    "location": "Hudson Heights, Manhattan",
    "borough": "Manhattan",
    "zipcode": "10040",
    "broker_fee": "No Fee",
    "description_base": "Newly constructed luxury residence at Forty Six Fifty featuring modern interiors, high ceilings, hardwood floors, in-unit washer/dryer, large windows with abundant natural light, quartz countertops, designer fixtures, and premium appliances. Located at the northern edge of Manhattan bordering Fort Tryon Park and The Cloisters with stunning park and river views. Building offers world-class amenities including double-height wood-paneled lobby with fireplace and green wall, fitness center with Precor equipment and Peloton bikes, yoga room, basketball court, game lounge with billiards and video games, coworking spaces, demonstration kitchen, landscaped rooftop terrace with grills and lounges, children's playroom, pet spa, bike storage, and on-site garage parking. Convenient to A and 1 trains at Dyckman Street. 2 months free on 12-month lease (net effective rent listed).",
    "amenities": [
        "Double-Height Wood-Paneled Lobby",
        "24/7 Doorman",
        "Package Room",
        "Fitness Center with Precor Equipment",
        "Peloton Bikes",
        "Yoga Room",
        "Basketball Court",
        "Game Lounge with Billiards",
        "Pinball, Shuffleboard, Foosball",
        "Video Games",
        "Projector Screen",
        "Wet Bar",
        "Coworking Lounge",
        "Private Phone Booths",
        "Demonstration Kitchen",
        "Children's Playroom",
        "Pet Spa",
        "Landscaped Rooftop Terrace",
        "Outdoor Lounge",
        "Pool Table",
        "Chaise Lounges",
        "BBQ Grills",
        "Bike Storage",
        "Resident Storage",
        "On-Site Garage Parking",
        "Green Wall",
        "Stone Fireplace",
        "Elevator",
        "In-Unit Washer/Dryer",
        "Dishwasher",
        "Hardwood Floors",
        "High Ceilings",
        "Large Windows",
        "Quartz Countertops",
        "Designer Fixtures",
        "Premium Appliances",
        "Fort Tryon Park Views",
        "Pet Friendly"
    ],
    "contact_name": "NoFeePlaces",
    "contact_email": "placesfirm@gmail.com",
    "contact_phone": "+1-646-408-8048",
    "source": "Forty Six Fifty Official Website",
    "listing_url": "https://www.fortysixfifty.com/availability",
    "pets_allowed": True,
    "laundry": "In-Unit",
    "parking": "On-Site Garage",
    "utilities_included": False,
    "lease_terms": "12 months (2 months free)",
    "verified": True,
    "featured": True,
    "landlord_paid_broker_fee": True,
    "listing_type": "rental",
    "status": "active",
    "available": True
}

# Apartment listings data
listings = [
    # STUDIOS
    {
        "unit": "2112",
        "bedrooms": 0,
        "bathrooms": 1,
        "square_feet": 368,
        "price": 2613.33,  # Net effective rent
        "original_price": 3136,
        "floor": "21",
        "available_date": "Immediate",
        "title": "Studio at Forty Six Fifty - Unit 2112"
    },
    {
        "unit": "1402",
        "bedrooms": 0,
        "bathrooms": 1,
        "square_feet": 500,
        "price": 2615.83,
        "original_price": 3139,
        "floor": "14",
        "available_date": "Immediate",
        "title": "Studio at Forty Six Fifty - Unit 1402"
    },
    {
        "unit": "0911",
        "bedrooms": 0,
        "bathrooms": 1,
        "square_feet": 501,
        "price": 2633.33,
        "original_price": 3160,
        "floor": "9",
        "available_date": "Immediate",
        "title": "Studio at Forty Six Fifty - Unit 0911"
    },
    {
        "unit": "1702",
        "bedrooms": 0,
        "bathrooms": 1,
        "square_feet": 500,
        "price": 2840.83,
        "original_price": 3409,
        "floor": "17",
        "available_date": "Immediate",
        "title": "Studio at Forty Six Fifty - Unit 1702"
    },
    {
        "unit": "1811",
        "bedrooms": 0,
        "bathrooms": 1,
        "square_feet": 501,
        "price": 2857.50,
        "original_price": 3429,
        "floor": "18",
        "available_date": "Immediate",
        "title": "Studio at Forty Six Fifty - Unit 1811"
    },
    # 1 BEDROOMS
    {
        "unit": "0708",
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 619,
        "price": 2822.50,
        "original_price": 3387,
        "floor": "7",
        "available_date": "11/14/2025",
        "title": "1 Bedroom at Forty Six Fifty - Unit 0708"
    },
    {
        "unit": "0909",
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 647,
        "price": 2962.50,
        "original_price": 3555,
        "floor": "9",
        "available_date": "Immediate",
        "title": "1 Bedroom at Forty Six Fifty - Unit 0909"
    },
    {
        "unit": "1009",
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 647,
        "price": 2975.00,
        "original_price": 3570,
        "floor": "10",
        "available_date": "Immediate",
        "title": "1 Bedroom at Forty Six Fifty - Unit 1009"
    },
    {
        "unit": "1906",
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 648,
        "price": 3200.00,
        "original_price": 3840,
        "floor": "19",
        "available_date": "2/23/2026",
        "title": "1 Bedroom at Forty Six Fifty - Unit 1906"
    },
    # 2 BEDROOMS
    {
        "unit": "1703",
        "bedrooms": 2,
        "bathrooms": 1,
        "square_feet": 840,
        "price": 4200.00,
        "original_price": 5040,
        "floor": "17",
        "available_date": "Immediate",
        "title": "2 Bedroom at Forty Six Fifty - Unit 1703"
    },
    {
        "unit": "1110",
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1103,
        "price": 4470.83,
        "original_price": 5365,
        "floor": "11",
        "available_date": "Immediate",
        "title": "2 Bedroom at Forty Six Fifty - Unit 1110"
    },
    {
        "unit": "1210",
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1103,
        "price": 4483.33,
        "original_price": 5380,
        "floor": "12",
        "available_date": "Immediate",
        "title": "2 Bedroom at Forty Six Fifty - Unit 1210"
    }
]

# Sample images from the website
SAMPLE_IMAGES = [
    "https://www.fortysixfifty.com/_next/image?url=%2Fimages%2Favailability%2F673250450-24kcjp_4650bwy_711_modelapt_175.jpg&w=3840&q=75",
    "https://www.fortysixfifty.com/_next/image?url=%2Fimages%2Fgallery%2Fresidences%2F24KCJP_4650Bwy_704_MdApt_20%20ret1.jpg&w=3840&q=75",
    "https://www.fortysixfifty.com/_next/image?url=%2Fimages%2Fmarch-photos%2F718894434-25kcjp_4650bwy_6fl_lounge_255-ret1.jpg&w=3840&q=75",
    "https://www.fortysixfifty.com/_next/image?url=%2Fimages%2Famenities%2F673251028-24kcjp_4650bwy_lobby_196.jpg&w=3840&q=75",
    "https://www.fortysixfifty.com/_next/image?url=%2Fimages%2Famenities%2F672845354-24kcjp_4650bwy_game_190-lowres.jpg&w=3840&q=75",
    "https://www.fortysixfifty.com/_next/image?url=%2Fimages%2Famenities%2F672845409-24kcjp_4650bwy_terr_205-lowres.jpg&w=3840&q=75"
]

def get_price_category(price):
    """Determine price category based on rent"""
    if price < 4500:
        return "Budget", "Budget 💰"
    elif price < 6500:
        return "Smart", "Smart 🎯"
    else:
        return "Sky's the Limit", "Sky's the Limit 💎"

async def add_listings():
    """Add Forty Six Fifty listings to the database"""
    try:
        # Connect to MongoDB
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client['nofeeplaces_database']
        
        added_count = 0
        updated_count = 0
        
        print(f"🏢 Adding {len(listings)} Forty Six Fifty listings...\n")
        
        for listing in listings:
            # Get price category
            price_cat, price_cat_label = get_price_category(listing['price'])
            
            # Build full listing data
            listing_data = {
                "id": str(uuid.uuid4()),
                "title": listing['title'],
                "price": listing['price'],
                "bedrooms": listing['bedrooms'],
                "bathrooms": listing['bathrooms'],
                "square_feet": listing['square_feet'],
                "address": f"{BUILDING_INFO['address_base']}, Unit {listing['unit']}",
                "full_address": f"{BUILDING_INFO['address_base']}, Unit {listing['unit']}, New York, NY {BUILDING_INFO['zipcode']}",
                "neighborhood": BUILDING_INFO['neighborhood'],
                "location": BUILDING_INFO['location'],
                "borough": BUILDING_INFO['borough'],
                "zipcode": BUILDING_INFO['zipcode'],
                "building_name": BUILDING_INFO['building_name'],
                "floor": listing['floor'],
                "unit": listing['unit'],
                "broker_fee": BUILDING_INFO['broker_fee'],
                "available_date": listing['available_date'],
                "description": f"{listing['title']} - {listing['square_feet']} sq ft. {BUILDING_INFO['description_base']} Original rent: ${listing['original_price']:,.2f}/month. Net effective rent with 2 months free: ${listing['price']:,.2f}/month.",
                "amenities": BUILDING_INFO['amenities'],
                "images": SAMPLE_IMAGES,
                "contact_name": BUILDING_INFO['contact_name'],
                "contact_email": BUILDING_INFO['contact_email'],
                "contact_phone": BUILDING_INFO['contact_phone'],
                "source": BUILDING_INFO['source'],
                "listing_url": BUILDING_INFO['listing_url'],
                "pets_allowed": BUILDING_INFO['pets_allowed'],
                "laundry": BUILDING_INFO['laundry'],
                "parking": BUILDING_INFO['parking'],
                "utilities_included": BUILDING_INFO['utilities_included'],
                "lease_terms": BUILDING_INFO['lease_terms'],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "verified": BUILDING_INFO['verified'],
                "featured": BUILDING_INFO['featured'],
                "price_category": price_cat,
                "price_category_label": price_cat_label,
                "best_value": False,
                "landlord_paid_broker_fee": BUILDING_INFO['landlord_paid_broker_fee'],
                "listing_type": BUILDING_INFO['listing_type'],
                "status": BUILDING_INFO['status'],
                "available": BUILDING_INFO['available']
            }
            
            # Check if listing already exists
            existing = await db.apartments.find_one({
                'building_name': BUILDING_INFO['building_name'],
                'unit': listing['unit']
            })
            
            if existing:
                # Update existing
                result = await db.apartments.update_one(
                    {'id': existing['id']},
                    {'$set': listing_data}
                )
                updated_count += 1
                print(f"✅ Updated: {listing['title']} - ${listing['price']:,.2f}/mo (Unit {listing['unit']})")
            else:
                # Insert new
                result = await db.apartments.insert_one(listing_data)
                added_count += 1
                print(f"✅ Added: {listing['title']} - ${listing['price']:,.2f}/mo (Unit {listing['unit']})")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"📊 Summary:")
        print(f"   New listings added: {added_count}")
        print(f"   Existing listings updated: {updated_count}")
        print(f"   Total processed: {len(listings)}")
        
        # Get total apartment count
        total = await db.apartments.count_documents({})
        print(f"\n📊 Total apartments in database: {total}")
        
        # Get Forty Six Fifty count
        forty_six_fifty_count = await db.apartments.count_documents({
            'building_name': 'Forty Six Fifty'
        })
        print(f"📊 Forty Six Fifty apartments: {forty_six_fifty_count}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding listings: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏢 Forty Six Fifty Listings Import")
    print("=" * 60)
    success = asyncio.run(add_listings())
    print("=" * 60)
    if success:
        print("✅ Script completed successfully!")
    else:
        print("❌ Script failed!")
