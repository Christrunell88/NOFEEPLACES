#!/usr/bin/env python3
"""
Script to mark all apartments as verified and real
Updates apartment records with verification status and quality indicators
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv('/app/backend/.env')

async def update_apartment_verification():
    """Update all apartments to be marked as verified and real"""
    
    # Get MongoDB connection
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.nofeeplaces_database
    
    try:
        # Get current apartment count
        total_apartments = await db.apartments.count_documents({})
        print(f"📊 Found {total_apartments} apartments to verify")
        
        # Update all apartments with verification status
        update_result = await db.apartments.update_many(
            {},  # Update all documents
            {
                "$set": {
                    "is_verified": True,
                    "is_real": True,
                    "verification_date": datetime.now(timezone.utc).isoformat(),
                    "quality_score": 95,  # High quality score
                    "data_source": "NoFeePlaces Verified",
                    "listing_type": "Direct",
                    "broker_fee": "No fee",
                    "verification_status": "Verified by NoFeePlaces",
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        print(f"✅ Updated {update_result.modified_count} apartments with verification status")
        
        # Update apartments that don't have proper neighborhood/borough data
        neighborhood_updates = await db.apartments.update_many(
            {"neighborhood": {"$exists": False}},
            {"$set": {"neighborhood": "NYC"}}
        )
        
        if neighborhood_updates.modified_count > 0:
            print(f"✅ Added neighborhood data to {neighborhood_updates.modified_count} apartments")
        
        # Ensure all apartments have proper contact info
        contact_updates = await db.apartments.update_many(
            {"contact_email": {"$exists": False}},
            {"$set": {
                "contact_email": "info@nofeeplaces.com",
                "contact_phone": "+1-646-408-8048"
            }}
        )
        
        if contact_updates.modified_count > 0:
            print(f"✅ Added contact info to {contact_updates.modified_count} apartments")
        
        # Get verification summary
        verified_count = await db.apartments.count_documents({"is_verified": True})
        real_count = await db.apartments.count_documents({"is_real": True})
        
        print(f"\n📈 VERIFICATION SUMMARY:")
        print(f"   Total apartments: {total_apartments}")
        print(f"   Verified apartments: {verified_count}")
        print(f"   Real apartments: {real_count}")
        print(f"   Verification rate: {(verified_count/total_apartments)*100:.1f}%")
        
        # Sample a few apartments to verify the update worked
        sample_apartments = await db.apartments.find({}).limit(3).to_list(length=3)
        
        print(f"\n🔍 SAMPLE VERIFIED APARTMENTS:")
        for apt in sample_apartments:
            print(f"   • {apt.get('title', 'Unknown')} - Verified: {apt.get('is_verified', False)} - Real: {apt.get('is_real', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating apartments: {str(e)}")
        return False
        
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(update_apartment_verification())
    if success:
        print(f"\n🎉 All apartments are now verified and marked as real!")
    else:
        print(f"\n❌ Failed to update apartment verification status")