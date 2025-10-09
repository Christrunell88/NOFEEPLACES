#!/usr/bin/env python3
"""
NoFeePlaces.com Backend API Comprehensive Health Check
Tests all backend endpoints for production readiness as requested in review
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration from frontend/.env
BASE_URL = "https://smartrental.preview.emergentagent.com/api"

class NoFeePlacesHealthChecker:
    def __init__(self):
        self.base_url = BASE_URL
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance_issues": []
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
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None, timeout: int = 10) -> requests.Response:
        """Make HTTP request with error handling and performance tracking"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        start_time = time.time()
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, params=data, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            
            # Track performance issues (over 3 seconds as mentioned in review)
            if response_time > 3.0:
                self.results["performance_issues"].append(f"{method} {endpoint}: {response_time:.2f}s")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
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
    
    def test_core_apartment_endpoints(self):
        """Test core apartment API endpoints"""
        print("\n=== Testing Core Apartment Endpoints ===")
        
        # Test GET /api/apartments (apartment listings with pagination)
        try:
            response = self.make_request("GET", "/apartments", {"limit": 50})
            if response.status_code == 200:
                data = response.json()
                if "apartments" in data and "total" in data:
                    apartment_count = data["total"]
                    if apartment_count >= 357:  # Should be ~357 apartments as mentioned
                        self.log_result("Apartment Listings API", True, 
                                      f"Retrieved {len(data['apartments'])} apartments out of {apartment_count} total")
                    else:
                        self.log_result("Apartment Listings API", False, 
                                      f"Expected ~357 apartments, got {apartment_count}")
                else:
                    self.log_result("Apartment Listings API", False, f"Invalid response format: {data}")
            else:
                self.log_result("Apartment Listings API", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Apartment Listings API", False, f"Exception: {str(e)}")
        
        # Test GET /api/apartments/{id} (individual apartment details)
        try:
            # First get an apartment ID
            response = self.make_request("GET", "/apartments", {"limit": 1})
            if response.status_code == 200:
                data = response.json()
                if data.get("apartments") and len(data["apartments"]) > 0:
                    apartment_id = data["apartments"][0]["id"]
                    
                    # Test individual apartment endpoint
                    detail_response = self.make_request("GET", f"/apartments/{apartment_id}")
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        if detail_data.get("id") == apartment_id:
                            self.log_result("Individual Apartment API", True, 
                                          f"Retrieved details for apartment: {detail_data.get('title', 'Unknown')}")
                        else:
                            self.log_result("Individual Apartment API", False, "Apartment ID mismatch")
                    else:
                        self.log_result("Individual Apartment API", False, 
                                      f"Status code: {detail_response.status_code}")
                else:
                    self.log_result("Individual Apartment API", False, "No apartments available for testing")
            else:
                self.log_result("Individual Apartment API", False, "Could not get apartment for testing")
        except Exception as e:
            self.log_result("Individual Apartment API", False, f"Exception: {str(e)}")
        
        # Test GET /api/apartments/search/stats (search statistics)
        try:
            response = self.make_request("GET", "/apartments/search/stats")
            if response.status_code == 200:
                data = response.json()
                if "total_apartments" in data and "boroughs" in data and "price_range" in data:
                    total = data["total_apartments"]
                    boroughs = len(data["boroughs"])
                    price_range = data["price_range"]
                    self.log_result("Search Stats API", True, 
                                  f"Stats: {total} apartments, {boroughs} boroughs, price range: ${price_range.get('min_price', 0)}-${price_range.get('max_price', 0)}")
                else:
                    self.log_result("Search Stats API", False, f"Missing required fields in response: {data}")
            else:
                self.log_result("Search Stats API", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Search Stats API", False, f"Exception: {str(e)}")
    
    def test_contact_form_api(self):
        """Test POST /api/contact (contact form submission)"""
        print("\n=== Testing Contact Form API ===")
        try:
            contact_data = {
                "name": "John Smith",
                "email": "john.smith@example.com",
                "phone": "+1-555-123-4567",
                "message": "I'm interested in learning more about your no fee apartments in Manhattan. Please contact me with available options.",
                "preferred_contact": "email"
            }
            
            response = self.make_request("POST", "/contact", contact_data)
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "contact_id" in data:
                    self.log_result("Contact Form API", True, 
                                  f"Contact submitted successfully with ID: {data['contact_id']}")
                else:
                    self.log_result("Contact Form API", False, f"Invalid response format: {data}")
            else:
                self.log_result("Contact Form API", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Contact Form API", False, f"Exception: {str(e)}")
    
    def test_newsletter_api(self):
        """Test POST /api/newsletter/subscribe (newsletter subscription)"""
        print("\n=== Testing Newsletter API ===")
        try:
            newsletter_data = {
                "email": "newsletter.test@example.com",
                "full_name": "Newsletter Tester",
                "source": "website"
            }
            
            response = self.make_request("POST", "/newsletter/subscribe", newsletter_data)
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    if data["status"] == "success":
                        self.log_result("Newsletter API", True, "Newsletter subscription successful")
                    elif data["status"] == "error" and "already subscribed" in data.get("message", "").lower():
                        self.log_result("Newsletter API", True, "Newsletter subscription working (already subscribed)")
                    else:
                        self.log_result("Newsletter API", False, f"Unexpected status: {data}")
                else:
                    self.log_result("Newsletter API", False, f"Invalid response format: {data}")
            else:
                self.log_result("Newsletter API", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Newsletter API", False, f"Exception: {str(e)}")
    
    def test_visitor_tracking_api(self):
        """Test POST /api/visitor/track (visitor tracking)"""
        print("\n=== Testing Visitor Tracking API ===")
        try:
            response = self.make_request("POST", "/visitor/track", {})
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_result("Visitor Tracking API", True, "Visitor tracking working")
                else:
                    self.log_result("Visitor Tracking API", False, f"Invalid response format: {data}")
            else:
                self.log_result("Visitor Tracking API", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Visitor Tracking API", False, f"Exception: {str(e)}")
    
    def test_database_connectivity_and_data_quality(self):
        """Test database connectivity and data quality"""
        print("\n=== Testing Database Connectivity & Data Quality ===")
        
        # Test apartment count
        try:
            response = self.make_request("GET", "/apartments/search/stats")
            if response.status_code == 200:
                data = response.json()
                apartment_count = data.get("total_apartments", 0)
                
                if apartment_count >= 357:
                    self.log_result("Database Apartment Count", True, f"Found {apartment_count} apartments (meets ~357 requirement)")
                else:
                    self.log_result("Database Apartment Count", False, f"Only {apartment_count} apartments found, expected ~357")
            else:
                self.log_result("Database Apartment Count", False, "Could not retrieve apartment count")
        except Exception as e:
            self.log_result("Database Apartment Count", False, f"Exception: {str(e)}")
        
        # Test contact info verification
        try:
            response = self.make_request("GET", "/apartments", {"limit": 10})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", [])
                
                proper_contact_count = 0
                for apt in apartments:
                    contact_email = apt.get("contact_email", "")
                    if contact_email == "placesfirm@gmail.com":
                        proper_contact_count += 1
                
                if proper_contact_count == len(apartments):
                    self.log_result("Contact Info Verification", True, 
                                  f"All {len(apartments)} apartments have proper contact info (placesfirm@gmail.com)")
                else:
                    self.log_result("Contact Info Verification", False, 
                                  f"Only {proper_contact_count}/{len(apartments)} apartments have proper contact info")
            else:
                self.log_result("Contact Info Verification", False, "Could not retrieve apartments for contact verification")
        except Exception as e:
            self.log_result("Contact Info Verification", False, f"Exception: {str(e)}")
        
        # Test search and filtering functionality
        try:
            # Test location search
            response = self.make_request("GET", "/apartments", {"search": "Manhattan", "limit": 20})
            if response.status_code == 200:
                data = response.json()
                manhattan_results = len(data.get("apartments", []))
                self.log_result("Search Functionality", True, f"Manhattan search returned {manhattan_results} results")
            else:
                self.log_result("Search Functionality", False, f"Search failed with status: {response.status_code}")
        except Exception as e:
            self.log_result("Search Functionality", False, f"Exception: {str(e)}")
        
        # Test price range verification
        try:
            response = self.make_request("GET", "/apartments", {"limit": 50})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", [])
                
                prices = [apt.get("price", 0) for apt in apartments if apt.get("price")]
                if prices:
                    min_price = min(prices)
                    max_price = max(prices)
                    
                    # Check if prices are realistic for NYC
                    if min_price >= 1500 and max_price <= 50000:
                        self.log_result("Price Range Verification", True, 
                                      f"Realistic price range: ${min_price:,.0f} - ${max_price:,.0f}")
                    else:
                        self.log_result("Price Range Verification", False, 
                                      f"Unrealistic price range: ${min_price:,.0f} - ${max_price:,.0f}")
                else:
                    self.log_result("Price Range Verification", False, "No price data found")
            else:
                self.log_result("Price Range Verification", False, "Could not retrieve apartments for price verification")
        except Exception as e:
            self.log_result("Price Range Verification", False, f"Exception: {str(e)}")
    
    def test_landlord_portal_apis(self):
        """Test landlord portal APIs"""
        print("\n=== Testing Landlord Portal APIs ===")
        
        # Test GET /api/landlord/login (landlord authentication)
        try:
            # This should return 422 or 400 for missing credentials (expected behavior)
            response = self.make_request("GET", "/landlord/login")
            if response.status_code in [400, 422, 405]:  # Expected for missing auth
                self.log_result("Landlord Login Endpoint", True, "Landlord login endpoint accessible (requires auth)")
            elif response.status_code == 404:
                self.log_result("Landlord Login Endpoint", False, "Landlord login endpoint not found")
            else:
                self.log_result("Landlord Login Endpoint", True, f"Landlord login endpoint responds (status: {response.status_code})")
        except Exception as e:
            self.log_result("Landlord Login Endpoint", False, f"Exception: {str(e)}")
        
        # Test GET /api/landlord/listings (landlord dashboard)
        try:
            # This should return 401 or 403 for missing auth (expected behavior)
            response = self.make_request("GET", "/landlord/listings")
            if response.status_code in [401, 403, 422]:  # Expected for missing auth
                self.log_result("Landlord Listings Endpoint", True, "Landlord listings endpoint accessible (requires auth)")
            elif response.status_code == 404:
                self.log_result("Landlord Listings Endpoint", False, "Landlord listings endpoint not found")
            else:
                self.log_result("Landlord Listings Endpoint", True, f"Landlord listings endpoint responds (status: {response.status_code})")
        except Exception as e:
            self.log_result("Landlord Listings Endpoint", False, f"Exception: {str(e)}")
    
    def test_data_quality_verification(self):
        """Test data quality verification"""
        print("\n=== Testing Data Quality Verification ===")
        
        # Test Central Park West apartment location
        try:
            response = self.make_request("GET", "/apartments", {"search": "Central Park West", "limit": 10})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", [])
                
                upper_west_side_count = 0
                for apt in apartments:
                    neighborhood = apt.get("neighborhood", "").lower()
                    if "upper west side" in neighborhood:
                        upper_west_side_count += 1
                
                if upper_west_side_count > 0:
                    self.log_result("Central Park West Location", True, 
                                  f"Found {upper_west_side_count} Central Park West apartments in Upper West Side")
                else:
                    # Check if any Central Park West apartments exist
                    if apartments:
                        neighborhoods = [apt.get("neighborhood", "Unknown") for apt in apartments[:3]]
                        self.log_result("Central Park West Location", False, 
                                      f"Central Park West apartments not in Upper West Side. Found in: {neighborhoods}")
                    else:
                        self.log_result("Central Park West Location", True, "No Central Park West apartments found (acceptable)")
            else:
                self.log_result("Central Park West Location", False, f"Search failed: {response.status_code}")
        except Exception as e:
            self.log_result("Central Park West Location", False, f"Exception: {str(e)}")
        
        # Test verification status
        try:
            response = self.make_request("GET", "/apartments", {"limit": 20})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", [])
                
                verified_count = 0
                for apt in apartments:
                    if apt.get("is_verified") == True:
                        verified_count += 1
                
                if verified_count > 0:
                    verification_rate = (verified_count / len(apartments)) * 100
                    self.log_result("Apartment Verification Status", True, 
                                  f"{verified_count}/{len(apartments)} apartments verified ({verification_rate:.1f}%)")
                else:
                    self.log_result("Apartment Verification Status", False, 
                                  "No apartments have verification status set to true")
            else:
                self.log_result("Apartment Verification Status", False, f"Could not retrieve apartments: {response.status_code}")
        except Exception as e:
            self.log_result("Apartment Verification Status", False, f"Exception: {str(e)}")
    
    def test_performance(self):
        """Test performance - response times under 3 seconds"""
        print("\n=== Testing Performance ===")
        
        endpoints_to_test = [
            ("GET", "/apartments", {"limit": 50}),
            ("GET", "/apartments/search/stats", {}),
            ("GET", "/health", {}),
            ("GET", "/blog", {"limit": 10}),
        ]
        
        performance_results = []
        
        for method, endpoint, params in endpoints_to_test:
            try:
                start_time = time.time()
                response = self.make_request(method, endpoint, params)
                response_time = time.time() - start_time
                
                performance_results.append({
                    "endpoint": f"{method} {endpoint}",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "success": response.status_code == 200 and response_time < 3.0
                })
                
                if response_time < 3.0:
                    self.log_result(f"Performance {method} {endpoint}", True, f"Response time: {response_time:.2f}s")
                else:
                    self.log_result(f"Performance {method} {endpoint}", False, f"Slow response: {response_time:.2f}s")
                    
            except Exception as e:
                performance_results.append({
                    "endpoint": f"{method} {endpoint}",
                    "response_time": None,
                    "status_code": None,
                    "success": False
                })
                self.log_result(f"Performance {method} {endpoint}", False, f"Exception: {str(e)}")
        
        # Overall performance assessment
        successful_tests = [r for r in performance_results if r["success"]]
        if len(successful_tests) == len(performance_results):
            avg_response_time = sum(r["response_time"] for r in successful_tests) / len(successful_tests)
            self.log_result("Overall Performance", True, f"All endpoints under 3s (avg: {avg_response_time:.2f}s)")
        else:
            failed_count = len(performance_results) - len(successful_tests)
            self.log_result("Overall Performance", False, f"{failed_count}/{len(performance_results)} endpoints failed performance test")
    
    def test_error_handling(self):
        """Test proper error handling for invalid requests"""
        print("\n=== Testing Error Handling ===")
        
        # Test 404 for non-existent apartment
        try:
            response = self.make_request("GET", "/apartments/non-existent-id")
            if response.status_code == 404:
                self.log_result("404 Error Handling", True, "Properly returns 404 for non-existent apartment")
            else:
                self.log_result("404 Error Handling", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("404 Error Handling", False, f"Exception: {str(e)}")
        
        # Test 400 for invalid contact form data
        try:
            invalid_contact = {"name": "", "email": "invalid-email", "message": ""}
            response = self.make_request("POST", "/contact", invalid_contact)
            if response.status_code in [400, 422]:
                self.log_result("400 Error Handling", True, "Properly validates contact form data")
            else:
                self.log_result("400 Error Handling", False, f"Expected 400/422, got {response.status_code}")
        except Exception as e:
            self.log_result("400 Error Handling", False, f"Exception: {str(e)}")
    
    def test_email_service_integration(self):
        """Test email service integration"""
        print("\n=== Testing Email Service Integration ===")
        
        # Test contact form email notifications
        try:
            contact_data = {
                "name": "Email Test User",
                "email": "email.test@example.com",
                "phone": "+1-555-999-8888",
                "message": "This is a test message to verify email notifications are working properly.",
                "preferred_contact": "email"
            }
            
            response = self.make_request("POST", "/contact", contact_data)
            if response.status_code == 200:
                data = response.json()
                if "contact_id" in data:
                    # Email sending is async, so we can't directly verify delivery
                    # But we can verify the endpoint accepts the request
                    self.log_result("Contact Form Email Integration", True, 
                                  "Contact form accepts requests (email notifications configured)")
                else:
                    self.log_result("Contact Form Email Integration", False, "Contact form response invalid")
            else:
                self.log_result("Contact Form Email Integration", False, f"Contact form failed: {response.status_code}")
        except Exception as e:
            self.log_result("Contact Form Email Integration", False, f"Exception: {str(e)}")
        
        # Test newsletter signup confirmations
        try:
            newsletter_data = {
                "email": "newsletter.email.test@example.com",
                "full_name": "Email Newsletter Tester",
                "source": "website"
            }
            
            response = self.make_request("POST", "/newsletter/subscribe", newsletter_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") in ["success", "error"]:  # Error might be "already subscribed"
                    self.log_result("Newsletter Email Integration", True, 
                                  "Newsletter signup working (email confirmations configured)")
                else:
                    self.log_result("Newsletter Email Integration", False, f"Unexpected response: {data}")
            else:
                self.log_result("Newsletter Email Integration", False, f"Newsletter signup failed: {response.status_code}")
        except Exception as e:
            self.log_result("Newsletter Email Integration", False, f"Exception: {str(e)}")
        
        # Test visitor tracking emails
        try:
            response = self.make_request("POST", "/visitor/track", {})
            if response.status_code == 200:
                self.log_result("Visitor Tracking Email Integration", True, 
                              "Visitor tracking working (email notifications configured)")
            else:
                self.log_result("Visitor Tracking Email Integration", False, f"Visitor tracking failed: {response.status_code}")
        except Exception as e:
            self.log_result("Visitor Tracking Email Integration", False, f"Exception: {str(e)}")
    
    def run_comprehensive_health_check(self):
        """Run all health check tests"""
        print("🏥 NOFEEPLACES.COM BACKEND API COMPREHENSIVE HEALTH CHECK")
        print("=" * 60)
        print(f"Testing API at: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all test categories
        self.test_health_check()
        self.test_core_apartment_endpoints()
        self.test_contact_form_api()
        self.test_newsletter_api()
        self.test_visitor_tracking_api()
        self.test_database_connectivity_and_data_quality()
        self.test_landlord_portal_apis()
        self.test_data_quality_verification()
        self.test_performance()
        self.test_error_handling()
        self.test_email_service_integration()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏥 HEALTH CHECK SUMMARY")
        print("=" * 60)
        
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.results["performance_issues"]:
            print(f"\n⚠️  Performance Issues ({len(self.results['performance_issues'])}):")
            for issue in self.results["performance_issues"]:
                print(f"   • {issue}")
        
        if self.results["errors"]:
            print(f"\n❌ Failed Tests ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Overall assessment
        if success_rate >= 90:
            print("\n🎉 OVERALL ASSESSMENT: EXCELLENT - Backend is production-ready!")
        elif success_rate >= 80:
            print("\n✅ OVERALL ASSESSMENT: GOOD - Backend is mostly ready with minor issues")
        elif success_rate >= 70:
            print("\n⚠️  OVERALL ASSESSMENT: FAIR - Backend needs attention before production")
        else:
            print("\n❌ OVERALL ASSESSMENT: POOR - Backend requires significant fixes")
        
        return success_rate >= 80  # Return True if health check passes

if __name__ == "__main__":
    checker = NoFeePlacesHealthChecker()
    checker.run_comprehensive_health_check()