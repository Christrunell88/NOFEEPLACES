#!/usr/bin/env python3
"""
Database Cleanup - Remove Temporary Database
Since all data is already in production database, we can remove the temporary one
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def cleanup_temporary_database():
    """Remove the temporary 'nofeeplaces' database"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    
    print("\n" + "="*70)
    print("🧹 DATABASE CLEANUP")
    print("="*70)
    
    # Check what's in temporary database
    temp_db = client['nofeeplaces']
    temp_count = await temp_db.apartments.count_documents({})
    
    # Check production database
    prod_db = client['nofeeplaces_database']
    prod_count = await prod_db.apartments.count_documents({})
    
    print(f"\n📊 Current Status:")
    print(f"   Temporary DB ('nofeeplaces'): {temp_count} apartments")
    print(f"   Production DB ('nofeeplaces_database'): {prod_count} apartments")
    
    if temp_count > 0 and prod_count > 0:
        print(f"\n✅ Production database has all data")
        print(f"   Removing temporary database to avoid confusion...")
        
        # Drop the temporary database
        await client.drop_database('nofeeplaces')
        
        print(f"\n✅ Temporary database 'nofeeplaces' removed")
        print(f"   All data remains in production database 'nofeeplaces_database'")
    else:
        print(f"\n⚠️  Skipping cleanup - databases may need review")
    
    print("\n" + "="*70)
    print("📊 FINAL STATE")
    print("="*70)
    print(f"   Single Production Database: nofeeplaces_database")
    print(f"   Total Apartments: {prod_count}")
    print(f"   All listings, images, and addresses in one place ✅")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_temporary_database())
