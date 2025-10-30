#!/usr/bin/env python3
"""
Deduplication Script for NoFeePlaces Apartments
Removes duplicate/similar listings in the same building with same bedroom count
"""
import os
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_database')
client = MongoClient(MONGO_URL)
db = client["nofeeplaces_database"]
apartments_collection = db['apartments']

def deduplicate_apartments(strategy='keep_cheapest', dry_run=True):
    """
    Deduplicate apartments based on strategy
    
    Strategies:
    - keep_cheapest: Keep the cheapest unit from each building/bedroom group
    - keep_newest: Keep the most recently added unit
    - keep_range: Keep min and max price to show range
    """
    
    print("=" * 70)
    print(f"DEDUPLICATION SCRIPT - Strategy: {strategy}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will delete)'}")
    print("=" * 70)
    
    # Find groups of similar listings
    pipeline = [
        {"$match": {"available": True}},
        {"$group": {
            "_id": {
                "address": "$address",
                "bedrooms": "$bedrooms",
                "neighborhood": "$neighborhood"
            },
            "count": {"$sum": 1},
            "listings": {"$push": {
                "id": "$id",
                "title": "$title",
                "price": "$price",
                "created_at": "$created_at",
                "building_name": "$building_name"
            }}
        }},
        {"$match": {"count": {"$gt": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    duplicate_groups = list(apartments_collection.aggregate(pipeline))
    
    to_delete = []
    to_keep = []
    
    for group in duplicate_groups:
        address = group['_id']['address']
        bedrooms = group['_id']['bedrooms']
        neighborhood = group['_id']['neighborhood']
        listings = group['listings']
        
        # Exclude our Manhattan Skyline listings (they have unique unit numbers)
        manhattan_skyline_units = [l for l in listings if l.get('building_name') in ['Chelsea Place®', 'Saranac®', '55 Thompson', 'CD 280®']]
        if len(manhattan_skyline_units) == len(listings):
            # All are Manhattan Skyline with unique units, skip
            continue
        
        # Sort for strategy
        if strategy == 'keep_cheapest':
            listings_sorted = sorted(listings, key=lambda x: x['price'])
            keep = listings_sorted[0]
            delete = listings_sorted[1:]
        
        elif strategy == 'keep_newest':
            listings_sorted = sorted(listings, key=lambda x: x.get('created_at', ''), reverse=True)
            keep = listings_sorted[0]
            delete = listings_sorted[1:]
        
        elif strategy == 'keep_range':
            listings_sorted = sorted(listings, key=lambda x: x['price'])
            # Keep cheapest and most expensive
            keep_list = [listings_sorted[0], listings_sorted[-1]]
            delete = [l for l in listings if l not in keep_list]
            keep = keep_list[0]  # For logging
        
        else:
            continue
        
        to_keep.append(keep)
        to_delete.extend(delete)
        
        bed_label = f"{bedrooms}BR" if bedrooms > 0 else "Studio"
        print(f"\n{neighborhood or 'Unknown'} - {bed_label} ({address or 'No address'})")
        print(f"  Total: {len(listings)} listings")
        print(f"  ✅ KEEP: {keep['title']} - ${keep['price']:,.0f}/mo")
        for d in delete:
            print(f"  ❌ DELETE: {d['title']} - ${d['price']:,.0f}/mo")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Duplicate groups found: {len(duplicate_groups)}")
    print(f"Listings to keep: {len(to_keep)}")
    print(f"Listings to delete: {len(to_delete)}")
    print(f"New total after cleanup: {264 - len(to_delete)}")
    
    if not dry_run and to_delete:
        print("\n⚠️  PERFORMING DELETION...")
        ids_to_delete = [l['id'] for l in to_delete]
        result = apartments_collection.update_many(
            {"id": {"$in": ids_to_delete}},
            {"$set": {"available": False, "deleted_reason": "Duplicate/Similar listing removed"}}
        )
        print(f"✅ Marked {result.modified_count} listings as unavailable")
    
    elif dry_run:
        print("\n💡 This was a DRY RUN. No changes made.")
        print("   Run with dry_run=False to apply changes.")
    
    client.close()
    return to_delete

if __name__ == "__main__":
    import sys
    
    strategy = sys.argv[1] if len(sys.argv) > 1 else 'keep_cheapest'
    dry_run = sys.argv[2].lower() != 'false' if len(sys.argv) > 2 else True
    
    valid_strategies = ['keep_cheapest', 'keep_newest', 'keep_range']
    if strategy not in valid_strategies:
        print(f"Invalid strategy. Choose from: {', '.join(valid_strategies)}")
        sys.exit(1)
    
    deduplicate_apartments(strategy=strategy, dry_run=dry_run)
