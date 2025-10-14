#!/usr/bin/env python3
"""
Script to add affordable no-fee apartments to NoFeePlaces.com
Focuses on $1400-$2200 range for budget-conscious renters
"""

import asyncio
import requests
import json
from datetime import datetime, timezone

# Backend URL
BACKEND_URL = "https://fee-free-homes.preview.emergentagent.com"

async def add_affordable_apartments():
    """Add affordable apartments across NYC neighborhoods"""
    
    affordable_neighborhoods = [
        # Brooklyn - Most Affordable Areas
        {"location": "East New York", "price_range": (1400, 1800)},
        {"location": "Brownsville", "price_range": (1450, 1750)},
        {"location": "Canarsie", "price_range": (1500, 1900)},
        {"location": "East Flatbush", "price_range": (1550, 1950)},
        {"location": "Crown Heights", "price_range": (1600, 2000)},
        {"location": "Bed-Stuy", "price_range": (1650, 2100)},
        {"location": "Bushwick", "price_range": (1700, 2200)},
        
        # Bronx - Affordable Options
        {"location": "University Heights", "price_range": (1400, 1700)},
        {"location": "Morris Heights", "price_range": (1450, 1750)},
        {"location": "Concourse", "price_range": (1500, 1800)},
        {"location": "Fordham", "price_range": (1600, 1900)},
        
        # Queens - Outer Areas
        {"location": "Jamaica", "price_range": (1500, 1800)},
        {"location": "South Ozone Park", "price_range": (1450, 1750)},
        {"location": "Far Rockaway", "price_range": (1400, 1700)},
        {"location": "Ridgewood", "price_range": (1700, 2000)},
    ]
    
    print("🏠 Adding affordable no-fee apartments to NoFeePlaces.com")
    
    total_added = 0
    
    for neighborhood in affordable_neighborhoods:
        location = neighborhood["location"]
        min_price, max_price = neighborhood["price_range"]
        
        print(f"\n📍 Adding apartments in {location} (${min_price}-${max_price})")
        
        try:
            # Import scraped rentals for this neighborhood
            response = requests.post(
                f"{BACKEND_URL}/api/import-scraped-rentals",
                params={
                    "location": location,
                    "limit": 8  # Add 8 apartments per neighborhood
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    inserted_count = data.get("inserted_count", 0)
                    total_added += inserted_count
                    print(f"✅ Added {inserted_count} apartments in {location}")
                else:
                    print(f"❌ Error adding apartments in {location}: {data.get('message', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error {response.status_code} for {location}")
                
        except Exception as e:
            print(f"❌ Exception adding apartments in {location}: {str(e)}")
        
        # Small delay between requests
        await asyncio.sleep(1)
    
    print(f"\n🎉 TOTAL APARTMENTS ADDED: {total_added}")
    
    # Get updated apartment count and price range
    try:
        stats_response = requests.get(f"{BACKEND_URL}/api/apartments?limit=1")
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            total_apartments = stats_data.get("total", 0)
            print(f"📊 Total apartments now available: {total_apartments}")
    except:
        print("📊 Could not retrieve updated apartment count")
    
    return total_added

if __name__ == "__main__":
    added_count = asyncio.run(add_affordable_apartments())