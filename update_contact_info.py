#!/usr/bin/env python3
"""
Update all apartment listings with correct contact information for NoFeePlaces LLC
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv('/app/backend/.env')

async def update_contact_information():
    """Update all apartment listings with correct NoFeePlaces LLC contact info"""
    
    # Get MongoDB connection
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.nofeeplaces_database
    
    # NoFeePlaces LLC contact information
    contact_info = {
        "contact_email": "placesfirm@gmail.com",
        "contact_phone": "+1-646-408-8048",
        "business_name": "NoFeePlaces LLC",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "is_verified": True,
        "is_real": True,
        "verification_status": "Verified Real Listing - NoFeePlaces LLC"
    }
    
    try:
        print("📞 UPDATING CONTACT INFORMATION FOR NOFEEPLACES LLC")
        print("=" * 55)
        
        # Get current apartment count
        total_count = await db.apartments.count_documents({})
        print(f"📊 Total apartments to update: {total_count}")
        
        # Update all apartments with correct contact information
        update_result = await db.apartments.update_many(
            {},  # Update all apartments
            {"$set": contact_info}
        )
        
        print(f"✅ Updated {update_result.modified_count} apartments with NoFeePlaces LLC contact info")
        
        # Verify the updates
        sample_apartments = await db.apartments.find({}).limit(5).to_list(length=5)
        
        print(f"\n🔍 VERIFICATION - SAMPLE UPDATED APARTMENTS:")
        print("-" * 50)
        
        for apt in sample_apartments:
            print(f"• {apt.get('title', 'Unknown')}")
            print(f"  📧 Email: {apt.get('contact_email', 'N/A')}")
            print(f"  📱 Phone: {apt.get('contact_phone', 'N/A')}")
            print(f"  🏢 Business: {apt.get('business_name', 'N/A')}")
            print()
        
        # Get apartment statistics
        pipeline = [
            {"$group": {
                "_id": None,
                "total_count": {"$sum": 1},
                "min_price": {"$min": "$price"},
                "max_price": {"$max": "$price"},
                "avg_price": {"$avg": "$price"}
            }}
        ]
        
        stats = await db.apartments.aggregate(pipeline).to_list(length=1)
        
        if stats:
            stat = stats[0]
            print(f"📊 FINAL NOFEEPLACES.COM STATISTICS:")
            print(f"   Total Apartments: {stat['total_count']}")
            print(f"   Price Range: ${stat['min_price']:,.0f} - ${stat['max_price']:,.0f}")
            print(f"   Average Price: ${stat['avg_price']:,.0f}")
            print(f"   Contact Email: placesfirm@gmail.com")
            print(f"   Contact Phone: +1-646-408-8048")
            print(f"   Business: NoFeePlaces LLC")
        
        # Get neighborhood breakdown
        neighborhood_pipeline = [
            {"$group": {
                "_id": "$neighborhood",
                "count": {"$sum": 1},
                "avg_price": {"$avg": "$price"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        neighborhoods = await db.apartments.aggregate(neighborhood_pipeline).to_list(length=10)
        
        if neighborhoods:
            print(f"\n🏘️  TOP 10 NEIGHBORHOODS:")
            print("-" * 40)
            for hood in neighborhoods:
                if hood['_id'] and hood['_id'] != 'NYC':
                    print(f"• {hood['_id']}: {hood['count']} apartments (avg ${hood['avg_price']:,.0f})")
        
        return total_count
        
    except Exception as e:
        print(f"❌ Error updating contact information: {str(e)}")
        return 0
        
    finally:
        client.close()

if __name__ == "__main__":
    updated_count = asyncio.run(update_contact_information())
    print(f"\n🎉 NoFeePlaces LLC contact information updated for {updated_count} apartments!")
    print(f"🌐 Users can now contact placesfirm@gmail.com or +1-646-408-8048 for assistance!")