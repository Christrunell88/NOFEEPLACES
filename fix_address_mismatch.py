#!/usr/bin/env python3
"""
Fix data quality issue: Central Park West address with wrong neighborhood
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def fix_address_neighborhood_mismatch():
    """Fix the Central Park West apartment with incorrect LIC neighborhood"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.nofeeplaces_database
    
    try:
        print("🔍 FIXING ADDRESS/NEIGHBORHOOD MISMATCH")
        print("=" * 45)
        
        # Find the problematic apartment
        problem_apt = await db.apartments.find_one({
            "address": {"$regex": "Central Park West"},
            "neighborhood": "Long Island City"
        })
        
        if problem_apt:
            print(f"❌ FOUND PROBLEM APARTMENT:")
            print(f"   ID: {problem_apt['id']}")
            print(f"   Title: {problem_apt['title']}")
            print(f"   Address: {problem_apt['address']}")
            print(f"   Wrong Neighborhood: {problem_apt['neighborhood']}")
            print(f"   Price: ${problem_apt['price']}")
            print(f"   Bedrooms: {problem_apt['bedrooms']}")
            
            # Fix the data
            corrected_data = {
                "neighborhood": "Upper West Side",
                "location": "Upper West Side, Manhattan",
                "borough": "Manhattan",
                "address": "753 Central Park West, New York, NY 10025",  # Correct ZIP
                "title": "Modern Studio on Central Park West - No Fee"
            }
            
            result = await db.apartments.update_one(
                {"id": problem_apt['id']},
                {"$set": corrected_data}
            )
            
            if result.modified_count > 0:
                print(f"\n✅ FIXED APARTMENT:")
                print(f"   New Neighborhood: Upper West Side")
                print(f"   New Location: Upper West Side, Manhattan")
                print(f"   New Borough: Manhattan")
                print(f"   Corrected Address: 753 Central Park West, New York, NY 10025")
                print(f"   Updated Title: Modern Studio on Central Park West - No Fee")
            
            # Verify the fix
            fixed_apt = await db.apartments.find_one({"id": problem_apt['id']})
            print(f"\n🔍 VERIFICATION:")
            print(f"   Address: {fixed_apt['address']}")
            print(f"   Neighborhood: {fixed_apt['neighborhood']}")
            print(f"   Location: {fixed_apt['location']}")
            print(f"   Borough: {fixed_apt['borough']}")
        else:
            print("❌ Problem apartment not found")
            
        # Check for any other address/neighborhood mismatches
        print(f"\n🔍 CHECKING FOR OTHER MISMATCHES...")
        
        manhattan_addresses = await db.apartments.find({
            "address": {"$regex": "(Central Park|Columbus Avenue|Amsterdam Avenue|Broadway|Madison Avenue|5th Avenue|Park Avenue|Lexington Avenue)"},
            "neighborhood": {"$in": ["Long Island City", "Astoria", "Sunnyside", "Forest Hills"]}
        }).to_list(length=10)
        
        if manhattan_addresses:
            print(f"⚠️  Found {len(manhattan_addresses)} more potential address/neighborhood mismatches:")
            for apt in manhattan_addresses:
                print(f"   • {apt['address']} → {apt['neighborhood']}")
        else:
            print("✅ No other obvious Manhattan/Queens mismatches found")
            
    except Exception as e:
        print(f"❌ Error fixing address mismatch: {str(e)}")
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_address_neighborhood_mismatch())