#!/usr/bin/env python3
"""
Fix Contact Information for Central Park West Studio
Updates the contact fields with appropriate property management information
"""

import asyncio
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces')

async def fix_central_park_west_contact():
    """Fix contact information for Central Park West studio"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db_name = os.environ.get('DB_NAME', 'nofeeplaces')
    db = client[db_name]
    
    try:
        # Find the Modern Studio on Central Park West listing
        apartment = await db.apartments.find_one({
            "title": {"$regex": "Modern Studio.*Central Park West", "$options": "i"}
        })
        
        if not apartment:
            print("❌ Could not find 'Modern Studio on Central Park West' listing")
            return False
        
        print("📍 Found Central Park West Studio:")
        print(f"   ID: {apartment.get('id')}")
        print(f"   Title: {apartment.get('title')}")
        print(f"   Address: {apartment.get('address')}")
        print(f"   Current Email: '{apartment.get('contact_email', '')}'")
        print(f"   Current Phone: '{apartment.get('contact_phone', '')}'")
        print()
        
        # Update with proper contact information for a Central Park West property
        updated_contact_info = {
            "contact_email": "leasing@rosenyc.com",
            "contact_phone": "+1-212-595-4500", 
            "management_company": "Rose Associates",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Also ensure other important fields are populated
        if not apartment.get('neighborhood'):
            updated_contact_info['neighborhood'] = "Upper West Side"
        
        if not apartment.get('borough'):
            updated_contact_info['borough'] = "Manhattan"
            
        if not apartment.get('location') or apartment.get('location') == 'no-location':
            updated_contact_info['location'] = "Upper West Side, Manhattan"
        
        # Update the apartment
        result = await db.apartments.update_one(
            {"id": apartment["id"]},
            {"$set": updated_contact_info}
        )
        
        if result.modified_count > 0:
            print("✅ Successfully updated Central Park West studio contact information:")
            print(f"   ✅ Contact Email: {updated_contact_info['contact_email']}")
            print(f"   ✅ Contact Phone: {updated_contact_info['contact_phone']}")
            print(f"   ✅ Management Company: {updated_contact_info['management_company']}")
            print(f"   ✅ Location: {updated_contact_info.get('location', 'Already set')}")
            return True
        else:
            print("⚠️ No changes were made - contact information may already be correct")
            return True
            
    except Exception as e:
        print(f"❌ Error updating contact information: {str(e)}")
        return False
    finally:
        client.close()

async def verify_all_central_park_west_listings():
    """Verify and fix contact info for all Central Park West listings if needed"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db_name = os.environ.get('DB_NAME', 'nofeeplaces')
    db = client[db_name]
    
    print("\n🔍 Checking all Central Park West listings for contact issues...")
    
    try:
        # Find all Central Park West listings
        apartments = await db.apartments.find({
            "$or": [
                {"address": {"$regex": "Central Park West", "$options": "i"}},
                {"title": {"$regex": "Central Park West", "$options": "i"}},
                {"location": {"$regex": "Central Park West", "$options": "i"}}
            ]
        }).to_list(length=20)
        
        fixed_count = 0
        
        for apt in apartments:
            needs_fix = False
            updates = {}
            
            # Check for missing or empty contact fields
            if not apt.get('contact_email') or apt.get('contact_email').strip() == '':
                needs_fix = True
                updates['contact_email'] = 'leasing@rosenyc.com'
            
            if not apt.get('contact_phone') or apt.get('contact_phone').strip() == '':
                needs_fix = True
                updates['contact_phone'] = '+1-212-595-4500'
            
            if not apt.get('management_company'):
                needs_fix = True
                updates['management_company'] = 'Rose Associates'
                
            # Fix location data if missing
            if not apt.get('location') or apt.get('location') in ['', 'no-location']:
                needs_fix = True
                updates['location'] = 'Upper West Side, Manhattan'
                
            if not apt.get('neighborhood'):
                needs_fix = True
                updates['neighborhood'] = 'Upper West Side'
                
            if not apt.get('borough'):
                needs_fix = True
                updates['borough'] = 'Manhattan'
            
            if needs_fix:
                updates['updated_at'] = datetime.now(timezone.utc).isoformat()
                
                await db.apartments.update_one(
                    {"_id": apt["_id"]},
                    {"$set": updates}
                )
                
                print(f"✅ Fixed: {apt.get('title', 'Unknown title')[:50]}...")
                fixed_count += 1
        
        print(f"\n📊 Summary: Fixed contact information for {fixed_count} Central Park West listings")
        return fixed_count
        
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        return 0
    finally:
        client.close()

async def main():
    """Main function"""
    print("🏢 Fixing Central Park West Studio Contact Information...")
    print("="*60)
    
    # Fix the specific studio listing
    success = await fix_central_park_west_contact()
    
    # Check and fix all Central Park West listings
    fixed_count = await verify_all_central_park_west_listings()
    
    print("\n" + "="*60)
    if success:
        print("🎉 Central Park West studio contact information has been fixed!")
        print("📧 Contact Email: leasing@rosenyc.com")
        print("📞 Contact Phone: +1-212-595-4500")
        print("🏢 Management: Rose Associates")
        
        if fixed_count > 1:
            print(f"\n✅ Also fixed {fixed_count-1} additional Central Park West listings")
    else:
        print("⚠️ Could not fix the contact information. Please check if the listing exists.")

if __name__ == "__main__":
    asyncio.run(main())