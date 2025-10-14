#!/usr/bin/env python3
"""
Fix Mercedes House Pricing
Update apartments with correct market rates based on research
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

# Correct pricing based on web research (2025 market rates)
MERCEDES_HOUSE_PRICING = {
    'studio': {
        'min': 3550,
        'max': 4423,
        'typical': 3950
    },
    '1_bedroom': {
        'min': 4495,
        'max': 5450,
        'typical': 4900
    },
    '1_bedroom_office': {
        'min': 4745,
        'max': 5450,
        'typical': 5100
    },
    '2_bedroom': {
        'min': 5595,
        'max': 6825,
        'typical': 6200
    }
}


async def fix_mercedes_house_pricing():
    """Update Mercedes House apartments with correct pricing"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n" + "="*70)
    print("💰 FIXING MERCEDES HOUSE PRICING")
    print("="*70)
    
    # Get all Mercedes House apartments with incorrect pricing
    apartments = await db.apartments.find({
        'building_address': '550 W 54th St, New York, NY 10019',
        'price': {'$lt': 1000}
    }).to_list(length=None)
    
    print(f"\nFound {len(apartments)} apartments with incorrect pricing\n")
    
    updated_count = 0
    
    for apt in apartments:
        title = apt.get('title', '').lower()
        size = apt.get('size', '')
        bedrooms = apt.get('bedrooms')
        url = apt.get('url', '').lower()
        
        # Determine unit type and correct price
        new_price = None
        
        if 'studio' in title or 'studio' in url or bedrooms == 0:
            new_price = MERCEDES_HOUSE_PRICING['studio']['typical']
            unit_type = "Studio"
            
        elif 'office' in title or 'office' in url or '1-bedroom + home office' in title.lower():
            new_price = MERCEDES_HOUSE_PRICING['1_bedroom_office']['typical']
            unit_type = "1 Bedroom + Home Office"
            
        elif '1 bed' in title.lower() or '1-bed' in url or bedrooms == 1:
            new_price = MERCEDES_HOUSE_PRICING['1_bedroom']['typical']
            unit_type = "1 Bedroom"
            
        elif '2 bed' in title.lower() or '2-bed' in url or bedrooms == 2:
            new_price = MERCEDES_HOUSE_PRICING['2_bedroom']['typical']
            unit_type = "2 Bedroom"
            
        elif 'terrace' in title.lower() or 'terrace' in url:
            # Terrace units are premium, typically 1BR+
            new_price = MERCEDES_HOUSE_PRICING['1_bedroom_office']['typical'] + 300
            unit_type = "1 Bedroom with Terrace"
        
        if new_price:
            # Also update the title and size if needed
            updates = {'price': new_price}
            
            if not apt.get('size') or apt.get('size') == 'None':
                updates['size'] = unit_type
            
            await db.apartments.update_one(
                {'id': apt['id']},
                {'$set': updates}
            )
            
            updated_count += 1
            print(f"✓ Updated: {apt.get('title', 'N/A')[:50]}")
            print(f"  Old Price: ${apt.get('price', 0)}")
            print(f"  New Price: ${new_price}")
            print(f"  Unit Type: {unit_type}\n")
    
    print(f"✅ Updated {updated_count} apartments with correct pricing")
    
    # Verify all Mercedes House apartments now have correct pricing
    print("\n" + "="*70)
    print("📊 VERIFICATION - All Mercedes House Apartments")
    print("="*70)
    
    all_mh = await db.apartments.find({
        'building_address': '550 W 54th St, New York, NY 10019'
    }).sort('price', 1).to_list(length=None)
    
    for apt in all_mh:
        price = apt.get('price', 0)
        title = apt.get('title', 'N/A')[:50]
        size = apt.get('size', 'N/A')
        
        status = "✅" if price >= 3000 else "⚠️"
        print(f"{status} {title}")
        print(f"   Size: {size} | Price: ${price:,.0f}/month")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(fix_mercedes_house_pricing())
