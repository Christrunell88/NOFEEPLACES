#!/usr/bin/env python3
"""
Focused Email Contact Modal Testing
Testing the specific issue: "Send Email Inquiry" on listing card is not populating
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FocusedEmailContactTester:
    def __init__(self):
        # Use production URL from frontend/.env
        self.base_url = "https://rentauth-test.preview.emergentagent.com/api"
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
    
    async def make_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None) -> dict:
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
    
    async def get_real_apartment_data(self) -> dict:
        """Get real apartment data from the API"""
        try:
            response = await self.make_request("GET", "/apartments?limit=5")
            if response["status"] == 200 and "apartments" in response["data"]:
                apartments = response["data"]["apartments"]
                if apartments:
                    apt = apartments[0]  # Use first apartment
                    return {
                        "id": apt.get("id"),
                        "title": apt.get("title", "2BR in Manhattan"),
                        "neighborhood": apt.get("neighborhood", "Chelsea"),
                        "price": apt.get("price", 3500),
                        "bedrooms": apt.get("bedrooms", 2),
                        "bathrooms": apt.get("bathrooms", 1.0),
                        "sqft": apt.get("sqft", 800),
                        "address": apt.get("address", "123 Main St, NYC"),
                        "amenities": apt.get("amenities", [])
                    }
            # Fallback data
            return {
                "id": "test-apartment-id",
                "title": "2BR in Manhattan",
                "neighborhood": "Chelsea", 
                "price": 3500,
                "bedrooms": 2,
                "bathrooms": 1.0,
                "sqft": 800,
                "address": "123 Main St, NYC",
                "amenities": ["Doorman", "Gym"]
            }
        except Exception as e:
            logger.error(f"Error getting apartment data: {e}")
            return {
                "id": "test-apartment-id",
                "title": "2BR in Manhattan",
                "neighborhood": "Chelsea",
                "price": 3500,
                "bedrooms": 2
            }
    
    # ==========================================
    # FOCUSED EMAIL CONTACT TESTS
    # ==========================================
    
    async def test_email_contact_endpoint_exists(self):
        """Test 1: Verify /api/send-contact-email endpoint exists and responds"""
        test_data = {
            "to": "placesfirm@gmail.com",
            "subject": "Test Email Inquiry",
            "sender_name": "Test User",
            "sender_email": "test@example.com",
            "message": "Test message"
        }
        
        response = await self.make_request("POST", "/send-contact-email", test_data)
        
        if response["status"] in [200, 201]:
            data = response["data"]
            if isinstance(data, dict) and data.get("success"):
                self.log_test_result(
                    "Email Contact Endpoint Exists",
                    True,
                    f"Endpoint working correctly: {data.get('message')}"
                )
            else:
                self.log_test_result(
                    "Email Contact Endpoint Exists",
                    False,
                    f"Endpoint exists but response invalid: {data}"
                )
        else:
            self.log_test_result(
                "Email Contact Endpoint Exists",
                False,
                f"Endpoint not working: status {response['status']}"
            )
    
    async def test_apartment_details_payload_structure(self):
        """Test 2: Test with exact apartment details payload structure from review"""
        apartment_data = await self.get_real_apartment_data()
        
        # Test with the exact payload structure from the review request
        test_data = {
            "to": "placesfirm@gmail.com",
            "subject": f"Interest in {apartment_data['title']}",
            "sender_name": "Test User",
            "sender_email": "test@example.com",
            "sender_phone": "555-1234",
            "message": "Interested in viewing",
            "apartment_details": {
                "title": apartment_data["title"],
                "neighborhood": apartment_data["neighborhood"],
                "price": apartment_data["price"],
                "bedrooms": apartment_data["bedrooms"]
            }
        }
        
        response = await self.make_request("POST", "/send-contact-email", test_data)
        
        if response["status"] in [200, 201]:
            data = response["data"]
            if isinstance(data, dict) and data.get("success"):
                self.log_test_result(
                    "Apartment Details Payload Test",
                    True,
                    f"Apartment details processed successfully: {apartment_data['title']}"
                )
            else:
                self.log_test_result(
                    "Apartment Details Payload Test",
                    False,
                    f"Apartment details failed: {data}"
                )
        else:
            self.log_test_result(
                "Apartment Details Payload Test",
                False,
                f"Request failed with status {response['status']}: {response.get('data', '')}"
            )
    
    async def test_email_service_integration(self):
        """Test 3: Verify email service integration is working"""
        test_data = {
            "to": "placesfirm@gmail.com",
            "subject": "SMTP Integration Test",
            "sender_name": "SMTP Tester",
            "sender_email": "smtp.test@example.com",
            "sender_phone": "555-SMTP",
            "message": "This is a test to verify SMTP email service is working correctly."
        }
        
        response = await self.make_request("POST", "/send-contact-email", test_data)
        
        if response["status"] in [200, 201]:
            data = response["data"]
            if isinstance(data, dict) and data.get("success"):
                self.log_test_result(
                    "Email Service Integration",
                    True,
                    "SMTP email service is working correctly"
                )
            else:
                self.log_test_result(
                    "Email Service Integration",
                    False,
                    f"SMTP service issue: {data.get('message', 'Unknown error')}"
                )
        else:
            self.log_test_result(
                "Email Service Integration",
                False,
                f"SMTP connection issue: status {response['status']}"
            )
    
    async def test_recipient_email_configuration(self):
        """Test 4: Verify recipient email is correctly configured to placesfirm@gmail.com"""
        test_data = {
            "to": "placesfirm@gmail.com",
            "subject": "Recipient Verification Test",
            "sender_name": "Recipient Tester",
            "sender_email": "recipient.test@example.com",
            "message": "Testing that emails are correctly sent to placesfirm@gmail.com"
        }
        
        response = await self.make_request("POST", "/send-contact-email", test_data)
        
        if response["status"] in [200, 201]:
            data = response["data"]
            if isinstance(data, dict) and data.get("success"):
                self.log_test_result(
                    "Recipient Email Configuration",
                    True,
                    "Email successfully sent to placesfirm@gmail.com"
                )
            else:
                self.log_test_result(
                    "Recipient Email Configuration",
                    False,
                    f"Recipient email issue: {data.get('message')}"
                )
        else:
            self.log_test_result(
                "Recipient Email Configuration",
                False,
                f"Recipient configuration error: status {response['status']}"
            )
    
    async def test_missing_required_fields_error_handling(self):
        """Test 5: Test error scenarios - missing required fields"""
        # Test missing sender_name
        test_data = {
            "to": "placesfirm@gmail.com",
            "subject": "Missing Name Test",
            "sender_email": "test@example.com",
            "message": "Test message"
            # Missing sender_name
        }
        
        response = await self.make_request("POST", "/send-contact-email", test_data)
        
        if response["status"] == 422:  # Validation error
            self.log_test_result(
                "Missing Required Fields Error Handling",
                True,
                "Correctly rejected request with missing sender_name"
            )
        else:
            self.log_test_result(
                "Missing Required Fields Error Handling",
                False,
                f"Should reject missing fields, got status {response['status']}"
            )
    
    async def test_invalid_email_format_error_handling(self):
        """Test 6: Test error scenarios - invalid email format"""
        test_data = {
            "to": "placesfirm@gmail.com",
            "subject": "Invalid Email Test",
            "sender_name": "Test User",
            "sender_email": "invalid-email-format",  # Invalid email
            "message": "Test message"
        }
        
        response = await self.make_request("POST", "/send-contact-email", test_data)
        
        # Note: The system might accept invalid emails but handle them gracefully
        if response["status"] == 422:
            self.log_test_result(
                "Invalid Email Format Error Handling",
                True,
                "Correctly rejected invalid email format"
            )
        elif response["status"] in [200, 201]:
            data = response["data"]
            if data.get("success") == False:
                self.log_test_result(
                    "Invalid Email Format Error Handling",
                    True,
                    "Invalid email handled gracefully at service level"
                )
            else:
                self.log_test_result(
                    "Invalid Email Format Error Handling",
                    False,
                    "Invalid email was accepted (may be handled at SMTP level)",
                    "Minor: Email validation could be stricter"
                )
        else:
            self.log_test_result(
                "Invalid Email Format Error Handling",
                False,
                f"Unexpected response to invalid email: {response['status']}"
            )
    
    async def test_missing_apartment_details_handling(self):
        """Test 7: Test missing apartment details (general inquiry)"""
        test_data = {
            "to": "placesfirm@gmail.com",
            "subject": "General Inquiry",
            "sender_name": "General Inquirer",
            "sender_email": "general@example.com",
            "message": "I'm looking for apartments in Manhattan. Can you help?"
            # No apartment_details field
        }
        
        response = await self.make_request("POST", "/send-contact-email", test_data)
        
        if response["status"] in [200, 201]:
            data = response["data"]
            if isinstance(data, dict) and data.get("success"):
                self.log_test_result(
                    "Missing Apartment Details Handling",
                    True,
                    "General inquiry without apartment details processed successfully"
                )
            else:
                self.log_test_result(
                    "Missing Apartment Details Handling",
                    False,
                    f"General inquiry failed: {data}"
                )
        else:
            self.log_test_result(
                "Missing Apartment Details Handling",
                False,
                f"General inquiry error: status {response['status']}"
            )
    
    async def test_smtp_connection_issues(self):
        """Test 8: Test SMTP connection issues (if any)"""
        # Send multiple emails to test SMTP stability
        for i in range(3):
            test_data = {
                "to": "placesfirm@gmail.com",
                "subject": f"SMTP Stability Test {i+1}",
                "sender_name": f"SMTP Tester {i+1}",
                "sender_email": f"smtp.test{i+1}@example.com",
                "message": f"This is SMTP stability test number {i+1}"
            }
            
            response = await self.make_request("POST", "/send-contact-email", test_data)
            
            if response["status"] not in [200, 201]:
                self.log_test_result(
                    "SMTP Connection Issues",
                    False,
                    f"SMTP failed on test {i+1}: status {response['status']}"
                )
                return
            
            data = response["data"]
            if not (isinstance(data, dict) and data.get("success")):
                self.log_test_result(
                    "SMTP Connection Issues",
                    False,
                    f"SMTP service issue on test {i+1}: {data}"
                )
                return
        
        self.log_test_result(
            "SMTP Connection Issues",
            True,
            "SMTP connection is stable - all 3 test emails sent successfully"
        )
    
    async def test_frontend_api_url_configuration(self):
        """Test 9: Verify frontend can reach the API endpoint"""
        # Test basic API connectivity
        response = await self.make_request("GET", "/apartments?limit=1")
        
        if response["status"] == 200:
            self.log_test_result(
                "Frontend API URL Configuration",
                True,
                "API is accessible from frontend URL configuration"
            )
        else:
            self.log_test_result(
                "Frontend API URL Configuration",
                False,
                f"API not accessible: status {response['status']}"
            )
    
    async def test_response_format_validation(self):
        """Test 10: Verify response format matches ContactEmailResponse model"""
        test_data = {
            "to": "placesfirm@gmail.com",
            "subject": "Response Format Test",
            "sender_name": "Format Tester",
            "sender_email": "format@example.com",
            "message": "Testing response format"
        }
        
        response = await self.make_request("POST", "/send-contact-email", test_data)
        
        if response["status"] in [200, 201]:
            data = response["data"]
            if isinstance(data, dict) and "success" in data and "message" in data:
                success_is_bool = isinstance(data["success"], bool)
                message_is_string = isinstance(data["message"], str)
                
                if success_is_bool and message_is_string:
                    self.log_test_result(
                        "Response Format Validation",
                        True,
                        "Response format matches ContactEmailResponse model"
                    )
                else:
                    self.log_test_result(
                        "Response Format Validation",
                        False,
                        f"Response format incorrect: success={type(data['success'])}, message={type(data['message'])}"
                    )
            else:
                self.log_test_result(
                    "Response Format Validation",
                    False,
                    f"Missing required fields in response: {data}"
                )
        else:
            self.log_test_result(
                "Response Format Validation",
                False,
                f"Could not test response format due to error: {response['status']}"
            )
    
    # ==========================================
    # MAIN TEST EXECUTION
    # ==========================================
    
    async def run_all_tests(self):
        """Run all focused email contact tests"""
        logger.info("🚀 Starting Focused Email Contact Modal Testing")
        logger.info("Testing: 'Send Email Inquiry' on listing card is not populating")
        logger.info("=" * 60)
        
        # Core Email Contact Tests
        await self.test_email_contact_endpoint_exists()
        await self.test_apartment_details_payload_structure()
        await self.test_email_service_integration()
        await self.test_recipient_email_configuration()
        
        # Error Handling Tests
        await self.test_missing_required_fields_error_handling()
        await self.test_invalid_email_format_error_handling()
        await self.test_missing_apartment_details_handling()
        
        # Service Integration Tests
        await self.test_smtp_connection_issues()
        await self.test_frontend_api_url_configuration()
        await self.test_response_format_validation()
        
        # Generate Summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        logger.info("\n" + "=" * 60)
        logger.info("🧪 FOCUSED EMAIL CONTACT TESTING SUMMARY")
        logger.info("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        logger.info(f"Total Tests: {self.total_tests}")
        logger.info(f"Passed: {self.passed_tests}")
        logger.info(f"Failed: {self.total_tests - self.passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        # Show all test results
        logger.info("\n📧 EMAIL CONTACT TEST RESULTS:")
        for test in self.test_results:
            logger.info(f"  {test['status']}: {test['test']}")
            if test['details']:
                logger.info(f"    Details: {test['details']}")
            if test['error']:
                logger.info(f"    Error: {test['error']}")
        
        # Critical Issues
        failed_tests = [r for r in self.test_results if not r["passed"]]
        if failed_tests:
            logger.info(f"\n❌ CRITICAL ISSUES FOUND ({len(failed_tests)}):")
            for test in failed_tests:
                logger.info(f"  • {test['test']}: {test.get('error', test.get('details', 'Unknown error'))}")
        else:
            logger.info("\n✅ ALL TESTS PASSED - EMAIL CONTACT FUNCTIONALITY IS WORKING")
        
        # Final Assessment
        logger.info(f"\n🎯 EMAIL CONTACT FUNCTIONALITY STATUS:")
        if self.total_tests - self.passed_tests == 0:
            logger.info("   🟢 FULLY FUNCTIONAL - Email contact system working perfectly")
        elif self.total_tests - self.passed_tests <= 2:
            logger.info("   🟡 MOSTLY FUNCTIONAL - Minor issues detected, core functionality working")
        else:
            logger.info("   🔴 ISSUES DETECTED - Multiple failures require attention")
        
        logger.info("\n" + "=" * 60)

async def main():
    """Main test execution function"""
    async with FocusedEmailContactTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())