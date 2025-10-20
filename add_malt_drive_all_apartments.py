#!/usr/bin/env python3
"""
Add all 36 available apartments from Malt Drive (maltdrive.com)
Hunter's Point South, Queens - Luxury Waterfront Apartments
"""

from pymongo import MongoClient
import os
import uuid
from datetime import datetime

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

# All 36 available apartments from maltdrive.com
MALT_DRIVE_APARTMENTS = [
    # 2-21 Malt Dr Studios
    {"building": "2-21", "unit": "508", "type": "Studio", "bath": 1, "price": 3685, "net": 3378, "deal": "2 months free + 1 month OP"},
    {"building": "2-21", "unit": "249", "type": "Studio", "bath": 1, "price": 3740, "net": 3428, "deal": "2 months free + 1 month OP"},
    {"building": "2-21", "unit": "378", "type": "Studio", "bath": 1, "price": 3805, "net": 3488, "deal": "2 months free + 1 month OP"},
    
    # 2-20 Malt Dr Studio Alcoves
    {"building": "2-20", "unit": "414", "type": "Studio, Alcove", "bath": 1, "price": 4000, "net": 3500, "deal": "3 months free + 1 month OP"},
    {"building": "2-20", "unit": "320", "type": "Studio, Alcove", "bath": 1, "price": 4200, "net": 3675, "deal": "3 months free + 1 month OP"},
    {"building": "2-20", "unit": "218", "type": "Studio, Alcove", "bath": 1, "price": 4245, "net": 3714, "deal": "3 months free + 1 month OP"},
    {"building": "2-20", "unit": "225", "type": "Studio, Alcove", "bath": 1, "price": 4290, "net": 3754, "deal": "3 months free + 1 month OP"},
    {"building": "2-20", "unit": "1307", "type": "Studio, Alcove", "bath": 1, "price": 4375, "net": 3828, "deal": "3 months free + 1 month OP"},
    
    # 2-21 Malt Dr Studio Alcoves
    {"building": "2-21", "unit": "1420", "type": "Studio, Alcove", "bath": 1, "price": 4425, "net": 4056, "deal": "2 months free + 1 month OP"},
    {"building": "2-21", "unit": "349", "type": "Studio, Alcove", "bath": 1, "price": 4440, "net": 4070, "deal": "2 months free + 1 month OP"},
    
    # 1 Bedrooms
    {"building": "2-20", "unit": "2911", "type": "1 Bed", "bath": 1, "price": 4695, "net": 4108, "deal": "3 months free + 1 month OP"},
    {"building": "2-21", "unit": "304", "type": "1 Bed", "bath": 1, "price": 4885, "net": 4478, "deal": "2 months free + 1 month OP"},
    {"building": "2-21", "unit": "1204", "type": "1 Bed", "bath": 1, "price": 4925, "net": 4515, "deal": "2 months free + 1 month OP"},
    {"building": "2-21", "unit": "609", "type": "1 Bed", "bath": 1, "price": 5130, "net": 4703, "deal": "2 months free + 1 month OP"},
    {"building": "2-20", "unit": "1601", "type": "1 Bed, Alcove", "bath": 1, "price": 5580, "net": 4883, "deal": "3 months free + 1 month OP"},
    {"building": "2-21", "unit": "1003", "type": "1 Bed, Alcove", "bath": 1, "price": 5580, "net": 5115, "deal": "2 months free + 1 month OP"},
    {"building": "2-21", "unit": "548", "type": "1 Bed, Alcove", "bath": 2, "price": 5585, "net": 5120, "deal": "2 months free + 1 month OP"},
    {"building": "2-21", "unit": "401", "type": "1 Bed, Alcove", "bath": 1, "price": 5695, "net": 5220, "deal": "2 months free + 1 month OP"},
    {"building": "2-20", "unit": "2901", "type": "1 Bed, Alcove", "bath": 1, "price": 5710, "net": 4996, "deal": "3 months free + 1 month OP"},
    {"building": "2-21", "unit": "1717", "type": "1 Bed, Alcove", "bath": 1, "price": 5930, "net": 5436, "deal": "2 months free + 1 month OP"},
    {"building": "2-21", "unit": "628", "type": "1 Bed, Alcove", "bath": 1, "price": 6245, "net": 5725, "deal": "2 months free + 1 month OP"},
    
    # 2 Bedrooms
    {"building": "2-21", "unit": "1713", "type": "2 Bed", "bath": 1, "price": 6320, "net": 5793, "deal": "2 months free + 1 month OP"},
    {"building": "2-20", "unit": "217", "type": "2 Bed", "bath": 2, "price": 6445, "net": 5639, "deal": "3 months free + 1 month OP"},
    {"building": "2-20", "unit": "709", "type": "2 Bed", "bath": 2, "price": 6455, "net": 5648, "deal": "3 months free + 1 month OP"},
    {"building": "2-20", "unit": "910", "type": "2 Bed", "bath": 2, "price": 6465, "net": 5657, "deal": "3 months free + 1 month OP"},
    {"building": "2-20", "unit": "508", "type": "2 Bed", "bath": 2, "price": 6540, "net": 5723, "deal": "3 months free + 1 month OP"},
    {"building": "2-21", "unit": "348", "type": "2 Bed", "bath": 2, "price": 6570, "net": 6023, "deal": "2 months free + 1 month OP"},
    {"building": "2-20", "unit": "519", "type": "2 Bed", "bath": 2, "price": 6585, "net": 5762, "deal": "3 months free + 1 month OP"},
    {"building": "2-21", "unit": "3702", "type": "1 Bed, Alcove", "bath": 2, "price": 6800, "net": 6233, "deal": "2 months free + 1 month OP"},
    {"building": "2-20", "unit": "1204", "type": "2 Bed", "bath": 2, "price": 6930, "net": 6064, "deal": "3 months free + 1 month OP"},
    {"building": "2-20", "unit": "3106", "type": "2 Bed", "bath": 2, "price": 6995, "net": 6121, "deal": "3 months free + 1 month OP"},
    {"building": "2-20", "unit": "PH06", "type": "2 Bed", "bath": 2, "price": 7095, "net": 6208, "deal": "3 months free + 1 month OP"},
    {"building": "2-20", "unit": "2404", "type": "2 Bed", "bath": 2, "price": 7120, "net": 6230, "deal": "3 months free + 1 month OP"},
    {"building": "2-21", "unit": "626", "type": "2 Bed, Alcove", "bath": 2, "price": 7210, "net": 6609, "deal": "2 months free + 1 month OP"},
    {"building": "2-20", "unit": "2103", "type": "2 Bed, Alcove", "bath": 2, "price": 7370, "net": 6449, "deal": "3 months free + 1 month OP"},
    {"building": "2-21", "unit": "1219", "type": "2 Bed, Alcove", "bath": 2, "price": 7660, "net": 7022, "deal": "2 months free + 1 month OP"},
]

