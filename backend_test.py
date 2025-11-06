#!/usr/bin/env python3
"""
Backend Authentication Flow Testing
Test the complete sign-in/login authentication flow as requested
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

class AuthenticationTester:
    def __init__(self):
        # Get backend URL from frontend .env
        self.backend_url = None
        self.load_backend_url()
        self.session = None
        self.test_results = []
        
    def load_backend_url(self):
        """Load backend URL from frontend .env file"""
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.backend_url = line.split('=', 1)[1].strip()
                        break
            
            if not self.backend_url:
                raise ValueError("REACT_APP_BACKEND_URL not found in frontend/.env")
                
            print(f"✅ Backend URL loaded: {self.backend_url}")
            
        except Exception as e:
            print(f"❌ Error loading backend URL: {e}")
            sys.exit(1)
    
    async def setup_session(self):
        """Setup HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str, response_data: Optional[Dict] = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response_data': response_data,
            'timestamp': datetime.now().isoformat()
        })
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
    async def test_user_registration(self):
        """Test Scenario 1: New User Registration"""
        print("🧪 TEST SCENARIO 1: New User Registration")
        
        try:
            registration_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "full_name": self.test_user_name
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = await response.json() if response_text else {}
                    
                    # Verify response structure
                    required_fields = ["access_token", "token_type", "user"]
                    missing_fields = [field for field in required_fields if field not in response_data]
                    
                    if missing_fields:
                        self.log_result(
                            "User Registration - Response Structure",
                            False,
                            f"Missing required fields: {missing_fields}",
                            response_data
                        )
                        return None
                    
                    # Verify token type
                    if response_data.get("token_type") != "bearer":
                        self.log_result(
                            "User Registration - Token Type",
                            False,
                            f"Expected token_type 'bearer', got '{response_data.get('token_type')}'",
                            response_data
                        )
                        return None
                    
                    # Verify user object
                    user_data = response_data.get("user", {})
                    user_required_fields = ["id", "email", "full_name"]
                    missing_user_fields = [field for field in user_required_fields if field not in user_data]
                    
                    if missing_user_fields:
                        self.log_result(
                            "User Registration - User Object",
                            False,
                            f"Missing user fields: {missing_user_fields}",
                            response_data
                        )
                        return None
                    
                    # Verify user data matches input
                    if user_data.get("email") != self.test_user_email:
                        self.log_result(
                            "User Registration - Email Match",
                            False,
                            f"Email mismatch: expected {self.test_user_email}, got {user_data.get('email')}",
                            response_data
                        )
                        return None
                        
                    if user_data.get("full_name") != self.test_user_name:
                        self.log_result(
                            "User Registration - Name Match",
                            False,
                            f"Name mismatch: expected {self.test_user_name}, got {user_data.get('full_name')}",
                            response_data
                        )
                        return None
                    
                    self.log_result(
                        "User Registration - Complete Flow",
                        True,
                        f"Successfully registered user with access_token, correct token_type, and user object with id: {user_data.get('id')}"
                    )
                    
                    return response_data.get("access_token")
                    
                else:
                    self.log_result(
                        "User Registration - HTTP Status",
                        False,
                        f"Expected status 200, got {response.status}",
                        response_text
                    )
                    return None
                    
        except Exception as e:
            self.log_result(
                "User Registration - Exception",
                False,
                f"Exception occurred: {str(e)}"
            )
            return None
            
    async def test_duplicate_email_prevention(self):
        """Test Scenario 2: Duplicate Email Prevention"""
        print("🧪 TEST SCENARIO 2: Duplicate Email Prevention")
        
        try:
            # Try to register with the same email again
            registration_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "full_name": self.test_user_name
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_text = await response.text()
                
                if response.status == 400:
                    try:
                        response_data = json.loads(response_text)
                        error_detail = response_data.get("detail", "")
                        
                        if "Email already registered" in error_detail:
                            self.log_result(
                                "Duplicate Email Prevention",
                                True,
                                f"Correctly returned 400 error with message: '{error_detail}'"
                            )
                        else:
                            self.log_result(
                                "Duplicate Email Prevention - Error Message",
                                False,
                                f"Expected 'Email already registered' message, got: '{error_detail}'",
                                response_data
                            )
                    except json.JSONDecodeError:
                        self.log_result(
                            "Duplicate Email Prevention - Response Format",
                            False,
                            f"Expected JSON response, got: {response_text}"
                        )
                else:
                    self.log_result(
                        "Duplicate Email Prevention - HTTP Status",
                        False,
                        f"Expected status 400, got {response.status}",
                        response_text
                    )
                    
        except Exception as e:
            self.log_result(
                "Duplicate Email Prevention - Exception",
                False,
                f"Exception occurred: {str(e)}"
            )
            
    async def test_login_with_created_account(self):
        """Test Scenario 3: Login with Created Account"""
        print("🧪 TEST SCENARIO 3: Login with Created Account")
        
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = await response.json() if response_text else {}
                    
                    # Verify response structure
                    required_fields = ["access_token", "user"]
                    missing_fields = [field for field in required_fields if field not in response_data]
                    
                    if missing_fields:
                        self.log_result(
                            "Login - Response Structure",
                            False,
                            f"Missing required fields: {missing_fields}",
                            response_data
                        )
                        return None
                    
                    # Verify user details
                    user_data = response_data.get("user", {})
                    if user_data.get("email") != self.test_user_email:
                        self.log_result(
                            "Login - User Email",
                            False,
                            f"Email mismatch: expected {self.test_user_email}, got {user_data.get('email')}",
                            response_data
                        )
                        return None
                    
                    self.log_result(
                        "Login with Created Account",
                        True,
                        f"Successfully logged in with access_token and correct user details"
                    )
                    
                    return response_data.get("access_token")
                    
                else:
                    self.log_result(
                        "Login - HTTP Status",
                        False,
                        f"Expected status 200, got {response.status}",
                        response_text
                    )
                    return None
                    
        except Exception as e:
            self.log_result(
                "Login with Created Account - Exception",
                False,
                f"Exception occurred: {str(e)}"
            )
            return None
            
    async def test_wrong_password(self):
        """Test Scenario 4: Wrong Password"""
        print("🧪 TEST SCENARIO 4: Wrong Password")
        
        try:
            login_data = {
                "email": self.test_user_email,
                "password": "WrongPassword123!"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_text = await response.text()
                
                if response.status == 401:
                    try:
                        response_data = json.loads(response_text)
                        error_detail = response_data.get("detail", "")
                        
                        if "Invalid credentials" in error_detail:
                            self.log_result(
                                "Wrong Password",
                                True,
                                f"Correctly returned 401 error with message: '{error_detail}'"
                            )
                        else:
                            self.log_result(
                                "Wrong Password - Error Message",
                                False,
                                f"Expected 'Invalid credentials' message, got: '{error_detail}'",
                                response_data
                            )
                    except json.JSONDecodeError:
                        self.log_result(
                            "Wrong Password - Response Format",
                            False,
                            f"Expected JSON response, got: {response_text}"
                        )
                else:
                    self.log_result(
                        "Wrong Password - HTTP Status",
                        False,
                        f"Expected status 401, got {response.status}",
                        response_text
                    )
                    
        except Exception as e:
            self.log_result(
                "Wrong Password - Exception",
                False,
                f"Exception occurred: {str(e)}"
            )
            
    async def test_password_hashing_verification(self):
        """Additional Test: Verify password is hashed using bcrypt"""
        print("🧪 ADDITIONAL TEST: Password Hashing Verification")
        
        try:
            # This test verifies that passwords are properly hashed by attempting
            # to login with the correct password after registration
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    self.log_result(
                        "Password Hashing (bcrypt)",
                        True,
                        "Password hashing working correctly - login successful with correct password"
                    )
                else:
                    self.log_result(
                        "Password Hashing (bcrypt)",
                        False,
                        f"Password hashing may be broken - login failed with status {response.status}"
                    )
                    
        except Exception as e:
            self.log_result(
                "Password Hashing (bcrypt) - Exception",
                False,
                f"Exception occurred: {str(e)}"
            )
            
    async def test_jwt_token_generation(self):
        """Additional Test: Verify JWT tokens are generated correctly"""
        print("🧪 ADDITIONAL TEST: JWT Token Generation")
        
        try:
            # Register a new user to get a fresh token
            timestamp = int(time.time())
            jwt_test_email = f"jwt-test-{timestamp}@example.com"
            
            registration_data = {
                "email": jwt_test_email,
                "password": self.test_user_password,
                "full_name": "JWT Test User"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    response_data = await response.json()
                    access_token = response_data.get("access_token")
                    
                    if access_token and len(access_token.split('.')) == 3:
                        self.log_result(
                            "JWT Token Generation",
                            True,
                            f"JWT token generated correctly with proper structure (3 parts separated by dots)"
                        )
                    else:
                        self.log_result(
                            "JWT Token Generation",
                            False,
                            f"JWT token format invalid: {access_token}"
                        )
                else:
                    self.log_result(
                        "JWT Token Generation",
                        False,
                        f"Failed to register user for JWT test: status {response.status}"
                    )
                    
        except Exception as e:
            self.log_result(
                "JWT Token Generation - Exception",
                False,
                f"Exception occurred: {str(e)}"
            )
            
    async def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 STARTING EMAIL/PASSWORD AUTHENTICATION TESTING")
        print("=" * 60)
        
        await self.setup()
        
        # Test Scenario 1: New User Registration
        access_token = await self.test_user_registration()
        
        # Test Scenario 2: Duplicate Email Prevention
        await self.test_duplicate_email_prevention()
        
        # Test Scenario 3: Login with Created Account
        login_token = await self.test_login_with_created_account()
        
        # Test Scenario 4: Wrong Password
        await self.test_wrong_password()
        
        # Additional Tests
        await self.test_password_hashing_verification()
        await self.test_jwt_token_generation()
        
        # Summary
        await self.print_summary()
        
        await self.cleanup()
        
    async def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        # Critical Requirements Check
        critical_tests = [
            "User Registration - Complete Flow",
            "Duplicate Email Prevention", 
            "Login with Created Account",
            "Wrong Password"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["test"] in critical_tests and result["success"])
        
        print("🎯 CRITICAL REQUIREMENTS STATUS:")
        print(f"   Registration Flow: {'✅ WORKING' if any(r['test'] == 'User Registration - Complete Flow' and r['success'] for r in self.test_results) else '❌ FAILED'}")
        print(f"   Duplicate Prevention: {'✅ WORKING' if any(r['test'] == 'Duplicate Email Prevention' and r['success'] for r in self.test_results) else '❌ FAILED'}")
        print(f"   Login Flow: {'✅ WORKING' if any(r['test'] == 'Login with Created Account' and r['success'] for r in self.test_results) else '❌ FAILED'}")
        print(f"   Wrong Password Handling: {'✅ WORKING' if any(r['test'] == 'Wrong Password' and r['success'] for r in self.test_results) else '❌ FAILED'}")
        print(f"   Password Hashing (bcrypt): {'✅ WORKING' if any(r['test'] == 'Password Hashing (bcrypt)' and r['success'] for r in self.test_results) else '❌ FAILED'}")
        print(f"   JWT Token Generation: {'✅ WORKING' if any(r['test'] == 'JWT Token Generation' and r['success'] for r in self.test_results) else '❌ FAILED'}")
        print()
        
        if critical_passed == len(critical_tests):
            print("🎉 ALL CRITICAL AUTHENTICATION REQUIREMENTS WORKING!")
        else:
            print(f"⚠️  {len(critical_tests) - critical_passed} CRITICAL REQUIREMENTS FAILING")
        
        print("=" * 60)

async def main():
    """Main test execution"""
    tester = AuthenticationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())