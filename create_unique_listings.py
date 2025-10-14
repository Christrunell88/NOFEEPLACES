#!/usr/bin/env python3
"""
Update the real apartments with dramatically different image styles to ensure no duplicates
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/nofeeplaces_db")
DB_NAME = os.getenv("DB_NAME", "nofeeplaces_database")

# Completely different visual themes for each apartment
UNIQUE_THEMED_IMAGES = {
    # DUMBO 1BR - Brooklyn Bridge/Historic brick theme
    "dumbo_1br": [
        "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&h=600&fit=crop",  # Brooklyn Bridge view
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop",  # Exposed brick walls  
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=600&fit=crop",  # Historic details
        "https://images.unsplash.com/photo-1571055107559-3e67626fa8be?w=800&h=600&fit=crop"   # Classic bathroom
    ],
    
    # DUMBO 2BR - Ultra-modern glass/steel theme
    "dumbo_2br": [
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&h=600&fit=crop",  # Glass skyscraper view
        "https://images.unsplash.com/photo-1567767292278-a4f21aa2d36e?w=800&h=600&fit=crop",  # Modern glass/steel
        "https://images.unsplash.com/photo-1574362848149-11496d93a7c7?w=800&h=600&fit=crop",  # Sleek kitchen
        "https://images.unsplash.com/photo-1560449752-270fa7881c71?w=800&h=600&fit=crop"     # Contemporary bath
    ],
    
    # Williamsburg - Industrial warehouse theme
    "williamsburg": [
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800&h=600&fit=crop",  # Warehouse exterior
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&h=600&fit=crop",  # Industrial interior
        "https://images.unsplash.com/photo-1581858727886-c4d5d2b8f857?w=800&h=600&fit=crop",  # Factory windows
        "https://images.unsplash.com/photo-1556020685-ae41abfc9365?w=800&h=600&fit=crop"     # Concrete/steel
    ],
    
    # Chelsea - Luxury/Art gallery theme  
    "chelsea": [
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop",  # Art gallery style
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&h=600&fit=crop",  # White luxury space
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=600&fit=crop",  # High-end building
        "https://images.unsplash.com/photo-1581858726788-75bc0f6a952d?w=800&h=600&fit=crop"   # Marble luxury
    ],
    
    # LIC - Converted factory/loft theme
    "lic": [
        "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&h=600&fit=crop",  # Factory conversion
        "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800&h=600&fit=crop",  # Industrial loft
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&h=600&fit=crop",  # High ceilings
        "https://images.unsplash.com/photo-1515263487990-61b07816b226?w=800&h=600&fit=crop"   # Open floor plan
    ]
}

async def create_unique_listings():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    apartments_collection = db.apartments
    
    print("🎨 Creating dramatically different apartment visual themes...")
    
    # Update with very distinct visual themes
    updates = [
        {
            "filter": {"address": {"$regex": "65 Washington Street, Unit 6A"}},
            "images": UNIQUE_THEMED_IMAGES["dumbo_1br"],
            "theme": "Historic Brooklyn Bridge/Exposed Brick"
        },
        {
            "filter": {"address": {"$regex": "65 Washington Street, Unit 4D"}},
            "images": UNIQUE_THEMED_IMAGES["dumbo_2br"],  
            "theme": "Ultra-Modern Glass/Steel"
        },
        {
            "filter": {"address": {"$regex": "255 Lorimer Street"}},
            "images": UNIQUE_THEMED_IMAGES["williamsburg"],
            "theme": "Industrial Warehouse Conversion"
        },
        {
            "filter": {"address": {"$regex": "555 West 23rd Street"}},
            "images": UNIQUE_THEMED_IMAGES["chelsea"],
            "theme": "Luxury Art Gallery Style"
        },
        {
            "filter": {"address": {"$regex": "12-15 Jackson Avenue"}},
            "images": UNIQUE_THEMED_IMAGES["lic"],
            "theme": "Converted Factory Loft"
        }
    ]
    
    updated_count = 0
    
    for update in updates:
        try:
            result = await apartments_collection.update_many(
                update["filter"],
                {"$set": {"images": update["images"]}}
            )
            
            if result.matched_count > 0:
                updated_count += result.matched_count
                print(f"✅ Updated {result.matched_count} apartment(s)")
                print(f"   🎨 Theme: {update['theme']}")
                print(f"   🖼️  First image: {update['images'][0]}")
            else:
                print(f"⚠️ No apartments found matching filter")
                
        except Exception as e:
            print(f"❌ Error updating apartment: {e}")
    
    print(f"\n🎉 Successfully updated {updated_count} apartments with unique themes!")
    print("\n🏗️ Visual themes now include:")
    print("   • Historic Brooklyn Bridge with exposed brick")  
    print("   • Ultra-modern glass and steel")
    print("   • Industrial warehouse conversion")
    print("   • Luxury art gallery style")
    print("   • Converted factory loft")
    print("\nEach apartment now has a completely distinct visual identity!")
    
    client.close()
    return updated_count

if __name__ == "__main__":
    asyncio.run(create_unique_listings())