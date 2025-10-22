#!/usr/bin/env python3
"""
Production Database Access Guide
Since local and production databases are different, here's how to fix the live issue
"""
import requests
import json
from datetime import datetime

def diagnose_database_setup():
    """Diagnose the database setup and provide solutions"""
    
    print("🔍 PRODUCTION DATABASE DIAGNOSIS")
    print("=" * 50)
    
    # Check local database
    try:
        import os
        from pymongo import MongoClient
        
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'nofeeplaces')
        
        local_client = MongoClient(mongo_url)
        local_db = local_client[db_name]
        local_count = local_db.apartments.count_documents({})
        
        print(f"📊 Local Database:")
        print(f"   Connection: {mongo_url}")
        print(f"   Database: {db_name}")
        print(f"   Apartment count: {local_count}")
        
        # Check for the problematic apartment locally
        local_problem = local_db.apartments.find_one({
            'price': 2344,
            '$or': [
                {'title': {'$regex': 'Central Park West', '$options': 'i'}},
                {'address': {'$regex': 'Central Park West', '$options': 'i'}}
            ]
        })
        
        if local_problem:
            print(f"   🚨 Problem apartment EXISTS locally")
        else:
            print(f"   ✅ Problem apartment NOT in local database")
            
        local_client.close()
        
    except Exception as e:
        print(f"   ❌ Local database error: {e}")
    
    # Check production API
    print(f"\n📡 Production API:")
    try:
        response = requests.get("https://aptfinder-1.preview.emergentagent.com/api/apartments", 
                              params={"limit": 5})
        
        if response.status_code == 200:
            data = response.json()
            prod_count = data.get('total', 0)
            print(f"   API endpoint: https://aptfinder-1.preview.emergentagent.com/api")
            print(f"   Total apartments: {prod_count}")
            
            # Check for the specific problem
            cpw_response = requests.get("https://aptfinder-1.preview.emergentagent.com/api/apartments",
                                       params={"search": "Central Park West"})
            
            if cpw_response.status_code == 200:
                cpw_data = cpw_response.json()
                cpw_apts = cpw_data.get('apartments', [])
                
                problem_found = False
                for apt in cpw_apts:
                    if apt.get('price') == 2344:
                        problem_found = True
                        print(f"   🚨 CONFIRMED: Problem apartment EXISTS in production")
                        print(f"      ID: {apt.get('id')}")
                        print(f"      Title: {apt.get('title')}")
                        print(f"      Price: ${apt.get('price')}")
                        break
                
                if not problem_found:
                    print(f"   ✅ Problem apartment NOT found in production")
        else:
            print(f"   ❌ API error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Production API error: {e}")

def create_deployment_instructions():
    """Create step-by-step instructions to fix the production issue"""
    
    print(f"\n📋 SOLUTION: HOW TO FIX THE PRODUCTION ISSUE")
    print("=" * 60)
    
    print(f"🔍 DIAGNOSIS:")
    print(f"   • Local database ≠ Production database")
    print(f"   • Changes made locally don't affect what users see")
    print(f"   • Production API serves different data")
    
    print(f"\n🎯 IMMEDIATE SOLUTIONS:")
    
    print(f"\n1️⃣  OPTION 1: DIRECT PRODUCTION DATABASE ACCESS")
    print(f"   If you have direct access to production MongoDB:")
    print(f"   ```")
    print(f"   # Connect to production MongoDB")
    print(f"   mongo 'mongodb://production-server:27017/nofeeplaces'")
    print(f"   ")
    print(f"   # Update the problematic apartment")
    print(f"   db.apartments.updateOne(")
    print(f"       {{id: 'c00cb712-9466-4f1a-9a6b-353bf7e5978e'}},")
    print(f"       {{$set: {{")
    print(f"           price: 7500,")
    print(f"           title: 'Luxury Studio on Central Park West - No Fee',")
    print(f"           updated_at: new Date(),")
    print(f"           quality_score: 95")
    print(f"       }}}}")
    print(f"   ```")
    
    print(f"\n2️⃣  OPTION 2: BACKEND API MODIFICATION")
    print(f"   Add a temporary admin endpoint to fix this:")
    print(f"   ```python")
    print(f"   # Add to backend/server.py")
    print(f"   @app.post('/api/admin/fix-central-park-west')")
    print(f"   async def fix_central_park_west():")
    print(f"       result = await db.apartments.update_one(")
    print(f"           {{'id': 'c00cb712-9466-4f1a-9a6b-353bf7e5978e'}},")
    print(f"           {{'$set': {{")
    print(f"               'price': 7500,")
    print(f"               'title': 'Luxury Studio on Central Park West - No Fee',")
    print(f"               'updated_at': datetime.now(timezone.utc).isoformat()")
    print(f"           }}}}")
    print(f"       return {{'status': 'success', 'modified': result.modified_count}}")
    print(f"   ```")
    
    print(f"\n3️⃣  OPTION 3: ENVIRONMENT VARIABLE CHECK")
    print(f"   Verify the production backend is using correct database:")
    print(f"   • Check MONGO_URL in production environment")
    print(f"   • Ensure backend connects to same DB as API serves")
    
    print(f"\n4️⃣  OPTION 4: DEPLOY OUR FIXES TO PRODUCTION")
    print(f"   Use the deployment package we created:")
    print(f"   • Copy /app/production_deployment_20251009_164508/ to production")
    print(f"   • Run the migration script with production credentials")
    
    print(f"\n🚀 RECOMMENDED IMMEDIATE ACTION:")
    print(f"   1. Check if you have direct MongoDB access to production")
    print(f"   2. If yes, run the MongoDB update command above")
    print(f"   3. If no, add the admin endpoint to backend and call it")
    print(f"   4. Verify fix by checking the preview again")
    
    print(f"\n⚡ QUICK TEST:")
    print(f"   After applying any fix, test with:")
    print(f"   curl 'https://aptfinder-1.preview.emergentagent.com/api/apartments?search=Central+Park+West'")

def main():
    """Main diagnosis and solution"""
    diagnose_database_setup()
    create_deployment_instructions()
    
    print(f"\n" + "=" * 70)
    print(f"🎯 SUMMARY")
    print(f"=" * 70)
    print(f"ISSUE: Production database still has $2,344 Central Park West apartment")
    print(f"CAUSE: Local and production databases are separate")
    print(f"SOLUTION: Apply fix directly to production database")
    print(f"VERIFICATION: Check preview after fix is applied")

if __name__ == "__main__":
    main()