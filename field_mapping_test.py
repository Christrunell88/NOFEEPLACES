#!/usr/bin/env python3
"""
Field Mapping and Data Consistency Testing Suite
Tests the specific issues mentioned in the review request:
1. Square Footage Filtering Fix (sqft vs square_feet)
2. Apartment Counts and Data Integrity
3. Mock Data vs Real Data preservation
4. Search Functionality
5. API Field Consistency
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configuration
BASE_URL = "https://fee-free-homes.preview.emergentagent.com/api"

class FieldMappingTester:
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
    
    def test_square_footage_filtering_fix(self):
        """Test GET /api/apartments with min_sqft and max_sqft parameters to verify field mapping fix"""
        print("\n=== Testing Square Footage Filtering Fix ===")
        try:
            # Test 1: Basic sqft filtering with min_sqft
            response = self.make_request("GET", "/apartments", {"min_sqft": 500, "limit": 100})
            if response.status_code == 200:
                apartments = response.json()
                if apartments:
                    # Check that all returned apartments have sqft >= 500
                    valid_sqft = True
                    for apt in apartments:
                        sqft = apt.get("sqft", 0)
                        if sqft < 500:
                            valid_sqft = False
                            break
                    
                    if valid_sqft:
                        self.log_result("Min SQFT Filter (500+)", True, f"Found {len(apartments)} apartments with sqft >= 500")
                    else:
                        self.log_result("Min SQFT Filter (500+)", False, f"Some apartments have sqft < 500")
                else:
                    self.log_result("Min SQFT Filter (500+)", False, "No apartments returned for min_sqft=500")
            else:
                self.log_result("Min SQFT Filter (500+)", False, f"Status code: {response.status_code}")
            
            # Test 2: Basic sqft filtering with max_sqft
            response = self.make_request("GET", "/apartments", {"max_sqft": 800, "limit": 100})
            if response.status_code == 200:
                apartments = response.json()
                if apartments:
                    # Check that all returned apartments have sqft <= 800
                    valid_sqft = True
                    for apt in apartments:
                        sqft = apt.get("sqft", 0)
                        if sqft > 800:
                            valid_sqft = False
                            break
                    
                    if valid_sqft:
                        self.log_result("Max SQFT Filter (800-)", True, f"Found {len(apartments)} apartments with sqft <= 800")
                    else:
                        self.log_result("Max SQFT Filter (800-)", False, f"Some apartments have sqft > 800")
                else:
                    self.log_result("Max SQFT Filter (800-)", False, "No apartments returned for max_sqft=800")
            else:
                self.log_result("Max SQFT Filter (800-)", False, f"Status code: {response.status_code}")
            
            # Test 3: Range sqft filtering (min_sqft and max_sqft together)
            response = self.make_request("GET", "/apartments", {"min_sqft": 600, "max_sqft": 1000, "limit": 100})
            if response.status_code == 200:
                apartments = response.json()
                if apartments:
                    # Check that all returned apartments have 600 <= sqft <= 1000
                    valid_range = True
                    for apt in apartments:
                        sqft = apt.get("sqft", 0)
                        if sqft < 600 or sqft > 1000:
                            valid_range = False
                            break
                    
                    if valid_range:
                        self.log_result("SQFT Range Filter (600-1000)", True, f"Found {len(apartments)} apartments in 600-1000 sqft range")
                    else:
                        self.log_result("SQFT Range Filter (600-1000)", False, f"Some apartments outside 600-1000 sqft range")
                else:
                    self.log_result("SQFT Range Filter (600-1000)", False, "No apartments returned for sqft range 600-1000")
            else:
                self.log_result("SQFT Range Filter (600-1000)", False, f"Status code: {response.status_code}")
            
            # Test 4: Verify field mapping - check that apartments have 'sqft' field, not 'square_feet'
            response = self.make_request("GET", "/apartments", {"limit": 10})
            if response.status_code == 200:
                apartments = response.json()
                if apartments:
                    has_sqft_field = all("sqft" in apt for apt in apartments)
                    has_square_feet_field = any("square_feet" in apt for apt in apartments)
                    
                    if has_sqft_field and not has_square_feet_field:
                        self.log_result("Field Mapping Consistency", True, "All apartments use 'sqft' field, no 'square_feet' field found")
                    elif has_sqft_field and has_square_feet_field:
                        self.log_result("Field Mapping Consistency", True, "Apartments have both 'sqft' and 'square_feet' fields (backward compatibility)")
                    else:
                        self.log_result("Field Mapping Consistency", False, f"Field mapping issue: sqft={has_sqft_field}, square_feet={has_square_feet_field}")
                else:
                    self.log_result("Field Mapping Consistency", False, "No apartments returned to check field mapping")
            else:
                self.log_result("Field Mapping Consistency", False, f"Status code: {response.status_code}")
            
        except Exception as e:
            self.log_result("Square Footage Filtering Fix", False, f"Exception: {str(e)}")
    
    def test_apartment_counts_and_data_integrity(self):
        """Verify apartment counts are consistent and search results return proper apartments with complete data"""
        print("\n=== Testing Apartment Counts and Data Integrity ===")
        try:
            # Test 1: Get total apartment count
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code == 200:
                apartments = response.json()
                total_count = len(apartments)
                self.log_result("Total Apartment Count", True, f"Found {total_count} total apartments")
                
                # Test 2: Verify data integrity - all apartments have required fields
                required_fields = ["id", "title", "address", "price", "bedrooms", "bathrooms", "sqft", "neighborhood", "borough"]
                missing_fields_count = 0
                apartments_with_images = 0
                
                for apt in apartments:
                    for field in required_fields:
                        if field not in apt or apt[field] is None:
                            missing_fields_count += 1
                            break
                    
                    # Check image arrays
                    images = apt.get("images", [])
                    if images and len(images) > 0:
                        apartments_with_images += 1
                
                if missing_fields_count == 0:
                    self.log_result("Required Fields Integrity", True, f"All {total_count} apartments have required fields")
                else:
                    self.log_result("Required Fields Integrity", False, f"{missing_fields_count} apartments missing required fields")
                
                # Test 3: Image arrays integrity
                if apartments_with_images >= total_count * 0.9:  # At least 90% should have images
                    self.log_result("Image Arrays Integrity", True, f"{apartments_with_images}/{total_count} apartments have image arrays")
                else:
                    self.log_result("Image Arrays Integrity", False, f"Only {apartments_with_images}/{total_count} apartments have image arrays")
                
                # Test 4: Price range consistency
                prices = [apt.get("price", 0) for apt in apartments if apt.get("price")]
                if prices:
                    min_price = min(prices)
                    max_price = max(prices)
                    self.log_result("Price Range Consistency", True, f"Price range: ${min_price:,} - ${max_price:,}")
                else:
                    self.log_result("Price Range Consistency", False, "No price data found")
                
                # Test 5: Borough distribution
                boroughs = {}
                for apt in apartments:
                    borough = apt.get("borough", "Unknown")
                    boroughs[borough] = boroughs.get(borough, 0) + 1
                
                if len(boroughs) >= 3:  # Should have at least 3 boroughs
                    borough_list = ", ".join([f"{k}: {v}" for k, v in boroughs.items()])
                    self.log_result("Borough Distribution", True, f"Found {len(boroughs)} boroughs: {borough_list}")
                else:
                    self.log_result("Borough Distribution", False, f"Only {len(boroughs)} boroughs found: {boroughs}")
                
            else:
                self.log_result("Apartment Counts and Data Integrity", False, f"Status code: {response.status_code}")
            
        except Exception as e:
            self.log_result("Apartment Counts and Data Integrity", False, f"Exception: {str(e)}")
    
    def test_mock_data_vs_real_data_preservation(self):
        """Check if manually added apartments are preserved and not being overridden by mock data"""
        print("\n=== Testing Mock Data vs Real Data Preservation ===")
        try:
            # Get all apartments
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code == 200:
                apartments = response.json()
                
                # Test 1: Look for StreetEasy OP Commission apartments
                streeteasy_apartments = []
                for apt in apartments:
                    source_url = apt.get("source_url", "")
                    title = apt.get("title", "")
                    if "streeteasy.com" in source_url or "StreetEasy" in title or "Owner-Paid" in title:
                        streeteasy_apartments.append(apt)
                
                if streeteasy_apartments:
                    self.log_result("StreetEasy OP Commission Preservation", True, f"Found {len(streeteasy_apartments)} StreetEasy apartments preserved")
                else:
                    self.log_result("StreetEasy OP Commission Preservation", False, "No StreetEasy OP Commission apartments found")
                
                # Test 2: Look for Gotham West apartments
                gotham_west_apartments = []
                for apt in apartments:
                    title = apt.get("title", "")
                    address = apt.get("address", "")
                    if "Gotham West" in title or "550 West 45th" in address or "550 W 45th" in address:
                        gotham_west_apartments.append(apt)
                
                if gotham_west_apartments:
                    self.log_result("Gotham West Preservation", True, f"Found {len(gotham_west_apartments)} Gotham West apartments preserved")
                else:
                    self.log_result("Gotham West Preservation", False, "No Gotham West apartments found")
                
                # Test 3: Look for Waterline Square apartments
                waterline_apartments = []
                for apt in apartments:
                    title = apt.get("title", "")
                    address = apt.get("address", "")
                    if "Waterline" in title or "400 West 61st" in address or "400 W 61st" in address:
                        waterline_apartments.append(apt)
                
                if waterline_apartments:
                    self.log_result("Waterline Square Preservation", True, f"Found {len(waterline_apartments)} Waterline Square apartments preserved")
                else:
                    self.log_result("Waterline Square Preservation", False, "No Waterline Square apartments found")
                
                # Test 4: Look for Two Trees apartments
                two_trees_apartments = []
                for apt in apartments:
                    title = apt.get("title", "")
                    source = apt.get("source", "")
                    if "Two Trees" in title or "Two Trees" in source:
                        two_trees_apartments.append(apt)
                
                if two_trees_apartments:
                    self.log_result("Two Trees Preservation", True, f"Found {len(two_trees_apartments)} Two Trees apartments preserved")
                else:
                    self.log_result("Two Trees Preservation", False, "No Two Trees apartments found")
                
                # Test 5: Look for Mercedes House apartments
                mercedes_apartments = []
                for apt in apartments:
                    title = apt.get("title", "")
                    address = apt.get("address", "")
                    if "Mercedes House" in title or "Mercedes" in address:
                        mercedes_apartments.append(apt)
                
                if mercedes_apartments:
                    self.log_result("Mercedes House Preservation", True, f"Found {len(mercedes_apartments)} Mercedes House apartments preserved")
                else:
                    self.log_result("Mercedes House Preservation", False, "No Mercedes House apartments found")
                
                # Test 6: Check for source attribution to identify data sources
                source_distribution = {}
                for apt in apartments:
                    source_url = apt.get("source_url", "Unknown")
                    source_distribution[source_url] = source_distribution.get(source_url, 0) + 1
                
                source_list = ", ".join([f"{k}: {v}" for k, v in source_distribution.items()])
                self.log_result("Data Source Distribution", True, f"Sources found: {source_list}")
                
            else:
                self.log_result("Mock Data vs Real Data Preservation", False, f"Status code: {response.status_code}")
            
        except Exception as e:
            self.log_result("Mock Data vs Real Data Preservation", False, f"Exception: {str(e)}")
    
    def test_search_functionality_comprehensive(self):
        """Test search functionality with various terms to ensure all apartment types are discoverable"""
        print("\n=== Testing Search Functionality Comprehensive ===")
        try:
            # Test 1: Search for "luxury" - should return luxury apartments
            response = self.make_request("GET", "/apartments", {"search_term": "luxury", "limit": 100})
            if response.status_code == 200:
                luxury_results = response.json()
                if luxury_results:
                    self.log_result("Search: Luxury", True, f"Found {len(luxury_results)} apartments for 'luxury' search")
                else:
                    self.log_result("Search: Luxury", False, "No results for 'luxury' search")
            else:
                self.log_result("Search: Luxury", False, f"Status code: {response.status_code}")
            
            # Test 2: Search for "studio" - should return studio apartments
            response = self.make_request("GET", "/apartments", {"search_term": "studio", "limit": 100})
            if response.status_code == 200:
                studio_results = response.json()
                if studio_results:
                    self.log_result("Search: Studio", True, f"Found {len(studio_results)} apartments for 'studio' search")
                else:
                    self.log_result("Search: Studio", False, "No results for 'studio' search")
            else:
                self.log_result("Search: Studio", False, f"Status code: {response.status_code}")
            
            # Test 3: Search for "Manhattan" - should return Manhattan apartments
            response = self.make_request("GET", "/apartments", {"search_term": "Manhattan", "limit": 100})
            if response.status_code == 200:
                manhattan_results = response.json()
                if manhattan_results:
                    self.log_result("Search: Manhattan", True, f"Found {len(manhattan_results)} apartments for 'Manhattan' search")
                else:
                    self.log_result("Search: Manhattan", False, "No results for 'Manhattan' search")
            else:
                self.log_result("Search: Manhattan", False, f"Status code: {response.status_code}")
            
            # Test 4: Search for "Gotham West" - should return Gotham West apartments
            response = self.make_request("GET", "/apartments", {"search_term": "Gotham West", "limit": 100})
            if response.status_code == 200:
                gotham_results = response.json()
                if gotham_results:
                    self.log_result("Search: Gotham West", True, f"Found {len(gotham_results)} apartments for 'Gotham West' search")
                else:
                    self.log_result("Search: Gotham West", False, "No results for 'Gotham West' search")
            else:
                self.log_result("Search: Gotham West", False, f"Status code: {response.status_code}")
            
            # Test 5: Search for "Waterline" - should return Waterline Square apartments
            response = self.make_request("GET", "/apartments", {"search_term": "Waterline", "limit": 100})
            if response.status_code == 200:
                waterline_results = response.json()
                if waterline_results:
                    self.log_result("Search: Waterline", True, f"Found {len(waterline_results)} apartments for 'Waterline' search")
                else:
                    self.log_result("Search: Waterline", False, "No results for 'Waterline' search")
            else:
                self.log_result("Search: Waterline", False, f"Status code: {response.status_code}")
            
            # Test 6: Search for "no fee" - should return no-fee apartments
            response = self.make_request("GET", "/apartments", {"search_term": "no fee", "limit": 100})
            if response.status_code == 200:
                no_fee_results = response.json()
                if no_fee_results:
                    self.log_result("Search: No Fee", True, f"Found {len(no_fee_results)} apartments for 'no fee' search")
                else:
                    self.log_result("Search: No Fee", False, "No results for 'no fee' search")
            else:
                self.log_result("Search: No Fee", False, f"Status code: {response.status_code}")
            
            # Test 7: Search for neighborhood names
            neighborhoods = ["Chelsea", "Williamsburg", "Upper East Side", "Financial District"]
            for neighborhood in neighborhoods:
                response = self.make_request("GET", "/apartments", {"search_term": neighborhood, "limit": 100})
                if response.status_code == 200:
                    results = response.json()
                    if results:
                        self.log_result(f"Search: {neighborhood}", True, f"Found {len(results)} apartments for '{neighborhood}' search")
                    else:
                        self.log_result(f"Search: {neighborhood}", False, f"No results for '{neighborhood}' search")
                else:
                    self.log_result(f"Search: {neighborhood}", False, f"Status code: {response.status_code}")
            
        except Exception as e:
            self.log_result("Search Functionality Comprehensive", False, f"Exception: {str(e)}")
    
    def test_api_field_consistency(self):
        """Verify all apartments have consistent field structures"""
        print("\n=== Testing API Field Consistency ===")
        try:
            # Get all apartments
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code == 200:
                apartments = response.json()
                
                # Test 1: Check sqft vs square_feet field consistency
                sqft_field_count = 0
                square_feet_field_count = 0
                both_fields_count = 0
                
                for apt in apartments:
                    has_sqft = "sqft" in apt
                    has_square_feet = "square_feet" in apt
                    
                    if has_sqft and has_square_feet:
                        both_fields_count += 1
                    elif has_sqft:
                        sqft_field_count += 1
                    elif has_square_feet:
                        square_feet_field_count += 1
                
                if sqft_field_count > 0 or both_fields_count > 0:
                    self.log_result("SQFT Field Consistency", True, f"sqft: {sqft_field_count}, square_feet: {square_feet_field_count}, both: {both_fields_count}")
                else:
                    self.log_result("SQFT Field Consistency", False, f"No apartments with sqft field found")
                
                # Test 2: Check no_fee vs is_no_fee field consistency
                no_fee_field_count = 0
                is_no_fee_field_count = 0
                both_no_fee_fields_count = 0
                
                for apt in apartments:
                    has_no_fee = "no_fee" in apt
                    has_is_no_fee = "is_no_fee" in apt
                    
                    if has_no_fee and has_is_no_fee:
                        both_no_fee_fields_count += 1
                    elif has_no_fee:
                        no_fee_field_count += 1
                    elif has_is_no_fee:
                        is_no_fee_field_count += 1
                
                if no_fee_field_count > 0 or both_no_fee_fields_count > 0:
                    self.log_result("No Fee Field Consistency", True, f"no_fee: {no_fee_field_count}, is_no_fee: {is_no_fee_field_count}, both: {both_no_fee_fields_count}")
                else:
                    self.log_result("No Fee Field Consistency", False, f"No apartments with no_fee field found")
                
                # Test 3: Check required field presence across all apartments
                required_fields = ["id", "title", "address", "price", "bedrooms", "bathrooms", "neighborhood", "borough"]
                field_presence = {field: 0 for field in required_fields}
                
                for apt in apartments:
                    for field in required_fields:
                        if field in apt and apt[field] is not None:
                            field_presence[field] += 1
                
                all_fields_present = all(count == len(apartments) for count in field_presence.values())
                if all_fields_present:
                    self.log_result("Required Fields Presence", True, f"All required fields present in all {len(apartments)} apartments")
                else:
                    missing_fields = [f"{field}: {count}/{len(apartments)}" for field, count in field_presence.items() if count < len(apartments)]
                    self.log_result("Required Fields Presence", False, f"Missing fields: {', '.join(missing_fields)}")
                
                # Test 4: Check data type consistency
                type_issues = []
                for i, apt in enumerate(apartments[:10]):  # Check first 10 apartments for performance
                    if not isinstance(apt.get("price"), int):
                        type_issues.append(f"Apartment {i}: price is not int")
                    if not isinstance(apt.get("bedrooms"), int):
                        type_issues.append(f"Apartment {i}: bedrooms is not int")
                    if not isinstance(apt.get("bathrooms"), (int, float)):
                        type_issues.append(f"Apartment {i}: bathrooms is not number")
                    if "sqft" in apt and not isinstance(apt.get("sqft"), int):
                        type_issues.append(f"Apartment {i}: sqft is not int")
                
                if not type_issues:
                    self.log_result("Data Type Consistency", True, "All data types are consistent")
                else:
                    self.log_result("Data Type Consistency", False, f"Type issues: {'; '.join(type_issues[:3])}")
                
            else:
                self.log_result("API Field Consistency", False, f"Status code: {response.status_code}")
            
        except Exception as e:
            self.log_result("API Field Consistency", False, f"Exception: {str(e)}")
    
    def test_statistics_endpoint_consistency(self):
        """Test that statistics endpoint uses correct field mappings"""
        print("\n=== Testing Statistics Endpoint Field Consistency ===")
        try:
            response = self.make_request("GET", "/apartments/search/stats")
            if response.status_code == 200:
                stats = response.json()
                
                # Check if stats endpoint returns data
                if "total_apartments" in stats:
                    total_count = stats["total_apartments"]
                    self.log_result("Statistics Endpoint Response", True, f"Stats endpoint returns {total_count} total apartments")
                    
                    # Verify the count matches actual apartment count
                    apartments_response = self.make_request("GET", "/apartments", {"limit": 100})
                    if apartments_response.status_code == 200:
                        actual_apartments = apartments_response.json()
                        actual_count = len(actual_apartments)
                        
                        if total_count == actual_count:
                            self.log_result("Statistics Count Consistency", True, f"Stats count ({total_count}) matches actual count ({actual_count})")
                        else:
                            self.log_result("Statistics Count Consistency", False, f"Stats count ({total_count}) != actual count ({actual_count})")
                    else:
                        self.log_result("Statistics Count Verification", False, f"Could not verify count: {apartments_response.status_code}")
                else:
                    self.log_result("Statistics Endpoint Response", False, f"Missing total_apartments in stats: {stats}")
            else:
                self.log_result("Statistics Endpoint Consistency", False, f"Status code: {response.status_code}")
            
        except Exception as e:
            self.log_result("Statistics Endpoint Consistency", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all field mapping and data consistency tests"""
        print("🔍 FIELD MAPPING AND DATA CONSISTENCY TESTING SUITE")
        print("=" * 60)
        
        # Run all test methods
        self.test_square_footage_filtering_fix()
        self.test_apartment_counts_and_data_integrity()
        self.test_mock_data_vs_real_data_preservation()
        self.test_search_functionality_comprehensive()
        self.test_api_field_consistency()
        self.test_statistics_endpoint_consistency()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 FIELD MAPPING TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ PASSED: {self.results['passed']}")
        print(f"❌ FAILED: {self.results['failed']}")
        
        if self.results['errors']:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\n📊 SUCCESS RATE: {success_rate:.1f}%")
        
        return self.results

if __name__ == "__main__":
    tester = FieldMappingTester()
    results = tester.run_all_tests()