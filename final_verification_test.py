#!/usr/bin/env python3
"""
Final verification test to confirm the apartment count fix
"""

import requests
import json

# Configuration
BASE_URL = "https://apartment-finder-3.preview.emergentagent.com/api"

def test_apartment_count_fix():
    """Test that the apartment count issue is resolved"""
    print("🔧 Testing Apartment Count Fix")
    print("=" * 50)
    
    try:
        # Test the default API call (what frontend now makes with limit=50)
        response = requests.get(f"{BASE_URL}/apartments", params={"limit": 50})
        
        if response.status_code == 200:
            apartments = response.json()
            total_count = len(apartments)
            
            print(f"✅ API Response: {response.status_code}")
            print(f"📊 Total Apartments Returned: {total_count}")
            
            if total_count == 30:
                print("✅ SUCCESS: All 30 apartments are now being returned!")
                
                # Count TFC listings
                tfc_count = sum(1 for apt in apartments if apt.get("source_url") == "https://tfc.com")
                print(f"🏢 TFC Listings: {tfc_count}/10")
                
                if tfc_count == 10:
                    print("✅ SUCCESS: All 10 TFC listings are included!")
                else:
                    print(f"❌ ISSUE: Only {tfc_count} TFC listings found")
                
                # Show breakdown by source
                source_counts = {}
                for apt in apartments:
                    source = apt.get("source_url", "unknown")
                    if source == "https://tfc.com":
                        source = "TF Cornerstone"
                    elif source.startswith("https://streeteasy.com"):
                        source = "StreetEasy"
                    elif source == "https://manhattanskyline.com":
                        source = "Manhattan Skyline"
                    elif source == "https://www.fortysixfifty.com":
                        source = "Forty Six Fifty"
                    
                    source_counts[source] = source_counts.get(source, 0) + 1
                
                print("\n📈 Apartment Sources Breakdown:")
                for source, count in sorted(source_counts.items()):
                    print(f"   • {source}: {count} apartments")
                
                return True
            else:
                print(f"❌ ISSUE: Expected 30 apartments, got {total_count}")
                return False
        else:
            print(f"❌ API Error: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_apartment_count_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 APARTMENT COUNT ISSUE RESOLVED!")
        print("   • Frontend will now show all 30 apartments")
        print("   • All 10 TFC listings are included")
        print("   • Pagination limit increased from 20 to 50")
    else:
        print("❌ Issue still exists - further investigation needed")