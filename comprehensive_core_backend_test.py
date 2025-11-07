#!/usr/bin/env python3
"""
Comprehensive Core Functionality Backend Testing for NoFeePlaces
Testing: Authentication, Contact, Schedule Showing, Borough Filtering
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

class ComprehensiveCoreBackendTester:
    def __init__(self):
        self.backend_url = None
        self.load_backend_url()
        self.session = None
        self.test_results = []
        self.test_user_token = None
        self.test_user_email = None
        
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
    
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, headers: Optional[Dict] = None) -> tuple[int, Dict]:
        """Make HTTP request and return status code and response data"""
        url = f"{self.backend_url}{endpoint}"
        
        request_headers = {'Content-Type': 'application/json'}
        if headers:
            request_headers.update(headers)
        
        try:
            if method.upper() == 'POST':
                async with self.session.post(url, json=data, headers=request_headers) as response:
                    status_code = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = {"error": "Invalid JSON response", "text": await response.text()}
                    return status_code, response_data
            elif method.upper() == 'GET':
                async with self.session.get(url, headers=request_headers) as response:
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
    
    # ==================== AUTHENTICATION TESTS ====================
    
    async def test_email_registration(self, timestamp: str) -> tuple[bool, Dict]:
        """Test email/password registration"""
        print("\n🔍 TEST: Email/Password Registration")
        
        test_email = f"nofeeplaces-test-{timestamp}@example.com"
        test_password = "SecurePass123!"
        test_name = "NoFeePlaces Test User"
        
        registration_data = {
            "email": test_email,
            "password": test_password,
            "full_name": test_name
        }
        
        status_code, response_data = await self.make_request('POST', '/api/auth/register', registration_data)
        
        if status_code == 200:
            required_fields = ['access_token', 'token_type', 'user']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                self.log_test_result(
                    "Email/Password Registration", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    response_data
                )
                return False, {}
            
            user_data = response_data.get('user', {})
            if user_data.get('email') != test_email:
                self.log_test_result(
                    "Email/Password Registration", 
                    False, 
                    f"Email mismatch. Expected: {test_email}, Got: {user_data.get('email')}",
                    response_data
                )
                return False, {}
            
            self.log_test_result(
                "Email/Password Registration", 
                True, 
                f"Successfully registered user {test_email}",
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
                "Email/Password Registration", 
                False, 
                f"Registration failed with status {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False, {}
    
    async def test_email_login(self, email: str, password: str) -> tuple[bool, str]:
        """Test email/password login"""
        print("\n🔍 TEST: Email/Password Login")
        
        login_data = {
            "email": email,
            "password": password
        }
        
        status_code, response_data = await self.make_request('POST', '/api/auth/login', login_data)
        
        if status_code == 200:
            required_fields = ['access_token', 'token_type', 'user']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                self.log_test_result(
                    "Email/Password Login", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    response_data
                )
                return False, ""
            
            self.log_test_result(
                "Email/Password Login", 
                True, 
                f"Successfully logged in user {email}",
                response_data
            )
            
            return True, response_data.get('access_token', '')
            
        else:
            self.log_test_result(
                "Email/Password Login", 
                False, 
                f"Login failed with status {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False, ""
    
    async def test_auth_me(self, token: str) -> bool:
        """Test /auth/me endpoint with JWT token"""
        print("\n🔍 TEST: JWT Token Validation (/auth/me)")
        
        headers = {"Authorization": f"Bearer {token}"}
        status_code, response_data = await self.make_request('GET', '/api/auth/me', headers=headers)
        
        if status_code == 200:
            required_fields = ['id', 'email', 'name']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                self.log_test_result(
                    "JWT Token Validation (/auth/me)", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    response_data
                )
                return False
            
            self.log_test_result(
                "JWT Token Validation (/auth/me)", 
                True, 
                f"Successfully validated JWT token for user {response_data.get('email')}",
                response_data
            )
            return True
            
        else:
            self.log_test_result(
                "JWT Token Validation (/auth/me)", 
                False, 
                f"Token validation failed with status {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    async def test_google_auth_endpoint_structure(self) -> bool:
        """Test Google authentication endpoint structure (without actual Google token)"""
        print("\n🔍 TEST: Google Authentication Endpoint Structure")
        
        # Test with invalid token to verify endpoint exists and validates properly
        test_data = {
            "googleToken": "invalid_test_token_for_structure_validation"
        }
        
        status_code, response_data = await self.make_request('POST', '/api/auth/google', test_data)
        
        # We expect 401 or 400 for invalid token, which means endpoint exists and validates
        if status_code in [400, 401, 500]:
            # Check if error message indicates token validation (not 404)
            detail = response_data.get('detail', '')
            if 'not found' in detail.lower() or '404' in detail:
                self.log_test_result(
                    "Google Authentication Endpoint Structure", 
                    False, 
                    f"Endpoint not found or not properly configured",
                    response_data
                )
                return False
            else:
                self.log_test_result(
                    "Google Authentication Endpoint Structure", 
                    True, 
                    f"Endpoint exists and validates tokens (status {status_code})",
                    response_data
                )
                return True
        elif status_code == 404:
            self.log_test_result(
                "Google Authentication Endpoint Structure", 
                False, 
                f"Google auth endpoint not found (404)",
                response_data
            )
            return False
        else:
            self.log_test_result(
                "Google Authentication Endpoint Structure", 
                False, 
                f"Unexpected status code {status_code}",
                response_data
            )
            return False
    
    # ==================== CONTACT FUNCTIONALITY TESTS ====================
    
    async def test_apartment_contact_email(self) -> bool:
        """Test apartment contact form email endpoint"""
        print("\n🔍 TEST: Apartment Contact Email (/send-contact-email)")
        
        contact_data = {
            "to": "placesfirm@gmail.com",
            "subject": "Inquiry about Studio Apartment in Brooklyn",
            "sender_name": "Sarah Johnson",
            "sender_email": "sarah.johnson@example.com",
            "sender_phone": "+1-555-123-4567",
            "message": "Hi, I'm interested in viewing this apartment. Is it still available? I'm looking to move in next month.",
            "apartment_details": {
                "title": "Studio 1 Bath in Brooklyn",
                "address": "123 Main St, Brooklyn, NY",
                "price": 2500,
                "bedrooms": 0
            }
        }
        
        status_code, response_data = await self.make_request('POST', '/api/send-contact-email', contact_data)
        
        if status_code == 200:
            if response_data.get('success') == True:
                self.log_test_result(
                    "Apartment Contact Email", 
                    True, 
                    f"Contact email sent successfully: {response_data.get('message')}",
                    response_data
                )
                return True
            else:
                self.log_test_result(
                    "Apartment Contact Email", 
                    False, 
                    f"Email sending failed: {response_data.get('message')}",
                    response_data
                )
                return False
        else:
            self.log_test_result(
                "Apartment Contact Email", 
                False, 
                f"Request failed with status {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    async def test_general_contact_form(self) -> bool:
        """Test general contact form endpoint"""
        print("\n🔍 TEST: General Contact Form (/contact)")
        
        contact_data = {
            "name": "Michael Chen",
            "email": "michael.chen@example.com",
            "phone": "+1-555-987-6543",
            "message": "I have a question about your no-fee apartment listings. Do you have any 2-bedroom apartments in Manhattan under $4000?",
            "preferred_contact": "email"
        }
        
        status_code, response_data = await self.make_request('POST', '/api/contact', contact_data)
        
        if status_code == 200:
            if 'contact_id' in response_data:
                self.log_test_result(
                    "General Contact Form", 
                    True, 
                    f"Contact form submitted successfully. Contact ID: {response_data.get('contact_id')}",
                    response_data
                )
                return True
            else:
                self.log_test_result(
                    "General Contact Form", 
                    False, 
                    f"Missing contact_id in response",
                    response_data
                )
                return False
        else:
            self.log_test_result(
                "General Contact Form", 
                False, 
                f"Request failed with status {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    # ==================== SCHEDULE SHOWING TESTS ====================
    
    async def test_schedule_showing(self) -> bool:
        """Test schedule showing endpoint"""
        print("\n🔍 TEST: Schedule Showing (/showings/schedule)")
        
        # Calculate tomorrow's date
        tomorrow = datetime.now() + timedelta(days=1)
        showing_date = tomorrow.strftime('%Y-%m-%d')
        
        showing_data = {
            "apartment_id": "test-apartment-123",
            "apartment_title": "Luxury 2BR in Manhattan",
            "apartment_address": "456 Park Ave, Manhattan, NY 10022",
            "apartment_price": 4500,
            "showing_date": showing_date,
            "showing_time": "3 PM",
            "visitor_name": "Emily Rodriguez",
            "visitor_email": "emily.rodriguez@example.com",
            "visitor_phone": "+1-555-234-5678",
            "special_notes": "I would prefer to see the apartment in the afternoon. Looking forward to it!"
        }
        
        status_code, response_data = await self.make_request('POST', '/api/showings/schedule', showing_data)
        
        if status_code == 200:
            required_fields = ['success', 'message', 'showing_id', 'confirmation_sent']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                self.log_test_result(
                    "Schedule Showing", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    response_data
                )
                return False
            
            if response_data.get('success') == True:
                self.log_test_result(
                    "Schedule Showing", 
                    True, 
                    f"Showing scheduled successfully. ID: {response_data.get('showing_id')}, Email sent: {response_data.get('confirmation_sent')}",
                    response_data
                )
                return True
            else:
                self.log_test_result(
                    "Schedule Showing", 
                    False, 
                    f"Showing scheduling failed: {response_data.get('message')}",
                    response_data
                )
                return False
        else:
            self.log_test_result(
                "Schedule Showing", 
                False, 
                f"Request failed with status {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    async def test_schedule_showing_date_validation(self) -> bool:
        """Test schedule showing date validation (must be at least 24 hours in advance)"""
        print("\n🔍 TEST: Schedule Showing Date Validation")
        
        # Try to schedule for today (should fail)
        today = datetime.now()
        showing_date = today.strftime('%Y-%m-%d')
        
        showing_data = {
            "apartment_id": "test-apartment-456",
            "apartment_title": "Studio in Queens",
            "apartment_address": "789 Queens Blvd, Queens, NY",
            "apartment_price": 2200,
            "showing_date": showing_date,
            "showing_time": "6 PM",
            "visitor_name": "David Kim",
            "visitor_email": "david.kim@example.com",
            "visitor_phone": "+1-555-345-6789",
            "special_notes": ""
        }
        
        status_code, response_data = await self.make_request('POST', '/api/showings/schedule', showing_data)
        
        # Should return 400 for invalid date (less than 24 hours)
        if status_code == 400:
            detail = response_data.get('detail', '')
            if '24 hours' in detail or 'advance' in detail.lower():
                self.log_test_result(
                    "Schedule Showing Date Validation", 
                    True, 
                    f"Correctly rejected showing with insufficient advance notice: {detail}",
                    response_data
                )
                return True
            else:
                self.log_test_result(
                    "Schedule Showing Date Validation", 
                    False, 
                    f"Got 400 but unexpected error message: {detail}",
                    response_data
                )
                return False
        else:
            self.log_test_result(
                "Schedule Showing Date Validation", 
                False, 
                f"Expected 400 status for invalid date, got {status_code}",
                response_data
            )
            return False
    
    # ==================== BOROUGH FILTERING TESTS ====================
    
    async def test_borough_filter_brooklyn(self) -> bool:
        """Test borough filtering for Brooklyn"""
        print("\n🔍 TEST: Borough Filter - Brooklyn")
        
        status_code, response_data = await self.make_request('GET', '/api/apartments?borough=Brooklyn&limit=10')
        
        if status_code == 200:
            apartments = response_data.get('apartments', [])
            total = response_data.get('total', 0)
            
            # Check if all apartments are in Brooklyn
            non_brooklyn = [apt for apt in apartments if apt.get('borough', '').lower() != 'brooklyn']
            
            if non_brooklyn:
                self.log_test_result(
                    "Borough Filter - Brooklyn", 
                    False, 
                    f"Found {len(non_brooklyn)} non-Brooklyn apartments in results",
                    response_data
                )
                return False
            
            self.log_test_result(
                "Borough Filter - Brooklyn", 
                True, 
                f"Brooklyn filter working correctly. Total: {total}, Retrieved: {len(apartments)}",
                response_data
            )
            return True
        else:
            self.log_test_result(
                "Borough Filter - Brooklyn", 
                False, 
                f"Request failed with status {status_code}",
                response_data
            )
            return False
    
    async def test_borough_filter_queens(self) -> bool:
        """Test borough filtering for Queens"""
        print("\n🔍 TEST: Borough Filter - Queens")
        
        status_code, response_data = await self.make_request('GET', '/api/apartments?borough=Queens&limit=10')
        
        if status_code == 200:
            apartments = response_data.get('apartments', [])
            total = response_data.get('total', 0)
            
            # Check if all apartments are in Queens
            non_queens = [apt for apt in apartments if apt.get('borough', '').lower() != 'queens']
            
            if non_queens:
                self.log_test_result(
                    "Borough Filter - Queens", 
                    False, 
                    f"Found {len(non_queens)} non-Queens apartments in results",
                    response_data
                )
                return False
            
            self.log_test_result(
                "Borough Filter - Queens", 
                True, 
                f"Queens filter working correctly. Total: {total}, Retrieved: {len(apartments)}",
                response_data
            )
            return True
        else:
            self.log_test_result(
                "Borough Filter - Queens", 
                False, 
                f"Request failed with status {status_code}",
                response_data
            )
            return False
    
    async def test_borough_filter_manhattan(self) -> bool:
        """Test borough filtering for Manhattan"""
        print("\n🔍 TEST: Borough Filter - Manhattan")
        
        status_code, response_data = await self.make_request('GET', '/api/apartments?borough=Manhattan&limit=10')
        
        if status_code == 200:
            apartments = response_data.get('apartments', [])
            total = response_data.get('total', 0)
            
            # Check if all apartments are in Manhattan
            non_manhattan = [apt for apt in apartments if apt.get('borough', '').lower() != 'manhattan']
            
            if non_manhattan:
                self.log_test_result(
                    "Borough Filter - Manhattan", 
                    False, 
                    f"Found {len(non_manhattan)} non-Manhattan apartments in results",
                    response_data
                )
                return False
            
            self.log_test_result(
                "Borough Filter - Manhattan", 
                True, 
                f"Manhattan filter working correctly. Total: {total}, Retrieved: {len(apartments)}",
                response_data
            )
            return True
        else:
            self.log_test_result(
                "Borough Filter - Manhattan", 
                False, 
                f"Request failed with status {status_code}",
                response_data
            )
            return False
    
    async def test_borough_filter_bronx(self) -> bool:
        """Test borough filtering for Bronx"""
        print("\n🔍 TEST: Borough Filter - Bronx")
        
        status_code, response_data = await self.make_request('GET', '/api/apartments?borough=Bronx&limit=10')
        
        if status_code == 200:
            apartments = response_data.get('apartments', [])
            total = response_data.get('total', 0)
            
            # Check if all apartments are in Bronx
            non_bronx = [apt for apt in apartments if apt.get('borough', '').lower() != 'bronx']
            
            if non_bronx:
                self.log_test_result(
                    "Borough Filter - Bronx", 
                    False, 
                    f"Found {len(non_bronx)} non-Bronx apartments in results",
                    response_data
                )
                return False
            
            self.log_test_result(
                "Borough Filter - Bronx", 
                True, 
                f"Bronx filter working correctly. Total: {total}, Retrieved: {len(apartments)}",
                response_data
            )
            return True
        else:
            self.log_test_result(
                "Borough Filter - Bronx", 
                False, 
                f"Request failed with status {status_code}",
                response_data
            )
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🔍 COMPREHENSIVE CORE FUNCTIONALITY BACKEND TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group results by category
        auth_tests = [r for r in self.test_results if 'auth' in r['test'].lower() or 'registration' in r['test'].lower() or 'login' in r['test'].lower() or 'jwt' in r['test'].lower() or 'google' in r['test'].lower()]
        contact_tests = [r for r in self.test_results if 'contact' in r['test'].lower() or 'email' in r['test'].lower()]
        showing_tests = [r for r in self.test_results if 'showing' in r['test'].lower()]
        borough_tests = [r for r in self.test_results if 'borough' in r['test'].lower()]
        
        print("\n📊 RESULTS BY CATEGORY:")
        print(f"  Authentication: {sum(1 for r in auth_tests if r['success'])}/{len(auth_tests)} passed")
        print(f"  Contact Forms: {sum(1 for r in contact_tests if r['success'])}/{len(contact_tests)} passed")
        print(f"  Schedule Showing: {sum(1 for r in showing_tests if r['success'])}/{len(showing_tests)} passed")
        print(f"  Borough Filtering: {sum(1 for r in borough_tests if r['success'])}/{len(borough_tests)} passed")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n" + "="*80)
        
        return passed_tests, failed_tests
    
    async def run_all_tests(self):
        """Run all comprehensive core functionality tests"""
        print("🚀 Starting Comprehensive Core Functionality Backend Testing")
        print(f"Backend URL: {self.backend_url}")
        print(f"Testing: Authentication, Contact, Schedule Showing, Borough Filtering")
        
        await self.setup_session()
        
        try:
            timestamp = str(int(time.time()))
            
            # ==================== AUTHENTICATION TESTS ====================
            print("\n" + "="*80)
            print("📧 AUTHENTICATION TESTS")
            print("="*80)
            
            # Test 1: Email/Password Registration
            registration_success, user_credentials = await self.test_email_registration(timestamp)
            
            if registration_success:
                self.test_user_email = user_credentials['email']
                self.test_user_token = user_credentials['access_token']
                
                # Test 2: Email/Password Login
                login_success, login_token = await self.test_email_login(
                    user_credentials['email'], 
                    user_credentials['password']
                )
                
                if login_success:
                    # Test 3: JWT Token Validation
                    await self.test_auth_me(login_token)
            
            # Test 4: Google Authentication Endpoint Structure
            await self.test_google_auth_endpoint_structure()
            
            # ==================== CONTACT FUNCTIONALITY TESTS ====================
            print("\n" + "="*80)
            print("📬 CONTACT FUNCTIONALITY TESTS")
            print("="*80)
            
            # Test 5: Apartment Contact Email
            await self.test_apartment_contact_email()
            
            # Test 6: General Contact Form
            await self.test_general_contact_form()
            
            # ==================== SCHEDULE SHOWING TESTS ====================
            print("\n" + "="*80)
            print("📅 SCHEDULE SHOWING TESTS")
            print("="*80)
            
            # Test 7: Schedule Showing
            await self.test_schedule_showing()
            
            # Test 8: Schedule Showing Date Validation
            await self.test_schedule_showing_date_validation()
            
            # ==================== BOROUGH FILTERING TESTS ====================
            print("\n" + "="*80)
            print("🗺️ BOROUGH FILTERING TESTS")
            print("="*80)
            
            # Test 9: Brooklyn Filter
            await self.test_borough_filter_brooklyn()
            
            # Test 10: Queens Filter
            await self.test_borough_filter_queens()
            
            # Test 11: Manhattan Filter
            await self.test_borough_filter_manhattan()
            
            # Test 12: Bronx Filter
            await self.test_borough_filter_bronx()
            
        finally:
            await self.cleanup_session()
        
        # Print summary
        passed, failed = self.print_summary()
        
        return passed, failed

async def main():
    """Main test function"""
    tester = ComprehensiveCoreBackendTester()
    passed, failed = await tester.run_all_tests()
    
    # Exit with appropriate code
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
