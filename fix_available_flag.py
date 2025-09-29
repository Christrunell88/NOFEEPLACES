#!/usr/bin/env python3
"""
Fix available flag for all apartments in the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_db')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

async def fix_available_flag():
    """Set available=True for all apartments that don't have this field"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔧 Fixing available flag for apartments...")
    
    # Count apartments without available field
    without_flag = await db.apartments.count_documents({"available": {"$exists": False}})
    print(f"📊 Apartments without 'available' field: {without_flag}")
    
    # Update all apartments to have available=True if not set
    result = await db.apartments.update_many(
        {"available": {"$exists": False}},
        {"$set": {"available": True}}
    )
    
    print(f"✅ Updated {result.modified_count} apartments to available=True")
    
    # Count totals
    total_apartments = await db.apartments.count_documents({})
    available_apartments = await db.apartments.count_documents({"available": True})
    
    print(f"📊 Total apartments in database: {total_apartments}")
    print(f"📊 Available apartments: {available_apartments}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_available_flag())