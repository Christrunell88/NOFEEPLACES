#!/usr/bin/env python3
"""
Share Listing Email Testing with Gmail App Password
Testing URL: https://login-rebuild.preview.emergentagent.com
Focus: Verify Share Listing emails are sent successfully with Gmail App Password
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

class ShareListingEmailTester:
    def __init__(self, base_url: str = "https://login-rebuild.preview.emergentagent.com"):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.auth_token = None
        self.test_results = []
        
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
        url = f"{self.base_url}{endpoint}"
        
        # Merge headers
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
    
    async def get_apartment_id(self) -> Optional[str]:
        """Get an apartment ID for testing"""
        print("\n🔍 Getting apartment ID for testing...")
        
        status_code, response_data = await self.make_request('GET', '/api/apartments?limit=1')
        
        if status_code == 200 and 'apartments' in response_data:
            apartments = response_data['apartments']
            if apartments:
                apartment_id = apartments[0]['id']
                apartment_title = apartments[0].get('title', 'Test Apartment')
                print(f"✅ Found apartment ID: {apartment_id} ({apartment_title})")
                return apartment_id
        
        print(f"❌ Failed to get apartment ID. Status: {status_code}, Response: {response_data}")
        return None
    
    async def authenticate_user(self) -> Optional[str]:
        """Authenticate user and return access token"""
        print("\n🔍 Authenticating user for authenticated share test...")
        
        # Try to login with known credentials
        login_data = {
            "email": "chris.trunell@gmail.com",
            "password": "Onetimeround247"
        }
        
        status_code, response_data = await self.make_request('POST', '/api/auth/login', login_data)
        
        if status_code == 200 and 'access_token' in response_data:
            access_token = response_data['access_token']
            print(f"✅ Successfully authenticated user")
            return access_token
        
        print(f"❌ Failed to authenticate user. Status: {status_code}, Response: {response_data}")
        return None
    
    async def test_basic_share_listing(self, apartment_id: str) -> bool:
        """Test 1: Basic Share Listing Test"""
        print("\n🔍 TEST 1: Basic Share Listing Test")
        
        share_data = {
            "recipient_email": "final-test@example.com"
        }
        
        status_code, response_data = await self.make_request(
            'POST', 
            f'/api/apartments/{apartment_id}/share', 
            share_data
        )
        
        if status_code == 200:
            # Check for success indicators
            success_indicators = ['successfully', 'success', 'shared']
            response_text = str(response_data).lower()
            
            if any(indicator in response_text for indicator in success_indicators):
                self.log_test_result(
                    "Basic Share Listing", 
                    True, 
                    f"Successfully shared listing (HTTP 200) - Response: {response_data.get('message', 'Success')}",
                    response_data
                )
                return True
            else:
                self.log_test_result(
                    "Basic Share Listing", 
                    False, 
                    f"Got HTTP 200 but no success message in response: {response_data}",
                    response_data
                )
                return False
        else:
            self.log_test_result(
                "Basic Share Listing", 
                False, 
                f"Share request failed with status {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    async def test_authenticated_share_listing(self, apartment_id: str, access_token: str) -> bool:
        """Test 2: Authenticated Share Test"""
        print("\n🔍 TEST 2: Authenticated Share Test")
        
        share_data = {
            "recipient_email": "authenticated-final-test@example.com"
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        status_code, response_data = await self.make_request(
            'POST', 
            f'/api/apartments/{apartment_id}/share', 
            share_data,
            headers
        )
        
        if status_code == 200:
            # Check for success indicators
            success_indicators = ['successfully', 'success', 'shared']
            response_text = str(response_data).lower()
            
            if any(indicator in response_text for indicator in success_indicators):
                self.log_test_result(
                    "Authenticated Share Test", 
                    True, 
                    f"Successfully shared listing with authentication (HTTP 200) - Response: {response_data.get('message', 'Success')}",
                    response_data
                )
                return True
            else:
                self.log_test_result(
                    "Authenticated Share Test", 
                    False, 
                    f"Got HTTP 200 but no success message in response: {response_data}",
                    response_data
                )
                return False
        else:
            self.log_test_result(
                "Authenticated Share Test", 
                False, 
                f"Authenticated share request failed with status {status_code}: {response_data.get('detail', 'Unknown error')}",
                response_data
            )
            return False
    
    async def test_multiple_rapid_shares(self, apartment_id: str) -> bool:
        """Test 3: Multiple Rapid Shares"""
        print("\n🔍 TEST 3: Multiple Rapid Shares")
        
        # Create multiple share requests concurrently
        tasks = []
        for i in range(1, 4):  # 3 concurrent requests
            share_data = {
                "recipient_email": f"bulk-test-{i}@example.com"
            }
            task = self.make_request('POST', f'/api/apartments/{apartment_id}/share', share_data)
            tasks.append((i, task))
        
        # Execute all requests concurrently
        results = []
        for i, task in tasks:
            try:
                status_code, response_data = await task
                results.append((i, status_code, response_data))
            except Exception as e:
                results.append((i, 500, {"error": str(e)}))
        
        # Analyze results
        successful_requests = 0
        failed_requests = 0
        
        for i, status_code, response_data in results:
            if status_code == 200:
                success_indicators = ['successfully', 'success', 'shared']
                response_text = str(response_data).lower()
                if any(indicator in response_text for indicator in success_indicators):
                    successful_requests += 1
                    print(f"  ✅ Request {i}: SUCCESS - {response_data.get('message', 'Success')}")
                else:
                    failed_requests += 1
                    print(f"  ❌ Request {i}: HTTP 200 but no success message - {response_data}")
            else:
                failed_requests += 1
                print(f"  ❌ Request {i}: FAILED (HTTP {status_code}) - {response_data.get('detail', 'Unknown error')}")
        
        if successful_requests == 3:
            self.log_test_result(
                "Multiple Rapid Shares", 
                True, 
                f"All 3 concurrent share requests succeeded without SMTP connection issues",
                {"successful": successful_requests, "failed": failed_requests}
            )
            return True
        elif successful_requests > 0:
            self.log_test_result(
                "Multiple Rapid Shares", 
                False, 
                f"Only {successful_requests}/3 requests succeeded - possible SMTP connection issues",
                {"successful": successful_requests, "failed": failed_requests}
            )
            return False
        else:
            self.log_test_result(
                "Multiple Rapid Shares", 
                False, 
                f"All 3 requests failed - SMTP connection issues likely",
                {"successful": successful_requests, "failed": failed_requests}
            )
            return False
    
    async def test_invalid_email_format(self, apartment_id: str) -> bool:
        """Test 4: Invalid Email Format"""
        print("\n🔍 TEST 4: Invalid Email Format")
        
        share_data = {
            "recipient_email": "invalid-email-format"
        }
        
        status_code, response_data = await self.make_request(
            'POST', 
            f'/api/apartments/{apartment_id}/share', 
            share_data
        )
        
        if status_code == 422:  # Validation error expected
            self.log_test_result(
                "Invalid Email Format", 
                True, 
                f"Correctly rejected invalid email format (HTTP 422): {response_data.get('detail', 'Validation error')}",
                response_data
            )
            return True
        else:
            self.log_test_result(
                "Invalid Email Format", 
                False, 
                f"Expected HTTP 422 for invalid email, got {status_code}: {response_data}",
                response_data
            )
            return False
    
    async def test_nonexistent_apartment(self) -> bool:
        """Test 5: Share Non-existent Apartment"""
        print("\n🔍 TEST 5: Share Non-existent Apartment")
        
        fake_apartment_id = "nonexistent-apartment-id-12345"
        share_data = {
            "recipient_email": "test@example.com"
        }
        
        status_code, response_data = await self.make_request(
            'POST', 
            f'/api/apartments/{fake_apartment_id}/share', 
            share_data
        )
        
        if status_code == 404:  # Not found expected
            self.log_test_result(
                "Share Non-existent Apartment", 
                True, 
                f"Correctly returned 404 for non-existent apartment: {response_data.get('detail', 'Not found')}",
                response_data
            )
            return True
        else:
            self.log_test_result(
                "Share Non-existent Apartment", 
                False, 
                f"Expected HTTP 404 for non-existent apartment, got {status_code}: {response_data}",
                response_data
            )
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("📧 SHARE LISTING EMAIL TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📧 EMAIL CONFIGURATION STATUS:")
        print(f"Backend URL: {self.base_url}")
        print(f"Gmail App Password: jssnmrgqlbqefgsh (configured)")
        print(f"SMTP Host: smtp.gmail.com:587")
        print(f"Email User: placesfirm@gmail.com")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n" + "="*80)
        
        return passed_tests, failed_tests
    
    async def run_all_tests(self):
        """Run all share listing email tests"""
        print("🚀 Starting Share Listing Email Testing")
        print(f"Backend URL: {self.base_url}")
        print("📧 Testing Gmail App Password: jssnmrgqlbqefgsh")
        
        await self.setup_session()
        
        try:
            # Get apartment ID for testing
            apartment_id = await self.get_apartment_id()
            if not apartment_id:
                print("❌ Cannot proceed without apartment ID")
                return 0, 1
            
            # Test 1: Basic Share Listing Test
            await self.test_basic_share_listing(apartment_id)
            
            # Test 2: Authenticated Share Test
            access_token = await self.authenticate_user()
            if access_token:
                await self.test_authenticated_share_listing(apartment_id, access_token)
            else:
                self.log_test_result(
                    "Authenticated Share Test", 
                    False, 
                    "Could not authenticate user - skipping authenticated share test",
                    {}
                )
            
            # Test 3: Multiple Rapid Shares
            await self.test_multiple_rapid_shares(apartment_id)
            
            # Test 4: Invalid Email Format
            await self.test_invalid_email_format(apartment_id)
            
            # Test 5: Share Non-existent Apartment
            await self.test_nonexistent_apartment()
            
        finally:
            await self.cleanup_session()
        
        # Print summary
        passed, failed = self.print_summary()
        
        return passed, failed

async def main():
    """Main test function"""
    tester = ShareListingEmailTester()
    passed, failed = await tester.run_all_tests()
    
    # Exit with appropriate code
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())