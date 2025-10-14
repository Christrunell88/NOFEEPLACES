#!/usr/bin/env python3
"""
Fix remaining similar-looking apartment images with more distinctly different photos
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/nofeeplaces_db")
DB_NAME = os.getenv("DB_NAME", "nofeeplaces_database")

# More distinctly different image sets
DISTINCT_IMAGE_SETS = {
    # DUMBO 1BR Unit 6A - Waterfront/Brooklyn Bridge theme
    "dumbo_1br_6a": [
        "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&h=600&fit=crop",  # Brooklyn Bridge view
        "https://images.unsplash.com/photo-1515263487990-61b07816b226?w=800&h=600&fit=crop",  # Modern kitchen
        "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?w=800&h=600&fit=crop",  # Bedroom
        "https://images.unsplash.com/photo-1571055107559-3e67626fa8be?w=800&h=600&fit=crop"   # Bathroom
    ],
    
    # DUMBO 2BR Unit 4D - Loft/Industrial theme
    "dumbo_2br_4d": [
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop",  # Exposed brick loft
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&h=600&fit=crop",  # Industrial living
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=600&fit=crop",  # High ceilings
        "https://images.unsplash.com/photo-1556020685-ae41abfc9365?w=800&h=600&fit=crop"     # Modern balcony
    ],
    
    # Williamsburg Copper Lofts - Modern/Contemporary theme  
    "williamsburg_copper": [
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop",  # Contemporary living
        "https://images.unsplash.com/photo-1574362848149-11496d93a7c7?w=800&h=600&fit=crop",  # Sleek kitchen
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&h=600&fit=crop",  # Modern bedroom
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=600&fit=crop"     # Building exterior
    ],
    
    # Chelsea 555 West 23rd - Luxury/High Line theme
    "chelsea_555w23": [
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&h=600&fit=crop",  # City skyline view
        "https://images.unsplash.com/photo-1567767292278-a4f21aa2d36e?w=800&h=600&fit=crop",  # Luxury living room
        "https://images.unsplash.com/photo-1560449752-270fa7881c71?w=800&h=600&fit=crop",  # High-end kitchen
        "https://images.unsplash.com/photo-1581858726788-75bc0f6a952d?w=800&h=600&fit=crop"   # Marble bathroom
    ],
    
    # Long Island City Loft - Loft/Warehouse theme
    "lic_jackson": [
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800&h=600&fit=crop",  # Warehouse loft
        "https://images.unsplash.com/photo-1581858727886-c4d5d2b8f857?w=800&h=600&fit=crop",  # Open floor plan
        "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800&h=600&fit=crop",  # Industrial windows
        "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&h=600&fit=crop"   # Rooftop access
    ]
}

async def fix_similar_images():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    apartments_collection = db.apartments
    
    print("🖼️ Updating apartments with distinctly different images...")
    
    # Update each apartment with very different image themes
    updates = [
        {
            "filter": {"address": {"$regex": "65 Washington Street, Unit 6A"}},
            "images": DISTINCT_IMAGE_SETS["dumbo_1br_6a"],
            "name": "DUMBO 1BR Unit 6A (Waterfront Theme)"
        },
        {
            "filter": {"address": {"$regex": "65 Washington Street, Unit 4D"}},
            "images": DISTINCT_IMAGE_SETS["dumbo_2br_4d"],  
            "name": "DUMBO 2BR Unit 4D (Industrial Theme)"
        },
        {
            "filter": {"address": {"$regex": "255 Lorimer Street"}},
            "images": DISTINCT_IMAGE_SETS["williamsburg_copper"],
            "name": "Williamsburg Copper Lofts (Contemporary Theme)"
        },
        {
            "filter": {"address": {"$regex": "555 West 23rd Street"}},
            "images": DISTINCT_IMAGE_SETS["chelsea_555w23"],
            "name": "Chelsea 555 West 23rd (Luxury Theme)"
        },
        {
            "filter": {"address": {"$regex": "12-15 Jackson Avenue"}},
            "images": DISTINCT_IMAGE_SETS["lic_jackson"],
            "name": "LIC Jackson Avenue (Warehouse Theme)"
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
                print(f"✅ Updated {result.matched_count} apartment(s): {update['name']}")
                print(f"   Theme: {update['name'].split('(')[1].replace(')', '')}")
            else:
                print(f"⚠️ No apartments found for: {update['name']}")
                
        except Exception as e:
            print(f"❌ Error updating {update['name']}: {e}")
    
    print(f"\n🎉 Successfully updated {updated_count} apartments with distinct themes!")
    
    # Show the different themes for each apartment
    print("\n🎨 Image themes by apartment:")
    print("   • DUMBO 1BR: Brooklyn Bridge/Waterfront views")  
    print("   • DUMBO 2BR: Industrial loft with exposed brick")
    print("   • Williamsburg: Modern contemporary design")
    print("   • Chelsea: Luxury with city/High Line views")
    print("   • LIC: Warehouse loft with rooftop access")
    
    client.close()
    return updated_count

if __name__ == "__main__":
    asyncio.run(fix_similar_images())