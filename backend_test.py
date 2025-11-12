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
    
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> tuple[int, Dict]:
        """Make HTTP request and return status code and response data"""
        url = f"{self.backend_url}{endpoint}"
        
        try:
            if method.upper() == 'POST':
                async with self.session.post(url, json=data) as response:
                    status_code = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = {"error": "Invalid JSON response", "text": await response.text()}
                    return status_code, response_data
            elif method.upper() == 'GET':
                async with self.session.get(url) as response:
                    status_code = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = {"error": "Invalid JSON response", "text": await response.text()}
                    return status_code, response_data
            else:
                return 400, {"error": f"Unsupported method: {method}"}
                
        except Exception as e:
            return 500, {"error": f"Request failed: {str(e)}"}
    
    async def test_user_registration(self, timestamp: str) -> tuple[bool, Dict]:
        """Test 1: Register a new user"""
        print("\n🔍 TEST 1: User Registration")
        
        test_email = f"signin-test-{timestamp}@example.com"
        test_password = "TestPass123!"
        test_name = "Sign In Test User"
        
        registration_data = {
            "email": test_email,
            "password": test_password,
            "full_name": test_name
        }
        
        status_code, response_data = await self.make_request('POST', '/api/auth/register', registration_data)
        
        if status_code == 200:
            # Check response structure
            required_fields = ['access_token', 'token_type', 'user']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                self.log_test_result(
                    "User Registration", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    response_data
                )
                return False, {}
            
            # Check token type
            if response_data.get('token_type') != 'bearer':
                self.log_test_result(
                    "User Registration", 
                    False, 
                    f"Expected token_type 'bearer', got '{response_data.get('token_type')}'",
                    response_data
                )
                return False, {}
            
            # Check user object
            user_data = response_data.get('user', {})
            if user_data.get('email') != test_email:
                self.log_test_result(
                    "User Registration", 
                    False, 
                    f"User email mismatch. Expected: {test_email}, Got: {user_data.get('email')}",
                    response_data
                )
                return False, {}
            
            self.log_test_result(
                "User Registration", 
                True, 
                f"Successfully registered user {test_email} with access token",
                response_data
            )
            
            return True, {
                'email': test_email,
                'password': test_password,
                'full_name': test_name,
                'access_token': response_data.get('access_token'),
                'user_id': user_data.get('id')
            }
            
        else:
            self.log_test_result(
                "User Registration", 
                False, 
                f"Registration failed with status {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False, {}
    
    async def test_user_login_success(self, user_credentials: Dict) -> bool:
        """Test 2: Login with correct credentials"""
        print("\n🔍 TEST 2: User Login (Correct Credentials)")
        
        login_data = {
            "email": user_credentials['email'],
            "password": user_credentials['password']
        }
        
        status_code, response_data = await self.make_request('POST', '/api/auth/login', login_data)
        
        if status_code == 200:
            # Check response structure
            required_fields = ['access_token', 'token_type', 'user']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                self.log_test_result(
                    "User Login (Success)", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    response_data
                )
                return False
            
            # Check token type
            if response_data.get('token_type') != 'bearer':
                self.log_test_result(
                    "User Login (Success)", 
                    False, 
                    f"Expected token_type 'bearer', got '{response_data.get('token_type')}'",
                    response_data
                )
                return False
            
            # Check user object
            user_data = response_data.get('user', {})
            if user_data.get('email') != user_credentials['email']:
                self.log_test_result(
                    "User Login (Success)", 
                    False, 
                    f"User email mismatch. Expected: {user_credentials['email']}, Got: {user_data.get('email')}",
                    response_data
                )
                return False
            
            self.log_test_result(
                "User Login (Success)", 
                True, 
                f"Successfully logged in user {user_credentials['email']} with access token",
                response_data
            )
            return True
            
        else:
            self.log_test_result(
                "User Login (Success)", 
                False, 
                f"Login failed with status {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    async def test_user_login_wrong_password(self, user_credentials: Dict) -> bool:
        """Test 3: Login with wrong password"""
        print("\n🔍 TEST 3: User Login (Wrong Password)")
        
        login_data = {
            "email": user_credentials['email'],
            "password": "WrongPassword123!"
        }
        
        status_code, response_data = await self.make_request('POST', '/api/auth/login', login_data)
        
        if status_code == 401:
            expected_detail = "Invalid credentials"
            actual_detail = response_data.get('detail', '')
            
            if expected_detail in actual_detail:
                self.log_test_result(
                    "User Login (Wrong Password)", 
                    True, 
                    f"Correctly rejected login with wrong password (401: {actual_detail})",
                    response_data
                )
                return True
            else:
                self.log_test_result(
                    "User Login (Wrong Password)", 
                    False, 
                    f"Got 401 but unexpected error message: {actual_detail}",
                    response_data
                )
                return False
        else:
            self.log_test_result(
                "User Login (Wrong Password)", 
                False, 
                f"Expected 401 status, got {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    async def test_user_login_nonexistent_user(self) -> bool:
        """Test 4: Login with non-existent user"""
        print("\n🔍 TEST 4: User Login (Non-existent User)")
        
        login_data = {
            "email": "nonexistent-user@example.com",
            "password": "SomePassword123!"
        }
        
        status_code, response_data = await self.make_request('POST', '/api/auth/login', login_data)
        
        if status_code == 401:
            expected_detail = "Invalid credentials"
            actual_detail = response_data.get('detail', '')
            
            if expected_detail in actual_detail:
                self.log_test_result(
                    "User Login (Non-existent User)", 
                    True, 
                    f"Correctly rejected login for non-existent user (401: {actual_detail})",
                    response_data
                )
                return True
            else:
                self.log_test_result(
                    "User Login (Non-existent User)", 
                    False, 
                    f"Got 401 but unexpected error message: {actual_detail}",
                    response_data
                )
                return False
        else:
            self.log_test_result(
                "User Login (Non-existent User)", 
                False, 
                f"Expected 401 status, got {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    async def test_jwt_validation_valid_token(self, user_credentials: Dict) -> bool:
        """Test 5: JWT Token Validation with valid token"""
        print("\n🔍 TEST 5: JWT Token Validation (Valid Token)")
        
        # First login to get a fresh token
        login_data = {
            "email": user_credentials['email'],
            "password": user_credentials['password']
        }
        
        status_code, response_data = await self.make_request('POST', '/api/auth/login', login_data)
        
        if status_code != 200:
            self.log_test_result(
                "JWT Token Validation (Valid Token)", 
                False, 
                f"Failed to get token for validation test. Login status: {status_code}",
                response_data
            )
            return False
        
        access_token = response_data.get('access_token')
        if not access_token:
            self.log_test_result(
                "JWT Token Validation (Valid Token)", 
                False, 
                "No access token received from login",
                response_data
            )
            return False
        
        # Test /api/auth/me with valid token
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            url = f"{self.backend_url}/api/auth/me"
            async with self.session.get(url, headers=headers) as response:
                status_code = response.status
                try:
                    response_data = await response.json()
                except:
                    response_data = {"error": "Invalid JSON response", "text": await response.text()}
        except Exception as e:
            self.log_test_result(
                "JWT Token Validation (Valid Token)", 
                False, 
                f"Request failed: {str(e)}",
                {}
            )
            return False
        
        if status_code == 200:
            # Check response structure
            required_fields = ['id', 'email']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                self.log_test_result(
                    "JWT Token Validation (Valid Token)", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    response_data
                )
                return False
            
            # Check user data matches
            if response_data.get('email') != user_credentials['email']:
                self.log_test_result(
                    "JWT Token Validation (Valid Token)", 
                    False, 
                    f"User email mismatch. Expected: {user_credentials['email']}, Got: {response_data.get('email')}",
                    response_data
                )
                return False
            
            self.log_test_result(
                "JWT Token Validation (Valid Token)", 
                True, 
                f"Successfully validated JWT token and retrieved user data for {user_credentials['email']}",
                response_data
            )
            return True
            
        else:
            self.log_test_result(
                "JWT Token Validation (Valid Token)", 
                False, 
                f"JWT validation failed with status {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    async def test_jwt_validation_invalid_token(self) -> bool:
        """Test 6: JWT Token Validation with invalid token"""
        print("\n🔍 TEST 6: JWT Token Validation (Invalid Token)")
        
        # Test /api/auth/me with invalid token
        headers = {'Authorization': 'Bearer invalid_token_12345'}
        
        try:
            url = f"{self.backend_url}/api/auth/me"
            async with self.session.get(url, headers=headers) as response:
                status_code = response.status
                try:
                    response_data = await response.json()
                except:
                    response_data = {"error": "Invalid JSON response", "text": await response.text()}
        except Exception as e:
            self.log_test_result(
                "JWT Token Validation (Invalid Token)", 
                False, 
                f"Request failed: {str(e)}",
                {}
            )
            return False
        
        if status_code == 401:
            expected_detail = "Invalid token"
            actual_detail = response_data.get('detail', '')
            
            if expected_detail in actual_detail or "token" in actual_detail.lower():
                self.log_test_result(
                    "JWT Token Validation (Invalid Token)", 
                    True, 
                    f"Correctly rejected invalid token (401: {actual_detail})",
                    response_data
                )
                return True
            else:
                self.log_test_result(
                    "JWT Token Validation (Invalid Token)", 
                    False, 
                    f"Got 401 but unexpected error message: {actual_detail}",
                    response_data
                )
                return False
        else:
            self.log_test_result(
                "JWT Token Validation (Invalid Token)", 
                False, 
                f"Expected 401 status, got {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    async def test_jwt_validation_no_token(self) -> bool:
        """Test 7: JWT Token Validation with no token"""
        print("\n🔍 TEST 7: JWT Token Validation (No Token)")
        
        # Test /api/auth/me without Authorization header
        try:
            url = f"{self.backend_url}/api/auth/me"
            async with self.session.get(url) as response:
                status_code = response.status
                try:
                    response_data = await response.json()
                except:
                    response_data = {"error": "Invalid JSON response", "text": await response.text()}
        except Exception as e:
            self.log_test_result(
                "JWT Token Validation (No Token)", 
                False, 
                f"Request failed: {str(e)}",
                {}
            )
            return False
        
        if status_code == 401:
            expected_detail = "Missing or invalid authorization header"
            actual_detail = response_data.get('detail', '')
            
            if "authorization" in actual_detail.lower() or "missing" in actual_detail.lower():
                self.log_test_result(
                    "JWT Token Validation (No Token)", 
                    True, 
                    f"Correctly rejected request without token (401: {actual_detail})",
                    response_data
                )
                return True
            else:
                self.log_test_result(
                    "JWT Token Validation (No Token)", 
                    False, 
                    f"Got 401 but unexpected error message: {actual_detail}",
                    response_data
                )
                return False
        else:
            self.log_test_result(
                "JWT Token Validation (No Token)", 
                False, 
                f"Expected 401 status, got {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    async def test_duplicate_registration(self, user_credentials: Dict) -> bool:
        """Test 8: Try to register with existing email"""
        print("\n🔍 TEST 8: Duplicate Registration Prevention")
        
        registration_data = {
            "email": user_credentials['email'],
            "password": "AnotherPassword123!",
            "full_name": "Another User"
        }
        
        status_code, response_data = await self.make_request('POST', '/api/auth/register', registration_data)
        
        if status_code == 400:
            expected_detail = "Email already registered"
            actual_detail = response_data.get('detail', '')
            
            if expected_detail in actual_detail:
                self.log_test_result(
                    "Duplicate Registration Prevention", 
                    True, 
                    f"Correctly prevented duplicate registration (400: {actual_detail})",
                    response_data
                )
                return True
            else:
                self.log_test_result(
                    "Duplicate Registration Prevention", 
                    False, 
                    f"Got 400 but unexpected error message: {actual_detail}",
                    response_data
                )
                return False
        else:
            self.log_test_result(
                "Duplicate Registration Prevention", 
                False, 
                f"Expected 400 status, got {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🔍 AUTHENTICATION FLOW TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n" + "="*80)
        
        return passed_tests, failed_tests
    
    async def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting Authentication Flow Testing")
        print(f"Backend URL: {self.backend_url}")
        
        await self.setup_session()
        
        try:
            # Generate unique timestamp for test user
            timestamp = str(int(time.time()))
            
            # Test 1: Register new user
            registration_success, user_credentials = await self.test_user_registration(timestamp)
            
            if not registration_success:
                print("❌ Registration failed - cannot proceed with login tests")
                return
            
            # Test 2: Login with correct credentials
            await self.test_user_login_success(user_credentials)
            
            # Test 3: Login with wrong password
            await self.test_user_login_wrong_password(user_credentials)
            
            # Test 4: Login with non-existent user
            await self.test_user_login_nonexistent_user()
            
            # Test 5: JWT Token Validation (Valid Token)
            await self.test_jwt_validation_valid_token(user_credentials)
            
            # Test 6: JWT Token Validation (Invalid Token)
            await self.test_jwt_validation_invalid_token()
            
            # Test 7: JWT Token Validation (No Token)
            await self.test_jwt_validation_no_token()
            
            # Test 8: Try duplicate registration
            await self.test_duplicate_registration(user_credentials)
            
        finally:
            await self.cleanup_session()
        
        # Print summary
        passed, failed = self.print_summary()
        
        return passed, failed

async def main():
    """Main test function"""
    tester = AuthenticationTester()
    passed, failed = await tester.run_all_tests()
    
    # Exit with appropriate code
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())