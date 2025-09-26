#!/usr/bin/env python3
"""
Fix apartment images that are not loading and ensure diverse, working images are displayed
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/nofeeplaces_db")
DB_NAME = os.getenv("DB_NAME", "nofeeplaces_database")

# Working apartment images with people and diverse interiors
WORKING_APARTMENT_IMAGES = {
    # Set 1 - Modern apartment with woman
    "modern_woman": [
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&h=600&fit=crop&auto=format"
    ],
    
    # Set 2 - Contemporary apartment with lifestyle shots
    "contemporary_lifestyle": [
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=600&fit=crop&auto=format", 
        "https://images.unsplash.com/photo-1567767292278-a4f21aa2d36e?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1574362848149-11496d93a7c7?w=800&h=600&fit=crop&auto=format"
    ],
    
    # Set 3 - Luxury apartment with people
    "luxury_people": [
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1556020685-ae41abfc9365?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1560449752-270fa7881c71?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1581858726788-75bc0f6a952d?w=800&h=600&fit=crop&auto=format"
    ],
    
    # Set 4 - Cozy apartment with lifestyle
    "cozy_lifestyle": [
        "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1515263487990-61b07816b226?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1571055107559-3e67626fa8be?w=800&h=600&fit=crop&auto=format"
    ],
    
    # Set 5 - Industrial loft with people
    "industrial_loft": [
        "https://images.unsplash.com/photo-1581858727886-c4d5d2b8f857?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800&h=600&fit=crop&auto=format"
    ],
    
    # Set 6 - Brooklyn apartment with woman
    "brooklyn_woman": [
        "https://images.unsplash.com/photo-1618219908412-a29a1bb7b86e?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1616137466211-f939a420be84?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1615529328331-f8917597711f?w=800&h=600&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=800&h=600&fit=crop&auto=format"
    ]
}

async def fix_apartment_images():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    apartments_collection = db.apartments
    
    print("🖼️ Fixing apartment images with working URLs...")
    
    # Update apartments that have broken or blocked images
    updates = [
        {
            "filter": {"neighborhood": "DUMBO", "bedrooms": 1},
            "images": WORKING_APARTMENT_IMAGES["modern_woman"],
            "name": "DUMBO 1BR apartments"
        },
        {
            "filter": {"neighborhood": "DUMBO", "bedrooms": 2},
            "images": WORKING_APARTMENT_IMAGES["contemporary_lifestyle"],
            "name": "DUMBO 2BR apartments"
        },
        {
            "filter": {"neighborhood": "Chelsea"},
            "images": WORKING_APARTMENT_IMAGES["luxury_people"],
            "name": "Chelsea apartments"
        },
        {
            "filter": {"neighborhood": "Williamsburg"},
            "images": WORKING_APARTMENT_IMAGES["industrial_loft"],
            "name": "Williamsburg apartments"
        },
        {
            "filter": {"neighborhood": "Astoria"},
            "images": WORKING_APARTMENT_IMAGES["cozy_lifestyle"],
            "name": "Astoria apartments"
        },
        {
            "filter": {"neighborhood": "Hudson Yards"},
            "images": WORKING_APARTMENT_IMAGES["luxury_people"],
            "name": "Hudson Yards apartments"
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
                print(f"   🖼️ First image: {update['images'][0]}")
            else:
                print(f"⚠️ No apartments found for: {update['name']}")
                
        except Exception as e:
            print(f"❌ Error updating {update['name']}: {e}")
    
    # Also fix any apartments with waterline-square.com images (which are broken)
    broken_waterline_result = await apartments_collection.update_many(
        {"images": {"$regex": "waterline-square.com"}},
        {"$set": {"images": WORKING_APARTMENT_IMAGES["brooklyn_woman"]}}
    )
    
    if broken_waterline_result.matched_count > 0:
        updated_count += broken_waterline_result.matched_count
        print(f"✅ Fixed {broken_waterline_result.matched_count} apartments with broken waterline-square.com images")
    
    print(f"\n🎉 Successfully updated {updated_count} apartments with working images!")
    print("\n📸 Image themes now include:")
    print("   • Modern apartment with woman lifestyle shots")
    print("   • Contemporary living with people")
    print("   • Luxury apartments with lifestyle photography")
    print("   • Cozy living spaces with residents")
    print("   • Industrial lofts with urban lifestyle")
    print("   • Brooklyn apartments with woman in living spaces")
    print("\n✨ All images should now load properly and show diverse people in apartments!")
    
    client.close()
    return updated_count

if __name__ == "__main__":
    asyncio.run(fix_apartment_images())