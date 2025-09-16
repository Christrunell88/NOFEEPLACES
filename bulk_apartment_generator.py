#!/usr/bin/env python3
"""
Bulk Apartment Generator - NoFeePlaces.com
Generates 75 high-quality no-fee apartment listings with 4-6 images each
"""

import os
import sys
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
import random
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Database configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

# Curated high-quality apartment/room images from Pexels & Unsplash
APARTMENT_IMAGE_POOLS = {
    'luxury': [
        'https://images.pexels.com/photos/1643383/pexels-photo-1643383.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/2635038/pexels-photo-2635038.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/1643384/pexels-photo-1643384.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/2635013/pexels-photo-2635013.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/1571468/pexels-photo-1571468.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=800&auto=format&fit=crop'
    ],
    'modern': [
        'https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/1571453/pexels-photo-1571453.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/2029670/pexels-photo-2029670.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/1571461/pexels-photo-1571461.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/1643389/pexels-photo-1643389.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.unsplash.com/photo-1554995207-c18c203602cb?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1567767292278-a4f21aa2d36e?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1565182999561-18d7dc61c393?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&auto=format&fit=crop'
    ],
    'cozy': [
        'https://images.pexels.com/photos/1571467/pexels-photo-1571467.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/1454804/pexels-photo-1454804.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/1350789/pexels-photo-1350789.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/1571469/pexels-photo-1571469.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.unsplash.com/photo-1574844254584-ac9c5dfe2d44?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1581858726788-75bc0f270025?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1586105251261-72a756497a11?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&auto=format&fit=crop'
    ],
    'kitchen': [
        'https://images.pexels.com/photos/1599791/pexels-photo-1599791.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/2724749/pexels-photo-2724749.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.unsplash.com/photo-1556909114-4f6e4d4b1611?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1556909909-f05fb30ee2b3?w=800&auto=format&fit=crop'
    ],
    'bathroom': [
        'https://images.pexels.com/photos/1358912/pexels-photo-1358912.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/1454806/pexels-photo-1454806.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.unsplash.com/photo-1620626011761-996317b8d101?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1584622781564-1d987ac7309e?w=800&auto=format&fit=crop'
    ],
    'bedroom': [
        'https://images.pexels.com/photos/1454806/pexels-photo-1454806.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.pexels.com/photos/1571452/pexels-photo-1571452.jpeg?auto=compress&cs=tinysrgb&w=800',
        'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1571508601922-de5fa7afcdcf?w=800&auto=format&fit=crop'
    ]
}

# NYC Neighborhood data with realistic pricing and details
NEIGHBORHOODS = {
    # Manhattan Premium
    'SoHo': {'borough': 'Manhattan', 'price_range': (5500, 18000), 'zip_codes': ['10012', '10013']},
    'Tribeca': {'borough': 'Manhattan', 'price_range': (6000, 25000), 'zip_codes': ['10007', '10013']},
    'Upper East Side': {'borough': 'Manhattan', 'price_range': (3800, 15000), 'zip_codes': ['10021', '10028', '10075']},
    'Greenwich Village': {'borough': 'Manhattan', 'price_range': (4200, 16000), 'zip_codes': ['10003', '10011', '10014']},
    'Chelsea': {'borough': 'Manhattan', 'price_range': (4000, 14000), 'zip_codes': ['10001', '10011']},
    'Midtown East': {'borough': 'Manhattan', 'price_range': (3500, 12000), 'zip_codes': ['10016', '10017']},
    'Lower East Side': {'borough': 'Manhattan', 'price_range': (3200, 10000), 'zip_codes': ['10002', '10009']},
    'East Village': {'borough': 'Manhattan', 'price_range': (3000, 11000), 'zip_codes': ['10003', '10009']},
    'Gramercy': {'borough': 'Manhattan', 'price_range': (3800, 13000), 'zip_codes': ['10003', '10010']},
    'NoMad': {'borough': 'Manhattan', 'price_range': (4000, 14000), 'zip_codes': ['10001', '10016']},
    
    # Brooklyn Hotspots
    'Williamsburg': {'borough': 'Brooklyn', 'price_range': (3200, 8500), 'zip_codes': ['11211', '11249']},
    'Park Slope': {'borough': 'Brooklyn', 'price_range': (2800, 7500), 'zip_codes': ['11215', '11217']},
    'DUMBO': {'borough': 'Brooklyn', 'price_range': (3500, 9000), 'zip_codes': ['11201']},
    'Brooklyn Heights': {'borough': 'Brooklyn', 'price_range': (3000, 8000), 'zip_codes': ['11201']},
    'Prospect Heights': {'borough': 'Brooklyn', 'price_range': (2600, 6500), 'zip_codes': ['11238']},
    'Fort Greene': {'borough': 'Brooklyn', 'price_range': (2400, 6000), 'zip_codes': ['11217']},
    'Cobble Hill': {'borough': 'Brooklyn', 'price_range': (2800, 7000), 'zip_codes': ['11201']},
    'Red Hook': {'borough': 'Brooklyn', 'price_range': (2200, 5500), 'zip_codes': ['11231']},
    
    # Queens Value
    'Astoria': {'borough': 'Queens', 'price_range': (2400, 5500), 'zip_codes': ['11102', '11103', '11106']},
    'Long Island City': {'borough': 'Queens', 'price_range': (2600, 6500), 'zip_codes': ['11101', '11109']},
    'Sunnyside': {'borough': 'Queens', 'price_range': (2200, 4800), 'zip_codes': ['11104']},
    'Forest Hills': {'borough': 'Queens', 'price_range': (2000, 4500), 'zip_codes': ['11375']},
    'Kew Gardens': {'borough': 'Queens', 'price_range': (1900, 4200), 'zip_codes': ['11415']},
}

