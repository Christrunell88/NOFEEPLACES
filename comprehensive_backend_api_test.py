#!/usr/bin/env python3
"""
NoFeePlaces.com Comprehensive Backend API Testing Suite
Focus: Testing backend API after fixing frontend black screen issue
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://fee-free-homes.preview.emergentagent.com/api"
TEST_USER_EMAIL = "sarah.johnson@nofeeplaces.com"
TEST_USER_PASSWORD = "SecurePassword123!"
TEST_USER_NAME = "Sarah Johnson"

class NoFeePlacesAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_apartment_id = None
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
        
        if self.auth_token and "Authorization" not in default_headers:
            default_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, params=data, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_apartment_listings_api(self):
        """Test GET /api/apartments endpoint returns apartments correctly"""
        print("\n=== Testing Apartment Listings API ===")
        try:
            # Test basic apartment listing
            response = self.make_request("GET", "/apartments")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response follows ApartmentListResponse format
                if isinstance(data, dict) and "apartments" in data:
                    apartments = data["apartments"]
                    total = data.get("total", 0)
                    
                    self.log_result("Apartment Listings API Structure", True, 
                                  f"Proper ApartmentListResponse format with {len(apartments)} apartments, total: {total}")
                    
                    # Verify apartment count matches frontend expectation (90+ apartments)
                    if total >= 90:
                        self.log_result("Apartment Count Verification", True, 
                                      f"Found {total} apartments (meets 90+ requirement)")
                    else:
                        self.log_result("Apartment Count Verification", False, 
                                      f"Only {total} apartments found (expected 90+)")
                    
                    # Test apartment data consistency
                    if apartments:
                        self.test_apartment_id = apartments[0].get("id")
                        sample_apt = apartments[0]
                        required_fields = ["id", "title", "price", "bedrooms", "bathrooms", "neighborhood", "borough"]
                        missing_fields = [field for field in required_fields if field not in sample_apt]
                        
                        if not missing_fields:
                            self.log_result("Apartment Data Consistency", True, 
                                          "All required fields present in apartment data")
                        else:
                            self.log_result("Apartment Data Consistency", False, 
                                          f"Missing fields: {missing_fields}")
                    
                elif isinstance(data, list):
                    # Legacy list format
                    apartments = data
                    self.log_result("Apartment Listings API Structure", True, 
                                  f"Legacy list format with {len(apartments)} apartments")
                    if apartments:
                        self.test_apartment_id = apartments[0].get("id")
                else:
                    self.log_result("Apartment Listings API Structure", False, 
                                  f"Unexpected response format: {type(data)}")
            else:
                self.log_result("Apartment Listings API", False, 
                              f"Status code: {response.status_code}, Response: {response.text[:200]}")
        except Exception as e:
            self.log_result("Apartment Listings API", False, f"Exception: {str(e)}")
    
    def test_search_functionality(self):
        """Test search parameters (search_term, min_price, max_price, bedrooms)"""
        print("\n=== Testing Search Functionality ===")
        try:
            # Test search_term parameter
            response = self.make_request("GET", "/apartments", {"search": "luxury", "limit": 20})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                self.log_result("Search Term Parameter", True, 
                              f"Search for 'luxury' returned {len(apartments)} apartments")
            else:
                self.log_result("Search Term Parameter", False, 
                              f"Search failed with status: {response.status_code}")
            
            # Test price range filtering
            response = self.make_request("GET", "/apartments", {"min_price": 3000, "max_price": 6000, "limit": 20})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                # Verify price filtering works
                valid_prices = 0
                for apt in apartments:
                    price = apt.get("price", 0)
                    if 3000 <= price <= 6000:
                        valid_prices += 1
                
                if valid_prices == len(apartments):
                    self.log_result("Price Range Filtering", True, 
                                  f"All {len(apartments)} apartments in $3000-$6000 range")
                else:
                    self.log_result("Price Range Filtering", False, 
                                  f"Only {valid_prices}/{len(apartments)} apartments in price range")
            else:
                self.log_result("Price Range Filtering", False, 
                              f"Price filtering failed with status: {response.status_code}")
            
            # Test bedrooms filtering
            response = self.make_request("GET", "/apartments", {"bedrooms": 1, "limit": 20})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                # Verify bedroom filtering works
                valid_bedrooms = 0
                for apt in apartments:
                    bedrooms = apt.get("bedrooms")
                    if bedrooms == 1:
                        valid_bedrooms += 1
                
                if valid_bedrooms == len(apartments):
                    self.log_result("Bedrooms Filtering", True, 
                                  f"All {len(apartments)} apartments have 1 bedroom")
                else:
                    self.log_result("Bedrooms Filtering", False, 
                                  f"Only {valid_bedrooms}/{len(apartments)} apartments have 1 bedroom")
            else:
                self.log_result("Bedrooms Filtering", False, 
                              f"Bedrooms filtering failed with status: {response.status_code}")
            
            # Test neighborhood filtering
            response = self.make_request("GET", "/apartments", {"neighborhood": "manhattan", "limit": 20})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                self.log_result("Neighborhood Filtering", True, 
                              f"Neighborhood search for 'manhattan' returned {len(apartments)} apartments")
            else:
                self.log_result("Neighborhood Filtering", False, 
                              f"Neighborhood filtering failed with status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Search Functionality", False, f"Exception: {str(e)}")
    
    def test_individual_apartment_details(self):
        """Test GET /api/apartments/{id} endpoint"""
        print("\n=== Testing Individual Apartment Details ===")
        try:
            if not self.test_apartment_id:
                self.log_result("Individual Apartment Details", False, "No apartment ID available for testing")
                return
            
            response = self.make_request("GET", f"/apartments/{self.test_apartment_id}")
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["id"] == self.test_apartment_id:
                    self.log_result("Individual Apartment Details", True, 
                                  f"Retrieved details for apartment: {data.get('title', 'Unknown')}")
                    
                    # Verify all required fields are present
                    required_fields = ["id", "title", "price", "description", "images", "contact_email"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        self.log_result("Apartment Details Completeness", True, 
                                      "All required fields present in apartment details")
                    else:
                        self.log_result("Apartment Details Completeness", False, 
                                      f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Individual Apartment Details", False, 
                                  f"Unexpected apartment data: {data}")
            else:
                self.log_result("Individual Apartment Details", False, 
                              f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Individual Apartment Details", False, f"Exception: {str(e)}")
    
    def test_authentication_endpoints(self):
        """Test user registration, login, and profile endpoints"""
        print("\n=== Testing Authentication Endpoints ===")
        try:
            # Test user registration
            registration_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME
            }
            
            response = self.make_request("POST", "/auth/register", registration_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "token_type" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("User Registration", True, "User registered successfully with JWT token")
                else:
                    self.log_result("User Registration", False, f"Missing token in response: {data}")
            elif response.status_code == 400:
                # User might already exist, try login
                login_response = self.make_request("POST", "/auth/login", {
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                })
                if login_response.status_code == 200:
                    token_data = login_response.json()
                    self.auth_token = token_data["access_token"]
                    self.log_result("User Registration", True, "User already exists, logged in successfully")
                else:
                    self.log_result("User Registration", False, f"Registration and login both failed")
            else:
                self.log_result("User Registration", False, 
                              f"Status code: {response.status_code}, Response: {response.text}")
            
            # Test user profile retrieval
            if self.auth_token:
                response = self.make_request("GET", "/auth/me")
                if response.status_code == 200:
                    data = response.json()
                    if "email" in data and data["email"] == TEST_USER_EMAIL:
                        self.log_result("User Profile Retrieval", True, 
                                      f"Profile retrieved for user: {data.get('full_name', 'Unknown')}")
                    else:
                        self.log_result("User Profile Retrieval", False, 
                                      f"Unexpected profile data: {data}")
                else:
                    self.log_result("User Profile Retrieval", False, 
                                  f"Profile retrieval failed: {response.status_code}")
            
        except Exception as e:
            self.log_result("Authentication Endpoints", False, f"Exception: {str(e)}")
    
    def test_blog_api(self):
        """Test GET /api/blog and GET /api/blog/{slug} endpoints"""
        print("\n=== Testing Blog API ===")
        try:
            # Test blog list endpoint
            response = self.make_request("GET", "/blog")
            if response.status_code == 200:
                data = response.json()
                if "posts" in data:
                    posts = data["posts"]
                    total = data.get("total", 0)
                    self.log_result("Blog List API", True, 
                                  f"Retrieved {len(posts)} blog posts, total: {total}")
                    
                    # Test individual blog post
                    if posts:
                        test_slug = posts[0].get("slug")
                        if test_slug:
                            post_response = self.make_request("GET", f"/blog/{test_slug}")
                            if post_response.status_code == 200:
                                post_data = post_response.json()
                                if "title" in post_data and "content" in post_data:
                                    self.log_result("Individual Blog Post", True, 
                                                  f"Retrieved blog post: {post_data.get('title', 'Unknown')}")
                                else:
                                    self.log_result("Individual Blog Post", False, 
                                                  f"Missing required fields in blog post")
                            else:
                                self.log_result("Individual Blog Post", False, 
                                              f"Blog post retrieval failed: {post_response.status_code}")
                else:
                    self.log_result("Blog List API", False, 
                                  f"Unexpected blog response format: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            else:
                self.log_result("Blog List API", False, 
                              f"Blog API failed with status: {response.status_code}")
        except Exception as e:
            self.log_result("Blog API", False, f"Exception: {str(e)}")
    
    def test_newsletter_api(self):
        """Test POST /api/newsletter/subscribe endpoint"""
        print("\n=== Testing Newsletter API ===")
        try:
            newsletter_data = {
                "email": "test.newsletter@example.com",
                "full_name": "Newsletter Test User",
                "source": "api_test"
            }
            
            response = self.make_request("POST", "/newsletter/subscribe", newsletter_data)
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    self.log_result("Newsletter Subscription", True, 
                                  f"Newsletter subscription successful: {data.get('message', 'Success')}")
                else:
                    self.log_result("Newsletter Subscription", True, 
                                  "Newsletter subscription completed")
            else:
                self.log_result("Newsletter Subscription", False, 
                              f"Newsletter API failed with status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Newsletter API", False, f"Exception: {str(e)}")
    
    def test_statistics_api(self):
        """Test GET /api/apartments/search/stats (if available)"""
        print("\n=== Testing Statistics API ===")
        try:
            # Try different possible stats endpoints
            stats_endpoints = [
                "/apartments/search/stats",
                "/apartments/stats", 
                "/apartments-summary",
                "/stats"
            ]
            
            stats_found = False
            for endpoint in stats_endpoints:
                try:
                    response = self.make_request("GET", endpoint)
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, dict) and len(data) > 0:
                            self.log_result(f"Statistics API ({endpoint})", True, 
                                          f"Statistics retrieved: {list(data.keys())[:5]}")
                            stats_found = True
                            break
                except:
                    continue
            
            if not stats_found:
                self.log_result("Statistics API", False, "No working statistics endpoint found")
                
        except Exception as e:
            self.log_result("Statistics API", False, f"Exception: {str(e)}")
    
    def test_api_response_times(self):
        """Test API response times are reasonable"""
        print("\n=== Testing API Response Times ===")
        try:
            endpoints_to_test = [
                ("/apartments", "Apartments Listing"),
                ("/blog", "Blog API"),
                ("/health", "Health Check")
            ]
            
            for endpoint, name in endpoints_to_test:
                start_time = time.time()
                response = self.make_request("GET", endpoint)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                if response.status_code == 200 and response_time < 5.0:
                    self.log_result(f"{name} Response Time", True, 
                                  f"Response time: {response_time:.3f}s (< 5s)")
                elif response.status_code == 200:
                    self.log_result(f"{name} Response Time", False, 
                                  f"Response time too slow: {response_time:.3f}s (>= 5s)")
                else:
                    self.log_result(f"{name} Response Time", False, 
                                  f"Endpoint failed with status: {response.status_code}")
                    
        except Exception as e:
            self.log_result("API Response Times", False, f"Exception: {str(e)}")
    
    def test_backend_errors(self):
        """Test for critical backend errors affecting frontend functionality"""
        print("\n=== Testing for Backend Errors ===")
        try:
            # Test error handling for invalid apartment ID
            response = self.make_request("GET", "/apartments/invalid-id-12345")
            if response.status_code == 404:
                self.log_result("Error Handling (Invalid Apartment ID)", True, 
                              "Properly returns 404 for invalid apartment ID")
            else:
                self.log_result("Error Handling (Invalid Apartment ID)", False, 
                              f"Unexpected status for invalid ID: {response.status_code}")
            
            # Test error handling for invalid blog slug
            response = self.make_request("GET", "/blog/invalid-slug-12345")
            if response.status_code == 404:
                self.log_result("Error Handling (Invalid Blog Slug)", True, 
                              "Properly returns 404 for invalid blog slug")
            else:
                self.log_result("Error Handling (Invalid Blog Slug)", False, 
                              f"Unexpected status for invalid slug: {response.status_code}")
            
            # Test malformed request handling
            response = self.make_request("GET", "/apartments", {"min_price": "invalid"})
            if response.status_code in [200, 400, 422]:  # Any reasonable response
                self.log_result("Error Handling (Malformed Request)", True, 
                              f"Handles malformed request appropriately: {response.status_code}")
            else:
                self.log_result("Error Handling (Malformed Request)", False, 
                              f"Unexpected response to malformed request: {response.status_code}")
                
        except Exception as e:
            self.log_result("Backend Error Testing", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🏢 NoFeePlaces.com Backend API Testing Suite")
        print("=" * 60)
        print("Focus: Testing backend API after fixing frontend black screen issue")
        print("=" * 60)
        
        # Run all test methods
        self.test_apartment_listings_api()
        self.test_search_functionality()
        self.test_individual_apartment_details()
        self.test_authentication_endpoints()
        self.test_blog_api()
        self.test_newsletter_api()
        self.test_statistics_api()
        self.test_api_response_times()
        self.test_backend_errors()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.results["errors"]:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        print("\n" + "=" * 60)
        print("📝 BACKEND API TESTING COMPLETE")
        print("=" * 60)
        
        return success_rate >= 80  # Consider 80%+ success rate as passing

if __name__ == "__main__":
    tester = NoFeePlacesAPITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)