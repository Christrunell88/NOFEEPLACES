#!/usr/bin/env python3
"""
Comprehensive Price Sorting Functionality Test Suite
Tests the new price sorting functionality implemented in the backend API
Focus areas from review request:
1. Database Consolidation Verification
2. Sorting API Parameters  
3. Price Order Verification
4. Combined Filtering with Sorting
5. API Response Structure
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configuration - Use production URL from frontend/.env
BASE_URL = "https://rentauth-test.preview.emergentagent.com/api"

class ComprehensivePriceSortingTester:
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
    
    def make_request(self, method: str, endpoint: str, params: Dict = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_database_consolidation_verification(self):
        """Test 1: Database Consolidation Verification"""
        print("\n=== 1. DATABASE CONSOLIDATION VERIFICATION ===")
        
        try:
            # Get all apartments to verify consolidation
            response = self.make_request("GET", "/apartments", {"limit": 50})
            
            if response.status_code != 200:
                self.log_result("Database Consolidation - API Access", False, f"Failed to access apartments API: {response.status_code}")
                return
            
            # Check if response is ApartmentListResponse format
            data = response.json()
            if isinstance(data, dict) and "apartments" in data:
                apartments = data["apartments"]
                total_count = data.get("total", len(apartments))
            else:
                # Handle legacy format (direct list)
                apartments = data if isinstance(data, list) else []
                total_count = len(apartments)
            
            print(f"\n📊 Database Analysis:")
            print(f"   Total apartments found: {total_count}")
            print(f"   Apartments in response: {len(apartments)}")
            
            # Verify apartment count (expecting 12 total apartments)
            if total_count == 12:
                self.log_result("Total Apartment Count", True, f"Found exactly 12 apartments as expected")
            else:
                self.log_result("Total Apartment Count", False, f"Expected 12 apartments, found {total_count}")
            
            if not apartments:
                self.log_result("Database Consolidation", False, "No apartments returned")
                return
            
            # Check for source_database label field
            apartments_with_source = 0
            apartments_in_nofeeplaces_db = 0
            price_range = {"min": float('inf'), "max": 0}
            
            for apt in apartments:
                # Check source_database field
                if "source_database" in apt:
                    apartments_with_source += 1
                    if apt["source_database"] == "nofeeplaces_database":
                        apartments_in_nofeeplaces_db += 1
                
                # Track price range
                price = apt.get("price", 0)
                if price > 0:
                    price_range["min"] = min(price_range["min"], price)
                    price_range["max"] = max(price_range["max"], price)
            
            # Verify source_database labeling
            if apartments_with_source == len(apartments):
                self.log_result("Source Database Labeling", True, f"All {len(apartments)} apartments have source_database field")
            else:
                self.log_result("Source Database Labeling", False, f"Only {apartments_with_source}/{len(apartments)} apartments have source_database field")
            
            # Verify all apartments are in nofeeplaces_database
            if apartments_in_nofeeplaces_db == len(apartments):
                self.log_result("Database Consolidation", True, f"All {len(apartments)} apartments are in 'nofeeplaces_database'")
            else:
                self.log_result("Database Consolidation", False, f"Only {apartments_in_nofeeplaces_db}/{len(apartments)} apartments are in 'nofeeplaces_database'")
            
            # Verify price range ($2,163 - $17,100)
            expected_min = 2163
            expected_max = 17100
            
            print(f"\n💰 Price Range Analysis:")
            print(f"   Found price range: ${price_range['min']:,.0f} - ${price_range['max']:,.0f}")
            print(f"   Expected price range: ${expected_min:,.0f} - ${expected_max:,.0f}")
            
            if price_range["min"] == expected_min and price_range["max"] == expected_max:
                self.log_result("Price Range Verification", True, f"Price range matches expected ${expected_min:,.0f} - ${expected_max:,.0f}")
            else:
                self.log_result("Price Range Verification", False, f"Price range ${price_range['min']:,.0f} - ${price_range['max']:,.0f} doesn't match expected ${expected_min:,.0f} - ${expected_max:,.0f}")
            
        except Exception as e:
            self.log_result("Database Consolidation Verification", False, f"Exception: {str(e)}")
    
    def test_sorting_api_parameters(self):
        """Test 2: Sorting API Parameters"""
        print("\n=== 2. SORTING API PARAMETERS ===")
        
        sorting_tests = [
            {
                "name": "Price Ascending (Cheapest First)",
                "params": {"sort_by": "price", "sort_order": "asc", "limit": 20},
                "expected_first_price": 2163,
                "description": "Should return cheapest first, starting with $2,163 Studio"
            },
            {
                "name": "Price Descending (Most Expensive First)", 
                "params": {"sort_by": "price", "sort_order": "desc", "limit": 20},
                "expected_first_price": 17100,
                "description": "Should return most expensive first, starting with $17,100 3BR"
            },
            {
                "name": "Bedrooms Ascending",
                "params": {"sort_by": "bedrooms", "sort_order": "asc", "limit": 20},
                "expected_field": "bedrooms",
                "description": "Should sort by bedrooms ascending"
            },
            {
                "name": "Bedrooms Descending",
                "params": {"sort_by": "bedrooms", "sort_order": "desc", "limit": 20},
                "expected_field": "bedrooms", 
                "description": "Should sort by bedrooms descending"
            },
            {
                "name": "Created At Descending (Newest First)",
                "params": {"sort_by": "created_at", "sort_order": "desc", "limit": 20},
                "expected_field": "created_at",
                "description": "Should sort by creation date, newest first"
            },
            {
                "name": "Default Behavior (No Sort Parameters)",
                "params": {"limit": 20},
                "expected_default": "price_asc",
                "description": "Should default to price ascending"
            }
        ]
        
        for test in sorting_tests:
            try:
                print(f"\n🔄 Testing: {test['name']}")
                print(f"   {test['description']}")
                
                response = self.make_request("GET", "/apartments", test["params"])
                
                if response.status_code != 200:
                    self.log_result(test["name"], False, f"API request failed: {response.status_code}")
                    continue
                
                # Parse response
                data = response.json()
                if isinstance(data, dict) and "apartments" in data:
                    apartments = data["apartments"]
                else:
                    apartments = data if isinstance(data, list) else []
                
                if not apartments:
                    self.log_result(test["name"], False, "No apartments returned")
                    continue
                
                # Test specific sorting logic
                if "expected_first_price" in test:
                    first_price = apartments[0].get("price", 0)
                    if first_price == test["expected_first_price"]:
                        self.log_result(test["name"], True, f"First apartment price ${first_price:,.0f} matches expected ${test['expected_first_price']:,.0f}")
                    else:
                        self.log_result(test["name"], False, f"First apartment price ${first_price:,.0f} doesn't match expected ${test['expected_first_price']:,.0f}")
                
                elif "expected_field" in test:
                    # Check if sorting is working for the field
                    field_values = [apt.get(test["expected_field"]) for apt in apartments if apt.get(test["expected_field"]) is not None]
                    
                    if len(field_values) >= 2:
                        is_ascending = test["params"].get("sort_order", "asc") == "asc"
                        
                        if is_ascending:
                            is_sorted = all(field_values[i] <= field_values[i+1] for i in range(len(field_values)-1))
                        else:
                            is_sorted = all(field_values[i] >= field_values[i+1] for i in range(len(field_values)-1))
                        
                        if is_sorted:
                            order_desc = "ascending" if is_ascending else "descending"
                            self.log_result(test["name"], True, f"Apartments correctly sorted by {test['expected_field']} {order_desc}")
                        else:
                            self.log_result(test["name"], False, f"Apartments not properly sorted by {test['expected_field']}")
                    else:
                        self.log_result(test["name"], True, f"Insufficient data to verify {test['expected_field']} sorting, but API responded correctly")
                
                elif "expected_default" in test:
                    # Test default behavior (should be price ascending)
                    prices = [apt.get("price", 0) for apt in apartments if apt.get("price", 0) > 0]
                    
                    if len(prices) >= 2:
                        is_price_ascending = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
                        
                        if is_price_ascending:
                            self.log_result(test["name"], True, f"Default sorting correctly uses price ascending (${prices[0]:,.0f} to ${prices[-1]:,.0f})")
                        else:
                            self.log_result(test["name"], False, f"Default sorting not working correctly")
                    else:
                        self.log_result(test["name"], True, "Default behavior API responded correctly")
                
            except Exception as e:
                self.log_result(test["name"], False, f"Exception: {str(e)}")
    
    def test_price_order_verification(self):
        """Test 3: Price Order Verification"""
        print("\n=== 3. PRICE ORDER VERIFICATION ===")
        
        try:
            # Test ascending order (prices should increase monotonically)
            print("\n📈 Testing Price Ascending Order...")
            asc_response = self.make_request("GET", "/apartments", {"sort_by": "price", "sort_order": "asc", "limit": 50})
            
            if asc_response.status_code == 200:
                asc_data = asc_response.json()
                asc_apartments = asc_data.get("apartments", asc_data) if isinstance(asc_data, dict) else asc_data
                
                if asc_apartments:
                    asc_prices = [apt.get("price", 0) for apt in asc_apartments if apt.get("price", 0) > 0]
                    
                    # Check monotonic increase
                    is_monotonic_asc = all(asc_prices[i] <= asc_prices[i+1] for i in range(len(asc_prices)-1))
                    
                    if is_monotonic_asc:
                        self.log_result("Price Ascending Monotonic", True, 
                                      f"Prices increase monotonically: ${asc_prices[0]:,.0f} → ${asc_prices[1]:,.0f} → ${asc_prices[2]:,.0f} → ... → ${asc_prices[-1]:,.0f}")
                    else:
                        # Find first violation
                        violation_idx = None
                        for i in range(len(asc_prices)-1):
                            if asc_prices[i] > asc_prices[i+1]:
                                violation_idx = i
                                break
                        
                        if violation_idx is not None:
                            self.log_result("Price Ascending Monotonic", False, 
                                          f"Price order violation at position {violation_idx}: ${asc_prices[violation_idx]:,.0f} > ${asc_prices[violation_idx+1]:,.0f}")
                        else:
                            self.log_result("Price Ascending Monotonic", False, "Price order not monotonic")
                    
                    # Verify expected starting price ($2,163)
                    if asc_prices[0] == 2163:
                        self.log_result("Expected Starting Price (Ascending)", True, f"First apartment price ${asc_prices[0]:,.0f} matches expected $2,163")
                    else:
                        self.log_result("Expected Starting Price (Ascending)", False, f"First apartment price ${asc_prices[0]:,.0f} doesn't match expected $2,163")
                else:
                    self.log_result("Price Ascending Order", False, "No apartments returned for ascending test")
            else:
                self.log_result("Price Ascending Order", False, f"API request failed: {asc_response.status_code}")
            
            # Test descending order (prices should decrease monotonically)
            print("\n📉 Testing Price Descending Order...")
            desc_response = self.make_request("GET", "/apartments", {"sort_by": "price", "sort_order": "desc", "limit": 50})
            
            if desc_response.status_code == 200:
                desc_data = desc_response.json()
                desc_apartments = desc_data.get("apartments", desc_data) if isinstance(desc_data, dict) else desc_data
                
                if desc_apartments:
                    desc_prices = [apt.get("price", 0) for apt in desc_apartments if apt.get("price", 0) > 0]
                    
                    # Check monotonic decrease
                    is_monotonic_desc = all(desc_prices[i] >= desc_prices[i+1] for i in range(len(desc_prices)-1))
                    
                    if is_monotonic_desc:
                        self.log_result("Price Descending Monotonic", True, 
                                      f"Prices decrease monotonically: ${desc_prices[0]:,.0f} → ${desc_prices[1]:,.0f} → ${desc_prices[2]:,.0f} → ... → ${desc_prices[-1]:,.0f}")
                    else:
                        # Find first violation
                        violation_idx = None
                        for i in range(len(desc_prices)-1):
                            if desc_prices[i] < desc_prices[i+1]:
                                violation_idx = i
                                break
                        
                        if violation_idx is not None:
                            self.log_result("Price Descending Monotonic", False, 
                                          f"Price order violation at position {violation_idx}: ${desc_prices[violation_idx]:,.0f} < ${desc_prices[violation_idx+1]:,.0f}")
                        else:
                            self.log_result("Price Descending Monotonic", False, "Price order not monotonic")
                    
                    # Verify expected starting price ($17,100)
                    if desc_prices[0] == 17100:
                        self.log_result("Expected Starting Price (Descending)", True, f"First apartment price ${desc_prices[0]:,.0f} matches expected $17,100")
                    else:
                        self.log_result("Expected Starting Price (Descending)", False, f"First apartment price ${desc_prices[0]:,.0f} doesn't match expected $17,100")
                else:
                    self.log_result("Price Descending Order", False, "No apartments returned for descending test")
            else:
                self.log_result("Price Descending Order", False, f"API request failed: {desc_response.status_code}")
            
            # Verify all 12 apartments appear in results
            print("\n🔢 Testing Complete Apartment Coverage...")
            all_response = self.make_request("GET", "/apartments", {"limit": 50})
            
            if all_response.status_code == 200:
                all_data = all_response.json()
                total_count = all_data.get("total", len(all_data.get("apartments", all_data))) if isinstance(all_data, dict) else len(all_data)
                
                if total_count == 12:
                    self.log_result("Complete Apartment Coverage", True, f"All 12 apartments appear in results")
                else:
                    self.log_result("Complete Apartment Coverage", False, f"Expected 12 apartments, found {total_count}")
            else:
                self.log_result("Complete Apartment Coverage", False, f"Failed to get all apartments: {all_response.status_code}")
            
        except Exception as e:
            self.log_result("Price Order Verification", False, f"Exception: {str(e)}")
    
    def test_combined_filtering_with_sorting(self):
        """Test 4: Combined Filtering with Sorting"""
        print("\n=== 4. COMBINED FILTERING WITH SORTING ===")
        
        combined_tests = [
            {
                "name": "Price Range + Price Sorting",
                "params": {"min_price": 3000, "max_price": 8000, "sort_by": "price", "sort_order": "asc", "limit": 20},
                "description": "Filter by price range and sort by price ascending"
            },
            {
                "name": "Bedroom Filter + Price Sorting",
                "params": {"bedrooms": 1, "sort_by": "price", "sort_order": "desc", "limit": 20},
                "description": "Filter by 1 bedroom and sort by price descending"
            },
            {
                "name": "Price Range + Bedroom Sorting",
                "params": {"min_price": 2000, "max_price": 10000, "sort_by": "bedrooms", "sort_order": "asc", "limit": 20},
                "description": "Filter by price range and sort by bedrooms ascending"
            },
            {
                "name": "Multiple Filters + Sorting",
                "params": {"min_price": 2500, "max_price": 15000, "bedrooms": 2, "sort_by": "price", "sort_order": "asc", "limit": 20},
                "description": "Multiple filters with price sorting"
            }
        ]
        
        for test in combined_tests:
            try:
                print(f"\n🔧 Testing: {test['name']}")
                print(f"   {test['description']}")
                
                response = self.make_request("GET", "/apartments", test["params"])
                
                if response.status_code != 200:
                    self.log_result(test["name"], False, f"API request failed: {response.status_code}")
                    continue
                
                # Parse response
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                if not apartments:
                    self.log_result(test["name"], True, "No apartments match the filter criteria (acceptable)")
                    continue
                
                # Verify filtering is applied
                filter_violations = []
                
                for i, apt in enumerate(apartments):
                    # Check price range filter
                    if "min_price" in test["params"]:
                        if apt.get("price", 0) < test["params"]["min_price"]:
                            filter_violations.append(f"Apartment {i+1} price ${apt.get('price', 0):,.0f} below min ${test['params']['min_price']:,.0f}")
                    
                    if "max_price" in test["params"]:
                        if apt.get("price", 0) > test["params"]["max_price"]:
                            filter_violations.append(f"Apartment {i+1} price ${apt.get('price', 0):,.0f} above max ${test['params']['max_price']:,.0f}")
                    
                    # Check bedroom filter
                    if "bedrooms" in test["params"]:
                        if apt.get("bedrooms") != test["params"]["bedrooms"]:
                            filter_violations.append(f"Apartment {i+1} has {apt.get('bedrooms')} bedrooms, expected {test['params']['bedrooms']}")
                
                # Verify sorting is maintained
                sort_by = test["params"].get("sort_by", "price")
                sort_order = test["params"].get("sort_order", "asc")
                
                sort_values = [apt.get(sort_by) for apt in apartments if apt.get(sort_by) is not None]
                
                if len(sort_values) >= 2:
                    if sort_order == "asc":
                        is_sorted = all(sort_values[i] <= sort_values[i+1] for i in range(len(sort_values)-1))
                    else:
                        is_sorted = all(sort_values[i] >= sort_values[i+1] for i in range(len(sort_values)-1))
                    
                    if not filter_violations and is_sorted:
                        self.log_result(test["name"], True, 
                                      f"Found {len(apartments)} apartments, all filters applied correctly, sorting by {sort_by} {sort_order} maintained")
                    elif filter_violations:
                        self.log_result(test["name"], False, f"Filter violations: {filter_violations[:3]}")
                    else:
                        self.log_result(test["name"], False, f"Sorting by {sort_by} {sort_order} not maintained")
                else:
                    if not filter_violations:
                        self.log_result(test["name"], True, f"Found {len(apartments)} apartments, filters applied correctly")
                    else:
                        self.log_result(test["name"], False, f"Filter violations: {filter_violations[:3]}")
                
            except Exception as e:
                self.log_result(test["name"], False, f"Exception: {str(e)}")
    
    def test_api_response_structure(self):
        """Test 5: API Response Structure"""
        print("\n=== 5. API RESPONSE STRUCTURE ===")
        
        try:
            # Test ApartmentListResponse format
            print("\n📋 Testing ApartmentListResponse Format...")
            response = self.make_request("GET", "/apartments", {"sort_by": "price", "sort_order": "asc", "limit": 10, "page": 1})
            
            if response.status_code != 200:
                self.log_result("API Response Structure", False, f"API request failed: {response.status_code}")
                return
            
            data = response.json()
            
            # Check if response follows ApartmentListResponse format
            if isinstance(data, dict):
                required_fields = ["apartments", "total", "page", "limit", "has_more"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_result("ApartmentListResponse Format", True, "Response contains all required fields: apartments, total, page, limit, has_more")
                    
                    # Verify field types and values
                    apartments = data["apartments"]
                    total = data["total"]
                    page = data["page"]
                    limit = data["limit"]
                    has_more = data["has_more"]
                    
                    # Test pagination fields
                    if isinstance(apartments, list) and isinstance(total, int) and isinstance(page, int) and isinstance(limit, int) and isinstance(has_more, bool):
                        self.log_result("Response Field Types", True, f"All fields have correct types")
                        
                        # Test pagination logic
                        expected_has_more = (page * limit) < total
                        if has_more == expected_has_more:
                            self.log_result("Pagination Logic", True, f"has_more field correctly calculated: {has_more}")
                        else:
                            self.log_result("Pagination Logic", False, f"has_more should be {expected_has_more}, got {has_more}")
                    else:
                        self.log_result("Response Field Types", False, "Some fields have incorrect types")
                    
                    # Test apartment fields
                    if apartments:
                        sample_apt = apartments[0]
                        required_apt_fields = ["id", "title", "price", "location", "bedrooms", "bathrooms", "images"]
                        missing_apt_fields = [field for field in required_apt_fields if field not in sample_apt]
                        
                        if not missing_apt_fields:
                            self.log_result("Apartment Fields", True, "Sample apartment contains all required fields")
                            
                            # Check for source_database label
                            if "source_database" in sample_apt:
                                self.log_result("Source Database Label", True, f"Apartment contains source_database field: {sample_apt['source_database']}")
                            else:
                                self.log_result("Source Database Label", False, "Apartment missing source_database field")
                        else:
                            self.log_result("Apartment Fields", False, f"Sample apartment missing fields: {missing_apt_fields}")
                    else:
                        self.log_result("Apartment Fields", False, "No apartments in response to test fields")
                else:
                    self.log_result("ApartmentListResponse Format", False, f"Response missing required fields: {missing_fields}")
            else:
                # Handle legacy format (direct list)
                if isinstance(data, list):
                    self.log_result("ApartmentListResponse Format", False, "Response is legacy list format, not ApartmentListResponse")
                    
                    # Still test apartment fields for legacy format
                    if data:
                        sample_apt = data[0]
                        required_apt_fields = ["id", "title", "price", "location", "bedrooms", "bathrooms", "images"]
                        missing_apt_fields = [field for field in required_apt_fields if field not in sample_apt]
                        
                        if not missing_apt_fields:
                            self.log_result("Apartment Fields (Legacy)", True, "Sample apartment contains all required fields")
                        else:
                            self.log_result("Apartment Fields (Legacy)", False, f"Sample apartment missing fields: {missing_apt_fields}")
                else:
                    self.log_result("API Response Structure", False, f"Unexpected response format: {type(data)}")
            
            # Test sorting with pagination
            print("\n📄 Testing Sorting with Pagination...")
            page1_response = self.make_request("GET", "/apartments", {"sort_by": "price", "sort_order": "asc", "page": 1, "limit": 5})
            page2_response = self.make_request("GET", "/apartments", {"sort_by": "price", "sort_order": "asc", "page": 2, "limit": 5})
            
            if page1_response.status_code == 200 and page2_response.status_code == 200:
                page1_data = page1_response.json()
                page2_data = page2_response.json()
                
                page1_apartments = page1_data.get("apartments", page1_data) if isinstance(page1_data, dict) else page1_data
                page2_apartments = page2_data.get("apartments", page2_data) if isinstance(page2_data, dict) else page2_data
                
                if page1_apartments and page2_apartments:
                    # Check that sorting is maintained across pages
                    last_page1_price = page1_apartments[-1].get("price", 0)
                    first_page2_price = page2_apartments[0].get("price", 0)
                    
                    if last_page1_price <= first_page2_price:
                        self.log_result("Sorting with Pagination", True, f"Sorting maintained across pages: Page 1 last ${last_page1_price:,.0f} ≤ Page 2 first ${first_page2_price:,.0f}")
                    else:
                        self.log_result("Sorting with Pagination", False, f"Sorting broken across pages: Page 1 last ${last_page1_price:,.0f} > Page 2 first ${first_page2_price:,.0f}")
                else:
                    self.log_result("Sorting with Pagination", True, "Insufficient data for cross-page sorting test")
            else:
                self.log_result("Sorting with Pagination", False, "Failed to get paginated results")
            
        except Exception as e:
            self.log_result("API Response Structure", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all price sorting tests"""
        print("🚀 STARTING COMPREHENSIVE PRICE SORTING FUNCTIONALITY TESTS")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_database_consolidation_verification()
        self.test_sorting_api_parameters()
        self.test_price_order_verification()
        self.test_combined_filtering_with_sorting()
        self.test_api_response_structure()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 70)
        print("🏁 COMPREHENSIVE PRICE SORTING TEST SUMMARY")
        print("=" * 70)
        print(f"⏱️  Total test duration: {duration:.2f} seconds")
        print(f"✅ Tests passed: {self.results['passed']}")
        print(f"❌ Tests failed: {self.results['failed']}")
        print(f"📊 Success rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results["errors"]:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        print("\n" + "=" * 70)
        
        return self.results

if __name__ == "__main__":
    tester = ComprehensivePriceSortingTester()
    results = tester.run_all_tests()