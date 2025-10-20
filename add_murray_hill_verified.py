#!/usr/bin/env python3
"""
Add verified listing from Manhattan Skyline - The Murray Hill Studio
Source: https://manhattanskyline.com/buildings/murray-hill/the-murray-hill/apartment-vckvbfgb
"""

from pymongo import MongoClient
import os
import uuid
from datetime import datetime

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

def add_murray_hill_listing():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("="*80)
    print("ADDING VERIFIED LISTING: THE MURRAY HILL STUDIO")
    print("="*80)
    
    # Apartment data extracted from Manhattan Skyline
    apartment = {
        "id": str(uuid.uuid4()),
        "title": "Studio at The Murray Hill - No Fee, South-Facing with Abundant Sunlight",
        "description": "This large studio faces South, has a great layout and enjoys abundant sunlight. Kitchen is separate from the large living room and comes with custom solid wood cabinetry, stainless steel appliances, and granite countertops. Bathroom features ceramic tile and tri-view medicine cabinet. In addition, this home has ample closet space. A 24-hour doorman building, The Murray Hill has a fantastic staff with Resident Manager, a landscaped and furnished roof deck. Complimentary amenity package offers membership to fully-equipped fitness center, tenant lounge and bicycle storage.",
        
        # Price and basics
        "price": 3600,
        "bedrooms": 0,  # Studio
        "bathrooms": 1.0,
        "sqft": None,  # Not specified
        
        # Location
        "address": "115 East 34th Street",
        "location": "Murray Hill, Manhattan",
        "neighborhood": "Murray Hill",
        "borough": "Manhattan",
        "building_name": "The Murray Hill",
        "unit_number": None,
        "zip_code": "10016",
        
        # Images (from the listing)
        "images": [
            "https://manhattanskyline.com/storage/_styles/multi-hero/unit/ENNOSTH5xXdydzxcJKjdqyZg63Pee20tQQ7MrraS.jpg",
            "https://manhattanskyline.com/storage/_styles/multi-hero/unit/spBiXXoLk14mUDjzlQ7QEZVJ1aIWxjuORlgCyZj5.jpg",
            "https://manhattanskyline.com/storage/_styles/multi-hero/unit/sPfCOGiCqiLsyKk1cQ6UDd4zfYUaYkTEEqAwoQLV.jpg",
            "https://manhattanskyline.com/storage/_styles/multi-hero/building/K6kH6objdNmCJpzIFTH6xl7QmZqtlKuGfbcVFSwX.jpg",
            "https://manhattanskyline.com/storage/_styles/multi-hero/building/VMpoNfdlkSxeoh5YAmouCJxtaNJ55eOqko84XCiU.jpg",
            "https://manhattanskyline.com/storage/_styles/multi-hero/building/Z2zNY9M1TLSaPUejWGUGMgjVNDqrBxsEiuQvlewT.jpg",
            "https://manhattanskyline.com/storage/_styles/multi-hero/building/vNrHaoEOl9Fwgo1CcpTM9KaHfVBvivL9HUOAUk2m.jpeg",
            "https://manhattanskyline.com/storage/_styles/multi-hero/building/UJs13pXCjv6bxE4XPCaXlRBCUiYlpqjgCNeiiImk.jpeg",
            "https://manhattanskyline.com/storage/_styles/multi-hero/building/DNYPgFQXGmakkKyBkyiSUiEw6t6KNsf5UaxDyJEj.jpeg"
        ],
        
        # Amenities
        "amenities": [
            "24-Hour Doorman",
            "Resident Manager",
            "Landscaped Roof Deck",
            "Furnished Roof Deck",
            "Fitness Center",
            "Tenant Lounge",
            "Bicycle Storage",
            "Laundry in Building",
            "Elevator",
            "Pet Friendly",
            "Courtyard",
            "Granite Countertops",
            "Stainless Steel Appliances",
            "Microwave",
            "Custom Wood Cabinetry",
            "Ceramic Tile Bathroom",
            "Ample Closet Space"
        ],
        
        # Listing details
        "broker_fee": "No fee",
        "available": True,
        "available_date": "Immediate",
        "lease_terms": "1 year",
        "pet_policy": "Pet Friendly",
        "utilities": "Not included",
        "deposit": "Security deposit alternative available via The Guarantors",
        
        # Verification
        "is_verified": True,
        "is_real": True,
        "is_featured": True,
        "quality_score": 95,
        "verification_status": "Verified by Manhattan Skyline",
        "data_source": "Manhattan Skyline",
        "listing_type": "Direct",
        "source_database": "nofeeplaces_database",
        "source_url": "https://manhattanskyline.com/buildings/murray-hill/the-murray-hill/apartment-vckvbfgb",
        
        # Contact
        "contact_email": "placesfirm@gmail.com",
        "contact_phone": "+1-347-728-0315",
        "leasing_phone": "+1-347-728-0315",
        
        # Transportation (from listing)
        "transportation": {
            "subway_lines": ["6", "4", "5", "7", "S", "N", "Q", "R", "W", "B", "D", "F", "M", "PATH"],
            "nearest_stations": [
                "33rd St/Park Ave South (6) - 2 min walk",
                "Grand Central Station (4,5,6,7,S) - 8 min walk",
                "34th St/Herald Square (N,Q,R,W,B,D,F,M,PATH) - 9 min walk"
            ],
            "bus_lines": ["M101", "M102", "M103", "M34"]
        },
        
        # Neighborhood info
        "neighborhood_info": {
            "description": "With a lively nightlife, rows of bars and restaurants, and proximity to offices in Midtown East, people flock to Murray Hill and its neighbor, Kips Bay. An excellent array of housing stock includes full service, doorman high rise buildings loaded with amenities. Grand Central Station is a short distance away and allows residents to plan for quick out of the city getaways.",
            "nearby_restaurants": ["2nd Avenue Deli", "Medium Rare", "Murray Hill Diner", "Ruby's", "Shake Shack", "Sticky's"],
            "nearby_shops": ["D'Agostino Supermarkets", "Fairway Market", "Trader Joe's"],
            "nearby_coffee": ["Arvaci Coffee", "Birch Coffee", "Charlotte Cafe", "Perk Coffee", "Semicolon Cafe"],
            "nearby_fitness": ["Crunch Fitness", "Equinox", "New York Sports Club"],
            "nearby_entertainment": ["AMC Movie Theater"]
        },
        
        # Timestamps
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_verified": datetime.utcnow(),
        
        # SEO
        "seo_title": "No Fee Studio at The Murray Hill - $3,600/mo - Murray Hill, Manhattan",
        "seo_description": "South-facing studio with separate kitchen, granite countertops, stainless steel appliances. 24-hour doorman, roof deck, fitness center. Pet friendly. No broker fee.",
        "seo_keywords": ["no fee apartment", "murray hill studio", "doorman building", "manhattan studio", "pet friendly", "roof deck", "fitness center"]
    }
    
    # Check if already exists
    existing = db.apartments.find_one({
        "address": apartment["address"],
        "building_name": apartment["building_name"],
        "price": apartment["price"]
    })
    
    if existing:
        print(f"\n⚠️  Apartment already exists in database:")
        print(f"   ID: {existing['id']}")
        print(f"   Title: {existing['title']}")
        print(f"\n   Updating instead of creating duplicate...")
        
        # Update existing
        db.apartments.update_one(
            {"id": existing["id"]},
            {"$set": {
                **apartment,
                "id": existing["id"],  # Keep original ID
                "created_at": existing.get("created_at", datetime.utcnow())  # Keep original created date
            }}
        )
        print(f"   ✅ Updated successfully")
    else:
        # Insert new
        db.apartments.insert_one(apartment)
        print(f"\n✅ NEW LISTING ADDED:")
        print(f"   ID: {apartment['id']}")
        print(f"   Title: {apartment['title']}")
        print(f"   Price: ${apartment['price']:,.0f}/month")
        print(f"   Location: {apartment['address']}, {apartment['neighborhood']}")
        print(f"   Building: {apartment['building_name']}")
        print(f"   Type: Studio, 1 Bath")
        print(f"   Amenities: {len(apartment['amenities'])} features")
        print(f"   Images: {len(apartment['images'])} high-quality photos")
        print(f"   Broker Fee: {apartment['broker_fee']}")
        print(f"   Verified: {apartment['is_verified']}")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"DATABASE SUMMARY")
    print(f"{'='*80}")
    
    total_apts = db.apartments.count_documents({})
    murray_hill_apts = db.apartments.count_documents({"neighborhood": "Murray Hill"})
    no_fee_apts = db.apartments.count_documents({"broker_fee": "No fee"})
    
    print(f"Total apartments: {total_apts}")
    print(f"Murray Hill apartments: {murray_hill_apts}")
    print(f"No fee apartments: {no_fee_apts}")
    
    client.close()
    
    print(f"\n✅ Listing is now live on NoFeePlaces.com!")
    print(f"   Users can search and view this apartment immediately")

if __name__ == "__main__":
    add_murray_hill_listing()
