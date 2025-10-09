#!/usr/bin/env python3
"""
Create demo landlord account for presentations to management companies
"""

import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_db')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

async def create_demo_landlord():
    """Create demo landlord account for presentations"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🎭 Creating Demo Landlord Account for Management Company Presentations...")
    
    # Create demo landlord profile
    demo_landlord_id = "demo-landlord-2025"
    trial_end = datetime.utcnow() + timedelta(days=14)
    
    demo_landlord = {
        "id": demo_landlord_id,
        "email": "demo@nofeeplaces.com",
        "name": "Manhattan Properties LLC",
        "phone": "+1 (212) 555-0123",
        "company_name": "Manhattan Properties LLC",
        "license_number": "NYC-RE-2024-001",
        "property_count": 25,
        "subscription_plan": "portfolio",
        "subscription_status": "active",  # Active subscription for demo
        "trial_end_date": trial_end.isoformat(),
        "billing_start_date": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "is_verified": True
    }
    
    # Delete existing demo landlord if exists
    await db.landlords.delete_many({"id": demo_landlord_id})
    
    # Insert demo landlord
    await db.landlords.insert_one(demo_landlord)
    
    # Create some demo apartment listings for the landlord
    demo_apartments = [
        {
            "id": str(uuid.uuid4()),
            "landlord_id": demo_landlord_id,
            "title": "Luxury 2BR in Midtown Manhattan - No Fee",
            "description": "Premium apartment with city views, modern amenities, and doorman building. Perfect for professionals.",
            "address": "350 W 42nd Street, New York, NY 10036",
            "neighborhood": "Midtown",
            "borough": "Manhattan",
            "price": 4500,
            "bedrooms": 2,
            "bathrooms": 2,
            "square_feet": 1200,
            "available": True,
            "featured": True,
            "priority": 2,
            "verified": True,
            "images": [
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1618219908412-a29a1bb7b86e?w=800&h=600&fit=crop&auto=format"
            ],
            "amenities": ["Doorman", "Gym", "Roof Deck", "Laundry", "Elevator"],
            "contact_info": {
                "email": "demo@nofeeplaces.com",
                "phone": "+1 (212) 555-0123",
                "company": "Manhattan Properties LLC"
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "landlord_id": demo_landlord_id,
            "title": "Modern 1BR in Financial District - No Fee",
            "description": "Stunning one-bedroom with waterfront views and luxury finishes.",
            "address": "75 Wall Street, New York, NY 10005",
            "neighborhood": "Financial District",
            "borough": "Manhattan",
            "price": 3800,
            "bedrooms": 1,
            "bathrooms": 1,
            "square_feet": 900,
            "available": True,
            "featured": True,
            "priority": 2,
            "verified": True,
            "images": [
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop&auto=format"
            ],
            "amenities": ["Waterfront Views", "Concierge", "Gym", "Rooftop", "Pet Friendly"],
            "contact_info": {
                "email": "demo@nofeeplaces.com",
                "phone": "+1 (212) 555-0123",
                "company": "Manhattan Properties LLC"
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "landlord_id": demo_landlord_id,
            "title": "Studio in Chelsea - No Fee",
            "description": "Charming studio apartment in vibrant Chelsea neighborhood.",
            "address": "200 W 26th Street, New York, NY 10001",
            "neighborhood": "Chelsea",
            "borough": "Manhattan",
            "price": 2800,
            "bedrooms": 0,
            "bathrooms": 1,
            "square_feet": 550,
            "available": True,
            "featured": True,
            "priority": 2,
            "verified": True,
            "images": [
                "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop&auto=format"
            ],
            "amenities": ["Laundry", "Elevator", "Near Subway"],
            "contact_info": {
                "email": "demo@nofeeplaces.com",
                "phone": "+1 (212) 555-0123",
                "company": "Manhattan Properties LLC"
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    # Delete existing demo apartments
    await db.apartments.delete_many({"landlord_id": demo_landlord_id})
    
    # Insert demo apartments
    for apartment in demo_apartments:
        await db.apartments.insert_one(apartment)
    
    # Create some demo contact inquiries
    demo_contacts = [
        {
            "id": str(uuid.uuid4()),
            "landlord_id": demo_landlord_id,
            "apartment_id": demo_apartments[0]["id"],
            "name": "Sarah Johnson",
            "email": "sarah.johnson@example.com",
            "phone": "+1 (917) 555-0156",
            "message": "Hi, I'm very interested in the 2BR apartment on W 42nd Street. When can I schedule a viewing?",
            "preferred_contact": "email",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "landlord_id": demo_landlord_id,
            "apartment_id": demo_apartments[1]["id"],
            "name": "Michael Chen",
            "email": "m.chen@gmail.com",
            "phone": "+1 (646) 555-0178",
            "message": "Looking to move in next month. Is the Financial District apartment still available?",
            "preferred_contact": "phone",
            "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "landlord_id": demo_landlord_id,
            "apartment_id": demo_apartments[2]["id"],
            "name": "Emma Rodriguez",
            "email": "emma.r@company.com",
            "phone": "+1 (718) 555-0134",
            "message": "I work in Chelsea and this studio looks perfect. What's the application process?",
            "preferred_contact": "email",
            "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat()
        }
    ]
    
    # Delete existing demo contacts
    await db.contacts.delete_many({"landlord_id": demo_landlord_id})
    
    # Insert demo contacts
    for contact in demo_contacts:
        await db.contacts.insert_one(contact)
    
    print("✅ Demo landlord account created successfully!")
    print(f"📧 Email: {demo_landlord['email']}")
    print(f"🏢 Company: {demo_landlord['company_name']}")
    print(f"📋 Plan: {demo_landlord['subscription_plan']} (Portfolio - $99/month)")
    print(f"🆔 Landlord ID: {demo_landlord_id}")
    print(f"🏠 Demo apartments: {len(demo_apartments)}")
    print(f"📞 Demo inquiries: {len(demo_contacts)}")
    print(f"\n🎯 Dashboard URL:")
    print(f"   https://smartrental.preview.emergentagent.com/landlord/dashboard/{demo_landlord_id}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_demo_landlord())