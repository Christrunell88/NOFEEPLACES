import os
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
apartments_collection = db['apartments']

# All high-quality images from the Moinian listing page
all_images = [
    # Unit/Apartment Photos
    "https://assets-img.nestiostatic.com/unit_photos/originals/49719869911d38d481a115c8bd8e7dc4.jpg",
    "https://assets-img.nestiostatic.com/unit_photos/originals/6d7e56e83cada076b148e9fa3f1bac11.jpg",
    "https://assets-img.nestiostatic.com/unit_photos/originals/a51e91a7864ee4b9fd979a226585a550.jpg",
    "https://assets-img.nestiostatic.com/unit_photos/originals/d4257d238f5407aa77f61b478abea91c.jpg",
    "https://assets-img.nestiostatic.com/unit_photos/originals/037bc3924f60861eca9fef4b47ede0bd.jpg",
    
    # Building Amenity Photos  
    "https://assets-img.nestiostatic.com/building_medias/full/d76b59896e1e0d86714d630ae7f3e9c4.jpg",  # Pool
    "https://assets-img.nestiostatic.com/building_medias/full/334a309d6c1ed33d45d8828497177cd0.jpg",  # City view
    "https://assets-img.nestiostatic.com/building_medias/full/89d6fd57bb1376eacde3b0648e20111a.jpg",  # Lounge
    "https://assets-img.nestiostatic.com/building_medias/full/f1dff826fb96a126824d334be54762e6.jpg",  # Amenity space
    "https://assets-img.nestiostatic.com/building_medias/full/4473e823c33e7c2b447baa04891b755c.jpg",  # Living area
    "https://assets-img.nestiostatic.com/building_medias/full/6a76be683d3fe8a4046981d57c9b6914.jpg",  # Dining
    "https://assets-img.nestiostatic.com/building_medias/full/297c2df776c602319f3d5337214c05e5.jpg",  # Space
    "https://assets-img.nestiostatic.com/building_medias/full/07953e66a4581193e721d87333cf4b34.jpg",  # Work space
    "https://assets-img.nestiostatic.com/building_medias/full/ea3e59136a5243132ecc61402983a046.jpg",  # Building exterior
    "https://assets-img.nestiostatic.com/building_medias/full/00b110e21563512a5bab87bdd0c5ce95.jpg",  # Amenity
    "https://assets-img.nestiostatic.com/building_medias/full/4f4f1edb87b4a0da63733eeca0132b20.jpg",  # Pool area
    "https://assets-img.nestiostatic.com/building_medias/full/0f869f247dcc517e04749611012fb254.jpg",  # Basketball court
    "https://assets-img.nestiostatic.com/building_medias/full/0261fdb62b4fb9e18458334a0f28164e.jpg",  # Amenity
    "https://assets-img.nestiostatic.com/building_medias/full/9c02c5aced04934f9e782451a59adc75.jpg",  # Amenity
    "https://assets-img.nestiostatic.com/building_medias/full/eae7ce7c3c21be2382a08e2d62d1596a.jpg"   # Skyline view
]

# Find the PLG listing
plg_listing = apartments_collection.find_one({'building_name': 'PLG'})

if not plg_listing:
    print("❌ PLG listing not found!")
else:
    print(f"✅ Found PLG listing: {plg_listing.get('title')}")
    print(f"   Current images: {len(plg_listing.get('images', []))}")
    
    # Update with new data
    update_data = {
        'building_name': 'The Aria',
        'title': 'Luxury Studio at The Aria - Unit 10N',
        'images': all_images,
        'updated_at': datetime.utcnow()
    }
    
    # Update the listing
    result = apartments_collection.update_one(
        {'_id': plg_listing['_id']},
        {'$set': update_data}
    )
    
    if result.modified_count > 0:
        print(f"\n✅ Successfully updated listing!")
        print(f"   - Building name: PLG → The Aria")
        print(f"   - Images: {len(plg_listing.get('images', []))} → {len(all_images)}")
        print(f"   - Title updated to: {update_data['title']}")
        print(f"\n📸 Image breakdown:")
        print(f"   - Unit/Apartment photos: 5 images")
        print(f"   - Building/Amenity photos: 15 images")
        print(f"   - Total: {len(all_images)} high-quality images")
    else:
        print("⚠️ No changes made")

client.close()
print("\n✅ Database connection closed")
