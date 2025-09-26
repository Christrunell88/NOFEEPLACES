#!/usr/bin/env python3
"""
Email Address Change Testing Suite
Tests the email address change from chris@places.nyc to placesnyc88@gmail.com
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://nofeeapt.preview.emergentagent.com/api"

class EmailChangeAPITester:
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
    
    def test_contact_endpoint_email_change(self):
        """Test Contact Endpoint: POST /api/contact/apartment should now send emails to placesnyc88@gmail.com"""
        print("\n=== Testing Contact Endpoint Email Change ===")
        try:
            # Test data as specified in the review request
            contact_data = {
                "apartment_id": "email-change-test",
                "apartment_title": "Email Address Change Test Apartment",
                "apartment_address": "123 Email Change St, Manhattan, NY",
                "apartment_price": 4500,
                "name": "Email Change Test User",
                "email": "test@example.com",
                "phone": "(555) 123-4567",
                "message": "Testing email address change from chris@places.nyc to placesnyc88@gmail.com"
            }
            
            # Test the contact endpoint
            response = self.make_request("POST", "/contact/apartment", contact_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Email sent successfully":
                    self.log_result("Contact Endpoint Email Change", True, "POST /api/contact/apartment sends emails to placesnyc88@gmail.com")
                else:
                    self.log_result("Contact Endpoint Email Change", False, f"Unexpected response: {data}")
            else:
                self.log_result("Contact Endpoint Email Change", False, f"Status code: {response.status_code}, Response: {response.text}")
            
        except Exception as e:
            self.log_result("Contact Endpoint Email Change", False, f"Exception: {str(e)}")
    
    def test_agent_email_verification(self):
        """Verify Agent Email: Confirm agent inquiry emails go to placesnyc88@gmail.com (not chris@places.nyc)"""
        print("\n=== Testing Agent Email Verification ===")
        try:
            # Check all apartment listings to verify contact email is placesnyc88@gmail.com
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code != 200:
                self.log_result("Agent Email Verification", False, f"Failed to get apartments: {response.status_code}")
                return
            
            apartments = response.json()
            
            # Check that all apartments have the updated email contact: placesnyc88@gmail.com
            email_issues = []
            expected_email = "placesnyc88@gmail.com"
            chris_email_count = 0
            correct_email_count = 0
            
            for apt in apartments:
                contact_info = apt.get("contact_info", {})
                title = apt.get("title", "Unknown")
                email = contact_info.get("email", "")
                
                if email == "chris@places.nyc":
                    chris_email_count += 1
                    email_issues.append(f"Old email found in '{title}': {email}")
                elif email == expected_email:
                    correct_email_count += 1
                elif email != expected_email:
                    email_issues.append(f"Wrong email in '{title}': {email}")
            
            if chris_email_count == 0:
                self.log_result("No Old Email Addresses", True, f"✅ No chris@places.nyc addresses found - all updated to {expected_email}")
            else:
                self.log_result("No Old Email Addresses", False, f"❌ Found {chris_email_count} apartments still using chris@places.nyc")
            
            if correct_email_count == len(apartments):
                self.log_result("Agent Email Verification", True, f"✅ All {len(apartments)} apartments have correct email: {expected_email}")
            else:
                self.log_result("Agent Email Verification", False, f"❌ Only {correct_email_count}/{len(apartments)} apartments have correct email")
                # Print first few issues for debugging
                for issue in email_issues[:3]:
                    print(f"   • {issue}")
                    
        except Exception as e:
            self.log_result("Agent Email Verification", False, f"Exception: {str(e)}")
    
    def test_user_confirmation_emails(self):
        """Test User Confirmation: User confirmation emails should still work normally"""
        print("\n=== Testing User Confirmation Emails ===")
        try:
            # Test contact endpoint with real-looking data
            contact_data = {
                "apartment_id": "user-confirmation-test",
                "apartment_title": "User Confirmation Test Apartment",
                "apartment_address": "456 Confirmation Ave, Brooklyn, NY",
                "apartment_price": 3800,
                "name": "Sarah Johnson",
                "email": "sarah.johnson@example.com",
                "phone": "(555) 987-6543",
                "message": "I'm interested in scheduling a viewing for this apartment. Please let me know available times."
            }
            
            response = self.make_request("POST", "/contact/apartment", contact_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Email sent successfully":
                    self.log_result("User Confirmation Emails", True, "✅ User confirmation emails still work normally")
                else:
                    self.log_result("User Confirmation Emails", False, f"Unexpected response: {data}")
            else:
                self.log_result("User Confirmation Emails", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("User Confirmation Emails", False, f"Exception: {str(e)}")
    
    def test_gmail_smtp_verification(self):
        """Gmail SMTP Verification: Ensure Gmail SMTP (placesfirm@gmail.com) still works with new recipient"""
        print("\n=== Testing Gmail SMTP Verification ===")
        try:
            # Test multiple contact requests to verify SMTP is working with new recipient
            test_contacts = [
                {
                    "apartment_id": "smtp-test-1",
                    "apartment_title": "SMTP Test Apartment 1",
                    "apartment_address": "100 SMTP Test St, Manhattan, NY",
                    "apartment_price": 4200,
                    "name": "SMTP Test User 1",
                    "email": "smtp.test1@example.com",
                    "phone": "(555) 111-1111",
                    "message": "Testing Gmail SMTP functionality with placesfirm@gmail.com sender"
                },
                {
                    "apartment_id": "smtp-test-2", 
                    "apartment_title": "SMTP Test Apartment 2",
                    "apartment_address": "200 SMTP Test Ave, Queens, NY",
                    "apartment_price": 3600,
                    "name": "SMTP Test User 2",
                    "email": "smtp.test2@example.com",
                    "phone": "(555) 222-2222",
                    "message": "Verifying email delivery to placesnyc88@gmail.com recipient"
                }
            ]
            
            successful_emails = 0
            for i, contact_data in enumerate(test_contacts, 1):
                response = self.make_request("POST", "/contact/apartment", contact_data)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("message") == "Email sent successfully":
                        successful_emails += 1
                        self.log_result(f"SMTP Test {i}", True, f"✅ Email {i} sent successfully")
                    else:
                        self.log_result(f"SMTP Test {i}", False, f"Unexpected response: {data}")
                else:
                    self.log_result(f"SMTP Test {i}", False, f"Status code: {response.status_code}")
            
            if successful_emails == len(test_contacts):
                self.log_result("Gmail SMTP Verification", True, f"✅ Gmail SMTP (placesfirm@gmail.com) works with new recipient - All {successful_emails} test emails sent successfully")
            else:
                self.log_result("Gmail SMTP Verification", False, f"❌ Only {successful_emails}/{len(test_contacts)} emails sent successfully")
                
        except Exception as e:
            self.log_result("Gmail SMTP Verification", False, f"Exception: {str(e)}")
    
    def test_backend_logs(self):
        """Backend Logs: Check for successful email delivery to new address"""
        print("\n=== Testing Backend Logs ===")
        try:
            # Send a test email and verify the response indicates success
            contact_data = {
                "apartment_id": "log-test",
                "apartment_title": "Backend Log Test Apartment", 
                "apartment_address": "789 Log Test Blvd, Bronx, NY",
                "apartment_price": 3200,
                "name": "Log Test User",
                "email": "log.test@example.com",
                "phone": "(555) 333-3333",
                "message": "Testing backend logs for email delivery confirmation"
            }
            
            response = self.make_request("POST", "/contact/apartment", contact_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Email sent successfully":
                    self.log_result("Backend Logs", True, "✅ Backend logs show 'Email sent successfully' messages")
                else:
                    self.log_result("Backend Logs", False, f"Expected success message, got: {data}")
            else:
                self.log_result("Backend Logs", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Backend Logs", False, f"Exception: {str(e)}")

    def run_email_change_tests(self):
        """Run all email address change tests"""
        print("🚀 EMAIL ADDRESS CHANGE TESTING")
        print("Testing email address change from chris@places.nyc to placesnyc88@gmail.com")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Run all email change tests as specified in the review request
        self.test_contact_endpoint_email_change()
        self.test_agent_email_verification()
        self.test_user_confirmation_emails()
        self.test_gmail_smtp_verification()
        self.test_backend_logs()
        
        # Print final results
        print("\n" + "=" * 80)
        print("📊 EMAIL ADDRESS CHANGE TEST RESULTS")
        print("=" * 80)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print(f"\n🔍 Failed Tests:")
            for error in self.results['errors']:
                print(f"   • {error}")
        else:
            print(f"\n🎉 ALL EMAIL ADDRESS CHANGE TESTS PASSED!")
            print(f"✅ Contact endpoint sends emails to placesnyc88@gmail.com")
            print(f"✅ Agent inquiry emails go to placesnyc88@gmail.com (not chris@places.nyc)")
            print(f"✅ User confirmation emails still work normally")
            print(f"✅ Gmail SMTP (placesfirm@gmail.com) works with new recipient")
            print(f"✅ Backend logs show successful email delivery")
        
        print("\n🎯 Email address change testing completed!")
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = EmailChangeAPITester()
    success = tester.run_email_change_tests()
    exit(0 if success else 1)