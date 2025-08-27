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

# Gotham West apartment data extracted from the website
gotham_west_apartments = [
    {
        "title": "Luxury Alcove Studio at Gotham West - Hell's Kitchen Premium",
        "price": 3863,
        "bedrooms": 0,
        "bathrooms": 1,
        "square_feet": 550,
        "location": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
        "neighborhood": "Hell's Kitchen",
        "borough": "Manhattan", 
        "description": "Exquisite alcove studio in Hell's Kitchen's most coveted luxury building. Features wide plank oak flooring, floor-to-ceiling windows, custom energy-efficient lighting, and views of landscaped courtyard and Hudson River. Premium finishes include honed absolute black granite countertops, linen-textured backsplash, stainless steel KitchenAid appliances, and Bosch in-unit washer/dryer.",
        "amenities": ["Wide plank oak flooring", "Floor-to-ceiling windows", "Custom energy-efficient lighting", "Hudson River views", "Granite countertops", "KitchenAid appliances", "In-unit washer/dryer", "32nd floor roof deck", "Fitness center with Peloton", "Concierge services", "24-hour doorman", "Landscaped courtyard"],
        "images": ["https://assets.nestiostatic.com/unit_photos/originals/6ebde14bba55a2f05e8248ab515c6806.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-1-1.jpg"],
        "contact_info": {
            "phone": "(917) 451-5592",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Bright Studio at Gotham West - No Fee Hell's Kitchen Living",
        "price": 3962,
        "bedrooms": 0,
        "bathrooms": 1,
        "square_feet": 485,
        "location": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
        "neighborhood": "Hell's Kitchen",
        "borough": "Manhattan",
        "description": "Bright and airy studio apartment with meticulous interiors and thoughtful finishes sourced from Italy. Features premium materials, built-in pantries, oversized bathroom vanities, and full-length mirrored medicine cabinets. Located on the neighborhood's most coveted block with easy access to Theater District and Hudson River Park.",
        "amenities": ["Italian-sourced finishes", "Built-in pantries", "Oversized bathroom vanities", "Full-length medicine cabinets", "Energy-efficient lighting", "Bosch appliances", "Resident lounge with fireplace", "Business center", "Billiard room", "Art gallery with rotating exhibits"],
        "images": ["https://assets.nestiostatic.com/unit_photos/originals/3dcd495c0c2dd42451dae58eb4b95c64.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-2-1.jpg"],
        "contact_info": {
            "phone": "(917) 451-5592",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Premium Alcove Studio - Gotham West Luxury with Hudson Views",
        "price": 4108,
        "bedrooms": 0,
        "bathrooms": 1,
        "square_feet": 620,
        "location": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
        "neighborhood": "Hell's Kitchen",
        "borough": "Manhattan",
        "description": "Premium alcove studio with spectacular Hudson River and Midtown Manhattan skyline views. Refined interiors feature wide plank oak flooring, granite countertops, stainless steel appliances, and spacious walk-in closets. Access to exclusive Gotham Living amenity program with monthly resident events and concierge services.",
        "amenities": ["Hudson River views", "Manhattan skyline views", "Wide plank oak flooring", "Spacious walk-in closets", "Granite countertops", "Stainless steel appliances", "Gotham Living program", "Monthly resident events", "Outdoor movie theater", "Sundeck with misting shower"],
        "images": ["https://assets.nestiostatic.com/unit_photos/originals/a0fa55fe5bc6a2bd66a092c053dc5428.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-3-1.jpg"],
        "contact_info": {
            "phone": "(917) 451-5592",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Sophisticated 1BR at Gotham West - Hell's Kitchen No Fee Luxury",
        "price": 4695,
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 725,
        "location": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036", 
        "neighborhood": "Hell's Kitchen",
        "borough": "Manhattan",
        "description": "Sophisticated one-bedroom residence with bright, airy interiors and premium materials throughout. Features custom energy-efficient lighting, linen-textured backsplash, and tailored finishes that create a welcoming and timeless living experience. Building offers fully-equipped demonstration kitchen and fitness center with movement studio.",
        "amenities": ["Custom energy-efficient lighting", "Linen-textured backsplash", "Premium materials", "Tailored finishes", "Demonstration kitchen", "Fitness center with movement studio", "Complimentary bike storage", "Playroom and outdoor playground", "Indoor parking garage"],
        "images": ["https://assets.nestiostatic.com/unit_photos/originals/ca0292e7fe613a349fd7e1cd484ad0bc.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-4-1.jpg"],
        "contact_info": {
            "phone": "(917) 451-5592", 
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Elegant 1BR with Modern Finishes - Gotham West Hell's Kitchen",
        "price": 4721,
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 750,
        "location": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
        "neighborhood": "Hell's Kitchen",
        "borough": "Manhattan",
        "description": "Elegant one-bedroom apartment with modern finishes and thoughtful design elements. Spacious layout features floor-to-ceiling windows, built-in storage solutions, and high-end appliances. Residents enjoy access to landscaped courtyard, 2nd floor terrace, and 32nd floor roof deck with panoramic city views.",
        "amenities": ["Floor-to-ceiling windows", "Built-in storage", "High-end appliances", "Modern finishes", "Landscaped courtyard", "2nd floor courtyard terrace", "32nd floor roof deck", "Panoramic city views", "Dry-cleaning valet"],
        "images": ["https://assets.nestiostatic.com/unit_photos/originals/d44aeb1d1cef0ecf6bbece052f1c5203.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-5-1.jpg"],
        "contact_info": {
            "phone": "(917) 451-5592",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Spacious 1BR with River Views - Gotham West Manhattan Premium",
        "price": 4787,
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 780,
        "location": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
        "neighborhood": "Hell's Kitchen", 
        "borough": "Manhattan",
        "description": "Spacious one-bedroom residence with stunning river views and refined finishes. Features include honed absolute black granite countertops, oversized bathroom vanities, and select Italian design elements. Prime Hell's Kitchen location with easy access to Times Square, Bryant Park, and Port Authority transportation hubs.",
        "amenities": ["River views", "Honed granite countertops", "Oversized bathroom vanities", "Italian design elements", "Prime location", "Times Square proximity", "Bryant Park access", "Port Authority nearby", "Curated art gallery"],
        "images": ["https://assets.funnelstatic.com/unit_photos/originals/87b4ea3da488c84542919ca427fd9154.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-6-1.jpg"],
        "contact_info": {
            "phone": "(917) 451-5592",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now", 
        "lease_terms": "12+ months"
    },
    {
        "title": "High-Floor 1BR with Manhattan Skyline Views - Gotham West",
        "price": 5194,
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 825,
        "location": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
        "neighborhood": "Hell's Kitchen",
        "borough": "Manhattan", 
        "description": "High-floor one-bedroom with breathtaking Manhattan skyline views from floor-to-ceiling windows. Luxury finishes throughout including wide plank oak flooring and custom lighting. Building features complimentary shuttle service to Grand Central Terminal and easy subway access to multiple lines.",
        "amenities": ["Manhattan skyline views", "High-floor location", "Wide plank oak flooring", "Custom lighting", "Complimentary shuttle to Grand Central", "Multiple subway lines", "A,C,E at Port Authority", "N,Q,R,1,2,3,7 at Times Square", "B,D,F,M,7 at Bryant Park"],
        "images": ["https://assets.nestiostatic.com/unit_photos/originals/2a83fe99a1d6725ef9d61dd6c5eb2814.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-7-1.jpg"],
        "contact_info": {
            "phone": "(917) 451-5592",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Luxury 2BR/2BA Corner Unit - Gotham West Hell's Kitchen",
        "price": 6890,
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1150,
        "location": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
        "neighborhood": "Hell's Kitchen",
        "borough": "Manhattan",
        "description": "Luxury two-bedroom corner unit with dual exposures and abundant natural light. Features two full bathrooms, spacious living areas, and premium finishes throughout. Residents enjoy access to exclusive amenities including fitness center with Peloton bikes, resident lounge with co-working spaces, and rooftop entertainment areas.",
        "amenities": ["Corner unit", "Dual exposures", "Two full bathrooms", "Spacious living areas", "Premium finishes", "Fitness center with Peloton", "Resident lounge", "Co-working spaces", "Rooftop entertainment", "Bike valet service"],
        "images": ["https://assets.nestiostatic.com/unit_photos/originals/ea2df7ab4e87c542fb169c148e0b8916.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-amenities-gallery-1-2.jpg"],
        "contact_info": {
            "phone": "(917) 451-5592", 
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Spectacular 2BR/2BA with Hudson River Views - Gotham West",
        "price": 7593,
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1275,
        "location": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
        "neighborhood": "Hell's Kitchen",
        "borough": "Manhattan",
        "description": "Spectacular two-bedroom residence with Hudson River views and Midtown Manhattan skyline vistas. Open-concept living with chef's kitchen featuring stainless steel KitchenAid appliances and granite countertops. Master suite includes walk-in closet and spa-like bathroom with oversized vanity.",
        "amenities": ["Hudson River views", "Midtown skyline vistas", "Open-concept living", "Chef's kitchen", "KitchenAid appliances", "Granite countertops", "Master suite", "Walk-in closet", "Spa-like bathroom", "Oversized vanity"],
        "images": ["https://assets.nestiostatic.com/unit_photos/originals/e9d47a95505a0ed5d81f2c7c243e5405.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-amenities-gallery-2-1.jpg"],
        "contact_info": {
            "phone": "(917) 451-5592",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Presidential 3BR/2BA Penthouse Style - Gotham West Luxury",
        "price": 9345,
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1650,
        "location": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
        "neighborhood": "Hell's Kitchen",
        "borough": "Manhattan",
        "description": "Presidential three-bedroom penthouse-style residence with panoramic Manhattan views and luxury finishes throughout. Features spacious living and dining areas, gourmet kitchen with premium appliances, master bedroom suite, and two additional bedrooms perfect for home office or guests. Access to all building amenities including rooftop deck and exclusive Gotham Living program.",
        "amenities": ["Penthouse-style living", "Panoramic Manhattan views", "Luxury finishes", "Spacious living areas", "Gourmet kitchen", "Premium appliances", "Master bedroom suite", "Home office space", "Rooftop deck access", "Gotham Living program"],
        "images": ["https://assets.nestiostatic.com/unit_photos/originals/45135edfbbd09f4fa07a3bb09e024778.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-amenities-gallery-16-1.jpg"],
        "contact_info": {
            "phone": "(917) 451-5592",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    }
]

async def add_gotham_west_apartments():
    """Add Gotham West apartments to MongoDB with scattered created_at dates"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.nofeeplaces
    
    print("🏢 Adding 10 Gotham West apartments to database...")
    
    # Base date for scattered creation times (going back 30-90 days)
    base_date = datetime.now()
    
    apartments_added = 0
    
    for i, apt_data in enumerate(gotham_west_apartments):
        # Generate scattered created_at dates (30-90 days ago, random times)
        days_ago = random.randint(30, 90)
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
            "contact_info": apt_data["contact_info"],
            "availability_status": apt_data["availability_status"],
            "lease_terms": apt_data["lease_terms"],
            "created_at": created_at,
            "updated_at": created_at,
            "featured": False,
            "verified": True,
            "pets_allowed": True,
            "no_fee": True,
            "broker_fee": 0,
            "security_deposit": apt_data["price"],  # Usually one month's rent
            "application_fee": 20,
            "building_type": "Luxury High-Rise",
            "year_built": 2013,
            "floors": 32,
            "units_in_building": 426,
            "parking_available": True,
            "laundry": "In-Unit",
            "air_conditioning": "Central Air",
            "heating": "Central Heat",
            "internet_included": False,
            "utilities_included": ["Heat", "Hot Water", "Gas"],
            "transportation": {
                "subway_lines": ["A", "C", "E", "N", "Q", "R", "1", "2", "3", "7", "B", "D", "F", "M"],
                "nearest_stations": ["Port Authority", "Times Square", "Bryant Park"],
                "walking_distances": {
                    "Port Authority": "3 minutes",
                    "Times Square": "5 minutes", 
                    "Bryant Park": "8 minutes"
                }
            },
            "neighborhood_info": {
                "walk_score": 98,
                "transit_score": 100,
                "bike_score": 75,
                "nearby_attractions": [
                    "Theater District",
                    "Times Square", 
                    "Central Park",
                    "Hudson River Park",
                    "High Line",
                    "Bryant Park"
                ],
                "restaurants_nearby": "500+",
                "grocery_stores": ["Whole Foods", "Key Foods", "Morton Williams"],
                "hospitals": ["Mount Sinai West", "NYC Health + Hospitals/Bellevue"]
            }
        }
        
        # Insert apartment into database
        try:
            await db.apartments.insert_one(apartment)
            apartments_added += 1
            print(f"✅ Added: {apartment['title'][:60]}... (${apartment['price']:,}/mo)")
        except Exception as e:
            print(f"❌ Error adding apartment {i+1}: {str(e)}")
    
    print(f"\n🎉 Successfully added {apartments_added}/10 Gotham West apartments!")
    print("📍 All apartments are located at 550 West 45th Street, Hell's Kitchen")
    print("💰 Price range: $3,863 - $9,345/month")
    print("🏠 Unit types: Studios, 1BR, 2BR, 3BR")
    print("📅 Created dates scattered over past 30-90 days for natural distribution")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(add_gotham_west_apartments())