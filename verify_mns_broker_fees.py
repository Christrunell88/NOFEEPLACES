#!/usr/bin/env python3
"""
Verify broker fee status for MNS.com Brooklyn listings
Check individual listing pages for "no fee" or broker fee information
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, List
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')


async def check_listing_fee_status(page, url: str) -> Dict:
    """Check a single listing for broker fee information"""
    
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2000)
        
        # Get page content
        html = await page.content()
        text_content = html.lower()
        
        # Check for various broker fee indicators
        is_no_fee = False
        fee_info = "Unknown"
        
        # Check for "no fee" indicators
        no_fee_patterns = [
            r'no\s+fee',
            r'no-fee',
            r'zero\s+fee',
            r'fee\s+free',
            r'no\s+broker\s+fee',
            r'owner\s+pays',
            r'landlord\s+pays'
        ]
        
        for pattern in no_fee_patterns:
            if re.search(pattern, text_content):
                is_no_fee = True
                fee_info = "No fee"
                break
        
        # Check for broker fee required
        broker_fee_patterns = [
            r'broker\s+fee\s+required',
            r'broker\s+fee:\s*1',
            r'1\s+month\s+broker',
            r'15%\s+broker',
            r'with\s+broker\s+fee'
        ]
        
        for pattern in broker_fee_patterns:
            if re.search(pattern, text_content):
                is_no_fee = False
                fee_info = "Broker fee required"
                break
        
        # If still unknown, look for "OP" (Owner Pays) or similar
        if fee_info == "Unknown":
            if re.search(r'\bop\b', text_content):
                is_no_fee = True
                fee_info = "No fee (OP)"
        
        return {
            'url': url,
            'is_no_fee': is_no_fee,
            'fee_info': fee_info
        }
        
    except Exception as e:
        print(f"      ❌ Error checking {url}: {e}")
        return {
            'url': url,
            'is_no_fee': False,
            'fee_info': f"Error: {str(e)}"
        }


async def verify_mns_broker_fees():
    """Verify broker fee status for all MNS listings"""
    
    print("="*80)
    print("🔍 VERIFYING MNS.COM BROKER FEE STATUS")
    print("="*80)
    
    # Get all MNS listings from database
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    mns_listings = await db.apartments.find({
        'data_source': 'MNS Real Estate'
    }).to_list(length=None)
    
    print(f"\n📋 Found {len(mns_listings)} MNS listings to verify")
    print(f"   Sampling 30 listings to check broker fee status...\n")
    
    # Sample 30 listings to check (representative sample)
    import random
    sample_size = min(30, len(mns_listings))
    sample_listings = random.sample(mns_listings, sample_size)
    
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for idx, listing in enumerate(sample_listings, 1):
            url = listing.get('mns_detail_url')
            if not url:
                continue
            
            print(f"[{idx}/{sample_size}] Checking: {listing['neighborhood']} - ${listing['price']:,.0f}/mo")
            
            result = await check_listing_fee_status(page, url)
            result['neighborhood'] = listing['neighborhood']
            result['price'] = listing['price']
            results.append(result)
            
            print(f"      Status: {result['fee_info']}")
            
            # Small delay to avoid rate limiting
            await page.wait_for_timeout(1000)
        
        await browser.close()
    
    client.close()
    
    # Analyze results
    print(f"\n{'='*80}")
    print("📊 VERIFICATION RESULTS")
    print(f"{'='*80}")
    
    no_fee_count = sum(1 for r in results if r['is_no_fee'])
    broker_fee_count = len(results) - no_fee_count
    
    print(f"\nSample size: {len(results)} listings")
    print(f"  • No fee: {no_fee_count} ({no_fee_count/len(results)*100:.1f}%)")
    print(f"  • Broker fee required: {broker_fee_count} ({broker_fee_count/len(results)*100:.1f}%)")
    
    # Show breakdown by fee status
    print(f"\n📋 Fee Status Breakdown:")
    fee_statuses = {}
    for r in results:
        status = r['fee_info']
        fee_statuses[status] = fee_statuses.get(status, 0) + 1
    
    for status, count in sorted(fee_statuses.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {status}: {count} listings")
    
    # Save results
    with open('/app/mns_fee_verification.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to /app/mns_fee_verification.json")
    
    # Recommendation
    print(f"\n{'='*80}")
    print("💡 RECOMMENDATION")
    print(f"{'='*80}")
    
    if no_fee_count == 0:
        print("All sampled listings appear to have broker fees.")
        print("✅ Current 'Broker Fee May Apply' label is accurate.")
        print("   No database updates needed.")
    elif no_fee_count == len(results):
        print("All sampled listings are NO FEE!")
        print("⚠️  Should update all 170 MNS listings to 'No fee'")
    else:
        print(f"Mixed results: {no_fee_count} no-fee, {broker_fee_count} with broker fee")
        print("⚠️  Need to check each listing individually or keep generic 'Broker Fee May Apply'")
    
    return results


async def update_no_fee_listings(results: List[Dict]):
    """Update database for listings confirmed as no-fee"""
    
    no_fee_urls = [r['url'] for r in results if r['is_no_fee']]
    
    if not no_fee_urls:
        print("\n⚠️  No no-fee listings to update")
        return
    
    print(f"\n{'='*80}")
    print(f"💾 UPDATING DATABASE")
    print(f"{'='*80}")
    print(f"Updating {len(no_fee_urls)} confirmed no-fee listings...")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    result = await db.apartments.update_many(
        {'mns_detail_url': {'$in': no_fee_urls}},
        {'$set': {'broker_fee': 'No fee'}}
    )
    
    print(f"✅ Updated {result.modified_count} listings to 'No fee'")
    
    client.close()


async def main():
    """Main workflow"""
    
    # Verify broker fees
    results = await verify_mns_broker_fees()
    
    # Ask if user wants to update database
    print(f"\n{'='*80}")
    print("Next steps:")
    print("1. Review /app/mns_fee_verification.json")
    print("2. If all/most are no-fee, run update function")
    print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(main())
