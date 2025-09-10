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
    
    print("🔍 Testing aggregation pipeline...")
    print("=" * 60)
    
    # Test the aggregation pipeline
    pipeline = [
        {"$addFields": {
            "priority_order": {
                "$cond": {
                    "if": {"$ne": ["$priority", None]},
                    "then": "$priority",
                    "else": 999  # Put null priorities last
                }
            }
        }},
        {"$sort": {
            "priority_order": 1,      # Priority 1 = highest (ascending: 1, 2, 3, 999...)
            "featured": -1,           # Featured apartments first
            "created_at": -1          # Newest apartments first
        }},
        {"$limit": 5},
        {"$project": {
            "title": 1,
            "priority": 1,
            "featured": 1,
            "priority_order": 1,
            "created_at": 1
        }}
    ]
    
    results = await db.apartments.aggregate(pipeline).to_list(length=5)
    
    print(f"📊 Top 5 apartments with aggregation:")
    for i, apt in enumerate(results, 1):
        print(f"  {i}. {apt['title'][:50]}...")
        print(f"     Priority: {apt.get('priority', 'None')} (order: {apt.get('priority_order', 'None')})")
        print(f"     Featured: {apt.get('featured', 'None')}")
        print(f"     Created: {apt.get('created_at', 'None')}")
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