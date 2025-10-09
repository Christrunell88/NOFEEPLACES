#!/usr/bin/env python3
"""
Fix Mercedes House Real Images
Replace stock images with real Nestio photos for Mercedes House apartments
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def fix_mercedes_house_images():
    """Update Mercedes House apartments with real Nestio photos"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'nofeeplaces')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🏢 FIXING MERCEDES HOUSE WITH REAL NESTIO IMAGES")
    print("=" * 60)
    
    # Real Mercedes House images from Nestio (from your previous scripts)
    real_mercedes_images = [
        "https://assets-img.nestiostatic.com/unit_photos/originals/3c06e0399a32160f9c01eb6a1384ff8b.jpg",
        "https://assets-img.nestiostatic.com/unit_photos/originals/43f5923a2b3d31c060a27afd5ee29f1a.jpg", 
        "https://assets-img.nestiostatic.com/unit_photos/originals/1b5eb51a3e59d381ad8ec85306f6775e.jpg",
        "https://assets-img.nestiostatic.com/unit_photos/originals/c7de3ffe94c5f3317e9122ccb540b5f1.jpg",
        "https://assets-img.nestiostatic.com/unit_photos/originals/d92dd3deb32245fbb801bc63d42243f4.jpg",
        "https://assets-img.nestiostatic.com/unit_photos/originals/9b2d394c1abdf9e6d8f2d4b937fee58a.jpg"
    ]
    
    try:
        # Find Mercedes House apartments
        mercedes_apartments = await db.apartments.find({
            'title': {'$regex': 'Mercedes House', '$options': 'i'}
        }).to_list(length=None)
        
        print(f"Found {len(mercedes_apartments)} Mercedes House apartments")
        
        updated_count = 0
        
        for apt in mercedes_apartments:
            apt_id = apt.get('id')
            title = apt.get('title', '')
            current_images = apt.get('images', [])
            
            # Check if using fake images
            has_fake_images = any('unsplash.com' in img for img in current_images)
            
            if has_fake_images:
                # Update with real Nestio images
                result = await db.apartments.update_one(
                    {'id': apt_id},
                    {
                        '$set': {
                            'images': real_mercedes_images,
                            'image_source': 'Nestio - Real Apartment Photos',
                            'updated_at': '2025-10-09T17:15:00Z'
                        }
                    }
                )
                
                if result.modified_count > 0:
                    print(f"✅ Updated: {title}")
                    print(f"   Replaced {len(current_images)} stock images with {len(real_mercedes_images)} real Nestio photos")
                    updated_count += 1
                else:
                    print(f"⚠️  Failed to update: {title}")
            else:
                print(f"✅ Already has real images: {title}")
        
        print(f"\n📊 MERCEDES HOUSE IMAGE FIX RESULTS:")
        print(f"   Apartments updated: {updated_count}")
        print(f"   Now using real Nestio photos from Mercedes House")
        
        return updated_count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_mercedes_house_images())