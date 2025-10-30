#!/usr/bin/env python3
"""
Rename Waterline Square images with descriptive room-type labels
"""
import os
import shutil

IMAGES_DIR = "/app/backend/uploads/building_images/waterline_square"

# Mapping of current filenames to new descriptive names
RENAME_MAP = {
    "Interior_Kitchen_WaterlineSquare_Rental-wsq2-featured-4-1440x720-1.jpg": "waterline_square_kitchen_modern.jpg",
    "Interiors_Kitchen20Island20witrh20Barstools_Waterline20Square_Rental_wsq1_kitchen1440x720.jpg": "waterline_square_kitchen_island_barstools.jpg",
    "Interiors_Living20Room20Water20View_Waterline20Square_Rental_1440x720.jpg": "waterline_square_living_room_water_view.jpg",
    "Interiors_Penthouse20Home20Water20View_Waterline20Square_3Penthouse_1440x720.jpg": "waterline_square_penthouse_living_water_view.jpg",
    "OurCommunity_Lobby_WaterlineSquare_wsq2-lobby.jpg": "waterline_square_lobby_entrance.jpg",
    "OurCommunity_Person20on20balcony_WaterlineSquare_3buildings_1WSQ_Hero_D.jpg": "waterline_square_balcony_exterior_view.jpg"
}

def main():
    """Rename all images with descriptive labels"""
    print("=" * 70)
    print("WATERLINE SQUARE IMAGE LABELING")
    print("=" * 70)
    
    renamed = 0
    errors = 0
    
    for old_name, new_name in RENAME_MAP.items():
        old_path = os.path.join(IMAGES_DIR, old_name)
        new_path = os.path.join(IMAGES_DIR, new_name)
        
        if not os.path.exists(old_path):
            print(f"⚠️  File not found: {old_name}")
            errors += 1
            continue
        
        try:
            # Rename the file
            os.rename(old_path, new_path)
            
            # Get file size for display
            file_size = os.path.getsize(new_path) / 1024
            
            # Extract room type for display
            room_type = new_name.replace("waterline_square_", "").replace(".jpg", "").replace("_", " ").title()
            
            print(f"✅ {room_type}")
            print(f"   Old: {old_name[:60]}...")
            print(f"   New: {new_name}")
            print(f"   Size: {file_size:.1f} KB")
            print()
            
            renamed += 1
        except Exception as e:
            print(f"❌ Error renaming {old_name}: {e}")
            errors += 1
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Successfully renamed: {renamed}/{len(RENAME_MAP)}")
    print(f"Errors: {errors}")
    
    print("\n📁 Final directory contents:")
    for filename in sorted(os.listdir(IMAGES_DIR)):
        filepath = os.path.join(IMAGES_DIR, filename)
        file_size = os.path.getsize(filepath) / 1024
        
        # Extract room type from filename
        room_type = filename.replace("waterline_square_", "").replace(".jpg", "").replace("_", " ").title()
        print(f"  • {room_type}: {filename} ({file_size:.1f} KB)")

if __name__ == "__main__":
    main()
