#!/usr/bin/env python3
"""
Improved Scraptio Scraper with JavaScript rendering support
Scrapes real apartment images from Mercedes House and other buildings
"""

import requests
import json
from bs4 import BeautifulSoup
import re
from typing import List, Dict
import time
import os

# Your Scraptio API key
SCRAPTIO_API_KEY = "yOfcV3dkuKvSnXg1Pf7MH4FKcY0a3S2QCE23pqps3UfpZPegmxWuHWthnCdZcIcd"
SCRAPTIO_BASE_URL = "https://api.scraptio.com"

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')


def scrape_with_scraptio(url: str, render_js: bool = True) -> dict:
    """
    Use Scraptio API to scrape a webpage with JavaScript rendering
    
    Args:
        url: URL to scrape
        render_js: Whether to render JavaScript (default True for modern sites)
    
    Returns:
        dict with 'html' and 'images' keys
    """
    
    print(f"🔍 Scraping: {url}")
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Scraptio API payload with JS rendering
    payload = {
        'api_key': SCRAPTIO_API_KEY,
        'url': url,
        'render_js': render_js,  # Enable JavaScript rendering
        'wait_for': 3000,  # Wait 3 seconds for JS to load
        'extract_images': True  # Extract all images from the page
    }
    
    try:
        response = requests.post(
            f"{SCRAPTIO_BASE_URL}/scrape",
            headers=headers,
            json=payload,
            timeout=60  # Longer timeout for JS rendering
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Scraped successfully")
            
            # Extract HTML
            html = data.get('html', '')
            
            # Extract images if provided by API
            images = data.get('images', [])
            
            return {
                'html': html,
                'images': images,
                'success': True
            }
        else:
            print(f"  ⚠️  Status {response.status_code}: {response.text[:200]}")
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {'success': False, 'error': str(e)}


def extract_images_from_html(html: str, base_url: str) -> List[str]:
    """Extract image URLs from HTML"""
    
    soup = BeautifulSoup(html, 'html.parser')
    images = []
    
    # Find all img tags
    for img in soup.find_all('img', src=True):
        src = img['src']
        
        # Skip icons, logos, etc.
        if any(skip in src.lower() for skip in ['logo', 'icon', 'svg', 'arrow', 'favicon']):
            continue
        
        # Convert relative URLs to absolute
        if src.startswith('//'):
            src = 'https:' + src
        elif src.startswith('/'):
            from urllib.parse import urljoin
            src = urljoin(base_url, src)
        
        if src.startswith('http'):
            images.append(src)
    
    # Find background images in CSS
    for elem in soup.find_all(style=re.compile(r'background-image', re.I)):
        style = elem.get('style', '')
        match = re.search(r'url\([\'"]?([^\'")\s]+)[\'"]?\)', style)
        if match:
            url = match.group(1)
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                from urllib.parse import urljoin
                url = urljoin(base_url, url)
            if url.startswith('http'):
                images.append(url)
    
    return list(set(images))


def extract_prices_from_html(html: str) -> List[int]:
    """Extract prices from HTML"""
    
    soup = BeautifulSoup(html, 'html.parser')
    prices = []
    
    # Look for price/rent text
    text_content = soup.get_text()
    
    # Find all price patterns
    price_patterns = [
        r'\$\s*([\d,]+)\s*(?:/month|per month|monthly)?',
        r'rent[:\s]+\$\s*([\d,]+)',
        r'price[:\s]+\$\s*([\d,]+)'
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        for match in matches:
            price = int(match.replace(',', ''))
            # Filter realistic NYC apartment prices
            if 1500 <= price <= 20000:
                prices.append(price)
    
    return sorted(set(prices))


def scrape_mercedes_house():
    """Scrape Mercedes House with Scraptio"""
    
    print("\n" + "="*80)
    print("🏢 SCRAPING MERCEDES HOUSE")
    print("="*80)
    
    pages = {
        'studio': 'https://www.mercedeshouseny.com/studio',
        '1-bedroom': 'https://www.mercedeshouseny.com/one-bed',
        '2-bedroom': 'https://www.mercedeshouseny.com/two-bed'
    }
    
    scraped_data = {}
    
    for page_type, url in pages.items():
        time.sleep(2)  # Rate limiting
        
        result = scrape_with_scraptio(url, render_js=True)
        
        if result.get('success'):
            html = result.get('html', '')
            api_images = result.get('images', [])
            
            # Extract images from HTML
            html_images = extract_images_from_html(html, url)
            
            # Combine images from API and HTML
            all_images = list(set(api_images + html_images))
            
            # Filter for apartment/building images
            filtered_images = [
                img for img in all_images
                if any(domain in img for domain in [
                    'mercedeshouseny.com',
                    'cloudinary.com',
                    'amazonaws.com',
                    'cdn'
                ])
            ]
            
            # Extract prices
            prices = extract_prices_from_html(html)
            
            scraped_data[page_type] = {
                'url': url,
                'images': filtered_images[:10],  # Limit to 10 best images
                'prices': prices,
                'total_images_found': len(all_images)
            }
            
            print(f"\n  {page_type.upper()}:")
            print(f"    Total images found: {len(all_images)}")
            print(f"    Filtered images: {len(filtered_images)}")
            print(f"    Prices found: {prices}")
    
    return scraped_data


def save_results(data: dict):
    """Save scraped results to JSON"""
    
    output_file = '/app/scraptio_mercedes_house_results.json'
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Print summary
    print(f"\n📊 SCRAPING SUMMARY:")
    for page_type, info in data.items():
        print(f"   {page_type}:")
        print(f"     Images: {len(info['images'])}")
        print(f"     Prices: {info['prices']}")
        if info['images']:
            print(f"     Sample image: {info['images'][0][:80]}...")


def main():
    """Main execution"""
    
    print("🚀 Starting Scraptio Mercedes House Scraper")
    print("   API Key: " + SCRAPTIO_API_KEY[:20] + "...")
    
    # Scrape Mercedes House
    data = scrape_mercedes_house()
    
    # Save results
    save_results(data)
    
    print("\n✅ Scraping complete!")
    print("\n💡 Next steps:")
    print("   1. Review scraptio_mercedes_house_results.json")
    print("   2. Verify image URLs are working")
    print("   3. Update database with real unit-specific images")


if __name__ == "__main__":
    main()
