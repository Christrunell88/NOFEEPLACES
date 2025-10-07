#!/usr/bin/env python3
"""
Fix Mercedes House Contact Information
Updates the contact fields to use NoFeePlaces standard contact info
"""

import asyncio
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces')

async def fix_mercedes_house_contact():
    """Fix contact information for Mercedes House apartment"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db_name = os.environ.get('DB_NAME', 'nofeeplaces')
    db = client[db_name]
    
    try:
        # Find the Mercedes House apartment
        apartment = await db.apartments.find_one({
            "building_name": "Mercedes House",
            "address": "550 West 54th Street, New York, NY 10019"
        })
        
        if not apartment:
            print("❌ Could not find Mercedes House apartment")
            return False
        
        print("📍 Found Mercedes House apartment:")
        print(f"   ID: {apartment.get('id')}")
        print(f"   Unit: {apartment.get('apartment_number')}")
        print(f"   Current Email: '{apartment.get('contact_email', '')}'")
        print(f"   Current Phone: '{apartment.get('contact_phone', '')}'")
        print()
        
        # Update with NoFeePlaces standard contact information
        updated_contact_info = {
            "contact_email": "placesfirm@gmail.com",
            "contact_phone": "+1-646-408-8048",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store the actual property management info in separate fields for internal use
        if apartment.get('contact_email') == 'mhleasing@twotreesny.com':
            updated_contact_info.update({
                "property_contact_email": "mhleasing@twotreesny.com",
                "property_contact_phone": "+1-212-876-6666",
                "management_company": "Two Trees Management Company"
            })
        
        # Update the apartment
        result = await db.apartments.update_one(
            {"id": apartment["id"]},
            {"$set": updated_contact_info}
        )
        
        if result.modified_count > 0:
            print("✅ Successfully updated Mercedes House contact information:")
            print(f"   ✅ Contact Email: {updated_contact_info['contact_email']}")
            print(f"   ✅ Contact Phone: {updated_contact_info['contact_phone']}")
            print("   ✅ Property management info stored separately for internal use")
            return True
        else:
            print("⚠️ No changes were made - contact information may already be correct")
            return True
            
    except Exception as e:
        print(f"❌ Error updating contact information: {str(e)}")
        return False
    finally:
        client.close()

async def fix_all_recent_apartments():
    """Fix contact info for any other apartments that might have wrong contact details"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db_name = os.environ.get('DB_NAME', 'nofeeplaces')
    db = client[db_name]
    
    print("\n🔍 Checking for other apartments with non-NoFeePlaces contact info...")
    
    try:
        # Find apartments that don't have the standard NoFeePlaces contact info
        apartments = await db.apartments.find({
            "$or": [
                {"contact_email": {"$ne": "placesfirm@gmail.com"}},
                {"contact_phone": {"$ne": "+1-646-408-8048"}}
            ]
        }).to_list(length=50)
        
        print(f"Found {len(apartments)} apartments with non-standard contact info")
        
        fixed_count = 0
        
        for apt in apartments:
            # Skip if it already has the correct info (edge case)
            if (apt.get('contact_email') == 'placesfirm@gmail.com' and 
                apt.get('contact_phone') == '+1-646-408-8048'):
                continue
                
            updates = {
                "contact_email": "placesfirm@gmail.com",
                "contact_phone": "+1-646-408-8048",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store original contact info if it exists and looks professional
            original_email = apt.get('contact_email', '')
            original_phone = apt.get('contact_phone', '')
            
            if original_email and '@' in original_email and 'placesfirm' not in original_email:
                updates['property_contact_email'] = original_email
            
            if original_phone and original_phone != '+1-646-408-8048':
                updates['property_contact_phone'] = original_phone
            
            await db.apartments.update_one(
                {"_id": apt["_id"]},
                {"$set": updates}
            )
            
            title = apt.get('title', 'Unknown title')[:50]
            print(f"✅ Fixed: {title}...")
            fixed_count += 1
        
        print(f"\n📊 Summary: Updated contact info for {fixed_count} apartments")
        print("   All apartments now show NoFeePlaces contact information")
        print("   Original property contacts stored separately for internal use")
        
        return fixed_count
        
    except Exception as e:
        print(f"❌ Error during batch update: {str(e)}")
        return 0
    finally:
        client.close()

async def main():
    """Main function"""
    print("🏢 Fixing Mercedes House Contact Information...")
    print("="*60)
    print("Requirement: All listings should show placesfirm@gmail.com and +1-646-408-8048")
    print("Property management contacts stored separately for internal use only")
    print()
    
    # Fix the Mercedes House apartment
    success = await fix_mercedes_house_contact()
    
    # Fix any other apartments with incorrect contact info
    fixed_count = await fix_all_recent_apartments()
    
    print("\n" + "="*60)
    if success:
        print("🎉 Mercedes House contact information has been corrected!")
        print("📧 Public Contact Email: placesfirm@gmail.com")
        print("📞 Public Contact Phone: +1-646-408-8048")
        print("🏢 Property management details stored separately for internal use")
        
        if fixed_count > 1:
            print(f"\n✅ Also fixed {fixed_count-1} other apartment listings")
        
        print("\n💡 Note: Users must sign up to access direct property management contacts")
    else:
        print("⚠️ Could not fix the contact information. Please check if the listing exists.")

if __name__ == "__main__":
    asyncio.run(main())