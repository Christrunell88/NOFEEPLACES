#!/usr/bin/env python3
"""
NoFeePlaces.com Comprehensive Backend Health Test
Focus on review request requirements:
1. Current System Health - Test all existing API endpoints
2. Mock Data Safeguards - Verify mock data protection system
3. Authentication System - Test auth endpoints
4. Database Integrity - Verify apartment listings and user management
5. API Performance - Check response times and error handling
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://nofee-enhancement.preview.emergentagent.com/api"
TEST_USER_EMAIL = "healthcheck@nofeeplaces.com"
TEST_USER_PASSWORD = "HealthCheck123!"
TEST_USER_NAME = "Health Check User"

class BackendHealthTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_user_id = None
        self.test_apartment_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance": {}
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
        """Make HTTP request with performance tracking"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        if self.auth_token and "Authorization" not in default_headers:
            default_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        start_time = time.time()
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
            
            response_time = time.time() - start_time
            self.results["performance"][f"{method} {endpoint}"] = response_time
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_system_health_endpoints(self):
        """Test basic system health and status endpoints"""
        print("\n=== 1. CURRENT SYSTEM HEALTH ===")
        
        # Test basic connectivity
        try:
            response = self.make_request("GET", "/apartments", {"limit": 1})
            if response.status_code == 200:
                self.log_result("API Connectivity", True, "Backend API is accessible")
            else:
                self.log_result("API Connectivity", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("API Connectivity", False, f"Exception: {str(e)}")
        
        # Test apartment listings endpoint
        try:
            response = self.make_request("GET", "/apartments", {"limit": 10})
            if response.status_code == 200:
                apartments = response.json()
                if isinstance(apartments, list) and len(apartments) > 0:
                    self.test_apartment_id = apartments[0].get("id")
                    self.log_result("Apartment Listings", True, f"Retrieved {len(apartments)} apartments")
                else:
                    self.log_result("Apartment Listings", False, "No apartments returned")
            else:
                self.log_result("Apartment Listings", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Apartment Listings", False, f"Exception: {str(e)}")
        
        # Test apartment details
        if self.test_apartment_id:
            try:
                response = self.make_request("GET", f"/apartments/{self.test_apartment_id}")
                if response.status_code == 200:
                    apartment = response.json()
                    required_fields = ["id", "title", "address", "price", "bedrooms", "bathrooms"]
                    missing_fields = [field for field in required_fields if field not in apartment]
                    if not missing_fields:
                        self.log_result("Apartment Details", True, "All required fields present")
                    else:
                        self.log_result("Apartment Details", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Apartment Details", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_result("Apartment Details", False, f"Exception: {str(e)}")
        
        # Test search functionality
        try:
            response = self.make_request("GET", "/apartments", {"search_term": "luxury", "limit": 5})
            if response.status_code == 200:
                results = response.json()
                self.log_result("Search Functionality", True, f"Search returned {len(results)} results")
            else:
                self.log_result("Search Functionality", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Search Functionality", False, f"Exception: {str(e)}")
        
        # Test filtering
        try:
            response = self.make_request("GET", "/apartments", {"min_price": 3000, "max_price": 5000, "limit": 5})
            if response.status_code == 200:
                results = response.json()
                valid_prices = all(3000 <= apt.get("price", 0) <= 5000 for apt in results)
                if valid_prices:
                    self.log_result("Price Filtering", True, f"All {len(results)} results within price range")
                else:
                    self.log_result("Price Filtering", False, "Some results outside price range")
            else:
                self.log_result("Price Filtering", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Price Filtering", False, f"Exception: {str(e)}")
        
        # Test statistics endpoint
        try:
            response = self.make_request("GET", "/apartments/search/stats")
            if response.status_code == 200:
                stats = response.json()
                if "total_apartments" in stats:
                    self.log_result("Statistics Endpoint", True, f"Total apartments: {stats['total_apartments']}")
                else:
                    self.log_result("Statistics Endpoint", False, "Missing total_apartments field")
            else:
                self.log_result("Statistics Endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Statistics Endpoint", False, f"Exception: {str(e)}")
    
    def test_mock_data_safeguards(self):
        """Test mock data protection system"""
        print("\n=== 2. MOCK DATA SAFEGUARDS ===")
        
        # Test admin status endpoint
        try:
            response = self.make_request("GET", "/admin/status")
            if response.status_code == 200:
                status = response.json()
                expected_config = {
                    "USE_MOCK_DATA": False,
                    "ENABLE_AUTO_SCRAPING": False,
                    "PRESERVE_MANUAL_DATA": True
                }
                
                config_correct = True
                for key, expected_value in expected_config.items():
                    if status.get(key) != expected_value:
                        config_correct = False
                        break
                
                if config_correct:
                    self.log_result("Mock Data Configuration", True, "All safeguards properly configured")
                else:
                    self.log_result("Mock Data Configuration", False, f"Config mismatch: {status}")
            else:
                self.log_result("Mock Data Configuration", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Mock Data Configuration", False, f"Exception: {str(e)}")
        
        # Test admin scrape endpoint (should be disabled)
        try:
            response = self.make_request("POST", "/admin/scrape")
            if response.status_code == 200:
                result = response.json()
                if "disabled" in result.get("message", "").lower() or "no data was modified" in result.get("message", "").lower():
                    self.log_result("Scrape Endpoint Protection", True, "Scraping properly disabled")
                else:
                    self.log_result("Scrape Endpoint Protection", False, f"Unexpected response: {result}")
            else:
                self.log_result("Scrape Endpoint Protection", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Scrape Endpoint Protection", False, f"Exception: {str(e)}")
        
        # Verify data preservation by checking apartment count before and after scrape attempt
        try:
            # Get initial count
            response1 = self.make_request("GET", "/apartments", {"limit": 1000})
            initial_count = len(response1.json()) if response1.status_code == 200 else 0
            
            # Attempt scrape
            self.make_request("POST", "/admin/scrape")
            
            # Get count after scrape attempt
            response2 = self.make_request("GET", "/apartments", {"limit": 1000})
            final_count = len(response2.json()) if response2.status_code == 200 else 0
            
            if initial_count == final_count and initial_count > 0:
                self.log_result("Data Preservation", True, f"Apartment count unchanged: {initial_count}")
            else:
                self.log_result("Data Preservation", False, f"Count changed: {initial_count} -> {final_count}")
        except Exception as e:
            self.log_result("Data Preservation", False, f"Exception: {str(e)}")
    
    def test_authentication_system(self):
        """Test authentication endpoints and JWT validation"""
        print("\n=== 3. AUTHENTICATION SYSTEM ===")
        
        # Test user registration
        try:
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
                    self.log_result("User Registration", True, "Registration successful with JWT token")
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
                    self.log_result("User Registration", True, "User exists, logged in successfully")
                else:
                    self.log_result("User Registration", False, f"Registration and login failed")
            else:
                self.log_result("User Registration", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")
        
        # Test user login
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "token_type" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("User Login", True, "Login successful")
                else:
                    self.log_result("User Login", False, f"Missing token in response: {data}")
            else:
                self.log_result("User Login", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("User Login", False, f"Exception: {str(e)}")
        
        # Test JWT token validation
        if self.auth_token:
            try:
                response = self.make_request("GET", "/auth/me")
                if response.status_code == 200:
                    user_data = response.json()
                    if user_data.get("email") == TEST_USER_EMAIL:
                        self.test_user_id = user_data.get("id")
                        self.log_result("JWT Token Validation", True, f"Token valid for user: {user_data['full_name']}")
                    else:
                        self.log_result("JWT Token Validation", False, f"Token returned wrong user: {user_data.get('email')}")
                else:
                    self.log_result("JWT Token Validation", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_result("JWT Token Validation", False, f"Exception: {str(e)}")
        
        # Test invalid token rejection
        try:
            invalid_headers = {"Authorization": "Bearer invalid_token_here"}
            response = self.make_request("GET", "/auth/me", headers=invalid_headers)
            if response.status_code == 401:
                self.log_result("Invalid Token Rejection", True, "Invalid tokens properly rejected")
            else:
                self.log_result("Invalid Token Rejection", False, f"Invalid token not rejected: {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Token Rejection", False, f"Exception: {str(e)}")
    
    def test_database_integrity(self):
        """Test database integrity and data consistency"""
        print("\n=== 4. DATABASE INTEGRITY ===")
        
        # Test apartment data consistency
        try:
            response = self.make_request("GET", "/apartments", {"limit": 50})
            if response.status_code == 200:
                apartments = response.json()
                
                # Check required fields
                required_fields = ["id", "title", "address", "price", "bedrooms", "bathrooms", "neighborhood", "borough"]
                apartments_with_all_fields = 0
                
                for apt in apartments:
                    if all(field in apt for field in required_fields):
                        apartments_with_all_fields += 1
                
                if apartments_with_all_fields == len(apartments):
                    self.log_result("Apartment Data Consistency", True, f"All {len(apartments)} apartments have required fields")
                else:
                    self.log_result("Apartment Data Consistency", False, f"Only {apartments_with_all_fields}/{len(apartments)} have all required fields")
                
                # Check data types
                type_errors = []
                for apt in apartments[:10]:  # Check first 10
                    if not isinstance(apt.get("price"), int):
                        type_errors.append(f"Price not integer in {apt.get('id')}")
                    if not isinstance(apt.get("bedrooms"), int):
                        type_errors.append(f"Bedrooms not integer in {apt.get('id')}")
                    if not isinstance(apt.get("bathrooms"), (int, float)):
                        type_errors.append(f"Bathrooms not number in {apt.get('id')}")
                
                if not type_errors:
                    self.log_result("Data Type Validation", True, "All data types correct")
                else:
                    self.log_result("Data Type Validation", False, f"Type errors: {type_errors[:3]}")
                
            else:
                self.log_result("Apartment Data Consistency", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Apartment Data Consistency", False, f"Exception: {str(e)}")
        
        # Test user data integrity (if authenticated)
        if self.auth_token and self.test_user_id:
            try:
                response = self.make_request("GET", "/auth/me")
                if response.status_code == 200:
                    user_data = response.json()
                    required_user_fields = ["id", "email", "full_name", "created_at"]
                    missing_fields = [field for field in required_user_fields if field not in user_data]
                    
                    if not missing_fields:
                        self.log_result("User Data Integrity", True, "User data has all required fields")
                    else:
                        self.log_result("User Data Integrity", False, f"Missing user fields: {missing_fields}")
                else:
                    self.log_result("User Data Integrity", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_result("User Data Integrity", False, f"Exception: {str(e)}")
        
        # Test apartment count consistency
        try:
            # Get count from listing endpoint
            response1 = self.make_request("GET", "/apartments", {"limit": 1000})
            listing_count = len(response1.json()) if response1.status_code == 200 else 0
            
            # Get count from stats endpoint
            response2 = self.make_request("GET", "/apartments/search/stats")
            stats_count = response2.json().get("total_apartments", 0) if response2.status_code == 200 else 0
            
            if listing_count == stats_count and listing_count > 0:
                self.log_result("Apartment Count Consistency", True, f"Consistent count: {listing_count}")
            else:
                self.log_result("Apartment Count Consistency", False, f"Count mismatch: listing={listing_count}, stats={stats_count}")
        except Exception as e:
            self.log_result("Apartment Count Consistency", False, f"Exception: {str(e)}")
    
    def test_api_performance(self):
        """Test API performance and error handling"""
        print("\n=== 5. API PERFORMANCE & ERROR HANDLING ===")
        
        # Test response times
        endpoints_to_test = [
            ("GET", "/apartments", {"limit": 10}),
            ("GET", "/apartments/search/stats", None),
            ("GET", "/admin/status", None)
        ]
        
        slow_endpoints = []
        for method, endpoint, params in endpoints_to_test:
            try:
                start_time = time.time()
                response = self.make_request(method, endpoint, params)
                response_time = time.time() - start_time
                
                if response_time < 2.0:  # Under 2 seconds is good
                    self.log_result(f"Performance {endpoint}", True, f"Response time: {response_time:.2f}s")
                else:
                    slow_endpoints.append(f"{endpoint}: {response_time:.2f}s")
                    self.log_result(f"Performance {endpoint}", False, f"Slow response: {response_time:.2f}s")
            except Exception as e:
                self.log_result(f"Performance {endpoint}", False, f"Exception: {str(e)}")
        
        # Test error handling
        error_tests = [
            ("GET", "/apartments/nonexistent-id", None, 404),
            ("GET", "/apartments", {"min_price": "invalid"}, [400, 422]),
            ("POST", "/auth/login", {"email": "invalid", "password": "test"}, [400, 422]),
        ]
        
        for method, endpoint, data, expected_codes in error_tests:
            try:
                response = self.make_request(method, endpoint, data)
                expected_codes = expected_codes if isinstance(expected_codes, list) else [expected_codes]
                
                if response.status_code in expected_codes:
                    self.log_result(f"Error Handling {endpoint}", True, f"Proper error code: {response.status_code}")
                else:
                    self.log_result(f"Error Handling {endpoint}", False, f"Unexpected code: {response.status_code}")
            except Exception as e:
                self.log_result(f"Error Handling {endpoint}", False, f"Exception: {str(e)}")
        
        # Test concurrent requests (basic load test)
        try:
            import threading
            import queue
            
            def make_concurrent_request(result_queue):
                try:
                    response = self.make_request("GET", "/apartments", {"limit": 5})
                    result_queue.put(response.status_code == 200)
                except:
                    result_queue.put(False)
            
            result_queue = queue.Queue()
            threads = []
            
            # Create 5 concurrent requests
            for _ in range(5):
                thread = threading.Thread(target=make_concurrent_request, args=(result_queue,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check results
            successful_requests = 0
            while not result_queue.empty():
                if result_queue.get():
                    successful_requests += 1
            
            if successful_requests == 5:
                self.log_result("Concurrent Request Handling", True, "All 5 concurrent requests successful")
            else:
                self.log_result("Concurrent Request Handling", False, f"Only {successful_requests}/5 concurrent requests successful")
                
        except Exception as e:
            self.log_result("Concurrent Request Handling", False, f"Exception: {str(e)}")
    
    def test_user_features(self):
        """Test user-specific features like favorites and saved searches"""
        print("\n=== 6. USER FEATURES ===")
        
        if not self.auth_token or not self.test_apartment_id:
            self.log_result("User Features", False, "No auth token or apartment ID for testing")
            return
        
        # Test favorites functionality
        try:
            # Add to favorites
            response = self.make_request("POST", f"/users/favorites/{self.test_apartment_id}")
            if response.status_code == 200:
                self.log_result("Add to Favorites", True, "Apartment added to favorites")
                
                # Get favorites
                response = self.make_request("GET", "/users/favorites")
                if response.status_code == 200:
                    favorites = response.json()
                    if any(fav.get("id") == self.test_apartment_id for fav in favorites):
                        self.log_result("Get Favorites", True, f"Found {len(favorites)} favorites")
                    else:
                        self.log_result("Get Favorites", False, "Added apartment not in favorites")
                else:
                    self.log_result("Get Favorites", False, f"Status code: {response.status_code}")
                
                # Remove from favorites
                response = self.make_request("DELETE", f"/users/favorites/{self.test_apartment_id}")
                if response.status_code == 200:
                    self.log_result("Remove from Favorites", True, "Apartment removed from favorites")
                else:
                    self.log_result("Remove from Favorites", False, f"Status code: {response.status_code}")
            else:
                self.log_result("Add to Favorites", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Favorites Functionality", False, f"Exception: {str(e)}")
        
        # Test saved searches
        try:
            search_data = {
                "name": "Test Search",
                "filters": {
                    "min_price": 3000,
                    "max_price": 5000,
                    "bedrooms": 1
                }
            }
            
            # Create saved search
            response = self.make_request("POST", "/users/saved-searches", search_data)
            if response.status_code == 200:
                saved_search = response.json()
                search_id = saved_search.get("id")
                self.log_result("Create Saved Search", True, "Saved search created")
                
                # Get saved searches
                response = self.make_request("GET", "/users/saved-searches")
                if response.status_code == 200:
                    searches = response.json()
                    self.log_result("Get Saved Searches", True, f"Found {len(searches)} saved searches")
                else:
                    self.log_result("Get Saved Searches", False, f"Status code: {response.status_code}")
                
                # Delete saved search
                if search_id:
                    response = self.make_request("DELETE", f"/users/saved-searches/{search_id}")
                    if response.status_code == 200:
                        self.log_result("Delete Saved Search", True, "Saved search deleted")
                    else:
                        self.log_result("Delete Saved Search", False, f"Status code: {response.status_code}")
            else:
                self.log_result("Create Saved Search", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Saved Searches Functionality", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend health tests"""
        print("🏥 NoFeePlaces.com Backend Health Check")
        print("=" * 50)
        print("Testing comprehensive backend functionality as requested in review")
        print("=" * 50)
        
        start_time = time.time()
        
        self.test_system_health_endpoints()
        self.test_mock_data_safeguards()
        self.test_authentication_system()
        self.test_database_integrity()
        self.test_api_performance()
        self.test_user_features()
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 50)
        print("🏁 BACKEND HEALTH CHECK RESULTS")
        print("=" * 50)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        
        if self.results["errors"]:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        # Performance summary
        if self.results["performance"]:
            print(f"\n⚡ PERFORMANCE SUMMARY:")
            for endpoint, time_taken in self.results["performance"].items():
                status = "🟢" if time_taken < 1.0 else "🟡" if time_taken < 2.0 else "🔴"
                print(f"   {status} {endpoint}: {time_taken:.2f}s")
        
        print("\n" + "=" * 50)
        return self.results

if __name__ == "__main__":
    tester = BackendHealthTester()
    results = tester.run_all_tests()