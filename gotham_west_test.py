#!/usr/bin/env python3
"""
Gotham West Apartments Verification Test
Tests the addition of 10 new Gotham West apartments as requested
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://buildingtracker-1.preview.emergentagent.com/api"

class GothamWestTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
    
    def make_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_gotham_west_apartments_verification(self):
        """Test the addition of 10 new Gotham West apartments as requested"""
        print("\n🏢 GOTHAM WEST APARTMENTS VERIFICATION")
        print("=" * 60)
        try:
            # First, trigger the scraping endpoint to ensure all data is populated
            print("Triggering scraping endpoint to ensure all data is populated...")
            scrape_response = self.make_request("POST", "/admin/scrape")
            if scrape_response.status_code == 200:
                scrape_data = scrape_response.json()
                self.log_result("Gotham West Scraping Setup", True, f"Scraping completed: {scrape_data.get('message', 'Success')}")
            else:
                self.log_result("Gotham West Scraping Setup", False, f"Scraping failed with status: {scrape_response.status_code}")
                return
            
            # Wait a moment for database updates
            time.sleep(2)
            
            # Test 1: Check total apartment count (should be around 92+ apartments)
            response = self.make_request("GET", "/apartments")
            if response.status_code != 200:
                self.log_result("Total Apartment Count Check", False, f"Failed to get apartments: {response.status_code}")
                return
            
            apartments = response.json()
            total_count = len(apartments)
            
            if total_count >= 92:
                self.log_result("Total Apartment Count (92+)", True, f"Confirmed {total_count} total apartments (expected 92+)")
            else:
                self.log_result("Total Apartment Count (92+)", False, f"Expected 92+ apartments, found {total_count}")
            
            # Test 2: Search for "Gotham West" apartments specifically
            response = self.make_request("GET", "/apartments", {"search_term": "Gotham West"})
            if response.status_code == 200:
                gotham_west_apartments = response.json()
                gotham_west_count = len(gotham_west_apartments)
                
                if gotham_west_count >= 10:
                    self.log_result("Gotham West Search Results", True, f"Found {gotham_west_count} Gotham West apartments")
                else:
                    self.log_result("Gotham West Search Results", False, f"Expected at least 10 Gotham West apartments, found {gotham_west_count}")
                
                # Test 3: Check that Gotham West apartments have proper data structure
                if gotham_west_apartments:
                    required_fields = ["id", "title", "address", "price", "bedrooms", "bathrooms", "sqft", "neighborhood", "borough", "description", "amenities", "images", "contact_info"]
                    data_quality_issues = []
                    
                    for apt in gotham_west_apartments:
                        for field in required_fields:
                            if field not in apt or apt[field] is None:
                                if field == "bedrooms" and apt.get(field) == 0:  # Allow 0 bedrooms for studios
                                    continue
                                data_quality_issues.append(f"Missing {field} in apartment: {apt.get('title', 'Unknown')}")
                    
                    if not data_quality_issues:
                        self.log_result("Gotham West Data Structure", True, f"All {gotham_west_count} Gotham West apartments have proper data structure")
                    else:
                        self.log_result("Gotham West Data Structure", False, f"Data structure issues: {len(data_quality_issues)} problems found")
                        # Print first few issues for debugging
                        for issue in data_quality_issues[:3]:
                            print(f"   • {issue}")
                
                # Print details of found Gotham West apartments
                print(f"\n   📋 GOTHAM WEST APARTMENTS FOUND:")
                for i, apt in enumerate(gotham_west_apartments[:10], 1):  # Show first 10
                    print(f"   {i}. {apt.get('title', 'Unknown')} - ${apt.get('price', 0):,} ({apt.get('bedrooms', 0)}BR/{apt.get('bathrooms', 0)}BA)")
                    print(f"      📍 {apt.get('address', 'Unknown address')}")
                    print(f"      🏘️  {apt.get('neighborhood', 'Unknown')}, {apt.get('borough', 'Unknown')}")
                
            else:
                self.log_result("Gotham West Search Results", False, f"Search failed with status: {response.status_code}")
                gotham_west_apartments = []
            
            # Test 4: Verify Waterline Square apartments are still positioned at the bottom
            response = self.make_request("GET", "/apartments", {"search_term": "Waterline Square"})
            if response.status_code == 200:
                waterline_apartments = response.json()
                waterline_count = len(waterline_apartments)
                
                if waterline_count >= 8:
                    self.log_result("Waterline Square Apartments", True, f"Found {waterline_count} Waterline Square apartments still accessible")
                    
                    # Check if they appear at the bottom of the full listing
                    all_apartments_response = self.make_request("GET", "/apartments")
                    if all_apartments_response.status_code == 200:
                        all_apartments = all_apartments_response.json()
                        
                        # Find positions of Waterline apartments in the full list
                        waterline_positions = []
                        for i, apt in enumerate(all_apartments):
                            if "Waterline Square" in apt.get("title", "") or "400 West 61st St" in apt.get("address", ""):
                                waterline_positions.append(i)
                        
                        if waterline_positions:
                            avg_position = sum(waterline_positions) / len(waterline_positions)
                            total_apartments = len(all_apartments)
                            
                            # Check if average position is in the bottom half
                            if avg_position > total_apartments * 0.5:
                                self.log_result("Waterline Square Positioning", True, f"Waterline apartments positioned in bottom half (avg position: {avg_position:.1f}/{total_apartments})")
                            else:
                                self.log_result("Waterline Square Positioning", False, f"Waterline apartments not at bottom (avg position: {avg_position:.1f}/{total_apartments})")
                        else:
                            self.log_result("Waterline Square Positioning", False, "Could not find Waterline apartments in full listing")
                    else:
                        self.log_result("Waterline Square Positioning", False, "Could not retrieve full apartment listing")
                else:
                    self.log_result("Waterline Square Apartments", False, f"Expected at least 8 Waterline Square apartments, found {waterline_count}")
            else:
                self.log_result("Waterline Square Apartments", False, f"Waterline search failed with status: {response.status_code}")
            
            # Test 5: Confirm Gotham West apartments are scattered throughout listings (not grouped together)
            if gotham_west_apartments:
                all_apartments_response = self.make_request("GET", "/apartments")
                if all_apartments_response.status_code == 200:
                    all_apartments = all_apartments_response.json()
                    
                    # Find positions of Gotham West apartments in the full list
                    gotham_positions = []
                    for i, apt in enumerate(all_apartments):
                        if "Gotham West" in apt.get("title", ""):
                            gotham_positions.append(i)
                    
                    if len(gotham_positions) >= 5:  # Need at least 5 to check distribution
                        # Check if apartments are scattered (not consecutive)
                        consecutive_count = 0
                        max_consecutive = 0
                        
                        for i in range(1, len(gotham_positions)):
                            if gotham_positions[i] - gotham_positions[i-1] == 1:
                                consecutive_count += 1
                            else:
                                max_consecutive = max(max_consecutive, consecutive_count)
                                consecutive_count = 0
                        max_consecutive = max(max_consecutive, consecutive_count)
                        
                        # If no more than 2 consecutive apartments, they're well distributed
                        if max_consecutive <= 2:
                            self.log_result("Gotham West Distribution", True, f"Gotham West apartments are well scattered (max {max_consecutive + 1} consecutive)")
                        else:
                            self.log_result("Gotham West Distribution", False, f"Gotham West apartments may be grouped together (max {max_consecutive + 1} consecutive)")
                        
                        # Show distribution
                        print(f"   📊 Gotham West apartment positions: {gotham_positions[:10]}")  # Show first 10 positions
                    else:
                        self.log_result("Gotham West Distribution", False, f"Not enough Gotham West apartments found to check distribution ({len(gotham_positions)})")
                else:
                    self.log_result("Gotham West Distribution", False, "Could not retrieve full apartment listing for distribution check")
            
            # Test 6: Verify contact information is standardized
            if gotham_west_apartments:
                contact_issues = []
                expected_phone = "(646) 408-8048"
                expected_broker = "Chris Trunell"
                
                for apt in gotham_west_apartments:
                    contact_info = apt.get("contact_info", {})
                    title = apt.get("title", "Unknown")
                    
                    if contact_info.get("phone") != expected_phone:
                        contact_issues.append(f"Wrong phone in '{title}': {contact_info.get('phone')}")
                    if contact_info.get("broker") != expected_broker:
                        contact_issues.append(f"Wrong broker in '{title}': {contact_info.get('broker')}")
                
                if not contact_issues:
                    self.log_result("Gotham West Contact Info", True, f"All {len(gotham_west_apartments)} Gotham West apartments have proper contact info")
                else:
                    self.log_result("Gotham West Contact Info", False, f"Contact info issues: {len(contact_issues)} problems")
            
            # Print comprehensive summary
            print(f"\n   📊 GOTHAM WEST VERIFICATION SUMMARY:")
            print(f"   • Total Apartments in Database: {total_count}")
            print(f"   • Gotham West Apartments Found: {len(gotham_west_apartments) if 'gotham_west_apartments' in locals() else 0}")
            print(f"   • Waterline Square Apartments: {waterline_count if 'waterline_count' in locals() else 'Not checked'}")
            print(f"   • Data Quality: {'✅ Good' if not data_quality_issues else '❌ Issues found'}")
            print(f"   • Distribution: {'✅ Scattered' if 'gotham_positions' in locals() and len(gotham_positions) > 0 else '❓ Unknown'}")
            
        except Exception as e:
            self.log_result("Gotham West Apartments Verification", False, f"Exception: {str(e)}")
    
    def run_test(self):
        """Run the Gotham West verification test"""
        print("🏢 Gotham West Apartments Verification Test")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        self.test_gotham_west_apartments_verification()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['passed'] + self.results['failed']}")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100 if (self.results['passed'] + self.results['failed']) > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        return self.results

if __name__ == "__main__":
    tester = GothamWestTester()
    tester.run_test()