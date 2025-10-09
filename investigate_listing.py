#!/usr/bin/env python3
"""
Investigate the Central Park West listing data quality issue
"""
import os
from pymongo import MongoClient

def investigate_central_park_west():
    # Get MongoDB URL
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    db = client['rental_platform']
    
    print("=== INVESTIGATING CENTRAL PARK WEST LISTINGS ===")
    
    # Find apartments with Central Park West in title or address
    apartments = list(db.apartments.find({
        '$or': [
            {'title': {'$regex': 'Central Park West', '$options': 'i'}},
            {'address': {'$regex': 'Central Park West', '$options': 'i'}},
            {'location': {'$regex': 'Central Park West', '$options': 'i'}}
        ]
    }).limit(10))
    
    if not apartments:
        print("No Central Park West apartments found. Searching for similar...")
        
        # First check total apartment count
        total_count = db.apartments.count_documents({})
        print(f"Total apartments in database: {total_count}")
        
        # Get some sample apartments
        apartments = list(db.apartments.find({}).sort('price', 1).limit(10))
        
        if not apartments:
            print("No apartments found at all!")
            return
    
    print(f"Found {len(apartments)} apartments")
    
    for i, apt in enumerate(apartments, 1):
        print(f"\n--- APARTMENT {i} ---")
        print(f"ID: {apt.get('id', apt.get('_id'))}")
        print(f"Title: {apt.get('title')}")
        print(f"Price: ${apt.get('price')}")
        print(f"Location: {apt.get('location')}")
        print(f"Address: {apt.get('address')}")
        print(f"Neighborhood: {apt.get('neighborhood')}")
        print(f"Borough: {apt.get('borough')}")
        print(f"Bedrooms: {apt.get('bedrooms')}")
        print(f"Bathrooms: {apt.get('bathrooms')}")
        print(f"Square Feet: {apt.get('sqft')}")
        print(f"Data Source: {apt.get('data_source')}")
        print(f"Images Count: {len(apt.get('images', []))}")
        
        if apt.get('images'):
            print(f"Image URLs:")
            for j, img in enumerate(apt['images'][:3], 1):  # Show first 3 images
                print(f"  {j}. {img}")
            if len(apt['images']) > 3:
                print(f"  ... and {len(apt['images']) - 3} more")
        
        # Check if price makes sense for location
        price = apt.get('price', 0)
        neighborhood = apt.get('neighborhood', '').lower()
        
        if 'central park west' in apt.get('title', '').lower() or 'central park west' in apt.get('address', '').lower():
            if price < 4000:
                print(f"🚨 PRICE ALERT: ${price} seems too low for Central Park West!")
        
        if 'upper west side' in neighborhood and price < 3000:
            print(f"⚠️  PRICE WARNING: ${price} might be low for Upper West Side")
    
    # Check overall price distribution
    print("\n=== PRICE DISTRIBUTION ANALYSIS ===")
    
    # Manhattan studios
    manhattan_studios = list(db.apartments.find({
        'borough': 'Manhattan',
        'bedrooms': 0
    }).sort('price', 1))
    
    if manhattan_studios:
        prices = [apt['price'] for apt in manhattan_studios]
        print(f"Manhattan Studios: {len(manhattan_studios)} total")
        print(f"Price Range: ${min(prices)} - ${max(prices)}")
        print(f"Average: ${sum(prices)/len(prices):.0f}")
        
        # Show cheapest and most expensive
        print(f"\nCheapest: {manhattan_studios[0]['title']} - ${manhattan_studios[0]['price']}")
        print(f"Most Expensive: {manhattan_studios[-1]['title']} - ${manhattan_studios[-1]['price']}")
    
    client.close()

if __name__ == "__main__":
    investigate_central_park_west()