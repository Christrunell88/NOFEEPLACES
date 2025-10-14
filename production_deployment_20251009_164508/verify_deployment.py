#!/usr/bin/env python3
'''
Post-Deployment Verification Script
Verifies that the migration was successful
'''
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def verify_deployment():
    '''Verify the production deployment was successful'''
    
    mongo_url = os.environ.get('PRODUCTION_MONGO_URL', 'mongodb://production:27017')
    db_name = os.environ.get('PRODUCTION_DB_NAME', 'nofeeplaces')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔍 VERIFYING PRODUCTION DEPLOYMENT")
    print("=" * 50)
    
    try:
        # Check apartment count
        total_count = await db.apartments.count_documents({})
        verified_count = await db.apartments.count_documents({'is_verified': True})
        
        print(f"📊 Total apartments: {total_count}")
        print(f"📊 Verified apartments: {verified_count}")
        
        # Check for the specific Central Park West issue
        cpw_problem = await db.apartments.find_one({
            '$and': [
                {'$or': [
                    {'title': {'$regex': 'Central Park West', '$options': 'i'}},
                    {'address': {'$regex': 'Central Park West', '$options': 'i'}}
                ]},
                {'price': {'$lt': 6000}}
            ]
        })
        
        if cpw_problem:
            print(f"❌ CRITICAL: Still found Central Park West apartment under $6,000:")
            print(f"   {cpw_problem.get('title')} - ${cpw_problem.get('price')}")
        else:
            print(f"✅ SUCCESS: No Central Park West apartments under $6,000 found")
        
        # Check pricing distribution
        price_ranges = {
            'under_3k': await db.apartments.count_documents({'price': {'$lt': 3000}},
            '3k_to_6k': await db.apartments.count_documents({'price': {'$gte': 3000, '$lt': 6000}},
            '6k_to_10k': await db.apartments.count_documents({'price': {'$gte': 6000, '$lt': 10000}},
            'over_10k': await db.apartments.count_documents({'price': {'$gte': 10000}}
        }
        
        print(f"\n💰 Pricing Distribution:")
        for range_name, count in price_ranges.items():
            percentage = (count / total_count * 100) if total_count > 0 else 0
            print(f"   {range_name}: {count} ({percentage:.1f}%)")
        
        # Check quality scores
        high_quality = await db.apartments.count_documents({'quality_score': {'$gte': 90}})
        quality_percentage = (high_quality / total_count * 100) if total_count > 0 else 0
        
        print(f"\n🏆 Quality Metrics:")
        print(f"   High quality (90+): {high_quality} ({quality_percentage:.1f}%)")
        
        # Overall assessment
        issues = []
        if cpw_problem:
            issues.append("Central Park West pricing issue persists")
        if verified_count < total_count * 0.9:
            issues.append(f"Low verification rate: {verified_count/total_count*100:.1f}%")
        if quality_percentage < 95:
            issues.append(f"Low quality score: {quality_percentage:.1f}%")
        
        if not issues:
            print(f"\n🎉 DEPLOYMENT VERIFICATION SUCCESSFUL!")
            print(f"   All quality metrics passed")
            print(f"   Central Park West issue resolved")
        else:
            print(f"\n⚠️  DEPLOYMENT ISSUES DETECTED:")
            for issue in issues:
                print(f"   - {issue}")
        
        return len(issues) == 0
        
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(verify_deployment())
    exit(0 if success else 1)
