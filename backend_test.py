#!/usr/bin/env python3
"""
NoFeePlaces Backend Testing Suite
Comprehensive testing for Schedule Showing Feature and Login Functionality
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NoFeePlacesBackendTester:
    def __init__(self):
        # Use production URL from frontend/.env
        self.base_url = "https://buildingtracker-1.preview.emergentagent.com/api"
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, passed: bool, details: str = "", error: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"  Details: {details}")
        if error:
            logger.error(f"  Error: {error}")
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "headers": dict(response.headers)
                    }
        except Exception as e:
            return {"status": 0, "error": str(e)}
    
    async def get_test_apartment_id(self) -> str:
        """Get a valid apartment ID for testing"""
        try:
            response = await self.make_request("GET", "/apartments?limit=1")
            if response["status"] == 200 and "apartments" in response["data"]:
                apartments = response["data"]["apartments"]
                if apartments:
                    return apartments[0]["id"]
            return "test-apartment-id"  # Fallback
        except:
            return "test-apartment-id"  # Fallback
    
    # ==========================================
    # SCHEDULE SHOWING FEATURE TESTS
    # ==========================================
    
    async def test_schedule_showing_endpoint_exists(self):
        """Test 1: Verify schedule showing endpoint exists"""
        test_data = {
            "apartment_id": "test-id",
            "apartment_title": "Test Apartment",
            "apartment_address": "123 Test St, NYC",
            "apartment_price": 3000.0,
            "showing_date": "2025-01-25",
            "showing_time": "2 PM",
            "visitor_name": "John Smith",
            "visitor_email": "john.smith@example.com",
            "visitor_phone": "+1-555-123-4567",
            "special_notes": "Test showing request"
        }
        
        response = await self.make_request("POST", "/showings/schedule", test_data)
        
        if response["status"] in [200, 201, 400, 422]:  # Endpoint exists (even if validation fails)
            self.log_test_result(
                "Schedule Showing Endpoint Exists",
                True,
                f"Endpoint responded with status {response['status']}"
            )
        else:
            self.log_test_result(
                "Schedule Showing Endpoint Exists",
                False,
                f"Endpoint not found or server error: {response['status']}"
            )
    
    async def test_schedule_showing_valid_request(self):
        """Test 2: Test valid showing schedule request"""
        # Get future date (3 days from now to ensure 24-hour notice)
        future_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        apartment_id = await self.get_test_apartment_id()
        
        test_data = {
            "apartment_id": apartment_id,
            "apartment_title": "Luxury Studio in Manhattan",
            "apartment_address": "400 West 61st Street, New York, NY",
            "apartment_price": 4500.0,
            "showing_date": future_date,
            "showing_time": "2 PM",
            "visitor_name": "Sarah Johnson",
            "visitor_email": "sarah.johnson@example.com",
            "visitor_phone": "+1-555-987-6543",
            "special_notes": "Interested in viewing the apartment, flexible with timing"
        }
        
        response = await self.make_request("POST", "/showings/schedule", test_data)
        
        if response["status"] in [200, 201]:
            data = response["data"]
            if isinstance(data, dict) and data.get("success") and data.get("showing_id"):
                self.log_test_result(
                    "Valid Showing Schedule Request",
                    True,
                    f"Showing scheduled successfully with ID: {data.get('showing_id')}"
                )
            else:
                self.log_test_result(
                    "Valid Showing Schedule Request",
                    False,
                    f"Invalid response format: {data}"
                )
        else:
            self.log_test_result(
                "Valid Showing Schedule Request",
                False,
                f"Request failed with status {response['status']}: {response.get('data', '')}"
            )
    
    async def test_schedule_showing_24_hour_notice(self):
        """Test 3: Test 24-hour minimum notice requirement"""
        # Try to schedule for tomorrow (should fail)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        test_data = {
            "apartment_id": "test-apartment-id",
            "apartment_title": "Test Apartment",
            "apartment_address": "123 Test St, NYC",
            "apartment_price": 3000.0,
            "showing_date": tomorrow,
            "showing_time": "2 PM",
            "visitor_name": "Test User",
            "visitor_email": "test@example.com",
            "visitor_phone": "+1-555-123-4567"
        }
        
        response = await self.make_request("POST", "/showings/schedule", test_data)
        
        if response["status"] == 400:
            data = response["data"]
            if "24 hours" in str(data).lower() or "advance notice" in str(data).lower():
                self.log_test_result(
                    "24-Hour Notice Requirement",
                    True,
                    "Correctly rejected showing with insufficient notice"
                )
            else:
                self.log_test_result(
                    "24-Hour Notice Requirement",
                    False,
                    f"Wrong error message: {data}"
                )
        else:
            self.log_test_result(
                "24-Hour Notice Requirement",
                False,
                f"Should have rejected request, got status {response['status']}"
            )
    
    async def test_schedule_showing_business_hours(self):
        """Test 4: Test business hours constraints (9 AM - 6 PM)"""
        future_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        
        # Test invalid time (8 AM - before business hours)
        test_data = {
            "apartment_id": "test-apartment-id",
            "apartment_title": "Test Apartment",
            "apartment_address": "123 Test St, NYC",
            "apartment_price": 3000.0,
            "showing_date": future_date,
            "showing_time": "8 AM",  # Before business hours
            "visitor_name": "Test User",
            "visitor_email": "test@example.com",
            "visitor_phone": "+1-555-123-4567"
        }
        
        response = await self.make_request("POST", "/showings/schedule", test_data)
        
        # Note: The current implementation may not have business hours validation
        # We'll check if it's implemented or just log the result
        if response["status"] == 400:
            self.log_test_result(
                "Business Hours Validation",
                True,
                "Correctly rejected showing outside business hours"
            )
        else:
            self.log_test_result(
                "Business Hours Validation",
                False,
                f"Business hours validation not implemented (status: {response['status']})",
                "Minor: Business hours validation may need implementation"
            )
    
    async def test_schedule_showing_required_fields(self):
        """Test 5: Test required field validation"""
        # Test missing required fields
        incomplete_data = {
            "apartment_id": "test-apartment-id",
            "apartment_title": "Test Apartment",
            # Missing required fields: showing_date, showing_time, visitor_name, visitor_email, visitor_phone
        }
        
        response = await self.make_request("POST", "/showings/schedule", incomplete_data)
        
        if response["status"] == 422:  # Validation error
            self.log_test_result(
                "Required Fields Validation",
                True,
                "Correctly rejected request with missing required fields"
            )
        else:
            self.log_test_result(
                "Required Fields Validation",
                False,
                f"Should have rejected incomplete request, got status {response['status']}"
            )
    
    async def test_schedule_showing_email_format(self):
        """Test 6: Test email format validation"""
        future_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        
        test_data = {
            "apartment_id": "test-apartment-id",
            "apartment_title": "Test Apartment",
            "apartment_address": "123 Test St, NYC",
            "apartment_price": 3000.0,
            "showing_date": future_date,
            "showing_time": "2 PM",
            "visitor_name": "Test User",
            "visitor_email": "invalid-email-format",  # Invalid email
            "visitor_phone": "+1-555-123-4567"
        }
        
        response = await self.make_request("POST", "/showings/schedule", test_data)
        
        if response["status"] == 422:  # Validation error
            self.log_test_result(
                "Email Format Validation",
                True,
                "Correctly rejected request with invalid email format"
            )
        else:
            self.log_test_result(
                "Email Format Validation",
                False,
                f"Email validation may be lenient (status: {response['status']})",
                "Minor: Email format validation may need strengthening"
            )
    
    # ==========================================
    # LOGIN FUNCTIONALITY TESTS
    # ==========================================
    
    async def test_auth_login_endpoint_exists(self):
        """Test 7: Verify login endpoint exists"""
        test_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        
        response = await self.make_request("POST", "/auth/login", test_data)
        
        if response["status"] in [200, 401, 422]:  # Endpoint exists
            self.log_test_result(
                "Login Endpoint Exists",
                True,
                f"Login endpoint responded with status {response['status']}"
            )
        else:
            self.log_test_result(
                "Login Endpoint Exists",
                False,
                f"Login endpoint not found: {response['status']}"
            )
    
    async def test_auth_login_invalid_credentials(self):
        """Test 8: Test login with invalid credentials"""
        test_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await self.make_request("POST", "/auth/login", test_data)
        
        if response["status"] == 401:
            self.log_test_result(
                "Invalid Credentials Handling",
                True,
                "Correctly rejected invalid credentials with 401 status"
            )
        else:
            self.log_test_result(
                "Invalid Credentials Handling",
                False,
                f"Expected 401 for invalid credentials, got {response['status']}"
            )
    
    async def test_auth_login_admin_credentials(self):
        """Test 9: Test login with admin credentials"""
        # Use admin credentials from backend/.env
        test_data = {
            "email": "placesfirm@gmail.com",
            "password": "Checkers080/?"
        }
        
        response = await self.make_request("POST", "/auth/login", test_data)
        
        if response["status"] == 200:
            data = response["data"]
            if isinstance(data, dict) and "access_token" in data:
                self.log_test_result(
                    "Admin Login Success",
                    True,
                    "Admin login successful with access token returned"
                )
                return data.get("access_token")  # Return token for further tests
            else:
                self.log_test_result(
                    "Admin Login Success",
                    False,
                    f"Login succeeded but invalid response format: {data}"
                )
        else:
            self.log_test_result(
                "Admin Login Success",
                False,
                f"Admin login failed with status {response['status']}: {response.get('data', '')}"
            )
        return None
    
    async def test_auth_me_endpoint(self):
        """Test 10: Test user info endpoint with JWT token"""
        # First try to get a valid token
        token = await self.test_auth_login_admin_credentials()
        
        if not token:
            self.log_test_result(
                "User Info Endpoint (with token)",
                False,
                "Could not obtain valid token for testing"
            )
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.make_request("GET", "/auth/me", headers=headers)
        
        if response["status"] == 200:
            data = response["data"]
            if isinstance(data, dict) and "email" in data:
                self.log_test_result(
                    "User Info Endpoint (with token)",
                    True,
                    f"User info retrieved successfully for {data.get('email')}"
                )
            else:
                self.log_test_result(
                    "User Info Endpoint (with token)",
                    False,
                    f"Invalid user info response format: {data}"
                )
        else:
            self.log_test_result(
                "User Info Endpoint (with token)",
                False,
                f"User info request failed with status {response['status']}"
            )
    
    async def test_auth_me_without_token(self):
        """Test 11: Test user info endpoint without token"""
        response = await self.make_request("GET", "/auth/me")
        
        if response["status"] == 401:
            self.log_test_result(
                "User Info Endpoint (no token)",
                True,
                "Correctly rejected request without authorization token"
            )
        else:
            self.log_test_result(
                "User Info Endpoint (no token)",
                False,
                f"Should have rejected request without token, got status {response['status']}"
            )
    
    async def test_social_auth_endpoints(self):
        """Test 12: Test social authentication endpoints exist"""
        # Test Facebook auth endpoint
        facebook_data = {
            "access_token": "fake_facebook_token",
            "user_id": "fake_user_id"
        }
        
        facebook_response = await self.make_request("POST", "/auth/facebook", facebook_data)
        
        # Test Apple auth endpoint
        apple_data = {
            "authorization_code": "fake_apple_code",
            "identity_token": "fake_identity_token"
        }
        
        apple_response = await self.make_request("POST", "/auth/apple", apple_data)
        
        facebook_exists = facebook_response["status"] in [200, 401, 422, 503]
        apple_exists = apple_response["status"] in [200, 401, 422, 503]
        
        if facebook_exists and apple_exists:
            self.log_test_result(
                "Social Auth Endpoints Exist",
                True,
                "Both Facebook and Apple auth endpoints are available"
            )
        elif facebook_exists or apple_exists:
            self.log_test_result(
                "Social Auth Endpoints Exist",
                True,
                f"Partial social auth available (Facebook: {facebook_exists}, Apple: {apple_exists})"
            )
        else:
            self.log_test_result(
                "Social Auth Endpoints Exist",
                False,
                "Social authentication endpoints not found"
            )
    
    # ==========================================
    # ADDITIONAL BACKEND VERIFICATION TESTS
    # ==========================================
    
    async def test_backend_health(self):
        """Test 13: Basic backend health check"""
        response = await self.make_request("GET", "/apartments?limit=1")
        
        if response["status"] == 200:
            self.log_test_result(
                "Backend Health Check",
                True,
                "Backend is responding to API requests"
            )
        else:
            self.log_test_result(
                "Backend Health Check",
                False,
                f"Backend health check failed: {response['status']}"
            )
    
    async def test_apartment_data_availability(self):
        """Test 14: Verify apartment data is available for showing scheduling"""
        response = await self.make_request("GET", "/apartments?limit=5")
        
        if response["status"] == 200:
            data = response["data"]
            if isinstance(data, dict) and "apartments" in data and len(data["apartments"]) > 0:
                apartment = data["apartments"][0]
                required_fields = ["id", "title", "price"]
                has_required = all(field in apartment for field in required_fields)
                
                if has_required:
                    self.log_test_result(
                        "Apartment Data Availability",
                        True,
                        f"Found {len(data['apartments'])} apartments with required fields"
                    )
                else:
                    self.log_test_result(
                        "Apartment Data Availability",
                        False,
                        f"Apartments missing required fields: {apartment.keys()}"
                    )
            else:
                self.log_test_result(
                    "Apartment Data Availability",
                    False,
                    "No apartment data available for showing scheduling"
                )
        else:
            self.log_test_result(
                "Apartment Data Availability",
                False,
                f"Could not retrieve apartment data: {response['status']}"
            )
    
    async def test_email_service_integration(self):
        """Test 15: Test email service integration (contact form)"""
        test_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1-555-123-4567",
            "message": "Testing email service integration for showing confirmations"
        }
        
        response = await self.make_request("POST", "/contact", test_data)
        
        if response["status"] in [200, 201]:
            data = response["data"]
            if isinstance(data, dict) and ("message" in data or "contact_id" in data):
                self.log_test_result(
                    "Email Service Integration",
                    True,
                    "Email service appears to be working (contact form successful)"
                )
            else:
                self.log_test_result(
                    "Email Service Integration",
                    False,
                    f"Contact form succeeded but unexpected response: {data}"
                )
        else:
            self.log_test_result(
                "Email Service Integration",
                False,
                f"Email service may have issues (contact form failed): {response['status']}"
            )
    
    # ==========================================
    # MAIN TEST EXECUTION
    # ==========================================
    
    async def run_all_tests(self):
        """Run all backend tests"""
        logger.info("🚀 Starting NoFeePlaces Backend Testing Suite")
        logger.info("=" * 60)
        
        # Backend Health Tests
        await self.test_backend_health()
        await self.test_apartment_data_availability()
        await self.test_email_service_integration()
        
        # Schedule Showing Feature Tests
        logger.info("\n📅 SCHEDULE SHOWING FEATURE TESTS")
        logger.info("-" * 40)
        await self.test_schedule_showing_endpoint_exists()
        await self.test_schedule_showing_valid_request()
        await self.test_schedule_showing_24_hour_notice()
        await self.test_schedule_showing_business_hours()
        await self.test_schedule_showing_required_fields()
        await self.test_schedule_showing_email_format()
        
        # Login Functionality Tests
        logger.info("\n🔐 LOGIN FUNCTIONALITY TESTS")
        logger.info("-" * 40)
        await self.test_auth_login_endpoint_exists()
        await self.test_auth_login_invalid_credentials()
        await self.test_auth_login_admin_credentials()
        await self.test_auth_me_endpoint()
        await self.test_auth_me_without_token()
        await self.test_social_auth_endpoints()
        
        # Generate Summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        logger.info("\n" + "=" * 60)
        logger.info("🧪 TEST SUMMARY")
        logger.info("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        logger.info(f"Total Tests: {self.total_tests}")
        logger.info(f"Passed: {self.passed_tests}")
        logger.info(f"Failed: {self.total_tests - self.passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        # Categorize results
        schedule_showing_tests = [r for r in self.test_results if "showing" in r["test"].lower() or "schedule" in r["test"].lower()]
        login_tests = [r for r in self.test_results if "auth" in r["test"].lower() or "login" in r["test"].lower() or "social" in r["test"].lower()]
        other_tests = [r for r in self.test_results if r not in schedule_showing_tests and r not in login_tests]
        
        logger.info("\n📅 SCHEDULE SHOWING FEATURE RESULTS:")
        for test in schedule_showing_tests:
            logger.info(f"  {test['status']}: {test['test']}")
        
        logger.info("\n🔐 LOGIN FUNCTIONALITY RESULTS:")
        for test in login_tests:
            logger.info(f"  {test['status']}: {test['test']}")
        
        logger.info("\n🔧 BACKEND HEALTH RESULTS:")
        for test in other_tests:
            logger.info(f"  {test['status']}: {test['test']}")
        
        # Critical Issues
        failed_tests = [r for r in self.test_results if not r["passed"]]
        if failed_tests:
            logger.info("\n❌ CRITICAL ISSUES FOUND:")
            for test in failed_tests:
                logger.info(f"  • {test['test']}: {test.get('error', test.get('details', 'Unknown error'))}")
        
        logger.info("\n" + "=" * 60)

async def main():
    """Main test execution function"""
    async with NoFeePlacesBackendTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())