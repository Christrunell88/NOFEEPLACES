#!/usr/bin/env python3
"""
Playwright-based scraper to extract apartment images from JavaScript-heavy sites
Uses browser automation to render dynamic content
"""

import asyncio
from playwright.async_api import async_playwright
import json
from urllib.parse import urljoin, urlparse
import re

async def scrape_with_playwright(url: str, wait_time: int = 5000):
    """
    Scrape a URL using Playwright with JavaScript rendering
    
    Args:
        url: URL to scrape
        wait_time: Time to wait for JavaScript to load (milliseconds)
    """
    
    print(f"\n{'='*80}")
    print(f"🔍 SCRAPING WITH PLAYWRIGHT: {url}")
    print(f"{'='*80}")
    
    async with async_playwright() as p:
        # Launch browser (headless mode)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        try:
            print(f"📄 Loading page...")
            
            # Navigate to URL
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            print(f"⏳ Waiting {wait_time/1000}s for JavaScript to render images...")
            await page.wait_for_timeout(wait_time)
            
            # Scroll to load lazy images
            print(f"📜 Scrolling to load lazy images...")
            await page.evaluate("""
                window.scrollTo(0, document.body.scrollHeight/4);
            """)
            await page.wait_for_timeout(1000)
            
            await page.evaluate("""
                window.scrollTo(0, document.body.scrollHeight/2);
            """)
            await page.wait_for_timeout(1000)
            
            await page.evaluate("""
                window.scrollTo(0, document.body.scrollHeight);
            """)
            await page.wait_for_timeout(2000)
            
            # Extract all images
            images = await page.evaluate("""
                () => {
                    const images = [];
                    const skipKeywords = ['logo', 'icon', 'svg', 'arrow', 'favicon', 'button', 'badge', 'marker', 'arrow'];
                    
                    // Get img tags
                    document.querySelectorAll('img').forEach(img => {
                        const src = img.src || img.getAttribute('data-src') || img.getAttribute('data-lazy-src');
                        if (src && src.startsWith('http')) {
                            const srcLower = src.toLowerCase();
                            if (!skipKeywords.some(keyword => srcLower.includes(keyword))) {
                                images.push({
                                    src: src,
                                    alt: img.alt || '',
                                    width: img.naturalWidth || img.width,
                                    height: img.naturalHeight || img.height
                                });
                            }
                        }
                    });
                    
                    // Get background images
                    document.querySelectorAll('*').forEach(elem => {
                        const style = window.getComputedStyle(elem);
                        const bgImage = style.backgroundImage;
                        if (bgImage && bgImage !== 'none') {
                            const match = bgImage.match(/url\\(['"]?([^'"\\)]+)['"]?\\)/);
                            if (match && match[1]) {
                                const src = match[1];
                                if (src.startsWith('http')) {
                                    const srcLower = src.toLowerCase();
                                    if (!skipKeywords.some(keyword => srcLower.includes(keyword))) {
                                        images.push({
                                            src: src,
                                            alt: 'background-image',
                                            width: elem.offsetWidth,
                                            height: elem.offsetHeight
                                        });
                                    }
                                }
                            }
                        }
                    });
                    
                    return images;
                }
            """)
            
            # Get page content for price extraction
            content = await page.content()
            
            # Extract prices
            prices = []
            price_matches = re.findall(r'\$\s*([\d,]+)', content)
            for match in price_matches:
                try:
                    price = int(match.replace(',', ''))
                    if 1500 <= price <= 20000:
                        prices.append(price)
                except:
                    continue
            
            # Categorize images by domain
            image_domains = {}
            unique_images = []
            seen = set()
            
            for img in images:
                src = img['src']
                if src not in seen:
                    seen.add(src)
                    unique_images.append(img)
                    
                    domain = urlparse(src).netloc
                    if domain not in image_domains:
                        image_domains[domain] = []
                    image_domains[domain].append(img)
            
            print(f"\n✅ Successfully scraped!")
            print(f"   Total unique images: {len(unique_images)}")
            
            if image_domains:
                print(f"\n🌐 Images by domain:")
                for domain, imgs in sorted(image_domains.items(), key=lambda x: len(x[1]), reverse=True):
                    print(f"   • {domain}: {len(imgs)} images")
            
            if unique_images:
                print(f"\n🖼️  Sample images (first 5):")
                for img in unique_images[:5]:
                    print(f"   {img['src'][:100]}...")
                    if img['alt']:
                        print(f"      Alt: {img['alt']}")
            
            if prices:
                unique_prices = sorted(set(prices))
                print(f"\n💰 Prices found: {unique_prices[:10]}")
            
            await browser.close()
            
            return {
                'success': True,
                'url': url,
                'images': [img['src'] for img in unique_images],
                'image_details': unique_images,
                'image_domains': {domain: [img['src'] for img in imgs] for domain, imgs in image_domains.items()},
                'prices': sorted(set(prices))
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await browser.close()
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }


