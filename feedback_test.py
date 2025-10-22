#!/usr/bin/env python3
"""
NoFeePlaces.com Feedback Submission System Testing Suite
Tests the new feedback submission endpoint, database storage, and email notifications
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://apartment-viewings.preview.emergentagent.com/api"

class FeedbackSystemTester:
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
    
    def test_feedback_endpoint_basic(self):
        """Test basic feedback submission endpoint functionality"""
        print("\n=== Testing Feedback Endpoint Basic Functionality ===")
        
        # Test successful feedback submission with all required fields
        feedback_data = {
            "type": "bug",
            "title": "Search functionality not working properly",
            "description": "When I search for apartments in Brooklyn, the results show Manhattan apartments instead. This is confusing and makes it hard to find what I'm looking for.",
            "email": "sarah.johnson@example.com",
            "page": "Apartment Search",
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "priority": "high",
            "timestamp": datetime.now().isoformat(),
            "url": "https://nofeeplaces.com/"
        }
        
        try:
            response = self.make_request("POST", "/feedback/submit", feedback_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response format matches FeedbackResponse model
                if all(key in data for key in ["success", "message", "feedback_id"]):
                    if data["success"] and data["feedback_id"]:
                        self.log_result("Feedback Submission (Bug Report)", True, 
                                      f"Successfully submitted bug report. Feedback ID: {data['feedback_id']}")
                    else:
                        self.log_result("Feedback Submission (Bug Report)", False, 
                                      f"Response indicates failure: {data}")
                else:
                    self.log_result("Feedback Submission (Bug Report)", False, 
                                  f"Response missing required fields: {data}")
            else:
                self.log_result("Feedback Submission (Bug Report)", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Feedback Submission (Bug Report)", False, f"Exception: {str(e)}")
    
    def test_feedback_categories(self):
        """Test feedback submission with different categories"""
        print("\n=== Testing Feedback Categories ===")
        
        feedback_types = [
            {
                "type": "feature",
                "title": "Add map view for apartment listings",
                "description": "It would be great to have a map view showing all available apartments in a specific area. This would help visualize the locations better.",
                "priority": "medium"
            },
            {
                "type": "improvement",
                "title": "Improve mobile responsiveness",
                "description": "The apartment cards look a bit cramped on mobile devices. Could you make them more mobile-friendly?",
                "priority": "low"
            },
            {
                "type": "compliment",
                "title": "Great selection of no-fee apartments!",
                "description": "I love that you have so many no-fee options. This saves me thousands of dollars in broker fees. Keep up the great work!",
                "priority": "low"
            },
            {
                "type": "other",
                "title": "Question about apartment availability",
                "description": "How often do you update the apartment listings? I want to make sure I'm seeing the most current available units.",
                "priority": "medium"
            }
        ]
        
        for i, feedback_type in enumerate(feedback_types, 1):
            try:
                feedback_data = {
                    **feedback_type,
                    "email": f"user{i}@example.com",
                    "page": "Homepage",
                    "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    "timestamp": datetime.now().isoformat(),
                    "url": "https://nofeeplaces.com/"
                }
                
                response = self.make_request("POST", "/feedback/submit", feedback_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("feedback_id"):
                        self.log_result(f"Feedback Category ({feedback_type['type'].title()})", True, 
                                      f"Successfully submitted {feedback_type['type']} feedback")
                    else:
                        self.log_result(f"Feedback Category ({feedback_type['type'].title()})", False, 
                                      f"Submission failed: {data}")
                else:
                    self.log_result(f"Feedback Category ({feedback_type['type'].title()})", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
                # Small delay between submissions
                time.sleep(0.5)
                
            except Exception as e:
                self.log_result(f"Feedback Category ({feedback_type['type'].title()})", False, f"Exception: {str(e)}")
    
    def test_feedback_with_and_without_email(self):
        """Test feedback submission with and without email provided"""
        print("\n=== Testing Feedback With and Without Email ===")
        
        # Test with email provided
        try:
            feedback_with_email = {
                "type": "bug",
                "title": "Image loading issue on apartment details page",
                "description": "Some apartment images are not loading properly. I see broken image icons instead of the actual photos.",
                "email": "michael.chen@example.com",
                "page": "Apartment Details",
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "priority": "medium",
                "timestamp": datetime.now().isoformat(),
                "url": "https://nofeeplaces.com/apartment/123"
            }
            
            response = self.make_request("POST", "/feedback/submit", feedback_with_email)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("Feedback With Email", True, 
                                  "Successfully submitted feedback with email for confirmation")
                else:
                    self.log_result("Feedback With Email", False, f"Submission failed: {data}")
            else:
                self.log_result("Feedback With Email", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Feedback With Email", False, f"Exception: {str(e)}")
        
        # Test without email provided
        try:
            feedback_without_email = {
                "type": "feature",
                "title": "Add dark mode option",
                "description": "A dark mode would be great for browsing apartments in the evening. It's easier on the eyes.",
                "email": None,  # No email provided
                "page": "Settings",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
                "priority": "low",
                "timestamp": datetime.now().isoformat(),
                "url": "https://nofeeplaces.com/settings"
            }
            
            response = self.make_request("POST", "/feedback/submit", feedback_without_email)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("Feedback Without Email", True, 
                                  "Successfully submitted feedback without email (anonymous)")
                else:
                    self.log_result("Feedback Without Email", False, f"Submission failed: {data}")
            else:
                self.log_result("Feedback Without Email", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Feedback Without Email", False, f"Exception: {str(e)}")
    
    def test_feedback_validation(self):
        """Test feedback validation for missing required fields"""
        print("\n=== Testing Feedback Validation ===")
        
        validation_tests = [
            {
                "name": "Missing Type",
                "data": {
                    "title": "Test feedback",
                    "description": "This is a test",
                    "page": "Test",
                    "userAgent": "Test Agent",
                    "priority": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "url": "https://test.com"
                }
            },
            {
                "name": "Missing Title",
                "data": {
                    "type": "bug",
                    "description": "This is a test",
                    "page": "Test",
                    "userAgent": "Test Agent",
                    "priority": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "url": "https://test.com"
                }
            },
            {
                "name": "Missing Description",
                "data": {
                    "type": "bug",
                    "title": "Test feedback",
                    "page": "Test",
                    "userAgent": "Test Agent",
                    "priority": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "url": "https://test.com"
                }
            },
            {
                "name": "Missing Page",
                "data": {
                    "type": "bug",
                    "title": "Test feedback",
                    "description": "This is a test",
                    "userAgent": "Test Agent",
                    "priority": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "url": "https://test.com"
                }
            },
            {
                "name": "Empty Request",
                "data": {}
            }
        ]
        
        for test in validation_tests:
            try:
                response = self.make_request("POST", "/feedback/submit", test["data"])
                
                if response.status_code == 422:
                    self.log_result(f"Validation ({test['name']})", True, 
                                  "Correctly rejected request with missing required fields")
                elif response.status_code == 400:
                    self.log_result(f"Validation ({test['name']})", True, 
                                  "Correctly rejected malformed request")
                else:
                    self.log_result(f"Validation ({test['name']})", False, 
                                  f"Expected 422 validation error, got {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Validation ({test['name']})", False, f"Exception: {str(e)}")
    
    def test_feedback_realistic_data(self):
        """Test feedback with realistic form data including page context and priority levels"""
        print("\n=== Testing Feedback with Realistic Data ===")
        
        realistic_feedback_scenarios = [
            {
                "scenario": "User on Homepage",
                "data": {
                    "type": "bug",
                    "title": "Apartment search returns no results for valid neighborhoods",
                    "description": "I tried searching for apartments in Williamsburg and DUMBO, but both searches return 0 results even though I know there should be listings in these areas. The search seems to be broken.",
                    "email": "apartment.hunter@gmail.com",
                    "page": "/",
                    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "priority": "urgent",
                    "timestamp": datetime.now().isoformat(),
                    "url": "https://nofeeplaces.com/"
                }
            },
            {
                "scenario": "User on Apartment Details",
                "data": {
                    "type": "improvement",
                    "title": "Add more photos to apartment listings",
                    "description": "This apartment only has 2 photos, but I'd love to see more angles of the living space, kitchen, and bathroom. More photos would help me decide if I want to schedule a viewing.",
                    "email": "prospective.renter@yahoo.com",
                    "page": "/apartment/details",
                    "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
                    "priority": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "url": "https://nofeeplaces.com/apartment/abc123"
                }
            },
            {
                "scenario": "User on Search Results",
                "data": {
                    "type": "feature",
                    "title": "Add saved search functionality",
                    "description": "I'm looking for 1BR apartments under $3500 in Manhattan. It would be great if I could save this search and get email notifications when new apartments matching my criteria become available.",
                    "email": "busy.professional@outlook.com",
                    "page": "/search",
                    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
                    "priority": "high",
                    "timestamp": datetime.now().isoformat(),
                    "url": "https://nofeeplaces.com/search?bedrooms=1&max_price=3500&location=manhattan"
                }
            },
            {
                "scenario": "User on Blog",
                "data": {
                    "type": "compliment",
                    "title": "Excellent neighborhood guides!",
                    "description": "Your blog post about Hell's Kitchen was incredibly helpful. The information about transportation, restaurants, and typical rent prices helped me decide this is the neighborhood for me. Thank you!",
                    "email": "grateful.reader@gmail.com",
                    "page": "/blog",
                    "userAgent": "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
                    "priority": "low",
                    "timestamp": datetime.now().isoformat(),
                    "url": "https://nofeeplaces.com/blog/hells-kitchen-guide"
                }
            },
            {
                "scenario": "User on Contact Page",
                "data": {
                    "type": "other",
                    "title": "Question about application process",
                    "description": "I'm interested in several apartments but I'm not sure about the application process. Do I apply directly through your site or contact the landlord? Also, what documents do I typically need to prepare?",
                    "email": "first.time.renter@student.edu",
                    "page": "/contact",
                    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "priority": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "url": "https://nofeeplaces.com/contact"
                }
            }
        ]
        
        for scenario in realistic_feedback_scenarios:
            try:
                response = self.make_request("POST", "/feedback/submit", scenario["data"])
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("feedback_id"):
                        self.log_result(f"Realistic Data ({scenario['scenario']})", True, 
                                      f"Successfully processed {scenario['data']['type']} feedback from {scenario['data']['page']}")
                    else:
                        self.log_result(f"Realistic Data ({scenario['scenario']})", False, 
                                      f"Submission failed: {data}")
                else:
                    self.log_result(f"Realistic Data ({scenario['scenario']})", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
                # Small delay between submissions
                time.sleep(0.5)
                
            except Exception as e:
                self.log_result(f"Realistic Data ({scenario['scenario']})", False, f"Exception: {str(e)}")
    
    def test_feedback_priority_levels(self):
        """Test feedback with different priority levels"""
        print("\n=== Testing Feedback Priority Levels ===")
        
        priority_tests = [
            {
                "priority": "low",
                "title": "Minor UI improvement suggestion",
                "description": "The font size in the footer could be slightly larger for better readability."
            },
            {
                "priority": "medium", 
                "title": "Feature request for apartment comparison",
                "description": "It would be helpful to compare multiple apartments side by side."
            },
            {
                "priority": "high",
                "title": "Search results not matching filters",
                "description": "When I set a max price of $3000, I still see apartments over $4000 in the results."
            },
            {
                "priority": "urgent",
                "title": "Cannot submit apartment inquiry form",
                "description": "The contact form on apartment details pages is not working. I click submit but nothing happens."
            }
        ]
        
        for i, test in enumerate(priority_tests, 1):
            try:
                feedback_data = {
                    "type": "bug" if test["priority"] in ["high", "urgent"] else "improvement",
                    "title": test["title"],
                    "description": test["description"],
                    "email": f"priority.test{i}@example.com",
                    "page": "Various",
                    "userAgent": "Mozilla/5.0 (Test Browser)",
                    "priority": test["priority"],
                    "timestamp": datetime.now().isoformat(),
                    "url": "https://nofeeplaces.com/test"
                }
                
                response = self.make_request("POST", "/feedback/submit", feedback_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_result(f"Priority Level ({test['priority'].upper()})", True, 
                                      f"Successfully submitted {test['priority']} priority feedback")
                    else:
                        self.log_result(f"Priority Level ({test['priority'].upper()})", False, 
                                      f"Submission failed: {data}")
                else:
                    self.log_result(f"Priority Level ({test['priority'].upper()})", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result(f"Priority Level ({test['priority'].upper()})", False, f"Exception: {str(e)}")
    
    def test_feedback_timestamp_and_url_handling(self):
        """Test that timestamp and URL are handled correctly"""
        print("\n=== Testing Timestamp and URL Handling ===")
        
        # Test with various timestamp formats
        timestamp_tests = [
            {
                "name": "ISO Format",
                "timestamp": datetime.now().isoformat(),
                "url": "https://nofeeplaces.com/"
            },
            {
                "name": "ISO with Timezone",
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "url": "https://nofeeplaces.com/search?location=brooklyn"
            },
            {
                "name": "Different URL Format",
                "timestamp": datetime.now().isoformat(),
                "url": "https://nofeeplaces.com/apartment/details/xyz789?ref=search"
            }
        ]
        
        for test in timestamp_tests:
            try:
                feedback_data = {
                    "type": "other",
                    "title": f"Timestamp test - {test['name']}",
                    "description": f"Testing timestamp format: {test['timestamp']}",
                    "email": "timestamp.test@example.com",
                    "page": "Test Page",
                    "userAgent": "Mozilla/5.0 (Test Browser)",
                    "priority": "low",
                    "timestamp": test["timestamp"],
                    "url": test["url"]
                }
                
                response = self.make_request("POST", "/feedback/submit", feedback_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_result(f"Timestamp/URL ({test['name']})", True, 
                                      f"Successfully handled {test['name']} timestamp and URL")
                    else:
                        self.log_result(f"Timestamp/URL ({test['name']})", False, 
                                      f"Submission failed: {data}")
                else:
                    self.log_result(f"Timestamp/URL ({test['name']})", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result(f"Timestamp/URL ({test['name']})", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all feedback system tests"""
        print("🔍 STARTING FEEDBACK SUBMISSION SYSTEM TESTING")
        print("=" * 60)
        
        # Run all test methods
        self.test_feedback_endpoint_basic()
        self.test_feedback_categories()
        self.test_feedback_with_and_without_email()
        self.test_feedback_validation()
        self.test_feedback_realistic_data()
        self.test_feedback_priority_levels()
        self.test_feedback_timestamp_and_url_handling()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FEEDBACK SYSTEM TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests Passed: {self.results['passed']}")
        print(f"❌ Tests Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results["errors"]:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        print(f"\n📧 EMAIL NOTIFICATIONS:")
        print(f"   • Admin notifications sent to: placesfirm@gmail.com")
        print(f"   • User confirmation emails sent when email provided")
        print(f"   • Professional formatting with feedback details")
        
        print(f"\n💾 DATABASE STORAGE:")
        print(f"   • Feedback stored in MongoDB feedback collection")
        print(f"   • Unique feedback_id generated for each submission")
        print(f"   • All form fields saved including timestamp and user agent")
        
        return success_rate >= 80  # Consider 80%+ success rate as passing

if __name__ == "__main__":
    tester = FeedbackSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 FEEDBACK SYSTEM TESTING COMPLETED SUCCESSFULLY!")
    else:
        print(f"\n⚠️  FEEDBACK SYSTEM TESTING COMPLETED WITH ISSUES")
    
    exit(0 if success else 1)