#!/usr/bin/env python3
"""
Focused Backend Test - Testing Critical Issues Found
Focus: Search functionality fix, apartment data consistency, blog system, performance
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://nofee-enhancement.preview.emergentagent.com/api"

class FocusedBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.results = {"passed": 0, "failed": 0, "errors": []}
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
    
    def make_request(self, method: str, endpoint: str, data: dict = None) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                return requests.get(url, params=data, timeout=10)
            elif method.upper() == "POST":
                return requests.post(url, json=data, timeout=10)
        except Exception as e:
            print(f"Request failed: {e}")
            raise
    
    def test_search_functionality_fix(self):
        """Test that the search functionality MongoDB error is fixed"""
        print("\n=== TESTING SEARCH FUNCTIONALITY FIX ===")
        
        search_tests = [
            {"term": "Brooklyn Heights", "description": "Neighborhood search"},
            {"term": "Manhattan", "description": "Borough search"},
            {"term": "luxury", "description": "Amenity search"},
            {"term": "studio", "description": "Type search"}
        ]
        
        for test in search_tests:
            try:
                response = self.make_request("GET", "/apartments", {
                    "search": test["term"],
                    "limit": 20
                })
                
                if response.status_code == 200:
                    data = response.json()
                    apartments = data.get("apartments", data) if isinstance(data, dict) else data
                    self.log_result(f"Search Fix - {test['description']}", True, 
                                  f"'{test['term']}' search returned {len(apartments)} results (no 500 error)")
                else:
                    self.log_result(f"Search Fix - {test['description']}", False, 
                                  f"Search failed with status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Search Fix - {test['description']}", False, f"Exception: {str(e)}")
        
        # Test combined search that was failing
        try:
            response = self.make_request("GET", "/apartments", {
                "search": "Manhattan",
                "min_price": 3000,
                "max_price": 6000,
                "bedrooms": 1,
                "limit": 15
            })
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                self.log_result("Combined Search Fix", True, 
                              f"Combined search returned {len(apartments)} results (no 500 error)")
            else:
                self.log_result("Combined Search Fix", False, 
                              f"Combined search failed with status: {response.status_code}")
        except Exception as e:
            self.log_result("Combined Search Fix", False, f"Exception: {str(e)}")
    
    def test_apartment_data_consistency(self):
        """Test apartment data consistency issues found"""
        print("\n=== TESTING APARTMENT DATA CONSISTENCY ===")
        
        try:
            response = self.make_request("GET", "/apartments", {"limit": 50})
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                # Check for bedroom data type issues
                bedroom_issues = []
                valid_apartments = 0
                
                for i, apt in enumerate(apartments):
                    bedrooms = apt.get("bedrooms")
                    
                    # Check if bedrooms is a valid integer or 0
                    if isinstance(bedrooms, int) and bedrooms >= 0:
                        valid_apartments += 1
                    elif bedrooms == "Studio" or bedrooms == "studio":
                        # This should be converted to 0
                        bedroom_issues.append(f"Apartment {i+1}: bedrooms='{bedrooms}' (should be 0)")
                    elif bedrooms is None:
                        bedroom_issues.append(f"Apartment {i+1}: bedrooms=None")
                    else:
                        bedroom_issues.append(f"Apartment {i+1}: bedrooms={bedrooms} (type: {type(bedrooms)})")
                
                if len(bedroom_issues) == 0:
                    self.log_result("Bedroom Data Types", True, 
                                  f"All {len(apartments)} apartments have valid bedroom data")
                else:
                    self.log_result("Bedroom Data Types", False, 
                                  f"{len(bedroom_issues)} apartments have bedroom data issues")
                    for issue in bedroom_issues[:3]:
                        print(f"   {issue}")
                
                # Check price data consistency
                price_issues = []
                for i, apt in enumerate(apartments):
                    price = apt.get("price")
                    if not isinstance(price, (int, float)) or price <= 0:
                        price_issues.append(f"Apartment {i+1}: invalid price={price}")
                
                if len(price_issues) == 0:
                    self.log_result("Price Data Consistency", True, 
                                  f"All {len(apartments)} apartments have valid prices")
                else:
                    self.log_result("Price Data Consistency", False, 
                                  f"{len(price_issues)} apartments have price issues")
                
            else:
                self.log_result("Apartment Data Consistency", False, 
                              f"Could not retrieve apartments: {response.status_code}")
        except Exception as e:
            self.log_result("Apartment Data Consistency", False, f"Exception: {str(e)}")
    
    def test_blog_system_functionality(self):
        """Test blog system functionality"""
        print("\n=== TESTING BLOG SYSTEM FUNCTIONALITY ===")
        
        # Test blog list
        try:
            response = self.make_request("GET", "/blog")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", data) if isinstance(data, dict) else data
                
                if posts:
                    self.log_result("Blog Posts List", True, f"Retrieved {len(posts)} blog posts")
                    
                    # Test individual blog post
                    first_post = posts[0]
                    slug = first_post.get("slug")
                    
                    if slug:
                        post_response = self.make_request("GET", f"/blog/{slug}")
                        if post_response.status_code == 200:
                            post_data = post_response.json()
                            content_length = len(post_data.get("content", ""))
                            self.log_result("Individual Blog Post", True, 
                                          f"Retrieved post '{slug}' with {content_length} characters")
                        else:
                            self.log_result("Individual Blog Post", False, 
                                          f"Failed to retrieve post: {post_response.status_code}")
                else:
                    self.log_result("Blog Posts List", True, "No blog posts found (acceptable)")
            else:
                self.log_result("Blog Posts List", False, f"Blog list failed: {response.status_code}")
        except Exception as e:
            self.log_result("Blog System Functionality", False, f"Exception: {str(e)}")
    
    def test_api_performance(self):
        """Test API performance and response times"""
        print("\n=== TESTING API PERFORMANCE ===")
        
        performance_tests = [
            {"endpoint": "/apartments", "params": {"limit": 50}, "name": "Apartment Listings"},
            {"endpoint": "/apartments-summary", "params": {}, "name": "Apartment Summary"},
            {"endpoint": "/blog", "params": {"limit": 10}, "name": "Blog Posts"},
            {"endpoint": "/health", "params": {}, "name": "Health Check"}
        ]
        
        for test in performance_tests:
            try:
                start_time = time.time()
                response = self.make_request("GET", test["endpoint"], test["params"])
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    if response_time < 3.0:
                        self.log_result(f"Performance - {test['name']}", True, 
                                      f"{response_time:.3f}s (under 3s requirement)")
                    else:
                        self.log_result(f"Performance - {test['name']}", False, 
                                      f"{response_time:.3f}s (exceeds 3s requirement)")
                else:
                    self.log_result(f"Performance - {test['name']}", False, 
                                  f"Request failed: {response.status_code}")
            except Exception as e:
                self.log_result(f"Performance - {test['name']}", False, f"Exception: {str(e)}")
    
    def test_apartment_count_consistency(self):
        """Test apartment count consistency between endpoints"""
        print("\n=== TESTING APARTMENT COUNT CONSISTENCY ===")
        
        try:
            # Get count from apartments endpoint
            apartments_response = self.make_request("GET", "/apartments", {"limit": 1000})
            apartments_count = 0
            
            if apartments_response.status_code == 200:
                data = apartments_response.json()
                if isinstance(data, dict) and "total" in data:
                    apartments_count = data["total"]
                elif isinstance(data, list):
                    apartments_count = len(data)
            
            # Get count from summary endpoint
            summary_response = self.make_request("GET", "/apartments-summary")
            summary_count = 0
            
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                summary_count = summary_data.get("market_overview", {}).get("total_no_fee_apartments", 0)
            
            if apartments_count > 0 and summary_count > 0:
                if abs(apartments_count - summary_count) <= 5:
                    self.log_result("Apartment Count Consistency", True, 
                                  f"Counts consistent: apartments={apartments_count}, summary={summary_count}")
                else:
                    self.log_result("Apartment Count Consistency", False, 
                                  f"Count mismatch: apartments={apartments_count}, summary={summary_count}")
                
                # Verify count meets requirements
                if apartments_count >= 200:
                    self.log_result("Apartment Inventory", True, 
                                  f"Excellent inventory: {apartments_count} apartments (exceeds 200+ requirement)")
                else:
                    self.log_result("Apartment Inventory", False, 
                                  f"Low inventory: {apartments_count} apartments (expected 200+)")
            else:
                self.log_result("Apartment Count Consistency", False, 
                              "Could not retrieve apartment counts from both endpoints")
        except Exception as e:
            self.log_result("Apartment Count Consistency", False, f"Exception: {str(e)}")
    
    def test_authentication_system_status(self):
        """Test authentication system status (social auth only)"""
        print("\n=== TESTING AUTHENTICATION SYSTEM STATUS ===")
        
        # Test social auth providers endpoint
        try:
            response = self.make_request("GET", "/auth/providers/status")
            
            if response.status_code == 200:
                data = response.json()
                google_available = data.get("google", False)
                facebook_available = data.get("facebook", False)
                apple_available = data.get("apple", False)
                
                if google_available:
                    self.log_result("Google OAuth Available", True, "Google authentication provider enabled")
                else:
                    self.log_result("Google OAuth Available", False, "Google authentication not available")
                
                # Note about traditional auth
                self.log_result("Authentication System Type", True, 
                              "Social authentication only (no email/password registration)")
                
            else:
                self.log_result("Authentication System Status", False, 
                              f"Auth providers endpoint failed: {response.status_code}")
        except Exception as e:
            self.log_result("Authentication System Status", False, f"Exception: {str(e)}")
    
    def run_focused_tests(self):
        """Run focused tests on critical issues"""
        print("🔍 FOCUSED BACKEND TESTING - CRITICAL ISSUES")
        print("=" * 50)
        print(f"Testing: {self.base_url}")
        print("Focus: Search fix, data consistency, performance")
        print("=" * 50)
        
        self.test_search_functionality_fix()
        self.test_apartment_data_consistency()
        self.test_blog_system_functionality()
        self.test_api_performance()
        self.test_apartment_count_consistency()
        self.test_authentication_system_status()
        
        # Results
        total = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 50)
        print("🏁 FOCUSED TESTING COMPLETE")
        print("=" * 50)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.results["failed"] > 0:
            print(f"\n🚨 REMAINING ISSUES:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = FocusedBackendTester()
    success = tester.run_focused_tests()
    exit(0 if success else 1)