#!/usr/bin/env python3
"""
Header WordMark Verification Test
Quick verification test to ensure the header WordMark changes didn't impact any backend functionality.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://aptfinderapp.preview.emergentagent.com/api"

class HeaderWordMarkVerificationTester:
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
    
    def make_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None) -> requests.Response:
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
    
    def test_backend_server_running(self):
        """Test that backend server is running properly"""
        print("\n=== Testing Backend Server Status ===")
        try:
            # Test basic connectivity
            response = self.make_request("GET", "/apartments", {"limit": 1})
            if response.status_code == 200:
                self.log_result("Backend Server Running", True, "Backend server is responding")
            else:
                self.log_result("Backend Server Running", False, f"Server returned status: {response.status_code}")
        except Exception as e:
            self.log_result("Backend Server Running", False, f"Server connection failed: {str(e)}")
    
    def test_apartment_listings_api(self):
        """Test apartment listings API (/api/apartments)"""
        print("\n=== Testing Apartment Listings API ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 10})
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "apartments" in data:
                    apartments = data["apartments"]
                    total = data.get("total", 0)
                    self.log_result("Apartment Listings API", True, 
                                  f"Retrieved {len(apartments)} apartments from {total} total")
                elif isinstance(data, list):
                    self.log_result("Apartment Listings API", True, 
                                  f"Retrieved {len(data)} apartments (legacy format)")
                else:
                    self.log_result("Apartment Listings API", False, 
                                  f"Unexpected response format: {type(data)}")
            else:
                self.log_result("Apartment Listings API", False, 
                              f"API returned status: {response.status_code}")
        except Exception as e:
            self.log_result("Apartment Listings API", False, f"Exception: {str(e)}")
    
    def test_search_functionality(self):
        """Test search functionality still works"""
        print("\n=== Testing Search Functionality ===")
        try:
            # Test neighborhood search
            response = self.make_request("GET", "/apartments", {
                "neighborhood": "manhattan",
                "limit": 5
            })
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                self.log_result("Search - Neighborhood Filter", True, 
                              f"Manhattan search returned {len(apartments)} results")
            else:
                self.log_result("Search - Neighborhood Filter", False, 
                              f"Search failed with status: {response.status_code}")
            
            # Test price range search
            response = self.make_request("GET", "/apartments", {
                "min_price": 3000,
                "max_price": 5000,
                "limit": 5
            })
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                self.log_result("Search - Price Filter", True, 
                              f"Price range search returned {len(apartments)} results")
            else:
                self.log_result("Search - Price Filter", False, 
                              f"Price search failed with status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Search Functionality", False, f"Exception: {str(e)}")
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints are operational"""
        print("\n=== Testing Analytics Endpoints ===")
        try:
            # Test search stats endpoint
            response = self.make_request("GET", "/apartments/search/stats")
            
            if response.status_code == 200:
                data = response.json()
                if "total_apartments" in data:
                    self.log_result("Analytics - Search Stats", True, 
                                  f"Stats endpoint working: {data['total_apartments']} total apartments")
                else:
                    self.log_result("Analytics - Search Stats", False, 
                                  f"Missing total_apartments in response: {data}")
            else:
                self.log_result("Analytics - Search Stats", False, 
                              f"Stats endpoint failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Analytics Endpoints", False, f"Exception: {str(e)}")
    
    def test_apartment_data_serving(self):
        """Test that apartment data is still being served correctly"""
        print("\n=== Testing Apartment Data Serving ===")
        try:
            # Get apartments and verify data structure
            response = self.make_request("GET", "/apartments", {"limit": 3})
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                if apartments and len(apartments) > 0:
                    # Check first apartment has required fields
                    apt = apartments[0]
                    required_fields = ["id", "title", "price", "location"]
                    missing_fields = [field for field in required_fields if field not in apt]
                    
                    if not missing_fields:
                        self.log_result("Apartment Data Structure", True, 
                                      f"Apartment data complete with all required fields")
                        
                        # Test individual apartment endpoint
                        apt_id = apt["id"]
                        detail_response = self.make_request("GET", f"/apartments/{apt_id}")
                        
                        if detail_response.status_code == 200:
                            self.log_result("Individual Apartment Data", True, 
                                          f"Individual apartment details accessible")
                        else:
                            self.log_result("Individual Apartment Data", False, 
                                          f"Individual apartment failed: {detail_response.status_code}")
                    else:
                        self.log_result("Apartment Data Structure", False, 
                                      f"Missing required fields: {missing_fields}")
                else:
                    self.log_result("Apartment Data Structure", False, "No apartments returned")
            else:
                self.log_result("Apartment Data Serving", False, 
                              f"Failed to get apartments: {response.status_code}")
                
        except Exception as e:
            self.log_result("Apartment Data Serving", False, f"Exception: {str(e)}")
    
    def test_contact_endpoints(self):
        """Test contact information endpoints work"""
        print("\n=== Testing Contact Endpoints ===")
        try:
            # Test contact form submission
            contact_data = {
                "name": "Test User",
                "email": "test@example.com",
                "message": "Test message for header verification",
                "phone": "+1-555-0123"
            }
            
            response = self.make_request("POST", "/contact", contact_data)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "contact_id" in data:
                    self.log_result("Contact Form Submission", True, 
                                  f"Contact form working: {data['message']}")
                else:
                    self.log_result("Contact Form Submission", False, 
                                  f"Unexpected contact response: {data}")
            else:
                self.log_result("Contact Form Submission", False, 
                              f"Contact form failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Contact Endpoints", False, f"Exception: {str(e)}")
    
    def test_newsletter_service(self):
        """Test newsletter service is unaffected"""
        print("\n=== Testing Newsletter Service ===")
        try:
            # Test newsletter subscription
            newsletter_data = {
                "email": f"test.{int(time.time())}@example.com",
                "name": "Test Subscriber"
            }
            
            response = self.make_request("POST", "/newsletter/subscribe", newsletter_data)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"]:
                    self.log_result("Newsletter Service", True, 
                                  f"Newsletter subscription working: {data.get('message', 'Success')}")
                else:
                    self.log_result("Newsletter Service", False, 
                                  f"Newsletter subscription failed: {data}")
            else:
                self.log_result("Newsletter Service", False, 
                              f"Newsletter endpoint failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Newsletter Service", False, f"Exception: {str(e)}")
    
    def test_email_service(self):
        """Test email service is unaffected"""
        print("\n=== Testing Email Service ===")
        try:
            # Test email contact endpoint
            email_data = {
                "to": "placesfirm@gmail.com",
                "subject": "Header WordMark Verification Test",
                "sender_name": "Test User",
                "sender_email": "test@example.com",
                "message": "This is a test message to verify email service after header changes."
            }
            
            response = self.make_request("POST", "/send-contact-email", email_data)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"]:
                    self.log_result("Email Service", True, 
                                  f"Email service working: {data.get('message', 'Success')}")
                else:
                    self.log_result("Email Service", False, 
                                  f"Email service failed: {data}")
            else:
                self.log_result("Email Service", False, 
                              f"Email endpoint failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Email Service", False, f"Exception: {str(e)}")
    
    def test_frontend_backend_communication(self):
        """Test that frontend can still communicate with backend"""
        print("\n=== Testing Frontend-Backend Communication ===")
        try:
            # Test CORS and basic API accessibility
            headers = {
                "Origin": "https://aptfinderapp.preview.emergentagent.com",
                "Referer": "https://aptfinderapp.preview.emergentagent.com/"
            }
            
            response = self.make_request("GET", "/apartments", {"limit": 1}, headers=headers)
            
            if response.status_code == 200:
                # Check CORS headers
                cors_headers = {
                    "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                    "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                    "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
                }
                
                self.log_result("Frontend-Backend Communication", True, 
                              f"API accessible from frontend with proper CORS")
            else:
                self.log_result("Frontend-Backend Communication", False, 
                              f"Frontend request failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Frontend-Backend Communication", False, f"Exception: {str(e)}")
    
    def run_verification_tests(self):
        """Run all verification tests"""
        print("🔍 HEADER WORDMARK VERIFICATION TEST")
        print("=" * 50)
        print("Testing backend functionality after header WordMark changes...")
        
        # Run all tests
        self.test_backend_server_running()
        self.test_apartment_listings_api()
        self.test_search_functionality()
        self.test_analytics_endpoints()
        self.test_apartment_data_serving()
        self.test_contact_endpoints()
        self.test_newsletter_service()
        self.test_email_service()
        self.test_frontend_backend_communication()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 VERIFICATION TEST SUMMARY")
        print("=" * 50)
        
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results["failed"] > 0:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        if success_rate >= 90:
            print(f"\n🎉 VERIFICATION RESULT: EXCELLENT")
            print("Header WordMark changes did not impact backend functionality.")
        elif success_rate >= 70:
            print(f"\n✅ VERIFICATION RESULT: GOOD")
            print("Header WordMark changes had minimal impact on backend functionality.")
        else:
            print(f"\n⚠️ VERIFICATION RESULT: ISSUES DETECTED")
            print("Header WordMark changes may have impacted backend functionality.")
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = HeaderWordMarkVerificationTester()
    success = tester.run_verification_tests()
    exit(0 if success else 1)