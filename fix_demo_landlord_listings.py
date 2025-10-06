#!/usr/bin/env python3
"""
Fix demo landlord listings - connect existing demo apartments to demo landlord
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_db')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

async def fix_demo_landlord_listings():
    """Connect demo apartments to demo landlord and add view tracking"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔧 Fixing demo landlord listings...")
    
    demo_landlord_id = "demo-landlord-2025"
    
    # Find apartments that should belong to demo landlord (created by our demo script)
    demo_apartment_addresses = [
        "350 W 42nd Street, New York, NY 10036",  # Midtown
        "75 Wall Street, New York, NY 10005",     # Financial District
        "200 W 26th Street, New York, NY 10001"  # Chelsea
    ]
    
    # Update these apartments to have the demo landlord_id
    for address in demo_apartment_addresses:
        result = await db.apartments.update_many(
            {"address": address},
            {
                "$set": {
                    "landlord_id": demo_landlord_id,
                    "contact_info.email": "demo@nofeeplaces.com",
                    "contact_info.phone": "+1 (212) 555-0123",
                    "contact_info.company": "Manhattan Properties LLC"
                }
            }
        )
        print(f"✅ Updated {result.modified_count} apartments at {address}")
    
    # Add some fake view counts for demo purposes
    apartments = await db.apartments.find({"landlord_id": demo_landlord_id}).to_list(length=None)
    
    for i, apartment in enumerate(apartments):
        # Create fake view records for analytics
        view_counts = [45, 38, 29]  # Different view counts for each apartment
        
        # Clear existing views for this apartment
        await db.apartment_views.delete_many({"apartment_id": apartment["id"]})
        
        # Add fake view records
        fake_views = []
        for view_num in range(view_counts[i] if i < len(view_counts) else 20):
            fake_views.append({
                "id": f"view-{apartment['id']}-{view_num}",
                "apartment_id": apartment["id"],
                "ip_address": f"192.168.1.{view_num % 50 + 100}",
                "user_agent": "Mozilla/5.0 (Demo Browser)",
                "timestamp": "2025-09-30T12:00:00Z"
            })
        
        if fake_views:
            await db.apartment_views.insert_many(fake_views)
        
        print(f"✅ Added {len(fake_views)} view records for {apartment['title']}")
    
    # Verify the setup
    total_listings = await db.apartments.count_documents({"landlord_id": demo_landlord_id})
    total_views = await db.apartment_views.count_documents({
        "apartment_id": {"$in": [apt["id"] for apt in apartments]}
    })
    total_inquiries = await db.contacts.count_documents({"landlord_id": demo_landlord_id})
    
    print(f"\n🎯 Demo Landlord Setup Complete:")
    print(f"📋 Total listings: {total_listings}")
    print(f"👀 Total views: {total_views}")
    print(f"📞 Total inquiries: {total_inquiries}")
    print(f"\n🔗 Dashboard URL:")
    print(f"   https://rentalnobroker.preview.emergentagent.com/landlord/dashboard/{demo_landlord_id}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_demo_landlord_listings())