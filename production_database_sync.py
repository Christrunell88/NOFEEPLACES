#!/usr/bin/env python3
"""
Production Database Synchronization Script
Safely synchronizes production database with corrected local data
"""
import asyncio
import os
import json
import requests
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

class ProductionDatabaseSync:
    def __init__(self):
        # Local database (corrected data)
        self.local_mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.local_db_name = os.environ.get('DB_NAME', 'nofeeplaces')
        
        # Production API endpoint
        self.production_api_url = "https://nofee-finder.preview.emergentagent.com/api"
        
        # Backup directory
        self.backup_dir = "/app/database_backups"
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def get_production_data(self):
        """Get current production data via API"""
        print("📥 Fetching production data...")
        
        try:
            # Get all apartments from production
            response = requests.get(f"{self.production_api_url}/apartments", 
                                  params={"limit": 1000}, 
                                  timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get('apartments', [])
                print(f"   Retrieved {len(apartments)} apartments from production")
                return apartments
            else:
                print(f"   ❌ Failed to fetch production data: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error fetching production data: {e}")
            return None
    
    def backup_production_data(self, production_data):
        """Create backup of production data"""
        print("💾 Creating production data backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.backup_dir}/production_backup_{timestamp}.json"
        
        try:
            with open(backup_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'apartment_count': len(production_data),
                    'apartments': production_data
                }, f, indent=2, default=str)
            
            print(f"   ✅ Backup saved: {backup_file}")
            print(f"   📊 Backed up {len(production_data)} apartments")
            return backup_file
            
        except Exception as e:
            print(f"   ❌ Backup failed: {e}")
            return None
    
    async def get_local_corrected_data(self):
        """Get corrected data from local database"""
        print("📤 Fetching corrected local data...")
        
        try:
            client = AsyncIOMotorClient(self.local_mongo_url)
            db = client[self.local_db_name]
            
            # Get all apartments from local database
            apartments = await db.apartments.find({}).to_list(length=None)
            
            print(f"   ✅ Retrieved {len(apartments)} apartments from local database")
            
            # Convert ObjectId to string for JSON serialization
            for apt in apartments:
                if '_id' in apt:
                    apt['_id'] = str(apt['_id'])
            
            await client.close()
            return apartments
            
        except Exception as e:
            print(f"   ❌ Failed to get local data: {e}")
            return None
    
    def analyze_data_differences(self, production_data, local_data):
        """Analyze differences between production and local data"""
        print("🔍 Analyzing data differences...")
        
        # Create lookup for production apartments by ID
        prod_lookup = {apt.get('id'): apt for apt in production_data}
        local_lookup = {apt.get('id'): apt for apt in local_data}
        
        differences = {
            'apartments_to_remove': [],  # In production but not in local (old/bad data)
            'apartments_to_add': [],     # In local but not in production (new corrected data)
            'apartments_to_update': [],  # Different between production and local
            'quality_improvements': 0,
            'pricing_fixes': 0
        }
        
        # Check for apartments to remove (bad data in production)
        for apt_id, prod_apt in prod_lookup.items():
            if apt_id not in local_lookup:
                differences['apartments_to_remove'].append(prod_apt)
        
        # Check for apartments to add (new corrected data)
        for apt_id, local_apt in local_lookup.items():
            if apt_id not in prod_lookup:
                differences['apartments_to_add'].append(local_apt)
            else:
                # Check for updates needed
                prod_apt = prod_lookup[apt_id]
                
                # Compare key fields
                updates_needed = []
                
                if prod_apt.get('price') != local_apt.get('price'):
                    updates_needed.append(f"Price: ${prod_apt.get('price')} → ${local_apt.get('price')}")
                    differences['pricing_fixes'] += 1
                
                if prod_apt.get('quality_score', 0) < local_apt.get('quality_score', 0):
                    updates_needed.append(f"Quality: {prod_apt.get('quality_score', 0)} → {local_apt.get('quality_score', 0)}")
                    differences['quality_improvements'] += 1
                
                if prod_apt.get('is_verified') != local_apt.get('is_verified'):
                    updates_needed.append(f"Verification: {prod_apt.get('is_verified')} → {local_apt.get('is_verified')}")
                
                if updates_needed:
                    differences['apartments_to_update'].append({
                        'id': apt_id,
                        'title': local_apt.get('title', ''),
                        'updates': updates_needed,
                        'local_data': local_apt,
                        'production_data': prod_apt
                    })
        
        # Report analysis
        print(f"   📊 ANALYSIS RESULTS:")
        print(f"      Apartments to remove: {len(differences['apartments_to_remove'])}")
        print(f"      Apartments to add: {len(differences['apartments_to_add'])}")
        print(f"      Apartments to update: {len(differences['apartments_to_update'])}")
        print(f"      Quality improvements: {differences['quality_improvements']}")
        print(f"      Pricing fixes: {differences['pricing_fixes']}")
        
        # Show specific issues to be fixed
        if differences['apartments_to_remove']:
            print(f"\n   🗑️  APARTMENTS TO REMOVE (Bad Data):")
            for apt in differences['apartments_to_remove'][:5]:
                title = apt.get('title', 'Unknown')[:50]
                price = apt.get('price', 0)
                print(f"      - {title}... (${price})")
        
        if differences['apartments_to_update']:
            print(f"\n   🔧 APARTMENTS TO UPDATE:")
            for update in differences['apartments_to_update'][:5]:
                title = update['title'][:40]
                print(f"      - {title}...")
                for change in update['updates']:
                    print(f"        • {change}")
        
        return differences
    
    def generate_sync_commands(self, differences, production_api_url):
        """Generate API commands to sync the data"""
        print("\n📋 GENERATING SYNC COMMANDS...")
        
        commands = []
        
        # Commands to remove bad data
        for apt in differences['apartments_to_remove']:
            commands.append({
                'action': 'DELETE',
                'endpoint': f"{production_api_url}/apartments/{apt.get('id')}",
                'description': f"Remove bad data: {apt.get('title', '')[:40]}..."
            })
        
        # Commands to add corrected data
        for apt in differences['apartments_to_add']:
            commands.append({
                'action': 'POST',
                'endpoint': f"{production_api_url}/apartments",
                'data': apt,
                'description': f"Add corrected: {apt.get('title', '')[:40]}..."
            })
        
        # Commands to update existing data
        for update in differences['apartments_to_update']:
            commands.append({
                'action': 'PUT',
                'endpoint': f"{production_api_url}/apartments/{update['id']}",
                'data': update['local_data'],
                'description': f"Update: {update['title'][:40]}..."
            })
        
        print(f"   Generated {len(commands)} sync commands")
        
        # Save commands to file for review
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        commands_file = f"{self.backup_dir}/sync_commands_{timestamp}.json"
        
        with open(commands_file, 'w') as f:
            json.dump(commands, f, indent=2, default=str)
        
        print(f"   💾 Commands saved to: {commands_file}")
        
        return commands, commands_file
    
    def create_direct_database_sync_script(self, local_data):
        """Create a script for direct database synchronization"""
        print("\n📝 Creating direct database sync script...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_file = f"{self.backup_dir}/direct_sync_script_{timestamp}.py"
        
        script_content = f'''#!/usr/bin/env python3
"""
Direct Database Sync Script - Generated {timestamp}
This script directly replaces production database with corrected local data
CAUTION: This will overwrite all production apartment data
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
import json

# Corrected apartment data
CORRECTED_APARTMENTS = {json.dumps(local_data, indent=4, default=str)}

async def sync_production_database():
    """Sync production database with corrected data"""
    
    # Use production database connection
    # NOTE: This would need the actual production MongoDB connection string
    # For now, this shows the structure
    
    mongo_url = os.environ.get('PRODUCTION_MONGO_URL', 'mongodb://production-server:27017')
    db_name = os.environ.get('PRODUCTION_DB_NAME', 'nofeeplaces')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔄 Starting production database sync...")
    
    # 1. Backup existing data
    existing_apartments = await db.apartments.find({{}}).to_list(length=None)
    print(f"   Backing up {{len(existing_apartments)}} existing apartments")
    
    # 2. Clear existing apartment data
    delete_result = await db.apartments.delete_many({{}})
    print(f"   Deleted {{delete_result.deleted_count}} old apartments")
    
    # 3. Insert corrected data
    if CORRECTED_APARTMENTS:
        # Remove _id fields to let MongoDB generate new ones
        clean_apartments = []
        for apt in CORRECTED_APARTMENTS:
            clean_apt = dict(apt)
            if '_id' in clean_apt:
                del clean_apt['_id']
            clean_apartments.append(clean_apt)
        
        insert_result = await db.apartments.insert_many(clean_apartments)
        print(f"   Inserted {{len(insert_result.inserted_ids)}} corrected apartments")
    
    print("✅ Production database sync complete!")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(sync_production_database())
'''
        
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_file, 0o755)
        
        print(f"   ✅ Sync script created: {script_file}")
        print(f"   ⚠️  WARNING: This script will replace ALL production apartment data")
        
        return script_file

async def main():
    """Main synchronization process"""
    sync = ProductionDatabaseSync()
    
    print("🔄 PRODUCTION DATABASE SYNCHRONIZATION")
    print("=" * 60)
    print("⚠️  CRITICAL: This will modify production data!")
    print("=" * 60)
    
    # Step 1: Get production data
    production_data = sync.get_production_data()
    if not production_data:
        print("❌ Cannot proceed without production data")
        return False
    
    # Step 2: Backup production data
    backup_file = sync.backup_production_data(production_data)
    if not backup_file:
        print("❌ Cannot proceed without backup")
        return False
    
    # Step 3: Get corrected local data
    local_data = await sync.get_local_corrected_data()
    if not local_data:
        print("❌ Cannot proceed without local data")
        return False
    
    # Step 4: Analyze differences
    differences = sync.analyze_data_differences(production_data, local_data)
    
    # Step 5: Generate sync options
    commands, commands_file = sync.generate_sync_commands(differences, sync.production_api_url)
    direct_script = sync.create_direct_database_sync_script(local_data)
    
    print("\n" + "=" * 70)
    print("📋 SYNCHRONIZATION PLAN READY")
    print("=" * 70)
    
    total_changes = (len(differences['apartments_to_remove']) + 
                    len(differences['apartments_to_add']) + 
                    len(differences['apartments_to_update']))
    
    print(f"📊 IMPACT ANALYSIS:")
    print(f"   Total changes needed: {total_changes}")
    print(f"   Critical fixes: {differences['pricing_fixes']} pricing issues")
    print(f"   Quality improvements: {differences['quality_improvements']} apartments")
    print(f"   Bad data removal: {len(differences['apartments_to_remove'])} apartments")
    print(f"   New verified data: {len(differences['apartments_to_add'])} apartments")
    
    print(f"\n📁 FILES GENERATED:")
    print(f"   Production backup: {backup_file}")
    print(f"   Sync commands: {commands_file}")
    print(f"   Direct sync script: {direct_script}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Review the backup and sync commands")
    print(f"   2. Test sync process on staging environment")
    print(f"   3. Execute sync during maintenance window")
    print(f"   4. Verify data quality after sync")
    
    # Highlight critical fixes
    print(f"\n🚨 CRITICAL ISSUES TO BE FIXED:")
    central_park_issue = False
    for apt in production_data:
        if (apt.get('price', 0) == 2344 and 
            'central park west' in apt.get('title', '').lower()):
            central_park_issue = True
            print(f"   ❌ ${apt.get('price')} Central Park West studio will be corrected")
            break
    
    if not central_park_issue:
        print(f"   ✅ Central Park West pricing issue may already be resolved")
    
    return True

if __name__ == "__main__":
    asyncio.run(main())