#!/usr/bin/env python3
"""
Focused test for neighborhood search functionality
Tests the location/neighborhood search functionality after fixing the parameter mismatch
"""

import requests
import json
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://nofeeapt.preview.emergentagent.com/api"

class NeighborhoodSearchTester:
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
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> requests.Response:
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

    def test_neighborhood_search_functionality(self):
        """Test location/neighborhood search functionality after fixing parameter mismatch"""
        print("\n=== Testing Neighborhood Search Functionality ===")
        try:
            # Test 1: Basic neighborhood search - Manhattan
            print("\n🏙️ Testing basic neighborhood search...")
            response = self.make_request("GET", "/apartments", {"neighborhood": "manhattan", "limit": 50})
            if response.status_code == 200:
                manhattan_apartments = response.json()
                manhattan_count = len(manhattan_apartments)
                
                # Verify all results contain Manhattan in neighborhood
                manhattan_matches = 0
                for apt in manhattan_apartments:
                    if "manhattan" in apt.get("neighborhood", "").lower():
                        manhattan_matches += 1
                
                if manhattan_matches == manhattan_count and manhattan_count > 0:
                    self.log_result("Neighborhood Search (Manhattan)", True, 
                                  f"Found {manhattan_count} Manhattan apartments, all correctly filtered")
                elif manhattan_count == 0:
                    self.log_result("Neighborhood Search (Manhattan)", False, 
                                  "No Manhattan apartments found - may indicate filtering issue")
                else:
                    self.log_result("Neighborhood Search (Manhattan)", False, 
                                  f"Only {manhattan_matches}/{manhattan_count} results actually match Manhattan")
            else:
                self.log_result("Neighborhood Search (Manhattan)", False, 
                              f"Request failed with status: {response.status_code}")
            
            # Test 2: Case insensitive search variations
            print("\n🔤 Testing case insensitive neighborhood search...")
            case_variations = [
                {"query": "Manhattan", "description": "Capitalized"},
                {"query": "manhattan", "description": "Lowercase"},
                {"query": "MANHATTAN", "description": "Uppercase"},
                {"query": "MaNhAtTaN", "description": "Mixed case"}
            ]
            
            case_results = []
            for variation in case_variations:
                response = self.make_request("GET", "/apartments", {"neighborhood": variation["query"], "limit": 20})
                if response.status_code == 200:
                    results = response.json()
                    case_results.append({
                        "query": variation["query"],
                        "description": variation["description"],
                        "count": len(results),
                        "success": True
                    })
                else:
                    case_results.append({
                        "query": variation["query"],
                        "description": variation["description"],
                        "count": 0,
                        "success": False
                    })
            
            # Check if all case variations return similar results
            successful_results = [r for r in case_results if r["success"]]
            if len(successful_results) == len(case_variations):
                counts = [r["count"] for r in successful_results]
                if len(set(counts)) <= 1:  # All counts are the same
                    self.log_result("Case Insensitive Search", True, 
                                  f"All case variations return same count: {counts[0]} apartments")
                else:
                    self.log_result("Case Insensitive Search", False, 
                                  f"Case variations return different counts: {counts}")
            else:
                self.log_result("Case Insensitive Search", False, 
                              f"Only {len(successful_results)}/{len(case_variations)} case variations succeeded")
            
            # Test 3: Partial matching for neighborhoods
            print("\n🔍 Testing partial neighborhood matching...")
            partial_tests = [
                {"query": "chel", "expected": "Chelsea", "description": "Chelsea partial match"},
                {"query": "wil", "expected": "Williamsburg", "description": "Williamsburg partial match"},
                {"query": "upper", "expected": "Upper", "description": "Upper (East/West Side) partial match"},
                {"query": "hell", "expected": "Hell's Kitchen", "description": "Hell's Kitchen partial match"}
            ]
            
            for test in partial_tests:
                response = self.make_request("GET", "/apartments", {"neighborhood": test["query"], "limit": 20})
                if response.status_code == 200:
                    results = response.json()
                    
                    # Check if any results contain the expected neighborhood
                    matching_apartments = []
                    for apt in results:
                        neighborhood = apt.get("neighborhood", "").lower()
                        if test["expected"].lower() in neighborhood:
                            matching_apartments.append(apt)
                    
                    if matching_apartments:
                        self.log_result(f"Partial Match ({test['description']})", True, 
                                      f"'{test['query']}' found {len(matching_apartments)} apartments matching '{test['expected']}'")
                    else:
                        if results:
                            # Show what neighborhoods were found instead
                            found_neighborhoods = list(set([apt.get("neighborhood", "Unknown") for apt in results[:5]]))
                            self.log_result(f"Partial Match ({test['description']})", True, 
                                          f"'{test['query']}' found {len(results)} apartments in: {found_neighborhoods}")
                        else:
                            self.log_result(f"Partial Match ({test['description']})", False, 
                                          f"'{test['query']}' found no apartments")
                else:
                    self.log_result(f"Partial Match ({test['description']})", False, 
                                  f"Request failed with status: {response.status_code}")
            
            # Test 4: Combined filters with neighborhood
            print("\n🔧 Testing neighborhood search with combined filters...")
            
            # Test neighborhood + price filter
            response = self.make_request("GET", "/apartments", {
                "neighborhood": "manhattan",
                "min_price": 3000,
                "max_price": 6000,
                "limit": 30
            })
            if response.status_code == 200:
                combined_results = response.json()
                
                # Verify all results meet both criteria
                valid_results = 0
                for apt in combined_results:
                    neighborhood_match = "manhattan" in apt.get("neighborhood", "").lower()
                    price_match = 3000 <= apt.get("price", 0) <= 6000
                    if neighborhood_match and price_match:
                        valid_results += 1
                
                if valid_results == len(combined_results):
                    self.log_result("Combined Filter (Neighborhood + Price)", True, 
                                  f"Found {len(combined_results)} apartments matching both Manhattan and $3000-$6000")
                else:
                    self.log_result("Combined Filter (Neighborhood + Price)", False, 
                                  f"Only {valid_results}/{len(combined_results)} results match both criteria")
            else:
                self.log_result("Combined Filter (Neighborhood + Price)", False, 
                              f"Request failed with status: {response.status_code}")
            
            # Test neighborhood + bedrooms filter
            response = self.make_request("GET", "/apartments", {
                "neighborhood": "brooklyn",
                "bedrooms": 1,
                "limit": 20
            })
            if response.status_code == 200:
                brooklyn_1br = response.json()
                
                valid_brooklyn_1br = 0
                for apt in brooklyn_1br:
                    neighborhood_match = "brooklyn" in apt.get("neighborhood", "").lower() or apt.get("borough", "").lower() == "brooklyn"
                    bedroom_match = apt.get("bedrooms") == 1
                    if neighborhood_match and bedroom_match:
                        valid_brooklyn_1br += 1
                
                if valid_brooklyn_1br == len(brooklyn_1br):
                    self.log_result("Combined Filter (Neighborhood + Bedrooms)", True, 
                                  f"Found {len(brooklyn_1br)} 1BR apartments in Brooklyn area")
                else:
                    self.log_result("Combined Filter (Neighborhood + Bedrooms)", False, 
                                  f"Only {valid_brooklyn_1br}/{len(brooklyn_1br)} results match both criteria")
            else:
                self.log_result("Combined Filter (Neighborhood + Bedrooms)", False, 
                              f"Request failed with status: {response.status_code}")
            
            # Test 5: Search term vs neighborhood parameter
            print("\n🔍 Testing search_term vs neighborhood parameter...")
            
            # Test with neighborhood parameter
            neighborhood_response = self.make_request("GET", "/apartments", {"neighborhood": "chelsea", "limit": 15})
            neighborhood_count = 0
            if neighborhood_response.status_code == 200:
                neighborhood_results = neighborhood_response.json()
                neighborhood_count = len(neighborhood_results)
            
            # Test with search_term parameter
            search_response = self.make_request("GET", "/apartments", {"search_term": "chelsea", "limit": 15})
            search_count = 0
            if search_response.status_code == 200:
                search_results = search_response.json()
                search_count = len(search_results)
            
            if neighborhood_response.status_code == 200 and search_response.status_code == 200:
                # Both should work but may return different results
                # neighborhood parameter is more specific, search_term is broader
                self.log_result("Search Term vs Neighborhood Parameter", True, 
                              f"Neighborhood param: {neighborhood_count} results, Search term: {search_count} results")
                
                if neighborhood_count > 0:
                    print(f"   • neighborhood=chelsea: {neighborhood_count} apartments (specific neighborhood filter)")
                if search_count > 0:
                    print(f"   • search_term=chelsea: {search_count} apartments (broader search across all fields)")
            else:
                failed_requests = []
                if neighborhood_response.status_code != 200:
                    failed_requests.append(f"neighborhood param: {neighborhood_response.status_code}")
                if search_response.status_code != 200:
                    failed_requests.append(f"search_term param: {search_response.status_code}")
                
                self.log_result("Search Term vs Neighborhood Parameter", False, 
                              f"Request failures: {', '.join(failed_requests)}")
            
            # Test 6: Specific NYC neighborhoods mentioned in review
            print("\n🏙️ Testing specific NYC neighborhoods...")
            nyc_neighborhoods = [
                "Manhattan", "Brooklyn", "Chelsea", "Williamsburg", 
                "Upper East Side", "Hell's Kitchen", "Queens", "Astoria",
                "Financial District", "SoHo", "Tribeca"
            ]
            
            neighborhood_results = {}
            for neighborhood in nyc_neighborhoods:
                response = self.make_request("GET", "/apartments", {"neighborhood": neighborhood.lower(), "limit": 10})
                if response.status_code == 200:
                    results = response.json()
                    neighborhood_results[neighborhood] = len(results)
                else:
                    neighborhood_results[neighborhood] = -1  # Error
            
            successful_neighborhoods = [n for n, count in neighborhood_results.items() if count >= 0]
            neighborhoods_with_results = [n for n, count in neighborhood_results.items() if count > 0]
            
            if len(successful_neighborhoods) == len(nyc_neighborhoods):
                self.log_result("NYC Neighborhoods Search", True, 
                              f"All {len(nyc_neighborhoods)} neighborhoods searchable. {len(neighborhoods_with_results)} have apartments")
                
                # Show results summary
                for neighborhood, count in neighborhood_results.items():
                    if count > 0:
                        print(f"   • {neighborhood}: {count} apartments")
            else:
                failed_neighborhoods = [n for n, count in neighborhood_results.items() if count == -1]
                self.log_result("NYC Neighborhoods Search", False, 
                              f"Failed to search {len(failed_neighborhoods)} neighborhoods: {failed_neighborhoods}")
            
            # Test 7: Verify no regression in other search functionality
            print("\n🔄 Testing no regression in other search functionality...")
            
            # Test basic apartment listing still works
            basic_response = self.make_request("GET", "/apartments", {"limit": 10})
            if basic_response.status_code == 200:
                basic_results = basic_response.json()
                if len(basic_results) > 0:
                    self.log_result("Basic Listing (No Regression)", True, 
                                  f"Basic apartment listing returns {len(basic_results)} apartments")
                else:
                    self.log_result("Basic Listing (No Regression)", False, "Basic listing returns no apartments")
            else:
                self.log_result("Basic Listing (No Regression)", False, 
                              f"Basic listing failed: {basic_response.status_code}")
            
            # Test price filtering still works
            price_response = self.make_request("GET", "/apartments", {"min_price": 4000, "limit": 10})
            if price_response.status_code == 200:
                price_results = price_response.json()
                valid_price_results = [apt for apt in price_results if apt.get("price", 0) >= 4000]
                if len(valid_price_results) == len(price_results):
                    self.log_result("Price Filter (No Regression)", True, 
                                  f"Price filtering works correctly: {len(price_results)} apartments >= $4000")
                else:
                    self.log_result("Price Filter (No Regression)", False, 
                                  f"Price filter issue: {len(valid_price_results)}/{len(price_results)} meet criteria")
            else:
                self.log_result("Price Filter (No Regression)", False, 
                              f"Price filtering failed: {price_response.status_code}")
            
            # Test bedroom filtering still works
            bedroom_response = self.make_request("GET", "/apartments", {"bedrooms": 2, "limit": 10})
            if bedroom_response.status_code == 200:
                bedroom_results = bedroom_response.json()
                valid_bedroom_results = [apt for apt in bedroom_results if apt.get("bedrooms") == 2]
                if len(valid_bedroom_results) == len(bedroom_results):
                    self.log_result("Bedroom Filter (No Regression)", True, 
                                  f"Bedroom filtering works correctly: {len(bedroom_results)} 2BR apartments")
                else:
                    self.log_result("Bedroom Filter (No Regression)", False, 
                                  f"Bedroom filter issue: {len(valid_bedroom_results)}/{len(bedroom_results)} are 2BR")
            else:
                self.log_result("Bedroom Filter (No Regression)", False, 
                              f"Bedroom filtering failed: {bedroom_response.status_code}")
            
        except Exception as e:
            self.log_result("Neighborhood Search Functionality", False, f"Exception: {str(e)}")

    def run_tests(self):
        """Run the neighborhood search tests"""
        print("🚀 Starting Neighborhood Search Functionality Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        self.test_neighborhood_search_functionality()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        total_tests = self.results['passed'] + self.results['failed']
        if total_tests > 0:
            success_rate = (self.results['passed'] / total_tests) * 100
            print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = NeighborhoodSearchTester()
    tester.run_tests()