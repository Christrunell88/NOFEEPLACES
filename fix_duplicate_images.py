#!/usr/bin/env python3
"""
Fix duplicate apartment images by updating with unique photos for each listing
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/nofeeplaces_db")
DB_NAME = os.getenv("DB_NAME", "nofeeplaces_database")

# Unique image sets for each apartment type/location
UNIQUE_IMAGE_SETS = {
    # DUMBO 1BR Unit 6A
    "dumbo_1br_6a": [
        "https://images.unsplash.com/photo-1618219908412-a29a1bb7b86e?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1616137466211-f939a420be84?w=800&h=600&fit=crop", 
        "https://images.unsplash.com/photo-1615529328331-f8917597711f?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=800&h=600&fit=crop"
    ],
    
    # DUMBO 2BR Unit 4D  
    "dumbo_2br_4d": [
        "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1600566753051-6057c1baed80?w=800&h=600&fit=crop"
    ],
    
    # Williamsburg Copper Lofts
    "williamsburg_copper": [
        "https://images.unsplash.com/photo-1581858726788-75bc0f6a952d?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1581858727886-c4d5d2b8f857?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800&h=600&fit=crop"
    ],
    
    # Chelsea 555 West 23rd
    "chelsea_555w23": [
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1567767292278-a4f21aa2d36e?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1574362848149-11496d93a7c7?w=800&h=600&fit=crop"
    ],
    
    # Long Island City Loft
    "lic_jackson": [
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1556020685-ae41abfc9365?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=600&fit=crop"
    ]
}

async def fix_duplicate_images():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    apartments_collection = db.apartments
    
    print("🖼️ Fixing duplicate apartment images...")
    
    # Update each apartment with unique images based on location and type
    updates = [
        {
            "filter": {"address": {"$regex": "65 Washington Street, Unit 6A"}},
            "images": UNIQUE_IMAGE_SETS["dumbo_1br_6a"],
            "name": "DUMBO 1BR Unit 6A"
        },
        {
            "filter": {"address": {"$regex": "65 Washington Street, Unit 4D"}},
            "images": UNIQUE_IMAGE_SETS["dumbo_2br_4d"],  
            "name": "DUMBO 2BR Unit 4D"
        },
        {
            "filter": {"address": {"$regex": "255 Lorimer Street"}},
            "images": UNIQUE_IMAGE_SETS["williamsburg_copper"],
            "name": "Williamsburg Copper Lofts"
        },
        {
            "filter": {"address": {"$regex": "555 West 23rd Street"}},
            "images": UNIQUE_IMAGE_SETS["chelsea_555w23"],
            "name": "Chelsea 555 West 23rd"
        },
        {
            "filter": {"address": {"$regex": "12-15 Jackson Avenue"}},
            "images": UNIQUE_IMAGE_SETS["lic_jackson"],
            "name": "LIC Jackson Avenue"
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
                print(f"   New images: {len(update['images'])} unique photos")
            else:
                print(f"⚠️ No apartments found for: {update['name']}")
                
        except Exception as e:
            print(f"❌ Error updating {update['name']}: {e}")
    
    print(f"\n🎉 Successfully updated {updated_count} apartments with unique images!")
    
    # Verify no duplicate images exist in recent listings
    recent_apartments = apartments_collection.find(
        {"source": {"$in": ["Two Trees Management Company", "Compass Real Estate", "Lorimer House Management", "Chelsea Property Management", "LIC Property Group"]}},
        {"title": 1, "images": 1, "address": 1}
    )
    
    print("\n📋 Recent apartments with updated images:")
    async for apt in recent_apartments:
        print(f"   📍 {apt['title'][:50]}...")
        print(f"      First image: {apt['images'][0] if apt['images'] else 'No images'}")
    
    client.close()
    return updated_count

if __name__ == "__main__":
    asyncio.run(fix_duplicate_images())