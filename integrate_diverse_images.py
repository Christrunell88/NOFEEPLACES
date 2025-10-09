#!/usr/bin/env python3
"""
Integrate Diverse Scraped Images
Replace existing images with building-specific diverse scraped images
"""
import asyncio
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

class DiverseImageIntegrator:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces_database')
        
        self.diverse_images_dir = Path('/app/backend/uploads/diverse_scraped_images')
        
        # Organize images by building
        self.building_images = {
            'Mercedes House': [],
            'Court Square': [],
            'DUMBO Heights': [],
            'West River House': []
        }
    
    async def connect_database(self):
        """Connect to database"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
    
    def organize_diverse_images(self):
        """Organize diverse images by building"""
        print("📁 Organizing diverse scraped images by building...")
        
        if not self.diverse_images_dir.exists():
            print("❌ No diverse images directory found")
            return
        
        image_files = list(self.diverse_images_dir.glob('*'))
        print(f"Found {len(image_files)} diverse image files")
        
        for image_file in image_files:
            image_url = f"/uploads/diverse_scraped_images/{image_file.name}"
            
            # Categorize by filename prefix (building name)
            filename = image_file.name.lower()
            
            if filename.startswith('mercedes_house'):
                self.building_images['Mercedes House'].append(image_url)
            elif filename.startswith('court_square'):
                self.building_images['Court Square'].append(image_url)
            elif filename.startswith('dumbo_heights'):
                self.building_images['DUMBO Heights'].append(image_url)
            elif filename.startswith('west_river_house'):
                self.building_images['West River House'].append(image_url)
        
        # Show organization
        total_organized = 0
        for building, images in self.building_images.items():
            if images:
                print(f"   🏢 {building}: {len(images)} diverse images")
                total_organized += len(images)
        
        print(f"   📊 Total organized: {total_organized}/{len(image_files)}")
    
    async def update_apartments_with_diverse_images(self):
        """Update apartments with building-specific diverse images"""
        print(f"\n🔄 Updating apartments with diverse scraped images...")
        
        total_updated = 0
        
        for building_name, images in self.building_images.items():
            if not images:
                print(f"   ⚠️ No diverse images for {building_name}")
                continue
            
            print(f"\n🏢 Updating {building_name} apartments...")
            print(f"   Available images: {len(images)}")
            
            # Update all apartments for this building
            result = await self.db.apartments.update_many(
                {'building_name': building_name},
                {
                    '$set': {
                        'images': images,
                        'image_source': f'Diverse Scraped Images - {building_name}',
                        'diverse_scraped_images': True,
                        'updated_at': '2025-01-09T23:30:00.000Z'
                    }
                }
            )
            
            print(f"   ✅ Updated {result.modified_count} apartments")
            total_updated += result.modified_count
        
        return total_updated
    
    async def assign_diverse_images_by_apartment_type(self):
        """Assign different images to different apartment types within buildings"""
        print(f"\n🎨 Assigning diverse images by apartment type...")
        
        for building_name, available_images in self.building_images.items():
            if len(available_images) < 2:
                continue  # Need at least 2 images for diversity
            
            # Get apartments for this building
            apartments = await self.db.apartments.find({'building_name': building_name}).to_list(None)
            
            if not apartments:
                continue
            
            print(f"\n🏢 {building_name}: Diversifying {len(apartments)} apartments")
            
            # Group apartments by type
            studios = [apt for apt in apartments if apt.get('bedrooms', 0) == 0]
            one_br = [apt for apt in apartments if apt.get('bedrooms', 0) == 1]
            two_br = [apt for apt in apartments if apt.get('bedrooms', 0) == 2]
            
            # Assign different image sets to different apartment types
            image_chunks = self.chunk_images(available_images, max(len(studios), len(one_br), len(two_br), 1))
            
            # Update studios
            if studios and len(image_chunks) > 0:
                studio_images = image_chunks[0]
                for studio in studios:
                    await self.db.apartments.update_one(
                        {'id': studio['id']},
                        {
                            '$set': {
                                'images': studio_images,
                                'image_source': f'{building_name} Studios - Diverse Images'
                            }
                        }
                    )
                print(f"   🏠 Studios ({len(studios)}): {len(studio_images)} images each")
            
            # Update 1BRs
            if one_br and len(image_chunks) > 1:
                one_br_images = image_chunks[1] if len(image_chunks) > 1 else image_chunks[0]
                for apt in one_br:
                    await self.db.apartments.update_one(
                        {'id': apt['id']},
                        {
                            '$set': {
                                'images': one_br_images,
                                'image_source': f'{building_name} 1BR - Diverse Images'
                            }
                        }
                    )
                print(f"   🏠 1 Bedrooms ({len(one_br)}): {len(one_br_images)} images each")
            
            # Update 2BRs  
            if two_br and len(image_chunks) > 2:
                two_br_images = image_chunks[2] if len(image_chunks) > 2 else image_chunks[0]
                for apt in two_br:
                    await self.db.apartments.update_one(
                        {'id': apt['id']},
                        {
                            '$set': {
                                'images': two_br_images,
                                'image_source': f'{building_name} 2BR - Diverse Images'
                            }
                        }
                    )
                print(f"   🏠 2 Bedrooms ({len(two_br)}): {len(two_br_images)} images each")
    
    def chunk_images(self, images, num_chunks):
        """Split images into chunks for different apartment types"""
        if num_chunks <= 1:
            return [images]
        
        chunk_size = max(1, len(images) // num_chunks)
        chunks = []
        
        for i in range(0, len(images), chunk_size):
            chunk = images[i:i + chunk_size]
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
                
        # Ensure we don't have more chunks than requested
        return chunks[:num_chunks]
    
    async def verify_diverse_integration(self):
        """Verify diverse image integration"""
        print(f"\n🔍 Verifying diverse image integration...")
        
        # Check apartments with diverse images
        diverse_count = await self.db.apartments.count_documents({'diverse_scraped_images': True})
        
        # Get sample apartments for each building
        print(f"   📊 Apartments with diverse images: {diverse_count}")
        
        for building_name in self.building_images.keys():
            sample_apt = await self.db.apartments.find_one(
                {'building_name': building_name},
                {'title': 1, 'images': 1, 'image_source': 1, 'bedrooms': 1}
            )
            
            if sample_apt:
                apartment_type = 'Studio' if sample_apt.get('bedrooms', 0) == 0 else f"{sample_apt.get('bedrooms')}BR"
                images = sample_apt.get('images', [])
                print(f"\n   🏢 {building_name} ({apartment_type}):")
                print(f"      Images: {len(images)}")
                print(f"      Source: {sample_apt.get('image_source', 'Unknown')}")
                if images:
                    print(f"      Sample: {Path(images[0]).name}")
    
    async def integrate_diverse_images(self):
        """Execute complete diverse image integration"""
        print("🎨 INTEGRATING DIVERSE SCRAPED IMAGES")
        print("=" * 60)
        print("🎯 Goal: Replace same images with building-specific diverse images")
        print("=" * 60)
        
        await self.connect_database()
        
        # Step 1: Organize images
        self.organize_diverse_images()
        
        # Step 2: Update with building-specific images
        total_updated = await self.update_apartments_with_diverse_images()
        
        # Step 3: Add type-specific diversity
        await self.assign_diverse_images_by_apartment_type()
        
        # Step 4: Verify integration
        await self.verify_diverse_integration()
        
        print(f"\n🎉 DIVERSE IMAGE INTEGRATION COMPLETE!")
        print("=" * 50)
        print(f"✅ Total apartments updated: {total_updated}")
        print(f"✅ Building-specific images assigned")
        print(f"✅ Apartment type diversity added")
        
        if total_updated > 0:
            print(f"\n🌐 PREVIEW WILL NOW SHOW:")
            print(f"   • Mercedes House: Unique Mercedes House images")
            print(f"   • Court Square: Unique Court Square images") 
            print(f"   • DUMBO Heights: Unique DUMBO images")
            print(f"   • West River House: Unique West River House images")
            print(f"   • Different apartment types show different image sets")
        
        return total_updated
    
    async def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()

async def main():
    """Run diverse image integration"""
    integrator = DiverseImageIntegrator()
    
    try:
        updated_count = await integrator.integrate_diverse_images()
        
        if updated_count > 0:
            print(f"\n🚀 RESTART BACKEND TO SEE DIVERSE IMAGES:")
            print("=" * 50)
            print("sudo supervisorctl restart backend")
            print("\n📸 Each building will now show its own unique images!")
        else:
            print(f"\n⚠️ No apartments updated - check image availability")
            
    except Exception as e:
        print(f"❌ Integration error: {e}")
    finally:
        await integrator.close_connection()

if __name__ == "__main__":
    asyncio.run(main())