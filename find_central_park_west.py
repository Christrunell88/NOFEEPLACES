#!/usr/bin/env python3
import os
from pymongo import MongoClient

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'nofeeplaces')
client = MongoClient(mongo_url)
db = client[db_name]

print("=== SEARCHING FOR CENTRAL PARK WEST APARTMENT ===")

# Search for Central Park West apartments
cpw_apartments = list(db.apartments.find({
    '$or': [
        {'title': {'$regex': 'Central Park West', '$options': 'i'}},
        {'address': {'$regex': 'Central Park West', '$options': 'i'}},
        {'location': {'$regex': 'Central Park West', '$options': 'i'}}
    ]
}))

print(f"Found {len(cpw_apartments)} Central Park West apartments")

for apt in cpw_apartments:
    print(f"- {apt['title']} - ${apt['price']} ({apt.get('neighborhood', 'Unknown')})")

if not cpw_apartments:
    print("\nNo Central Park West apartments found. Checking for low-priced apartments...")
    
    # Look for apartments under $2500 (suspiciously low for NYC)
    low_price = list(db.apartments.find({'price': {'$lt': 2500}}).sort('price', 1))
    print(f"\nFound {len(low_price)} apartments under $2,500:")
    
    for apt in low_price:
        print(f"- {apt['title']} - ${apt['price']} ({apt.get('neighborhood', 'Unknown')})")
        if len(apt.get('images', [])) > 0:
            print(f"  First image: {apt['images'][0]}")

    # Also check apartments with title containing "Modern Studio"
    modern_studios = list(db.apartments.find({'title': {'$regex': 'Modern Studio', '$options': 'i'}}))
    print(f"\nFound {len(modern_studios)} 'Modern Studio' apartments:")
    
    for apt in modern_studios:
        print(f"- {apt['title']} - ${apt['price']} ({apt.get('neighborhood', 'Unknown')})")

client.close()