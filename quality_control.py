#!/usr/bin/env python3
"""
Listing Quality Control & Verification Script
Identifies potentially illegitimate or low-quality listings
"""
import os
from pymongo import MongoClient
from datetime import datetime, timezone

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_database')
client = MongoClient(MONGO_URL)
db = client["nofeeplaces_database"]
apartments_collection = db['apartments']

def quality_check_listing(apt):
    """
    Check listing quality and return score + flags
    """
    flags = []
    score = 100
    
    # Image checks
    images = apt.get('images', [])
    if not images:
        flags.append("No images")
        score -= 30
    elif len(images) == 1:
        flags.append("Only 1 image")
        score -= 20
    
    # Interior photo check
    if images:
        interior_photos = [img for img in images if '/unit/' in img]
        if not interior_photos:
            flags.append("No interior unit photos")
            score -= 15
    
    # Address check
    if not apt.get('address') or apt.get('address') == '':
        flags.append("No address")
        score -= 20
    
    # Source verification
    if not apt.get('source_url'):
        flags.append("No source URL")
        score -= 15
    
    # Data source check
    verified_sources = ['Manhattan Skyline', 'Direct', 'Zillow']
    if apt.get('data_source') not in verified_sources:
        flags.append(f"Unverified source: {apt.get('data_source', 'Unknown')}")
        score -= 10
    
    # Description check
    desc = apt.get('description', '')
    if not desc or len(desc) < 50:
        flags.append("Minimal description")
        score -= 10
    
    # Amenities check
    if not apt.get('amenities') or len(apt.get('amenities', [])) == 0:
        flags.append("No amenities listed")
        score -= 10
    
    # Price reasonableness (very basic check)
    price = apt.get('price', 0)
    bedrooms = apt.get('bedrooms', 0)
    if price < 1500 and bedrooms > 0:
        flags.append("Price unusually low")
        score -= 15
    elif price > 20000:
        flags.append("Price unusually high")
        score -= 10
    
    return max(0, score), flags

def scan_all_listings(min_score=70, auto_flag=False):
    """
    Scan all available listings for quality issues
    """
    print("=" * 70)
    print("LISTING QUALITY CONTROL SCAN")
    print("=" * 70)
    
    listings = list(apartments_collection.find({"available": True}))
    
    print(f"\nScanning {len(listings)} available listings...")
    print(f"Minimum acceptable score: {min_score}")
    
    suspicious = []
    
    for apt in listings:
        score, flags = quality_check_listing(apt)
        
        if score < min_score or len(flags) >= 3:
            suspicious.append({
                'listing': apt,
                'score': score,
                'flags': flags
            })
    
    # Sort by score (worst first)
    suspicious.sort(key=lambda x: x['score'])
    
    print(f"\n{'='*70}")
    print(f"FOUND {len(suspicious)} SUSPICIOUS LISTINGS")
    print(f"{'='*70}")
    
    for i, item in enumerate(suspicious, 1):
        apt = item['listing']
        score = item['score']
        flags = item['flags']
        
        print(f"\n{i}. {apt.get('title', 'Untitled')} (Score: {score}/100)")
        print(f"   ID: {apt['id']}")
        print(f"   Price: ${apt.get('price', 0):,.0f}/mo")
        print(f"   {apt.get('bedrooms', 0)}BR in {apt.get('neighborhood', 'Unknown')}")
        print(f"   Source: {apt.get('data_source', 'Unknown')}")
        
        print(f"\n   🚩 Issues ({len(flags)}):")
        for flag in flags:
            print(f"      - {flag}")
        
        if score < 50:
            print(f"   ❌ RECOMMEND: Remove (score too low)")
        elif len(flags) >= 4:
            print(f"   ⚠️  RECOMMEND: Review (multiple issues)")
        else:
            print(f"   ⚠️  RECOMMEND: Improve data quality")
    
    if auto_flag and suspicious:
        print(f"\n{'='*70}")
        print("AUTO-FLAGGING LOW QUALITY LISTINGS")
        print(f"{'='*70}")
        
        flagged_count = 0
        for item in suspicious:
            if item['score'] < 50:
                apt = item['listing']
                apartments_collection.update_one(
                    {"id": apt['id']},
                    {
                        "$set": {
                            "available": False,
                            "quality_score": item['score'],
                            "deleted_reason": f"Auto-flagged: Quality score {item['score']}/100",
                            "flagged_date": datetime.now(timezone.utc).isoformat(),
                            "quality_flags": item['flags']
                        }
                    }
                )
                flagged_count += 1
                print(f"   ❌ Flagged: {apt.get('title', 'Untitled')}")
        
        print(f"\n✅ Flagged {flagged_count} listings")
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total scanned: {len(listings)}")
    print(f"Suspicious: {len(suspicious)}")
    print(f"Critical (score < 50): {sum(1 for x in suspicious if x['score'] < 50)}")
    print(f"Warning (score < 70): {sum(1 for x in suspicious if 50 <= x['score'] < 70)}")
    
    client.close()
    return suspicious

if __name__ == "__main__":
    import sys
    
    min_score = int(sys.argv[1]) if len(sys.argv) > 1 else 70
    auto_flag = sys.argv[2].lower() == 'true' if len(sys.argv) > 2 else False
    
    scan_all_listings(min_score=min_score, auto_flag=auto_flag)
