#!/usr/bin/env python3
"""
Mercedes House Unit Scraper
Systematically finds and adds Mercedes House listings from Funnel Leasing
"""

import asyncio
import aiohttp
import os
import uuid
import json
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import time
import random

# Load environment variables
load_dotenv('/app/backend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces')

class MercedesHouseScraper:
    def __init__(self):
        self.base_url = "https://api.funnelleasing.com"
        self.building_id = "1259"  # From the URLs we've seen
        self.property_id = "15"    # From the URLs we've seen
        self.session = None
        self.found_listings = []
        self.added_count = 0
        
    async def get_building_page(self):
        """Get the main building page to find available units"""
        building_url = f"{self.base_url}/p/building/15/1259/10/6z9-3989e719bddc0ebde5e0/"
        
        print(f"🏢 Checking Mercedes House building page...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(building_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        print(f"✅ Successfully loaded building page ({len(content)} characters)")
                        return content
                    else:
                        print(f"❌ Building page returned status {response.status}")
                        return None
        except Exception as e:
            print(f"❌ Error loading building page: {str(e)}")
            return None
    
    async def find_listing_urls(self):
        """Systematically search for Mercedes House listing URLs"""
        print("🔍 Searching for Mercedes House listing URLs...")
        
        # Pattern from the URLs we know:
        # https://api.funnelleasing.com/p/listing/15/16004/10/6z9-522755ce9379a8bb079d/
        # https://api.funnelleasing.com/p/listing/15/116647/10/6z9-a0413999956c359e34fc/
        
        # Known listing IDs to start with
        known_listing_ids = ["16004", "116647"]
        
        # Try to find patterns or adjacent listing IDs
        potential_ids = []
        
        # Add known IDs
        potential_ids.extend(known_listing_ids)
        
        # Try numbers around the known IDs
        for known_id in known_listing_ids:
            base_num = int(known_id)
            # Try ±100 around each known ID
            for offset in range(-100, 101, 10):
                potential_id = str(base_num + offset)
                if potential_id not in potential_ids:
                    potential_ids.append(potential_id)
        
        print(f"📋 Generated {len(potential_ids)} potential listing IDs to check")
        
        valid_urls = []
        
        # Test each potential listing ID
        for i, listing_id in enumerate(potential_ids[:50]):  # Limit to first 50 for efficiency
            # Generate a reasonable hash (pattern from known URLs)
            test_hash = f"6z9-{random.randint(100000000000000000, 999999999999999999):x}"
            test_url = f"{self.base_url}/p/listing/15/{listing_id}/10/{test_hash}/"
            
            print(f"Testing {i+1}/50: Listing ID {listing_id}...", end="")
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(test_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            # Check if it's a Mercedes House listing
                            if "Mercedes House" in content and "550 West 54th" in content:
                                valid_urls.append(test_url)
                                print(" ✅ Found Mercedes House unit!")
                            elif "550 West 54th" in content:
                                valid_urls.append(test_url)
                                print(" ✅ Found 550 West 54th unit!")
                            else:
                                print(" ⚠️ Not Mercedes House")
                        else:
                            print(" ❌ No listing")
                            
            except Exception as e:
                print(f" ❌ Error: {str(e)}")
            
            # Be respectful with requests
            await asyncio.sleep(1)
        
        return valid_urls
    
    async def extract_listing_data(self, url):
        """Extract apartment data from a listing URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    
                    content = await response.text()
                    
                    # Parse the content to extract apartment details
                    # This is a simplified extraction - in production, you'd use proper HTML parsing
                    listing_data = {
                        "url": url,
                        "content_preview": content[:500] + "..." if len(content) > 500 else content
                    }
                    
                    return listing_data
                    
        except Exception as e:
            print(f"Error extracting data from {url}: {str(e)}")
            return None
    
    async def generate_more_listing_urls(self):
        """Generate more systematic listing URL attempts"""
        print("\n🔄 Generating systematic listing URLs...")
        
        # Use the known pattern but try different approaches
        base_patterns = [
            "https://api.funnelleasing.com/p/listing/15/{}/10/6z9-{}/"
        ]
        
        # Try a range of listing IDs based on known ones
        listing_id_ranges = [
            range(15900, 16100),   # Around 16004
            range(116500, 116800), # Around 116647
            range(120000, 120200), # Newer potential range
            range(10000, 10200),   # Lower range
        ]
        
        test_urls = []
        
        for pattern in base_patterns:
            for id_range in listing_id_ranges:
                for listing_id in list(id_range)[:20]:  # Limit each range
                    # Generate random hash-like suffix
                    hash_suffix = f"{random.randint(100000000000000000000000, 999999999999999999999999):x}"[:24]
                    url = pattern.format(listing_id, hash_suffix)
                    test_urls.append(url)
        
        print(f"🎯 Generated {len(test_urls)} systematic test URLs")
        
        # Test the URLs
        valid_listings = []
        
        for i, url in enumerate(test_urls[:30]):  # Test first 30
            print(f"Testing {i+1}/30: {url.split('/')[-3]}...", end="")
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            content = await response.text()
                            if "Mercedes House" in content or "550 West 54th" in content:
                                print(" ✅ Found!")
                                valid_listings.append(url)
                            else:
                                print(" ⚠️ Different property")
                        else:
                            print(" ❌")
            except Exception as e:
                print(f" ❌ {str(e)[:30]}")
            
            await asyncio.sleep(0.5)  # Be respectful
        
        return valid_listings

    async def get_mercedes_house_info(self):
        """Get general information about Mercedes House availability"""
        print("🏢 Mercedes House Unit Discovery")
        print("="*50)
        print("Building: Mercedes House (Two Trees Management)")
        print("Address: 550 West 54th Street, Hell's Kitchen")
        print("Known Units: #1915 (19th floor), #902 (9th floor)")
        print()
        
        # Try to find more listings
        building_content = await self.get_building_page()
        
        if building_content:
            # Look for patterns in the building page
            print("📊 Building page analysis:")
            if "available" in building_content.lower():
                print("   ✅ Contains availability information")
            if "unit" in building_content.lower():
                print("   ✅ Contains unit information")
            if "studio" in building_content.lower():
                print("   ✅ Contains studio listings")
            if "bedroom" in building_content.lower():
                print("   ✅ Contains bedroom listings")
        
        # Try systematic URL generation
        found_urls = await self.generate_more_listing_urls()
        
        return found_urls

async def main():
    """Main function to discover Mercedes House units"""
    print("🏙️ Mercedes House Unit Discovery System")
    print("="*60)
    
    scraper = MercedesHouseScraper()
    
    # Get information and find more units
    found_urls = await scraper.get_mercedes_house_info()
    
    print(f"\n📈 Discovery Results:")
    print(f"   Found {len(found_urls)} potential Mercedes House listings")
    
    if found_urls:
        print("\n🔗 Discovered URLs:")
        for i, url in enumerate(found_urls, 1):
            print(f"   {i}. {url}")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Manually verify these URLs contain Mercedes House units")
        print(f"   2. Extract apartment data from each valid URL") 
        print(f"   3. Add units to NoFeePlaces database")
        print(f"   4. Continue systematic discovery for more units")
    else:
        print("\n💭 Alternative Approaches:")
        print("   1. Contact Mercedes House leasing directly")
        print("   2. Check their main website for available units")
        print("   3. Use the building page to find unit listings")
        print("   4. Try different Funnel Leasing URL patterns")
    
    return found_urls

if __name__ == "__main__":
    asyncio.run(main())