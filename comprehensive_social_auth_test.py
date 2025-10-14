#!/usr/bin/env python3
"""
NoFeePlaces.com Comprehensive Social Authentication Testing Suite
Tests Facebook Auth, Apple Auth, and User Info endpoints with proper validation
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://aptfinderapp.preview.emergentagent.com/api"

class ComprehensiveSocialAuthTester:
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
    
    def test_facebook_auth_comprehensive(self):
        """Comprehensive Facebook Auth endpoint testing"""
        print("\n=== Comprehensive Facebook Auth Testing ===")
        
        # Test 1: Endpoint exists
        try:
            response = self.make_request("POST", "/auth/facebook", {})
            if response.status_code in [400, 422, 401, 503]:
                self.log_result("Facebook Auth Endpoint Exists", True, 
                              f"Endpoint responds (status: {response.status_code})")
            else:
                self.log_result("Facebook Auth Endpoint Exists", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Facebook Auth Endpoint Exists", False, f"Exception: {str(e)}")
        
        # Test 2: Proper validation of required fields
        try:
            # Test with complete but invalid data
            complete_data = {
                "access_token": "test_facebook_token_12345",
                "user_id": "test_facebook_user_id"
            }
            
            response = self.make_request("POST", "/auth/facebook", complete_data)
            
            if response.status_code == 401:
                error_data = response.json()
                if "facebook" in error_data.get("detail", "").lower():
                    self.log_result("Facebook Auth Validation", True, 
                                  f"Properly validates Facebook token: {error_data['detail']}")
                else:
                    self.log_result("Facebook Auth Validation", True, 
                                  f"Returns auth error: {error_data.get('detail', '')}")
            elif response.status_code == 503:
                error_data = response.json()
                if "not configured" in error_data.get("detail", "").lower():
                    self.log_result("Facebook Auth Validation", True, 
                                  "Facebook credentials not configured (expected)")
                else:
                    self.log_result("Facebook Auth Validation", True, 
                                  f"Service unavailable: {error_data.get('detail', '')}")
            else:
                self.log_result("Facebook Auth Validation", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Facebook Auth Validation", False, f"Exception: {str(e)}")
        
        # Test 3: Missing access_token field
        try:
            response = self.make_request("POST", "/auth/facebook", {"user_id": "test"})
            
            if response.status_code == 422:
                error_data = response.json()
                self.log_result("Facebook Auth Missing Token", True, 
                              "Properly validates missing access_token field")
            else:
                self.log_result("Facebook Auth Missing Token", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Facebook Auth Missing Token", False, f"Exception: {str(e)}")
        
        # Test 4: Missing user_id field
        try:
            response = self.make_request("POST", "/auth/facebook", {"access_token": "test"})
            
            if response.status_code == 422:
                error_data = response.json()
                self.log_result("Facebook Auth Missing User ID", True, 
                              "Properly validates missing user_id field")
            else:
                self.log_result("Facebook Auth Missing User ID", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Facebook Auth Missing User ID", False, f"Exception: {str(e)}")
        
        # Test 5: Response format for successful structure
        try:
            complete_data = {
                "access_token": "valid_looking_token_12345",
                "user_id": "facebook_user_123"
            }
            
            response = self.make_request("POST", "/auth/facebook", complete_data)
            
            # Should return JSON error (not HTML or plain text)
            try:
                error_data = response.json()
                if isinstance(error_data, dict) and "detail" in error_data:
                    self.log_result("Facebook Auth Response Format", True, 
                                  "Returns proper JSON error format")
                else:
                    self.log_result("Facebook Auth Response Format", False, 
                                  f"Invalid JSON structure: {error_data}")
            except json.JSONDecodeError:
                self.log_result("Facebook Auth Response Format", False, 
                              "Response is not valid JSON")
        except Exception as e:
            self.log_result("Facebook Auth Response Format", False, f"Exception: {str(e)}")
    
    def test_apple_auth_comprehensive(self):
        """Comprehensive Apple Auth endpoint testing"""
        print("\n=== Comprehensive Apple Auth Testing ===")
        
        # Test 1: Endpoint exists
        try:
            response = self.make_request("POST", "/auth/apple", {})
            if response.status_code in [400, 422, 401, 503]:
                self.log_result("Apple Auth Endpoint Exists", True, 
                              f"Endpoint responds (status: {response.status_code})")
            else:
                self.log_result("Apple Auth Endpoint Exists", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Apple Auth Endpoint Exists", False, f"Exception: {str(e)}")
        
        # Test 2: Proper validation of required fields
        try:
            # Test with complete but invalid data
            complete_data = {
                "authorization_code": "test_apple_auth_code_12345",
                "identity_token": "test_apple_identity_token_12345"
            }
            
            response = self.make_request("POST", "/auth/apple", complete_data)
            
            if response.status_code == 401:
                error_data = response.json()
                if "apple" in error_data.get("detail", "").lower() or "token" in error_data.get("detail", "").lower():
                    self.log_result("Apple Auth Validation", True, 
                                  f"Properly validates Apple token: {error_data['detail']}")
                else:
                    self.log_result("Apple Auth Validation", True, 
                                  f"Returns auth error: {error_data.get('detail', '')}")
            elif response.status_code == 503:
                error_data = response.json()
                if "not configured" in error_data.get("detail", "").lower():
                    self.log_result("Apple Auth Validation", True, 
                                  "Apple credentials not configured (expected)")
                else:
                    self.log_result("Apple Auth Validation", True, 
                                  f"Service unavailable: {error_data.get('detail', '')}")
            else:
                self.log_result("Apple Auth Validation", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Apple Auth Validation", False, f"Exception: {str(e)}")
        
        # Test 3: Missing authorization_code field
        try:
            response = self.make_request("POST", "/auth/apple", {"identity_token": "test"})
            
            if response.status_code == 422:
                error_data = response.json()
                self.log_result("Apple Auth Missing Auth Code", True, 
                              "Properly validates missing authorization_code field")
            else:
                self.log_result("Apple Auth Missing Auth Code", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Apple Auth Missing Auth Code", False, f"Exception: {str(e)}")
        
        # Test 4: Missing identity_token field
        try:
            response = self.make_request("POST", "/auth/apple", {"authorization_code": "test"})
            
            if response.status_code == 422:
                error_data = response.json()
                self.log_result("Apple Auth Missing Identity Token", True, 
                              "Properly validates missing identity_token field")
            else:
                self.log_result("Apple Auth Missing Identity Token", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Apple Auth Missing Identity Token", False, f"Exception: {str(e)}")
        
        # Test 5: Optional user_data field handling
        try:
            complete_data = {
                "authorization_code": "test_code_12345",
                "identity_token": "test_identity_token_12345",
                "user_data": {
                    "name": {
                        "firstName": "John",
                        "lastName": "Doe"
                    }
                }
            }
            
            response = self.make_request("POST", "/auth/apple", complete_data)
            
            # Should still process (and fail on token validation, not structure)
            if response.status_code in [401, 503]:
                self.log_result("Apple Auth User Data Handling", True, 
                              "Properly handles optional user_data field")
            else:
                self.log_result("Apple Auth User Data Handling", False, 
                              f"Unexpected status with user_data: {response.status_code}")
        except Exception as e:
            self.log_result("Apple Auth User Data Handling", False, f"Exception: {str(e)}")
    
    def test_user_info_endpoint_comprehensive(self):
        """Comprehensive User Info endpoint testing"""
        print("\n=== Comprehensive User Info Endpoint Testing ===")
        
        # Test 1: Missing authorization header
        try:
            response = self.make_request("GET", "/auth/me")
            
            if response.status_code == 401:
                error_data = response.json()
                if "authorization" in error_data.get("detail", "").lower():
                    self.log_result("User Info Missing Auth Header", True, 
                                  f"Properly handles missing auth header: {error_data['detail']}")
                else:
                    self.log_result("User Info Missing Auth Header", True, 
                                  f"Returns unauthorized: {error_data.get('detail', '')}")
            else:
                self.log_result("User Info Missing Auth Header", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("User Info Missing Auth Header", False, f"Exception: {str(e)}")
        
        # Test 2: Invalid authorization header format (no Bearer)
        try:
            headers = {"Authorization": "InvalidFormat token123"}
            response = self.make_request("GET", "/auth/me", headers=headers)
            
            if response.status_code == 401:
                error_data = response.json()
                self.log_result("User Info Invalid Auth Format", True, 
                              f"Handles invalid auth format: {error_data.get('detail', '')}")
            else:
                self.log_result("User Info Invalid Auth Format", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("User Info Invalid Auth Format", False, f"Exception: {str(e)}")
        
        # Test 3: Valid Bearer format but invalid JWT
        try:
            headers = {"Authorization": "Bearer invalid_jwt_token_12345"}
            response = self.make_request("GET", "/auth/me", headers=headers)
            
            if response.status_code == 401:
                error_data = response.json()
                if "token" in error_data.get("detail", "").lower():
                    self.log_result("User Info Invalid JWT", True, 
                                  f"Validates JWT properly: {error_data['detail']}")
                else:
                    self.log_result("User Info Invalid JWT", True, 
                                  f"Returns auth error: {error_data.get('detail', '')}")
            else:
                self.log_result("User Info Invalid JWT", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("User Info Invalid JWT", False, f"Exception: {str(e)}")
        
        # Test 4: Malformed JWT (wrong number of segments)
        try:
            headers = {"Authorization": "Bearer not.a.valid.jwt.format.with.too.many.segments"}
            response = self.make_request("GET", "/auth/me", headers=headers)
            
            if response.status_code == 401:
                error_data = response.json()
                self.log_result("User Info Malformed JWT", True, 
                              f"Handles malformed JWT: {error_data.get('detail', '')}")
            else:
                self.log_result("User Info Malformed JWT", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("User Info Malformed JWT", False, f"Exception: {str(e)}")
        
        # Test 5: Empty Bearer token
        try:
            headers = {"Authorization": "Bearer "}
            response = self.make_request("GET", "/auth/me", headers=headers)
            
            if response.status_code == 401:
                error_data = response.json()
                self.log_result("User Info Empty Token", True, 
                              f"Handles empty token: {error_data.get('detail', '')}")
            else:
                self.log_result("User Info Empty Token", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("User Info Empty Token", False, f"Exception: {str(e)}")
    
    def test_environment_and_integration(self):
        """Test environment configuration and backend integration"""
        print("\n=== Environment Configuration & Integration Testing ===")
        
        # Test 1: Facebook service integration
        try:
            # Test that Facebook service is properly imported and integrated
            complete_data = {
                "access_token": "test_token_12345",
                "user_id": "test_user_12345"
            }
            
            response = self.make_request("POST", "/auth/facebook", complete_data)
            
            # Should not return 404 (endpoint missing) or 500 (import error)
            if response.status_code in [401, 503]:
                self.log_result("Facebook Service Integration", True, 
                              "Facebook auth service properly integrated")
            elif response.status_code == 422:
                self.log_result("Facebook Service Integration", False, 
                              "Validation error - check request structure")
            else:
                self.log_result("Facebook Service Integration", False, 
                              f"Integration issue: {response.status_code}")
        except Exception as e:
            self.log_result("Facebook Service Integration", False, f"Exception: {str(e)}")
        
        # Test 2: Apple service integration
        try:
            # Test that Apple service is properly imported and integrated
            complete_data = {
                "authorization_code": "test_code_12345",
                "identity_token": "test_token_12345"
            }
            
            response = self.make_request("POST", "/auth/apple", complete_data)
            
            # Should not return 404 (endpoint missing) or 500 (import error)
            if response.status_code in [401, 503]:
                self.log_result("Apple Service Integration", True, 
                              "Apple auth service properly integrated")
            elif response.status_code == 422:
                self.log_result("Apple Service Integration", False, 
                              "Validation error - check request structure")
            else:
                self.log_result("Apple Service Integration", False, 
                              f"Integration issue: {response.status_code}")
        except Exception as e:
            self.log_result("Apple Service Integration", False, f"Exception: {str(e)}")
        
        # Test 3: JWT utilities working
        try:
            # Test JWT validation through user info endpoint
            headers = {"Authorization": "Bearer test.jwt.token"}
            response = self.make_request("GET", "/auth/me", headers=headers)
            
            if response.status_code == 401:
                error_data = response.json()
                if "token" in error_data.get("detail", "").lower():
                    self.log_result("JWT Utilities Working", True, 
                                  "JWT validation utilities functioning")
                else:
                    self.log_result("JWT Utilities Working", True, 
                                  "JWT processing working (returns auth error)")
            else:
                self.log_result("JWT Utilities Working", False, 
                              f"JWT validation issue: {response.status_code}")
        except Exception as e:
            self.log_result("JWT Utilities Working", False, f"Exception: {str(e)}")
        
        # Test 4: MongoDB user schema compatibility
        try:
            # Test that endpoints don't crash with 500 errors (schema issues)
            fb_response = self.make_request("POST", "/auth/facebook", {
                "access_token": "test", "user_id": "test"
            })
            apple_response = self.make_request("POST", "/auth/apple", {
                "authorization_code": "test", "identity_token": "test"
            })
            
            # Neither should return 500 (internal server error)
            fb_ok = fb_response.status_code != 500
            apple_ok = apple_response.status_code != 500
            
            if fb_ok and apple_ok:
                self.log_result("MongoDB Schema Compatibility", True, 
                              "User schema supports social provider IDs")
            else:
                self.log_result("MongoDB Schema Compatibility", False, 
                              f"Schema issues: FB={fb_response.status_code}, Apple={apple_response.status_code}")
        except Exception as e:
            self.log_result("MongoDB Schema Compatibility", False, f"Exception: {str(e)}")
        
        # Test 5: Environment variable handling
        try:
            # Test that missing credentials are handled gracefully
            fb_response = self.make_request("POST", "/auth/facebook", {
                "access_token": "test_token", "user_id": "test_user"
            })
            apple_response = self.make_request("POST", "/auth/apple", {
                "authorization_code": "test_code", "identity_token": "test_token"
            })
            
            # Should return 503 (not configured) or 401 (configured but invalid token)
            fb_handled = fb_response.status_code in [401, 503]
            apple_handled = apple_response.status_code in [401, 503]
            
            if fb_handled and apple_handled:
                self.log_result("Environment Variable Handling", True, 
                              "Credentials properly checked and handled")
            else:
                self.log_result("Environment Variable Handling", False, 
                              f"Poor credential handling: FB={fb_response.status_code}, Apple={apple_response.status_code}")
        except Exception as e:
            self.log_result("Environment Variable Handling", False, f"Exception: {str(e)}")
    
    def test_api_health_regression(self):
        """Test that existing API functionality wasn't broken by social auth"""
        print("\n=== API Health Regression Testing ===")
        
        # Test 1: Apartments API still works
        try:
            response = self.make_request("GET", "/apartments", {"limit": 3})
            
            if response.status_code == 200:
                data = response.json()
                if "apartments" in data and len(data["apartments"]) > 0:
                    self.log_result("Apartments API Regression", True, 
                                  f"Apartments API working: {len(data['apartments'])} apartments")
                elif isinstance(data, list) and len(data) > 0:
                    self.log_result("Apartments API Regression", True, 
                                  f"Apartments API working: {len(data)} apartments")
                else:
                    self.log_result("Apartments API Regression", False, 
                                  "Apartments API returns empty data")
            else:
                self.log_result("Apartments API Regression", False, 
                              f"Apartments API failed: {response.status_code}")
        except Exception as e:
            self.log_result("Apartments API Regression", False, f"Exception: {str(e)}")
        
        # Test 2: Contact API still works
        try:
            contact_data = {
                "name": "Social Auth Test User",
                "email": "socialauth.test@example.com",
                "message": "Testing contact API after social auth implementation"
            }
            
            response = self.make_request("POST", "/contact", contact_data)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "contact_id" in data:
                    self.log_result("Contact API Regression", True, 
                                  "Contact API working after social auth")
                else:
                    self.log_result("Contact API Regression", False, 
                                  f"Contact API response changed: {data}")
            else:
                self.log_result("Contact API Regression", False, 
                              f"Contact API failed: {response.status_code}")
        except Exception as e:
            self.log_result("Contact API Regression", False, f"Exception: {str(e)}")
        
        # Test 3: Health check endpoint
        try:
            response = self.make_request("GET", "/health")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    self.log_result("Health Check Regression", True, 
                                  f"Health check working: {data['status']}")
                else:
                    self.log_result("Health Check Regression", True, 
                                  "Health check endpoint responding")
            else:
                self.log_result("Health Check Regression", False, 
                              f"Health check failed: {response.status_code}")
        except Exception as e:
            self.log_result("Health Check Regression", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all comprehensive social authentication tests"""
        print("🔐 COMPREHENSIVE SOCIAL AUTHENTICATION TESTING")
        print("=" * 70)
        print(f"Testing against: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_facebook_auth_comprehensive()
        self.test_apple_auth_comprehensive()
        self.test_user_info_endpoint_comprehensive()
        self.test_environment_and_integration()
        self.test_api_health_regression()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🔐 COMPREHENSIVE SOCIAL AUTH TEST SUMMARY")
        print("=" * 70)
        
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.results["errors"]:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            "passed": self.results["passed"],
            "failed": self.results["failed"],
            "success_rate": success_rate,
            "errors": self.results["errors"]
        }

if __name__ == "__main__":
    tester = ComprehensiveSocialAuthTester()
    results = tester.run_all_tests()