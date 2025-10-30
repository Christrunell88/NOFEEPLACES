#!/usr/bin/env python3
"""
Scrape Waterline Square interior images from gallery page
"""
import re
import os
import requests
import hashlib
from urllib.parse import urlparse
import time

# URLs extracted from the gallery page
IMAGE_URLS = [
    "https://www.windsorcommunities.com/wp-content/uploads/2022/03/Interiors_Penthouse20Home20Water20View_Waterline20Square_3Penthouse_1440x720.jpg",
    "https://www.windsorcommunities.com/wp-content/uploads/2022/03/Interior_Kitchen_WaterlineSquare_Rental-wsq2-featured-4-1440x720-1.jpg",
    "https://www.windsorcommunities.com/wp-content/uploads/2022/03/Interiors_Living20Room20Water20View_Waterline20Square_Rental_1440x720.jpg",
    "https://www.windsorcommunities.com/wp-content/uploads/2022/03/Interiors_Kitchen20Island20witrh20Barstools_Waterline20Square_Rental_wsq1_kitchen1440x720.jpg",
    "https://www.windsorcommunities.com/wp-content/uploads/2022/03/OurCommunity_Person20on20balcony_WaterlineSquare_3buildings_1WSQ_Hero_D.jpg",
    "https://www.windsorcommunities.com/wp-content/uploads/2022/03/OurCommunity_Lobby_WaterlineSquare_wsq2-lobby.jpg",
]

OUTPUT_DIR = "/app/backend/uploads/building_images/waterline_square"

def download_image(url, output_path):
    """Download image from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"Failed to download {url}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def main():
    """Main function to download all images"""
    print("=" * 70)
    print("WATERLINE SQUARE IMAGE SCRAPER")
    print("=" * 70)
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    downloaded = 0
    failed = 0
    
    for i, url in enumerate(IMAGE_URLS, 1):
        # Extract filename from URL
        filename = os.path.basename(urlparse(url).path)
        
        # Clean up filename (remove URL encoding)
        filename = filename.replace('%20', '_')
        
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        print(f"\n[{i}/{len(IMAGE_URLS)}] Downloading: {filename}")
        print(f"   URL: {url[:80]}...")
        
        if download_image(url, output_path):
            file_size = os.path.getsize(output_path) / 1024  # KB
            print(f"   ✅ Downloaded ({file_size:.1f} KB)")
            downloaded += 1
        else:
            print(f"   ❌ Failed")
            failed += 1
        
        # Be nice to the server
        time.sleep(0.5)
    
    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"Total images: {len(IMAGE_URLS)}")
    print(f"Downloaded: {downloaded}")
    print(f"Failed: {failed}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # List downloaded files
    print("\nDownloaded files:")
    for filename in sorted(os.listdir(OUTPUT_DIR)):
        filepath = os.path.join(OUTPUT_DIR, filename)
        file_size = os.path.getsize(filepath) / 1024  # KB
        print(f"  - {filename} ({file_size:.1f} KB)")

if __name__ == "__main__":
    main()
