#!/usr/bin/env python3
"""
Review and Remove Listings - Interactive Approval System
Review suspicious listings and mark them for removal
"""
import json
import os
from pymongo import MongoClient

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_database')

def review_and_remove():
    """
    Interactive review process
    """
    # Load review data
    with open('/app/listings_to_review.json', 'r') as f:
        review_data = json.load(f)
    
    print("=" * 80)
    print("INTERACTIVE LISTING REVIEW & REMOVAL")
    print("=" * 80)
    
    print("\nReview Options:")
    print("1. Remove all MNS Real Estate listings (62 listings)")
    print("2. Remove all listings with score < 30")
    print("3. Remove all listings with score < 50")
    print("4. Review and approve individual listings")
    print("5. Exit without changes")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    client = MongoClient(MONGO_URL)
    db = client["nofeeplaces_database"]
    apartments_collection = db['apartments']
    
    if choice == '1':
        # Remove all MNS Real Estate
        print("\n⚠️  This will remove ALL MNS Real Estate listings (62 listings)")
        confirm = input("Type 'REMOVE' to confirm: ").strip()
        
        if confirm == 'REMOVE':
            result = apartments_collection.update_many(
                {"data_source": "MNS Real Estate", "available": True},
                {"$set": {
                    "available": False,
                    "deleted_reason": "Unverified source - failed quality checks",
                    "flagged_date": "2025-01-30"
                }}
            )
            print(f"\n✅ Removed {result.modified_count} MNS Real Estate listings")
            
            # New total
            new_total = apartments_collection.count_documents({"available": True})
            print(f"📊 New total available: {new_total}")
    
    elif choice == '2':
        # Remove score < 30
        ids_to_remove = []
        for source, items in review_data.items():
            for item in items:
                if item['score'] < 30:
                    ids_to_remove.append(item['id'])
        
        print(f"\n⚠️  This will remove {len(ids_to_remove)} listings with score < 30")
        confirm = input("Type 'REMOVE' to confirm: ").strip()
        
        if confirm == 'REMOVE':
            result = apartments_collection.update_many(
                {"id": {"$in": ids_to_remove}, "available": True},
                {"$set": {
                    "available": False,
                    "deleted_reason": "Quality score below 30 - critical issues",
                    "flagged_date": "2025-01-30"
                }}
            )
            print(f"\n✅ Removed {result.modified_count} listings")
            
            new_total = apartments_collection.count_documents({"available": True})
            print(f"📊 New total available: {new_total}")
    
    elif choice == '3':
        # Remove score < 50
        ids_to_remove = []
        for source, items in review_data.items():
            for item in items:
                if item['score'] < 50:
                    ids_to_remove.append(item['id'])
        
        print(f"\n⚠️  This will remove {len(ids_to_remove)} listings with score < 50")
        confirm = input("Type 'REMOVE' to confirm: ").strip()
        
        if confirm == 'REMOVE':
            result = apartments_collection.update_many(
                {"id": {"$in": ids_to_remove}, "available": True},
                {"$set": {
                    "available": False,
                    "deleted_reason": "Quality score below 50 - multiple issues",
                    "flagged_date": "2025-01-30"
                }}
            )
            print(f"\n✅ Removed {result.modified_count} listings")
            
            new_total = apartments_collection.count_documents({"available": True})
            print(f"📊 New total available: {new_total}")
    
    elif choice == '4':
        # Individual review
        print("\n📋 Individual Review Mode")
        print("For each listing, enter: k (keep), r (remove), q (quit)")
        
        to_remove = []
        
        for source, items in review_data.items():
            print(f"\n{'='*80}")
            print(f"SOURCE: {source}")
            print(f"{'='*80}")
            
            for item in items[:20]:  # Review first 20 per source
                print(f"\n{item['title']}")
                print(f"  Price: ${item['price']}/mo | {item['bedrooms']}BR in {item['neighborhood']}")
                print(f"  Score: {item['score']}/100")
                print(f"  Issues: {', '.join(item['flags'])}")
                
                decision = input("  Decision (k/r/q): ").strip().lower()
                
                if decision == 'r':
                    to_remove.append(item['id'])
                    print("  ❌ Marked for removal")
                elif decision == 'k':
                    print("  ✅ Keeping")
                elif decision == 'q':
                    break
            
            if decision == 'q':
                break
        
        if to_remove:
            print(f"\n⚠️  Removing {len(to_remove)} listings...")
            result = apartments_collection.update_many(
                {"id": {"$in": to_remove}, "available": True},
                {"$set": {
                    "available": False,
                    "deleted_reason": "Manual review - removed by admin",
                    "flagged_date": "2025-01-30"
                }}
            )
            print(f"✅ Removed {result.modified_count} listings")
            
            new_total = apartments_collection.count_documents({"available": True})
            print(f"📊 New total available: {new_total}")
    
    else:
        print("\nNo changes made.")
    
    client.close()

if __name__ == "__main__":
    review_and_remove()
