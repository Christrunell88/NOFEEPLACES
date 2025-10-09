#!/usr/bin/env python3
"""
Fix apartment images by assigning appropriate images based on apartment type
Studios get compact studio images, 1BR get appropriate 1BR images, etc.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

class ApartmentImageTypeFixer:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces_database')
        
        # Apartment-type specific images
        self.apartment_images = {
            # Studio apartment images - compact, efficient spaces
            'studio': [
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",  # Compact studio
                "https://images.unsplash.com/photo-1631679706909-faf398e6ddfd?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",  # Studio living area
                "https://images.unsplash.com/photo-1524758631624-e2822e304c36?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",  # Small efficient space
                "https://images.unsplash.com/photo-1556020685-ae41abfc9365?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"   # Studio kitchen area
            ],
            
            # 1 bedroom apartment images
            '1br': [
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",  # 1BR living room
                "https://images.unsplash.com/photo-1586281380349-632531db7ed4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",  # 1BR bedroom
                "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",  # Kitchen
                "https://images.unsplash.com/photo-1620626011761-996317b8d101?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"   # Bathroom
            ],
            
            # 2 bedroom apartment images
            '2br': [
                "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",  # Spacious living room
                "https://images.unsplash.com/photo-1540518614846-7eded47c9390?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",  # Master bedroom
                "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",  # Second bedroom
                "https://images.unsplash.com/photo-1556909045-f208c09ff5d4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"   # 2BR kitchen
            ],
            
            # 3+ bedroom apartment images
            '3br+': [
                "https://images.unsplash.com/photo-1618219908412-a29a1bb7b86e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",  # Large living area
                "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",  # Luxury living room
                "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",  # Master suite
                "https://images.unsplash.com/photo-1556912173-3bb406ef7e77?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"   # Luxury bathroom
            ]
        }
    
    async def connect_database(self):
        """Connect to database"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
    
    def get_images_for_apartment_type(self, bedrooms):
        """Get appropriate images based on bedroom count"""
        if bedrooms == 0:
            return self.apartment_images['studio']
        elif bedrooms == 1:
            return self.apartment_images['1br']
        elif bedrooms == 2:
            return self.apartment_images['2br']
        else:
            return self.apartment_images['3br+']
    
    async def fix_images_by_type(self):
        """Fix all apartment images based on their bedroom count"""
        print("🏠 FIXING APARTMENT IMAGES BY TYPE")
        print("=" * 60)
        print("🎯 Assigning appropriate images based on apartment type")
        print("=" * 60)
        
        # Get all apartments
        apartments = await self.db.apartments.find({}).to_list(None)
        
        fixed_count = 0
        
        for apartment in apartments:
            try:
                apt_id = apartment.get('id')
                title = apartment.get('title', 'Unknown')
                bedrooms = apartment.get('bedrooms', 0)
                
                # Get appropriate images for this apartment type
                appropriate_images = self.get_images_for_apartment_type(bedrooms)
                
                # Determine apartment type for display
                if bedrooms == 0:
                    apt_type = "Studio"
                else:
                    apt_type = f"{bedrooms}BR"
                
                # Update apartment with appropriate images
                await self.db.apartments.update_one(
                    {'id': apt_id},
                    {
                        '$set': {
                            'images': appropriate_images,
                            'image_source': f'Unsplash - {apt_type} Apartment Photos'
                        }
                    }
                )
                
                print(f"✅ Fixed: {apt_type} - {title}")
                print(f"   Assigned {len(appropriate_images)} {apt_type.lower()} appropriate images")
                
                fixed_count += 1
                
            except Exception as e:
                print(f"❌ Error fixing {title}: {e}")
        
        return fixed_count, len(apartments)
    
    def show_fix_summary(self, fixed_count, total_count):
        """Show summary of type-based image fixes"""
        print(f"\n📊 APARTMENT TYPE IMAGE FIX SUMMARY")
        print("=" * 50)
        
        print(f"🎯 RESULTS:")
        print(f"   Fixed apartments: {fixed_count}/{total_count}")
        print(f"   All apartments now have type-appropriate images")
        
        print(f"\n🏠 IMAGE ASSIGNMENTS:")
        print(f"   • Studios: Compact, efficient studio spaces")
        print(f"   • 1 Bedroom: Living room + bedroom + kitchen + bath")
        print(f"   • 2 Bedroom: Spacious living + 2 bedrooms + kitchen")
        print(f"   • 3+ Bedroom: Luxury spaces + multiple rooms")
        
        print(f"\n🎉 TYPE MATCHING FIXED:")
        print(f"   • Studios no longer show large living rooms")
        print(f"   • Each apartment type shows appropriate spaces")
        print(f"   • Images match apartment size and layout")
    
    async def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()

async def main():
    """Main apartment type image fixing process"""
    fixer = ApartmentImageTypeFixer()
    
    try:
        print("🏠 APARTMENT IMAGE TYPE MATCHING FIX")
        print("=" * 60)
        print("🎯 Goal: Assign appropriate images based on apartment type")
        print("🏠 Studios get studio images, 1BR get 1BR images, etc.")
        print("=" * 60)
        
        await fixer.connect_database()
        
        # Fix all apartment images by type
        fixed_count, total_count = await fixer.fix_images_by_type()
        
        # Show summary
        fixer.show_fix_summary(fixed_count, total_count)
        
        print(f"\n🎉 APARTMENT TYPE IMAGE MATCHING COMPLETE!")
        print(f"   • {fixed_count} apartments updated with appropriate images")
        print(f"   • Studios now show compact studio spaces")
        print(f"   • 1BR apartments show appropriate 1BR layouts")
        print(f"   • 2BR apartments show spacious 2BR layouts")
        print(f"   • Images now match apartment types correctly")
        
        return fixed_count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0
    finally:
        await fixer.close_connection()

if __name__ == "__main__":
    asyncio.run(main())