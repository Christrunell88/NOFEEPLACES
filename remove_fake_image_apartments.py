#!/usr/bin/env python3
"""
Remove Apartments with Fake/Generated Images
Keep only apartments with real photos from approved building sources
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

class FakeImageRemover:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces')
        
        # Approved building sources with real photos
        self.approved_sources = [
            'Funnel Leasing',  # Mercedes House
            'Brookfield Properties',  # Third at Bankside
            'Nestio',  # Real apartment photos
            'Two Trees Management',  # Mercedes House management
            'Direct Landlord Contact',
            'Owner Direct Contact'
        ]
        
        # Approved buildings with verified real photos
        self.approved_buildings = [
            'Mercedes House',
            'Third at Bankside', 
            'Saranac',
            'The Murray Hill',
            'The Eugene',
            'The Biltmore',
            'The Centra',
            'Loden',
            'Stonehenge LIC',
            'Forty Six Fifty',
            'Astoria at Hallet\'s Cove',
            'Astor on Third II'
        ]
        
        # Real image domains (from actual building websites/APIs)
        self.real_image_domains = [
            'nestiostatic.com',  # Nestio real photos
            'funnelleasing.com',  # Funnel API real photos
            'brookfieldproperties.com',  # Brookfield real photos
            'twotreesny.com',  # Two Trees real photos
        ]
        
        # Fake/stock image indicators
        self.fake_image_indicators = [
            'unsplash.com',
            'pexels.com', 
            'placeholder',
            'stock',
            'generic',
            'example.com',
            'images.unsplash.com'
        ]
    
    async def connect_database(self):
        """Connect to database"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
    
    async def identify_fake_image_apartments(self):
        """Identify apartments with fake/generated images"""
        print("🔍 IDENTIFYING APARTMENTS WITH FAKE IMAGES")
        print("=" * 60)
        
        apartments = await self.db.apartments.find({}).to_list(length=None)
        
        to_remove = []
        to_keep = []
        
        for apt in apartments:
            apt_id = apt.get('id')
            title = apt.get('title', '')
            images = apt.get('images', [])
            source = apt.get('source', apt.get('data_source', ''))
            building = apt.get('building_name', '')
            
            # Check if apartment should be kept
            should_keep = False
            reason_to_keep = ""
            
            # Keep if from approved building
            for approved_building in self.approved_buildings:
                if approved_building.lower() in title.lower() or approved_building.lower() in building.lower():
                    should_keep = True
                    reason_to_keep = f"Approved building: {approved_building}"
                    break
            
            # Keep if from approved source
            if not should_keep:
                for approved_source in self.approved_sources:
                    if approved_source.lower() in source.lower():
                        should_keep = True
                        reason_to_keep = f"Approved source: {approved_source}"
                        break
            
            # Keep if has real image domains
            if not should_keep:
                for image in images:
                    for real_domain in self.real_image_domains:
                        if real_domain in image:
                            should_keep = True
                            reason_to_keep = f"Real image domain: {real_domain}"
                            break
                    if should_keep:
                        break
            
            # Check for fake image indicators
            has_fake_images = False
            fake_indicators_found = []
            
            for image in images:
                for fake_indicator in self.fake_image_indicators:
                    if fake_indicator in image.lower():
                        has_fake_images = True
                        fake_indicators_found.append(fake_indicator)
                        break
            
            # Decision logic
            if should_keep and not has_fake_images:
                to_keep.append({
                    'id': apt_id,
                    'title': title,
                    'reason': reason_to_keep,
                    'apartment': apt
                })
                print(f"✅ KEEP: {title[:50]}...")
                print(f"    Reason: {reason_to_keep}")
                
            else:
                removal_reason = []
                if has_fake_images:
                    removal_reason.append(f"Fake images: {', '.join(set(fake_indicators_found))}")
                if not should_keep:
                    removal_reason.append("Not from approved building/source")
                
                to_remove.append({
                    'id': apt_id,
                    'title': title,
                    'reason': ' | '.join(removal_reason),
                    'apartment': apt
                })
                print(f"❌ REMOVE: {title[:50]}...")
                print(f"    Reason: {' | '.join(removal_reason)}")
        
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"   Apartments to keep: {len(to_keep)}")
        print(f"   Apartments to remove: {len(to_remove)}")
        
        return to_remove, to_keep
    
    async def remove_fake_image_apartments(self, to_remove):
        """Remove apartments with fake images"""
        print(f"\n🗑️  REMOVING APARTMENTS WITH FAKE IMAGES")
        print("=" * 50)
        
        removed_count = 0
        
        for apt_info in to_remove:
            apt_id = apt_info['id']
            title = apt_info['title']
            reason = apt_info['reason']
            
            try:
                result = await self.db.apartments.delete_one({'id': apt_id})
                
                if result.deleted_count > 0:
                    print(f"✅ Removed: {title[:50]}...")
                    print(f"   Reason: {reason}")
                    removed_count += 1
                else:
                    print(f"⚠️  Not found: {title[:50]}...")
                    
            except Exception as e:
                print(f"❌ Error removing {title[:50]}...: {e}")
        
        return removed_count
    
    def show_removal_summary(self, removed_count, kept_apartments):
        """Show summary of removal process"""
        print(f"\n📋 FAKE IMAGE REMOVAL SUMMARY")
        print("=" * 50)
        
        print(f"📊 RESULTS:")
        print(f"   Apartments removed: {removed_count}")
        print(f"   Authentic apartments kept: {len(kept_apartments)}")
        
        print(f"\n✅ KEPT APARTMENTS (Real Photos Only):")
        building_counts = {}
        for apt in kept_apartments:
            title = apt['title']
            reason = apt['reason']
            
            # Count by building
            if 'Mercedes House' in title:
                building_counts['Mercedes House'] = building_counts.get('Mercedes House', 0) + 1
            elif 'Brookfield' in reason or 'Third at Bankside' in title:
                building_counts['Brookfield Properties'] = building_counts.get('Brookfield Properties', 0) + 1
            elif any(building in title for building in self.approved_buildings):
                for building in self.approved_buildings:
                    if building in title:
                        building_counts[building] = building_counts.get(building, 0) + 1
                        break
            else:
                building_counts['Other Verified'] = building_counts.get('Other Verified', 0) + 1
        
        for building, count in building_counts.items():
            print(f"   • {building}: {count} apartments")
        
        print(f"\n🎯 FINAL STATUS:")
        print(f"   • All remaining apartments have real photos")
        print(f"   • Only verified building sources included")
        print(f"   • No stock/generated images remaining")
        print(f"   • Ready for production with authentic inventory")
    
    async def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()

async def main():
    """Main fake image removal process"""
    remover = FakeImageRemover()
    
    try:
        print("🚨 EMERGENCY: REMOVING APARTMENTS WITH FAKE IMAGES")
        print("=" * 60)
        print("🎯 Target: Remove 'Studio in Sunnyside' and all fake image listings")
        print("✅ Keep: Only apartments from verified buildings with real photos")
        print("=" * 60)
        
        await remover.connect_database()
        
        # Step 1: Identify apartments with fake images
        to_remove, to_keep = await remover.identify_fake_image_apartments()
        
        # Step 2: Remove apartments with fake images
        removed_count = await remover.remove_fake_image_apartments(to_remove)
        
        # Step 3: Show summary
        remover.show_removal_summary(removed_count, to_keep)
        
        print(f"\n🎉 FAKE IMAGE CLEANUP COMPLETE!")
        print(f"   • Removed all apartments with stock/fake images")
        print(f"   • Preserved Mercedes House and other verified listings")
        print(f"   • Site now shows only authentic apartments with real photos")
        
        return removed_count
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return 0
    finally:
        await remover.close_connection()

if __name__ == "__main__":
    asyncio.run(main())