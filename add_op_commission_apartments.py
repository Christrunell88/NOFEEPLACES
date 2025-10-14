#!/usr/bin/env python3

import asyncio
import uuid
from datetime import datetime, timedelta
import random
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')

# Owner Paid Commission (OP) apartments from StreetEasy and other sources
op_commission_apartments = [
    {
        "title": "Luxury 2BR/2BA at Gotham West - Owner Paid Commission",
        "price": 7870,
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1100,
        "location": "550 West 45th Street #1120, Hell's Kitchen, Manhattan, NY 10036",
        "neighborhood": "Hell's Kitchen",
        "borough": "Manhattan",
        "description": "Luxury 2-bedroom at Gotham West with owner-paid broker commission. No tenant fees! Features premium finishes, floor-to-ceiling windows, and building amenities. 0.5 months free on 18-month lease.",
        "amenities": ["Owner Paid Commission", "No tenant broker fee", "Premium finishes", "Floor-to-ceiling windows", "Rooftop deck", "Fitness center", "Concierge", "0.5 months free"],
        "images": ["https://photos.zillowstatic.com/fp/bca26fd6e5a7db0cb09eac9f8209b9b5-p_e.webp", "https://photos.zillowstatic.com/fp/c936f8d6957242abda74f0e21f44a81e-p_e.webp"],
        "broker_commission_paid_by": "Owner",
        "original_rent": 8095,
        "net_effective_rent": 7870,
        "free_months": 0.5,
        "lease_term": 18
    },
    {
        "title": "Spacious 2BR/1BA in East Flatbush - Owner Pays Broker Fee",
        "price": 3188,
        "bedrooms": 2,
        "bathrooms": 1,
        "square_feet": 950,
        "location": "1634 Flatbush Avenue #1201, East Flatbush, Brooklyn, NY 11210",
        "neighborhood": "East Flatbush",
        "borough": "Brooklyn",
        "description": "Spacious 2-bedroom in East Flatbush with owner-paid broker commission. Excellent value with 2.25 months free! Modern building with amenities, perfect for families or roommates.",
        "amenities": ["Owner Paid Broker Fee", "2.25 months free", "Modern building", "Family-friendly", "Near subway", "Laundry facilities"],
        "images": ["https://photos.zillowstatic.com/fp/55ef97b580b25b1e1aa87a7486e4178b-p_e.webp", "https://photos.zillowstatic.com/fp/0f1f66b988a70d7860e2a9eb9dc45faa-p_e.webp"],
        "broker_commission_paid_by": "Owner",
        "original_rent": 3750,
        "net_effective_rent": 3188,
        "free_months": 2.25,
        "lease_term": 15
    },
    {
        "title": "Modern 2BR/1BA in Kips Bay - Owner Paid Commission",
        "price": 5969,
        "bedrooms": 2,
        "bathrooms": 1,
        "square_feet": 670,
        "location": "480 2nd Avenue #16E, Kips Bay, Manhattan, NY 10016",
        "neighborhood": "Kips Bay",
        "borough": "Manhattan",
        "description": "Modern 2-bedroom in prime Kips Bay location with owner-paid broker commission. No fee to tenant! Great location near NYU, hospitals, and excellent dining. Managed by Beam Living.",
        "amenities": ["Owner Paid Commission", "Prime Kips Bay location", "Near NYU", "Near hospitals", "Excellent dining", "Beam Living management"],
        "images": ["https://photos.zillowstatic.com/fp/5497fc1532c68856eb6f2e90ec9dbc1c-p_e.webp", "https://photos.zillowstatic.com/fp/3d81fcfd9603a37cca3f6d30a8ccc75e-p_e.webp"],
        "broker_commission_paid_by": "Owner",
        "original_rent": 5969,
        "net_effective_rent": 5969,
        "free_months": 0,
        "lease_term": 12
    },
    {
        "title": "Studio in Bronx with Owner Paid Commission - 4 Months Free",
        "price": 2163,
        "bedrooms": 0,
        "bathrooms": 1,
        "square_feet": 478,
        "location": "40 Bruckner Boulevard #2230, Mott Haven, Bronx, NY 10454",
        "neighborhood": "Mott Haven",
        "borough": "Bronx",
        "description": "Amazing studio deal in the Bronx with owner-paid commission! 4 months free on 13-month lease. Modern building with great amenities and easy Manhattan access.",
        "amenities": ["Owner Paid Commission", "4 months free", "Modern building", "Great amenities", "Manhattan access", "No broker fee"],
        "images": ["https://photos.zillowstatic.com/fp/f54b420bf866a95afe8d696c57c9bb77-p_e.webp", "https://photos.zillowstatic.com/fp/caadee3652cda156ef2667ea6ce5b79b-p_e.webp"],
        "broker_commission_paid_by": "Owner", 
        "original_rent": 3125,
        "net_effective_rent": 2163,
        "free_months": 4,
        "lease_term": 13
    },
    {
        "title": "Luxury 3BR/2.5BA on Upper East Side - Owner Paid Commission",
        "price": 17100,
        "bedrooms": 3,
        "bathrooms": 2.5,
        "square_feet": 1654,
        "location": "356 East 78th Street #19A, Lenox Hill, Manhattan, NY 10075",
        "neighborhood": "Lenox Hill",
        "borough": "Manhattan",
        "description": "Luxury 3-bedroom on prestigious Upper East Side with owner-paid broker commission. 2 months free on 20-month lease! Premium building with doorman and amenities.",
        "amenities": ["Owner Paid Commission", "2 months free", "Prestigious UES", "Doorman building", "Premium amenities", "Lenox Hill location"],
        "images": ["https://photos.zillowstatic.com/fp/281d4f040a63ec544084ad4e7c4fc4ec-p_e.webp", "https://photos.zillowstatic.com/fp/2a6ea1f4b22c74f77d3f9a9174d6b721-p_e.webp"],
        "broker_commission_paid_by": "Owner",
        "original_rent": 19000,
        "net_effective_rent": 17100,
        "free_months": 2,
        "lease_term": 20
    },
    {
        "title": "1BR in Midtown with Owner Commission - Theater District",
        "price": 5393,
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 550,
        "location": "271 West 47th Street #30C, Midtown, Manhattan, NY 10036",
        "neighborhood": "Theater District",
        "borough": "Manhattan",
        "description": "Perfect 1-bedroom in heart of Theater District with owner-paid broker commission. Steps from Broadway theaters, Times Square, and all transportation. Managed by Greystar.",
        "amenities": ["Owner Paid Commission", "Theater District location", "Near Broadway", "Times Square proximity", "All transportation", "Greystar management"],
        "images": ["https://photos.zillowstatic.com/fp/8cea302d825cb2d6327050ed4ab85c65-p_e.webp", "https://photos.zillowstatic.com/fp/bf364ca6a44e1ad7737fa4c223056035-p_e.webp"],
        "broker_commission_paid_by": "Owner",
        "original_rent": 5393,
        "net_effective_rent": 5393,
        "free_months": 0,
        "lease_term": 12
    },
    {
        "title": "1BR in Fort Greene Brooklyn - Owner Paid Commission",
        "price": 6305,
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 650,
        "location": "240 Willoughby Street #17B, Fort Greene, Brooklyn, NY 11205",
        "neighborhood": "Fort Greene",
        "borough": "Brooklyn",
        "description": "Beautiful 1-bedroom in trendy Fort Greene with owner-paid broker commission. 1.25 months free! Great neighborhood with parks, restaurants, and easy Manhattan commute.",
        "amenities": ["Owner Paid Commission", "1.25 months free", "Trendy Fort Greene", "Near parks", "Great restaurants", "Easy Manhattan commute"],
        "images": ["https://photos.zillowstatic.com/fp/1a24b1459067fba384b2db9e3e514b46-p_e.webp", "https://photos.zillowstatic.com/fp/773822f8a9f3b214515a0346ba91fa70-p_e.webp"],
        "broker_commission_paid_by": "Owner",
        "original_rent": 6775,
        "net_effective_rent": 6305,
        "free_months": 1.25,
        "lease_term": 18
    },
    {
        "title": "1BR in Hunters Point Queens - Owner Commission Paid",
        "price": 4870,
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 700,
        "location": "23-10 42nd Road #26B, Hunters Point, Queens, NY 11101",
        "neighborhood": "Hunters Point",
        "borough": "Queens",
        "description": "Modern 1-bedroom in rapidly developing Hunters Point with owner-paid commission. Stunning Manhattan views, waterfront location, and easy commute to Midtown.",
        "amenities": ["Owner Paid Commission", "Manhattan views", "Waterfront location", "Easy Midtown commute", "Hunters Point location", "Modern building"],
        "images": ["https://photos.zillowstatic.com/fp/70df76c137b89972267eda4dae5927b9-p_e.webp", "https://photos.zillowstatic.com/fp/77281c3bc352f30bf070f6e7e7f69d71-p_e.webp"],
        "broker_commission_paid_by": "Owner",
        "original_rent": 4870,
        "net_effective_rent": 4870,
        "free_months": 0,
        "lease_term": 12
    },
    {
        "title": "1BR in Central Harlem - Owner Paid Commission Deal",
        "price": 3840,
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 600,
        "location": "1975 Madison Avenue #204, Central Harlem, Manhattan, NY 10035",
        "neighborhood": "Central Harlem",
        "borough": "Manhattan",
        "description": "Great 1-bedroom deal in Central Harlem with owner-paid commission. 1.5 months free! Up-and-coming neighborhood with great restaurants, near Central Park and multiple subway lines.",
        "amenities": ["Owner Paid Commission", "1.5 months free", "Central Harlem location", "Near Central Park", "Multiple subway lines", "Great restaurants"],
        "images": ["https://photos.zillowstatic.com/fp/721a96858f6dfeeb8d0b6b9015347bff-p_e.webp", "https://photos.zillowstatic.com/fp/b7334359d5aa8f6d888c448cb3a97997-p_e.webp"],
        "broker_commission_paid_by": "Owner",
        "original_rent": 4320,
        "net_effective_rent": 3840,
        "free_months": 1.5,
        "lease_term": 13
    },
    {
        "title": "1BR in Boerum Hill Brooklyn - Owner Commission Paid",
        "price": 3850,
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 580,
        "location": "526 Baltic Street #12L, Boerum Hill, Brooklyn, NY 11217",
        "neighborhood": "Boerum Hill",
        "borough": "Brooklyn",
        "description": "Charming 1-bedroom in historic Boerum Hill with owner-paid commission. 1 month free! Beautiful neighborhood near downtown Brooklyn, with easy access to Manhattan.",
        "amenities": ["Owner Paid Commission", "1 month free", "Historic Boerum Hill", "Near downtown Brooklyn", "Easy Manhattan access", "Charming neighborhood"],
        "images": ["https://photos.zillowstatic.com/fp/b9508ac4d7f29851c17503b9aac757ef-p_e.webp", "https://photos.zillowstatic.com/fp/1d1430d532be8c97c0123dcaab87c447-p_e.webp"],
        "broker_commission_paid_by": "Owner",
        "original_rent": 4200,
        "net_effective_rent": 3850,
        "free_months": 1,
        "lease_term": 12
    },
    {
        "title": "2BR/2BA in North Bronx - Owner Pays All Broker Fees",
        "price": 3392,
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 850,
        "location": "138 Bruckner Boulevard #3449, Mott Haven, Bronx, NY 10454",
        "neighborhood": "Mott Haven",
        "borough": "Bronx",
        "description": "Excellent 2-bedroom deal in developing Mott Haven with owner paying all broker fees. 2.5 months free! New luxury building with premium amenities and easy Manhattan access via multiple trains.",
        "amenities": ["Owner Pays All Fees", "2.5 months free", "New luxury building", "Premium amenities", "Easy Manhattan access", "Multiple train lines"],
        "images": ["https://photos.zillowstatic.com/fp/d5ce9edbc8cc45edd1ea84bb425a49f6-p_e.webp", "https://photos.zillowstatic.com/fp/571065a5970cfcaaeb8c66806dc3fdee-p_e.webp"],
        "broker_commission_paid_by": "Owner",
        "original_rent": 4200,
        "net_effective_rent": 3392,
        "free_months": 2.5,
        "lease_term": 13
    },
    {
        "title": "Elegant 2BR/2BA on Upper East Side - Owner Commission",
        "price": 10500,
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 900,
        "location": "220 East 72nd Street #27C, Lenox Hill, Manhattan, NY 10021",
        "neighborhood": "Lenox Hill",
        "borough": "Manhattan",
        "description": "Elegant 2-bedroom on prestigious Upper East Side with owner-paid commission. Prime Lenox Hill location near Central Park, high-end shopping, and excellent dining.",
        "amenities": ["Owner Paid Commission", "Prestigious UES", "Near Central Park", "High-end shopping", "Excellent dining", "Prime location"],
        "images": ["https://photos.zillowstatic.com/fp/acba1d1fb0b3d9ddeaa78ca1dde8c290-p_e.webp", "https://photos.zillowstatic.com/fp/1b95fdc43a6f2af41e7c330b788174d5-p_e.webp"],
        "broker_commission_paid_by": "Owner", 
        "original_rent": 10500,
        "net_effective_rent": 10500,
        "free_months": 0,
        "lease_term": 12
    }
]

