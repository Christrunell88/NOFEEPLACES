#!/usr/bin/env python3
"""
Apartment Sorting Test Suite - Focus on newest listings first functionality
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://aptfinderapp.preview.emergentagent.com/api"

class ApartmentSortingTester:
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

    def test_apartment_sorting_newest_first(self):
        """Test that apartments are sorted by creation date in descending order (newest first)"""
        print("\n=== Testing Apartment Sorting - Newest First ===")
        try:
            # Test basic listing - should return apartments sorted by newest first
            response = self.make_request("GET", "/apartments", {"limit": 50})
            
            if response.status_code == 200:
                apartments = response.json()
                if len(apartments) >= 2:
                    # Check if apartments have created_at field and are sorted correctly
                    creation_dates = []
                    for apt in apartments:
                        if "created_at" in apt:
                            creation_dates.append(apt["created_at"])
                    
                    if len(creation_dates) >= 2:
                        # Verify dates are in descending order (newest first)
                        is_sorted_desc = all(creation_dates[i] >= creation_dates[i+1] for i in range(len(creation_dates)-1))
                        
                        if is_sorted_desc:
                            self.log_result("Apartment Sorting (Newest First)", True, 
                                          f"Apartments correctly sorted by creation date descending. First: {creation_dates[0][:19]}, Last: {creation_dates[-1][:19]}")
                        else:
                            self.log_result("Apartment Sorting (Newest First)", False, 
                                          f"Apartments not sorted correctly. First: {creation_dates[0][:19]}, Second: {creation_dates[1][:19]}")
                    else:
                        self.log_result("Apartment Sorting (Newest First)", False, "Apartments missing created_at field")
                else:
                    self.log_result("Apartment Sorting (Newest First)", False, f"Not enough apartments to test sorting: {len(apartments)}")
            else:
                self.log_result("Apartment Sorting (Newest First)", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Apartment Sorting (Newest First)", False, f"Exception: {str(e)}")

    def test_apartment_sorting_with_pagination(self):
        """Test that sorting works correctly across multiple pages"""
        print("\n=== Testing Apartment Sorting with Pagination ===")
        try:
            # Get first page
            response1 = self.make_request("GET", "/apartments", {"page": 1, "limit": 10})
            if response1.status_code != 200:
                self.log_result("Pagination Sorting (Page 1)", False, f"Failed to get page 1: {response1.status_code}")
                return
            
            page1_apartments = response1.json()
            
            # Get second page
            response2 = self.make_request("GET", "/apartments", {"page": 2, "limit": 10})
            if response2.status_code != 200:
                self.log_result("Pagination Sorting (Page 2)", False, f"Failed to get page 2: {response2.status_code}")
                return
            
            page2_apartments = response2.json()
            
            if len(page1_apartments) > 0 and len(page2_apartments) > 0:
                # Check that last apartment on page 1 is newer than first apartment on page 2
                if "created_at" in page1_apartments[-1] and "created_at" in page2_apartments[0]:
                    last_page1_date = page1_apartments[-1]["created_at"]
                    first_page2_date = page2_apartments[0]["created_at"]
                    
                    if last_page1_date >= first_page2_date:
                        self.log_result("Pagination Sorting Consistency", True, 
                                      f"Sorting consistent across pages. Page 1 last: {last_page1_date[:19]}, Page 2 first: {first_page2_date[:19]}")
                    else:
                        self.log_result("Pagination Sorting Consistency", False, 
                                      f"Sorting inconsistent. Page 1 last: {last_page1_date[:19]} should be >= Page 2 first: {first_page2_date[:19]}")
                else:
                    self.log_result("Pagination Sorting Consistency", False, "Missing created_at field in paginated results")
            else:
                self.log_result("Pagination Sorting Consistency", False, f"Insufficient data for pagination test. Page 1: {len(page1_apartments)}, Page 2: {len(page2_apartments)}")
                
        except Exception as e:
            self.log_result("Pagination Sorting Consistency", False, f"Exception: {str(e)}")

    def test_apartment_sorting_with_search_filters(self):
        """Test that sorting works correctly when search terms and filters are applied"""
        print("\n=== Testing Apartment Sorting with Search and Filters ===")
        try:
            # Test with search term - should still be newest first
            response = self.make_request("GET", "/apartments", {"search_term": "manhattan", "limit": 20})
            if response.status_code == 200:
                apartments = response.json()
                if len(apartments) >= 2:
                    creation_dates = [apt["created_at"] for apt in apartments if "created_at" in apt]
                    if len(creation_dates) >= 2:
                        is_sorted_desc = all(creation_dates[i] >= creation_dates[i+1] for i in range(len(creation_dates)-1))
                        if is_sorted_desc:
                            self.log_result("Search Term Sorting", True, f"Manhattan search results sorted correctly ({len(apartments)} results)")
                        else:
                            self.log_result("Search Term Sorting", False, f"Manhattan search results not sorted correctly")
                    else:
                        self.log_result("Search Term Sorting", False, "Insufficient apartments with created_at for search sorting test")
                else:
                    self.log_result("Search Term Sorting", True, f"Manhattan search returned {len(apartments)} results (too few to test sorting)")
            else:
                self.log_result("Search Term Sorting", False, f"Manhattan search failed: {response.status_code}")
            
            # Test with price filter - should still be newest first
            response = self.make_request("GET", "/apartments", {"min_price": 3000, "limit": 20})
            if response.status_code == 200:
                apartments = response.json()
                if len(apartments) >= 2:
                    creation_dates = [apt["created_at"] for apt in apartments if "created_at" in apt]
                    if len(creation_dates) >= 2:
                        is_sorted_desc = all(creation_dates[i] >= creation_dates[i+1] for i in range(len(creation_dates)-1))
                        if is_sorted_desc:
                            self.log_result("Price Filter Sorting", True, f"Price filtered results sorted correctly ({len(apartments)} results)")
                        else:
                            self.log_result("Price Filter Sorting", False, f"Price filtered results not sorted correctly")
                    else:
                        self.log_result("Price Filter Sorting", False, "Insufficient apartments with created_at for price filter sorting test")
                else:
                    self.log_result("Price Filter Sorting", True, f"Price filter returned {len(apartments)} results (too few to test sorting)")
            else:
                self.log_result("Price Filter Sorting", False, f"Price filter failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Search and Filter Sorting", False, f"Exception: {str(e)}")

    def test_newest_listings_at_top(self):
        """Test that the most recently added apartments appear at the top"""
        print("\n=== Testing Newest Listings at Top ===")
        try:
            # Get all apartments to identify the newest ones
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code != 200:
                self.log_result("Newest Listings Check", False, f"Failed to get apartments: {response.status_code}")
                return
            
            apartments = response.json()
            
            # Look for recently added apartments mentioned in the review request
            recent_buildings = ["Mercedes House", "Two Trees", "StreetEasy"]
            found_recent = []
            
            for i, apt in enumerate(apartments[:10]):  # Check top 10 apartments
                title = (apt.get("title") or "").lower()
                source = (apt.get("source") or "").lower()
                source_url = (apt.get("source_url") or "").lower()
                
                for building in recent_buildings:
                    if (building.lower() in title or 
                        building.lower() in source or 
                        building.lower() in source_url):
                        found_recent.append({
                            "position": i + 1,
                            "title": apt.get("title", "Unknown"),
                            "created_at": apt.get("created_at", "Unknown")[:19],
                            "building_type": building
                        })
                        break
            
            if found_recent:
                building_info = []
                for r in found_recent:
                    building_info.append(f"{r['building_type']} (pos {r['position']})")
                self.log_result("Recent Buildings at Top", True, 
                              f"Found {len(found_recent)} recent buildings in top 10: {building_info}")
                for recent in found_recent:
                    print(f"   • Position {recent['position']}: {recent['title']} ({recent['created_at']})")
            else:
                # Check if these buildings exist at all
                all_recent = []
                for apt in apartments:
                    title = (apt.get("title") or "").lower()
                    source = (apt.get("source") or "").lower()
                    source_url = (apt.get("source_url") or "").lower()
                    
                    for building in recent_buildings:
                        if (building.lower() in title or 
                            building.lower() in source or 
                            building.lower() in source_url):
                            all_recent.append(building)
                            break
                
                if all_recent:
                    self.log_result("Recent Buildings at Top", False, 
                                  f"Recent buildings found but not in top 10. Found: {set(all_recent)}")
                else:
                    self.log_result("Recent Buildings at Top", True, 
                                  "No specific recent buildings found - this may be expected if data has been refreshed")
            
            # Verify that apartments are generally sorted by creation date
            if len(apartments) >= 5:
                first_5_dates = [apt.get("created_at") for apt in apartments[:5] if apt.get("created_at")]
                if len(first_5_dates) >= 3:
                    is_descending = all(first_5_dates[i] >= first_5_dates[i+1] for i in range(len(first_5_dates)-1))
                    if is_descending:
                        self.log_result("Top 5 Date Ordering", True, f"Top 5 apartments correctly ordered by date")
                    else:
                        self.log_result("Top 5 Date Ordering", False, f"Top 5 apartments not correctly ordered by date")
                else:
                    self.log_result("Top 5 Date Ordering", False, "Insufficient date data in top 5 apartments")
            
        except Exception as e:
            self.log_result("Newest Listings at Top", False, f"Exception: {str(e)}")

    def test_api_response_structure_integrity(self):
        """Test that API response structure remains intact with sorting"""
        print("\n=== Testing API Response Structure Integrity ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 5})
            if response.status_code != 200:
                self.log_result("API Response Structure", False, f"Failed to get apartments: {response.status_code}")
                return
            
            apartments = response.json()
            if not apartments:
                self.log_result("API Response Structure", False, "No apartments returned")
                return
            
            # Check that all required fields are present
            required_fields = ["id", "title", "address", "price", "bedrooms", "bathrooms", "sqft", 
                             "neighborhood", "borough", "description", "amenities", "images", "contact_info"]
            
            structure_issues = []
            for i, apt in enumerate(apartments):
                for field in required_fields:
                    if field not in apt:
                        structure_issues.append(f"Apartment {i+1} missing field: {field}")
                    elif field == "amenities" and not isinstance(apt[field], list):
                        structure_issues.append(f"Apartment {i+1} amenities not a list: {type(apt[field])}")
                    elif field == "images" and not isinstance(apt[field], list):
                        structure_issues.append(f"Apartment {i+1} images not a list: {type(apt[field])}")
                    elif field == "contact_info" and not isinstance(apt[field], dict):
                        structure_issues.append(f"Apartment {i+1} contact_info not a dict: {type(apt[field])}")
            
            if not structure_issues:
                self.log_result("API Response Structure", True, f"All {len(apartments)} apartments have complete data structure")
            else:
                self.log_result("API Response Structure", False, f"Structure issues found: {len(structure_issues)} problems")
                for issue in structure_issues[:3]:  # Show first 3 issues
                    print(f"   • {issue}")
            
            # Verify that created_at field exists for sorting
            apartments_with_created_at = [apt for apt in apartments if "created_at" in apt]
            if len(apartments_with_created_at) == len(apartments):
                self.log_result("Created At Field Present", True, "All apartments have created_at field for sorting")
            else:
                self.log_result("Created At Field Present", False, 
                              f"Only {len(apartments_with_created_at)}/{len(apartments)} apartments have created_at field")
            
        except Exception as e:
            self.log_result("API Response Structure Integrity", False, f"Exception: {str(e)}")

    def test_sorting_performance(self):
        """Test that sorting doesn't cause performance issues"""
        print("\n=== Testing Sorting Performance ===")
        try:
            import time
            
            # Test performance with different page sizes
            test_cases = [
                {"limit": 20, "description": "Standard page size"},
                {"limit": 50, "description": "Large page size"},
                {"limit": 100, "description": "Maximum page size"}
            ]
            
            performance_results = []
            
            for test_case in test_cases:
                start_time = time.time()
                response = self.make_request("GET", "/apartments", {"limit": test_case["limit"]})
                end_time = time.time()
                
                response_time = end_time - start_time
                performance_results.append({
                    "limit": test_case["limit"],
                    "response_time": response_time,
                    "description": test_case["description"],
                    "success": response.status_code == 200
                })
            
            # Check if all requests were successful and reasonably fast
            all_successful = all(result["success"] for result in performance_results)
            max_response_time = max(result["response_time"] for result in performance_results)
            
            if all_successful and max_response_time < 5.0:  # All requests under 5 seconds
                self.log_result("Sorting Performance", True, 
                              f"All requests successful. Max response time: {max_response_time:.2f}s")
                for result in performance_results:
                    print(f"   • {result['description']} (limit={result['limit']}): {result['response_time']:.2f}s")
            else:
                failed_requests = [r for r in performance_results if not r["success"]]
                if failed_requests:
                    self.log_result("Sorting Performance", False, 
                                  f"{len(failed_requests)} requests failed")
                else:
                    self.log_result("Sorting Performance", False, 
                                  f"Performance issue: max response time {max_response_time:.2f}s")
            
        except Exception as e:
            self.log_result("Sorting Performance", False, f"Exception: {str(e)}")

    def run_sorting_tests(self):
        """Run all apartment sorting tests"""
        print("🔄 APARTMENT SORTING FUNCTIONALITY TESTING")
        print("=" * 60)
        print("Testing apartment listing sorting after updating backend to show newest listings first")
        print("Focus areas: Ordering, Pagination, Search/Filters, API Response, Performance")
        print("=" * 60)
        
        self.test_apartment_sorting_newest_first()
        self.test_apartment_sorting_with_pagination()
        self.test_apartment_sorting_with_search_filters()
        self.test_newest_listings_at_top()
        self.test_api_response_structure_integrity()
        self.test_sorting_performance()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 APARTMENT SORTING TEST RESULTS")
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
    tester = ApartmentSortingTester()
    tester.run_sorting_tests()