#!/usr/bin/env python3
"""
Test scraping images from building management websites using Scraptio
"""

import requests
import json
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time

SCRAPTIO_API_KEY = "EojY57ygRvBC5z7OANEBcYA3AUGcd6hto7akS68SpSRRBowU6E7eD7Av7nRjXKsG"
SCRAPTIO_BASE_URL = "https://api.scraptio.com"

def scrape_with_scraptio(url: str):
    """Scrape a URL and extract images"""
    
    print(f"\n{'='*80}")
    print(f"🔍 SCRAPING: {url}")
    print(f"{'='*80}")
    
    payload = {
        'api_key': SCRAPTIO_API_KEY,
        'url': url
    }
    
    try:
        response = requests.post(
            f"{SCRAPTIO_BASE_URL}/scrape",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            html_content = data.get('data', '')
            
            print(f"✅ Successfully scraped ({len(html_content)} characters)")
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract all images
            images = []
            
            # Method 1: img tags with src
            for img in soup.find_all('img', src=True):
                src = img['src']
                
                # Skip icons, logos, etc.
                skip_keywords = ['logo', 'icon', 'svg', 'arrow', 'favicon', 'button', 'badge', 'marker']
                if any(keyword in src.lower() for keyword in skip_keywords):
                    continue
                
                # Convert relative to absolute URLs
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin(url, src)
                
                if src.startswith('http'):
                    images.append(src)
            
            # Method 2: data-src attributes (lazy loading)
            for elem in soup.find_all(attrs={'data-src': True}):
                src = elem['data-src']
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin(url, src)
                if src.startswith('http'):
                    images.append(src)
            
            # Method 3: Background images in style
            for elem in soup.find_all(style=re.compile(r'background-image', re.I)):
                style = elem.get('style', '')
                matches = re.findall(r'url\([\'"]?([^\'")\s]+)[\'"]?\)', style)
                for match in matches:
                    if match.startswith('//'):
                        match = 'https:' + match
                    elif match.startswith('/'):
                        match = urljoin(url, match)
                    if match.startswith('http'):
                        images.append(match)
            
            # Remove duplicates
            images = list(set(images))
            
            # Categorize images by domain
            image_domains = {}
            for img in images:
                domain = urlparse(img).netloc
                if domain not in image_domains:
                    image_domains[domain] = []
                image_domains[domain].append(img)
            
            print(f"\n📊 RESULTS:")
            print(f"   Total unique images: {len(images)}")
            print(f"\n🌐 Images by domain:")
            for domain, imgs in sorted(image_domains.items(), key=lambda x: len(x[1]), reverse=True):
                print(f"   • {domain}: {len(imgs)} images")
            
            if images:
                print(f"\n🖼️  Sample images (first 5):")
                for img in images[:5]:
                    print(f"   {img}")
            
            # Extract prices
            prices = []
            price_matches = re.findall(r'\$\s*([\d,]+)', html_content)
            for match in price_matches:
                try:
                    price = int(match.replace(',', ''))
                    if 1500 <= price <= 20000:
                        prices.append(price)
                except:
                    continue
            
            if prices:
                unique_prices = sorted(set(prices))
                print(f"\n💰 Prices found: {unique_prices[:10]}")
            
            return {
                'success': True,
                'url': url,
                'images': images,
                'image_domains': image_domains,
                'prices': sorted(set(prices)),
                'html_length': len(html_content)
            }
            
        else:
            print(f"❌ Error {response.status_code}: {response.text[:200]}")
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return {'success': False, 'error': str(e)}


def test_all_sites():
    """Test all building sites"""
    
    sites = [
        {
            'name': 'Two Trees Management',
            'url': 'https://www.twotreesny.com/',
            'description': 'Main website - Mercedes House, DUMBO properties'
        },
        {
            'name': 'Mercedes House (Two Trees)',
            'url': 'https://www.mercedeshouseny.com/',
            'description': 'Mercedes House specific site'
        },
        {
            'name': 'Forty Six Fifty',
            'url': 'https://fortysixfifty.com/availability',
            'description': 'Forty Six Fifty availability page'
        },
        {
            'name': 'Manhattan Skyline Management',
            'url': 'https://www.manhattanskyline.com/',
            'description': 'Manhattan Skyline main site'
        }
    ]
    
    results = {}
    
    for site in sites:
        print(f"\n\n{'#'*80}")
        print(f"# {site['name']}")
        print(f"# {site['description']}")
        print(f"{'#'*80}")
        
        time.sleep(2)  # Rate limiting
        
        result = scrape_with_scraptio(site['url'])
        results[site['name']] = result
    
    return results


def generate_summary(results):
    """Generate summary of scraping results"""
    
    print(f"\n\n{'='*80}")
    print(f"📊 FINAL SUMMARY")
    print(f"{'='*80}")
    
    total_images = 0
    accessible_sites = 0
    
    for site_name, result in results.items():
        if result.get('success'):
            accessible_sites += 1
            image_count = len(result.get('images', []))
            total_images += image_count
            
            print(f"\n✅ {site_name}")
            print(f"   Images found: {image_count}")
            print(f"   Prices found: {len(result.get('prices', []))}")
            
            if result.get('image_domains'):
                print(f"   Top domains:")
                for domain, imgs in list(result['image_domains'].items())[:3]:
                    print(f"      • {domain}: {len(imgs)}")
        else:
            print(f"\n❌ {site_name}")
            print(f"   Error: {result.get('error', 'Unknown')[:100]}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL RESULTS:")
    print(f"   Sites scraped: {len(results)}")
    print(f"   Sites accessible: {accessible_sites}")
    print(f"   Total images found: {total_images}")
    print(f"{'='*80}")
    
    if total_images > 0:
        print(f"\n✅ SUCCESS! Found {total_images} images across {accessible_sites} sites")
        print(f"   These images can be used for real apartment listings")
    else:
        print(f"\n⚠️  No images found - sites may use JavaScript image loading")
        print(f"   May need browser automation (Playwright/Selenium)")
    
    # Save results
    output_file = '/app/building_sites_scraping_results.json'
    with open(output_file, 'w') as f:
        # Convert results to JSON-serializable format
        json_results = {}
        for site_name, result in results.items():
            json_results[site_name] = {
                'success': result.get('success'),
                'url': result.get('url'),
                'images': result.get('images', []),
                'image_count': len(result.get('images', [])),
                'prices': result.get('prices', []),
                'html_length': result.get('html_length', 0),
                'top_domains': list(result.get('image_domains', {}).keys())[:5]
            }
        json.dump(json_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")


if __name__ == "__main__":
    print("🚀 TESTING BUILDING SITE IMAGE ACCESSIBILITY")
    print(f"   Scraptio API Key: {SCRAPTIO_API_KEY[:20]}...")
    
    results = test_all_sites()
    generate_summary(results)
    
    print("\n✅ Testing complete!")
