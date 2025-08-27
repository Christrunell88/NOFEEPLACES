#!/usr/bin/env python3
"""
Gotham West Apartments Field Mapping Test
Tests the specific field mapping fixes mentioned in the review request
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://nyc-rental-platform.preview.emergentagent.com/api"

class GothamWestFieldMappingTester:
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
    
    def test_apartments_api_basic_functionality(self):
        """Test that GET /api/apartments returns apartments with proper field structure"""
        print("\n=== Testing Basic Apartments API Functionality ===")
        try:
            response = self.make_request("GET", "/apartments")
            
            if response.status_code == 200:
                apartments = response.json()
                if isinstance(apartments, list) and len(apartments) > 0:
                    self.log_result("GET /api/apartments Basic", True, f"Retrieved {len(apartments)} apartments")
                    
                    # Check first apartment has expected fields
                    first_apt = apartments[0]
                    expected_fields = ["id", "title", "address", "price", "bedrooms", "bathrooms", "sqft", "neighborhood", "borough"]
                    missing_fields = []
                    
                    for field in expected_fields:
                        if field not in first_apt:
                            missing_fields.append(field)
                    
                    if not missing_fields:
                        self.log_result("Apartment Data Structure", True, "All expected fields present in apartment data")
                    else:
                        self.log_result("Apartment Data Structure", False, f"Missing fields: {missing_fields}")
                    
                    return apartments
                else:
                    self.log_result("GET /api/apartments Basic", False, f"Expected list with apartments, got: {type(apartments)} with {len(apartments) if isinstance(apartments, list) else 'N/A'} items")
                    return []
            else:
                self.log_result("GET /api/apartments Basic", False, f"Status code: {response.status_code}, Response: {response.text[:200]}")
                return []
        except Exception as e:
            self.log_result("GET /api/apartments Basic", False, f"Exception: {str(e)}")
            return []
    
    def test_gotham_west_search_functionality(self):
        """Test search for 'Gotham West' apartments"""
        print("\n=== Testing Gotham West Search Functionality ===")
        try:
            # Test search for "Gotham West"
            response = self.make_request("GET", "/apartments", {"search_term": "Gotham West"})
            
            if response.status_code == 200:
                gotham_apartments = response.json()
                gotham_count = len(gotham_apartments)
                
                if gotham_count >= 10:
                    self.log_result("Gotham West Search Results", True, f"Found {gotham_count} Gotham West apartments")
                    
                    # Check that results actually contain "Gotham West" in title or address
                    valid_results = 0
                    for apt in gotham_apartments:
                        title = apt.get("title", "").lower()
                        address = apt.get("address", "").lower()
                        if "gotham west" in title or "gotham west" in address:
                            valid_results += 1
                    
                    if valid_results >= 10:
                        self.log_result("Gotham West Search Relevance", True, f"{valid_results} results actually contain 'Gotham West'")
                    else:
                        self.log_result("Gotham West Search Relevance", False, f"Only {valid_results} results actually contain 'Gotham West'")
                    
                    return gotham_apartments
                elif gotham_count > 0:
                    self.log_result("Gotham West Search Results", False, f"Found only {gotham_count} Gotham West apartments, expected at least 10")
                    return gotham_apartments
                else:
                    self.log_result("Gotham West Search Results", False, "No Gotham West apartments found - they may not be implemented yet")
                    return []
            else:
                self.log_result("Gotham West Search Results", False, f"Search failed with status: {response.status_code}")
                return []
        except Exception as e:
            self.log_result("Gotham West Search Functionality", False, f"Exception: {str(e)}")
            return []
    
    def test_hells_kitchen_search_functionality(self):
        """Test search for 'Hell's Kitchen' to confirm general search functionality"""
        print("\n=== Testing Hell's Kitchen Search Functionality ===")
        try:
            # Test search for "Hell's Kitchen"
            response = self.make_request("GET", "/apartments", {"search_term": "Hell's Kitchen"})
            
            if response.status_code == 200:
                hells_kitchen_apartments = response.json()
                hk_count = len(hells_kitchen_apartments)
                
                if hk_count > 0:
                    self.log_result("Hell's Kitchen Search Results", True, f"Found {hk_count} Hell's Kitchen apartments")
                    
                    # Check that results are relevant
                    valid_results = 0
                    for apt in hells_kitchen_apartments:
                        title = apt.get("title", "").lower()
                        address = apt.get("address", "").lower()
                        neighborhood = apt.get("neighborhood", "").lower()
                        description = apt.get("description", "").lower()
                        
                        if any(term in text for term in ["hell's kitchen", "hells kitchen", "midtown west"] 
                               for text in [title, address, neighborhood, description]):
                            valid_results += 1
                    
                    if valid_results > 0:
                        self.log_result("Hell's Kitchen Search Relevance", True, f"{valid_results}/{hk_count} results are relevant to Hell's Kitchen")
                    else:
                        self.log_result("Hell's Kitchen Search Relevance", False, "No relevant Hell's Kitchen results found")
                    
                    return hells_kitchen_apartments
                else:
                    self.log_result("Hell's Kitchen Search Results", False, "No Hell's Kitchen apartments found")
                    return []
            else:
                self.log_result("Hell's Kitchen Search Results", False, f"Search failed with status: {response.status_code}")
                return []
        except Exception as e:
            self.log_result("Hell's Kitchen Search Functionality", False, f"Exception: {str(e)}")
            return []
    
    def test_field_mapping_fixes(self):
        """Test the specific field mapping fixes mentioned in the review request"""
        print("\n=== Testing Field Mapping Fixes ===")
        try:
            # Get all apartments to check field mappings
            response = self.make_request("GET", "/apartments")
            
            if response.status_code != 200:
                self.log_result("Field Mapping Test Setup", False, f"Failed to get apartments: {response.status_code}")
                return
            
            apartments = response.json()
            
            # Test 1: Check that apartments have "no_fee" field (not "is_no_fee")
            no_fee_field_issues = []
            is_no_fee_field_found = []
            
            for apt in apartments:
                title = apt.get("title", "Unknown")
                
                # Check if apartment has the old "is_no_fee" field
                if "is_no_fee" in apt:
                    is_no_fee_field_found.append(title)
                
                # Check if apartment has proper "no_fee" field or equivalent
                if "no_fee" not in apt and "is_no_fee" not in apt:
                    no_fee_field_issues.append(title)
            
            if not is_no_fee_field_found:
                self.log_result("No Fee Field Mapping", True, "No apartments using old 'is_no_fee' field")
            else:
                self.log_result("No Fee Field Mapping", False, f"{len(is_no_fee_field_found)} apartments still using 'is_no_fee' field")
            
            # Test 2: Check that apartments have "address" field (not "location")
            address_field_issues = []
            location_field_found = []
            
            for apt in apartments:
                title = apt.get("title", "Unknown")
                
                # Check if apartment has "location" field instead of "address"
                if "location" in apt and "address" not in apt:
                    location_field_found.append(title)
                
                # Check if apartment is missing address field
                if "address" not in apt:
                    address_field_issues.append(title)
            
            if not address_field_issues:
                self.log_result("Address Field Mapping", True, "All apartments have 'address' field")
            else:
                self.log_result("Address Field Mapping", False, f"{len(address_field_issues)} apartments missing 'address' field")
            
            if not location_field_found:
                self.log_result("Location Field Check", True, "No apartments using 'location' field instead of 'address'")
            else:
                self.log_result("Location Field Check", False, f"{len(location_field_found)} apartments using 'location' field")
            
            # Test 3: Check that apartments have "sqft" field (not "square_feet")
            sqft_field_issues = []
            square_feet_field_found = []
            
            for apt in apartments:
                title = apt.get("title", "Unknown")
                
                # Check if apartment has "square_feet" field instead of "sqft"
                if "square_feet" in apt and "sqft" not in apt:
                    square_feet_field_found.append(title)
                
                # Check if apartment is missing sqft field
                if "sqft" not in apt:
                    sqft_field_issues.append(title)
            
            if not sqft_field_issues:
                self.log_result("Square Feet Field Mapping", True, "All apartments have 'sqft' field")
            else:
                self.log_result("Square Feet Field Mapping", False, f"{len(sqft_field_issues)} apartments missing 'sqft' field")
            
            if not square_feet_field_found:
                self.log_result("Square Feet Field Check", True, "No apartments using 'square_feet' field instead of 'sqft'")
            else:
                self.log_result("Square Feet Field Check", False, f"{len(square_feet_field_found)} apartments using 'square_feet' field")
            
            # Test 4: Test filtering functionality with correct field names
            print("\n--- Testing Filtering with Correct Field Names ---")
            
            # Test no_fee filtering (should work with apartments having no_fee: True)
            response = self.make_request("GET", "/apartments", {"no_fee": True})
            if response.status_code == 200:
                no_fee_results = response.json()
                self.log_result("No Fee Filtering", True, f"No fee filter returned {len(no_fee_results)} apartments")
            else:
                self.log_result("No Fee Filtering", False, f"No fee filter failed: {response.status_code}")
            
            # Test sqft filtering (should work with apartments having sqft field)
            response = self.make_request("GET", "/apartments", {"min_sqft": 500, "max_sqft": 1000})
            if response.status_code == 200:
                sqft_results = response.json()
                self.log_result("Square Feet Filtering", True, f"Sqft filter returned {len(sqft_results)} apartments")
                
                # Verify results are within range
                out_of_range = []
                for apt in sqft_results:
                    sqft = apt.get("sqft", 0)
                    if sqft < 500 or sqft > 1000:
                        out_of_range.append(f"{apt.get('title', 'Unknown')}: {sqft} sqft")
                
                if not out_of_range:
                    self.log_result("Square Feet Filter Accuracy", True, "All results within 500-1000 sqft range")
                else:
                    self.log_result("Square Feet Filter Accuracy", False, f"{len(out_of_range)} results out of range")
            else:
                self.log_result("Square Feet Filtering", False, f"Sqft filter failed: {response.status_code}")
            
        except Exception as e:
            self.log_result("Field Mapping Fixes", False, f"Exception: {str(e)}")
    
    def test_backend_field_mapping_issues(self):
        """Test specific backend field mapping issues found in server.py"""
        print("\n=== Testing Backend Field Mapping Issues ===")
        try:
            # Test 1: Check if sqft filtering works (backend should use 'sqft' not 'square_feet')
            response = self.make_request("GET", "/apartments", {"min_sqft": 600, "max_sqft": 800})
            if response.status_code == 200:
                sqft_results = response.json()
                
                # Check if any results were returned
                if len(sqft_results) > 0:
                    # Verify the results actually match the sqft criteria
                    valid_results = 0
                    for apt in sqft_results:
                        sqft = apt.get("sqft", 0)
                        if 600 <= sqft <= 800:
                            valid_results += 1
                    
                    if valid_results == len(sqft_results):
                        self.log_result("Backend Sqft Filtering Logic", True, f"Sqft filter working correctly: {valid_results} valid results")
                    else:
                        self.log_result("Backend Sqft Filtering Logic", False, f"Sqft filter issue: {valid_results}/{len(sqft_results)} results match criteria")
                else:
                    # Check if there should be results in this range
                    all_response = self.make_request("GET", "/apartments")
                    if all_response.status_code == 200:
                        all_apartments = all_response.json()
                        expected_results = [apt for apt in all_apartments if 600 <= apt.get("sqft", 0) <= 800]
                        
                        if len(expected_results) > 0:
                            self.log_result("Backend Sqft Filtering Logic", False, f"Sqft filter returned 0 results but {len(expected_results)} apartments match criteria - backend may be using 'square_feet' field")
                        else:
                            self.log_result("Backend Sqft Filtering Logic", True, "Sqft filter correctly returned 0 results (no apartments in range)")
            else:
                self.log_result("Backend Sqft Filtering Logic", False, f"Sqft filter request failed: {response.status_code}")
            
            # Test 2: Check if search works with address field (backend should search 'address' not 'location')
            response = self.make_request("GET", "/apartments", {"search_term": "Greenwich St"})
            if response.status_code == 200:
                search_results = response.json()
                
                # Check if results contain the search term in address
                address_matches = 0
                for apt in search_results:
                    address = apt.get("address", "").lower()
                    if "greenwich st" in address:
                        address_matches += 1
                
                if len(search_results) > 0 and address_matches > 0:
                    self.log_result("Backend Address Search Logic", True, f"Address search working: found {address_matches} matches")
                elif len(search_results) == 0:
                    # Check if there should be results
                    all_response = self.make_request("GET", "/apartments")
                    if all_response.status_code == 200:
                        all_apartments = all_response.json()
                        expected_results = [apt for apt in all_apartments if "greenwich st" in apt.get("address", "").lower()]
                        
                        if len(expected_results) > 0:
                            self.log_result("Backend Address Search Logic", False, f"Address search returned 0 results but {len(expected_results)} apartments match - backend may be searching 'location' field")
                        else:
                            self.log_result("Backend Address Search Logic", True, "Address search correctly returned 0 results (no matches)")
                else:
                    self.log_result("Backend Address Search Logic", False, f"Address search returned {len(search_results)} results but none match address field")
            else:
                self.log_result("Backend Address Search Logic", False, f"Address search request failed: {response.status_code}")
            
            # Test 3: Check statistics endpoint (should handle both is_no_fee and no_fee fields)
            response = self.make_request("GET", "/apartments/search/stats")
            if response.status_code == 200:
                stats = response.json()
                total_from_stats = stats.get("total_apartments", 0)
                
                # Get actual apartment count
                all_response = self.make_request("GET", "/apartments", {"limit": 100})
                if all_response.status_code == 200:
                    all_apartments = all_response.json()
                    actual_count = len(all_apartments)
                    
                    if total_from_stats == actual_count:
                        self.log_result("Backend Stats Field Logic", True, f"Stats endpoint correctly counts {total_from_stats} apartments")
                    else:
                        self.log_result("Backend Stats Field Logic", False, f"Stats endpoint shows {total_from_stats} but actual count is {actual_count} - may be using wrong field filter")
                else:
                    self.log_result("Backend Stats Field Logic", False, "Could not get apartments for comparison")
            else:
                self.log_result("Backend Stats Field Logic", False, f"Stats endpoint failed: {response.status_code}")
            
        except Exception as e:
            self.log_result("Backend Field Mapping Issues", False, f"Exception: {str(e)}")
    
    def test_apartment_distribution(self):
        """Test that apartments are properly distributed and not all grouped together"""
        print("\n=== Testing Apartment Distribution ===")
        try:
            response = self.make_request("GET", "/apartments")
            
            if response.status_code != 200:
                self.log_result("Apartment Distribution Test", False, f"Failed to get apartments: {response.status_code}")
                return
            
            apartments = response.json()
            
            if len(apartments) < 10:
                self.log_result("Apartment Distribution Test", False, f"Not enough apartments to test distribution: {len(apartments)}")
                return
            
            # Check price distribution
            prices = [apt.get("price", 0) for apt in apartments if apt.get("price")]
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                price_range = max_price - min_price
                
                if price_range > 1000:  # Good price diversity
                    self.log_result("Price Distribution", True, f"Good price range: ${min_price:,} - ${max_price:,}")
                else:
                    self.log_result("Price Distribution", False, f"Limited price range: ${min_price:,} - ${max_price:,}")
            
            # Check neighborhood distribution
            neighborhoods = [apt.get("neighborhood", "") for apt in apartments if apt.get("neighborhood")]
            unique_neighborhoods = set(neighborhoods)
            
            if len(unique_neighborhoods) >= 5:
                self.log_result("Neighborhood Distribution", True, f"Good neighborhood diversity: {len(unique_neighborhoods)} neighborhoods")
            else:
                self.log_result("Neighborhood Distribution", False, f"Limited neighborhood diversity: {len(unique_neighborhoods)} neighborhoods")
            
            # Check borough distribution
            boroughs = [apt.get("borough", "") for apt in apartments if apt.get("borough")]
            unique_boroughs = set(boroughs)
            
            if len(unique_boroughs) >= 2:
                self.log_result("Borough Distribution", True, f"Multi-borough coverage: {', '.join(unique_boroughs)}")
            else:
                self.log_result("Borough Distribution", False, f"Limited borough coverage: {', '.join(unique_boroughs)}")
            
        except Exception as e:
            self.log_result("Apartment Distribution", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all field mapping and Gotham West tests"""
        print("🏢 GOTHAM WEST APARTMENTS FIELD MAPPING TEST")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run tests in order
        apartments = self.test_apartments_api_basic_functionality()
        gotham_apartments = self.test_gotham_west_search_functionality()
        hk_apartments = self.test_hells_kitchen_search_functionality()
        self.test_field_mapping_fixes()
        self.test_backend_field_mapping_issues()
        self.test_apartment_distribution()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 FIELD MAPPING TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['passed'] + self.results['failed']}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100 if (self.results['passed'] + self.results['failed']) > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n❌ Errors Found:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return self.results

if __name__ == "__main__":
    tester = GothamWestFieldMappingTester()
    results = tester.run_all_tests()