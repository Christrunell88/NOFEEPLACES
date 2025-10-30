#!/usr/bin/env python3
"""
NoFeePlaces.com Comprehensive Backend API Testing Suite
Post-GitHub Pull Verification - Testing all functionality after code pull and database population
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration from frontend/.env
BASE_URL = "https://renteasy-nyc.preview.emergentagent.com/api"
ADMIN_EMAIL = "placesfirm@gmail.com"
ADMIN_PASSWORD = "Checkers080/?"

class NoFeePlacesGitHubVerificationTester:
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
                response = requests.get(url, headers=default_headers, params=data, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_health_and_basic_endpoints(self):
        """Test health check and basic endpoints"""
        print("\n=== 1. HEALTH & BASIC ENDPOINTS ===")
        
        # Test health endpoint
        try:
            response = self.make_request("GET", "/health")
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_result("Health Check", True, "Backend is responsive and healthy")
                else:
                    self.log_result("Health Check", False, f"Unexpected health response: {data}")
            else:
                self.log_result("Health Check", False, f"Health check failed: {response.status_code}")
        except Exception as e:
            self.log_result("Health Check", False, f"Health check exception: {str(e)}")
        
        # Test root endpoint availability
        try:
            response = self.make_request("GET", "")
            if response.status_code in [200, 404]:  # 404 is acceptable for root
                self.log_result("Root Endpoint", True, f"Root endpoint accessible (status: {response.status_code})")
            else:
                self.log_result("Root Endpoint", False, f"Root endpoint issue: {response.status_code}")
        except Exception as e:
            self.log_result("Root Endpoint", False, f"Root endpoint exception: {str(e)}")
    
    def test_apartments_api(self):
        """Test apartments API endpoints - expecting 33 apartments"""
        print("\n=== 2. APARTMENTS API (PRIORITY) ===")
        
        # Test GET /api/apartments (should return 33 apartments)
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code == 200:
                data = response.json()
                
                # Check if response is ApartmentListResponse format
                if isinstance(data, dict) and "apartments" in data:
                    apartments = data["apartments"]
                    total = data.get("total", len(apartments))
                    
                    if total == 33:
                        self.log_result("Apartments Count (33 Expected)", True, f"Found exactly 33 apartments as expected")
                    else:
                        self.log_result("Apartments Count (33 Expected)", False, f"Found {total} apartments, expected 33")
                    
                    # Verify apartment data structure
                    if apartments:
                        sample_apt = apartments[0]
                        required_fields = ["id", "title", "price", "location", "bedrooms", "bathrooms", "images", "contact_email", "contact_phone"]
                        missing_fields = [field for field in required_fields if field not in sample_apt]
                        
                        if not missing_fields:
                            self.log_result("Apartment Data Structure", True, "All required fields present")
                        else:
                            self.log_result("Apartment Data Structure", False, f"Missing fields: {missing_fields}")
                        
                        # Verify contact info
                        contact_email = sample_apt.get("contact_email")
                        contact_phone = sample_apt.get("contact_phone")
                        
                        if contact_email == "placesfirm@gmail.com" and contact_phone == "+1-646-408-8048":
                            self.log_result("Contact Information", True, "Correct contact info in apartments")
                        else:
                            self.log_result("Contact Information", False, f"Incorrect contact: {contact_email}, {contact_phone}")
                
                elif isinstance(data, list):
                    # Legacy format
                    if len(data) == 33:
                        self.log_result("Apartments Count (33 Expected)", True, f"Found exactly 33 apartments as expected")
                    else:
                        self.log_result("Apartments Count (33 Expected)", False, f"Found {len(data)} apartments, expected 33")
                else:
                    self.log_result("Apartments API Format", False, f"Unexpected response format: {type(data)}")
            else:
                self.log_result("Apartments API", False, f"Failed to get apartments: {response.status_code}")
        except Exception as e:
            self.log_result("Apartments API", False, f"Exception: {str(e)}")
        
        # Test GET /api/apartments/{id} with valid apartment ID
        try:
            # First get an apartment ID
            response = self.make_request("GET", "/apartments", {"limit": 1})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                if apartments:
                    apt_id = apartments[0]["id"]
                    
                    # Test individual apartment endpoint
                    detail_response = self.make_request("GET", f"/apartments/{apt_id}")
                    if detail_response.status_code == 200:
                        apt_data = detail_response.json()
                        if apt_data.get("id") == apt_id:
                            self.log_result("Individual Apartment Details", True, f"Retrieved apartment: {apt_data.get('title', 'Unknown')}")
                        else:
                            self.log_result("Individual Apartment Details", False, "ID mismatch in response")
                    else:
                        self.log_result("Individual Apartment Details", False, f"Failed: {detail_response.status_code}")
                else:
                    self.log_result("Individual Apartment Details", False, "No apartments available for testing")
        except Exception as e:
            self.log_result("Individual Apartment Details", False, f"Exception: {str(e)}")
        
        # Test GET /api/apartments/search/stats
        try:
            response = self.make_request("GET", "/apartments/search/stats")
            if response.status_code == 200:
                stats = response.json()
                total_apartments = stats.get("total_apartments", 0)
                
                if total_apartments == 33:
                    self.log_result("Search Stats (33 Expected)", True, f"Stats show 33 apartments correctly")
                else:
                    self.log_result("Search Stats (33 Expected)", False, f"Stats show {total_apartments} apartments, expected 33")
            else:
                self.log_result("Search Stats", False, f"Stats endpoint failed: {response.status_code}")
        except Exception as e:
            self.log_result("Search Stats", False, f"Exception: {str(e)}")
        
        # Test search functionality with filters
        try:
            # Test neighborhood filter
            response = self.make_request("GET", "/apartments", {"neighborhood": "Manhattan", "limit": 20})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                self.log_result("Neighborhood Search", True, f"Manhattan search returned {len(apartments)} apartments")
            else:
                self.log_result("Neighborhood Search", False, f"Failed: {response.status_code}")
            
            # Test price range filter
            response = self.make_request("GET", "/apartments", {"min_price": 3000, "max_price": 8000, "limit": 20})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                self.log_result("Price Range Filter", True, f"Price filter returned {len(apartments)} apartments")
            else:
                self.log_result("Price Range Filter", False, f"Failed: {response.status_code}")
            
            # Test bedrooms filter
            response = self.make_request("GET", "/apartments", {"bedrooms": 1, "limit": 20})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                self.log_result("Bedrooms Filter", True, f"1BR filter returned {len(apartments)} apartments")
            else:
                self.log_result("Bedrooms Filter", False, f"Failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Search Functionality", False, f"Exception: {str(e)}")
        
        # Verify data integrity - price ranges and boroughs
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                if apartments:
                    prices = [apt.get("price", 0) for apt in apartments if apt.get("price")]
                    boroughs = set([apt.get("borough", apt.get("location", "")).split(",")[-1].strip() for apt in apartments])
                    
                    min_price = min(prices) if prices else 0
                    max_price = max(prices) if prices else 0
                    
                    # Check if price range is realistic ($2,163 - $17,100 as mentioned)
                    if 2000 <= min_price <= 3000 and 15000 <= max_price <= 20000:
                        self.log_result("Price Range Validation", True, f"Realistic prices: ${min_price:,.0f} - ${max_price:,.0f}")
                    else:
                        self.log_result("Price Range Validation", False, f"Unusual price range: ${min_price:,.0f} - ${max_price:,.0f}")
                    
                    # Check for 4 boroughs (Manhattan, Brooklyn, Queens, Bronx)
                    expected_boroughs = {"Manhattan", "Brooklyn", "Queens", "Bronx"}
                    found_boroughs = {b for b in boroughs if b in expected_boroughs}
                    
                    if len(found_boroughs) >= 3:  # At least 3 of 4 boroughs
                        self.log_result("Borough Distribution", True, f"Found apartments in: {', '.join(found_boroughs)}")
                    else:
                        self.log_result("Borough Distribution", False, f"Limited borough coverage: {', '.join(found_boroughs)}")
                        
        except Exception as e:
            self.log_result("Data Integrity Check", False, f"Exception: {str(e)}")
    
    def test_admin_api(self):
        """Test admin API endpoints"""
        print("\n=== 3. ADMIN API ===")
        
        # Test admin login
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.make_request("POST", "/admin/login", login_data)
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.admin_token = data["token"]
                    self.log_result("Admin Login", True, f"Successfully logged in as {ADMIN_EMAIL}")
                elif "access_token" in data:
                    self.admin_token = data["access_token"]
                    self.log_result("Admin Login", True, f"Successfully logged in as {ADMIN_EMAIL}")
                else:
                    self.log_result("Admin Login", False, f"No access token in response: {data}")
            else:
                self.log_result("Admin Login", False, f"Login failed: {response.status_code}")
        except Exception as e:
            self.log_result("Admin Login", False, f"Exception: {str(e)}")
        
        if not self.admin_token:
            self.log_result("Admin API Tests", False, "Cannot test admin endpoints without token")
            return
        
        # Test admin endpoints with JWT token
        admin_endpoints = [
            ("/admin/apartments", "Admin Apartments"),
            ("/admin/users", "Admin Users"),
            ("/admin/feedback", "Admin Feedback"),
            ("/admin/newsletter", "Admin Newsletter"),
            ("/admin/analytics", "Admin Analytics")
        ]
        
        for endpoint, test_name in admin_endpoints:
            try:
                response = self.make_request("GET", endpoint)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(test_name, True, f"Endpoint accessible, returned data")
                else:
                    self.log_result(test_name, False, f"Failed: {response.status_code}")
            except Exception as e:
                self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def test_blog_api(self):
        """Test blog API endpoints - expecting 5 blog posts"""
        print("\n=== 4. BLOG API ===")
        
        # Test GET /api/blog (should return 5 blog posts)
        try:
            response = self.make_request("GET", "/blog")
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and "posts" in data:
                    posts = data["posts"]
                    total = data.get("total", len(posts))
                    
                    if total == 5:
                        self.log_result("Blog Posts Count (5 Expected)", True, f"Found exactly 5 blog posts as expected")
                    else:
                        self.log_result("Blog Posts Count (5 Expected)", False, f"Found {total} posts, expected 5")
                    
                    # Verify blog post structure
                    if posts:
                        sample_post = posts[0]
                        required_fields = ["id", "title", "slug", "excerpt", "content", "author", "category"]
                        missing_fields = [field for field in required_fields if field not in sample_post]
                        
                        if not missing_fields:
                            self.log_result("Blog Post Structure", True, "All required fields present")
                        else:
                            self.log_result("Blog Post Structure", False, f"Missing fields: {missing_fields}")
                
                elif isinstance(data, list):
                    if len(data) == 5:
                        self.log_result("Blog Posts Count (5 Expected)", True, f"Found exactly 5 blog posts as expected")
                    else:
                        self.log_result("Blog Posts Count (5 Expected)", False, f"Found {len(data)} posts, expected 5")
                else:
                    self.log_result("Blog API Format", False, f"Unexpected response format: {type(data)}")
            else:
                self.log_result("Blog API", False, f"Failed to get blog posts: {response.status_code}")
        except Exception as e:
            self.log_result("Blog API", False, f"Exception: {str(e)}")
        
        # Test GET /api/blog/{slug} with valid blog post slug
        try:
            # First get a blog post slug
            response = self.make_request("GET", "/blog", {"limit": 1})
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", data) if isinstance(data, dict) else data
                
                if posts:
                    slug = posts[0]["slug"]
                    
                    # Test individual blog post endpoint
                    post_response = self.make_request("GET", f"/blog/{slug}")
                    if post_response.status_code == 200:
                        post_data = post_response.json()
                        if post_data.get("slug") == slug:
                            self.log_result("Individual Blog Post", True, f"Retrieved post: {post_data.get('title', 'Unknown')}")
                        else:
                            self.log_result("Individual Blog Post", False, "Slug mismatch in response")
                    else:
                        self.log_result("Individual Blog Post", False, f"Failed: {post_response.status_code}")
                else:
                    self.log_result("Individual Blog Post", False, "No blog posts available for testing")
        except Exception as e:
            self.log_result("Individual Blog Post", False, f"Exception: {str(e)}")
    
    def test_contact_and_newsletter(self):
        """Test contact and newsletter endpoints"""
        print("\n=== 5. CONTACT & NEWSLETTER ===")
        
        # Test contact form submission
        try:
            contact_data = {
                "name": "Test User",
                "email": "test@example.com",
                "phone": "+1-555-123-4567",
                "message": "This is a test contact form submission from backend testing.",
                "preferred_contact": "email"
            }
            
            response = self.make_request("POST", "/contact", contact_data)
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "contact_id" in data:
                    self.log_result("Contact Form Submission", True, "Contact form submitted successfully")
                else:
                    self.log_result("Contact Form Submission", False, f"Unexpected response: {data}")
            else:
                self.log_result("Contact Form Submission", False, f"Failed: {response.status_code}")
        except Exception as e:
            self.log_result("Contact Form Submission", False, f"Exception: {str(e)}")
        
        # Test newsletter subscription
        try:
            newsletter_data = {
                "email": "newsletter.test@example.com",
                "name": "Newsletter Test User",
                "interests": ["Manhattan", "1BR"]
            }
            
            response = self.make_request("POST", "/newsletter/subscribe", newsletter_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("Newsletter Subscription", True, "Newsletter subscription successful")
                else:
                    self.log_result("Newsletter Subscription", False, f"Subscription failed: {data.get('message')}")
            else:
                self.log_result("Newsletter Subscription", False, f"Failed: {response.status_code}")
        except Exception as e:
            self.log_result("Newsletter Subscription", False, f"Exception: {str(e)}")
        
        # Test email service integration (contact email endpoint)
        try:
            email_data = {
                "to": "placesfirm@gmail.com",
                "subject": "Backend Test Email",
                "sender_name": "Backend Tester",
                "sender_email": "backend.test@example.com",
                "message": "This is a test email from the backend testing suite.",
                "apartment_details": {
                    "title": "Test Apartment",
                    "price": 3500,
                    "neighborhood": "Test Neighborhood"
                }
            }
            
            response = self.make_request("POST", "/send-contact-email", email_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("Email Service Integration", True, "Email sent successfully")
                else:
                    self.log_result("Email Service Integration", False, f"Email failed: {data.get('message')}")
            else:
                self.log_result("Email Service Integration", False, f"Failed: {response.status_code}")
        except Exception as e:
            self.log_result("Email Service Integration", False, f"Exception: {str(e)}")
    
    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n=== 6. AUTHENTICATION ===")
        
        # Test JWT token validation
        try:
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token_here"}
            response = self.make_request("GET", "/auth/me", headers=invalid_headers)
            if response.status_code == 401:
                self.log_result("JWT Token Validation (Invalid)", True, "Invalid token properly rejected")
            else:
                self.log_result("JWT Token Validation (Invalid)", False, f"Invalid token not rejected: {response.status_code}")
        except Exception as e:
            self.log_result("JWT Token Validation", False, f"Exception: {str(e)}")
        
        # Test social auth endpoints exist
        social_endpoints = [
            ("/auth/facebook", "Facebook Auth Endpoint"),
            ("/auth/apple", "Apple Auth Endpoint"),
            ("/auth/me", "User Info Endpoint")
        ]
        
        for endpoint, test_name in social_endpoints:
            try:
                # Test with missing data (should return 400 or 422, not 500)
                response = self.make_request("POST", endpoint, {})
                if response.status_code in [400, 401, 422]:
                    self.log_result(f"{test_name} Exists", True, f"Endpoint exists and handles invalid requests properly")
                elif response.status_code == 500:
                    self.log_result(f"{test_name} Exists", False, f"Endpoint returns 500 error")
                else:
                    self.log_result(f"{test_name} Exists", True, f"Endpoint exists (status: {response.status_code})")
            except Exception as e:
                self.log_result(f"{test_name} Exists", False, f"Exception: {str(e)}")
    
    def test_data_integrity(self):
        """Test data integrity across the system"""
        print("\n=== 7. DATA INTEGRITY ===")
        
        # Verify all 33 apartments have required fields
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                if apartments:
                    complete_apartments = 0
                    for apt in apartments:
                        required_fields = ["id", "title", "price", "location", "bedrooms", "bathrooms"]
                        if all(field in apt and apt[field] is not None for field in required_fields):
                            complete_apartments += 1
                    
                    completion_rate = (complete_apartments / len(apartments)) * 100
                    if completion_rate >= 90:
                        self.log_result("Apartment Data Completeness", True, f"{completion_rate:.1f}% of apartments have complete data")
                    else:
                        self.log_result("Apartment Data Completeness", False, f"Only {completion_rate:.1f}% of apartments have complete data")
                        
                    # Check contact info consistency
                    correct_contact = 0
                    for apt in apartments:
                        if (apt.get("contact_email") == "placesfirm@gmail.com" and 
                            apt.get("contact_phone") == "+1-646-408-8048"):
                            correct_contact += 1
                    
                    contact_rate = (correct_contact / len(apartments)) * 100
                    if contact_rate >= 95:
                        self.log_result("Contact Info Consistency", True, f"{contact_rate:.1f}% have correct contact info")
                    else:
                        self.log_result("Contact Info Consistency", False, f"Only {contact_rate:.1f}% have correct contact info")
                        
                    # Check image URLs validity
                    valid_images = 0
                    total_images = 0
                    for apt in apartments:
                        images = apt.get("images", [])
                        for img_url in images:
                            total_images += 1
                            if isinstance(img_url, str) and (img_url.startswith("http://") or img_url.startswith("https://")):
                                valid_images += 1
                    
                    if total_images > 0:
                        image_validity_rate = (valid_images / total_images) * 100
                        if image_validity_rate >= 95:
                            self.log_result("Image URL Validity", True, f"{image_validity_rate:.1f}% of image URLs are valid")
                        else:
                            self.log_result("Image URL Validity", False, f"Only {image_validity_rate:.1f}% of image URLs are valid")
                    else:
                        self.log_result("Image URL Validity", False, "No images found to validate")
                        
        except Exception as e:
            self.log_result("Data Integrity Check", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 STARTING COMPREHENSIVE BACKEND VERIFICATION")
        print("=" * 60)
        print(f"Testing backend at: {self.base_url}")
        print(f"Admin credentials: {ADMIN_EMAIL}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_health_and_basic_endpoints()
        self.test_apartments_api()
        self.test_admin_api()
        self.test_blog_api()
        self.test_contact_and_newsletter()
        self.test_authentication()
        self.test_data_integrity()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 COMPREHENSIVE BACKEND VERIFICATION COMPLETE")
        print("=" * 60)
        print(f"⏱️  Total test duration: {duration:.2f} seconds")
        print(f"✅ Tests passed: {self.results['passed']}")
        print(f"❌ Tests failed: {self.results['failed']}")
        print(f"📊 Success rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print("\n" + "=" * 60)
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = NoFeePlacesGitHubVerificationTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED - Backend is fully functional!")
        exit(0)
    else:
        print("⚠️  SOME TESTS FAILED - Check the results above")
        exit(1)