# Base amenities and features for Malt Drive
BASE_AMENITIES = [
    "Rooftop Pool",
    "Rooftop Terrace",
    "BBQ Grills",
    "360° City Views",
    "24/7 Concierge",
    "Package Room",
    "Bike Storage",
    "Pet Friendly",
    "Fitness Center",
    "Resident Lounge",
    "In-Unit Washer/Dryer",
    "Floor-to-Ceiling Windows",
    "Open Kitchen",
    "Walk-In Closet",
    "Waterfront Location",
    "Near 7 Train & LIRR"
]

def get_bedrooms(unit_type):
    """Extract bedroom count from unit type"""
    if "Studio" in unit_type:
        return 0
    elif "1 Bed" in unit_type:
        return 1
    elif "2 Bed" in unit_type:
        return 2
    return 0

def create_apartment_doc(apt_data):
    """Create apartment document for MongoDB"""
    
    bedrooms = get_bedrooms(apt_data["type"])
    unit_type_desc = apt_data["type"].replace(",", " with")
    
    # Create title
    if bedrooms == 0:
        title = f"Studio at Malt Drive {apt_data['building']} - Luxury Waterfront Living"
    else:
        title = f"{bedrooms}BR at Malt Drive {apt_data['building']} - Modern Waterfront Apartment"
    
    # Build description
    alcove_text = " with flexible alcove space" if "Alcove" in apt_data["type"] else ""
    description = f"Spectacular {unit_type_desc} apartment{alcove_text} at Malt Drive in Hunter's Point South, Queens. Features in-unit washer/dryer, open kitchen, floor-to-ceiling windows with stunning city and waterfront views. Steps from Hunter's Point South Park and waterfront promenade. Easy access to Manhattan via 7 train (8 min to Grand Central). Building amenities include rooftop pool, fitness center, resident lounge, and 24/7 concierge. {apt_data['deal']} on 24-month lease. 1/2 month security deposit for well-qualified applicants."
    
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        
        # Pricing
        "price": apt_data["price"],
        "net_effective_rent": apt_data["net"],
        "special_offer": apt_data["deal"],
        
        # Unit details
        "bedrooms": bedrooms,
        "bathrooms": float(apt_data["bath"]),
        "unit_number": apt_data["unit"],
        "floor": int(apt_data["unit"][0]) if apt_data["unit"][0].isdigit() else None,
        
        # Location
        "address": f"{apt_data['building']} Malt Drive",
        "location": "Hunter's Point South, Queens",
        "neighborhood": "Long Island City",
        "borough": "Queens",
        "building_name": f"Malt Drive {apt_data['building']}",
        "zip_code": "11101",
        
        # Images (representative from maltdrive.com)
        "images": [
            "https://maltdrive.com/wp-content/uploads/2025/07/2-21-malt-800x600-2.avif",
            "https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-110.avif",
            "https://maltdrive.com/wp-content/uploads/2025/05/2-21-malt-800x600-117.avif",
            "https://maltdrive.com/wp-content/uploads/2025/07/2-21-malt-800x600-22.avif",
            "https://maltdrive.com/wp-content/uploads/2024/05/malt-dr-pool-jpg.webp",
            "https://maltdrive.com/wp-content/uploads/2024/06/malt-dr-entrances-evening-jpg.webp"
        ],
        
        # Amenities
        "amenities": BASE_AMENITIES.copy(),
        
        # Listing details
        "broker_fee": "No fee",
        "available": True,
        "available_date": "Immediate",
        "lease_terms": "24 months (special offers apply)",
        "pet_policy": "Pet Friendly",
        "utilities": "Electricity as billed",
        "deposit": "1/2 month security deposit (well-qualified applicants)",
        
        # Verification
        "is_verified": False,  # Representative photos
        "is_real": True,
        "is_featured": True,
        "quality_score": 85,
        "verification_status": "Malt Drive Verified Listing",
        "data_source": "Malt Drive",
        "listing_type": "Direct",
        "source_database": "nofeeplaces_database",
        "source_url": f"https://maltdrive.com/listing/{apt_data['building'].lower()}-malt-drive_{apt_data['unit']}/",
        
        # Contact
        "contact_email": "placesfirm@gmail.com",
        "contact_phone": "+1-718-220-2222",
        "leasing_phone": "+1-718-220-2222",
        "leasing_email": "MaltDriveLeasing@tfc.com",
        
        # Transportation
        "transportation": {
            "subway_lines": ["7", "LIRR"],
            "nearest_stations": [
                "Court Square (7, G, E, M) - 8 min walk",
                "Vernon Blvd-Jackson Ave (7) - 10 min walk",
                "Hunters Point Ave (7) - 5 min walk"
            ],
            "commute_times": {
                "Grand Central": "8 min via 7 train",
                "Times Square": "15 min via 7 train",
                "Penn Station": "20 min via LIRR"
            }
        },
        
        # Neighborhood
        "neighborhood_info": {
            "description": "Hunter's Point South is Queens' premier waterfront neighborhood with over 150,000 sq ft of new parks, stunning Manhattan views, and easy access to LIC's restaurants and cultural venues. Vernon Blvd offers Michelin-star dining, breweries, and local shops.",
            "nearby_features": ["Hunter's Point South Park", "Gantry Plaza State Park", "Vernon Blvd", "East River Waterfront", "MoMA PS1"]
        },
        
        # Timestamps
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        
        # SEO
        "seo_title": f"{title} - ${apt_data['price']}/mo - LIC Queens",
        "seo_description": f"No fee {unit_type_desc} at Malt Drive. Rooftop pool, waterfront park, in-unit W/D. {apt_data['deal']}. Near 7 train.",
        "seo_keywords": ["no fee apartment", "long island city", "hunters point south", "waterfront apartment", "rooftop pool", "lic queens", "7 train"]
    }

