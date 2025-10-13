#!/usr/bin/env python3
"""
Set Featured Apartments and Fix Display Issues
Mark apartments as featured so they show prominently on the homepage
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')


async def set_featured_apartments():
    """Mark best apartments as featured"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n" + "="*70)
    print("⭐ SETTING FEATURED APARTMENTS")
    print("="*70)
    
    # Get all apartments sorted by price and image count
    apartments = await db.apartments.find({}).sort('price', 1).to_list(length=None)
    
    print(f"\nTotal apartments: {len(apartments)}")
    
    # Mark top apartments with most images as featured
    featured_count = 0
    
    for i, apt in enumerate(apartments):
        # Feature apartments with good images
        image_count = len(apt.get('images', []))
        
        # Mark as featured if:
        # - Has 3+ images
        # - Is in top 10 by price (affordable)
        should_feature = image_count >= 3 and i < 10
        
        if should_feature:
            await db.apartments.update_one(
                {'id': apt['id']},
                {
                    '$set': {
                        'featured': True,
                        'priority': 10 - i  # Higher priority for lower priced
                    }
                }
            )
            featured_count += 1
            print(f"  ⭐ Featured: {apt.get('title', 'N/A')[:50]} - {image_count} images - ${apt.get('price', 0)}")
    
    print(f"\n✅ Set {featured_count} featured apartments")
    
    # Verify
    featured = await db.apartments.find({'featured': True}).to_list(length=None)
    print(f"\n📊 Total featured apartments: {len(featured)}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(set_featured_apartments())
