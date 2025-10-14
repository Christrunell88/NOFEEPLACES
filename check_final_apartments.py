#!/usr/bin/env python3
"""
Check final apartment database state
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def final_check():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    db = client[os.environ.get('DB_NAME', 'nofeeplaces')]
    
    # Get total count
    count = await db.apartments.count_documents({})
    print(f'Total apartments in database: {count}')
    
    # Check by management company
    nestio_count = await db.apartments.count_documents({'data_source': 'Nestio Verified Real Photos'})
    manhattan_skyline_count = await db.apartments.count_documents({'data_source': 'Manhattan Skyline Management - Verified'})
    
    print(f'Nestio verified apartments: {nestio_count}')
    print(f'Manhattan Skyline apartments: {manhattan_skyline_count}')
    
    # Check building distribution
    buildings = await db.apartments.aggregate([
        {'$group': {'_id': '$building_name', 'count': {'$sum': 1}}}
    ]).to_list(None)
    
    print(f'\nBuildings by count:')
    for building in buildings:
        building_name = building['_id']
        apartment_count = building['count']
        print(f'- {building_name}: {apartment_count} apartments')
    
    # Check price ranges
    price_stats = await db.apartments.aggregate([
        {'$group': {
            '_id': None,
            'min_price': {'$min': '$price'},
            'max_price': {'$max': '$price'},
            'avg_price': {'$avg': '$price'}
        }}
    ]).to_list(1)
    
    if price_stats:
        stats = price_stats[0]
        min_price = stats['min_price']
        max_price = stats['max_price'] 
        avg_price = stats['avg_price']
        print(f'\nPrice Statistics:')
        print(f'- Min price: ${min_price}')
        print(f'- Max price: ${max_price}')
        print(f'- Average price: ${avg_price:.0f}')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(final_check())