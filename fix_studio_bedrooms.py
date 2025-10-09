#!/usr/bin/env python3
"""Fix studios missing bedrooms field"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

async def fix_studios():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'nofeeplaces')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Fix studios missing bedrooms field
    result = await db.apartments.update_many(
        {'title': {'$regex': 'STUDIO', '$options': 'i'}, 'bedrooms': {'$exists': False}},
        {'$set': {'bedrooms': 0, 'updated_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    print(f'Fixed {result.modified_count} studio apartments missing bedrooms')
    
    # Also fix any that have null bedrooms
    result2 = await db.apartments.update_many(
        {'title': {'$regex': 'STUDIO', '$options': 'i'}, 'bedrooms': None},
        {'$set': {'bedrooms': 0, 'updated_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    print(f'Fixed {result2.modified_count} studio apartments with null bedrooms')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_studios())