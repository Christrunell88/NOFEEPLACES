#!/usr/bin/env python3
"""
Extract all interior image URLs from Waterline Square gallery
Parse the shortpixel CDN URLs to get original image URLs
"""
import re
import os
import requests
import time
from urllib.parse import urlparse, unquote

# Markdown content from crawl (extracted image URLs)
MARKDOWN_CONTENT = """
https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Amenities_GatheringSpace_WaterlineSquare_Rental-wsq2-amenities-1-1440x720-1.jpg
https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/OurCommunity_Person20on20balcony_WaterlineSquare_3buildings_1WSQ_Hero_D.jpg
https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Interiors_Penthouse20Home20Water20View_Waterline20Square_3Penthouse_1440x720.jpg
https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/OurCommunity_Lobby_WaterlineSquare_wsq2-lobby.jpg
https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/OurCommunity_DuskBuilding_WaterlineSquare-1440x960.jpg
https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Interior_Kitchen_WaterlineSquare_Rental-wsq2-featured-4-1440x720-1.jpg
https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/OurCommunity_ApartmentExterior_WaterlineSquare-1440x960.jpg
https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/OurCommunity_Woman20walking20dog20on20trail_Waterline20Square_Park-purposefuldesign-4-1440x720-1.jpg
https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Interiors_Living20Room20Water20View_Waterline20Square_Rental_1440x720.jpg
https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Interiors_Kitchen20Island20witrh20Barstools_Waterline20Square_Rental_wsq1_kitchen1440x720.jpg
https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Amenities_Common20Area20Seating_Waterline20Square_200730_EJ_waterline_square-021913_MEDIUM_RES.jpg
https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Amenities_GatheringSpace_WaterlineSquare_Rental-wsq2-amenities-4-1440x720-1.jpg
"""

OUTPUT_DIR = "/app/backend/uploads/building_images/waterline_square"

def extract_original_url(cdn_url):
    """Extract original URL from shortpixel CDN URL"""
    # Remove the CDN prefix and get the original URL
    if "spcdn.shortpixel.ai" in cdn_url:
        # Pattern: https://spcdn.shortpixel.ai/spio/ret_img,q_cdnize,to_webp,s_webp/www.windsorcommunities.com/...
        match = re.search(r'/www\.windsorcommunities\.com/(.+)$', cdn_url)
        if match:
            return f"https://www.windsorcommunities.com/{match.group(1)}"
    return cdn_url

def is_interior_image(filename):
    """Check if image is an interior image based on filename"""
    interior_keywords = ['interior', 'kitchen', 'living', 'bedroom', 'bathroom', 'penthouse', 'home']
    filename_lower = filename.lower()
    return any(keyword in filename_lower for keyword in interior_keywords)

def download_image(url, output_path):
    """Download image from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"   Status {response.status_code}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 70)
    print("WATERLINE SQUARE INTERIOR IMAGES EXTRACTOR")
    print("=" * 70)
    
    # Extract all URLs from markdown
    cdn_urls = re.findall(r'https://[^\s\)]+', MARKDOWN_CONTENT)
    
    # Convert CDN URLs to original URLs
    original_urls = []
    for cdn_url in cdn_urls:
        original_url = extract_original_url(cdn_url)
        if original_url:
            original_urls.append(original_url)
    
    # Remove duplicates
    original_urls = list(set(original_urls))
    
    # Filter for interior images only
    interior_urls = []
    for url in original_urls:
        filename = os.path.basename(urlparse(url).path)
        if is_interior_image(filename):
            interior_urls.append(url)
    
    print(f"\nFound {len(original_urls)} total images")
    print(f"Filtered to {len(interior_urls)} interior images")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    for i, url in enumerate(interior_urls, 1):
        filename = os.path.basename(urlparse(url).path)
        filename = unquote(filename)  # Decode URL encoding
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # Skip if already exists
        if os.path.exists(output_path):
            print(f"[{i}/{len(interior_urls)}] {filename} - Already exists, skipping")
            skipped += 1
            continue
        
        print(f"[{i}/{len(interior_urls)}] Downloading: {filename}")
        
        if download_image(url, output_path):
            file_size = os.path.getsize(output_path) / 1024
            print(f"   ✅ Downloaded ({file_size:.1f} KB)")
            downloaded += 1
        else:
            print(f"   ❌ Failed")
            failed += 1
        
        time.sleep(0.5)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total interior images: {len(interior_urls)}")
    print(f"Downloaded: {downloaded}")
    print(f"Skipped (already exist): {skipped}")
    print(f"Failed: {failed}")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    
    # List all files
    all_files = sorted(os.listdir(OUTPUT_DIR))
    print(f"\nTotal files in directory: {len(all_files)}")
    for filename in all_files:
        filepath = os.path.join(OUTPUT_DIR, filename)
        file_size = os.path.getsize(filepath) / 1024
        print(f"  - {filename} ({file_size:.1f} KB)")

if __name__ == "__main__":
    main()
