#!/usr/bin/env python3
"""
Debug script to check priority sorting in the database
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Database configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

async def debug_priority():
    """Debug priority sorting"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔍 Checking apartments with priority fields...")
    print("=" * 60)
    
    # Find apartments with priority set
    priority_apartments = await db.apartments.find({
        "priority": {"$ne": None}
    }).to_list(length=10)
    
    print(f"📊 Found {len(priority_apartments)} apartments with priority set:")
    for apt in priority_apartments:
        print(f"  - {apt['title'][:50]}...")
        print(f"    Priority: {apt.get('priority', 'None')}")
        print(f"    Featured: {apt.get('featured', 'None')}")
        print(f"    Created: {apt.get('created_at', 'None')}")
        print()
    
    print("🔍 Examining Claridge's apartment directly...")
    print("=" * 60)
    
    # Find the Claridge's apartment directly
    claridges = await db.apartments.find_one({"title": {"$regex": "Claridge", "$options": "i"}})
    
    if claridges:
        print("✅ Found Claridge's apartment:")
        print(f"   Title: {claridges['title']}")
        print(f"   Priority: {claridges.get('priority')} (type: {type(claridges.get('priority'))})")
        print(f"   Featured: {claridges.get('featured')} (type: {type(claridges.get('featured'))})")
        print(f"   Created: {claridges.get('created_at')}")
        
        # Test aggregation with just this one apartment
        test_pipeline = [
            {"$match": {"title": {"$regex": "Claridge", "$options": "i"}}},
            {"$addFields": {
                "has_priority": {"$ifNull": ["$priority", False]},
                "priority_sort": {"$ifNull": ["$priority", 999]},
                "featured_sort": {"$ifNull": ["$featured", False]}
            }},
            {"$project": {
                "title": 1,
                "priority": 1,
                "featured": 1,
                "has_priority": 1,
                "priority_sort": 1,
                "featured_sort": 1
            }}
        ]
        
        test_result = await db.apartments.aggregate(test_pipeline).to_list(length=1)
        if test_result:
            result = test_result[0]
            print(f"\n🧪 Aggregation test result:")
            print(f"   has_priority: {result.get('has_priority')} (type: {type(result.get('has_priority'))})")
            print(f"   priority_sort: {result.get('priority_sort')} (type: {type(result.get('priority_sort'))})")
            print(f"   featured_sort: {result.get('featured_sort')} (type: {type(result.get('featured_sort'))})")
    else:
        print("❌ Claridge's apartment not found!")
        
    print()
    
    print("🔍 Simple find with sort...")
    print("=" * 60)
    
    # Simple find with sort
    simple_results = await db.apartments.find().sort([
        ("priority", 1),
        ("featured", -1),
        ("created_at", -1)
    ]).limit(5).to_list(length=5)
    
    print(f"📊 Top 5 apartments with simple sort:")
    for i, apt in enumerate(simple_results, 1):
        print(f"  {i}. {apt['title'][:50]}...")
        print(f"     Priority: {apt.get('priority', 'None')}")
        print(f"     Featured: {apt.get('featured', 'None')}")
        print(f"     Created: {apt.get('created_at', 'None')}")
        print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_priority())