#!/usr/bin/env python3
"""
Check for real users in NoFeePlaces.com database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv('/app/backend/.env')

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_db')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

async def check_real_users():
    """Check for real users in the database"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("👥 Checking for real users in NoFeePlaces.com database...")
    print("=" * 60)
    
    # Check all collections for user-related data
    collections = await db.list_collection_names()
    print(f"📋 Available collections: {', '.join(collections)}")
    print()
    
    # Check for users collection
    if 'users' in collections:
        users = await db.users.find().to_list(length=None)
        print(f"👤 Users collection: {len(users)} total users")
        
        if users:
            print("\n📊 User Details:")
            for i, user in enumerate(users, 1):
                print(f"\n{i}. User ID: {user.get('id', user.get('_id', 'N/A'))}")
                print(f"   Email: {user.get('email', 'N/A')}")
                print(f"   Name: {user.get('name', user.get('full_name', 'N/A'))}")
                print(f"   Auth Method: {user.get('auth_provider', user.get('provider', 'N/A'))}")
                print(f"   Created: {user.get('created_at', user.get('createdAt', 'N/A'))}")
                print(f"   Last Login: {user.get('last_login', user.get('lastLogin', 'N/A'))}")
                print(f"   Verified: {user.get('verified', user.get('email_verified', False))}")
        else:
            print("   No users found in users collection")
    else:
        print("❌ No 'users' collection found")
    
    print("\n" + "=" * 60)
    
    # Check for contacts/leads
    if 'contacts' in collections:
        contacts = await db.contacts.find().to_list(length=None)
        print(f"📞 Contact requests: {len(contacts)} total inquiries")
        
        if contacts:
            print("\n📊 Recent Contact Requests:")
            recent_contacts = sorted(contacts, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
            
            for i, contact in enumerate(recent_contacts, 1):
                print(f"\n{i}. Name: {contact.get('name', 'N/A')}")
                print(f"   Email: {contact.get('email', 'N/A')}")
                print(f"   Phone: {contact.get('phone', 'N/A')}")
                print(f"   Date: {contact.get('created_at', 'N/A')}")
                print(f"   Apartment ID: {contact.get('apartment_id', 'N/A')}")
                if contact.get('message'):
                    message = contact['message'][:100] + "..." if len(contact['message']) > 100 else contact['message']
                    print(f"   Message: {message}")
        else:
            print("   No contact requests found")
    else:
        print("❌ No 'contacts' collection found")
    
    print("\n" + "=" * 60)
    
    # Check for newsletter subscriptions
    if 'newsletter_subscribers' in collections:
        subscribers = await db.newsletter_subscribers.find().to_list(length=None)
        print(f"📧 Newsletter subscribers: {len(subscribers)} total")
        
        if subscribers:
            print("\n📊 Recent Newsletter Subscribers:")
            recent_subs = sorted(subscribers, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
            
            for i, sub in enumerate(recent_subs, 1):
                print(f"\n{i}. Email: {sub.get('email', 'N/A')}")
                print(f"   Name: {sub.get('name', 'N/A')}")
                print(f"   Source: {sub.get('source', 'N/A')}")
                print(f"   Subscribed: {sub.get('created_at', 'N/A')}")
                print(f"   Status: {sub.get('status', 'N/A')}")
        else:
            print("   No newsletter subscribers found")
    else:
        print("❌ No 'newsletter_subscribers' collection found")
    
    print("\n" + "=" * 60)
    
    # Check for any other user activity collections
    activity_collections = ['favorites', 'saved_searches', 'user_sessions', 'analytics_events']
    
    for collection_name in activity_collections:
        if collection_name in collections:
            count = await db[collection_name].count_documents({})
            print(f"📊 {collection_name}: {count} records")
            
            if count > 0 and count <= 5:
                # Show sample data for small collections
                samples = await db[collection_name].find().limit(3).to_list(length=3)
                print(f"   Sample data: {len(samples)} records")
                for sample in samples:
                    print(f"   - {sample}")
        else:
            print(f"❌ No '{collection_name}' collection found")
    
    print("\n" + "=" * 60)
    
    # Summary
    total_users = len(users) if 'users' in collections else 0
    total_contacts = len(contacts) if 'contacts' in collections else 0
    total_subscribers = len(subscribers) if 'newsletter_subscribers' in collections else 0
    
    print(f"\n📈 SUMMARY - Real User Activity:")
    print(f"   👤 Registered Users: {total_users}")
    print(f"   📞 Contact Inquiries: {total_contacts}")  
    print(f"   📧 Newsletter Subscribers: {total_subscribers}")
    print(f"   🎯 Total User Interactions: {total_users + total_contacts + total_subscribers}")
    
    if total_users + total_contacts + total_subscribers > 0:
        print("\n✅ YES - NoFeePlaces.com has real user activity!")
    else:
        print("\n❌ NO - No real users found in the database")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_real_users())