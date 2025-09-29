#!/usr/bin/env python3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_db')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

async def check_bedstuy():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    apartments = await db.apartments.find({'neighborhood': 'Bedford-Stuyvesant'}).to_list(length=None)
    print(f'Total Bed-Stuy apartments in DB: {len(apartments)}')
    for apt in apartments:
        print(f'- {apt["title"]} - ${apt["price"]}')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_bedstuy())