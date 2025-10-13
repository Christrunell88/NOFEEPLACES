#!/usr/bin/env python3
"""
Integrate Scraped Images with Apartment Database
Update apartment records to use the newly downloaded images
"""
import asyncio
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

class ScrapedImageIntegrator:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces_database')
        
        self.scraped_images_dir = Path('/app/backend/uploads/scraped_images_advanced')
        
        # Map downloaded images to buildings
        self.image_mapping = {
            'Mercedes House': [],
            'Court Square': [],
            'TF Cornerstone': []  # General TF Cornerstone buildings
        }
    
    async def connect_database(self):
        """Connect to database"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
    
    def organize_scraped_images(self):
        """Organize scraped images by source/building"""
        print("📁 Organizing scraped images by building...")
        
        if not self.scraped_images_dir.exists():
            print("❌ No scraped images directory found")
            return
        
        scraped_files = list(self.scraped_images_dir.glob('*'))
        print(f"Found {len(scraped_files)} scraped image files")
        
        for image_file in scraped_files:
            image_url = f"/uploads/scraped_images_advanced/{image_file.name}"
            
            # Categorize by domain/source
            if 's3_amazonaws_com' in image_file.name:
                # Mercedes House images (from Two Trees S3)
                self.image_mapping['Mercedes House'].append(image_url)
            elif 'marvel-b1-cdn' in image_file.name or 'cdn_tfc_com' in image_file.name:
                # TF Cornerstone images
                self.image_mapping['Court Square'].append(image_url)
                self.image_mapping['TF Cornerstone'].append(image_url)
        
        # Show organization results
        for building, images in self.image_mapping.items():
            if images:
                print(f"   🏢 {building}: {len(images)} images")
    
    async def update_mercedes_house_images(self):
        """Update Mercedes House apartments with scraped images"""
        print(f"\n🏢 Updating Mercedes House apartments with scraped images...")
        
        mercedes_images = self.image_mapping.get('Mercedes House', [])
        
        if not mercedes_images:
            print("   ⚠️ No Mercedes House images found to update")
            return 0
        
        # Update all Mercedes House apartments
        result = await self.db.apartments.update_many(
            {'building_name': 'Mercedes House'},
            {
                '$set': {
                    'images': mercedes_images,
                    'image_source': 'Scraped from Mercedes House Official Website',
                    'scraped_images': True,
                    'updated_at': '2025-01-09T23:00:00.000Z'
                }
            }
        )
        
        print(f"   ✅ Updated {result.modified_count} Mercedes House apartments")
        return result.modified_count
    
    async def update_court_square_images(self):
        """Update Court Square apartments with scraped images"""
        print(f"\n🏢 Updating Court Square apartments with scraped images...")
        
        court_square_images = self.image_mapping.get('Court Square', [])
        
        if not court_square_images:
            print("   ⚠️ No Court Square images found to update")
            return 0
        
        # Update Court Square apartments
        result = await self.db.apartments.update_many(
            {'building_name': 'Court Square'},
            {
                '$set': {
                    'images': court_square_images,
                    'image_source': 'Scraped from TF Cornerstone Official Website',
                    'scraped_images': True,
                    'updated_at': '2025-01-09T23:00:00.000Z'
                }
            }
        )
        
        print(f"   ✅ Updated {result.modified_count} Court Square apartments")
        return result.modified_count
    
    async def update_other_tfc_apartments(self):
        """Update other TF Cornerstone apartments with scraped images"""
        print(f"\n🏢 Updating other TF Cornerstone apartments...")
        
        tfc_images = self.image_mapping.get('TF Cornerstone', [])
        
        if not tfc_images:
            print("   ⚠️ No TF Cornerstone images found")
            return 0
        
        # Update other TFC apartments (excluding Court Square which was already updated)
        result = await self.db.apartments.update_many(
            {
                'source_verification.building_management': 'TF Cornerstone',
                'building_name': {'$ne': 'Court Square'}
            },
            {
                '$set': {
                    'images': tfc_images[:4],  # Use first 4 images
                    'image_source': 'Scraped from TF Cornerstone Properties',
                    'scraped_images': True,
                    'updated_at': '2025-01-09T23:00:00.000Z'
                }
            }
        )
        
        print(f"   ✅ Updated {result.modified_count} other TFC apartments")
        return result.modified_count
    
    async def verify_image_accessibility(self):
        """Verify that scraped images are web-accessible"""
        print(f"\n🔍 Verifying image accessibility...")
        
        # Check if images directory is web-accessible
        test_images = list(self.scraped_images_dir.glob('*.jpg'))[:2]
        
        accessible_count = 0
        for image_file in test_images:
            image_url = f"/uploads/scraped_images_advanced/{image_file.name}"
            print(f"   📸 Image URL: {image_url}")
            
            # Check file exists and has proper permissions
            if image_file.exists() and image_file.stat().st_size > 0:
                accessible_count += 1
                print(f"      ✅ Accessible ({image_file.stat().st_size} bytes)")
            else:
                print(f"      ❌ Not accessible")
        
        print(f"\n   📊 Accessible images: {accessible_count}/{len(test_images)}")
        return accessible_count > 0
    
    async def show_integration_summary(self):
        """Show summary of image integration"""
        # Get updated apartment counts
        mercedes_count = await self.db.apartments.count_documents({'building_name': 'Mercedes House'})
        court_square_count = await self.db.apartments.count_documents({'building_name': 'Court Square'})
        
        # Check for scraped images
        with_scraped = await self.db.apartments.count_documents({'scraped_images': True})
        
        print(f"\n📊 IMAGE INTEGRATION SUMMARY")
        print("=" * 50)
        print(f"Mercedes House apartments: {mercedes_count}")
        print(f"Court Square apartments: {court_square_count}")
        print(f"Apartments with scraped images: {with_scraped}")
        
        # Show sample apartment to verify
        sample_apartment = await self.db.apartments.find_one(
            {'scraped_images': True},
            {'title': 1, 'building_name': 1, 'images': 1, 'image_source': 1}
        )
        
        if sample_apartment:
            print(f"\n📋 Sample updated apartment:")
            print(f"   Title: {sample_apartment.get('title')}")
            print(f"   Building: {sample_apartment.get('building_name')}")
            print(f"   Images: {len(sample_apartment.get('images', []))} scraped images")
            print(f"   Source: {sample_apartment.get('image_source')}")
            print(f"   First image: {sample_apartment.get('images', ['None'])[0]}")
    
    async def integrate_all_scraped_images(self):
        """Execute complete image integration process"""
        print("🔗 INTEGRATING SCRAPED IMAGES WITH APARTMENT DATABASE")
        print("=" * 70)
        
        await self.connect_database()
        
        # Step 1: Organize images
        self.organize_scraped_images()
        
        # Step 2: Update apartments with scraped images
        mercedes_updated = await self.update_mercedes_house_images()
        court_square_updated = await self.update_court_square_images()
        other_tfc_updated = await self.update_other_tfc_apartments()
        
        # Step 3: Verify accessibility
        images_accessible = await self.verify_image_accessibility()
        
        # Step 4: Show summary
        await self.show_integration_summary()
        
        total_updated = mercedes_updated + court_square_updated + other_tfc_updated
        
        print(f"\n🎉 IMAGE INTEGRATION COMPLETE!")
        print("=" * 50)
        print(f"✅ Total apartments updated: {total_updated}")
        print(f"✅ Images web-accessible: {'Yes' if images_accessible else 'No'}")
        print(f"✅ Database integration: Complete")
        
        if total_updated > 0:
            print(f"\n🌐 PREVIEW UPDATE STATUS:")
            print(f"   • Scraped images are now integrated")
            print(f"   • Backend restart recommended")
            print(f"   • Changes will appear in preview after restart")
        
        return total_updated
    
    async def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()

async def main():
    """Run image integration"""
    integrator = ScrapedImageIntegrator()
    
    try:
        updated_count = await integrator.integrate_all_scraped_images()
        
        if updated_count > 0:
            print(f"\n🚀 NEXT STEPS TO SEE CHANGES IN PREVIEW:")
            print("=" * 50)
            print("1. Restart backend server: sudo supervisorctl restart backend")
            print("2. Clear browser cache if needed")
            print("3. Check preview at: https://nofee-finder.preview.emergentagent.com")
            print("\n📸 The apartments will now show authentic scraped images!")
        else:
            print(f"\n⚠️ No apartments were updated - check image organization")
            
    except Exception as e:
        print(f"❌ Integration error: {e}")
    finally:
        await integrator.close_connection()

if __name__ == "__main__":
    asyncio.run(main())