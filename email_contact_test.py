#!/usr/bin/env python3
"""
NoFeePlaces.com Email Contact Functionality Testing Suite
Tests the new email contact functionality as requested in the review
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://aptlistpro.preview.emergentagent.com/api"

class EmailContactTester:
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
    
    def test_send_contact_email_endpoint_basic(self):
        """Test POST /api/send-contact-email endpoint with basic functionality"""
        print("\n=== Testing Send Contact Email Endpoint - Basic Functionality ===")
        
        # Test data from review request
        test_data = {
            "to": "placesfirm@gmail.com",
            "subject": "Interest in Renovated Studio on Lewis Avenue",
            "sender_name": "Test User",
            "sender_email": "test@example.com",
            "sender_phone": "555-123-4567",
            "message": "Hi, I'm interested in this apartment listing. Please provide more information.",
            "apartment_details": {
                "title": "Renovated Studio on Lewis Avenue - No Fee",
                "neighborhood": "Bedford-Stuyvesant",
                "price": 2300,
                "bedrooms": 0
            }
        }
        
        try:
            response = self.make_request("POST", "/send-contact-email", test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "success" in data and "message" in data:
                    if data["success"] == True:
                        self.log_result("Send Contact Email - Basic Success", True, 
                                      f"Email sent successfully: {data['message']}")
                    else:
                        self.log_result("Send Contact Email - Basic Success", False, 
                                      f"Email marked as failed: {data['message']}")
                    
                    # Verify response format matches ContactEmailResponse
                    if isinstance(data["success"], bool) and isinstance(data["message"], str):
                        self.log_result("Send Contact Email - Response Format", True, 
                                      "Response matches ContactEmailResponse format")
                    else:
                        self.log_result("Send Contact Email - Response Format", False, 
                                      f"Invalid response format: success={type(data['success'])}, message={type(data['message'])}")
                else:
                    self.log_result("Send Contact Email - Response Structure", False, 
                                  f"Missing required fields in response: {data}")
            else:
                self.log_result("Send Contact Email - Basic Success", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Send Contact Email - Basic Success", False, f"Exception: {str(e)}")
    
    def test_send_contact_email_with_apartment_details(self):
        """Test email sending with apartment details populated (from listing cards)"""
        print("\n=== Testing Send Contact Email - With Apartment Details ===")
        
        # Test with comprehensive apartment details
        test_data = {
            "to": "placesfirm@gmail.com",
            "subject": "Inquiry about 2BR in Chelsea",
            "sender_name": "Sarah Johnson",
            "sender_email": "sarah.johnson@example.com",
            "sender_phone": "646-555-0123",
            "message": "I'm very interested in this 2-bedroom apartment. When can I schedule a viewing?",
            "apartment_details": {
                "title": "Luxury 2BR in Chelsea - No Fee",
                "neighborhood": "Chelsea",
                "price": 4500,
                "bedrooms": 2,
                "bathrooms": 2.0,
                "sqft": 1200,
                "amenities": ["Doorman", "Gym", "Rooftop", "Laundry"]
            }
        }
        
        try:
            response = self.make_request("POST", "/send-contact-email", test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") == True:
                    self.log_result("Send Contact Email - With Apartment Details", True, 
                                  "Email with apartment details sent successfully")
                    
                    # Verify the message indicates apartment-specific inquiry
                    message = data.get("message", "")
                    if "apartment" in message.lower() or "inquiry" in message.lower():
                        self.log_result("Send Contact Email - Apartment Context", True, 
                                      "Response message indicates apartment-specific context")
                    else:
                        self.log_result("Send Contact Email - Apartment Context", False, 
                                      f"Response doesn't indicate apartment context: {message}")
                else:
                    self.log_result("Send Contact Email - With Apartment Details", False, 
                                  f"Email failed: {data.get('message', 'Unknown error')}")
            else:
                self.log_result("Send Contact Email - With Apartment Details", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Send Contact Email - With Apartment Details", False, f"Exception: {str(e)}")
    
    def test_send_contact_email_without_apartment_details(self):
        """Test email sending without apartment details (general inquiries)"""
        print("\n=== Testing Send Contact Email - General Inquiry (No Apartment Details) ===")
        
        # Test without apartment_details for general inquiries
        test_data = {
            "to": "placesfirm@gmail.com",
            "subject": "General Inquiry about No Fee Apartments",
            "sender_name": "Michael Chen",
            "sender_email": "michael.chen@example.com",
            "message": "Hi, I'm looking for a 1-bedroom apartment in Manhattan under $3500. Do you have any available listings?",
            # No apartment_details field
        }
        
        try:
            response = self.make_request("POST", "/send-contact-email", test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") == True:
                    self.log_result("Send Contact Email - General Inquiry", True, 
                                  "General inquiry email sent successfully")
                    
                    # Verify response is appropriate for general inquiry
                    message = data.get("message", "")
                    if message and len(message) > 0:
                        self.log_result("Send Contact Email - General Response", True, 
                                      f"Appropriate response message: {message}")
                    else:
                        self.log_result("Send Contact Email - General Response", False, 
                                      "Empty or missing response message")
                else:
                    self.log_result("Send Contact Email - General Inquiry", False, 
                                  f"General inquiry failed: {data.get('message', 'Unknown error')}")
            else:
                self.log_result("Send Contact Email - General Inquiry", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Send Contact Email - General Inquiry", False, f"Exception: {str(e)}")
    
    def test_required_field_validation(self):
        """Test validation of required fields (sender_name, sender_email, message)"""
        print("\n=== Testing Required Field Validation ===")
        
        # Test missing sender_name
        try:
            test_data = {
                "to": "placesfirm@gmail.com",
                "subject": "Test Subject",
                "sender_email": "test@example.com",
                "message": "Test message"
                # Missing sender_name
            }
            
            response = self.make_request("POST", "/send-contact-email", test_data)
            
            if response.status_code == 422:  # Validation error
                self.log_result("Required Field Validation - Missing Name", True, 
                              "Correctly rejected request with missing sender_name")
            elif response.status_code == 400:
                self.log_result("Required Field Validation - Missing Name", True, 
                              "Correctly rejected request with missing sender_name (400)")
            else:
                self.log_result("Required Field Validation - Missing Name", False, 
                              f"Should reject missing sender_name, got {response.status_code}")
        except Exception as e:
            self.log_result("Required Field Validation - Missing Name", False, f"Exception: {str(e)}")
        
        # Test missing sender_email
        try:
            test_data = {
                "to": "placesfirm@gmail.com",
                "subject": "Test Subject",
                "sender_name": "Test User",
                "message": "Test message"
                # Missing sender_email
            }
            
            response = self.make_request("POST", "/send-contact-email", test_data)
            
            if response.status_code in [422, 400]:
                self.log_result("Required Field Validation - Missing Email", True, 
                              "Correctly rejected request with missing sender_email")
            else:
                self.log_result("Required Field Validation - Missing Email", False, 
                              f"Should reject missing sender_email, got {response.status_code}")
        except Exception as e:
            self.log_result("Required Field Validation - Missing Email", False, f"Exception: {str(e)}")
        
        # Test missing message
        try:
            test_data = {
                "to": "placesfirm@gmail.com",
                "subject": "Test Subject",
                "sender_name": "Test User",
                "sender_email": "test@example.com"
                # Missing message
            }
            
            response = self.make_request("POST", "/send-contact-email", test_data)
            
            if response.status_code in [422, 400]:
                self.log_result("Required Field Validation - Missing Message", True, 
                              "Correctly rejected request with missing message")
            else:
                self.log_result("Required Field Validation - Missing Message", False, 
                              f"Should reject missing message, got {response.status_code}")
        except Exception as e:
            self.log_result("Required Field Validation - Missing Message", False, f"Exception: {str(e)}")
    
    def test_optional_fields(self):
        """Test optional fields (sender_phone)"""
        print("\n=== Testing Optional Fields ===")
        
        # Test with sender_phone provided
        try:
            test_data_with_phone = {
                "to": "placesfirm@gmail.com",
                "subject": "Test with Phone",
                "sender_name": "Test User With Phone",
                "sender_email": "test.phone@example.com",
                "sender_phone": "555-987-6543",
                "message": "This is a test message with phone number provided."
            }
            
            response = self.make_request("POST", "/send-contact-email", test_data_with_phone)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Optional Fields - With Phone", True, 
                                  "Email sent successfully with phone number")
                else:
                    self.log_result("Optional Fields - With Phone", False, 
                                  f"Email failed with phone: {data.get('message')}")
            else:
                self.log_result("Optional Fields - With Phone", False, 
                              f"HTTP {response.status_code} with phone")
        except Exception as e:
            self.log_result("Optional Fields - With Phone", False, f"Exception: {str(e)}")
        
        # Test without sender_phone (should still work)
        try:
            test_data_no_phone = {
                "to": "placesfirm@gmail.com",
                "subject": "Test without Phone",
                "sender_name": "Test User No Phone",
                "sender_email": "test.nophone@example.com",
                "message": "This is a test message without phone number."
                # No sender_phone field
            }
            
            response = self.make_request("POST", "/send-contact-email", test_data_no_phone)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Optional Fields - Without Phone", True, 
                                  "Email sent successfully without phone number")
                else:
                    self.log_result("Optional Fields - Without Phone", False, 
                                  f"Email failed without phone: {data.get('message')}")
            else:
                self.log_result("Optional Fields - Without Phone", False, 
                              f"HTTP {response.status_code} without phone")
        except Exception as e:
            self.log_result("Optional Fields - Without Phone", False, f"Exception: {str(e)}")
    
    def test_email_format_validation(self):
        """Test validation of email format"""
        print("\n=== Testing Email Format Validation ===")
        
        invalid_emails = [
            "invalid-email",
            "test@",
            "@example.com",
            "test..test@example.com",
            "test@example",
            ""
        ]
        
        for invalid_email in invalid_emails:
            try:
                test_data = {
                    "to": "placesfirm@gmail.com",
                    "subject": "Test Invalid Email",
                    "sender_name": "Test User",
                    "sender_email": invalid_email,
                    "message": "Test message with invalid email"
                }
                
                response = self.make_request("POST", "/send-contact-email", test_data)
                
                if response.status_code in [422, 400]:
                    self.log_result(f"Email Validation - Invalid '{invalid_email}'", True, 
                                  f"Correctly rejected invalid email: {invalid_email}")
                elif response.status_code == 200:
                    # Some systems might accept invalid emails but fail at SMTP level
                    data = response.json()
                    if data.get("success") == False:
                        self.log_result(f"Email Validation - Invalid '{invalid_email}'", True, 
                                      f"Email rejected at service level: {invalid_email}")
                    else:
                        self.log_result(f"Email Validation - Invalid '{invalid_email}'", False, 
                                      f"Invalid email accepted: {invalid_email}")
                else:
                    self.log_result(f"Email Validation - Invalid '{invalid_email}'", False, 
                                  f"Unexpected response {response.status_code} for {invalid_email}")
                    
            except Exception as e:
                self.log_result(f"Email Validation - Invalid '{invalid_email}'", False, f"Exception: {str(e)}")
        
        # Test valid email format
        try:
            test_data = {
                "to": "placesfirm@gmail.com",
                "subject": "Test Valid Email",
                "sender_name": "Test User",
                "sender_email": "valid.email@example.com",
                "message": "Test message with valid email format"
            }
            
            response = self.make_request("POST", "/send-contact-email", test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Email Validation - Valid Format", True, 
                                  "Valid email format accepted")
                else:
                    self.log_result("Email Validation - Valid Format", False, 
                                  f"Valid email rejected: {data.get('message')}")
            else:
                self.log_result("Email Validation - Valid Format", False, 
                              f"Valid email failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Email Validation - Valid Format", False, f"Exception: {str(e)}")
    
    def test_recipient_email_verification(self):
        """Test that recipient email is correctly set to placesfirm@gmail.com"""
        print("\n=== Testing Recipient Email Verification ===")
        
        # Test with correct recipient
        try:
            test_data = {
                "to": "placesfirm@gmail.com",
                "subject": "Test Correct Recipient",
                "sender_name": "Test User",
                "sender_email": "test@example.com",
                "message": "Testing correct recipient email"
            }
            
            response = self.make_request("POST", "/send-contact-email", test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Recipient Email - Correct", True, 
                                  "Email sent to placesfirm@gmail.com successfully")
                else:
                    self.log_result("Recipient Email - Correct", False, 
                                  f"Failed to send to placesfirm@gmail.com: {data.get('message')}")
            else:
                self.log_result("Recipient Email - Correct", False, 
                              f"HTTP {response.status_code} for correct recipient")
                
        except Exception as e:
            self.log_result("Recipient Email - Correct", False, f"Exception: {str(e)}")
        
        # Test with different recipient (should still work if endpoint allows it)
        try:
            test_data = {
                "to": "different@example.com",
                "subject": "Test Different Recipient",
                "sender_name": "Test User",
                "sender_email": "test@example.com",
                "message": "Testing different recipient email"
            }
            
            response = self.make_request("POST", "/send-contact-email", test_data)
            
            if response.status_code == 200:
                data = response.json()
                # This might succeed or fail depending on implementation
                self.log_result("Recipient Email - Different", True, 
                              f"Different recipient handling: success={data.get('success')}")
            else:
                self.log_result("Recipient Email - Different", True, 
                              f"Different recipient rejected: {response.status_code}")
                
        except Exception as e:
            self.log_result("Recipient Email - Different", False, f"Exception: {str(e)}")
    
    def test_subject_line_formatting(self):
        """Test proper subject line formatting"""
        print("\n=== Testing Subject Line Formatting ===")
        
        test_subjects = [
            "Interest in Studio Apartment",
            "Question about 2BR in Manhattan",
            "Viewing Request - Chelsea Apartment",
            "General Inquiry about No Fee Apartments"
        ]
        
        for subject in test_subjects:
            try:
                test_data = {
                    "to": "placesfirm@gmail.com",
                    "subject": subject,
                    "sender_name": "Test User",
                    "sender_email": "test@example.com",
                    "message": f"Test message for subject: {subject}"
                }
                
                response = self.make_request("POST", "/send-contact-email", test_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") == True:
                        self.log_result(f"Subject Line - '{subject[:30]}...'", True, 
                                      "Subject line processed successfully")
                    else:
                        self.log_result(f"Subject Line - '{subject[:30]}...'", False, 
                                      f"Failed with subject: {data.get('message')}")
                else:
                    self.log_result(f"Subject Line - '{subject[:30]}...'", False, 
                                  f"HTTP {response.status_code} for subject")
                    
            except Exception as e:
                self.log_result(f"Subject Line - '{subject[:30]}...'", False, f"Exception: {str(e)}")
    
    def test_email_template_generation(self):
        """Test email template generation with apartment details"""
        print("\n=== Testing Email Template Generation ===")
        
        # Test with comprehensive apartment details to verify template
        test_data = {
            "to": "placesfirm@gmail.com",
            "subject": "Template Test - Luxury Apartment",
            "sender_name": "Template Tester",
            "sender_email": "template.test@example.com",
            "sender_phone": "555-TEMPLATE",
            "message": "This is a comprehensive test of the email template generation with all possible apartment details included.",
            "apartment_details": {
                "title": "Luxury 3BR Penthouse - No Fee",
                "neighborhood": "Upper East Side",
                "price": 8500,
                "bedrooms": 3,
                "bathrooms": 2.5,
                "sqft": 1800,
                "amenities": ["Doorman", "Concierge", "Gym", "Pool", "Rooftop Terrace", "Parking"],
                "building_name": "The Manhattan Tower",
                "address": "123 Park Avenue, New York, NY 10021"
            }
        }
        
        try:
            response = self.make_request("POST", "/send-contact-email", test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Email Template Generation", True, 
                                  "Email template generated successfully with apartment details")
                    
                    # Verify response message is appropriate
                    message = data.get("message", "")
                    if "success" in message.lower() or "sent" in message.lower():
                        self.log_result("Email Template Response", True, 
                                      f"Appropriate success message: {message}")
                    else:
                        self.log_result("Email Template Response", False, 
                                      f"Unclear success message: {message}")
                else:
                    self.log_result("Email Template Generation", False, 
                                  f"Template generation failed: {data.get('message')}")
            else:
                self.log_result("Email Template Generation", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Email Template Generation", False, f"Exception: {str(e)}")
    
    def test_error_handling_scenarios(self):
        """Test error handling for various failure scenarios"""
        print("\n=== Testing Error Handling Scenarios ===")
        
        # Test with malformed JSON
        try:
            response = requests.post(
                f"{self.base_url}/send-contact-email",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [400, 422]:
                self.log_result("Error Handling - Malformed JSON", True, 
                              "Correctly handled malformed JSON")
            else:
                self.log_result("Error Handling - Malformed JSON", False, 
                              f"Unexpected response to malformed JSON: {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling - Malformed JSON", False, f"Exception: {str(e)}")
        
        # Test with empty request body
        try:
            response = self.make_request("POST", "/send-contact-email", {})
            
            if response.status_code in [400, 422]:
                self.log_result("Error Handling - Empty Request", True, 
                              "Correctly handled empty request")
            else:
                self.log_result("Error Handling - Empty Request", False, 
                              f"Unexpected response to empty request: {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling - Empty Request", False, f"Exception: {str(e)}")
        
        # Test with extremely long message
        try:
            long_message = "A" * 10000  # 10KB message
            test_data = {
                "to": "placesfirm@gmail.com",
                "subject": "Test Long Message",
                "sender_name": "Test User",
                "sender_email": "test@example.com",
                "message": long_message
            }
            
            response = self.make_request("POST", "/send-contact-email", test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Error Handling - Long Message", True, 
                                  "Long message handled successfully")
                else:
                    self.log_result("Error Handling - Long Message", True, 
                                  f"Long message appropriately rejected: {data.get('message')}")
            elif response.status_code in [400, 413, 422]:
                self.log_result("Error Handling - Long Message", True, 
                              "Long message appropriately rejected")
            else:
                self.log_result("Error Handling - Long Message", False, 
                              f"Unexpected response to long message: {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling - Long Message", False, f"Exception: {str(e)}")
    
    def test_response_format_consistency(self):
        """Test that all responses follow ContactEmailResponse format"""
        print("\n=== Testing Response Format Consistency ===")
        
        test_cases = [
            {
                "name": "Success Case",
                "data": {
                    "to": "placesfirm@gmail.com",
                    "subject": "Format Test Success",
                    "sender_name": "Format Tester",
                    "sender_email": "format@example.com",
                    "message": "Testing response format consistency"
                },
                "expected_success": True
            },
            {
                "name": "Missing Field Case",
                "data": {
                    "to": "placesfirm@gmail.com",
                    "subject": "Format Test Failure",
                    "sender_email": "format@example.com",
                    "message": "Testing response format with missing name"
                    # Missing sender_name
                },
                "expected_success": False
            }
        ]
        
        for test_case in test_cases:
            try:
                response = self.make_request("POST", "/send-contact-email", test_case["data"])
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response has required fields
                    if "success" in data and "message" in data:
                        # Verify field types
                        if isinstance(data["success"], bool) and isinstance(data["message"], str):
                            self.log_result(f"Response Format - {test_case['name']}", True, 
                                          f"Correct format: success={data['success']}, message='{data['message'][:50]}...'")
                        else:
                            self.log_result(f"Response Format - {test_case['name']}", False, 
                                          f"Wrong field types: success={type(data['success'])}, message={type(data['message'])}")
                    else:
                        self.log_result(f"Response Format - {test_case['name']}", False, 
                                      f"Missing required fields: {list(data.keys())}")
                elif response.status_code in [400, 422]:
                    # Error responses should still be JSON
                    try:
                        error_data = response.json()
                        if "detail" in error_data or "message" in error_data:
                            self.log_result(f"Response Format - {test_case['name']} Error", True, 
                                          "Error response properly formatted")
                        else:
                            self.log_result(f"Response Format - {test_case['name']} Error", False, 
                                          f"Error response missing details: {error_data}")
                    except json.JSONDecodeError:
                        self.log_result(f"Response Format - {test_case['name']} Error", False, 
                                      "Error response not valid JSON")
                else:
                    self.log_result(f"Response Format - {test_case['name']}", False, 
                                  f"Unexpected status code: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Response Format - {test_case['name']}", False, f"Exception: {str(e)}")
    
    def test_integration_with_frontend_modal(self):
        """Test integration scenarios that would come from frontend EmailContactModal"""
        print("\n=== Testing Frontend Integration Scenarios ===")
        
        # Simulate data that would come from apartment listing card
        apartment_card_data = {
            "to": "placesfirm@gmail.com",
            "subject": "Interest in Apartment from Listing Card",
            "sender_name": "Frontend User",
            "sender_email": "frontend.user@example.com",
            "sender_phone": "555-FRONTEND",
            "message": "I saw this apartment on your website and I'm very interested. Can we schedule a viewing?",
            "apartment_details": {
                "title": "Modern 1BR in Williamsburg - No Fee",
                "neighborhood": "Williamsburg",
                "price": 3200,
                "bedrooms": 1,
                "bathrooms": 1.0,
                "sqft": 750,
                "amenities": ["Dishwasher", "Laundry in Unit", "Balcony"]
            }
        }
        
        try:
            response = self.make_request("POST", "/send-contact-email", apartment_card_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Frontend Integration - Apartment Card", True, 
                                  "Successfully processed apartment card inquiry")
                else:
                    self.log_result("Frontend Integration - Apartment Card", False, 
                                  f"Apartment card inquiry failed: {data.get('message')}")
            else:
                self.log_result("Frontend Integration - Apartment Card", False, 
                              f"HTTP {response.status_code} for apartment card data")
                
        except Exception as e:
            self.log_result("Frontend Integration - Apartment Card", False, f"Exception: {str(e)}")
        
        # Simulate general contact form data
        general_contact_data = {
            "to": "placesfirm@gmail.com",
            "subject": "General Contact Form Inquiry",
            "sender_name": "General Inquirer",
            "sender_email": "general@example.com",
            "message": "I'm looking for a pet-friendly apartment in Brooklyn under $2800. Do you have any recommendations?"
            # No apartment_details for general inquiry
        }
        
        try:
            response = self.make_request("POST", "/send-contact-email", general_contact_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Frontend Integration - General Contact", True, 
                                  "Successfully processed general contact form")
                else:
                    self.log_result("Frontend Integration - General Contact", False, 
                                  f"General contact failed: {data.get('message')}")
            else:
                self.log_result("Frontend Integration - General Contact", False, 
                              f"HTTP {response.status_code} for general contact")
                
        except Exception as e:
            self.log_result("Frontend Integration - General Contact", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all email contact functionality tests"""
        print("🧪 STARTING EMAIL CONTACT FUNCTIONALITY TESTING")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test methods
        self.test_send_contact_email_endpoint_basic()
        self.test_send_contact_email_with_apartment_details()
        self.test_send_contact_email_without_apartment_details()
        self.test_required_field_validation()
        self.test_optional_fields()
        self.test_email_format_validation()
        self.test_recipient_email_verification()
        self.test_subject_line_formatting()
        self.test_email_template_generation()
        self.test_error_handling_scenarios()
        self.test_response_format_consistency()
        self.test_integration_with_frontend_modal()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 EMAIL CONTACT FUNCTIONALITY TEST SUMMARY")
        print("=" * 60)
        print(f"⏱️  Total test duration: {duration:.2f} seconds")
        print(f"✅ Tests passed: {self.results['passed']}")
        print(f"❌ Tests failed: {self.results['failed']}")
        print(f"📈 Success rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 FAILED TESTS ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print(f"\n🎯 EMAIL CONTACT FUNCTIONALITY STATUS:")
        if self.results['failed'] == 0:
            print("   🟢 ALL TESTS PASSED - Email contact functionality is working perfectly!")
        elif self.results['failed'] <= 2:
            print("   🟡 MOSTLY WORKING - Minor issues detected, but core functionality operational")
        else:
            print("   🔴 ISSUES DETECTED - Multiple failures require attention")
        
        return self.results['failed'] == 0


if __name__ == "__main__":
    tester = EmailContactTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Email contact functionality testing completed successfully!")
    else:
        print("\n⚠️  Email contact functionality testing completed with issues.")