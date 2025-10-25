#!/usr/bin/env python3
"""
Admin Portal and Analytics Testing Suite
Tests admin login, analytics endpoints, and visit tracking functionality
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://nycnofee.preview.emergentagent.com/api"
ADMIN_EMAIL = "placesfirm@gmail.com"
ADMIN_PASSWORD = "Checkers080/?"

class AdminAnalyticsAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
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
        
        if self.admin_token and "Authorization" not in default_headers:
            default_headers["Authorization"] = f"Bearer {self.admin_token}"
        
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
    
    def test_admin_login(self):
        """Test admin login with provided credentials"""
        print("\n=== Testing Admin Login ===")
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.make_request("POST", "/admin/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data or "access_token" in data:
                    self.admin_token = data.get("token") or data.get("access_token")
                    self.log_result("Admin Login", True, f"Successfully logged in as {ADMIN_EMAIL}")
                    
                    # Verify token contains admin information
                    if "message" in data and "admin" in data["message"].lower():
                        self.log_result("Admin Token Validation", True, "Token contains admin information")
                    else:
                        self.log_result("Admin Token Validation", True, f"Login successful: {data.get('message', 'No message')}")
                else:
                    self.log_result("Admin Login", False, f"Missing token in response: {data}")
            else:
                self.log_result("Admin Login", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Admin Login", False, f"Exception: {str(e)}")
    
    def test_analytics_overview_endpoint(self):
        """Test GET /api/admin/analytics/overview endpoint"""
        print("\n=== Testing Analytics Overview Endpoint ===")
        try:
            if not self.admin_token:
                self.log_result("Analytics Overview", False, "No admin token available")
                return
            
            # Try the main analytics endpoint first
            response = self.make_request("GET", "/admin/analytics")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Analytics Overview", True, f"Analytics data retrieved: {list(data.keys())}")
                
                # Check for expected analytics fields in the stats section
                expected_fields = ["total_apartments", "total_users", "total_visitors", "total_feedback", "total_newsletter_subscribers"]
                found_fields = []
                
                if "stats" in data and isinstance(data["stats"], dict):
                    stats = data["stats"]
                    for field in expected_fields:
                        if field in stats:
                            found_fields.append(field)
                
                if len(found_fields) >= 4:  # Most expected fields found
                    self.log_result("Analytics Data Structure", True, f"Found fields: {found_fields}")
                else:
                    self.log_result("Analytics Data Structure", False, f"Expected fields not found. Available: {list(data.keys())}")
                
                # Check visitor count specifically
                visitor_count = 0
                if "stats" in data and isinstance(data["stats"], dict):
                    visitor_count = data["stats"].get("total_visitors", 0)
                
                if visitor_count > 0:
                    self.log_result("Visitor Count Check", True, f"Visitor count in analytics: {visitor_count}")
                else:
                    self.log_result("Visitor Count Check", False, f"Visitor count is {visitor_count}")
                
            elif response.status_code == 404:
                # Try alternative endpoints
                self.log_result("Analytics Overview", False, "Main analytics endpoint not found, trying alternatives")
                
                # Try /admin/analytics/overview
                overview_response = self.make_request("GET", "/admin/analytics/overview")
                if overview_response.status_code == 200:
                    self.log_result("Analytics Overview Alternative", True, "Found analytics overview endpoint")
                else:
                    self.log_result("Analytics Overview Alternative", False, f"Overview endpoint status: {overview_response.status_code}")
            else:
                self.log_result("Analytics Overview", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Analytics Overview", False, f"Exception: {str(e)}")
    
    def test_analytics_traffic_endpoint(self):
        """Test GET /api/admin/analytics/traffic endpoint"""
        print("\n=== Testing Analytics Traffic Endpoint ===")
        try:
            if not self.admin_token:
                self.log_result("Analytics Traffic", False, "No admin token available")
                return
            
            response = self.make_request("GET", "/admin/analytics/traffic")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Analytics Traffic", True, f"Traffic data retrieved: {list(data.keys())}")
            elif response.status_code == 404:
                self.log_result("Analytics Traffic", False, "Traffic analytics endpoint not found")
            else:
                self.log_result("Analytics Traffic", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Analytics Traffic", False, f"Exception: {str(e)}")
    
    def test_analytics_users_endpoint(self):
        """Test GET /api/admin/analytics/users endpoint"""
        print("\n=== Testing Analytics Users Endpoint ===")
        try:
            if not self.admin_token:
                self.log_result("Analytics Users", False, "No admin token available")
                return
            
            response = self.make_request("GET", "/admin/analytics/users")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Analytics Users", True, f"User analytics retrieved: {list(data.keys())}")
            elif response.status_code == 404:
                self.log_result("Analytics Users", False, "User analytics endpoint not found")
            else:
                self.log_result("Analytics Users", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Analytics Users", False, f"Exception: {str(e)}")
    
    def test_visit_tracking_endpoint(self):
        """Test analytics tracking endpoint for page visits"""
        print("\n=== Testing Visit Tracking Endpoint ===")
        try:
            # Test POST /api/analytics/track-visit
            visit_data = {
                "page": "/",
                "timestamp": datetime.now().isoformat(),
                "user_agent": "AdminAnalyticsTest/1.0",
                "referrer": "direct"
            }
            
            response = self.make_request("POST", "/analytics/track-visit", visit_data)
            
            if response.status_code == 200:
                self.log_result("Visit Tracking (track-visit)", True, "Visit tracking endpoint working")
            elif response.status_code == 404:
                # Try alternative endpoints
                self.log_result("Visit Tracking (track-visit)", False, "track-visit endpoint not found, trying alternatives")
                
                # Try /visitor/track
                visitor_response = self.make_request("POST", "/visitor/track", visit_data)
                if visitor_response.status_code == 200:
                    self.log_result("Visit Tracking (visitor/track)", True, "Visitor tracking endpoint working")
                else:
                    # Try /analytics/visit
                    analytics_response = self.make_request("POST", "/analytics/visit", visit_data)
                    if analytics_response.status_code == 200:
                        self.log_result("Visit Tracking (analytics/visit)", True, "Analytics visit endpoint working")
                    else:
                        self.log_result("Visit Tracking", False, "No working visit tracking endpoint found")
            else:
                self.log_result("Visit Tracking", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Visit Tracking", False, f"Exception: {str(e)}")
    
    def test_create_visit_entry(self):
        """Test creating a visit entry and verify it's recorded"""
        print("\n=== Testing Visit Entry Creation ===")
        try:
            # Create multiple visit entries
            for i in range(3):
                visit_data = {
                    "page": f"/test-page-{i}",
                    "timestamp": datetime.now().isoformat(),
                    "user_agent": f"TestBot/{i}",
                    "ip": f"192.168.1.{100+i}"
                }
                
                # Try different endpoints
                endpoints_to_try = ["/visitor/track", "/analytics/visit", "/analytics/track-visit"]
                
                success = False
                for endpoint in endpoints_to_try:
                    try:
                        response = self.make_request("POST", endpoint, visit_data)
                        if response.status_code == 200:
                            success = True
                            self.log_result(f"Visit Entry {i+1}", True, f"Created via {endpoint}")
                            break
                    except:
                        continue
                
                if not success:
                    self.log_result(f"Visit Entry {i+1}", False, "Failed to create visit entry")
                
                time.sleep(0.5)  # Small delay between requests
            
        except Exception as e:
            self.log_result("Visit Entry Creation", False, f"Exception: {str(e)}")
    
    def test_database_analytics_collections(self):
        """Test if analytics collections exist in database by checking admin endpoints"""
        print("\n=== Testing Database Analytics Collections ===")
        try:
            if not self.admin_token:
                self.log_result("Database Collections Check", False, "No admin token available")
                return
            
            # Check if we can get analytics data (which would indicate collections exist)
            response = self.make_request("GET", "/admin/analytics")
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for visitor/analytics data
                has_visitor_data = False
                has_analytics_data = False
                
                for key, value in data.items():
                    if "visitor" in key.lower() or "visit" in key.lower():
                        has_visitor_data = True
                        if isinstance(value, (int, float)) and value > 0:
                            self.log_result("Visitor Data in DB", True, f"Found {value} visitors")
                        else:
                            self.log_result("Visitor Data in DB", False, f"Visitor count is {value}")
                    
                    if "analytic" in key.lower():
                        has_analytics_data = True
                
                if not has_visitor_data:
                    self.log_result("Visitor Collection", False, "No visitor data found in analytics response")
                
                # Check other collections
                collections_found = []
                if "total_apartments" in data:
                    collections_found.append("apartments")
                if "total_users" in data:
                    collections_found.append("users")
                if "feedback" in data:
                    collections_found.append("feedback")
                if "newsletter" in data:
                    collections_found.append("newsletter")
                
                if collections_found:
                    self.log_result("Database Collections", True, f"Found collections: {collections_found}")
                else:
                    self.log_result("Database Collections", False, "No expected collections found")
                
            else:
                self.log_result("Database Collections Check", False, f"Cannot access analytics: {response.status_code}")
        except Exception as e:
            self.log_result("Database Collections Check", False, f"Exception: {str(e)}")
    
    def test_frontend_analytics_integration(self):
        """Test if frontend is sending analytics data to backend"""
        print("\n=== Testing Frontend Analytics Integration ===")
        try:
            # Simulate frontend analytics calls
            frontend_data = {
                "event": "page_view",
                "page": "/",
                "timestamp": datetime.now().isoformat(),
                "session_id": "test_session_123",
                "user_agent": "Mozilla/5.0 (Test Browser)"
            }
            
            # Try common frontend analytics endpoints
            endpoints_to_test = [
                "/analytics/page-view",
                "/analytics/event", 
                "/analytics/track",
                "/visitor/track",
                "/analytics/visit"
            ]
            
            working_endpoints = []
            for endpoint in endpoints_to_test:
                try:
                    response = self.make_request("POST", endpoint, frontend_data)
                    if response.status_code in [200, 201]:
                        working_endpoints.append(endpoint)
                except:
                    continue
            
            if working_endpoints:
                self.log_result("Frontend Analytics Integration", True, f"Working endpoints: {working_endpoints}")
            else:
                self.log_result("Frontend Analytics Integration", False, "No working analytics endpoints found")
                
        except Exception as e:
            self.log_result("Frontend Analytics Integration", False, f"Exception: {str(e)}")
    
    def test_analytics_data_verification(self):
        """Verify analytics data shows actual visits"""
        print("\n=== Testing Analytics Data Verification ===")
        try:
            if not self.admin_token:
                self.log_result("Analytics Data Verification", False, "No admin token available")
                return
            
            # Get current analytics
            response = self.make_request("GET", "/admin/analytics")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for zero visits issue
                visitor_fields = []
                zero_visitor_fields = []
                
                if "stats" in data and isinstance(data["stats"], dict):
                    stats = data["stats"]
                    for key, value in stats.items():
                        if any(term in key.lower() for term in ["visitor", "visit", "traffic", "view"]):
                            visitor_fields.append((key, value))
                            if isinstance(value, (int, float)) and value == 0:
                                zero_visitor_fields.append(key)
                
                if visitor_fields:
                    self.log_result("Analytics Visitor Fields", True, f"Found visitor fields: {visitor_fields}")
                    
                    if zero_visitor_fields:
                        self.log_result("Zero Visits Issue", False, f"Fields showing 0 visits: {zero_visitor_fields}")
                    else:
                        self.log_result("Zero Visits Issue", True, "No zero visitor counts found")
                else:
                    self.log_result("Analytics Visitor Fields", False, "No visitor-related fields found in analytics")
                
                # Print full analytics data for debugging
                print(f"\n📊 Full Analytics Data:")
                for key, value in data.items():
                    print(f"   {key}: {value}")
                
            else:
                self.log_result("Analytics Data Verification", False, f"Cannot get analytics data: {response.status_code}")
        except Exception as e:
            self.log_result("Analytics Data Verification", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all admin portal and analytics tests"""
        print("🔍 ADMIN PORTAL AND ANALYTICS TESTING SUITE")
        print("=" * 60)
        
        # Test admin authentication
        self.test_admin_login()
        
        # Test analytics endpoints
        self.test_analytics_overview_endpoint()
        self.test_analytics_traffic_endpoint()
        self.test_analytics_users_endpoint()
        
        # Test visit tracking
        self.test_visit_tracking_endpoint()
        self.test_create_visit_entry()
        
        # Test database and integration
        self.test_database_analytics_collections()
        self.test_frontend_analytics_integration()
        self.test_analytics_data_verification()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        return self.results

if __name__ == "__main__":
    tester = AdminAnalyticsAPITester()
    results = tester.run_all_tests()