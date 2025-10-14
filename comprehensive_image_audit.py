#!/usr/bin/env python3
"""
Comprehensive apartment image audit across all databases
"""

import pymongo
from pymongo import MongoClient
import os

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')

client = MongoClient(MONGO_URL)

def audit_database(db_name):
    """Audit a single database"""
    db = client[db_name]
    apartments = list(db.apartments.find({}))
    
    if not apartments:
        return None
    
    image_sources = {}
    for apt in apartments:
        images = apt.get('images', [])
        if images:
            from urllib.parse import urlparse
            source = urlparse(images[0]).netloc
            if source not in image_sources:
                image_sources[source] = []
            image_sources[source].append(apt.get('title', 'Unknown'))
    
    return {
        'count': len(apartments),
        'image_sources': image_sources
    }

if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE APARTMENT DATABASE AUDIT")
    print("=" * 80)
    
    databases = ['nofeeplaces', 'nofeeplaces_database', 'nofeeplaces_db']
    
    for db_name in databases:
        print(f"\n📊 Database: {db_name}")
        print("-" * 80)
        
        result = audit_database(db_name)
        
        if result is None:
            print(f"   No apartments found")
            continue
        
        print(f"   Total apartments: {result['count']}")
        print(f"\n   Image sources:")
        
        for source, titles in result['image_sources'].items():
            print(f"      • {source}: {len(titles)} apartments")
            
            # Categorize image source
            if 'unsplash.com' in source:
                print(f"        ⚠️  Type: STOCK PHOTOS (not unit-specific)")
            elif 'pexels.com' in source:
                print(f"        ⚠️  Type: STOCK PHOTOS (not unit-specific)")
            elif 'zillowstatic.com' in source:
                print(f"        ⚠️  Type: LISTING PHOTOS (may not match specific units in your database)")
            elif 'nestiostatic.com' in source:
                print(f"        ❌ Type: BROKEN - Returns 403 Forbidden")
            elif 'luxuryrentalsmanhattan.com' in source:
                print(f"        ❌ Type: BROKEN - Returns 404 Not Found")
            elif 'apartments.com' in source:
                print(f"        ❌ Type: INACCESSIBLE")
            else:
                print(f"        ❓ Type: UNKNOWN")
    
    # Check which database backend is using
    print(f"\n" + "=" * 80)
    print(f"BACKEND CONFIGURATION")
    print(f"=" * 80)
    
    db_name_env = os.environ.get('DB_NAME', 'NOT SET')
    print(f"   Backend is using database: {db_name_env}")
    
    result = audit_database(db_name_env)
    if result:
        print(f"\n   ⚠️  CRITICAL FINDING:")
        has_stock = any('unsplash' in src or 'pexels' in src for src in result['image_sources'].keys())
        has_broken = any('nestio' in src or 'luxury' in src or 'apartments.com' in src for src in result['image_sources'].keys())
        
        if has_stock:
            print(f"   ❌ Backend is using STOCK PHOTOS (Unsplash/Pexels)")
            print(f"   These are NOT unit-specific images as requested")
        if has_broken:
            print(f"   ❌ Backend has BROKEN image URLs that return 403/404 errors")
    
    client.close()