async def add_op_commission_apartments():
    """Add Owner Paid Commission apartments to MongoDB with scattered created_at dates"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.nofeeplaces
    
    print("💼 Adding Owner Paid Commission apartments to database...")
    
    # Base date for scattered creation times (going back 20-60 days)
    base_date = datetime.now()
    
    apartments_added = 0
    
    for i, apt_data in enumerate(op_commission_apartments):
        # Generate scattered created_at dates (20-60 days ago, random times)
        days_ago = random.randint(20, 60)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        created_at = base_date - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # Prepare apartment document
        apartment = {
            "id": str(uuid.uuid4()),
            "title": apt_data["title"],
            "price": apt_data["price"],
            "bedrooms": apt_data["bedrooms"],
            "bathrooms": apt_data["bathrooms"],
            "square_feet": apt_data["square_feet"],
            "location": apt_data["location"],
            "neighborhood": apt_data["neighborhood"],
            "borough": apt_data["borough"],
            "description": apt_data["description"],
            "amenities": apt_data["amenities"],
            "images": apt_data["images"],
            "image": apt_data["images"][0],  # Primary image
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com"
            },
            "availability_status": "Available Now",
            "lease_terms": f"{apt_data['lease_term']}+ months",
            "created_at": created_at,
            "updated_at": created_at,
            "featured": False,
            "verified": True,
            "pets_allowed": True,
            "no_fee": True,
            "broker_fee": 0,
            "broker_commission_paid_by": apt_data["broker_commission_paid_by"],
            "original_rent": apt_data.get("original_rent", apt_data["price"]),
            "net_effective_rent": apt_data.get("net_effective_rent", apt_data["price"]),
            "free_months": apt_data.get("free_months", 0),
            "lease_term_months": apt_data["lease_term"],
            "security_deposit": apt_data["price"],  # Usually one month's rent
            "application_fee": 25,
            "building_type": "Modern High-Rise",
            "parking_available": True,
            "laundry": "In-Building",
            "air_conditioning": "Central Air",
            "heating": "Central Heat",
            "internet_included": False,
            "utilities_included": ["Heat", "Hot Water"],
            "op_commission": True,  # Special flag for Owner Paid commission
            "special_offers": f"{apt_data.get('free_months', 0)} months free" if apt_data.get('free_months', 0) > 0 else "Move-in ready"
        }
        
        # Insert apartment into database
        try:
            await db.apartments.insert_one(apartment)
            apartments_added += 1
            print(f"✅ Added: {apartment['title'][:70]}... (${apartment['price']:,}/mo)")
        except Exception as e:
            print(f"❌ Error adding apartment {i+1}: {str(e)}")
    
    print(f"\n🎉 Successfully added {apartments_added}/{len(op_commission_apartments)} Owner Paid Commission apartments!")
    print("💼 All apartments feature owner-paid broker commissions")
    print("💰 Price range: $2,163 - $17,100/month (net effective)")
    print("🏠 Locations: Manhattan, Brooklyn, Bronx")
    print("📅 Created dates scattered over past 20-60 days for distribution")
    
    # Verify total count
    total_count = await db.apartments.count_documents({})
    op_count = await db.apartments.count_documents({"op_commission": True})
    print(f"📊 Total apartments in database: {total_count}")
    print(f"💼 Total OP commission apartments: {op_count}")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(add_op_commission_apartments())