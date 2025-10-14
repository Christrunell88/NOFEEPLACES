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

# Waterline Square apartments data (the missing 8 apartments)
waterline_apartments = [
    {
        "title": "Studio at Waterline Square - Hudson River Views No Fee",
        "price": 6229,
        "bedrooms": 0,
        "bathrooms": 1,
        "square_feet": 550,
        "location": "400 West 61st Street, Upper West Side, Manhattan, NY 10069",
        "neighborhood": "Upper West Side",
        "borough": "Manhattan",
        "description": "Luxury studio at Waterline Square with stunning Hudson River views. Features floor-to-ceiling windows, premium finishes, and access to resort-style amenities including rooftop deck, fitness center, and concierge services. No broker fee.",
        "amenities": ["Hudson River views", "Floor-to-ceiling windows", "Premium finishes", "Rooftop deck", "Fitness center", "Concierge services", "Swimming pool", "Spa", "Private park", "Pet spa"],
        "images": ["https://images.waterline-square.com/studio-river-view.jpg", "https://images.waterline-square.com/building-exterior.jpg"],
        "contact_info": {
            "phone": "(646) 408-8048",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Spacious 1BR at Waterline Square - Modern Luxury Living",
        "price": 7496,
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 750,
        "location": "400 West 61st Street, Upper West Side, Manhattan, NY 10069",
        "neighborhood": "Upper West Side",
        "borough": "Manhattan",
        "description": "Spacious one-bedroom apartment at Waterline Square featuring modern luxury living with river views. Open kitchen with premium appliances, marble bathrooms, and access to world-class amenities.",
        "amenities": ["River views", "Modern kitchen", "Premium appliances", "Marble bathrooms", "World-class amenities", "24/7 concierge", "Fitness center", "Swimming pool"],
        "images": ["https://images.waterline-square.com/1br-modern.jpg", "https://images.waterline-square.com/amenities.jpg"],
        "contact_info": {
            "phone": "(646) 408-8048",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Premium 1BR with Den - Waterline Square Upper West Side",
        "price": 9995,
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 890,
        "location": "400 West 61st Street, Upper West Side, Manhattan, NY 10069",
        "neighborhood": "Upper West Side",
        "borough": "Manhattan",
        "description": "Premium one-bedroom with den at Waterline Square offering luxury Upper West Side living. Features panoramic city and river views, chef's kitchen, and spa-like bathroom. Den perfect for home office or guest area.",
        "amenities": ["Panoramic views", "Chef's kitchen", "Spa-like bathroom", "Den/home office", "Luxury finishes", "Smart home technology", "Private balcony", "Resort amenities"],
        "images": ["https://images.waterline-square.com/1br-den.jpg", "https://images.waterline-square.com/river-view.jpg"],
        "contact_info": {
            "phone": "(646) 408-8048",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Luxury 2BR/2BA at Waterline Square - River Views",
        "price": 12500,
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1200,
        "location": "400 West 61st Street, Upper West Side, Manhattan, NY 10069",
        "neighborhood": "Upper West Side",
        "borough": "Manhattan",
        "description": "Luxury two-bedroom, two-bathroom residence with stunning river views at Waterline Square. Master suite with walk-in closet, gourmet kitchen with island, and access to private park and resort-style amenities.",
        "amenities": ["Stunning river views", "Master suite", "Walk-in closet", "Gourmet kitchen", "Private park", "Resort amenities", "Swimming pool", "Spa", "24/7 doorman"],
        "images": ["https://images.waterline-square.com/2br-luxury.jpg", "https://images.waterline-square.com/master-suite.jpg"],
        "contact_info": {
            "phone": "(646) 408-8048",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Stunning 2BR Corner Unit - Waterline Square Premium",
        "price": 15200,
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1350,
        "location": "400 West 61st Street, Upper West Side, Manhattan, NY 10069",
        "neighborhood": "Upper West Side",
        "borough": "Manhattan",
        "description": "Stunning corner two-bedroom unit at Waterline Square with premium finishes and dual exposures. Floor-to-ceiling windows, marble bathrooms, custom millwork, and access to exclusive amenities.",
        "amenities": ["Corner unit", "Dual exposures", "Floor-to-ceiling windows", "Marble bathrooms", "Custom millwork", "Exclusive amenities", "Concierge", "Valet parking"],
        "images": ["https://images.waterline-square.com/2br-corner.jpg", "https://images.waterline-square.com/luxury-bath.jpg"],
        "contact_info": {
            "phone": "(646) 408-8048",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Luxurious 2BR/2.5BA Duplex Style - Waterline Square Premium",
        "price": 18900,
        "bedrooms": 2,
        "bathrooms": 2.5,
        "square_feet": 1500,
        "location": "400 West 61st Street, Upper West Side, Manhattan, NY 10069",
        "neighborhood": "Upper West Side",
        "borough": "Manhattan",
        "description": "Luxurious duplex-style two-bedroom with 2.5 bathrooms at Waterline Square. Two-story layout with soaring ceilings, private terrace, and unobstructed river views. Premium appliances and finishes throughout.",
        "amenities": ["Duplex layout", "Soaring ceilings", "Private terrace", "Unobstructed river views", "Premium appliances", "Luxury finishes", "Two-story living", "Private entrance"],
        "images": ["https://images.waterline-square.com/duplex.jpg", "https://images.waterline-square.com/terrace.jpg"],
        "contact_info": {
            "phone": "(646) 408-8048",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Spectacular 3BR/2.5BA - Waterline Square Luxury Residence",
        "price": 22400,
        "bedrooms": 3,
        "bathrooms": 2.5,
        "square_feet": 1800,
        "location": "400 West 61st Street, Upper West Side, Manhattan, NY 10069",
        "neighborhood": "Upper West Side",
        "borough": "Manhattan",
        "description": "Spectacular three-bedroom luxury residence at Waterline Square with 2.5 bathrooms. Expansive living spaces, chef's kitchen with breakfast bar, master suite with river views, and two additional bedrooms perfect for family living.",
        "amenities": ["Three bedrooms", "Expansive living", "Chef's kitchen", "Breakfast bar", "Master suite with views", "Family living", "Luxury building", "Full service"],
        "images": ["https://images.waterline-square.com/3br-luxury.jpg", "https://images.waterline-square.com/chefs-kitchen.jpg"],
        "contact_info": {
            "phone": "(646) 408-8048",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    },
    {
        "title": "Grand 4BR/3.5BA Family Residence - Waterline Square Premium",
        "price": 28750,
        "bedrooms": 4,
        "bathrooms": 3.5,
        "square_feet": 2200,
        "location": "400 West 61st Street, Upper West Side, Manhattan, NY 10069",
        "neighborhood": "Upper West Side",
        "borough": "Manhattan",
        "description": "Grand four-bedroom family residence with 3.5 bathrooms at Waterline Square. Sprawling layout with multiple living areas, formal dining room, private study, and panoramic Hudson River views. Perfect for families.",
        "amenities": ["Four bedrooms", "Multiple living areas", "Formal dining", "Private study", "Panoramic Hudson views", "Family residence", "Sprawling layout", "Premium building"],
        "images": ["https://images.waterline-square.com/4br-family.jpg", "https://images.waterline-square.com/dining-room.jpg"],
        "contact_info": {
            "phone": "(646) 408-8048",
            "email": "placesnyc88@gmail.com"
        },
        "availability_status": "Available Now",
        "lease_terms": "12+ months"
    }
]

async def add_waterline_apartments():
    """Add Waterline Square apartments to MongoDB with scattered created_at dates"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.nofeeplaces
    
    print("🏢 Adding 8 Waterline Square apartments to database...")
    
    # Base date for scattered creation times (going back 45-120 days)
    base_date = datetime.now()
    
    apartments_added = 0
    
    for i, apt_data in enumerate(waterline_apartments):
        # Generate scattered created_at dates (45-120 days ago, random times)
        days_ago = random.randint(45, 120)
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
            "application_fee": 50,
            "building_type": "Luxury High-Rise",
            "year_built": 2018,
            "floors": 38,
            "units_in_building": 1132,
            "parking_available": True,
            "laundry": "In-Unit",
            "air_conditioning": "Central Air",
            "heating": "Central Heat",
            "internet_included": False,
            "utilities_included": ["Heat", "Hot Water"],
            "transportation": {
                "subway_lines": ["1", "2", "3", "A", "B", "C", "D"],
                "nearest_stations": ["59th St-Columbus Circle", "66th St-Lincoln Center"],
                "walking_distances": {
                    "59th St-Columbus Circle": "4 minutes",
                    "66th St-Lincoln Center": "6 minutes",
                    "72nd St": "8 minutes"
                }
            },
            "neighborhood_info": {
                "walk_score": 95,
                "transit_score": 100,
                "bike_score": 80,
                "nearby_attractions": [
                    "Lincoln Center",
                    "Central Park",
                    "Hudson River Park",
                    "Columbus Circle",
                    "Time Warner Center",
                    "Riverside Park"
                ],
                "restaurants_nearby": "200+",
                "grocery_stores": ["Whole Foods", "Trader Joe's", "Fairway Market"],
                "hospitals": ["Mount Sinai West", "NewYork-Presbyterian"]
            }
        }
        
        # Insert apartment into database
        try:
            await db.apartments.insert_one(apartment)
            apartments_added += 1
            print(f"✅ Added: {apartment['title'][:60]}... (${apartment['price']:,}/mo)")
        except Exception as e:
            print(f"❌ Error adding apartment {i+1}: {str(e)}")
    
    print(f"\n🎉 Successfully added {apartments_added}/8 Waterline Square apartments!")
    print("📍 All apartments are located at 400 West 61st Street, Upper West Side")
    print("💰 Price range: $6,229 - $28,750/month")
    print("🏠 Unit types: Studios, 1BR, 2BR, 3BR, 4BR")
    print("📅 Created dates scattered over past 45-120 days for natural distribution")
    
    # Verify total count
    total_count = await db.apartments.count_documents({})
    print(f"📊 Total apartments in database: {total_count}")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(add_waterline_apartments())