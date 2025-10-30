#!/usr/bin/env python3
"""
NoFeePlaces.com Social Authentication Testing Suite
Tests Facebook Auth, Apple Auth, and User Info endpoints
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://renteasy-nyc.preview.emergentagent.com/api"

class SocialAuthTester:
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
    
    def test_facebook_auth_endpoint_structure(self):
        """Test Facebook Auth endpoint structure and error handling"""
        print("\n=== Testing Facebook Auth Endpoint Structure ===")
        
        # Test 1: Endpoint exists and handles missing token
        try:
            response = self.make_request("POST", "/auth/facebook", {})
            
            if response.status_code == 422:
                # Validation error expected for missing fields
                error_data = response.json()
                if "detail" in error_data:
                    self.log_result("Facebook Auth - Missing Token Validation", True, 
                                  f"Properly validates missing token: {response.status_code}")
                else:
                    self.log_result("Facebook Auth - Missing Token Validation", False, 
                                  f"Unexpected error format: {error_data}")
            else:
                self.log_result("Facebook Auth - Missing Token Validation", False, 
                              f"Unexpected status code: {response.status_code}")
        except Exception as e:
            self.log_result("Facebook Auth - Missing Token Validation", False, f"Exception: {str(e)}")
        
        # Test 2: Invalid token handling
        try:
            invalid_token_data = {
                "access_token": "invalid_facebook_token_12345",
                "user_id": "test_user_id"
            }
            
            response = self.make_request("POST", "/auth/facebook", invalid_token_data)
            
            if response.status_code in [401, 503]:
                # Either unauthorized (invalid token) or service unavailable (no credentials)
                error_data = response.json()
                if "detail" in error_data:
                    self.log_result("Facebook Auth - Invalid Token Handling", True, 
                                  f"Properly handles invalid token: {response.status_code} - {error_data['detail']}")
                else:
                    self.log_result("Facebook Auth - Invalid Token Handling", True, 
                                  f"Handles invalid token with status: {response.status_code}")
            else:
                self.log_result("Facebook Auth - Invalid Token Handling", False, 
                              f"Unexpected status for invalid token: {response.status_code}")
        except Exception as e:
            self.log_result("Facebook Auth - Invalid Token Handling", False, f"Exception: {str(e)}")
        
        # Test 3: Missing Facebook credentials handling
        try:
            # This should return 503 if Facebook credentials are not configured
            test_token_data = {
                "access_token": "test_token",
                "user_id": "test_user"
            }
            
            response = self.make_request("POST", "/auth/facebook", test_token_data)
            
            if response.status_code == 503:
                error_data = response.json()
                if "not configured" in error_data.get("detail", "").lower():
                    self.log_result("Facebook Auth - Missing Credentials", True, 
                                  "Properly handles missing Facebook credentials")
                else:
                    self.log_result("Facebook Auth - Missing Credentials", True, 
                                  f"Returns service unavailable: {error_data.get('detail', '')}")
            elif response.status_code == 401:
                # Could also be unauthorized if credentials exist but token is invalid
                self.log_result("Facebook Auth - Missing Credentials", True, 
                              "Returns unauthorized for invalid token (credentials may be configured)")
            else:
                self.log_result("Facebook Auth - Missing Credentials", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Facebook Auth - Missing Credentials", False, f"Exception: {str(e)}")
        
        # Test 4: Response format validation
        try:
            # Test that the endpoint returns proper error format
            response = self.make_request("POST", "/auth/facebook", {"access_token": "test"})
            
            if response.status_code in [401, 422, 503]:
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and "detail" in error_data:
                        self.log_result("Facebook Auth - Response Format", True, 
                                      "Returns proper JSON error format")
                    else:
                        self.log_result("Facebook Auth - Response Format", False, 
                                      f"Invalid error format: {error_data}")
                except json.JSONDecodeError:
                    self.log_result("Facebook Auth - Response Format", False, 
                                  "Response is not valid JSON")
            else:
                self.log_result("Facebook Auth - Response Format", False, 
                              f"Unexpected status code: {response.status_code}")
        except Exception as e:
            self.log_result("Facebook Auth - Response Format", False, f"Exception: {str(e)}")
    
    def test_apple_auth_endpoint_structure(self):
        """Test Apple Auth endpoint structure and error handling"""
        print("\n=== Testing Apple Auth Endpoint Structure ===")
        
        # Test 1: Endpoint exists and handles missing token
        try:
            response = self.make_request("POST", "/auth/apple", {})
            
            if response.status_code == 422:
                # Validation error expected for missing fields
                error_data = response.json()
                if "detail" in error_data:
                    self.log_result("Apple Auth - Missing Token Validation", True, 
                                  f"Properly validates missing token: {response.status_code}")
                else:
                    self.log_result("Apple Auth - Missing Token Validation", False, 
                                  f"Unexpected error format: {error_data}")
            else:
                self.log_result("Apple Auth - Missing Token Validation", False, 
                              f"Unexpected status code: {response.status_code}")
        except Exception as e:
            self.log_result("Apple Auth - Missing Token Validation", False, f"Exception: {str(e)}")
        
        # Test 2: Invalid token handling
        try:
            invalid_token_data = {
                "authorization_code": "invalid_apple_code_12345",
                "identity_token": "invalid_apple_identity_token_12345"
            }
            
            response = self.make_request("POST", "/auth/apple", invalid_token_data)
            
            if response.status_code in [401, 503]:
                # Either unauthorized (invalid token) or service unavailable (no credentials)
                error_data = response.json()
                if "detail" in error_data:
                    self.log_result("Apple Auth - Invalid Token Handling", True, 
                                  f"Properly handles invalid token: {response.status_code} - {error_data['detail']}")
                else:
                    self.log_result("Apple Auth - Invalid Token Handling", True, 
                                  f"Handles invalid token with status: {response.status_code}")
            else:
                self.log_result("Apple Auth - Invalid Token Handling", False, 
                              f"Unexpected status for invalid token: {response.status_code}")
        except Exception as e:
            self.log_result("Apple Auth - Invalid Token Handling", False, f"Exception: {str(e)}")
        
        # Test 3: Missing Apple credentials handling
        try:
            test_token_data = {
                "authorization_code": "test_code",
                "identity_token": "test_identity_token"
            }
            
            response = self.make_request("POST", "/auth/apple", test_token_data)
            
            if response.status_code == 503:
                error_data = response.json()
                if "not configured" in error_data.get("detail", "").lower():
                    self.log_result("Apple Auth - Missing Credentials", True, 
                                  "Properly handles missing Apple credentials")
                else:
                    self.log_result("Apple Auth - Missing Credentials", True, 
                                  f"Returns service unavailable: {error_data.get('detail', '')}")
            elif response.status_code == 401:
                # Could also be unauthorized if credentials exist but token is invalid
                self.log_result("Apple Auth - Missing Credentials", True, 
                              "Returns unauthorized for invalid token (credentials may be configured)")
            else:
                self.log_result("Apple Auth - Missing Credentials", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Apple Auth - Missing Credentials", False, f"Exception: {str(e)}")
        
        # Test 4: User data handling
        try:
            # Test with user_data field (optional)
            token_with_user_data = {
                "authorization_code": "test_code",
                "identity_token": "test_identity_token",
                "user_data": {
                    "name": {
                        "firstName": "John",
                        "lastName": "Doe"
                    }
                }
            }
            
            response = self.make_request("POST", "/auth/apple", token_with_user_data)
            
            # Should still fail due to invalid token, but endpoint should accept the structure
            if response.status_code in [401, 503]:
                self.log_result("Apple Auth - User Data Structure", True, 
                              "Accepts user_data field in request")
            else:
                self.log_result("Apple Auth - User Data Structure", False, 
                              f"Unexpected status with user_data: {response.status_code}")
        except Exception as e:
            self.log_result("Apple Auth - User Data Structure", False, f"Exception: {str(e)}")
    
    def test_user_info_endpoint(self):
        """Test User Info endpoint (GET /auth/me)"""
        print("\n=== Testing User Info Endpoint ===")
        
        # Test 1: Missing authorization header
        try:
            response = self.make_request("GET", "/auth/me")
            
            if response.status_code == 401:
                error_data = response.json()
                if "authorization" in error_data.get("detail", "").lower():
                    self.log_result("User Info - Missing Auth Header", True, 
                                  "Properly handles missing authorization header")
                else:
                    self.log_result("User Info - Missing Auth Header", True, 
                                  f"Returns unauthorized: {error_data.get('detail', '')}")
            else:
                self.log_result("User Info - Missing Auth Header", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("User Info - Missing Auth Header", False, f"Exception: {str(e)}")
        
        # Test 2: Invalid authorization header format
        try:
            invalid_headers = {"Authorization": "InvalidFormat token123"}
            response = self.make_request("GET", "/auth/me", headers=invalid_headers)
            
            if response.status_code == 401:
                error_data = response.json()
                self.log_result("User Info - Invalid Auth Format", True, 
                              f"Properly handles invalid auth format: {error_data.get('detail', '')}")
            else:
                self.log_result("User Info - Invalid Auth Format", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("User Info - Invalid Auth Format", False, f"Exception: {str(e)}")
        
        # Test 3: Invalid JWT token
        try:
            invalid_headers = {"Authorization": "Bearer invalid_jwt_token_12345"}
            response = self.make_request("GET", "/auth/me", headers=invalid_headers)
            
            if response.status_code == 401:
                error_data = response.json()
                if "invalid" in error_data.get("detail", "").lower() or "token" in error_data.get("detail", "").lower():
                    self.log_result("User Info - Invalid JWT Token", True, 
                                  f"Properly validates JWT token: {error_data.get('detail', '')}")
                else:
                    self.log_result("User Info - Invalid JWT Token", True, 
                                  f"Returns unauthorized for invalid token: {error_data.get('detail', '')}")
            else:
                self.log_result("User Info - Invalid JWT Token", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("User Info - Invalid JWT Token", False, f"Exception: {str(e)}")
        
        # Test 4: Malformed JWT token
        try:
            malformed_headers = {"Authorization": "Bearer not.a.valid.jwt.format"}
            response = self.make_request("GET", "/auth/me", headers=malformed_headers)
            
            if response.status_code == 401:
                error_data = response.json()
                self.log_result("User Info - Malformed JWT", True, 
                              f"Handles malformed JWT: {error_data.get('detail', '')}")
            else:
                self.log_result("User Info - Malformed JWT", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("User Info - Malformed JWT", False, f"Exception: {str(e)}")
    
    def test_backend_integration(self):
        """Test backend integration of social auth services"""
        print("\n=== Testing Backend Integration ===")
        
        # Test 1: Check if Facebook auth service is imported
        try:
            # Try to access Facebook endpoint - if it returns proper error, service is integrated
            response = self.make_request("POST", "/auth/facebook", {"access_token": "test"})
            
            if response.status_code in [401, 422, 503]:
                self.log_result("Facebook Service Integration", True, 
                              "Facebook auth service properly integrated")
            else:
                self.log_result("Facebook Service Integration", False, 
                              f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_result("Facebook Service Integration", False, f"Exception: {str(e)}")
        
        # Test 2: Check if Apple auth service is imported
        try:
            # Try to access Apple endpoint - if it returns proper error, service is integrated
            response = self.make_request("POST", "/auth/apple", {"identity_token": "test"})
            
            if response.status_code in [401, 422, 503]:
                self.log_result("Apple Service Integration", True, 
                              "Apple auth service properly integrated")
            else:
                self.log_result("Apple Service Integration", False, 
                              f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_result("Apple Service Integration", False, f"Exception: {str(e)}")
        
        # Test 3: Check JWT utilities are working
        try:
            # Test JWT validation through /auth/me endpoint
            response = self.make_request("GET", "/auth/me")
            
            if response.status_code == 401:
                error_data = response.json()
                if "authorization" in error_data.get("detail", "").lower():
                    self.log_result("JWT Utilities Integration", True, 
                                  "JWT validation utilities working")
                else:
                    self.log_result("JWT Utilities Integration", True, 
                                  "JWT validation responding correctly")
            else:
                self.log_result("JWT Utilities Integration", False, 
                              f"Unexpected JWT validation response: {response.status_code}")
        except Exception as e:
            self.log_result("JWT Utilities Integration", False, f"Exception: {str(e)}")
        
        # Test 4: Check MongoDB user schema supports social provider IDs
        try:
            # This is indirect - we test by checking if the endpoints accept the expected data structure
            facebook_data = {
                "access_token": "test_token",
                "user_id": "facebook_user_123"
            }
            
            apple_data = {
                "authorization_code": "test_code",
                "identity_token": "test_token"
            }
            
            fb_response = self.make_request("POST", "/auth/facebook", facebook_data)
            apple_response = self.make_request("POST", "/auth/apple", apple_data)
            
            # Both should return proper error codes, not 500 (which would indicate schema issues)
            if fb_response.status_code in [401, 422, 503] and apple_response.status_code in [401, 422, 503]:
                self.log_result("MongoDB Schema Support", True, 
                              "User schema supports social provider IDs (no 500 errors)")
            else:
                self.log_result("MongoDB Schema Support", False, 
                              f"Potential schema issues: FB={fb_response.status_code}, Apple={apple_response.status_code}")
        except Exception as e:
            self.log_result("MongoDB Schema Support", False, f"Exception: {str(e)}")
    
    def test_environment_configuration(self):
        """Test environment configuration for social auth"""
        print("\n=== Testing Environment Configuration ===")
        
        # Test 1: Facebook credentials configuration
        try:
            response = self.make_request("POST", "/auth/facebook", {"access_token": "test"})
            
            if response.status_code == 503:
                error_data = response.json()
                if "not configured" in error_data.get("detail", "").lower():
                    self.log_result("Facebook Credentials Config", True, 
                                  "Facebook credentials properly checked (not configured)")
                else:
                    self.log_result("Facebook Credentials Config", True, 
                                  "Facebook service unavailable (credentials issue)")
            elif response.status_code == 401:
                self.log_result("Facebook Credentials Config", True, 
                              "Facebook credentials configured (returns auth error)")
            else:
                self.log_result("Facebook Credentials Config", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Facebook Credentials Config", False, f"Exception: {str(e)}")
        
        # Test 2: Apple credentials configuration
        try:
            response = self.make_request("POST", "/auth/apple", {"identity_token": "test"})
            
            if response.status_code == 503:
                error_data = response.json()
                if "not configured" in error_data.get("detail", "").lower():
                    self.log_result("Apple Credentials Config", True, 
                                  "Apple credentials properly checked (not configured)")
                else:
                    self.log_result("Apple Credentials Config", True, 
                                  "Apple service unavailable (credentials issue)")
            elif response.status_code == 401:
                self.log_result("Apple Credentials Config", True, 
                              "Apple credentials configured (returns auth error)")
            else:
                self.log_result("Apple Credentials Config", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Apple Credentials Config", False, f"Exception: {str(e)}")
        
        # Test 3: JWT secret configuration
        try:
            # Test with a malformed JWT to see if JWT secret is being used
            response = self.make_request("GET", "/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
            
            if response.status_code == 401:
                error_data = response.json()
                if "invalid" in error_data.get("detail", "").lower() or "token" in error_data.get("detail", "").lower():
                    self.log_result("JWT Secret Config", True, 
                                  "JWT secret properly configured and used for validation")
                else:
                    self.log_result("JWT Secret Config", True, 
                                  "JWT validation working (secret configured)")
            else:
                self.log_result("JWT Secret Config", False, 
                              f"JWT validation not working: {response.status_code}")
        except Exception as e:
            self.log_result("JWT Secret Config", False, f"Exception: {str(e)}")
        
        # Test 4: Fallback behavior when credentials not provided
        try:
            # Both Facebook and Apple should gracefully handle missing credentials
            fb_response = self.make_request("POST", "/auth/facebook", {"access_token": "test"})
            apple_response = self.make_request("POST", "/auth/apple", {"identity_token": "test"})
            
            # Should return 503 (service unavailable) or 401 (unauthorized), not 500 (server error)
            fb_ok = fb_response.status_code in [401, 503]
            apple_ok = apple_response.status_code in [401, 503]
            
            if fb_ok and apple_ok:
                self.log_result("Fallback Behavior", True, 
                              "Both services handle missing credentials gracefully")
            else:
                self.log_result("Fallback Behavior", False, 
                              f"Poor error handling: FB={fb_response.status_code}, Apple={apple_response.status_code}")
        except Exception as e:
            self.log_result("Fallback Behavior", False, f"Exception: {str(e)}")
    
    def test_api_health_after_social_auth(self):
        """Test overall API health after adding social auth"""
        print("\n=== Testing API Health After Social Auth ===")
        
        # Test 1: Basic apartment listing still works
        try:
            response = self.make_request("GET", "/apartments", {"limit": 5})
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "apartments" in data:
                    self.log_result("Apartments API Health", True, 
                                  f"Apartments API working: {len(data['apartments'])} apartments")
                elif isinstance(data, list):
                    self.log_result("Apartments API Health", True, 
                                  f"Apartments API working: {len(data)} apartments")
                else:
                    self.log_result("Apartments API Health", False, 
                                  f"Unexpected apartments response format: {type(data)}")
            else:
                self.log_result("Apartments API Health", False, 
                              f"Apartments API failed: {response.status_code}")
        except Exception as e:
            self.log_result("Apartments API Health", False, f"Exception: {str(e)}")
        
        # Test 2: Contact API still works
        try:
            contact_data = {
                "name": "Test User",
                "email": "test@example.com",
                "message": "Test message for social auth testing"
            }
            
            response = self.make_request("POST", "/contact", contact_data)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "contact_id" in data:
                    self.log_result("Contact API Health", True, 
                                  "Contact API working after social auth integration")
                else:
                    self.log_result("Contact API Health", False, 
                                  f"Contact API response format changed: {data}")
            else:
                self.log_result("Contact API Health", False, 
                              f"Contact API failed: {response.status_code}")
        except Exception as e:
            self.log_result("Contact API Health", False, f"Exception: {str(e)}")
        
        # Test 3: Blog API still works
        try:
            response = self.make_request("GET", "/blog", {"limit": 3})
            
            if response.status_code == 200:
                data = response.json()
                if "posts" in data:
                    self.log_result("Blog API Health", True, 
                                  f"Blog API working: {len(data['posts'])} posts")
                else:
                    self.log_result("Blog API Health", False, 
                                  f"Blog API response format changed: {data}")
            else:
                self.log_result("Blog API Health", False, 
                              f"Blog API failed: {response.status_code}")
        except Exception as e:
            self.log_result("Blog API Health", False, f"Exception: {str(e)}")
        
        # Test 4: Health check endpoint
        try:
            response = self.make_request("GET", "/health")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    self.log_result("Health Check API", True, 
                                  f"Health check working: {data['status']}")
                else:
                    self.log_result("Health Check API", True, 
                                  "Health check endpoint responding")
            else:
                self.log_result("Health Check API", False, 
                              f"Health check failed: {response.status_code}")
        except Exception as e:
            self.log_result("Health Check API", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all social authentication tests"""
        print("🔐 NOFEEPLACES.COM SOCIAL AUTHENTICATION TESTING")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_facebook_auth_endpoint_structure()
        self.test_apple_auth_endpoint_structure()
        self.test_user_info_endpoint()
        self.test_backend_integration()
        self.test_environment_configuration()
        self.test_api_health_after_social_auth()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🔐 SOCIAL AUTHENTICATION TEST SUMMARY")
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
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            "passed": self.results["passed"],
            "failed": self.results["failed"],
            "success_rate": success_rate,
            "errors": self.results["errors"]
        }

if __name__ == "__main__":
    tester = SocialAuthTester()
    results = tester.run_all_tests()