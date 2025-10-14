#!/usr/bin/env python3
"""
Deep scrape Mercedes House for high-quality interior and amenity images
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_mercedes_house_gallery():
    """Scrape Mercedes House gallery and amenities pages for better images"""
    
    print("🏢 DEEP SCRAPING MERCEDES HOUSE FOR HIGH-QUALITY IMAGES")
    print("="*80)
    
    urls_to_scrape = [
        {
            'name': 'Studio Gallery',
            'url': 'https://www.mercedeshouseny.com/studio',
            'type': 'studio'
        },
        {
            'name': '1BR Gallery',
            'url': 'https://www.mercedeshouseny.com/one-bed',
            'type': '1-bedroom'
        },
        {
            'name': '2BR Gallery',
            'url': 'https://www.mercedeshouseny.com/two-bed',
            'type': '2-bedroom'
        },
        {
            'name': 'Amenities',
            'url': 'https://www.mercedeshouseny.com/amenities',
            'type': 'amenities'
        },
        {
            'name': 'Building',
            'url': 'https://www.mercedeshouseny.com/building',
            'type': 'building'
        },
        {
            'name': 'Neighborhood',
            'url': 'https://www.mercedeshouseny.com/neighborhood',
            'type': 'neighborhood'
        }
    ]
    
    all_results = {}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        for page_info in urls_to_scrape:
            page = await context.new_page()
            
            print(f"\n📄 Scraping: {page_info['name']}")
            print(f"   URL: {page_info['url']}")
            
            try:
                await page.goto(page_info['url'], wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(5000)
                
                # Scroll to load all images
                for i in range(3):
                    await page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {(i+1)/3})")
                    await page.wait_for_timeout(1500)
                
                # Extract all high-quality images
                images = await page.evaluate("""
                    () => {
                        const images = [];
                        const skipKeywords = ['logo', 'icon', 'arrow', 'favicon', 'button'];
                        
                        // Get all img tags
                        document.querySelectorAll('img').forEach(img => {
                            const src = img.src || img.getAttribute('data-src') || img.getAttribute('data-lazy-src');
                            if (src && src.startsWith('http')) {
                                const srcLower = src.toLowerCase();
                                if (!skipKeywords.some(k => srcLower.includes(k))) {
                                    images.push({
                                        src: src,
                                        alt: img.alt || '',
                                        width: img.naturalWidth || 0,
                                        height: img.naturalHeight || 0,
                                        srcset: img.srcset || ''
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
                                if (match && match[1] && match[1].startsWith('http')) {
                                    const src = match[1];
                                    const srcLower = src.toLowerCase();
                                    if (!skipKeywords.some(k => srcLower.includes(k))) {
                                        images.push({
                                            src: src,
                                            alt: 'background-image',
                                            width: elem.offsetWidth,
                                            height: elem.offsetHeight,
                                            srcset: ''
                                        });
                                    }
                                }
                            }
                        });
                        
                        return images;
                    }
                """)
                
                # Filter for high-quality images
                quality_images = []
                seen = set()
                
                for img in images:
                    src = img['src']
                    if src in seen:
                        continue
                    seen.add(src)
                    
                    # Include mercedeshouseny.com images
                    if 'mercedeshouseny.com' in src:
                        quality_images.append(img)
                    # Include other CDN images if they're large enough
                    elif img['width'] > 500 or img['height'] > 500:
                        quality_images.append(img)
                
                all_results[page_info['type']] = {
                    'url': page_info['url'],
                    'images': quality_images,
                    'image_count': len(quality_images)
                }
                
                print(f"   ✅ Found {len(quality_images)} high-quality images")
                
                # Show sample
                if quality_images:
                    print(f"   📸 Sample images:")
                    for img in quality_images[:3]:
                        print(f"      • {img['src'][:80]}... ({img['width']}x{img['height']})")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                all_results[page_info['type']] = {
                    'url': page_info['url'],
                    'images': [],
                    'image_count': 0,
                    'error': str(e)
                }
            
            await page.close()
            await asyncio.sleep(2)
        
        await browser.close()
    
    return all_results

async def main():
    results = await scrape_mercedes_house_gallery()
    
    # Save results
    output_file = '/app/mercedes_house_high_quality_images.json'
    
    # Convert to JSON-serializable format
    json_results = {}
    for page_type, data in results.items():
        json_results[page_type] = {
            'url': data['url'],
            'image_count': data['image_count'],
            'images': [img['src'] for img in data.get('images', [])]
        }
    
    with open(output_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"📊 SCRAPING SUMMARY")
    print(f"{'='*80}")
    
    total_images = sum(data['image_count'] for data in results.values())
    print(f"\nTotal high-quality images found: {total_images}")
    
    for page_type, data in results.items():
        print(f"\n{page_type.upper()}:")
        print(f"   Images: {data['image_count']}")
        if data.get('images'):
            # Group by domain
            domains = {}
            for img in data['images']:
                from urllib.parse import urlparse
                domain = urlparse(img['src']).netloc
                domains[domain] = domains.get(domain, 0) + 1
            
            print(f"   Sources:")
            for domain, count in domains.items():
                print(f"      • {domain}: {count} images")
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"\n✅ Deep scraping complete!")

if __name__ == "__main__":
    asyncio.run(main())
