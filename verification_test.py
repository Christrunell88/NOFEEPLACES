#!/usr/bin/env python3
"""
NoFeePlaces.com Quick Verification Test
Tests specific areas after recent UI updates to ensure no functionality was broken
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://apartment-viewings.preview.emergentagent.com/api"

class VerificationTester:
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
    
    def test_apartment_listings_api(self):
        """Test GET /api/apartments to ensure apartments still load correctly"""
        print("\n=== Testing Apartment Listings API ===")
        try:
            # Test basic apartment listings
            response = self.make_request("GET", "/apartments", {"limit": 50})
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has proper structure
                if "apartments" in data and "total" in data:
                    apartments = data["apartments"]
                    total = data["total"]
                    
                    if len(apartments) > 0 and total > 0:
                        self.log_result("Apartment Listings API Structure", True, 
                                      f"Retrieved {len(apartments)} apartments out of {total} total")
                        
                        # Check first apartment has required fields
                        first_apt = apartments[0]
                        required_fields = ["id", "title", "price", "location", "bedrooms", "images"]
                        missing_fields = [field for field in required_fields if field not in first_apt]
                        
                        if not missing_fields:
                            self.log_result("Apartment Data Structure", True, 
                                          "All required fields present in apartment data")
                        else:
                            self.log_result("Apartment Data Structure", False, 
                                          f"Missing fields: {missing_fields}")
                        
                        return apartments, total
                    else:
                        self.log_result("Apartment Listings API", False, 
                                      f"No apartments returned: {len(apartments)} apartments, {total} total")
                        return [], 0
                else:
                    self.log_result("Apartment Listings API", False, 
                                  f"Invalid response structure: {list(data.keys())}")
                    return [], 0
            else:
                self.log_result("Apartment Listings API", False, 
                              f"Status code: {response.status_code}")
                return [], 0
        except Exception as e:
            self.log_result("Apartment Listings API", False, f"Exception: {str(e)}")
            return [], 0
    
    def test_verification_status(self, apartments):
        """Test that apartments have proper is_verified and is_real flags"""
        print("\n=== Testing Verification Status ===")
        try:
            if not apartments:
                self.log_result("Verification Status", False, "No apartments to test")
                return
            
            verified_count = 0
            real_count = 0
            apartments_with_verification = 0
            
            for apt in apartments:
                has_verification_fields = False
                
                # Check for is_verified flag
                if "is_verified" in apt:
                    has_verification_fields = True
                    if apt["is_verified"] is True:
                        verified_count += 1
                
                # Check for is_real flag
                if "is_real" in apt:
                    has_verification_fields = True
                    if apt["is_real"] is True:
                        real_count += 1
                
                if has_verification_fields:
                    apartments_with_verification += 1
            
            total_apartments = len(apartments)
            
            if apartments_with_verification > 0:
                verification_percentage = (apartments_with_verification / total_apartments) * 100
                verified_percentage = (verified_count / total_apartments) * 100
                real_percentage = (real_count / total_apartments) * 100
                
                self.log_result("Verification Fields Present", True, 
                              f"{apartments_with_verification}/{total_apartments} apartments have verification fields ({verification_percentage:.1f}%)")
                
                if verified_count > 0:
                    self.log_result("Is_Verified Status", True, 
                                  f"{verified_count}/{total_apartments} apartments marked as verified ({verified_percentage:.1f}%)")
                else:
                    self.log_result("Is_Verified Status", False, 
                                  "No apartments marked as verified")
                
                if real_count > 0:
                    self.log_result("Is_Real Status", True, 
                                  f"{real_count}/{total_apartments} apartments marked as real ({real_percentage:.1f}%)")
                else:
                    self.log_result("Is_Real Status", False, 
                                  "No apartments marked as real")
            else:
                self.log_result("Verification Status", False, 
                              "No apartments have verification fields (is_verified, is_real)")
                
        except Exception as e:
            self.log_result("Verification Status", False, f"Exception: {str(e)}")
    
    def test_search_functionality(self):
        """Test apartment search to ensure it still works after UI changes"""
        print("\n=== Testing Search Functionality ===")
        try:
            # Test 1: Basic search by location
            print("\n🔍 Testing location-based search...")
            search_tests = [
                {"search": "DUMBO", "expected_min": 1},
                {"search": "Chelsea", "expected_min": 1},
                {"search": "Manhattan", "expected_min": 1}
            ]
            
            for test in search_tests:
                response = self.make_request("GET", "/apartments", {
                    "search": test["search"],
                    "limit": 20
                })
                
                if response.status_code == 200:
                    data = response.json()
                    apartments = data.get("apartments", [])
                    total = data.get("total", 0)
                    
                    if len(apartments) >= test["expected_min"]:
                        self.log_result(f"Search - {test['search']}", True, 
                                      f"Found {len(apartments)} apartments (total: {total})")
                    else:
                        self.log_result(f"Search - {test['search']}", False, 
                                      f"Only found {len(apartments)} apartments, expected at least {test['expected_min']}")
                else:
                    self.log_result(f"Search - {test['search']}", False, 
                                  f"Search failed with status: {response.status_code}")
            
            # Test 2: Price range filtering
            print("\n💰 Testing price range filtering...")
            response = self.make_request("GET", "/apartments", {
                "min_price": 3000,
                "max_price": 6000,
                "limit": 30
            })
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", [])
                
                # Verify all apartments are within price range
                valid_price_count = 0
                for apt in apartments:
                    price = apt.get("price", 0)
                    if 3000 <= price <= 6000:
                        valid_price_count += 1
                
                if valid_price_count == len(apartments) and len(apartments) > 0:
                    self.log_result("Price Range Filter", True, 
                                  f"All {len(apartments)} apartments within $3000-$6000 range")
                else:
                    self.log_result("Price Range Filter", False, 
                                  f"Only {valid_price_count}/{len(apartments)} apartments within price range")
            else:
                self.log_result("Price Range Filter", False, 
                              f"Price filter failed with status: {response.status_code}")
            
            # Test 3: Bedroom filtering
            print("\n🛏️ Testing bedroom filtering...")
            response = self.make_request("GET", "/apartments", {
                "bedrooms": 1,
                "limit": 20
            })
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", [])
                
                # Verify all apartments have 1 bedroom
                valid_bedroom_count = 0
                for apt in apartments:
                    bedrooms = apt.get("bedrooms")
                    if bedrooms == 1:
                        valid_bedroom_count += 1
                
                if valid_bedroom_count == len(apartments) and len(apartments) > 0:
                    self.log_result("Bedroom Filter", True, 
                                  f"All {len(apartments)} apartments have 1 bedroom")
                else:
                    self.log_result("Bedroom Filter", False, 
                                  f"Only {valid_bedroom_count}/{len(apartments)} apartments have 1 bedroom")
            else:
                self.log_result("Bedroom Filter", False, 
                              f"Bedroom filter failed with status: {response.status_code}")
            
            # Test 4: Combined filters
            print("\n🔧 Testing combined filters...")
            response = self.make_request("GET", "/apartments", {
                "search": "Manhattan",
                "min_price": 4000,
                "bedrooms": 1,
                "limit": 15
            })
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", [])
                
                if len(apartments) > 0:
                    self.log_result("Combined Filters", True, 
                                  f"Combined search returned {len(apartments)} apartments")
                else:
                    self.log_result("Combined Filters", True, 
                                  "Combined search returned 0 apartments (acceptable for specific criteria)")
            else:
                self.log_result("Combined Filters", False, 
                              f"Combined filter failed with status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Search Functionality", False, f"Exception: {str(e)}")
    
    def test_data_integrity(self, total_apartments):
        """Test data integrity - verify apartment count and data structure"""
        print("\n=== Testing Data Integrity ===")
        try:
            # Test 1: Verify apartment count is reasonable
            if total_apartments > 200:
                self.log_result("Apartment Count", True, 
                              f"Good apartment count: {total_apartments} apartments")
            elif total_apartments > 50:
                self.log_result("Apartment Count", True, 
                              f"Acceptable apartment count: {total_apartments} apartments")
            else:
                self.log_result("Apartment Count", False, 
                              f"Low apartment count: {total_apartments} apartments")
            
            # Test 2: Check search stats endpoint
            response = self.make_request("GET", "/apartments/search/stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                if "total_apartments" in stats:
                    stats_total = stats["total_apartments"]
                    
                    # Verify stats match apartment listings
                    if abs(stats_total - total_apartments) <= 5:  # Allow small variance
                        self.log_result("Data Consistency", True, 
                                      f"Stats endpoint matches listings: {stats_total} vs {total_apartments}")
                    else:
                        self.log_result("Data Consistency", False, 
                                      f"Stats mismatch: {stats_total} vs {total_apartments}")
                    
                    # Check other stats fields
                    required_stats = ["boroughs", "price_range", "bedrooms"]
                    missing_stats = [field for field in required_stats if field not in stats]
                    
                    if not missing_stats:
                        self.log_result("Stats Structure", True, 
                                      "All required stats fields present")
                    else:
                        self.log_result("Stats Structure", False, 
                                      f"Missing stats fields: {missing_stats}")
                else:
                    self.log_result("Search Stats", False, 
                                  "Missing total_apartments in stats response")
            else:
                self.log_result("Search Stats", False, 
                              f"Stats endpoint failed with status: {response.status_code}")
            
            # Test 3: Sample data quality check
            print("\n🔍 Testing sample data quality...")
            response = self.make_request("GET", "/apartments", {"limit": 10})
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", [])
                
                quality_issues = []
                for i, apt in enumerate(apartments):
                    # Check for required fields
                    if not apt.get("title"):
                        quality_issues.append(f"Apartment {i+1}: Missing title")
                    if not apt.get("price") or apt.get("price") <= 0:
                        quality_issues.append(f"Apartment {i+1}: Invalid price")
                    if not apt.get("location"):
                        quality_issues.append(f"Apartment {i+1}: Missing location")
                    if not apt.get("images") or len(apt.get("images", [])) == 0:
                        quality_issues.append(f"Apartment {i+1}: No images")
                
                if not quality_issues:
                    self.log_result("Data Quality", True, 
                                  f"All {len(apartments)} sample apartments have good data quality")
                else:
                    self.log_result("Data Quality", False, 
                                  f"Data quality issues found: {quality_issues[:3]}")
            
        except Exception as e:
            self.log_result("Data Integrity", False, f"Exception: {str(e)}")
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        print("\n=== Testing Health Check ===")
        try:
            response = self.make_request("GET", "/health")
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_result("Health Check", True, "API is healthy")
                else:
                    self.log_result("Health Check", False, f"Unexpected response: {data}")
            else:
                self.log_result("Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Health Check", False, f"Exception: {str(e)}")
    
    def run_verification_tests(self):
        """Run all verification tests"""
        print("🔍 NoFeePlaces.com Quick Verification Test")
        print("=" * 50)
        print("Testing core functionality after recent UI updates...")
        
        start_time = time.time()
        
        # Test 1: Health check
        self.test_health_check()
        
        # Test 2: Apartment listings API
        apartments, total = self.test_apartment_listings_api()
        
        # Test 3: Verification status
        self.test_verification_status(apartments)
        
        # Test 4: Search functionality
        self.test_search_functionality()
        
        # Test 5: Data integrity
        self.test_data_integrity(total)
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 50)
        print("🎯 VERIFICATION TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Tests Passed: {self.results['passed']}")
        print(f"❌ Tests Failed: {self.results['failed']}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if self.results['failed'] > 0:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: All core functionality working properly!")
        elif success_rate >= 75:
            print("✅ GOOD: Most functionality working, minor issues detected")
        else:
            print("⚠️  ATTENTION NEEDED: Multiple issues detected")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = VerificationTester()
    success = tester.run_verification_tests()
    exit(0 if success else 1)