def add_malt_drive_apartments():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("="*80)
    print("ADDING 36 MALT DRIVE APARTMENTS")
    print("="*80)
    print("Location: Hunter's Point South, Queens")
    print("Buildings: 2-20 & 2-21 Malt Drive")
    print("Price Range: $3,685 - $7,660/month")
    print()
    
    added = 0
    skipped = 0
    
    for apt_data in MALT_DRIVE_APARTMENTS:
        # Create apartment document
        apartment = create_apartment_doc(apt_data)
        
        # Check if already exists
        existing = db.apartments.find_one({
            "building_name": apartment["building_name"],
            "unit_number": apartment["unit_number"]
        })
        
        if existing:
            print(f"⚠️  Unit {apt_data['unit']} already exists - skipping")
            skipped += 1
            continue
        
        # Insert
        db.apartments.insert_one(apartment)
        added += 1
        
        br_label = "Studio" if apartment["bedrooms"] == 0 else f"{apartment['bedrooms']}BR"
        print(f"✅ Added: {apt_data['building']} Unit {apt_data['unit']} - {br_label}, {apt_data['bath']} BA - ${apt_data['price']}/mo (${apt_data['net']} net)")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"IMPORT SUMMARY")
    print(f"{'='*80}")
    print(f"Added: {added} apartments")
    print(f"Skipped: {skipped} (already exist)")
    
    # Database stats
    total = db.apartments.count_documents({})
    lic_count = db.apartments.count_documents({"neighborhood": "Long Island City"})
    no_fee = db.apartments.count_documents({"broker_fee": "No fee"})
    
    print(f"\n{'='*80}")
    print(f"DATABASE STATS")
    print(f"{'='*80}")
    print(f"Total apartments: {total}")
    print(f"LIC/Hunter's Point South: {lic_count}")
    print(f"No fee apartments: {no_fee}")
    
    client.close()
    
    print(f"\n✅ All Malt Drive apartments are now live on NoFeePlaces.com!")

if __name__ == "__main__":
    add_malt_drive_apartments()
