#!/usr/bin/env python3
"""
NoFeePlaces.com Backend API Verification Test
Tests all backend endpoints to ensure they're working correctly after frontend changes
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://rentnocomm.preview.emergentagent.com/api"
TEST_USER_EMAIL = "verification.test@nofeeplaces.com"
TEST_USER_PASSWORD = "VerifyPassword123!"
TEST_USER_NAME = "Verification Test User"

class BackendVerificationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_apartment_id = None
        self.test_appointment_id = None
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
                response = requests.get(url, headers=default_headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=default_headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_apartments_health_check(self):
        """Test basic API health check - GET /api/apartments"""
        print("\n=== Testing Basic API Health Check - GET /api/apartments ===")
        try:
            response = self.make_request("GET", "/apartments")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.test_apartment_id = data[0].get("id")
                    self.log_result("GET /api/apartments", True, f"Retrieved {len(data)} apartments successfully")
                else:
                    self.log_result("GET /api/apartments", False, f"Expected non-empty list, got: {type(data)} with {len(data) if isinstance(data, list) else 'N/A'} items")
            else:
                self.log_result("GET /api/apartments", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("GET /api/apartments", False, f"Exception: {str(e)}")
    
    def test_authentication_endpoints(self):
        """Test authentication endpoints - POST /api/auth/login and POST /api/auth/register"""
        print("\n=== Testing Authentication Endpoints ===")
        
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
                    self.log_result("POST /api/auth/register", True, "User registered successfully with JWT token")
                else:
                    self.log_result("POST /api/auth/register", False, f"Missing token in response: {data}")
            elif response.status_code == 400:
                # User might already exist, try login
                login_response = self.make_request("POST", "/auth/login", {
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                })
                if login_response.status_code == 200:
                    token_data = login_response.json()
                    self.auth_token = token_data["access_token"]
                    self.log_result("POST /api/auth/register", True, "User already exists, using existing account")
                else:
                    self.log_result("POST /api/auth/register", False, f"Registration and login both failed")
            else:
                self.log_result("POST /api/auth/register", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("POST /api/auth/register", False, f"Exception: {str(e)}")
        
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
                    self.log_result("POST /api/auth/login", True, "Login successful with JWT token")
                else:
                    self.log_result("POST /api/auth/login", False, f"Missing token in response: {data}")
            else:
                self.log_result("POST /api/auth/login", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("POST /api/auth/login", False, f"Exception: {str(e)}")
    
    def test_user_favorites_functionality(self):
        """Test user favorites functionality - GET/POST/DELETE /api/users/favorites"""
        print("\n=== Testing User Favorites Functionality ===")
        
        if not self.auth_token:
            self.log_result("User Favorites", False, "No auth token available")
            return
        
        if not self.test_apartment_id:
            self.log_result("User Favorites", False, "No apartment ID available for testing")
            return
        
        try:
            # Test POST /api/users/favorites/{apartment_id} - Add to favorites
            response = self.make_request("POST", f"/users/favorites/{self.test_apartment_id}")
            if response.status_code == 200:
                self.log_result("POST /api/users/favorites/{id}", True, "Apartment added to favorites")
            else:
                self.log_result("POST /api/users/favorites/{id}", False, f"Status code: {response.status_code}")
            
            # Test GET /api/users/favorites - Get favorites
            response = self.make_request("GET", "/users/favorites")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET /api/users/favorites", True, f"Retrieved {len(data)} favorite apartments")
                else:
                    self.log_result("GET /api/users/favorites", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("GET /api/users/favorites", False, f"Status code: {response.status_code}")
            
            # Test DELETE /api/users/favorites/{apartment_id} - Remove from favorites
            response = self.make_request("DELETE", f"/users/favorites/{self.test_apartment_id}")
            if response.status_code == 200:
                self.log_result("DELETE /api/users/favorites/{id}", True, "Apartment removed from favorites")
            else:
                self.log_result("DELETE /api/users/favorites/{id}", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("User Favorites Functionality", False, f"Exception: {str(e)}")
    
    def test_apartment_search_and_filtering(self):
        """Test apartment search and filtering functionality"""
        print("\n=== Testing Apartment Search and Filtering ===")
        
        try:
            # Test search by term
            response = self.make_request("GET", "/apartments", {"search_term": "luxury"})
            if response.status_code == 200:
                data = response.json()
                self.log_result("Apartment Search (search_term)", True, f"Search returned {len(data)} apartments")
            else:
                self.log_result("Apartment Search (search_term)", False, f"Status code: {response.status_code}")
            
            # Test price filtering
            response = self.make_request("GET", "/apartments", {"min_price": 3000, "max_price": 5000})
            if response.status_code == 200:
                data = response.json()
                self.log_result("Apartment Filter (price)", True, f"Price filter returned {len(data)} apartments")
            else:
                self.log_result("Apartment Filter (price)", False, f"Status code: {response.status_code}")
            
            # Test bedrooms filtering
            response = self.make_request("GET", "/apartments", {"bedrooms": 1})
            if response.status_code == 200:
                data = response.json()
                self.log_result("Apartment Filter (bedrooms)", True, f"Bedrooms filter returned {len(data)} apartments")
            else:
                self.log_result("Apartment Filter (bedrooms)", False, f"Status code: {response.status_code}")
            
            # Test borough filtering
            response = self.make_request("GET", "/apartments", {"borough": "Manhattan"})
            if response.status_code == 200:
                data = response.json()
                self.log_result("Apartment Filter (borough)", True, f"Borough filter returned {len(data)} apartments")
            else:
                self.log_result("Apartment Filter (borough)", False, f"Status code: {response.status_code}")
            
            # Test neighborhood filtering
            response = self.make_request("GET", "/apartments", {"neighborhood": "Chelsea"})
            if response.status_code == 200:
                data = response.json()
                self.log_result("Apartment Filter (neighborhood)", True, f"Neighborhood filter returned {len(data)} apartments")
            else:
                self.log_result("Apartment Filter (neighborhood)", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Apartment Search and Filtering", False, f"Exception: {str(e)}")
    
    def test_ai_chatbot_endpoint(self):
        """Test AI chatbot endpoint - POST /api/chat"""
        print("\n=== Testing AI Chatbot Endpoint - POST /api/chat ===")
        
        try:
            # Test basic chat
            chat_data = {
                "message": "Hello, I'm looking for a 1-bedroom apartment in Manhattan under $4000",
                "session_id": "test_session_123"
            }
            
            response = self.make_request("POST", "/chat", chat_data)
            if response.status_code == 200:
                data = response.json()
                if "response" in data and data["response"]:
                    self.log_result("POST /api/chat (basic)", True, f"AI responded: {data['response'][:100]}...")
                else:
                    self.log_result("POST /api/chat (basic)", False, f"Missing or empty response: {data}")
            else:
                self.log_result("POST /api/chat (basic)", False, f"Status code: {response.status_code}")
            
            # Test chat with apartment context
            if self.test_apartment_id:
                chat_with_context = {
                    "message": "Tell me more about this apartment",
                    "session_id": "test_session_123",
                    "apartment_id": self.test_apartment_id,
                    "context": "apartment_details"
                }
                
                response = self.make_request("POST", "/chat", chat_with_context)
                if response.status_code == 200:
                    data = response.json()
                    if "response" in data and data["response"]:
                        self.log_result("POST /api/chat (with context)", True, f"AI responded with context: {data['response'][:100]}...")
                    else:
                        self.log_result("POST /api/chat (with context)", False, f"Missing or empty response: {data}")
                else:
                    self.log_result("POST /api/chat (with context)", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("AI Chatbot Endpoint", False, f"Exception: {str(e)}")
    
    def test_appointment_booking_system(self):
        """Test appointment booking system - POST /api/appointments"""
        print("\n=== Testing Appointment Booking System - POST /api/appointments ===")
        
        if not self.test_apartment_id:
            self.log_result("Appointment Booking", False, "No apartment ID available for testing")
            return
        
        try:
            # Test valid appointment creation
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            appointment_data = {
                "apartment_id": self.test_apartment_id,
                "visitor_name": "Jane Smith",
                "visitor_email": "jane.smith@email.com",
                "visitor_phone": "+1-555-987-6543",
                "appointment_date": tomorrow,
                "appointment_time": "2:00 PM",
                "notes": "Interested in viewing this apartment for immediate move-in"
            }
            
            response = self.make_request("POST", "/appointments", appointment_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("visitor_name") == "Jane Smith":
                    self.test_appointment_id = data["id"]
                    self.log_result("POST /api/appointments (valid)", True, f"Created appointment for {data['visitor_name']}")
                else:
                    self.log_result("POST /api/appointments (valid)", False, f"Unexpected response: {data}")
            else:
                self.log_result("POST /api/appointments (valid)", False, f"Status code: {response.status_code}")
            
            # Test business hours validation (before 10 AM)
            early_appointment = appointment_data.copy()
            early_appointment["appointment_time"] = "9:00 AM"
            early_appointment["visitor_email"] = "early.test@email.com"
            
            response = self.make_request("POST", "/appointments", early_appointment)
            if response.status_code == 400:
                self.log_result("POST /api/appointments (business hours)", True, "Correctly rejected 9 AM appointment")
            else:
                self.log_result("POST /api/appointments (business hours)", False, f"Should reject 9 AM appointment, got: {response.status_code}")
            
            # Test business hours validation (after 7 PM)
            late_appointment = appointment_data.copy()
            late_appointment["appointment_time"] = "8:00 PM"
            late_appointment["visitor_email"] = "late.test@email.com"
            
            response = self.make_request("POST", "/appointments", late_appointment)
            if response.status_code == 400:
                self.log_result("POST /api/appointments (after hours)", True, "Correctly rejected 8 PM appointment")
            else:
                self.log_result("POST /api/appointments (after hours)", False, f"Should reject 8 PM appointment, got: {response.status_code}")
            
            # Test conflict detection (same time slot)
            if self.test_appointment_id:
                conflict_appointment = appointment_data.copy()
                conflict_appointment["visitor_name"] = "John Conflict"
                conflict_appointment["visitor_email"] = "john.conflict@email.com"
                
                response = self.make_request("POST", "/appointments", conflict_appointment)
                if response.status_code == 409:
                    self.log_result("POST /api/appointments (conflict)", True, "Correctly detected time slot conflict")
                else:
                    self.log_result("POST /api/appointments (conflict)", False, f"Should detect conflict, got: {response.status_code}")
            
        except Exception as e:
            self.log_result("Appointment Booking System", False, f"Exception: {str(e)}")
    
    def test_additional_endpoints(self):
        """Test additional important endpoints"""
        print("\n=== Testing Additional Important Endpoints ===")
        
        try:
            # Test apartment statistics
            response = self.make_request("GET", "/apartments/search/stats")
            if response.status_code == 200:
                data = response.json()
                if "total_apartments" in data:
                    self.log_result("GET /api/apartments/search/stats", True, f"Stats retrieved: {data['total_apartments']} total apartments")
                else:
                    self.log_result("GET /api/apartments/search/stats", False, f"Missing total_apartments in response")
            else:
                self.log_result("GET /api/apartments/search/stats", False, f"Status code: {response.status_code}")
            
            # Test individual apartment details
            if self.test_apartment_id:
                response = self.make_request("GET", f"/apartments/{self.test_apartment_id}")
                if response.status_code == 200:
                    data = response.json()
                    if "id" in data and data["id"] == self.test_apartment_id:
                        self.log_result("GET /api/apartments/{id}", True, f"Retrieved apartment details: {data.get('title', 'Unknown')}")
                    else:
                        self.log_result("GET /api/apartments/{id}", False, f"Unexpected apartment data")
                else:
                    self.log_result("GET /api/apartments/{id}", False, f"Status code: {response.status_code}")
            
            # Test user profile (if authenticated)
            if self.auth_token:
                response = self.make_request("GET", "/auth/me")
                if response.status_code == 200:
                    data = response.json()
                    if "email" in data:
                        self.log_result("GET /api/auth/me", True, f"Profile retrieved for: {data.get('full_name', 'Unknown')}")
                    else:
                        self.log_result("GET /api/auth/me", False, f"Missing email in profile data")
                else:
                    self.log_result("GET /api/auth/me", False, f"Status code: {response.status_code}")
            
        except Exception as e:
            self.log_result("Additional Endpoints", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all verification tests"""
        print("🔍 NoFeePlaces.com Backend API Verification Test")
        print("=" * 60)
        print("Testing backend API endpoints after frontend button hover effects updates")
        print("=" * 60)
        
        # Run all tests in order
        self.test_apartments_health_check()
        self.test_authentication_endpoints()
        self.test_user_favorites_functionality()
        self.test_apartment_search_and_filtering()
        self.test_ai_chatbot_endpoint()
        self.test_appointment_booking_system()
        self.test_additional_endpoints()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 VERIFICATION TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n❌ Failed Tests:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print("\n" + "=" * 60)
        if success_rate >= 90:
            print("🎉 BACKEND API VERIFICATION: PASSED")
            print("All critical endpoints are functioning correctly after frontend changes.")
        else:
            print("⚠️  BACKEND API VERIFICATION: ISSUES DETECTED")
            print("Some endpoints may need attention.")
        print("=" * 60)

if __name__ == "__main__":
    tester = BackendVerificationTester()
    tester.run_all_tests()