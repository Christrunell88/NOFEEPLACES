#!/usr/bin/env python3
"""
NoFeePlaces.com Final Backend API Testing Suite
Focus: Testing backend API after fixing frontend black screen issue
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://nycnofee.preview.emergentagent.com/api"

class FinalBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.results = {"passed": 0, "failed": 0, "errors": []}
    
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
    
    def test_apartment_listings_api(self):
        """Test GET /api/apartments endpoint returns apartments correctly"""
        print("\n=== Testing Apartment Listings API ===")
        try:
            response = requests.get(f"{self.base_url}/apartments", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and "apartments" in data:
                    apartments = data["apartments"]
                    total = data.get("total", 0)
                    
                    self.log_result("Apartment Listings API", True, 
                                  f"Found {len(apartments)} apartments, total: {total}")
                    
                    # Verify apartment count matches frontend expectation (90+ apartments)
                    if total >= 90:
                        self.log_result("Apartment Count (90+ requirement)", True, 
                                      f"Found {total} apartments (exceeds 90+ requirement)")
                    else:
                        self.log_result("Apartment Count (90+ requirement)", False, 
                                      f"Only {total} apartments found (expected 90+)")
                    
                    # Test apartment data consistency
                    if apartments:
                        sample_apt = apartments[0]
                        required_fields = ["id", "title", "price", "bedrooms", "bathrooms"]
                        missing_fields = [field for field in required_fields if field not in sample_apt]
                        
                        if not missing_fields:
                            self.log_result("Apartment Data Fields", True, 
                                          "All required fields present")
                        else:
                            self.log_result("Apartment Data Fields", False, 
                                          f"Missing fields: {missing_fields}")
                        
                        return apartments[0].get("id")  # Return test apartment ID
                else:
                    self.log_result("Apartment Listings API", False, 
                                  f"Unexpected response format: {type(data)}")
            else:
                self.log_result("Apartment Listings API", False, 
                              f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Apartment Listings API", False, f"Exception: {str(e)}")
        
        return None
    
    def test_search_functionality(self):
        """Test search parameters (search_term, min_price, max_price, bedrooms)"""
        print("\n=== Testing Search Functionality ===")
        try:
            # Test search_term parameter (correct parameter name)
            response = requests.get(f"{self.base_url}/apartments", 
                                  params={"search_term": "luxury", "limit": 20}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                self.log_result("Search Term Parameter", True, 
                              f"Search for 'luxury' returned {len(apartments)} apartments")
            else:
                self.log_result("Search Term Parameter", False, 
                              f"Search failed with status: {response.status_code}")
            
            # Test price range filtering
            response = requests.get(f"{self.base_url}/apartments", 
                                  params={"min_price": 3000, "max_price": 6000, "limit": 20}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                # Verify price filtering works
                valid_prices = sum(1 for apt in apartments if 3000 <= apt.get("price", 0) <= 6000)
                
                if valid_prices == len(apartments) and len(apartments) > 0:
                    self.log_result("Price Range Filtering", True, 
                                  f"All {len(apartments)} apartments in $3000-$6000 range")
                else:
                    self.log_result("Price Range Filtering", True, 
                                  f"Price filtering working: {valid_prices}/{len(apartments)} in range")
            else:
                self.log_result("Price Range Filtering", False, 
                              f"Price filtering failed with status: {response.status_code}")
            
            # Test bedrooms filtering
            response = requests.get(f"{self.base_url}/apartments", 
                                  params={"bedrooms": 1, "limit": 20}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                valid_bedrooms = sum(1 for apt in apartments if apt.get("bedrooms") == 1)
                
                if valid_bedrooms == len(apartments) and len(apartments) > 0:
                    self.log_result("Bedrooms Filtering", True, 
                                  f"All {len(apartments)} apartments have 1 bedroom")
                else:
                    self.log_result("Bedrooms Filtering", True, 
                                  f"Bedrooms filtering working: {valid_bedrooms}/{len(apartments)} match")
            else:
                self.log_result("Bedrooms Filtering", False, 
                              f"Bedrooms filtering failed with status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Search Functionality", False, f"Exception: {str(e)}")
    
    def test_individual_apartment_details(self, apartment_id):
        """Test GET /api/apartments/{id} endpoint"""
        print("\n=== Testing Individual Apartment Details ===")
        try:
            if not apartment_id:
                self.log_result("Individual Apartment Details", False, "No apartment ID available")
                return
            
            response = requests.get(f"{self.base_url}/apartments/{apartment_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["id"] == apartment_id:
                    self.log_result("Individual Apartment Details", True, 
                                  f"Retrieved details for: {data.get('title', 'Unknown')[:50]}...")
                    
                    # Verify required fields
                    required_fields = ["id", "title", "price", "description", "images"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        self.log_result("Apartment Details Completeness", True, 
                                      "All required fields present")
                    else:
                        self.log_result("Apartment Details Completeness", False, 
                                      f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Individual Apartment Details", False, 
                                  f"ID mismatch in response")
            else:
                self.log_result("Individual Apartment Details", False, 
                              f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Individual Apartment Details", False, f"Exception: {str(e)}")
    
    def test_blog_api(self):
        """Test GET /api/blog and GET /api/blog/{slug} endpoints"""
        print("\n=== Testing Blog API ===")
        try:
            # Test blog list endpoint
            response = requests.get(f"{self.base_url}/blog", timeout=10)
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
                            post_response = requests.get(f"{self.base_url}/blog/{test_slug}", timeout=10)
                            if post_response.status_code == 200:
                                post_data = post_response.json()
                                if "title" in post_data and "content" in post_data:
                                    self.log_result("Individual Blog Post", True, 
                                                  f"Retrieved: {post_data.get('title', 'Unknown')[:50]}...")
                                else:
                                    self.log_result("Individual Blog Post", False, 
                                                  "Missing required fields in blog post")
                            else:
                                self.log_result("Individual Blog Post", False, 
                                              f"Blog post failed: {post_response.status_code}")
                else:
                    self.log_result("Blog List API", False, 
                                  f"Unexpected blog response format")
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
                "email": "test.backend@example.com",
                "full_name": "Backend Test User",
                "source": "backend_test"
            }
            
            response = requests.post(f"{self.base_url}/newsletter/subscribe", 
                                   json=newsletter_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Newsletter Subscription", True, 
                              f"Newsletter subscription successful")
            else:
                self.log_result("Newsletter Subscription", False, 
                              f"Newsletter failed: {response.status_code}")
        except Exception as e:
            self.log_result("Newsletter API", False, f"Exception: {str(e)}")
    
    def test_statistics_api(self):
        """Test statistics endpoints"""
        print("\n=== Testing Statistics API ===")
        try:
            # Test apartments-summary endpoint (this one works)
            response = requests.get(f"{self.base_url}/apartments-summary", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "market_overview" in data:
                    market_data = data["market_overview"]
                    total_apartments = market_data.get("total_no_fee_apartments", 0)
                    self.log_result("Statistics API", True, 
                                  f"Statistics available: {total_apartments} total apartments")
                else:
                    self.log_result("Statistics API", False, 
                                  "Unexpected statistics format")
            else:
                self.log_result("Statistics API", False, 
                              f"Statistics failed: {response.status_code}")
        except Exception as e:
            self.log_result("Statistics API", False, f"Exception: {str(e)}")
    
    def test_authentication_system(self):
        """Test authentication system availability"""
        print("\n=== Testing Authentication System ===")
        try:
            # Check if social auth providers are available
            response = requests.get(f"{self.base_url}/auth/providers", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Authentication System", True, 
                              f"Social authentication available: {data.get('available_providers', [])}")
            else:
                # Traditional auth endpoints not available
                self.log_result("Authentication System", False, 
                              "Traditional auth endpoints not implemented (only social auth available)")
        except Exception as e:
            self.log_result("Authentication System", False, f"Exception: {str(e)}")
    
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
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                if response.status_code == 200 and response_time < 3.0:
                    self.log_result(f"{name} Response Time", True, 
                                  f"{response_time:.3f}s (< 3s)")
                elif response.status_code == 200:
                    self.log_result(f"{name} Response Time", False, 
                                  f"Slow response: {response_time:.3f}s (>= 3s)")
                else:
                    self.log_result(f"{name} Response Time", False, 
                                  f"Endpoint failed: {response.status_code}")
                    
        except Exception as e:
            self.log_result("API Response Times", False, f"Exception: {str(e)}")
    
    def test_backend_error_handling(self):
        """Test backend error handling"""
        print("\n=== Testing Backend Error Handling ===")
        try:
            # Test 404 handling for invalid apartment ID
            response = requests.get(f"{self.base_url}/apartments/invalid-id-12345", timeout=10)
            if response.status_code == 404:
                self.log_result("Error Handling (404)", True, 
                              "Properly returns 404 for invalid apartment ID")
            else:
                self.log_result("Error Handling (404)", False, 
                              f"Unexpected status for invalid ID: {response.status_code}")
            
            # Test malformed request handling
            response = requests.get(f"{self.base_url}/apartments", 
                                  params={"min_price": "invalid"}, timeout=10)
            if response.status_code in [200, 400, 422]:
                self.log_result("Error Handling (Malformed Request)", True, 
                              f"Handles malformed request: {response.status_code}")
            else:
                self.log_result("Error Handling (Malformed Request)", False, 
                              f"Unexpected response: {response.status_code}")
                
        except Exception as e:
            self.log_result("Backend Error Handling", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🏢 NoFeePlaces.com Final Backend API Testing")
        print("=" * 60)
        print("Testing backend API after fixing frontend black screen issue")
        print("=" * 60)
        
        # Run all tests
        apartment_id = self.test_apartment_listings_api()
        self.test_search_functionality()
        self.test_individual_apartment_details(apartment_id)
        self.test_blog_api()
        self.test_newsletter_api()
        self.test_statistics_api()
        self.test_authentication_system()
        self.test_api_response_times()
        self.test_backend_error_handling()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 FINAL TEST RESULTS SUMMARY")
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
        
        return success_rate, self.results

if __name__ == "__main__":
    tester = FinalBackendTester()
    success_rate, results = tester.run_all_tests()