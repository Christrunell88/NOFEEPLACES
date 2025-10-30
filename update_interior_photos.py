#!/usr/bin/env python3
"""
Script to automatically update apartment listings with interior unit photos only.
Crawls source URLs, extracts interior photos (/unit/ paths), and updates MongoDB.
"""
import os
import sys
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import time

# MongoDB connection
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_database')
client = MongoClient(MONGO_URL)
db = client["nofeeplaces_database"]
apartments_collection = db['apartments']

def extract_interior_photos(source_url):
    """
    Crawl the source URL and extract only interior unit photos.
    Returns list of image URLs containing /unit/ in path.
    """
    try:
        print(f"   Crawling: {source_url}")
        response = requests.get(source_url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all images
        all_images = soup.find_all('img')
        
        # Extract URLs and filter for interior unit photos
        interior_photos = []
        for img in all_images:
            src = img.get('src', '')
            if '/unit/' in src and 'manhattanskyline.com' in src:
                # Use multi-hero style for consistency
                if '_styles/multi-hero/unit/' in src:
                    interior_photos.append(src)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_photos = []
        for photo in interior_photos:
            if photo not in seen:
                seen.add(photo)
                unique_photos.append(photo)
        
        print(f"   ✅ Found {len(unique_photos)} interior unit photos")
        return unique_photos
        
    except Exception as e:
        print(f"   ❌ Error crawling URL: {str(e)}")
        return None

def update_apartment_photos(apartment_id, unit_number, interior_photos):
    """
    Update apartment in MongoDB with interior photos only.
    """
    try:
        result = apartments_collection.update_one(
            {"id": apartment_id},
            {"$set": {"images": interior_photos}}
        )
        
        if result.modified_count > 0:
            print(f"   ✅ Updated unit {unit_number} with {len(interior_photos)} interior photos")
            return True
        else:
            print(f"   ⚠️  No changes needed for unit {unit_number}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error updating database: {str(e)}")
        return False

def main():
    """
    Main function to process all Manhattan Skyline listings.
    """
    print("=" * 70)
    print("🏢 INTERIOR PHOTOS UPDATE SCRIPT")
    print("=" * 70)
    print("\nSearching for Manhattan Skyline listings...\n")
    
    # Find all Manhattan Skyline listings with source URLs
    query = {
        "data_source": "Manhattan Skyline",
        "source_url": {"$exists": True, "$ne": ""}
    }
    
    listings = list(apartments_collection.find(query))
    
    if not listings:
        print("❌ No Manhattan Skyline listings found with source URLs")
        return
    
    print(f"📊 Found {len(listings)} Manhattan Skyline listings to process\n")
    print("=" * 70)
    
    # Statistics
    processed = 0
    updated = 0
    failed = 0
    skipped = 0
    
    for i, apartment in enumerate(listings, 1):
        print(f"\n[{i}/{len(listings)}] Processing: {apartment.get('title', 'Unknown')}")
        print(f"   Unit: {apartment.get('unit_number', 'N/A')}")
        print(f"   Current images: {len(apartment.get('images', []))}")
        
        source_url = apartment.get('source_url')
        
        # Check if already has interior photos only
        current_images = apartment.get('images', [])
        if current_images and all('/unit/' in img for img in current_images):
            print(f"   ⏭️  Already has interior photos only - skipping")
            skipped += 1
            processed += 1
            continue
        
        # Extract interior photos from source
        interior_photos = extract_interior_photos(source_url)
        
        if interior_photos is None:
            print(f"   ❌ Failed to crawl source URL")
            failed += 1
            processed += 1
            continue
        
        if not interior_photos:
            print(f"   ⚠️  No interior photos found - keeping original images")
            skipped += 1
            processed += 1
            continue
        
        # Update database
        success = update_apartment_photos(
            apartment['id'],
            apartment.get('unit_number', 'N/A'),
            interior_photos
        )
        
        if success:
            updated += 1
        
        processed += 1
        
        # Rate limiting - be nice to the server
        time.sleep(1)
    
    # Final summary
    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    print(f"Total listings processed: {processed}")
    print(f"✅ Successfully updated: {updated}")
    print(f"⏭️  Already up-to-date: {skipped}")
    print(f"❌ Failed: {failed}")
    print("\n🎉 Interior photos update complete!")
    print("=" * 70)
    
    client.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
