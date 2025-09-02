#!/usr/bin/env python3

import asyncio
import random
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')

# High-quality room-specific images from Unsplash
ROOM_IMAGES = {
    'living_room': [
        'https://images.unsplash.com/photo-1586023492125-27b2c045efd7',  # Modern living room
        'https://images.unsplash.com/photo-1555636222-cae831e670b3',   # Stylish living room
        'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2',   # Contemporary living
        'https://images.unsplash.com/photo-1567767292278-a4f21aa2d36e', # Luxury living room
        'https://images.unsplash.com/photo-1586105251261-72a756497a11', # Cozy living room
        'https://images.unsplash.com/photo-1631679706909-fcc30845c399', # Bright living room
        'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688', # Modern apartment living
        'https://images.unsplash.com/photo-1560185007-cde436f6a4d0',   # Elegant living space
    ],
    
    'kitchen': [
        'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136',   # Modern kitchen
        'https://images.unsplash.com/photo-1556909195-f080c4f7cd81',   # White kitchen
        'https://images.unsplash.com/photo-1556909264-4422bc60a394',   # Luxury kitchen
        'https://images.unsplash.com/photo-1565538810643-b5bdb714032a', # Contemporary kitchen
        'https://images.unsplash.com/photo-1571508601891-ca5e7a713859', # Sleek kitchen
        'https://images.unsplash.com/photo-1588854337236-6889d631faa8', # Open kitchen
        'https://images.unsplash.com/photo-1584622650111-993a426fbf0a', # Designer kitchen
        'https://images.unsplash.com/photo-1583847268964-b28dc8f51f92', # Granite kitchen
    ],
    
    'bedroom': [
        'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267', # Modern bedroom
        'https://images.unsplash.com/photo-1554995207-c18c203602cb',   # Cozy bedroom
        'https://images.unsplash.com/photo-1556020685-ae41abfc9365',   # Elegant bedroom
        'https://images.unsplash.com/photo-1564013799919-ab600027ffc6', # Luxury bedroom
        'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2',   # Contemporary bedroom
        'https://images.unsplash.com/photo-1560185127-6ed189bf02f4',   # Stylish bedroom
        'https://images.unsplash.com/photo-1502672023488-70e25813eb80', # Bright bedroom
        'https://images.unsplash.com/photo-1567538096630-e0c55bd6374c', # Master bedroom
    ],
    
    'bathroom': [
        'https://images.unsplash.com/photo-1584622650111-993a426fbf0a', # Modern bathroom
        'https://images.unsplash.com/photo-1620626011761-996317b8d101', # Luxury bathroom
        'https://images.unsplash.com/photo-1584622781564-1d987d7c6c19', # Marble bathroom
        'https://images.unsplash.com/photo-1564540583246-934409427776', # Spa-like bathroom
        'https://images.unsplash.com/photo-1585128792020-803d29415281', # Contemporary bathroom
        'https://images.unsplash.com/photo-1507652313519-d4e9174996dd', # Designer bathroom
        'https://images.unsplash.com/photo-1503594384566-461fe158e797', # Elegant bathroom
        'https://images.unsplash.com/photo-1584622650111-993a426fbf0a', # Sleek bathroom
    ],
    
    'exterior': [
        'https://images.unsplash.com/photo-1571939228382-b2f2b585ce15', # NYC building
        'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab', # Manhattan exterior
        'https://images.unsplash.com/photo-1449824913935-59a10b8d2000', # Brooklyn building
        'https://images.unsplash.com/photo-1518780664697-55e3ad937233', # Modern building
        'https://images.unsplash.com/photo-1516156008625-3a99312d8b96', # High-rise exterior
        'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00', # NYC architecture
        'https://images.unsplash.com/photo-1606046604972-77cc76adf42d', # Urban exterior
        'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2', # Building facade
    ],
    
    'amenities': [
        'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b', # Gym/fitness
        'https://images.unsplash.com/photo-1544197150-b99a580bb7a8', # Rooftop terrace
        'https://images.unsplash.com/photo-1571896349842-33c89424de2d', # Pool area
        'https://images.unsplash.com/photo-1566195992011-5f6b21e539aa', # Lobby
        'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b', # Lounge area
        'https://images.unsplash.com/photo-1495433324511-bf8e92934d90', # Concierge desk
        'https://images.unsplash.com/photo-1562113530-57ba4cea70cd', # Common area
        'https://images.unsplash.com/photo-1560472354-b33ff0c44a43', # Business center
    ]
}

def get_room_images_for_apartment(apartment_type, bedrooms, price):
    """Generate room-specific image array based on apartment characteristics"""
    images = []
    
    # Main living space (always first)
    images.append(random.choice(ROOM_IMAGES['living_room']))
    
    # Kitchen (always included)
    images.append(random.choice(ROOM_IMAGES['kitchen']))
    
    # Bedrooms (based on bedroom count)
    if bedrooms == 0:  # Studio
        # For studio, add one more living/bedroom combo image
        images.append(random.choice(ROOM_IMAGES['bedroom']))
    else:
        # Add bedroom images based on bedroom count
        for _ in range(min(bedrooms, 2)):  # Max 2 bedroom images
            images.append(random.choice(ROOM_IMAGES['bedroom']))
    
    # Bathroom (always included)
    images.append(random.choice(ROOM_IMAGES['bathroom']))
    
    # For luxury apartments (price > 5000), add more images
    if price > 5000:
        images.append(random.choice(ROOM_IMAGES['amenities']))
        images.append(random.choice(ROOM_IMAGES['exterior']))
    
    # For mid-range apartments (price > 3500), add one more
    elif price > 3500:
        images.append(random.choice(ROOM_IMAGES['exterior']))
    
    return images

async def update_apartment_images():
    """Update all apartments with multiple room-specific images"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.nofeeplaces
    
    print("🖼️  Adding room-specific images to apartment listings...")
    
    apartments_updated = 0
    
    # Get all apartments
    async for apartment in db.apartments.find({}):
        apartment_id = apartment.get('_id')
        title = apartment.get('title', 'No title')[:50]
        bedrooms = apartment.get('bedrooms', 0)
        price = apartment.get('price', 3000)
        
        # Generate room-specific images
        new_images = get_room_images_for_apartment('apartment', bedrooms, price)
        
        # Update apartment with new images array
        try:
            await db.apartments.update_one(
                {'_id': apartment_id},
                {
                    '$set': {
                        'images': new_images,
                        'image': new_images[0]  # Keep first image as primary
                    }
                }
            )
            apartments_updated += 1
            print(f"✅ Updated: {title}... ({len(new_images)} images)")
        
        except Exception as e:
            print(f"❌ Error updating apartment {title}: {str(e)}")
    
    print(f"\n🎉 Successfully updated {apartments_updated} apartments with room-specific images!")
    print("📸 Each apartment now has 4-6 images showing:")
    print("   • Living room/main space")
    print("   • Kitchen")
    print("   • Bedroom(s)")
    print("   • Bathroom")
    print("   • Building exterior (mid-tier+)")
    print("   • Amenities (luxury tier)")
    
    # Verify total count
    total_count = await db.apartments.count_documents({})
    print(f"📊 Total apartments in database: {total_count}")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(update_apartment_images())