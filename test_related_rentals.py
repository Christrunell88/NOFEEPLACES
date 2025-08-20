#!/usr/bin/env python3
"""
Related Rentals Scraping Integration Tests
Tests the newly added Related Rentals functionality for PLACES No Fee platform
"""

import sys
sys.path.append('/app')
from backend_test import NoFeePlacesAPITester

def main():
    print("🏢 Testing Related Rentals Scraping Integration")
    print("=" * 60)
    
    tester = NoFeePlacesAPITester()
    
    # Authenticate first
    tester.test_user_registration()
    tester.test_user_login()
    
    # Run Related Rentals specific tests
    tester.test_related_rentals_scraping_integration()
    tester.test_related_rentals_integration_with_existing_system()
    tester.test_related_rentals_specific_price_points()
    
    # Print results
    print("\n" + "=" * 60)
    print("🏁 RELATED RENTALS TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {tester.results['passed']}")
    print(f"❌ Failed: {tester.results['failed']}")
    print(f"📊 Total: {tester.results['passed'] + tester.results['failed']}")
    
    if tester.results['errors']:
        print("\n🔍 FAILED TESTS:")
        for error in tester.results['errors']:
            print(f"   • {error}")
    
    success_rate = (tester.results['passed'] / (tester.results['passed'] + tester.results['failed'])) * 100 if (tester.results['passed'] + tester.results['failed']) > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")

if __name__ == "__main__":
    main()