#!/usr/bin/env python3
import os
from pymongo import MongoClient

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'nofeeplaces')
client = MongoClient(mongo_url)
db = client[db_name]

# Check studio apartments
studios = list(db.apartments.find({'title': {'$regex': 'STUDIO', '$options': 'i'}}).limit(5))

print(f"Found {len(studios)} studio apartments:")
for studio in studios:
    print(f'Title: {studio.get("title")}')
    print(f'Bedrooms: {studio.get("bedrooms")} (type: {type(studio.get("bedrooms"))})')
    print(f'Has bedrooms field: {"bedrooms" in studio}')
    print('---')

client.close()