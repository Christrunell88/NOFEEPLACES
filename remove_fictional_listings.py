#!/usr/bin/env python3
"""
Remove fictional apartment listings added by the batch script
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/nofeeplaces_db")
DB_NAME = os.getenv("DB_NAME", "nofeeplaces_database")

# IDs of fictional apartments to remove (from the batch I just added)
FICTIONAL_APARTMENT_IDS = [
    "5f28f856-77ee-4267-a62e-fd8f82bbfb5a",  # Murray Hill
    "68691106-8c5c-4999-81b3-25cc634b1992",  # Upper East Side
    "75f5b4b1-8e87-441f-9797-5245d2710e20",  # Hell's Kitchen
    "0a679227-cf1c-4ec9-9ec1-86827bbd65aa",  # Financial District
    "2ea732f7-4fe4-4d15-99f7-0fa724eea106"   # West Village (Jane Street)
]

async def remove_fictional_listings():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    apartments_collection = db.apartments
    
    print("🗑️ Removing fictional apartment listings...")
    
    # Remove by source (NoFeePlaces Curated = fictional)
    result1 = await apartments_collection.delete_many({"source": "NoFeePlaces Curated"})
    print(f"✅ Removed {result1.deleted_count} apartments with source 'NoFeePlaces Curated'")
    
    # Also remove any with the specific IDs as backup
    result2 = await apartments_collection.delete_many({"id": {"$in": FICTIONAL_APARTMENT_IDS}})
    print(f"✅ Removed {result2.deleted_count} apartments by specific IDs")
    
    # Check remaining count
    total_count = await apartments_collection.count_documents({})
    print(f"📊 Remaining apartments in database: {total_count}")
    
    client.close()
    return result1.deleted_count + result2.deleted_count

if __name__ == "__main__":
    asyncio.run(remove_fictional_listings())