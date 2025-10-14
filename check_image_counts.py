#!/usr/bin/env python3
"""
Script to check image counts in apartments
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from collections import Counter

# Load environment variables
load_dotenv('/app/backend/.env')

# Database configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

async def check_image_counts():
    """Check image counts across all apartments"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🖼️  Analyzing apartment image counts...")
    print("=" * 60)
    
    # Get all apartments
    apartments = await db.apartments.find({}).to_list(length=None)
    
    image_counts = []
    apartments_with_multiple_images = []
    
    for apt in apartments:
        images = apt.get('images', [])
        image_count = len(images)
        image_counts.append(image_count)
        
        if image_count > 2:  # More than 2 images = "multiple pictures"
            apartments_with_multiple_images.append({
                'title': apt['title'][:50] + '...',
                'image_count': image_count,
                'price': apt.get('price', 0),
                'neighborhood': apt.get('neighborhood', 'N/A')
            })
    
    # Statistics
    counter = Counter(image_counts)
    
    print(f"📊 Total apartments analyzed: {len(apartments)}")
    print(f"📊 Image count distribution:")
    for count in sorted(counter.keys()):
        print(f"   {count} images: {counter[count]} apartments ({counter[count]/len(apartments)*100:.1f}%)")
    
    print(f"\n🌟 Apartments with more than 2 images ({len(apartments_with_multiple_images)} total):")
    for apt in sorted(apartments_with_multiple_images, key=lambda x: x['image_count'], reverse=True):
        print(f"   • {apt['title']} - {apt['image_count']} images")
        print(f"     ${apt['price']:,}/month in {apt['neighborhood']}")
        print()
    
    if apartments_with_multiple_images:
        print(f"✅ Found {len(apartments_with_multiple_images)} apartments with multiple images that can be prioritized!")
    else:
        print("ℹ️  No apartments found with more than 2 images. Consider adding more images to listings.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_image_counts())