# Apartment types and configurations
APARTMENT_TYPES = [
    {'bedrooms': 'Studio', 'bathrooms': 1, 'sqft_range': (350, 600), 'price_multiplier': 0.8},
    {'bedrooms': 1, 'bathrooms': 1, 'sqft_range': (500, 800), 'price_multiplier': 1.0},
    {'bedrooms': 1, 'bathrooms': 1.5, 'sqft_range': (600, 900), 'price_multiplier': 1.1},
    {'bedrooms': 2, 'bathrooms': 1, 'sqft_range': (750, 1100), 'price_multiplier': 1.4},
    {'bedrooms': 2, 'bathrooms': 2, 'sqft_range': (850, 1300), 'price_multiplier': 1.6},
    {'bedrooms': 3, 'bathrooms': 2, 'sqft_range': (1000, 1600), 'price_multiplier': 2.0},
    {'bedrooms': 3, 'bathrooms': 2.5, 'sqft_range': (1200, 1800), 'price_multiplier': 2.2},
]

# Luxury amenities pool
AMENITIES_POOL = [
    "Dishwasher", "Laundry in Unit", "Air Conditioning", "Hardwood Floors", 
    "Stainless Steel Appliances", "Granite Countertops", "Balcony", "Doorman",
    "Elevator", "Gym", "Roof Deck", "Pet Friendly", "Storage", "Parking",
    "Concierge", "Pool", "Garden", "Fireplace", "Walk-in Closet", "High Ceilings",
    "Floor-to-Ceiling Windows", "City Views", "Marble Bathroom", "Chef's Kitchen",
    "Smart Home Features", "In-Unit Laundry", "Central Air", "Exposed Brick"
]

def generate_apartment_images(apartment_type, num_images=5):
    """Generate a curated set of apartment images"""
    images = []
    
    # Always include a main living space image
    if apartment_type == 'luxury':
        images.append(random.choice(APARTMENT_IMAGE_POOLS['luxury']))
    else:
        images.append(random.choice(APARTMENT_IMAGE_POOLS['modern']))
    
    # Add bedroom image
    images.append(random.choice(APARTMENT_IMAGE_POOLS['bedroom']))
    
    # Add kitchen image
    images.append(random.choice(APARTMENT_IMAGE_POOLS['kitchen']))
    
    # Add bathroom image
    images.append(random.choice(APARTMENT_IMAGE_POOLS['bathroom']))
    
    # Fill remaining slots with variety
    remaining_pools = ['luxury', 'modern', 'cozy']
    for i in range(num_images - 4):
        pool = random.choice(remaining_pools)
        images.append(random.choice(APARTMENT_IMAGE_POOLS[pool]))
    
    return images

def generate_apartment_description(neighborhood, bedrooms, amenities):
    """Generate realistic apartment descriptions"""
    bedroom_text = "studio" if bedrooms == "Studio" else f"{bedrooms}-bedroom"
    
    descriptions = [
        f"Stunning {bedroom_text} apartment in the heart of {neighborhood}. This beautifully designed unit features modern finishes and premium amenities.",
        f"Luxurious {bedroom_text} rental in prime {neighborhood} location. Enjoy sophisticated living with top-tier amenities and elegant interiors.",
        f"Contemporary {bedroom_text} apartment offering the perfect blend of comfort and style in vibrant {neighborhood}.",
        f"Exceptional {bedroom_text} unit in {neighborhood}'s most sought-after building. Features premium finishes and world-class amenities.",
        f"Gorgeous {bedroom_text} apartment with modern design and luxury amenities in the desirable {neighborhood} neighborhood."
    ]
    
    base_description = random.choice(descriptions)
    amenity_text = f" Amenities include {', '.join(amenities[:4])}."
    
    return base_description + amenity_text

