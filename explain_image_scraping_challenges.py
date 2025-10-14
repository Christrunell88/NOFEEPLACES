#!/usr/bin/env python3
"""
Why Image Scraping Fails vs Text Crawling Success
Explanation and solutions for image download limitations
"""

def explain_scraping_limitations():
    """Explain why text crawling works but image copying fails"""
    
    print("🔍 WHY TEXT CRAWLING WORKS BUT IMAGE COPYING FAILS")
    print("=" * 70)
    
    limitations = {
        "1. CORS (Cross-Origin Resource Sharing) Restrictions": {
            "explanation": "Websites block cross-origin requests to images",
            "technical_detail": "Images return 'Access-Control-Allow-Origin' errors",
            "example": "nestiostatic.com blocks our domain from downloading images",
            "workaround": "Use server-side proxy or different headers"
        },
        
        "2. Anti-Bot Protection": {
            "explanation": "Websites detect and block automated scraping bots", 
            "technical_detail": "Cloudflare, bot detection services block requests",
            "example": "Many real estate sites use bot protection",
            "workaround": "Rotate user agents, use residential proxies, add delays"
        },
        
        "3. Authentication Requirements": {
            "explanation": "Images may require login or special tokens",
            "technical_detail": "403/401 errors when accessing image URLs directly", 
            "example": "Private property photos behind login walls",
            "workaround": "Session management, cookie handling"
        },
        
        "4. Rate Limiting": {
            "explanation": "Servers limit download frequency to prevent abuse",
            "technical_detail": "429 Too Many Requests errors after several downloads",
            "example": "Image CDNs throttle excessive requests",
            "workaround": "Add delays, respect robots.txt, use multiple IP addresses"
        },
        
        "5. Dynamic Loading (JavaScript)": {
            "explanation": "Images loaded via JavaScript after page load",
            "technical_detail": "Initial HTML doesn't contain actual image URLs",
            "example": "Lazy loading, infinite scroll image galleries",
            "workaround": "Use browser automation (Playwright/Selenium)"
        },
        
        "6. Hotlinking Protection": {
            "explanation": "Images require proper Referer header",
            "technical_detail": "403 Forbidden without correct referer",
            "example": "Image CDNs check if request comes from same domain",
            "workaround": "Set proper referer headers in requests"
        },
        
        "7. Legal/Terms of Service": {
            "explanation": "Website terms prohibit image downloading",
            "technical_detail": "Copyright protection, usage licensing",
            "example": "Professional photography, copyrighted content",
            "workaround": "Use with permission, respect fair use, use alternatives"
        }
    }
    
    for reason, details in limitations.items():
        print(f"\n🚫 {reason}")
        print("-" * 50)
        print(f"Issue: {details['explanation']}")
        print(f"Technical: {details['technical_detail']}")
        print(f"Example: {details['example']}")
        print(f"Solution: {details['workaround']}")
    
    print(f"\n✅ WHY TEXT CRAWLING USUALLY WORKS:")
    print("-" * 50)
    print("• HTML content is meant to be publicly readable")
    print("• Search engines need access to text for indexing")
    print("• Text is typically served with permissive CORS policies")
    print("• Less server resources needed for text vs images")
    print("• Legal protections are usually lower for factual data")

def demonstrate_solutions():
    """Show potential solutions for better image downloading"""
    
    print(f"\n🛠️  POTENTIAL SOLUTIONS FOR IMAGE DOWNLOADING")
    print("=" * 60)
    
    solutions = [
        {
            "name": "Enhanced Headers & User Agents",
            "description": "Mimic real browser requests more accurately",
            "code": """
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://source-website.com/',
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site'
}"""
        },
        
        {
            "name": "Session Management",
            "description": "Maintain cookies and session state",
            "code": """
async with aiohttp.ClientSession(
    connector=aiohttp.TCPConnector(ssl=False),
    timeout=aiohttp.ClientTimeout(total=30),
    cookies=session_cookies
) as session:
    # First visit the page to establish session
    await session.get(page_url)
    # Then download images with session context
    await session.get(image_url)"""
        },
        
        {
            "name": "Browser Automation for JS-Heavy Sites",
            "description": "Use Playwright for sites requiring JavaScript execution",
            "code": """
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    
    # Wait for images to load
    await page.goto(url)
    await page.wait_for_load_state('networkidle')
    
    # Extract image URLs after JS execution
    image_urls = await page.evaluate('''() => {
        return Array.from(document.images).map(img => img.src);
    }''')"""
        },
        
        {
            "name": "Proxy Rotation",
            "description": "Rotate IP addresses to avoid rate limiting",
            "code": """
proxies = [
    'http://proxy1:8080',
    'http://proxy2:8080',
    'http://proxy3:8080'
]

for proxy in proxies:
    try:
        response = await session.get(
            image_url, 
            proxy=proxy,
            timeout=10
        )
        if response.status == 200:
            break
    except:
        continue"""
        },
        
        {
            "name": "Respectful Rate Limiting",
            "description": "Add delays to avoid being blocked",
            "code": """
import random
import asyncio

async def download_with_delay(urls):
    for url in urls:
        try:
            await download_image(url)
            # Random delay between 1-3 seconds
            await asyncio.sleep(random.uniform(1.0, 3.0))
        except Exception as e:
            print(f"Failed: {url} - {e}")
            # Longer delay after failure
            await asyncio.sleep(5.0)"""
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f"\n{i}. {solution['name']}")
        print(f"   Purpose: {solution['description']}")
        print(f"   Implementation:")
        print(solution['code'])

def show_legal_considerations():
    """Show legal and ethical considerations"""
    
    print(f"\n⚖️  LEGAL & ETHICAL CONSIDERATIONS")
    print("=" * 50)
    
    considerations = [
        "✅ Always check robots.txt and terms of service",
        "✅ Respect rate limits and server resources", 
        "✅ Use images only with proper licensing/permission",
        "✅ Consider fair use for factual/news purposes",
        "✅ Provide attribution when required",
        "✅ Don't republish copyrighted professional photography",
        "✅ Use alternatives like stock photos when possible",
        "⚠️ Real estate photos often have strict copyright",
        "⚠️ Professional photography is heavily protected",
        "⚠️ Bulk downloading can be considered abuse"
    ]
    
    for consideration in considerations:
        print(f"  {consideration}")

def main():
    """Run the explanation"""
    explain_scraping_limitations()
    demonstrate_solutions()
    show_legal_considerations()
    
    print(f"\n💡 SUMMARY:")
    print("=" * 30)
    print("Text crawling works because:")
    print("  • Publicly accessible for SEO/search engines")
    print("  • Lower server cost and legal protection")
    print("  • Standardized access methods")
    print("")
    print("Image copying fails because:")
    print("  • Technical protections (CORS, auth, rate limits)")
    print("  • Legal protections (copyright, terms of service)")
    print("  • Higher server costs (bandwidth, storage)")
    print("")
    print("Solutions exist but require:")
    print("  • More sophisticated technical approaches")
    print("  • Respect for legal and ethical boundaries")
    print("  • Often better to use stock photos or get permission")

if __name__ == "__main__":
    main()