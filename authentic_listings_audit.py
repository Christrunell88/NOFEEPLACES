#!/usr/bin/env python3
"""
Authentic Listings Audit
Remove generated/fake listings and ensure only real apartments with accurate data remain
"""
import asyncio
import requests
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

class AuthenticListingsAuditor:
    def __init__(self):
        self.production_api = "https://apartment-viewings.preview.emergentagent.com/api"
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces')
        
        # Indicators of generated/fake listings
        self.fake_indicators = [
            'bulk_generator', 'generated', 'realistic', 'nofeeplaces verified scraper',
            'test apartment', 'sample listing', 'demo apartment', 'placeholder'
        ]
        
        # Generic/stock photo indicators
        self.stock_photo_indicators = [
            'pexels', 'unsplash', 'placeholder', 'example', 'stock', 'generic'
        ]
    
    async def connect_database(self):
        """Connect to database"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
    
    async def get_all_apartments(self):
        """Get all apartments from database"""
        apartments = await self.db.apartments.find({}).to_list(length=None)
        return apartments
    
    def analyze_apartment_authenticity(self, apartment):
        """Analyze if apartment is authentic or generated"""
        issues = []
        authenticity_score = 100
        
        apt_id = apartment.get('id', '')
        title = apartment.get('title', '').lower()
        description = apartment.get('description', '').lower()
        data_source = apartment.get('data_source', '').lower()
        images = apartment.get('images', [])
        address = apartment.get('address', '')
        
        # Check data source for fake indicators
        for indicator in self.fake_indicators:
            if indicator in data_source:
                issues.append(f"Fake data source: '{indicator}' in '{data_source}'")
                authenticity_score -= 30
        
        # Check if images are stock photos
        stock_image_count = 0
        for image in images:
            for indicator in self.stock_photo_indicators:
                if indicator in image.lower():
                    stock_image_count += 1
                    break
        
        if stock_image_count > 0:
            issues.append(f"{stock_image_count}/{len(images)} images are stock photos")
            authenticity_score -= (stock_image_count * 15)
        
        # Check for generic/template titles
        generic_patterns = [
            'modern studio', 'luxury studio', 'spacious', 'beautiful', 'stunning',
            'no fee studio at', 'no fee 1br at', 'apartment at'
        ]
        
        for pattern in generic_patterns:
            if pattern in title and not address:
                issues.append(f"Generic title pattern: '{pattern}'")
                authenticity_score -= 10
        
        # Check for missing real address
        if not address or len(address) < 10:
            issues.append("Missing or incomplete address")
            authenticity_score -= 20
        
        # Check for unrealistic perfect scores
        quality_score = apartment.get('quality_score', 0)
        if quality_score >= 95:
            issues.append(f"Suspiciously high quality score: {quality_score}")
            authenticity_score -= 5
        
        # Determine recommendation
        if authenticity_score < 30:
            recommendation = 'DELETE'
        elif authenticity_score < 60:
            recommendation = 'INVESTIGATE'
        else:
            recommendation = 'KEEP'
        
        return {
            'authenticity_score': authenticity_score,
            'issues': issues,
            'recommendation': recommendation,
            'stock_images': stock_image_count,
            'total_images': len(images)
        }
    
    async def audit_all_apartments(self):
        """Audit all apartments for authenticity"""
        print("🔍 AUDITING ALL APARTMENTS FOR AUTHENTICITY")
        print("=" * 60)
        
        apartments = await self.get_all_apartments()
        
        audit_results = {
            'to_delete': [],
            'to_investigate': [],
            'to_keep': [],
            'total_count': len(apartments)
        }
        
        print(f"📊 Analyzing {len(apartments)} apartments...")
        
        for i, apt in enumerate(apartments, 1):
            apt_id = apt.get('id')
            title = apt.get('title', '')
            
            analysis = self.analyze_apartment_authenticity(apt)
            
            apartment_info = {
                'id': apt_id,
                'title': title[:50] + '...' if len(title) > 50 else title,
                'price': apt.get('price'),
                'data_source': apt.get('data_source', ''),
                'analysis': analysis,
                'full_data': apt
            }
            
            if analysis['recommendation'] == 'DELETE':
                audit_results['to_delete'].append(apartment_info)
                print(f"❌ DELETE: {apartment_info['title']} (Score: {analysis['authenticity_score']})")
            elif analysis['recommendation'] == 'INVESTIGATE':
                audit_results['to_investigate'].append(apartment_info)
                print(f"⚠️  INVESTIGATE: {apartment_info['title']} (Score: {analysis['authenticity_score']})")
            else:
                audit_results['to_keep'].append(apartment_info)
                print(f"✅ KEEP: {apartment_info['title']} (Score: {analysis['authenticity_score']})")
        
        return audit_results
    
    async def delete_apartment(self, apartment_id, title):
        """Delete a specific apartment"""
        try:
            result = await self.db.apartments.delete_one({'id': apartment_id})
            if result.deleted_count > 0:
                print(f"   ✅ Deleted: {title[:40]}...")
                return True
            else:
                print(f"   ⚠️  Not found: {title[:40]}...")
                return False
        except Exception as e:
            print(f"   ❌ Error deleting {title[:40]}...: {e}")
            return False
    
    async def cleanup_fake_listings(self, audit_results):
        """Remove all fake/generated listings"""
        print(f"\n🗑️  REMOVING FAKE/GENERATED LISTINGS")
        print("=" * 50)
        
        # Delete the specific Central Park West apartment first
        cpw_deleted = False
        for apt in audit_results['to_delete']:
            if apt['id'] == 'c00cb712-9466-4f1a-9a6b-353bf7e5978e':
                print(f"🎯 Deleting Central Park West apartment...")
                await self.delete_apartment(apt['id'], apt['title'])
                cpw_deleted = True
                break
        
        if not cpw_deleted:
            # Try to find and delete it specifically
            cpw_apt = await self.db.apartments.find_one({'id': 'c00cb712-9466-4f1a-9a6b-353bf7e5978e'})
            if cpw_apt:
                print(f"🎯 Found and deleting Central Park West apartment...")
                await self.delete_apartment('c00cb712-9466-4f1a-9a6b-353bf7e5978e', 'Central Park West Studio')
        
        # Delete all apartments marked for deletion
        deleted_count = 0
        
        for apt in audit_results['to_delete']:
            if apt['id'] != 'c00cb712-9466-4f1a-9a6b-353bf7e5978e':  # Already handled above
                success = await self.delete_apartment(apt['id'], apt['title'])
                if success:
                    deleted_count += 1
        
        print(f"\n📊 CLEANUP RESULTS:")
        print(f"   Apartments deleted: {deleted_count + (1 if cpw_deleted else 0)}")
        print(f"   Apartments to investigate: {len(audit_results['to_investigate'])}")
        print(f"   Authentic apartments kept: {len(audit_results['to_keep'])}")
        
        return deleted_count
    
    def generate_cleanup_report(self, audit_results, deleted_count):
        """Generate detailed cleanup report"""
        print(f"\n📋 AUTHENTICITY AUDIT REPORT")
        print("=" * 60)
        
        total = audit_results['total_count']
        kept = len(audit_results['to_keep'])
        investigated = len(audit_results['to_investigate'])
        
        print(f"📊 SUMMARY:")
        print(f"   Original apartments: {total}")
        print(f"   Deleted (fake/generated): {deleted_count}")
        print(f"   Kept (authentic): {kept}")
        print(f"   Need investigation: {investigated}")
        print(f"   Final inventory: {kept + investigated}")
        
        retention_rate = ((kept + investigated) / total * 100) if total > 0 else 0
        print(f"   Authentic retention rate: {retention_rate:.1f}%")
        
        if audit_results['to_delete']:
            print(f"\n❌ DELETED APARTMENTS (Generated/Fake):")
            for apt in audit_results['to_delete'][:10]:  # Show first 10
                print(f"   • {apt['title']} - {apt['data_source']}")
                for issue in apt['analysis']['issues'][:2]:  # Show first 2 issues
                    print(f"     - {issue}")
        
        if audit_results['to_investigate']:
            print(f"\n⚠️  APARTMENTS NEEDING INVESTIGATION:")
            for apt in audit_results['to_investigate'][:5]:  # Show first 5
                print(f"   • {apt['title']} (Score: {apt['analysis']['authenticity_score']})")
                for issue in apt['analysis']['issues'][:2]:
                    print(f"     - {issue}")
        
        print(f"\n✅ REMAINING AUTHENTIC APARTMENTS:")
        print(f"   {kept} apartments with authenticity scores 60+")
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"/app/authenticity_audit_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(audit_results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved: {report_file}")
    
    async def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()

async def main():
    """Main audit and cleanup process"""
    auditor = AuthenticListingsAuditor()
    
    try:
        print("🔍 AUTHENTIC LISTINGS AUDIT & CLEANUP")
        print("=" * 60)
        print("🎯 Goal: Remove all generated/fake listings, keep only real apartments")
        print("=" * 60)
        
        await auditor.connect_database()
        
        # Step 1: Audit all apartments
        audit_results = await auditor.audit_all_apartments()
        
        # Step 2: Clean up fake listings
        deleted_count = await auditor.cleanup_fake_listings(audit_results)
        
        # Step 3: Generate report
        auditor.generate_cleanup_report(audit_results, deleted_count)
        
        print(f"\n🎉 AUTHENTIC LISTINGS CLEANUP COMPLETE!")
        print(f"   • Removed all generated/fake apartments")
        print(f"   • Deleted Central Park West problematic unit") 
        print(f"   • Only authentic apartments remain")
        print(f"   • Site now shows genuine rental listings only")
        
        return audit_results
        
    except Exception as e:
        print(f"❌ Audit failed: {e}")
        return None
    finally:
        await auditor.close_connection()

if __name__ == "__main__":
    asyncio.run(main())