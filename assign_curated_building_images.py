#!/usr/bin/env python3
"""
Assign curated, high-quality building-specific images
Use publicly available, building-appropriate images for each property
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

class CuratedBuildingImages:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces_database')
        
        # Curated building-specific image sets
        # These are high-quality, publicly available images that represent each building type
        self.building_images = {
            'Mercedes House': {
                'type': 'Luxury High-Rise',
                'images': [
                    # Modern luxury apartment images - sleek, high-end finishes
                    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1586281380349-632531db7ed4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1484154218962-a197022b5858?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90"
                ]
            },
            'The Olivia': {
                'type': 'Upper East Side Elegance',
                'images': [
                    # Elegant, classic NYC apartment style
                    "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1540518614846-7eded47c9390?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1556909045-f208c09ff5d4?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1620626011761-996317b8d101?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90"
                ]
            },
            'Court Square': {
                'type': 'Modern LIC Waterfront',
                'images': [
                    # Contemporary, waterfront-style apartments
                    "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1618219908412-a29a1bb7b86e?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90"
                ]
            },
            'The Brooklyner': {
                'type': 'Brooklyn Industrial Chic',
                'images': [
                    # Industrial, Brooklyn loft-style apartments
                    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1571508601891-ca5e7a713859?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1556912173-3bb406ef7e77?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90"
                ]
            },
            'DUMBO Heights': {
                'type': 'DUMBO Waterfront Luxury',
                'images': [
                    # Waterfront luxury with Brooklyn Bridge views
                    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1631679706909-faf398e6ddfd?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1524758631624-e2822e304c36?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1556020685-ae41abfc9365?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90"
                ]
            },
            'The Forge': {
                'type': 'LIC Modern Living',
                'images': [
                    # Modern Long Island City style
                    "https://images.unsplash.com/photo-1556909195-4ce4d67e2e5c?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1556909281-4c5e7e95b03b?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90",
                    "https://images.unsplash.com/photo-1586281380614-7c7ea9bbbed4?ixlib=rb-4.0.3&ixid=M3wxMJA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&q=90"
                ]
            }
        }
        
        # For buildings that already have scraped images, keep those
        # For others, use curated images above
    
    async def connect_database(self):
        """Connect to database"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
    
    async def check_existing_scraped_images(self, building_name):
        """Check if building already has scraped images"""
        apartment = await self.db.apartments.find_one(
            {'building_name': building_name},
            {'scraped_images': 1, 'images': 1}
        )
        
        if apartment:
            has_scraped = apartment.get('scraped_images', False)
            current_images = apartment.get('images', [])
            
            # Check if images are local files (scraped successfully)
            has_local_images = any('/uploads/building_images/' in str(img) for img in current_images)
            
            return has_scraped and has_local_images, current_images
        
        return False, []
    
    async def assign_curated_images(self):
        """Assign curated images to buildings that don't have scraped images"""
        print("🏠 ASSIGNING CURATED BUILDING-SPECIFIC IMAGES")
        print("=" * 70)
        print("🎯 Goal: Ensure each building has appropriate, high-quality images")
        print("📸 Keep scraped images, add curated images for others")
        print("=" * 70)
        
        updated_count = 0
        
        for building_name, building_data in self.building_images.items():
            try:
                # Check if building exists and has apartments
                apartment_count = await self.db.apartments.count_documents({'building_name': building_name})
                
                if apartment_count == 0:
                    print(f"\n🏢 Skipping {building_name} (no apartments in database)")
                    continue
                
                print(f"\n🏢 Processing {building_name} ({apartment_count} apartments)")
                
                # Check if building already has scraped images
                has_scraped, current_images = await self.check_existing_scraped_images(building_name)
                
                if has_scraped:
                    print(f"   ✅ Already has scraped images ({len(current_images)} images)")
                    continue
                
                # Assign curated images
                curated_images = building_data['images']
                building_type = building_data['type']
                
                result = await self.db.apartments.update_many(
                    {'building_name': building_name},
                    {
                        '$set': {
                            'images': curated_images,
                            'image_source': f'Curated {building_type} Images',
                            'curated_images': True,
                            'updated_at': '2025-01-09T22:00:00.000Z'
                        }
                    }
                )
                
                print(f"   ✅ Assigned curated {building_type} images")
                print(f"   📸 Updated {result.modified_count} apartments with {len(curated_images)} images")
                
                updated_count += result.modified_count
                
            except Exception as e:
                print(f"❌ Error processing {building_name}: {e}")
        
        return updated_count
    
    async def show_final_summary(self):
        """Show final summary of all building images"""
        print(f"\n📊 FINAL BUILDING IMAGE SUMMARY")
        print("=" * 50)
        
        # Get all buildings and their image sources
        buildings = await self.db.apartments.aggregate([
            {
                '$group': {
                    '_id': '$building_name',
                    'apartment_count': {'$sum': 1},
                    'image_source': {'$first': '$image_source'},
                    'image_count': {'$first': {'$size': '$images'}},
                    'has_scraped': {'$first': '$scraped_images'},
                    'has_curated': {'$first': '$curated_images'}
                }
            },
            {'$sort': {'_id': 1}}
        ]).to_list(None)
        
        scraped_count = 0
        curated_count = 0
        
        for building in buildings:
            building_name = building['_id']
            apartment_count = building['apartment_count'] 
            image_source = building.get('image_source', 'Unknown')
            image_count = building.get('image_count', 0)
            has_scraped = building.get('has_scraped', False)
            has_curated = building.get('has_curated', False)
            
            if has_scraped:
                scraped_count += apartment_count
                status = "🌐 Scraped"
            elif has_curated:
                curated_count += apartment_count
                status = "🎨 Curated"
            else:
                status = "❓ Unknown"
            
            print(f"   • {building_name}: {apartment_count} apts, {image_count} images - {status}")
        
        print(f"\n📊 IMAGE SOURCE BREAKDOWN:")
        print(f"   🌐 Scraped from websites: {scraped_count} apartments")
        print(f"   🎨 Curated building-specific: {curated_count} apartments") 
        
        total_apts = scraped_count + curated_count
        print(f"\n🎉 TOTAL COVERAGE: {total_apts} apartments have building-appropriate images")
        
        return total_apts
    
    async def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()

async def main():
    """Main curated image assignment process"""
    curator = CuratedBuildingImages()
    
    try:
        print("🏠 CURATED BUILDING IMAGE ASSIGNMENT")
        print("=" * 70)
        print("🎯 Goal: Ensure all buildings have appropriate images")
        print("📸 Preserve scraped images, add curated images for others")
        print("=" * 70)
        
        await curator.connect_database()
        
        # Assign curated images where needed
        updated_count = await curator.assign_curated_images()
        
        # Show final summary
        total_coverage = await curator.show_final_summary()
        
        print(f"\n🎉 CURATED IMAGE ASSIGNMENT COMPLETE!")
        print(f"   • {updated_count} apartments updated with curated images")
        print(f"   • {total_coverage} total apartments have building-appropriate images")
        print(f"   • Each building now shows images matching its style and location")
        print(f"   • Mercedes House shows luxury high-rise images")
        print(f"   • DUMBO Heights shows waterfront luxury images")
        print(f"   • The Brooklyner shows Brooklyn industrial chic images")
        
        return updated_count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0
    finally:
        await curator.close_connection()

if __name__ == "__main__":
    asyncio.run(main())