async def scrape_all_building_sites():
    """Scrape all building sites with Playwright"""
    
    sites = [
        {
            'name': 'Mercedes House',
            'url': 'https://www.mercedeshouseny.com/studio',
            'type': 'studio'
        },
        {
            'name': 'Mercedes House',
            'url': 'https://www.mercedeshouseny.com/one-bed',
            'type': '1-bedroom'
        },
        {
            'name': 'Mercedes House',
            'url': 'https://www.mercedeshouseny.com/two-bed',
            'type': '2-bedroom'
        },
        {
            'name': 'Forty Six Fifty',
            'url': 'https://fortysixfifty.com/availability',
            'type': 'availability'
        },
        {
            'name': 'Manhattan Skyline',
            'url': 'https://www.manhattanskyline.com/',
            'type': 'main'
        }
    ]
    
    results = {}
    
    for site in sites:
        print(f"\n\n{'#'*80}")
        print(f"# {site['name']} - {site['type']}")
        print(f"{'#'*80}")
        
        result = await scrape_with_playwright(site['url'], wait_time=5000)
        
        key = f"{site['name']}_{site['type']}"
        results[key] = result
        
        # Small delay between requests
        await asyncio.sleep(2)
    
    return results


def generate_summary(results):
    """Generate summary of scraping results"""
    
    print(f"\n\n{'='*80}")
    print(f"📊 PLAYWRIGHT SCRAPING SUMMARY")
    print(f"{'='*80}")
    
    total_images = 0
    successful_scrapes = 0
    
    for site_name, result in results.items():
        if result.get('success'):
            successful_scrapes += 1
            image_count = len(result.get('images', []))
            total_images += image_count
            
            print(f"\n✅ {site_name}")
            print(f"   Images: {image_count}")
            print(f"   Prices: {len(result.get('prices', []))}")
            
            if result.get('image_domains'):
                print(f"   Top image sources:")
                for domain, imgs in list(result['image_domains'].items())[:3]:
                    print(f"      • {domain}: {len(imgs)} images")
        else:
            print(f"\n❌ {site_name}")
            print(f"   Error: {result.get('error', 'Unknown')[:150]}")
    
    print(f"\n{'='*80}")
    print(f"FINAL RESULTS:")
    print(f"   Sites attempted: {len(results)}")
    print(f"   Successful scrapes: {successful_scrapes}")
    print(f"   Total images found: {total_images}")
    print(f"{'='*80}")
    
    if total_images > 0:
        print(f"\n🎉 SUCCESS! Found {total_images} real apartment images!")
        print(f"   These are authentic images from building websites")
        print(f"   Ready to add to database")
    else:
        print(f"\n⚠️  No images found")
    
    # Save results
    output_file = '/app/playwright_scraping_results.json'
    
    # Prepare JSON-serializable data
    json_results = {}
    for site_name, result in results.items():
        json_results[site_name] = {
            'success': result.get('success'),
            'url': result.get('url'),
            'images': result.get('images', []),
            'image_count': len(result.get('images', [])),
            'prices': result.get('prices', []),
            'top_domains': list(result.get('image_domains', {}).keys())[:5]
        }
    
    with open(output_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")


async def main():
    print("🚀 PLAYWRIGHT-BASED APARTMENT IMAGE SCRAPER")
    print("   Using browser automation to render JavaScript")
    
    results = await scrape_all_building_sites()
    generate_summary(results)
    
    print("\n✅ Scraping complete!")


if __name__ == "__main__":
    asyncio.run(main())
