#!/usr/bin/env python3
"""
Search Functionality Testing Suite for NoFeePlaces.com
Tests comprehensive search functionality including search_term parameter coverage
"""

import requests
import json
import time
from typing import Dict, Any, List

# Configuration
BASE_URL = "https://smartrental.preview.emergentagent.com/api"

class SearchFunctionalityTester:
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
        headers = {"Content-Type": "application/json"}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_general_search_endpoint(self):
        """Test 1: General Search Endpoint - Test GET /api/apartments with search_term parameter"""
        print("\n=== Test 1: General Search Endpoint ===")
        try:
            # Test basic search_term functionality
            search_terms = [
                {"term": "luxury", "description": "Luxury apartments"},
                {"term": "studio", "description": "Studio apartments"},
                {"term": "manhattan", "description": "Manhattan location"},
                {"term": "bedroom", "description": "Bedroom keyword"}
            ]
            
            for search_test in search_terms:
                response = self.make_request("GET", "/apartments", {"search_term": search_test["term"], "limit": 20})
                
                if response.status_code == 200:
                    apartments = response.json()
                    if isinstance(apartments, list):
                        self.log_result(f"Search Term '{search_test['term']}'", True, 
                                      f"Found {len(apartments)} apartments for {search_test['description']}")
                        
                        # Verify search results contain the search term in relevant fields
                        if apartments:
                            relevant_matches = 0
                            for apt in apartments[:5]:  # Check first 5 results
                                title = apt.get("title", "").lower()
                                description = apt.get("description", "").lower()
                                neighborhood = apt.get("neighborhood", "").lower()
                                address = apt.get("address", "").lower()
                                
                                if (search_test["term"].lower() in title or 
                                    search_test["term"].lower() in description or
                                    search_test["term"].lower() in neighborhood or
                                    search_test["term"].lower() in address):
                                    relevant_matches += 1
                            
                            if relevant_matches > 0:
                                print(f"      ✓ {relevant_matches}/5 results contain '{search_test['term']}' in relevant fields")
                            else:
                                print(f"      ⚠ No obvious matches found in title/description/location fields")
                    else:
                        self.log_result(f"Search Term '{search_test['term']}'", False, 
                                      f"Expected list, got {type(apartments)}")
                else:
                    self.log_result(f"Search Term '{search_test['term']}'", False, 
                                  f"HTTP {response.status_code}: {response.text[:100]}")
                
                time.sleep(0.5)  # Small delay between requests
                
        except Exception as e:
            self.log_result("General Search Endpoint", False, f"Exception: {str(e)}")
    
    def test_search_term_coverage(self):
        """Test 2: Search Term Coverage - Test searching across title, location, address, neighborhood, description, source fields"""
        print("\n=== Test 2: Search Term Coverage ===")
        try:
            # Test keywords that should match different fields
            coverage_tests = [
                {
                    "term": "bedroom", 
                    "expected_fields": ["title", "description"],
                    "description": "Should match apartments with bedroom mentions"
                },
                {
                    "term": "luxury", 
                    "expected_fields": ["title", "description"],
                    "description": "Should match luxury apartments"
                },
                {
                    "term": "studio", 
                    "expected_fields": ["title", "description"],
                    "description": "Should match studio apartments"
                },
                {
                    "term": "manhattan", 
                    "expected_fields": ["neighborhood", "address", "location"],
                    "description": "Should match Manhattan locations"
                },
                {
                    "term": "chelsea", 
                    "expected_fields": ["neighborhood", "address"],
                    "description": "Should match Chelsea neighborhood"
                },
                {
                    "term": "waterline", 
                    "expected_fields": ["title", "address", "source"],
                    "description": "Should match Waterline Square apartments"
                }
            ]
            
            for test in coverage_tests:
                response = self.make_request("GET", "/apartments", {"search_term": test["term"], "limit": 30})
                
                if response.status_code == 200:
                    apartments = response.json()
                    
                    if apartments:
                        # Analyze which fields contain the search term
                        field_matches = {
                            "title": 0,
                            "description": 0,
                            "neighborhood": 0,
                            "address": 0,
                            "location": 0,
                            "source": 0,
                            "source_url": 0
                        }
                        
                        total_matches = 0
                        for apt in apartments:
                            apt_has_match = False
                            
                            for field in field_matches.keys():
                                field_value = str(apt.get(field, "")).lower()
                                if test["term"].lower() in field_value:
                                    field_matches[field] += 1
                                    apt_has_match = True
                            
                            if apt_has_match:
                                total_matches += 1
                        
                        # Report field coverage
                        matching_fields = [field for field, count in field_matches.items() if count > 0]
                        
                        if matching_fields:
                            self.log_result(f"Coverage '{test['term']}'", True, 
                                          f"Found {len(apartments)} results, {total_matches} with matches in fields: {matching_fields}")
                            
                            # Show detailed field breakdown
                            for field, count in field_matches.items():
                                if count > 0:
                                    print(f"      • {field}: {count} matches")
                        else:
                            self.log_result(f"Coverage '{test['term']}'", False, 
                                          f"Found {len(apartments)} results but no field matches detected")
                    else:
                        # Empty results might be valid for some search terms
                        self.log_result(f"Coverage '{test['term']}'", True, 
                                      f"No results found for '{test['term']}' (may be expected)")
                else:
                    self.log_result(f"Coverage '{test['term']}'", False, 
                                  f"HTTP {response.status_code}: {response.text[:100]}")
                
                time.sleep(0.5)
                
        except Exception as e:
            self.log_result("Search Term Coverage", False, f"Exception: {str(e)}")
    
    def test_combined_filters(self):
        """Test 3: Combined Filters - Test search_term combined with other filters"""
        print("\n=== Test 3: Combined Filters ===")
        try:
            combined_tests = [
                {
                    "params": {"search_term": "luxury", "bedrooms": 1},
                    "description": "Luxury 1-bedroom apartments"
                },
                {
                    "params": {"search_term": "studio", "max_price": 4000},
                    "description": "Studios under $4000"
                },
                {
                    "params": {"search_term": "manhattan", "min_price": 5000, "max_price": 8000},
                    "description": "Manhattan apartments $5000-$8000"
                },
                {
                    "params": {"search_term": "bedroom", "neighborhood": "chelsea"},
                    "description": "Bedrooms in Chelsea"
                },
                {
                    "params": {"search_term": "luxury", "borough": "Manhattan", "bedrooms": 2},
                    "description": "Luxury 2BR in Manhattan"
                },
                {
                    "params": {"search_term": "waterline", "min_sqft": 700},
                    "description": "Waterline apartments over 700 sqft"
                }
            ]
            
            for test in combined_tests:
                response = self.make_request("GET", "/apartments", {**test["params"], "limit": 20})
                
                if response.status_code == 200:
                    apartments = response.json()
                    
                    # Verify results meet all criteria
                    valid_results = 0
                    total_results = len(apartments)
                    
                    for apt in apartments:
                        meets_criteria = True
                        
                        # Check search_term
                        if "search_term" in test["params"]:
                            search_term = test["params"]["search_term"].lower()
                            searchable_text = " ".join([
                                str(apt.get("title", "")),
                                str(apt.get("description", "")),
                                str(apt.get("neighborhood", "")),
                                str(apt.get("address", "")),
                                str(apt.get("source", ""))
                            ]).lower()
                            
                            if search_term not in searchable_text:
                                meets_criteria = False
                        
                        # Check other filters
                        if "bedrooms" in test["params"] and apt.get("bedrooms") != test["params"]["bedrooms"]:
                            meets_criteria = False
                        
                        if "min_price" in test["params"] and apt.get("price", 0) < test["params"]["min_price"]:
                            meets_criteria = False
                        
                        if "max_price" in test["params"] and apt.get("price", 0) > test["params"]["max_price"]:
                            meets_criteria = False
                        
                        if "neighborhood" in test["params"]:
                            neighborhood_filter = test["params"]["neighborhood"].lower()
                            apt_neighborhood = str(apt.get("neighborhood", "")).lower()
                            if neighborhood_filter not in apt_neighborhood:
                                meets_criteria = False
                        
                        if "borough" in test["params"]:
                            borough_filter = test["params"]["borough"].lower()
                            apt_borough = str(apt.get("borough", "")).lower()
                            if borough_filter not in apt_borough:
                                meets_criteria = False
                        
                        if "min_sqft" in test["params"] and apt.get("sqft", 0) < test["params"]["min_sqft"]:
                            meets_criteria = False
                        
                        if meets_criteria:
                            valid_results += 1
                    
                    if total_results == 0:
                        self.log_result(f"Combined Filter: {test['description']}", True, 
                                      "No results found (may be expected for specific combinations)")
                    elif valid_results == total_results:
                        self.log_result(f"Combined Filter: {test['description']}", True, 
                                      f"All {total_results} results meet combined criteria")
                    else:
                        self.log_result(f"Combined Filter: {test['description']}", False, 
                                      f"Only {valid_results}/{total_results} results meet all criteria")
                else:
                    self.log_result(f"Combined Filter: {test['description']}", False, 
                                  f"HTTP {response.status_code}: {response.text[:100]}")
                
                time.sleep(0.5)
                
        except Exception as e:
            self.log_result("Combined Filters", False, f"Exception: {str(e)}")
    
    def test_case_sensitivity(self):
        """Test 4: Case Sensitivity - Verify search is case-insensitive"""
        print("\n=== Test 4: Case Sensitivity ===")
        try:
            case_tests = [
                {
                    "base_term": "bedroom",
                    "variations": ["bedroom", "BEDROOM", "Bedroom", "BeDrOoM"]
                },
                {
                    "base_term": "luxury",
                    "variations": ["luxury", "LUXURY", "Luxury", "LuXuRy"]
                },
                {
                    "base_term": "manhattan",
                    "variations": ["manhattan", "MANHATTAN", "Manhattan", "MaNhAtTaN"]
                },
                {
                    "base_term": "studio",
                    "variations": ["studio", "STUDIO", "Studio", "StUdIo"]
                }
            ]
            
            for test in case_tests:
                results_by_case = {}
                
                for variation in test["variations"]:
                    response = self.make_request("GET", "/apartments", {"search_term": variation, "limit": 15})
                    
                    if response.status_code == 200:
                        apartments = response.json()
                        results_by_case[variation] = len(apartments)
                    else:
                        results_by_case[variation] = -1  # Error
                
                # Check if all variations return the same number of results
                valid_results = [count for count in results_by_case.values() if count >= 0]
                
                if len(valid_results) == len(test["variations"]):
                    unique_counts = set(valid_results)
                    
                    if len(unique_counts) == 1:
                        result_count = list(unique_counts)[0]
                        self.log_result(f"Case Insensitive: '{test['base_term']}'", True, 
                                      f"All case variations return {result_count} results")
                        
                        # Show breakdown
                        for variation, count in results_by_case.items():
                            print(f"      • '{variation}': {count} results")
                    else:
                        self.log_result(f"Case Insensitive: '{test['base_term']}'", False, 
                                      f"Case variations return different counts: {dict(results_by_case)}")
                else:
                    failed_variations = [var for var, count in results_by_case.items() if count == -1]
                    self.log_result(f"Case Insensitive: '{test['base_term']}'", False, 
                                  f"Failed requests for: {failed_variations}")
                
                time.sleep(0.5)
                
        except Exception as e:
            self.log_result("Case Sensitivity", False, f"Exception: {str(e)}")
    
    def test_regex_matching(self):
        """Test 5: Regex Matching - Test partial matches (e.g., 'bed' should match 'bedroom')"""
        print("\n=== Test 5: Regex/Partial Matching ===")
        try:
            partial_tests = [
                {
                    "partial": "bed",
                    "should_match": ["bedroom", "bedrooms", "1-bed", "2-bed"],
                    "description": "Bed should match bedroom variations"
                },
                {
                    "partial": "lux",
                    "should_match": ["luxury", "luxurious", "deluxe"],
                    "description": "Lux should match luxury variations"
                },
                {
                    "partial": "man",
                    "should_match": ["manhattan", "Manhattan"],
                    "description": "Man should match Manhattan"
                },
                {
                    "partial": "stud",
                    "should_match": ["studio", "studios"],
                    "description": "Stud should match studio"
                },
                {
                    "partial": "chel",
                    "should_match": ["chelsea", "Chelsea"],
                    "description": "Chel should match Chelsea"
                }
            ]
            
            for test in partial_tests:
                response = self.make_request("GET", "/apartments", {"search_term": test["partial"], "limit": 20})
                
                if response.status_code == 200:
                    apartments = response.json()
                    
                    if apartments:
                        # Check if results contain expected matches
                        found_matches = set()
                        
                        for apt in apartments:
                            searchable_text = " ".join([
                                str(apt.get("title", "")),
                                str(apt.get("description", "")),
                                str(apt.get("neighborhood", "")),
                                str(apt.get("address", ""))
                            ]).lower()
                            
                            for expected_match in test["should_match"]:
                                if expected_match.lower() in searchable_text:
                                    found_matches.add(expected_match.lower())
                        
                        if found_matches:
                            self.log_result(f"Partial Match: '{test['partial']}'", True, 
                                          f"Found {len(apartments)} results with matches: {list(found_matches)}")
                        else:
                            # Check if the partial term itself appears
                            partial_found = False
                            for apt in apartments[:3]:  # Check first 3
                                searchable_text = " ".join([
                                    str(apt.get("title", "")),
                                    str(apt.get("description", "")),
                                    str(apt.get("neighborhood", "")),
                                    str(apt.get("address", ""))
                                ]).lower()
                                
                                if test["partial"].lower() in searchable_text:
                                    partial_found = True
                                    break
                            
                            if partial_found:
                                self.log_result(f"Partial Match: '{test['partial']}'", True, 
                                              f"Found {len(apartments)} results containing '{test['partial']}'")
                            else:
                                self.log_result(f"Partial Match: '{test['partial']}'", False, 
                                              f"Found {len(apartments)} results but no obvious matches")
                    else:
                        self.log_result(f"Partial Match: '{test['partial']}'", True, 
                                      f"No results for '{test['partial']}' (may be expected)")
                else:
                    self.log_result(f"Partial Match: '{test['partial']}'", False, 
                                  f"HTTP {response.status_code}: {response.text[:100]}")
                
                time.sleep(0.5)
                
        except Exception as e:
            self.log_result("Regex Matching", False, f"Exception: {str(e)}")
    
    def test_no_results_handling(self):
        """Test 6: No Results Handling - Test searches that should return no results"""
        print("\n=== Test 6: No Results Handling ===")
        try:
            no_results_tests = [
                {
                    "term": "xyzzyx123",
                    "description": "Random nonsense term"
                },
                {
                    "term": "mars_apartment",
                    "description": "Non-existent location"
                },
                {
                    "term": "unicorn_penthouse",
                    "description": "Fantasy apartment type"
                },
                {
                    "term": "qwertyuiop",
                    "description": "Keyboard mash"
                },
                {
                    "term": "antarctica_luxury",
                    "description": "Impossible location"
                }
            ]
            
            for test in no_results_tests:
                response = self.make_request("GET", "/apartments", {"search_term": test["term"], "limit": 10})
                
                if response.status_code == 200:
                    apartments = response.json()
                    
                    if isinstance(apartments, list):
                        if len(apartments) == 0:
                            self.log_result(f"No Results: '{test['term']}'", True, 
                                          f"Correctly returned 0 results for {test['description']}")
                        else:
                            # Unexpected results - check if they're actually relevant
                            relevant_results = 0
                            for apt in apartments:
                                searchable_text = " ".join([
                                    str(apt.get("title", "")),
                                    str(apt.get("description", "")),
                                    str(apt.get("neighborhood", "")),
                                    str(apt.get("address", ""))
                                ]).lower()
                                
                                if test["term"].lower() in searchable_text:
                                    relevant_results += 1
                            
                            if relevant_results == 0:
                                self.log_result(f"No Results: '{test['term']}'", True, 
                                              f"Returned {len(apartments)} results but none contain search term (acceptable)")
                            else:
                                self.log_result(f"No Results: '{test['term']}'", False, 
                                              f"Unexpectedly found {relevant_results} relevant results")
                    else:
                        self.log_result(f"No Results: '{test['term']}'", False, 
                                      f"Expected list, got {type(apartments)}")
                else:
                    self.log_result(f"No Results: '{test['term']}'", False, 
                                  f"HTTP {response.status_code}: {response.text[:100]}")
                
                time.sleep(0.5)
                
        except Exception as e:
            self.log_result("No Results Handling", False, f"Exception: {str(e)}")
    
    def test_empty_search(self):
        """Test 7: Empty Search - Test behavior with empty search_term"""
        print("\n=== Test 7: Empty Search Handling ===")
        try:
            empty_search_tests = [
                {
                    "params": {"search_term": ""},
                    "description": "Empty string search_term"
                },
                {
                    "params": {"search_term": "   "},
                    "description": "Whitespace-only search_term"
                },
                {
                    "params": {},
                    "description": "No search_term parameter (baseline)"
                }
            ]
            
            baseline_count = None
            
            for test in empty_search_tests:
                response = self.make_request("GET", "/apartments", {**test["params"], "limit": 20})
                
                if response.status_code == 200:
                    apartments = response.json()
                    
                    if isinstance(apartments, list):
                        result_count = len(apartments)
                        
                        if test["description"] == "No search_term parameter (baseline)":
                            baseline_count = result_count
                            self.log_result("Empty Search: Baseline", True, 
                                          f"Baseline (no search_term): {result_count} results")
                        else:
                            if baseline_count is not None:
                                if result_count == baseline_count:
                                    self.log_result(f"Empty Search: {test['description']}", True, 
                                                  f"Empty search returns same as baseline: {result_count} results")
                                else:
                                    self.log_result(f"Empty Search: {test['description']}", True, 
                                                  f"Empty search returns {result_count} results (vs baseline {baseline_count})")
                            else:
                                self.log_result(f"Empty Search: {test['description']}", True, 
                                              f"Empty search returns {result_count} results")
                    else:
                        self.log_result(f"Empty Search: {test['description']}", False, 
                                      f"Expected list, got {type(apartments)}")
                else:
                    self.log_result(f"Empty Search: {test['description']}", False, 
                                  f"HTTP {response.status_code}: {response.text[:100]}")
                
                time.sleep(0.5)
                
        except Exception as e:
            self.log_result("Empty Search", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all search functionality tests"""
        print("🔍 SEARCH FUNCTIONALITY TESTING SUITE")
        print("=" * 50)
        
        start_time = time.time()
        
        # Run all test methods
        self.test_general_search_endpoint()
        self.test_search_term_coverage()
        self.test_combined_filters()
        self.test_case_sensitivity()
        self.test_regex_matching()
        self.test_no_results_handling()
        self.test_empty_search()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 50)
        print("🎯 SEARCH FUNCTIONALITY TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Tests Passed: {self.results['passed']}")
        print(f"❌ Tests Failed: {self.results['failed']}")
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"📊 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print(f"\n❌ FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return self.results

if __name__ == "__main__":
    tester = SearchFunctionalityTester()
    results = tester.run_all_tests()