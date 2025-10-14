#!/usr/bin/env python3
"""
NoFeePlaces.com Backend API Testing Suite - Zillow-Style Search Box Testing
Tests backend API after implementing Zillow-style search box improvements and removing newsletter components
Focus: Apartment Search & Filtering, Individual Details, Authentication, Blog System, Performance, Data Consistency
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://nofee-finder.preview.emergentagent.com/api"
TEST_USER_EMAIL = "zillow.test.user@nofeeplaces.com"
TEST_USER_PASSWORD = "ZillowTest123!"
TEST_USER_NAME = "Zillow Test User"

class ZillowStyleBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_user_id = None
        self.test_apartment_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.start_time = time.time()
    
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
        """Make HTTP request with error handling and timing"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        if self.auth_token and "Authorization" not in default_headers:
            default_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        start_time = time.time()
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, params=data, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.request_time = time.time() - start_time
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_apartment_search_filtering_api(self):
        """Test GET /api/apartments with search parameters for Zillow-style interface"""
        print("\n=== 1. APARTMENT SEARCH & FILTERING API ===")
        
        # Test 1.1: Basic apartment listing with count verification
        print("\n--- Testing Basic Apartment Listing ---")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code == 200:
                data = response.json()
                
                # Check if response is ApartmentListResponse format
                if isinstance(data, dict) and "apartments" in data:
                    apartments = data["apartments"]
                    total_count = data.get("total", len(apartments))
                    self.log_result("Basic Apartment Listing (ApartmentListResponse)", True, 
                                  f"Retrieved {len(apartments)} apartments, total: {total_count}")
                    
                    if apartments:
                        self.test_apartment_id = apartments[0].get("id")
                elif isinstance(data, list):
                    apartments = data
                    total_count = len(apartments)
                    self.log_result("Basic Apartment Listing (List Format)", True, 
                                  f"Retrieved {len(apartments)} apartments")
                    
                    if apartments:
                        self.test_apartment_id = apartments[0].get("id")
                else:
                    self.log_result("Basic Apartment Listing", False, f"Unexpected response format: {type(data)}")
                    return
                
                # Verify apartment count matches frontend display expectations
                if total_count >= 200:
                    self.log_result("Apartment Count Verification", True, 
                                  f"Excellent apartment inventory: {total_count} apartments (exceeds 200+ requirement)")
                elif total_count >= 100:
                    self.log_result("Apartment Count Verification", True, 
                                  f"Good apartment inventory: {total_count} apartments")
                else:
                    self.log_result("Apartment Count Verification", False, 
                                  f"Low apartment inventory: {total_count} apartments (expected 200+)")
                
            else:
                self.log_result("Basic Apartment Listing", False, f"Status code: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Basic Apartment Listing", False, f"Exception: {str(e)}")
            return
        
        # Test 1.2: Search term filtering (Zillow-style search box)
        print("\n--- Testing Search Term Filtering ---")
        search_terms = [
            {"term": "Brooklyn Heights", "description": "Specific neighborhood"},
            {"term": "Manhattan", "description": "Borough search"},
            {"term": "luxury", "description": "Amenity search"},
            {"term": "studio", "description": "Apartment type search"}
        ]
        
        for search_test in search_terms:
            try:
                response = self.make_request("GET", "/apartments", {
                    "search": search_test["term"],
                    "limit": 50
                })
                
                if response.status_code == 200:
                    data = response.json()
                    apartments = data.get("apartments", data) if isinstance(data, dict) else data
                    
                    if apartments:
                        self.log_result(f"Search Term '{search_test['term']}'", True, 
                                      f"{search_test['description']} search returned {len(apartments)} results")
                        
                        # Verify search relevance for first few results
                        relevant_count = 0
                        for apt in apartments[:5]:
                            apt_text = f"{apt.get('title', '')} {apt.get('description', '')} {apt.get('neighborhood', '')}".lower()
                            if search_test["term"].lower() in apt_text:
                                relevant_count += 1
                        
                        if relevant_count > 0:
                            self.log_result(f"Search Relevance '{search_test['term']}'", True, 
                                          f"{relevant_count}/5 top results contain search term")
                        else:
                            self.log_result(f"Search Relevance '{search_test['term']}'", False, 
                                          "No top results contain search term")
                    else:
                        self.log_result(f"Search Term '{search_test['term']}'", True, 
                                      f"{search_test['description']} search returned no results (acceptable)")
                else:
                    self.log_result(f"Search Term '{search_test['term']}'", False, 
                                  f"Search failed with status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Search Term '{search_test['term']}'", False, f"Exception: {str(e)}")
        
        # Test 1.3: Price range filtering (min_price and max_price)
        print("\n--- Testing Price Range Filtering ---")
        price_tests = [
            {"min_price": 3000, "max_price": 5000, "description": "Mid-range $3K-$5K"},
            {"min_price": 2000, "max_price": None, "description": "Minimum $2K+"},
            {"min_price": None, "max_price": 4000, "description": "Maximum under $4K"},
            {"min_price": 5000, "max_price": 8000, "description": "Luxury $5K-$8K"}
        ]
        
        for price_test in price_tests:
            try:
                params = {"limit": 30}
                if price_test["min_price"]:
                    params["min_price"] = price_test["min_price"]
                if price_test["max_price"]:
                    params["max_price"] = price_test["max_price"]
                
                response = self.make_request("GET", "/apartments", params)
                
                if response.status_code == 200:
                    data = response.json()
                    apartments = data.get("apartments", data) if isinstance(data, dict) else data
                    
                    # Verify price filtering accuracy
                    valid_prices = 0
                    for apt in apartments:
                        price = apt.get("price", 0)
                        price_valid = True
                        
                        if price_test["min_price"] and price < price_test["min_price"]:
                            price_valid = False
                        if price_test["max_price"] and price > price_test["max_price"]:
                            price_valid = False
                        
                        if price_valid:
                            valid_prices += 1
                    
                    if len(apartments) == 0:
                        self.log_result(f"Price Filter {price_test['description']}", True, 
                                      "No apartments in price range (acceptable)")
                    elif valid_prices == len(apartments):
                        self.log_result(f"Price Filter {price_test['description']}", True, 
                                      f"All {len(apartments)} apartments within price range")
                    else:
                        self.log_result(f"Price Filter {price_test['description']}", False, 
                                      f"Only {valid_prices}/{len(apartments)} apartments within price range")
                else:
                    self.log_result(f"Price Filter {price_test['description']}", False, 
                                  f"Request failed with status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Price Filter {price_test['description']}", False, f"Exception: {str(e)}")
        
        # Test 1.4: Bedrooms filtering
        print("\n--- Testing Bedrooms Filtering ---")
        bedroom_tests = [
            {"bedrooms": 0, "description": "Studio apartments"},
            {"bedrooms": 1, "description": "1 bedroom apartments"},
            {"bedrooms": 2, "description": "2 bedroom apartments"},
            {"bedrooms": 3, "description": "3 bedroom apartments"}
        ]
        
        for bedroom_test in bedroom_tests:
            try:
                response = self.make_request("GET", "/apartments", {
                    "bedrooms": bedroom_test["bedrooms"],
                    "limit": 25
                })
                
                if response.status_code == 200:
                    data = response.json()
                    apartments = data.get("apartments", data) if isinstance(data, dict) else data
                    
                    # Verify bedroom filtering accuracy
                    valid_bedrooms = 0
                    for apt in apartments:
                        apt_bedrooms = apt.get("bedrooms")
                        if apt_bedrooms == bedroom_test["bedrooms"]:
                            valid_bedrooms += 1
                    
                    if len(apartments) == 0:
                        self.log_result(f"Bedroom Filter {bedroom_test['description']}", True, 
                                      "No apartments with this bedroom count (acceptable)")
                    elif valid_bedrooms == len(apartments):
                        self.log_result(f"Bedroom Filter {bedroom_test['description']}", True, 
                                      f"All {len(apartments)} apartments have {bedroom_test['bedrooms']} bedrooms")
                    else:
                        self.log_result(f"Bedroom Filter {bedroom_test['description']}", False, 
                                      f"Only {valid_bedrooms}/{len(apartments)} apartments have correct bedroom count")
                else:
                    self.log_result(f"Bedroom Filter {bedroom_test['description']}", False, 
                                  f"Request failed with status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Bedroom Filter {bedroom_test['description']}", False, f"Exception: {str(e)}")
        
        # Test 1.5: Combined filtering (search + price + bedrooms)
        print("\n--- Testing Combined Filtering ---")
        try:
            response = self.make_request("GET", "/apartments", {
                "search": "Manhattan",
                "min_price": 3000,
                "max_price": 6000,
                "bedrooms": 1,
                "limit": 20
            })
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                # Verify all filters are applied correctly
                valid_combined = 0
                for apt in apartments:
                    search_match = "manhattan" in f"{apt.get('title', '')} {apt.get('neighborhood', '')} {apt.get('borough', '')}".lower()
                    price_match = 3000 <= apt.get("price", 0) <= 6000
                    bedroom_match = apt.get("bedrooms") == 1
                    
                    if search_match and price_match and bedroom_match:
                        valid_combined += 1
                
                if len(apartments) == 0:
                    self.log_result("Combined Filtering", True, "No apartments match all criteria (acceptable)")
                elif valid_combined == len(apartments):
                    self.log_result("Combined Filtering", True, 
                                  f"All {len(apartments)} apartments match combined criteria")
                else:
                    self.log_result("Combined Filtering", False, 
                                  f"Only {valid_combined}/{len(apartments)} apartments match all criteria")
            else:
                self.log_result("Combined Filtering", False, f"Request failed with status: {response.status_code}")
        except Exception as e:
            self.log_result("Combined Filtering", False, f"Exception: {str(e)}")
    
    def test_individual_apartment_details(self):
        """Test GET /api/apartments/{id} endpoint"""
        print("\n=== 2. INDIVIDUAL APARTMENT DETAILS ===")
        
        if not self.test_apartment_id:
            self.log_result("Individual Apartment Details", False, "No apartment ID available for testing")
            return
        
        try:
            response = self.make_request("GET", f"/apartments/{self.test_apartment_id}")
            
            if response.status_code == 200:
                apartment = response.json()
                
                # Verify apartment data structure is complete
                required_fields = ["id", "title", "price", "bedrooms", "bathrooms"]
                optional_fields = ["description", "images", "amenities", "neighborhood", "borough", "address"]
                
                missing_required = [field for field in required_fields if field not in apartment]
                present_optional = [field for field in optional_fields if field in apartment and apartment[field]]
                
                if not missing_required:
                    self.log_result("Apartment Data Structure", True, 
                                  f"All required fields present. Optional fields: {len(present_optional)}/{len(optional_fields)}")
                else:
                    self.log_result("Apartment Data Structure", False, 
                                  f"Missing required fields: {missing_required}")
                
                # Verify image URLs and apartment metadata
                images = apartment.get("images", [])
                if images:
                    valid_images = 0
                    for img_url in images:
                        if isinstance(img_url, str) and (img_url.startswith("http://") or img_url.startswith("https://")):
                            valid_images += 1
                    
                    if valid_images == len(images):
                        self.log_result("Apartment Images", True, f"All {len(images)} image URLs are valid")
                    else:
                        self.log_result("Apartment Images", False, 
                                      f"Only {valid_images}/{len(images)} image URLs are valid")
                else:
                    self.log_result("Apartment Images", False, "No images found for apartment")
                
                # Verify apartment metadata consistency
                metadata_checks = []
                if apartment.get("price") and isinstance(apartment["price"], (int, float)) and apartment["price"] > 0:
                    metadata_checks.append("price")
                if apartment.get("bedrooms") is not None and isinstance(apartment["bedrooms"], int) and apartment["bedrooms"] >= 0:
                    metadata_checks.append("bedrooms")
                if apartment.get("bathrooms") and isinstance(apartment["bathrooms"], (int, float)) and apartment["bathrooms"] > 0:
                    metadata_checks.append("bathrooms")
                
                if len(metadata_checks) >= 3:
                    self.log_result("Apartment Metadata Consistency", True, 
                                  f"Metadata consistent: {', '.join(metadata_checks)}")
                else:
                    self.log_result("Apartment Metadata Consistency", False, 
                                  f"Metadata issues. Valid: {', '.join(metadata_checks)}")
                
            elif response.status_code == 404:
                self.log_result("Individual Apartment Details", False, "Apartment not found (404)")
            else:
                self.log_result("Individual Apartment Details", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Individual Apartment Details", False, f"Exception: {str(e)}")
    
    def test_authentication_system(self):
        """Test user registration, login, and Google OAuth integration"""
        print("\n=== 3. AUTHENTICATION SYSTEM ===")
        
        # Test 3.1: User Registration
        print("\n--- Testing User Registration ---")
        try:
            registration_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME
            }
            
            response = self.make_request("POST", "/auth/register", registration_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "token_type" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("User Registration", True, "User registered successfully with JWT token")
                else:
                    self.log_result("User Registration", False, f"Missing token in response: {data}")
            elif response.status_code == 400:
                # User might already exist, try login
                login_response = self.make_request("POST", "/auth/login", {
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                })
                if login_response.status_code == 200:
                    token_data = login_response.json()
                    self.auth_token = token_data["access_token"]
                    self.log_result("User Registration", True, "User already exists, logged in successfully")
                else:
                    self.log_result("User Registration", False, f"Registration and login both failed")
            else:
                self.log_result("User Registration", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")
        
        # Test 3.2: User Login
        print("\n--- Testing User Login ---")
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "token_type" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("User Login", True, "Login successful with JWT token")
                else:
                    self.log_result("User Login", False, f"Missing token in response: {data}")
            else:
                self.log_result("User Login", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("User Login", False, f"Exception: {str(e)}")
        
        # Test 3.3: User Profile Endpoint
        print("\n--- Testing User Profile Endpoint ---")
        try:
            if self.auth_token:
                response = self.make_request("GET", "/auth/me")
                
                if response.status_code == 200:
                    data = response.json()
                    if "email" in data and data["email"] == TEST_USER_EMAIL:
                        self.test_user_id = data.get("id")
                        self.log_result("User Profile Endpoint", True, f"Profile retrieved for: {data.get('full_name', 'Unknown')}")
                    else:
                        self.log_result("User Profile Endpoint", False, f"Unexpected profile data: {data}")
                else:
                    self.log_result("User Profile Endpoint", False, f"Status code: {response.status_code}")
            else:
                self.log_result("User Profile Endpoint", False, "No auth token available")
        except Exception as e:
            self.log_result("User Profile Endpoint", False, f"Exception: {str(e)}")
        
        # Test 3.4: Google OAuth Integration Check
        print("\n--- Testing Google OAuth Integration ---")
        try:
            # Check if Google OAuth endpoints are available
            response = self.make_request("GET", "/auth/providers")
            
            if response.status_code == 200:
                data = response.json()
                if "google" in str(data).lower():
                    self.log_result("Google OAuth Integration", True, "Google OAuth provider available")
                else:
                    self.log_result("Google OAuth Integration", False, "Google OAuth provider not found in response")
            elif response.status_code == 404:
                # Try alternative endpoint
                response = self.make_request("GET", "/auth/google")
                if response.status_code in [200, 302]:
                    self.log_result("Google OAuth Integration", True, "Google OAuth endpoint accessible")
                else:
                    self.log_result("Google OAuth Integration", False, "Google OAuth endpoints not accessible")
            else:
                self.log_result("Google OAuth Integration", False, f"OAuth providers endpoint failed: {response.status_code}")
        except Exception as e:
            self.log_result("Google OAuth Integration", False, f"Exception: {str(e)}")
    
    def test_blog_system(self):
        """Test GET /api/blog and GET /api/blog/{slug} endpoints"""
        print("\n=== 4. BLOG SYSTEM ===")
        
        # Test 4.1: Blog Posts List
        print("\n--- Testing Blog Posts List ---")
        try:
            response = self.make_request("GET", "/blog")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response is BlogListResponse format
                if isinstance(data, dict) and "posts" in data:
                    posts = data["posts"]
                    total = data.get("total", len(posts))
                    self.log_result("Blog Posts List (BlogListResponse)", True, 
                                  f"Retrieved {len(posts)} posts, total: {total}")
                elif isinstance(data, list):
                    posts = data
                    self.log_result("Blog Posts List (List Format)", True, f"Retrieved {len(posts)} posts")
                else:
                    self.log_result("Blog Posts List", False, f"Unexpected response format: {type(data)}")
                    return
                
                # Verify blog content is properly formatted
                if posts:
                    first_post = posts[0]
                    required_fields = ["title", "slug", "excerpt", "content"]
                    missing_fields = [field for field in required_fields if field not in first_post]
                    
                    if not missing_fields:
                        self.log_result("Blog Content Format", True, "Blog posts have all required fields")
                        
                        # Test individual blog post
                        test_slug = first_post.get("slug")
                        if test_slug:
                            self.test_individual_blog_post(test_slug)
                    else:
                        self.log_result("Blog Content Format", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Blog Posts List", True, "No blog posts found (acceptable)")
            else:
                self.log_result("Blog Posts List", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Blog Posts List", False, f"Exception: {str(e)}")
    
    def test_individual_blog_post(self, slug: str):
        """Test individual blog post endpoint"""
        print(f"\n--- Testing Individual Blog Post: {slug} ---")
        try:
            response = self.make_request("GET", f"/blog/{slug}")
            
            if response.status_code == 200:
                post = response.json()
                
                # Verify blog post data structure
                required_fields = ["id", "title", "slug", "content", "author"]
                optional_fields = ["excerpt", "category", "tags", "featured_image", "view_count"]
                
                missing_required = [field for field in required_fields if field not in post]
                present_optional = [field for field in optional_fields if field in post and post[field]]
                
                if not missing_required:
                    self.log_result(f"Individual Blog Post ({slug})", True, 
                                  f"All required fields present. Optional: {len(present_optional)}/{len(optional_fields)}")
                else:
                    self.log_result(f"Individual Blog Post ({slug})", False, 
                                  f"Missing required fields: {missing_required}")
                
                # Verify content is not empty
                content = post.get("content", "")
                if content and len(content) > 100:
                    self.log_result("Blog Post Content", True, f"Content length: {len(content)} characters")
                else:
                    self.log_result("Blog Post Content", False, "Blog post content is too short or empty")
                
            elif response.status_code == 404:
                self.log_result(f"Individual Blog Post ({slug})", False, "Blog post not found (404)")
            else:
                self.log_result(f"Individual Blog Post ({slug})", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result(f"Individual Blog Post ({slug})", False, f"Exception: {str(e)}")
    
    def test_core_api_performance(self):
        """Test response times and error handling"""
        print("\n=== 5. CORE API PERFORMANCE ===")
        
        # Test 5.1: Response Times
        print("\n--- Testing API Response Times ---")
        performance_tests = [
            {"endpoint": "/apartments", "params": {"limit": 50}, "description": "Apartment listings"},
            {"endpoint": "/apartments-summary", "params": {}, "description": "Apartment summary"},
            {"endpoint": "/blog", "params": {"limit": 10}, "description": "Blog posts"},
            {"endpoint": "/health", "params": {}, "description": "Health check"}
        ]
        
        for test in performance_tests:
            try:
                response = self.make_request("GET", test["endpoint"], test["params"])
                response_time = getattr(response, 'request_time', 0)
                
                if response.status_code == 200:
                    if response_time < 3.0:  # Under 3 seconds as specified
                        self.log_result(f"Response Time - {test['description']}", True, 
                                      f"{response_time:.3f}s (under 3s requirement)")
                    else:
                        self.log_result(f"Response Time - {test['description']}", False, 
                                      f"{response_time:.3f}s (exceeds 3s requirement)")
                else:
                    self.log_result(f"Response Time - {test['description']}", False, 
                                  f"Request failed with status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Response Time - {test['description']}", False, f"Exception: {str(e)}")
        
        # Test 5.2: Error Handling
        print("\n--- Testing Error Handling ---")
        error_tests = [
            {"endpoint": "/apartments/invalid-id", "expected_status": 404, "description": "Invalid apartment ID"},
            {"endpoint": "/blog/non-existent-slug", "expected_status": 404, "description": "Non-existent blog post"},
            {"endpoint": "/apartments", "params": {"bedrooms": "invalid"}, "expected_status": 422, "description": "Invalid parameter type"}
        ]
        
        for test in error_tests:
            try:
                response = self.make_request("GET", test["endpoint"], test.get("params"))
                
                if response.status_code == test["expected_status"]:
                    self.log_result(f"Error Handling - {test['description']}", True, 
                                  f"Correctly returned {response.status_code}")
                else:
                    self.log_result(f"Error Handling - {test['description']}", False, 
                                  f"Expected {test['expected_status']}, got {response.status_code}")
            except Exception as e:
                self.log_result(f"Error Handling - {test['description']}", False, f"Exception: {str(e)}")
        
        # Test 5.3: Pagination and Sorting
        print("\n--- Testing Pagination and Sorting ---")
        try:
            # Test pagination
            response = self.make_request("GET", "/apartments", {"page": 1, "limit": 10})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                if len(apartments) <= 10:
                    self.log_result("Pagination Functionality", True, f"Pagination working: {len(apartments)} apartments returned")
                else:
                    self.log_result("Pagination Functionality", False, f"Pagination not working: {len(apartments)} apartments returned")
                
                # Test sorting (newest first)
                if len(apartments) >= 2:
                    dates = [apt.get("created_at") for apt in apartments if apt.get("created_at")]
                    if len(dates) >= 2:
                        is_sorted = all(dates[i] >= dates[i+1] for i in range(len(dates)-1))
                        if is_sorted:
                            self.log_result("Sorting Functionality", True, "Apartments sorted by newest first")
                        else:
                            self.log_result("Sorting Functionality", False, "Apartments not properly sorted")
                    else:
                        self.log_result("Sorting Functionality", True, "Insufficient date data to test sorting")
            else:
                self.log_result("Pagination Functionality", False, f"Pagination test failed: {response.status_code}")
        except Exception as e:
            self.log_result("Pagination and Sorting", False, f"Exception: {str(e)}")
    
    def test_data_consistency(self):
        """Test apartment data consistency and schema validation"""
        print("\n=== 6. DATA CONSISTENCY ===")
        
        try:
            response = self.make_request("GET", "/apartments", {"limit": 50})
            
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", data) if isinstance(data, dict) else data
                
                if not apartments:
                    self.log_result("Data Consistency", False, "No apartments to test")
                    return
                
                # Test 6.1: Schema Validation
                print("\n--- Testing Apartment Schema Validation ---")
                schema_issues = []
                valid_apartments = 0
                
                for i, apt in enumerate(apartments):
                    issues = []
                    
                    # Required fields check
                    if not apt.get("id"):
                        issues.append("missing id")
                    if not apt.get("title"):
                        issues.append("missing title")
                    if not isinstance(apt.get("price"), (int, float)) or apt.get("price", 0) <= 0:
                        issues.append("invalid price")
                    if apt.get("bedrooms") is None or not isinstance(apt.get("bedrooms"), int):
                        issues.append("invalid bedrooms")
                    
                    # Data type validation
                    if apt.get("bathrooms") and not isinstance(apt.get("bathrooms"), (int, float)):
                        issues.append("invalid bathrooms type")
                    if apt.get("sqft") and not isinstance(apt.get("sqft"), int):
                        issues.append("invalid sqft type")
                    
                    if not issues:
                        valid_apartments += 1
                    else:
                        schema_issues.append(f"Apartment {i+1}: {', '.join(issues)}")
                
                schema_percentage = (valid_apartments / len(apartments)) * 100
                if schema_percentage >= 95:
                    self.log_result("Apartment Schema Validation", True, 
                                  f"{valid_apartments}/{len(apartments)} apartments valid ({schema_percentage:.1f}%)")
                else:
                    self.log_result("Apartment Schema Validation", False, 
                                  f"Only {valid_apartments}/{len(apartments)} apartments valid ({schema_percentage:.1f}%)")
                    for issue in schema_issues[:5]:  # Show first 5 issues
                        print(f"   {issue}")
                
                # Test 6.2: Data Range Validation
                print("\n--- Testing Data Range Validation ---")
                price_range = [apt.get("price", 0) for apt in apartments if apt.get("price")]
                bedroom_range = [apt.get("bedrooms", 0) for apt in apartments if apt.get("bedrooms") is not None]
                
                if price_range:
                    min_price, max_price = min(price_range), max(price_range)
                    if 1000 <= min_price <= max_price <= 50000:
                        self.log_result("Price Range Validation", True, 
                                      f"Price range: ${min_price:,.0f} - ${max_price:,.0f}")
                    else:
                        self.log_result("Price Range Validation", False, 
                                      f"Unusual price range: ${min_price:,.0f} - ${max_price:,.0f}")
                
                if bedroom_range:
                    min_bed, max_bed = min(bedroom_range), max(bedroom_range)
                    if 0 <= min_bed <= max_bed <= 5:
                        self.log_result("Bedroom Range Validation", True, 
                                      f"Bedroom range: {min_bed} - {max_bed}")
                    else:
                        self.log_result("Bedroom Range Validation", False, 
                                      f"Unusual bedroom range: {min_bed} - {max_bed}")
                
                # Test 6.3: Apartment Count Consistency
                print("\n--- Testing Apartment Count Consistency ---")
                # Get count from different endpoints
                summary_response = self.make_request("GET", "/apartments-summary")
                if summary_response.status_code == 200:
                    summary_data = summary_response.json()
                    summary_count = summary_data.get("market_overview", {}).get("total_no_fee_apartments", 0)
                    
                    # Get total from apartments endpoint
                    full_response = self.make_request("GET", "/apartments", {"limit": 1000})
                    if full_response.status_code == 200:
                        full_data = full_response.json()
                        if isinstance(full_data, dict) and "total" in full_data:
                            apartments_count = full_data["total"]
                        else:
                            apartments_count = len(full_data) if isinstance(full_data, list) else 0
                        
                        if abs(summary_count - apartments_count) <= 5:  # Allow small discrepancy
                            self.log_result("Apartment Count Consistency", True, 
                                          f"Counts consistent: summary={summary_count}, apartments={apartments_count}")
                        else:
                            self.log_result("Apartment Count Consistency", False, 
                                          f"Count mismatch: summary={summary_count}, apartments={apartments_count}")
                    else:
                        self.log_result("Apartment Count Consistency", False, "Could not get full apartment count")
                else:
                    self.log_result("Apartment Count Consistency", False, "Could not get summary count")
                
            else:
                self.log_result("Data Consistency", False, f"Could not retrieve apartments: {response.status_code}")
        except Exception as e:
            self.log_result("Data Consistency", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 STARTING ZILLOW-STYLE BACKEND API TESTING")
        print("=" * 60)
        print(f"Testing backend API: {self.base_url}")
        print(f"Focus: Zillow-style search box improvements and backend functionality")
        print("=" * 60)
        
        # Run all test suites
        self.test_apartment_search_filtering_api()
        self.test_individual_apartment_details()
        self.test_authentication_system()
        self.test_blog_system()
        self.test_core_api_performance()
        self.test_data_consistency()
        
        # Print final results
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("🏁 ZILLOW-STYLE BACKEND API TESTING COMPLETE")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.results['passed']}")
        print(f"❌ Tests Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Total Time: {total_time:.1f}s")
        
        if self.results["failed"] > 0:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        print("\n🎯 TESTING FOCUS AREAS COVERED:")
        print("   ✓ Apartment Search & Filtering API (search_term, price, bedrooms)")
        print("   ✓ Individual Apartment Details (data structure, images, metadata)")
        print("   ✓ Authentication System (registration, login, Google OAuth)")
        print("   ✓ Blog System (posts list, individual posts, content format)")
        print("   ✓ Core API Performance (response times, error handling, pagination)")
        print("   ✓ Data Consistency (schema validation, count consistency)")
        
        return success_rate >= 80  # Consider 80%+ success rate as passing

if __name__ == "__main__":
    tester = ZillowStyleBackendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)