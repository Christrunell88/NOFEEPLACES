#!/usr/bin/env python3
"""
Script to enhance apartment listings with multiple images (4-6 per apartment)
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import random

# Set up MongoDB connection
MONGO_URL = "mongodb://localhost:27017/nofeeplaces_db"

# High-quality apartment images from various sources
APARTMENT_IMAGES = [
    # Living rooms
    "https://images.unsplash.com/photo-1594295800284-990f74bb6928?w=800",
    "https://images.unsplash.com/photo-1568486776380-bf9c4e93347a?w=800",
    "https://images.unsplash.com/photo-1553287222-da8a77d59c5c?w=800",
    "https://images.unsplash.com/photo-1618861138969-0d7a9d315b1f?w=800",
    "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800",
    "https://images.unsplash.com/photo-1560448204-61dc36dc98c8?w=800",
    
    # Bedrooms
    "https://images.unsplash.com/photo-1631049307290-bb947b114627?w=800",
    "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e?w=800",
    "https://images.unsplash.com/photo-1632830025328-cce71800b9ec?w=800",
    "https://images.unsplash.com/photo-1714153542012-6164546db890?w=800",
    "https://images.unsplash.com/photo-1540543234938-6ac4b2f1ec48?w=800",
    "https://images.unsplash.com/photo-1556906795-9d3e1f21b5e6?w=800",
    
    # Kitchens
    "https://images.unsplash.com/photo-1556909265-71269c4e3b5a?w=800",
    "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800",
    "https://images.unsplash.com/photo-1603354350317-6f7aaa5911c5?w=800",
    "https://images.unsplash.com/photo-1595526051245-4506e0006a94?w=800",
    "https://images.unsplash.com/photo-1581539250439-c96689b516dd?w=800",
    
    # Bathrooms
    "https://images.unsplash.com/photo-1559671552-7bb7c9c0b10d?w=800",
    "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800",
    "https://images.unsplash.com/photo-1562113295-57ba58f9cd15?w=800",
    "https://images.unsplash.com/photo-1584116831289-e53912463c35?w=800",
    "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=800",
    
    # Building exteriors and amenities
    "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800",
    "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800",
    "https://images.unsplash.com/photo-1581431821087-da84b7f4b6ec?w=800",
    "https://images.unsplash.com/photo-1576941089067-2de3c901e126?w=800",
    "https://images.unsplash.com/photo-1610457461233-0f13c4b8b6c4?w=800",
    
    # NYC neighborhood views
    "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800",  # NYC street
    "https://images.unsplash.com/photo-1519832521-0b6b1b3ad69b?w=800",   # Brooklyn bridge view
    "https://images.unsplash.com/photo-1520637836862-4d197d17c93a?w=800",  # Manhattan skyline
    
    # Room details and views
    "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?w=800",
    "https://images.unsplash.com/photo-1561501900-3701fa6a0864?w=800",
    "https://images.unsplash.com/photo-1597640985509-26742e52b5b4?w=800",
    "https://images.unsplash.com/photo-1512915922686-57c11dde9b6b?w=800",
    
    # Additional modern apartment images
    "https://images.pexels.com/photos/6970025/pexels-photo-6970025.jpeg?w=800",
    "https://images.pexels.com/photos/3773575/pexels-photo-3773575.jpeg?w=800",
    "https://images.pexels.com/photos/2119714/pexels-photo-2119714.jpeg?w=800",
    "https://images.pexels.com/photos/4113779/pexels-photo-4113779.jpeg?w=800",
    "https://images.pexels.com/photos/3935350/pexels-photo-3935350.jpeg?w=800",
    "https://images.pexels.com/photos/4098369/pexels-photo-4098369.jpeg?w=800",
    "https://images.pexels.com/photos/6480209/pexels-photo-6480209.jpeg?w=800",
    "https://images.pexels.com/photos/2883049/pexels-photo-2883049.jpeg?w=800",
]

async def enhance_apartment_images():
    """Add multiple high-quality images to all apartments"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.nofeeplaces_db
    
    try:
        # Get all apartments
        apartments = await db.apartments.find().to_list(length=None)
        print(f"Found {len(apartments)} apartments to enhance")
        
        updated_count = 0
        
        for apartment in apartments:
            current_images = apartment.get('images', [])
            current_count = len(current_images)
            
            # Determine target number of images based on apartment type
            bedrooms = apartment.get('bedrooms', 0)
            if bedrooms == 0:  # Studio
                target_images = 4
            elif bedrooms == 1:  # 1BR
                target_images = 5
            else:  # 2BR+
                target_images = 6
            
            if current_count < target_images:
                # Keep existing images and add more
                enhanced_images = current_images.copy()
                
                # Add random images to reach target count
                available_images = [img for img in APARTMENT_IMAGES if img not in enhanced_images]
                random.shuffle(available_images)
                
                images_needed = target_images - current_count
                new_images = available_images[:images_needed]
                
                enhanced_images.extend(new_images)
                
                # Update the apartment
                await db.apartments.update_one(
                    {'id': apartment['id']},
                    {
                        '$set': {
                            'images': enhanced_images,
                            'updated_at': datetime.now().isoformat()
                        }
                    }
                )
                
                updated_count += 1
                title = apartment.get('title', 'Unknown')
                price = apartment.get('price', 'Unknown')
                print(f"✅ Enhanced {title} (${price}) from {current_count} to {len(enhanced_images)} images")
        
        print(f"\n🎉 Successfully enhanced {updated_count} apartments with more images!")
        print(f"All apartments now have 4-6 high-quality images for better user experience.")
        
    except Exception as e:
        print(f"❌ Error enhancing apartment images: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(enhance_apartment_images())