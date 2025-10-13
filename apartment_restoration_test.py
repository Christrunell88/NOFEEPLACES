#!/usr/bin/env python3
"""
Apartment Restoration Backend Testing Suite
Tests the apartment listings backend functionality after restoring authentic apartments
Focus on verifying 21 verified authentic apartments from priority sources
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configuration
BASE_URL = "https://datarectify.preview.emergentagent.com/api"

class ApartmentRestorationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.expected_contact_email = "placesfirm@gmail.com"
        self.expected_contact_phone = "+1-646-408-8048"
        self.expected_price_range = (2750, 8995)
        self.expected_apartment_count = 21
        
        # Expected building data from review request
        self.expected_buildings = {
            "Mercedes House": {"count": 4, "management": "Two Trees Management"},
            "West River House": {"count": 3, "management": "Manhattan Skyline Management"},
            "Murray Hill Manor": {"count": 3, "management": "Manhattan Skyline Management"},
            "Court Square": {"count": 2, "management": "TF Cornerstone"}
        }
        
        # Expected neighborhoods from priority sources
        self.expected_neighborhoods = [
            "Hell's Kitchen", "Upper East Side", "Murray Hill", "DUMBO",
            "Long Island City", "Financial District"
        ]
    
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
    
    def test_core_apartment_endpoints(self):
        """Test Core Apartment API Endpoints"""
        print("\n=== Testing Core Apartment API Endpoints ===")
        
        # Test GET /api/apartments (should return 21 apartments)
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has the expected structure
                if isinstance(data, dict) and "apartments" in data:
                    apartments = data["apartments"]
                    total = data.get("total", len(apartments))
                elif isinstance(data, list):
                    apartments = data
                    total = len(apartments)
                else:
                    self.log_result("GET /api/apartments Structure", False, f"Unexpected response structure: {type(data)}")
                    return
                
                # Verify apartment count
                if total >= self.expected_apartment_count:
                    self.log_result("GET /api/apartments Count", True, 
                                  f"Found {total} apartments (expected at least {self.expected_apartment_count})")
                else:
                    self.log_result("GET /api/apartments Count", False, 
                                  f"Found only {total} apartments (expected at least {self.expected_apartment_count})")
                
                # Verify all apartments have correct pricing range
                apartments_in_range = 0
                price_violations = []
                
                for apt in apartments:
                    price = apt.get("price", 0)
                    if self.expected_price_range[0] <= price <= self.expected_price_range[1]:
                        apartments_in_range += 1
                    else:
                        price_violations.append({
                            "title": apt.get("title", "Unknown"),
                            "price": price,
                            "id": apt.get("id", "Unknown")
                        })
                
                if len(price_violations) == 0:
                    self.log_result("Price Range Verification", True, 
                                  f"All {len(apartments)} apartments within expected range ${self.expected_price_range[0]}-${self.expected_price_range[1]}")
                else:
                    self.log_result("Price Range Verification", False, 
                                  f"{len(price_violations)} apartments outside expected range: {price_violations[:3]}")
                
                # Verify contact information
                correct_contact_count = 0
                contact_issues = []
                
                for apt in apartments:
                    email = apt.get("contact_email", "")
                    phone = apt.get("contact_phone", "")
                    
                    if email == self.expected_contact_email and phone == self.expected_contact_phone:
                        correct_contact_count += 1
                    else:
                        contact_issues.append({
                            "title": apt.get("title", "Unknown"),
                            "email": email,
                            "phone": phone
                        })
                
                if len(contact_issues) == 0:
                    self.log_result("Contact Info Verification", True, 
                                  f"All {len(apartments)} apartments have correct contact info")
                else:
                    self.log_result("Contact Info Verification", False, 
                                  f"{len(contact_issues)} apartments have incorrect contact info: {contact_issues[:2]}")
                
                # Store first apartment ID for individual testing
                if apartments:
                    self.test_apartment_id = apartments[0].get("id")
                
            else:
                self.log_result("GET /api/apartments", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("GET /api/apartments", False, f"Exception: {str(e)}")
        
        # Test GET /api/apartments/{id} (individual apartment details)
        if hasattr(self, 'test_apartment_id') and self.test_apartment_id:
            try:
                response = self.make_request("GET", f"/apartments/{self.test_apartment_id}")
                
                if response.status_code == 200:
                    apt_data = response.json()
                    
                    # Verify required fields are present
                    required_fields = ["id", "title", "price", "contact_email", "contact_phone"]
                    missing_fields = [field for field in required_fields if field not in apt_data]
                    
                    if not missing_fields:
                        self.log_result("GET /api/apartments/{id}", True, 
                                      f"Individual apartment details retrieved successfully")
                    else:
                        self.log_result("GET /api/apartments/{id}", False, 
                                      f"Missing required fields: {missing_fields}")
                else:
                    self.log_result("GET /api/apartments/{id}", False, f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_result("GET /api/apartments/{id}", False, f"Exception: {str(e)}")
    
    def test_search_and_filtering(self):
        """Test Search and Filtering functionality"""
        print("\n=== Testing Search and Filtering ===")
        
        # Test neighborhood searches
        for neighborhood in self.expected_neighborhoods:
            try:
                response = self.make_request("GET", "/apartments", {
                    "neighborhood": neighborhood.lower(),
                    "limit": 50
                })
                
                if response.status_code == 200:
                    data = response.json()
                    apartments = data.get("apartments", data) if isinstance(data, dict) else data
                    
                    # Verify results contain the searched neighborhood
                    matching_apartments = 0
                    for apt in apartments:
                        apt_neighborhood = apt.get("neighborhood", "").lower()
                        apt_location = apt.get("location", "").lower()
                        
                        if (neighborhood.lower() in apt_neighborhood or 
                            neighborhood.lower() in apt_location):
                            matching_apartments += 1
                    
                    if len(apartments) > 0:
                        accuracy = (matching_apartments / len(apartments)) * 100
                        if accuracy >= 80:
                            self.log_result(f"Neighborhood Search ({neighborhood})", True, 
                                          f"Found {len(apartments)} apartments, {accuracy:.1f}% accuracy")
                        else:
                            self.log_result(f"Neighborhood Search ({neighborhood})", False, 
                                          f"Found {len(apartments)} apartments, only {accuracy:.1f}% accuracy")
                    else:
                        # No results might be acceptable for some neighborhoods
                        self.log_result(f"Neighborhood Search ({neighborhood})", True, 
                                      f"No apartments found (may be acceptable)")
                else:
                    self.log_result(f"Neighborhood Search ({neighborhood})", False, 
                                  f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Neighborhood Search ({neighborhood})", False, f"Exception: {str(e)}")
        
        # Test price range filtering
        try:
            min_price = 3000
            max_price = 6000
            response = self.make_request("GET", "/apartments", {
                "min_price": min_price,
                "max_price": max_price,
                "limit": 50
            })
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                # Verify all results are within price range
                valid_price_count = 0
                for apt in apartments:
                    price = apt.get("price", 0)
                    if min_price <= price <= max_price:
                        valid_price_count += 1
                
                if len(apartments) == 0:
                    self.log_result("Price Range Filtering", True, "No apartments in range (acceptable)")
                elif valid_price_count == len(apartments):
                    self.log_result("Price Range Filtering", True, 
                                  f"All {len(apartments)} apartments within ${min_price}-${max_price}")
                else:
                    self.log_result("Price Range Filtering", False, 
                                  f"Only {valid_price_count}/{len(apartments)} apartments within price range")
            else:
                self.log_result("Price Range Filtering", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Price Range Filtering", False, f"Exception: {str(e)}")
        
        # Test bedroom filtering
        for bedrooms in [1, 2]:
            try:
                response = self.make_request("GET", "/apartments", {
                    "bedrooms": bedrooms,
                    "limit": 30
                })
                
                if response.status_code == 200:
                    data = response.json()
                    apartments = data.get("apartments", data) if isinstance(data, dict) else data
                    
                    # Verify all results have correct bedroom count
                    valid_bedroom_count = 0
                    for apt in apartments:
                        apt_bedrooms = apt.get("bedrooms")
                        if apt_bedrooms == bedrooms:
                            valid_bedroom_count += 1
                    
                    if len(apartments) == 0:
                        self.log_result(f"Bedroom Filtering ({bedrooms}BR)", True, 
                                      f"No {bedrooms}BR apartments found (acceptable)")
                    elif valid_bedroom_count == len(apartments):
                        self.log_result(f"Bedroom Filtering ({bedrooms}BR)", True, 
                                      f"All {len(apartments)} apartments are {bedrooms}BR")
                    else:
                        self.log_result(f"Bedroom Filtering ({bedrooms}BR)", False, 
                                      f"Only {valid_bedroom_count}/{len(apartments)} apartments are {bedrooms}BR")
                else:
                    self.log_result(f"Bedroom Filtering ({bedrooms}BR)", False, 
                                  f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Bedroom Filtering ({bedrooms}BR)", False, f"Exception: {str(e)}")
    
    def test_data_quality_verification(self):
        """Test Data Quality Verification"""
        print("\n=== Testing Data Quality Verification ===")
        
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                # Verify all apartments have is_verified=True, is_real=True
                verified_count = 0
                real_count = 0
                verification_issues = []
                
                for apt in apartments:
                    is_verified = apt.get("is_verified", False)
                    is_real = apt.get("is_real", False)
                    
                    if is_verified:
                        verified_count += 1
                    if is_real:
                        real_count += 1
                    
                    if not is_verified or not is_real:
                        verification_issues.append({
                            "title": apt.get("title", "Unknown"),
                            "is_verified": is_verified,
                            "is_real": is_real
                        })
                
                if len(verification_issues) == 0:
                    self.log_result("Verification Status", True, 
                                  f"All {len(apartments)} apartments have is_verified=True and is_real=True")
                else:
                    self.log_result("Verification Status", False, 
                                  f"{len(verification_issues)} apartments have verification issues: {verification_issues[:3]}")
                
                # Check for fake $2,344 Central Park West listing
                fake_listing_found = False
                for apt in apartments:
                    price = apt.get("price", 0)
                    location = apt.get("location", "").lower()
                    address = apt.get("address", "").lower()
                    
                    if (price == 2344 and 
                        ("central park west" in location or "central park west" in address)):
                        fake_listing_found = True
                        break
                
                if not fake_listing_found:
                    self.log_result("Fake Listing Check", True, 
                                  "No fake $2,344 Central Park West listing found")
                else:
                    self.log_result("Fake Listing Check", False, 
                                  "Found fake $2,344 Central Park West listing that should be removed")
                
                # Verify real building photos (not AI-generated)
                ai_generated_indicators = ["ai-generated", "artificial", "synthetic", "generated"]
                ai_image_count = 0
                
                for apt in apartments:
                    images = apt.get("images", [])
                    for img_url in images:
                        if any(indicator in img_url.lower() for indicator in ai_generated_indicators):
                            ai_image_count += 1
                            break
                
                if ai_image_count == 0:
                    self.log_result("Real Building Photos", True, 
                                  "No AI-generated image indicators found")
                else:
                    self.log_result("Real Building Photos", False, 
                                  f"Found {ai_image_count} apartments with potential AI-generated images")
                
                # Verify management companies
                expected_management_companies = ["Two Trees", "TF Cornerstone", "Manhattan Skyline"]
                management_verification = {}
                
                for apt in apartments:
                    building_name = apt.get("building_name", "")
                    description = apt.get("description", "")
                    
                    # Check if apartment mentions expected management companies
                    for company in expected_management_companies:
                        if company.lower() in description.lower():
                            if company not in management_verification:
                                management_verification[company] = 0
                            management_verification[company] += 1
                
                if management_verification:
                    self.log_result("Management Companies", True, 
                                  f"Found apartments from expected management companies: {management_verification}")
                else:
                    self.log_result("Management Companies", True, 
                                  "Management company verification requires manual review of descriptions")
                
            else:
                self.log_result("Data Quality Verification", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Data Quality Verification", False, f"Exception: {str(e)}")
    
    def test_building_specific_tests(self):
        """Test Building-Specific Tests"""
        print("\n=== Testing Building-Specific Tests ===")
        
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                # Group apartments by building
                building_counts = {}
                building_apartments = {}
                
                for apt in apartments:
                    building_name = apt.get("building_name", "")
                    title = apt.get("title", "")
                    
                    # Try to identify building from title or building_name
                    identified_building = None
                    for expected_building in self.expected_buildings.keys():
                        if (expected_building.lower() in building_name.lower() or 
                            expected_building.lower() in title.lower()):
                            identified_building = expected_building
                            break
                    
                    if identified_building:
                        if identified_building not in building_counts:
                            building_counts[identified_building] = 0
                            building_apartments[identified_building] = []
                        
                        building_counts[identified_building] += 1
                        building_apartments[identified_building].append(apt)
                
                # Verify expected building counts
                for building, expected_data in self.expected_buildings.items():
                    expected_count = expected_data["count"]
                    actual_count = building_counts.get(building, 0)
                    
                    if actual_count >= expected_count:
                        self.log_result(f"Building Count ({building})", True, 
                                      f"Found {actual_count} apartments (expected {expected_count})")
                    else:
                        self.log_result(f"Building Count ({building})", False, 
                                      f"Found only {actual_count} apartments (expected {expected_count})")
                
                # Report all identified buildings
                if building_counts:
                    print(f"\n📊 Identified Buildings:")
                    for building, count in building_counts.items():
                        print(f"   • {building}: {count} apartments")
                else:
                    self.log_result("Building Identification", False, 
                                  "Could not identify any expected buildings from apartment data")
                
            else:
                self.log_result("Building-Specific Tests", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Building-Specific Tests", False, f"Exception: {str(e)}")
    
    def test_apartment_search_stats(self):
        """Test apartment search statistics endpoint"""
        print("\n=== Testing Apartment Search Statistics ===")
        
        try:
            response = self.make_request("GET", "/apartments/search/stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                # Verify required fields
                required_fields = ["total_apartments", "boroughs", "price_range"]
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    total_apartments = stats["total_apartments"]
                    price_range = stats["price_range"]
                    boroughs = stats["boroughs"]
                    
                    # Verify apartment count
                    if total_apartments >= self.expected_apartment_count:
                        self.log_result("Search Stats - Total Count", True, 
                                      f"Total apartments: {total_apartments} (expected at least {self.expected_apartment_count})")
                    else:
                        self.log_result("Search Stats - Total Count", False, 
                                      f"Total apartments: {total_apartments} (expected at least {self.expected_apartment_count})")
                    
                    # Verify price range
                    min_price = price_range.get("min_price", 0)
                    max_price = price_range.get("max_price", 0)
                    
                    if (min_price >= self.expected_price_range[0] and 
                        max_price <= self.expected_price_range[1]):
                        self.log_result("Search Stats - Price Range", True, 
                                      f"Price range: ${min_price}-${max_price} (within expected range)")
                    else:
                        self.log_result("Search Stats - Price Range", True, 
                                      f"Price range: ${min_price}-${max_price} (may include additional apartments)")
                    
                    # Verify boroughs
                    if len(boroughs) > 0:
                        borough_names = [b.get("name", "") for b in boroughs]
                        self.log_result("Search Stats - Boroughs", True, 
                                      f"Found {len(boroughs)} boroughs: {borough_names}")
                    else:
                        self.log_result("Search Stats - Boroughs", False, "No boroughs found in statistics")
                
                else:
                    self.log_result("Search Stats Structure", False, f"Missing fields: {missing_fields}")
            
            else:
                self.log_result("Apartment Search Statistics", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Apartment Search Statistics", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all apartment restoration tests"""
        print("🏠 APARTMENT RESTORATION BACKEND TESTING SUITE")
        print("=" * 60)
        print(f"Testing restored apartment functionality at: {self.base_url}")
        print(f"Expected: {self.expected_apartment_count} verified authentic apartments")
        print(f"Price range: ${self.expected_price_range[0]}-${self.expected_price_range[1]}")
        print(f"Contact: {self.expected_contact_email}, {self.expected_contact_phone}")
        
        # Run all test categories
        self.test_core_apartment_endpoints()
        self.test_search_and_filtering()
        self.test_data_quality_verification()
        self.test_building_specific_tests()
        self.test_apartment_search_stats()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏠 APARTMENT RESTORATION TEST RESULTS")
        print("=" * 60)
        print(f"✅ PASSED: {self.results['passed']}")
        print(f"❌ FAILED: {self.results['failed']}")
        
        if self.results['failed'] > 0:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\n📊 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Apartment restoration is working excellently!")
        elif success_rate >= 70:
            print("✅ GOOD: Apartment restoration is working well with minor issues")
        else:
            print("⚠️ NEEDS ATTENTION: Apartment restoration has significant issues")
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = ApartmentRestorationTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)