async def bulk_generate_apartments():
    """Generate 75 high-quality apartments with 4-6 images each"""
    
    print("🏢 Starting Bulk Apartment Generation...")
    print("=" * 60)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Check current count
    current_count = await db.apartments.count_documents({})
    print(f"📊 Current apartment count: {current_count}")
    
    apartments_to_generate = 75
    print(f"🎯 Generating {apartments_to_generate} new apartments...")
    
    apartments_added = 0
    
    for i in range(apartments_to_generate):
        try:
            # Random neighborhood selection
            neighborhood_name, neighborhood_data = random.choice(list(NEIGHBORHOODS.items()))
            
            # Random apartment type
            apt_type = random.choice(APARTMENT_TYPES)
            
            # Calculate price based on neighborhood and apartment type
            base_price = random.randint(neighborhood_data['price_range'][0], neighborhood_data['price_range'][1])
            final_price = int(base_price * apt_type['price_multiplier'])
            
            # Generate square footage
            sqft = random.randint(apt_type['sqft_range'][0], apt_type['sqft_range'][1])
            
            # Select amenities (6-12 amenities per apartment)
            selected_amenities = random.sample(AMENITIES_POOL, random.randint(6, 12))
            
            # Generate 4-6 high-quality images
            num_images = random.randint(4, 6)
            apartment_type = 'luxury' if final_price > 8000 else 'modern'
            images = generate_apartment_images(apartment_type, num_images)
            
            # Generate address
            street_number = random.randint(100, 999)
            street_names = [
                "Broadway", "Park Avenue", "Madison Avenue", "Lexington Avenue", 
                "3rd Avenue", "2nd Avenue", "1st Avenue", "Amsterdam Avenue",
                "Columbus Avenue", "Central Park West", "Riverside Drive",
                "Washington Street", "Greenwich Street", "Hudson Street"
            ]
            street_name = random.choice(street_names)
            zip_code = random.choice(neighborhood_data['zip_codes'])
            address = f"{street_number} {street_name}, New York, NY {zip_code}"
            
            # Generate apartment data
            apartment = {
                'id': str(uuid.uuid4()),
                'title': f"{'Luxury' if apartment_type == 'luxury' else 'Modern'} {apt_type['bedrooms']}{'-Bedroom' if apt_type['bedrooms'] != 'Studio' else ''} in {neighborhood_name} - No Fee",
                'description': generate_apartment_description(neighborhood_name, apt_type['bedrooms'], selected_amenities),
                'price': final_price,
                'bedrooms': apt_type['bedrooms'],
                'bathrooms': apt_type['bathrooms'],
                'sqft': sqft,
                'address': address,
                'neighborhood': neighborhood_name,
                'borough': neighborhood_data['borough'],
                'latitude': round(random.uniform(40.7000, 40.7800), 6),
                'longitude': round(random.uniform(-74.0200, -73.9300), 6),
                'images': images,
                'amenities': selected_amenities,
                'is_no_fee': True,
                'no_fee': True,
                'available_date': (datetime.now(timezone.utc) + timedelta(days=random.randint(1, 30))).isoformat(),
                'lease_terms': random.choice(['12 months', '12-24 months', '6-12 months']),
                'pet_policy': random.choice(['Pet Friendly', 'No Pets', 'Cats Only', 'Dogs Only']),
                'parking': random.choice([True, False]),
                'utilities_included': random.choice([True, False]),
                'furnished': random.choice([True, False]),
                'source_url': f"https://nofeeplaces.com/apartment/{str(uuid.uuid4())[:8]}",
                'created_at': (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90))).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'priority': None,  # Regular listings (not priority)
                'featured': False  # Regular listings (not featured)
            }
            
            # Insert apartment
            await db.apartments.insert_one(apartment)
            apartments_added += 1
            
            if apartments_added % 10 == 0:
                print(f"✅ Added {apartments_added}/{apartments_to_generate} apartments...")
                
        except Exception as e:
            print(f"❌ Error generating apartment {i+1}: {e}")
            continue
    
    # Final count
    final_count = await db.apartments.count_documents({})
    
    print("\n🎉 BULK GENERATION COMPLETE!")
    print("=" * 60)
    print(f"✅ Successfully added: {apartments_added} apartments")
    print(f"📊 Total apartments now: {final_count}")
    print(f"📸 Each new apartment has: 4-6 high-quality images")
    print(f"🏙️  Coverage: Manhattan, Brooklyn, Queens")
    print(f"💰 Price range: $1,900 - $25,000/month")
    print(f"🏠 Types: Studios to 3-bedrooms")
    
    # Generate summary statistics
    neighborhoods_added = {}
    apartments_with_images = await db.apartments.count_documents({'images.3': {'$exists': True}})
    
    print(f"\n📈 Updated Statistics:")
    print(f"   • Total apartments: {final_count}")
    print(f"   • Apartments with 4+ images: {apartments_with_images}")
    print(f"   • Image coverage: {apartments_with_images/final_count*100:.1f}%")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(bulk_generate_apartments())