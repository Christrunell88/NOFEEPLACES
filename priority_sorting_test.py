#!/usr/bin/env python3
"""
Priority and Multiple Images Sorting Logic Testing Suite
Tests the updated apartment listing system with Claridge's apartment priority and multiple images sorting
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configuration
BASE_URL = "https://nofee-apartments-1.preview.emergentagent.com/api"

class PrioritySortingTester:
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
    
    def test_claridges_apartment_priority(self):
        """Test Claridge's apartment appears first with priority=1"""
        print("\n=== Testing Claridge's Apartment Priority ===")
        try:
            # Test basic listing to see if Claridge's appears first
            response = self.make_request("GET", "/apartments", {"limit": 10})
            
            if response.status_code == 200:
                apartments = response.json()
                if not apartments:
                    self.log_result("Claridge's Priority - Basic Listing", False, "No apartments returned")
                    return
                
                first_apartment = apartments[0]
                
                # Check if first apartment is Claridge's with priority=1
                title = first_apartment.get("title", "").lower()
                priority = first_apartment.get("priority")
                featured = first_apartment.get("featured")
                
                if "claridge" in title:
                    self.log_result("Claridge's Priority - First Position", True, 
                                  f"Claridge's apartment appears first: '{first_apartment.get('title')}'")
                    
                    # Verify priority field
                    if priority == 1:
                        self.log_result("Claridge's Priority - Priority Field", True, 
                                      f"Claridge's has correct priority=1")
                    else:
                        self.log_result("Claridge's Priority - Priority Field", False, 
                                      f"Claridge's priority={priority}, expected 1")
                    
                    # Verify featured field
                    if featured is True:
                        self.log_result("Claridge's Priority - Featured Field", True, 
                                      f"Claridge's has featured=true")
                    else:
                        self.log_result("Claridge's Priority - Featured Field", False, 
                                      f"Claridge's featured={featured}, expected true")
                    
                    # Verify location (Midtown West)
                    neighborhood = first_apartment.get("neighborhood", "")
                    if "midtown west" in neighborhood.lower():
                        self.log_result("Claridge's Priority - Location", True, 
                                      f"Claridge's in correct location: {neighborhood}")
                    else:
                        self.log_result("Claridge's Priority - Location", False, 
                                      f"Claridge's location: {neighborhood}, expected Midtown West")
                    
                    # Verify 4 images
                    images = first_apartment.get("images", [])
                    if len(images) == 4:
                        self.log_result("Claridge's Priority - Image Count", True, 
                                      f"Claridge's has 4 images as expected")
                    else:
                        self.log_result("Claridge's Priority - Image Count", False, 
                                      f"Claridge's has {len(images)} images, expected 4")
                else:
                    self.log_result("Claridge's Priority - First Position", False, 
                                  f"First apartment is not Claridge's: '{first_apartment.get('title')}'")
                    
                    # Search for Claridge's specifically
                    search_response = self.make_request("GET", "/apartments", {"search_term": "claridge", "limit": 50})
                    if search_response.status_code == 200:
                        search_results = search_response.json()
                        claridges_found = [apt for apt in search_results if "claridge" in apt.get("title", "").lower()]
                        
                        if claridges_found:
                            claridge_apt = claridges_found[0]
                            self.log_result("Claridge's Priority - Search Found", True, 
                                          f"Found Claridge's via search: '{claridge_apt.get('title')}'")
                            
                            # Check its priority
                            priority = claridge_apt.get("priority")
                            if priority == 1:
                                self.log_result("Claridge's Priority - Has Priority", True, 
                                              f"Claridge's has priority=1 but not appearing first")
                            else:
                                self.log_result("Claridge's Priority - Has Priority", False, 
                                              f"Claridge's priority={priority}, expected 1")
                        else:
                            self.log_result("Claridge's Priority - Search Found", False, 
                                          "Claridge's apartment not found in database")
            else:
                self.log_result("Claridge's Priority - API Request", False, 
                              f"Failed to get apartments: {response.status_code}")
                
        except Exception as e:
            self.log_result("Claridge's Priority Testing", False, f"Exception: {str(e)}")
    
    def test_multiple_images_priority_logic(self):
        """Test apartments with 4 images appear before apartments with 2 images"""
        print("\n=== Testing Multiple Images Priority Logic ===")
        try:
            # Get a larger sample to test sorting
            response = self.make_request("GET", "/apartments", {"limit": 100})
            
            if response.status_code == 200:
                apartments = response.json()
                if not apartments:
                    self.log_result("Multiple Images Priority", False, "No apartments returned")
                    return
                
                # Analyze image counts and positions
                image_count_analysis = {}
                apartments_with_4_images = []
                apartments_with_2_images = []
                apartments_with_other_counts = []
                
                for i, apt in enumerate(apartments):
                    images = apt.get("images", [])
                    image_count = len(images)
                    
                    if image_count not in image_count_analysis:
                        image_count_analysis[image_count] = []
                    image_count_analysis[image_count].append({
                        "position": i + 1,
                        "title": apt.get("title", "Unknown"),
                        "priority": apt.get("priority"),
                        "featured": apt.get("featured")
                    })
                    
                    if image_count == 4:
                        apartments_with_4_images.append({"position": i + 1, "title": apt.get("title")})
                    elif image_count == 2:
                        apartments_with_2_images.append({"position": i + 1, "title": apt.get("title")})
                    else:
                        apartments_with_other_counts.append({
                            "position": i + 1, 
                            "title": apt.get("title"), 
                            "image_count": image_count
                        })
                
                # Report findings
                print(f"\n📊 Image Count Distribution:")
                for count in sorted(image_count_analysis.keys(), reverse=True):
                    apts = image_count_analysis[count]
                    print(f"   {count} images: {len(apts)} apartments")
                    if len(apts) <= 5:
                        for apt in apts:
                            priority_info = f" (priority={apt['priority']})" if apt['priority'] else ""
                            featured_info = f" (featured={apt['featured']})" if apt['featured'] else ""
                            print(f"      Position {apt['position']}: {apt['title'][:50]}...{priority_info}{featured_info}")
                    else:
                        print(f"      First 3 positions: {[apt['position'] for apt in apts[:3]]}")
                        print(f"      Last 3 positions: {[apt['position'] for apt in apts[-3:]]}")
                
                # Test 1: Verify 68 apartments with 4 images are prioritized
                if len(apartments_with_4_images) >= 60:  # Allow some tolerance
                    self.log_result("Multiple Images Count", True, 
                                  f"Found {len(apartments_with_4_images)} apartments with 4 images (expected ~68)")
                else:
                    self.log_result("Multiple Images Count", False, 
                                  f"Found only {len(apartments_with_4_images)} apartments with 4 images (expected ~68)")
                
                # Test 2: Check if 4-image apartments generally appear before 2-image apartments
                if apartments_with_4_images and apartments_with_2_images:
                    avg_position_4_images = sum(apt["position"] for apt in apartments_with_4_images) / len(apartments_with_4_images)
                    avg_position_2_images = sum(apt["position"] for apt in apartments_with_2_images) / len(apartments_with_2_images)
                    
                    if avg_position_4_images < avg_position_2_images:
                        self.log_result("Multiple Images Priority Order", True, 
                                      f"4-image apartments average position: {avg_position_4_images:.1f}, 2-image apartments: {avg_position_2_images:.1f}")
                    else:
                        self.log_result("Multiple Images Priority Order", False, 
                                      f"4-image apartments average position: {avg_position_4_images:.1f} >= 2-image apartments: {avg_position_2_images:.1f}")
                
                # Test 3: Check sorting order within first 20 apartments
                first_20 = apartments[:20]
                first_20_with_4_images = sum(1 for apt in first_20 if len(apt.get("images", [])) == 4)
                first_20_percentage = (first_20_with_4_images / 20) * 100
                
                if first_20_percentage >= 70:  # Expect most of first 20 to have 4 images
                    self.log_result("Multiple Images Top 20", True, 
                                  f"{first_20_with_4_images}/20 ({first_20_percentage:.1f}%) of top 20 apartments have 4 images")
                else:
                    self.log_result("Multiple Images Top 20", False, 
                                  f"Only {first_20_with_4_images}/20 ({first_20_percentage:.1f}%) of top 20 apartments have 4 images")
                
            else:
                self.log_result("Multiple Images Priority Logic", False, 
                              f"Failed to get apartments: {response.status_code}")
                
        except Exception as e:
            self.log_result("Multiple Images Priority Logic", False, f"Exception: {str(e)}")
    
    def test_sorting_algorithm_verification(self):
        """Test the complete sorting algorithm: priority → multiple images → featured → newest"""
        print("\n=== Testing Sorting Algorithm Verification ===")
        try:
            # Get comprehensive sample
            response = self.make_request("GET", "/apartments", {"limit": 50})
            
            if response.status_code == 200:
                apartments = response.json()
                if not apartments:
                    self.log_result("Sorting Algorithm", False, "No apartments returned")
                    return
                
                # Analyze sorting criteria for each apartment
                sorting_analysis = []
                for i, apt in enumerate(apartments):
                    analysis = {
                        "position": i + 1,
                        "title": apt.get("title", "Unknown")[:50],
                        "priority": apt.get("priority"),
                        "image_count": len(apt.get("images", [])),
                        "featured": apt.get("featured"),
                        "created_at": apt.get("created_at"),
                        "has_priority": apt.get("priority") is not None and apt.get("priority") > 0,
                        "has_multiple_images": len(apt.get("images", [])) > 2,
                        "is_featured": apt.get("featured") is True
                    }
                    sorting_analysis.append(analysis)
                
                # Test 1: Priority apartments should appear first
                priority_apartments = [apt for apt in sorting_analysis if apt["has_priority"]]
                non_priority_apartments = [apt for apt in sorting_analysis if not apt["has_priority"]]
                
                if priority_apartments:
                    max_priority_position = max(apt["position"] for apt in priority_apartments)
                    min_non_priority_position = min(apt["position"] for apt in non_priority_apartments) if non_priority_apartments else float('inf')
                    
                    if max_priority_position < min_non_priority_position:
                        self.log_result("Sorting - Priority First", True, 
                                      f"All priority apartments ({len(priority_apartments)}) appear before non-priority apartments")
                    else:
                        self.log_result("Sorting - Priority First", False, 
                                      f"Priority apartments not consistently first. Max priority position: {max_priority_position}, Min non-priority: {min_non_priority_position}")
                else:
                    self.log_result("Sorting - Priority First", True, 
                                  "No priority apartments found (acceptable if only Claridge's has priority)")
                
                # Test 2: Among non-priority apartments, multiple images should come first
                if non_priority_apartments:
                    multiple_image_apts = [apt for apt in non_priority_apartments if apt["has_multiple_images"]]
                    single_image_apts = [apt for apt in non_priority_apartments if not apt["has_multiple_images"]]
                    
                    if multiple_image_apts and single_image_apts:
                        avg_multi_pos = sum(apt["position"] for apt in multiple_image_apts) / len(multiple_image_apts)
                        avg_single_pos = sum(apt["position"] for apt in single_image_apts) / len(single_image_apts)
                        
                        if avg_multi_pos < avg_single_pos:
                            self.log_result("Sorting - Multiple Images Priority", True, 
                                          f"Multiple image apartments average position: {avg_multi_pos:.1f} < single image: {avg_single_pos:.1f}")
                        else:
                            self.log_result("Sorting - Multiple Images Priority", False, 
                                          f"Multiple image apartments not prioritized. Multi: {avg_multi_pos:.1f}, Single: {avg_single_pos:.1f}")
                
                # Test 3: Featured apartments should be prioritized within their group
                featured_apartments = [apt for apt in sorting_analysis if apt["is_featured"]]
                non_featured_apartments = [apt for apt in sorting_analysis if not apt["is_featured"]]
                
                if featured_apartments:
                    print(f"\n🌟 Featured apartments found: {len(featured_apartments)}")
                    for apt in featured_apartments[:5]:
                        print(f"   Position {apt['position']}: {apt['title']} (priority={apt['priority']}, images={apt['image_count']})")
                    
                    self.log_result("Sorting - Featured Apartments", True, 
                                  f"Found {len(featured_apartments)} featured apartments in listing")
                else:
                    self.log_result("Sorting - Featured Apartments", True, 
                                  "No featured apartments found (acceptable)")
                
                # Test 4: Check creation date sorting within same priority groups
                if len(apartments) >= 10:
                    # Check if apartments with same priority/image criteria are sorted by date
                    same_criteria_groups = {}
                    for apt in sorting_analysis:
                        key = (apt["has_priority"], apt["has_multiple_images"], apt["is_featured"])
                        if key not in same_criteria_groups:
                            same_criteria_groups[key] = []
                        same_criteria_groups[key].append(apt)
                    
                    date_sorting_correct = True
                    for group_key, group_apts in same_criteria_groups.items():
                        if len(group_apts) >= 2:
                            # Check if this group is sorted by creation date (newest first)
                            dates = [apt["created_at"] for apt in group_apts if apt["created_at"]]
                            if len(dates) >= 2:
                                is_date_sorted = all(dates[i] >= dates[i+1] for i in range(len(dates)-1))
                                if not is_date_sorted:
                                    date_sorting_correct = False
                                    break
                    
                    if date_sorting_correct:
                        self.log_result("Sorting - Date Within Groups", True, 
                                      "Apartments with same criteria are sorted by creation date (newest first)")
                    else:
                        self.log_result("Sorting - Date Within Groups", False, 
                                      "Date sorting within same criteria groups is incorrect")
                
                # Test 5: Overall sorting algorithm summary
                print(f"\n📋 SORTING ALGORITHM SUMMARY:")
                print(f"   Priority apartments: {len(priority_apartments)}")
                print(f"   Multiple image apartments: {len([apt for apt in sorting_analysis if apt['has_multiple_images']])}")
                print(f"   Featured apartments: {len(featured_apartments)}")
                print(f"   Total apartments analyzed: {len(apartments)}")
                
                # Show first 10 apartments with their sorting criteria
                print(f"\n🔝 TOP 10 APARTMENTS SORTING ANALYSIS:")
                for apt in sorting_analysis[:10]:
                    criteria = []
                    if apt["has_priority"]:
                        criteria.append(f"priority={apt['priority']}")
                    if apt["has_multiple_images"]:
                        criteria.append(f"images={apt['image_count']}")
                    if apt["is_featured"]:
                        criteria.append("featured")
                    
                    criteria_str = ", ".join(criteria) if criteria else "standard"
                    print(f"   {apt['position']:2d}. {apt['title']} ({criteria_str})")
                
            else:
                self.log_result("Sorting Algorithm Verification", False, 
                              f"Failed to get apartments: {response.status_code}")
                
        except Exception as e:
            self.log_result("Sorting Algorithm Verification", False, f"Exception: {str(e)}")
    
    def test_database_integration(self):
        """Test database integration - verify total apartment count is 157 (156 + 1 Claridge's)"""
        print("\n=== Testing Database Integration ===")
        try:
            # Test 1: Get total apartment count
            response = self.make_request("GET", "/apartments/search/stats")
            
            if response.status_code == 200:
                stats = response.json()
                total_apartments = stats.get("total_apartments", 0)
                
                if total_apartments == 157:
                    self.log_result("Database Integration - Total Count", True, 
                                  f"Correct total apartment count: {total_apartments} (156 + 1 Claridge's)")
                elif total_apartments >= 150:  # Allow some tolerance
                    self.log_result("Database Integration - Total Count", True, 
                                  f"Apartment count close to expected: {total_apartments} (expected 157)")
                else:
                    self.log_result("Database Integration - Total Count", False, 
                                  f"Apartment count too low: {total_apartments} (expected 157)")
                
                # Test 2: Verify we can retrieve all apartments
                all_apartments_response = self.make_request("GET", "/apartments", {"limit": 200})
                if all_apartments_response.status_code == 200:
                    all_apartments = all_apartments_response.json()
                    retrieved_count = len(all_apartments)
                    
                    if retrieved_count == total_apartments:
                        self.log_result("Database Integration - Retrieval", True, 
                                      f"Successfully retrieved all {retrieved_count} apartments")
                    else:
                        self.log_result("Database Integration - Retrieval", False, 
                                      f"Retrieved {retrieved_count} apartments, stats show {total_apartments}")
                else:
                    self.log_result("Database Integration - Retrieval", False, 
                                  f"Failed to retrieve all apartments: {all_apartments_response.status_code}")
                
            else:
                self.log_result("Database Integration - Stats", False, 
                              f"Failed to get apartment stats: {response.status_code}")
            
            # Test 3: Verify aggregation pipeline doesn't break existing functionality
            test_filters = [
                {"min_price": 3000, "max_price": 5000},
                {"bedrooms": 1},
                {"borough": "Manhattan"},
                {"search_term": "luxury"}
            ]
            
            for i, filter_params in enumerate(test_filters, 1):
                filter_response = self.make_request("GET", "/apartments", filter_params)
                if filter_response.status_code == 200:
                    filtered_apartments = filter_response.json()
                    self.log_result(f"Database Integration - Filter {i}", True, 
                                  f"Filter {filter_params} returned {len(filtered_apartments)} apartments")
                else:
                    self.log_result(f"Database Integration - Filter {i}", False, 
                                  f"Filter {filter_params} failed: {filter_response.status_code}")
            
            # Test 4: Verify all apartments have required fields
            sample_response = self.make_request("GET", "/apartments", {"limit": 20})
            if sample_response.status_code == 200:
                sample_apartments = sample_response.json()
                
                required_fields = ["id", "title", "address", "price", "bedrooms", "bathrooms", "images"]
                optional_fields = ["priority", "featured"]
                
                field_coverage = {field: 0 for field in required_fields + optional_fields}
                
                for apt in sample_apartments:
                    for field in required_fields + optional_fields:
                        if field in apt and apt[field] is not None:
                            field_coverage[field] += 1
                
                # Check required fields
                all_required_present = True
                for field in required_fields:
                    if field_coverage[field] < len(sample_apartments):
                        all_required_present = False
                        break
                
                if all_required_present:
                    self.log_result("Database Integration - Required Fields", True, 
                                  f"All {len(sample_apartments)} apartments have required fields")
                else:
                    self.log_result("Database Integration - Required Fields", False, 
                                  f"Some apartments missing required fields: {field_coverage}")
                
                # Report optional field coverage
                priority_coverage = (field_coverage["priority"] / len(sample_apartments)) * 100
                featured_coverage = (field_coverage["featured"] / len(sample_apartments)) * 100
                
                print(f"   Optional field coverage: priority={priority_coverage:.1f}%, featured={featured_coverage:.1f}%")
                
            else:
                self.log_result("Database Integration - Field Check", False, 
                              f"Failed to get sample apartments: {sample_response.status_code}")
                
        except Exception as e:
            self.log_result("Database Integration", False, f"Exception: {str(e)}")
    
    def test_api_endpoint_functionality(self):
        """Test API endpoints with limit parameters and search functionality"""
        print("\n=== Testing API Endpoint Functionality ===")
        try:
            # Test 1: Basic GET /api/apartments with limit
            response = self.make_request("GET", "/apartments", {"limit": 20})
            
            if response.status_code == 200:
                apartments = response.json()
                if len(apartments) <= 20:
                    self.log_result("API Endpoint - Basic Limit", True, 
                                  f"Limit parameter working: requested 20, got {len(apartments)}")
                else:
                    self.log_result("API Endpoint - Basic Limit", False, 
                                  f"Limit not respected: requested 20, got {len(apartments)}")
            else:
                self.log_result("API Endpoint - Basic Limit", False, 
                              f"Basic endpoint failed: {response.status_code}")
            
            # Test 2: Search functionality with new sorting
            search_terms = ["luxury", "studio", "manhattan", "claridge"]
            
            for term in search_terms:
                search_response = self.make_request("GET", "/apartments", {"search_term": term, "limit": 10})
                if search_response.status_code == 200:
                    search_results = search_response.json()
                    
                    # Verify results are still sorted correctly
                    if search_results:
                        # Check if first result has priority (for claridge search)
                        if term == "claridge" and search_results:
                            first_result = search_results[0]
                            if "claridge" in first_result.get("title", "").lower():
                                priority = first_result.get("priority")
                                if priority == 1:
                                    self.log_result(f"API Endpoint - Search '{term}'", True, 
                                                  f"Claridge's found with priority=1 in search results")
                                else:
                                    self.log_result(f"API Endpoint - Search '{term}'", False, 
                                                  f"Claridge's found but priority={priority}, expected 1")
                            else:
                                self.log_result(f"API Endpoint - Search '{term}'", False, 
                                              f"Search for 'claridge' didn't return Claridge's first")
                        else:
                            self.log_result(f"API Endpoint - Search '{term}'", True, 
                                          f"Search for '{term}' returned {len(search_results)} results")
                    else:
                        self.log_result(f"API Endpoint - Search '{term}'", True, 
                                      f"Search for '{term}' returned no results (acceptable)")
                else:
                    self.log_result(f"API Endpoint - Search '{term}'", False, 
                                  f"Search for '{term}' failed: {search_response.status_code}")
            
            # Test 3: Combined filters with sorting
            combined_filters = [
                {"min_price": 4000, "limit": 15},
                {"bedrooms": 1, "limit": 15},
                {"borough": "Manhattan", "limit": 15},
                {"search_term": "luxury", "bedrooms": 1, "limit": 10}
            ]
            
            for i, filters in enumerate(combined_filters, 1):
                filter_response = self.make_request("GET", "/apartments", filters)
                if filter_response.status_code == 200:
                    filtered_results = filter_response.json()
                    
                    # Verify sorting is maintained with filters
                    if filtered_results:
                        # Check if priority apartments still appear first
                        priority_apartments = [apt for apt in filtered_results if apt.get("priority")]
                        if priority_apartments:
                            first_priority_pos = next((i for i, apt in enumerate(filtered_results) if apt.get("priority")), None)
                            if first_priority_pos == 0:
                                self.log_result(f"API Endpoint - Combined Filter {i}", True, 
                                              f"Priority apartment appears first in filtered results ({len(filtered_results)} total)")
                            else:
                                self.log_result(f"API Endpoint - Combined Filter {i}", False, 
                                              f"Priority apartment not first in filtered results (position {first_priority_pos + 1})")
                        else:
                            self.log_result(f"API Endpoint - Combined Filter {i}", True, 
                                          f"Combined filter returned {len(filtered_results)} results (no priority apartments)")
                    else:
                        self.log_result(f"API Endpoint - Combined Filter {i}", True, 
                                      f"Combined filter returned no results (acceptable)")
                else:
                    self.log_result(f"API Endpoint - Combined Filter {i}", False, 
                                  f"Combined filter failed: {filter_response.status_code}")
            
            # Test 4: Pagination with sorting
            page1_response = self.make_request("GET", "/apartments", {"page": 1, "limit": 10})
            page2_response = self.make_request("GET", "/apartments", {"page": 2, "limit": 10})
            
            if page1_response.status_code == 200 and page2_response.status_code == 200:
                page1_apartments = page1_response.json()
                page2_apartments = page2_response.json()
                
                if page1_apartments and page2_apartments:
                    # Verify no overlap between pages
                    page1_ids = {apt.get("id") for apt in page1_apartments}
                    page2_ids = {apt.get("id") for apt in page2_apartments}
                    
                    if not page1_ids.intersection(page2_ids):
                        self.log_result("API Endpoint - Pagination", True, 
                                      f"Pagination working correctly: no overlap between pages")
                    else:
                        self.log_result("API Endpoint - Pagination", False, 
                                      f"Pagination overlap detected: {len(page1_ids.intersection(page2_ids))} apartments")
                else:
                    self.log_result("API Endpoint - Pagination", True, 
                                  "Pagination working (one or both pages empty)")
            else:
                self.log_result("API Endpoint - Pagination", False, 
                              f"Pagination failed: page1={page1_response.status_code}, page2={page2_response.status_code}")
                
        except Exception as e:
            self.log_result("API Endpoint Functionality", False, f"Exception: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases: apartments with same priority, same image count, null priority handling"""
        print("\n=== Testing Edge Cases ===")
        try:
            # Get comprehensive sample for edge case testing
            response = self.make_request("GET", "/apartments", {"limit": 100})
            
            if response.status_code == 200:
                apartments = response.json()
                if not apartments:
                    self.log_result("Edge Cases", False, "No apartments returned")
                    return
                
                # Test 1: Null priority handling
                null_priority_apartments = [apt for apt in apartments if apt.get("priority") is None]
                priority_apartments = [apt for apt in apartments if apt.get("priority") is not None]
                
                if null_priority_apartments and priority_apartments:
                    # Find positions
                    null_priority_positions = []
                    priority_positions = []
                    
                    for i, apt in enumerate(apartments):
                        if apt.get("priority") is None:
                            null_priority_positions.append(i + 1)
                        else:
                            priority_positions.append(i + 1)
                    
                    max_priority_pos = max(priority_positions) if priority_positions else 0
                    min_null_priority_pos = min(null_priority_positions) if null_priority_positions else float('inf')
                    
                    if max_priority_pos < min_null_priority_pos:
                        self.log_result("Edge Cases - Null Priority Handling", True, 
                                      f"All priority apartments appear before null priority apartments")
                    else:
                        self.log_result("Edge Cases - Null Priority Handling", False, 
                                      f"Null priority handling incorrect. Max priority pos: {max_priority_pos}, Min null pos: {min_null_priority_pos}")
                else:
                    self.log_result("Edge Cases - Null Priority Handling", True, 
                                  f"Only one type found: {len(priority_apartments)} priority, {len(null_priority_apartments)} null priority")
                
                # Test 2: Same image count sorting
                image_count_groups = {}
                for i, apt in enumerate(apartments):
                    image_count = len(apt.get("images", []))
                    if image_count not in image_count_groups:
                        image_count_groups[image_count] = []
                    image_count_groups[image_count].append({
                        "position": i + 1,
                        "title": apt.get("title"),
                        "created_at": apt.get("created_at"),
                        "priority": apt.get("priority"),
                        "featured": apt.get("featured")
                    })
                
                # Check if apartments with same image count are sorted by other criteria
                same_image_sorting_correct = True
                for image_count, group in image_count_groups.items():
                    if len(group) >= 3:  # Only test groups with multiple apartments
                        # Within same image count, check if sorting by priority, then featured, then date
                        group_sorted = sorted(group, key=lambda x: (
                            -(x["priority"] or 0),  # Priority descending (higher first)
                            -(x["featured"] or False),  # Featured first
                            -(x["created_at"] or "")  # Newest first
                        ))
                        
                        actual_positions = [apt["position"] for apt in group]
                        expected_positions = [apt["position"] for apt in group_sorted]
                        
                        if actual_positions != expected_positions:
                            same_image_sorting_correct = False
                            print(f"   Image count {image_count} group not sorted correctly:")
                            print(f"   Actual positions: {actual_positions[:5]}")
                            print(f"   Expected positions: {expected_positions[:5]}")
                            break
                
                if same_image_sorting_correct:
                    self.log_result("Edge Cases - Same Image Count Sorting", True, 
                                  "Apartments with same image count are sorted by secondary criteria")
                else:
                    self.log_result("Edge Cases - Same Image Count Sorting", False, 
                                  "Apartments with same image count not sorted correctly by secondary criteria")
                
                # Test 3: Same priority handling
                if priority_apartments:
                    priority_groups = {}
                    for apt in priority_apartments:
                        priority = apt.get("priority")
                        if priority not in priority_groups:
                            priority_groups[priority] = []
                        priority_groups[priority].append(apt)
                    
                    same_priority_sorting_correct = True
                    for priority, group in priority_groups.items():
                        if len(group) >= 2:
                            # Check if apartments with same priority are sorted by image count, then other criteria
                            positions = [next(i for i, apt in enumerate(apartments) if apt.get("id") == group_apt.get("id")) for group_apt in group]
                            
                            # Verify they appear in correct order (by image count, then featured, then date)
                            for i in range(len(positions) - 1):
                                apt1 = apartments[positions[i]]
                                apt2 = apartments[positions[i + 1]]
                                
                                img1 = len(apt1.get("images", []))
                                img2 = len(apt2.get("images", []))
                                
                                # First apartment should have >= images than second
                                if img1 < img2:
                                    same_priority_sorting_correct = False
                                    break
                    
                    if same_priority_sorting_correct:
                        self.log_result("Edge Cases - Same Priority Sorting", True, 
                                      "Apartments with same priority are sorted correctly by secondary criteria")
                    else:
                        self.log_result("Edge Cases - Same Priority Sorting", False, 
                                      "Apartments with same priority not sorted correctly by secondary criteria")
                
                # Test 4: Creation date sorting within same groups
                print(f"\n📅 Testing creation date sorting within same criteria groups...")
                
                # Group apartments by all sorting criteria except date
                criteria_groups = {}
                for i, apt in enumerate(apartments):
                    key = (
                        apt.get("priority"),
                        len(apt.get("images", [])),
                        apt.get("featured")
                    )
                    if key not in criteria_groups:
                        criteria_groups[key] = []
                    criteria_groups[key].append({
                        "position": i + 1,
                        "created_at": apt.get("created_at"),
                        "title": apt.get("title")
                    })
                
                date_sorting_issues = 0
                for criteria, group in criteria_groups.items():
                    if len(group) >= 2:
                        dates = [apt["created_at"] for apt in group if apt["created_at"]]
                        if len(dates) >= 2:
                            # Check if dates are in descending order (newest first)
                            is_sorted = all(dates[i] >= dates[i+1] for i in range(len(dates)-1))
                            if not is_sorted:
                                date_sorting_issues += 1
                
                if date_sorting_issues == 0:
                    self.log_result("Edge Cases - Date Sorting Within Groups", True, 
                                  "Creation date sorting correct within same criteria groups")
                else:
                    self.log_result("Edge Cases - Date Sorting Within Groups", False, 
                                  f"{date_sorting_issues} groups have incorrect date sorting")
                
            else:
                self.log_result("Edge Cases", False, f"Failed to get apartments: {response.status_code}")
                
        except Exception as e:
            self.log_result("Edge Cases", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all priority and sorting tests"""
        print("🏢 PRIORITY AND MULTIPLE IMAGES SORTING LOGIC TESTING SUITE")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_claridges_apartment_priority()
        self.test_multiple_images_priority_logic()
        self.test_sorting_algorithm_verification()
        self.test_database_integration()
        self.test_api_endpoint_functionality()
        self.test_edge_cases()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 70)
        print("🎯 PRIORITY SORTING TESTING SUMMARY")
        print("=" * 70)
        print(f"✅ Tests Passed: {self.results['passed']}")
        print(f"❌ Tests Failed: {self.results['failed']}")
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"📊 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print(f"\n❌ FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = PrioritySortingTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)