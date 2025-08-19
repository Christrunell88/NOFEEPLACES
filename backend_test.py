#!/usr/bin/env python3
"""
NoFeePlaces.com Backend API Testing Suite
Tests all backend endpoints for authentication, apartments, user features, and data scraping
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://9baa349b-86eb-4d82-b63e-aa2a6cd5417c.preview.emergentagent.com/api"
TEST_USER_EMAIL = "testuser@nofeeplaces.com"
TEST_USER_PASSWORD = "SecurePassword123!"
TEST_USER_NAME = "John Doe"

class NoFeePlacesAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_user_id = None
        self.test_apartment_id = None
        self.test_saved_search_id = None
        self.test_appointment_id = None
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
        
        if self.auth_token and "Authorization" not in default_headers:
            default_headers["Authorization"] = f"Bearer {self.auth_token}"
        
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
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        print("\n=== Testing Health Check ===")
        try:
            response = self.make_request("GET", "/health")
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_result("Health Check", True, "API is healthy")
                else:
                    self.log_result("Health Check", False, f"Unexpected response: {data}")
            else:
                self.log_result("Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Health Check", False, f"Exception: {str(e)}")
    
    def test_user_registration(self):
        """Test user registration"""
        print("\n=== Testing User Registration ===")
        try:
            # First, try to clean up any existing test user
            try:
                login_response = self.make_request("POST", "/auth/login", {
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                })
                if login_response.status_code == 200:
                    print("Test user already exists, continuing with existing user...")
                    token_data = login_response.json()
                    self.auth_token = token_data["access_token"]
                    self.log_result("User Registration", True, "Using existing test user")
                    return
            except:
                pass
            
            # Register new user
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
                    self.log_result("User Registration", True, "User registered successfully")
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
                    self.log_result("User Registration", False, f"Registration failed: {response.text}")
            else:
                self.log_result("User Registration", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")
    
    def test_user_login(self):
        """Test user login"""
        print("\n=== Testing User Login ===")
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
                    self.log_result("User Login", True, "Login successful")
                else:
                    self.log_result("User Login", False, f"Missing token in response: {data}")
            else:
                self.log_result("User Login", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("User Login", False, f"Exception: {str(e)}")
    
    def test_user_profile(self):
        """Test getting user profile with JWT token"""
        print("\n=== Testing User Profile ===")
        try:
            if not self.auth_token:
                self.log_result("User Profile", False, "No auth token available")
                return
            
            response = self.make_request("GET", "/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                if "email" in data and data["email"] == TEST_USER_EMAIL:
                    self.test_user_id = data.get("id")
                    self.log_result("User Profile", True, f"Profile retrieved for user: {data['full_name']}")
                else:
                    self.log_result("User Profile", False, f"Unexpected profile data: {data}")
            else:
                self.log_result("User Profile", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("User Profile", False, f"Exception: {str(e)}")
    
    def test_jwt_validation(self):
        """Test JWT token validation"""
        print("\n=== Testing JWT Token Validation ===")
        try:
            # Test with valid token
            if self.auth_token:
                response = self.make_request("GET", "/auth/me")
                if response.status_code == 200:
                    self.log_result("JWT Validation (Valid Token)", True, "Valid token accepted")
                else:
                    self.log_result("JWT Validation (Valid Token)", False, f"Valid token rejected: {response.status_code}")
            
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token_here"}
            response = self.make_request("GET", "/auth/me", headers=invalid_headers)
            if response.status_code == 401:
                self.log_result("JWT Validation (Invalid Token)", True, "Invalid token properly rejected")
            else:
                self.log_result("JWT Validation (Invalid Token)", False, f"Invalid token not rejected: {response.status_code}")
                
        except Exception as e:
            self.log_result("JWT Validation", False, f"Exception: {str(e)}")
    
    def test_apartments_listing(self):
        """Test apartments listing endpoint"""
        print("\n=== Testing Apartments Listing ===")
        try:
            # Test basic listing
            response = self.make_request("GET", "/apartments")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Apartments Listing (Basic)", True, f"Retrieved {len(data)} apartments")
                    if data:
                        self.test_apartment_id = data[0].get("id")
                else:
                    self.log_result("Apartments Listing (Basic)", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Apartments Listing (Basic)", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Apartments Listing (Basic)", False, f"Exception: {str(e)}")
    
    def test_apartments_filtering(self):
        """Test apartments filtering"""
        print("\n=== Testing Apartments Filtering ===")
        try:
            # Test price filter
            response = self.make_request("GET", "/apartments", {"min_price": 2000, "max_price": 4000})
            if response.status_code == 200:
                data = response.json()
                self.log_result("Apartments Filter (Price)", True, f"Price filter returned {len(data)} apartments")
            else:
                self.log_result("Apartments Filter (Price)", False, f"Status code: {response.status_code}")
            
            # Test bedrooms filter
            response = self.make_request("GET", "/apartments", {"bedrooms": 1})
            if response.status_code == 200:
                data = response.json()
                self.log_result("Apartments Filter (Bedrooms)", True, f"Bedrooms filter returned {len(data)} apartments")
            else:
                self.log_result("Apartments Filter (Bedrooms)", False, f"Status code: {response.status_code}")
            
            # Test borough filter
            response = self.make_request("GET", "/apartments", {"borough": "Manhattan"})
            if response.status_code == 200:
                data = response.json()
                self.log_result("Apartments Filter (Borough)", True, f"Borough filter returned {len(data)} apartments")
            else:
                self.log_result("Apartments Filter (Borough)", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Apartments Filtering", False, f"Exception: {str(e)}")
    
    def test_apartments_pagination(self):
        """Test apartments pagination"""
        print("\n=== Testing Apartments Pagination ===")
        try:
            # Test pagination
            response = self.make_request("GET", "/apartments", {"page": 1, "limit": 2})
            if response.status_code == 200:
                data = response.json()
                if len(data) <= 2:
                    self.log_result("Apartments Pagination", True, f"Pagination working, got {len(data)} apartments")
                else:
                    self.log_result("Apartments Pagination", False, f"Limit not respected, got {len(data)} apartments")
            else:
                self.log_result("Apartments Pagination", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Apartments Pagination", False, f"Exception: {str(e)}")
    
    def test_apartments_search(self):
        """Test apartments search functionality"""
        print("\n=== Testing Apartments Search ===")
        try:
            # Test search term
            response = self.make_request("GET", "/apartments", {"search_term": "luxury"})
            if response.status_code == 200:
                data = response.json()
                self.log_result("Apartments Search", True, f"Search returned {len(data)} apartments")
            else:
                self.log_result("Apartments Search", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Apartments Search", False, f"Exception: {str(e)}")
    
    def test_apartment_details(self):
        """Test individual apartment details"""
        print("\n=== Testing Apartment Details ===")
        try:
            if not self.test_apartment_id:
                self.log_result("Apartment Details", False, "No apartment ID available for testing")
                return
            
            response = self.make_request("GET", f"/apartments/{self.test_apartment_id}")
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["id"] == self.test_apartment_id:
                    self.log_result("Apartment Details", True, f"Retrieved details for apartment: {data.get('title', 'Unknown')}")
                else:
                    self.log_result("Apartment Details", False, f"Unexpected apartment data: {data}")
            else:
                self.log_result("Apartment Details", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Apartment Details", False, f"Exception: {str(e)}")
    
    def test_apartment_stats(self):
        """Test apartment statistics endpoint"""
        print("\n=== Testing Apartment Statistics ===")
        try:
            response = self.make_request("GET", "/apartments/search/stats")
            if response.status_code == 200:
                data = response.json()
                if "total_apartments" in data:
                    self.log_result("Apartment Statistics", True, f"Stats retrieved: {data['total_apartments']} total apartments")
                else:
                    self.log_result("Apartment Statistics", False, f"Missing total_apartments in response: {data}")
            else:
                self.log_result("Apartment Statistics", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Apartment Statistics", False, f"Exception: {str(e)}")
    
    def test_favorites_functionality(self):
        """Test user favorites functionality"""
        print("\n=== Testing Favorites Functionality ===")
        try:
            if not self.auth_token:
                self.log_result("Favorites", False, "No auth token available")
                return
            
            if not self.test_apartment_id:
                self.log_result("Favorites", False, "No apartment ID available for testing")
                return
            
            # Add to favorites
            response = self.make_request("POST", f"/users/favorites/{self.test_apartment_id}")
            if response.status_code == 200:
                self.log_result("Add Favorite", True, "Apartment added to favorites")
            else:
                self.log_result("Add Favorite", False, f"Status code: {response.status_code}, Response: {response.text}")
            
            # Get favorites
            response = self.make_request("GET", "/users/favorites")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Favorites", True, f"Retrieved {len(data)} favorite apartments")
                else:
                    self.log_result("Get Favorites", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Get Favorites", False, f"Status code: {response.status_code}")
            
            # Remove from favorites
            response = self.make_request("DELETE", f"/users/favorites/{self.test_apartment_id}")
            if response.status_code == 200:
                self.log_result("Remove Favorite", True, "Apartment removed from favorites")
            else:
                self.log_result("Remove Favorite", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Favorites Functionality", False, f"Exception: {str(e)}")
    
    def test_saved_searches(self):
        """Test saved searches functionality"""
        print("\n=== Testing Saved Searches ===")
        try:
            if not self.auth_token:
                self.log_result("Saved Searches", False, "No auth token available")
                return
            
            # Create saved search
            search_data = {
                "name": "Test Search",
                "filters": {
                    "min_price": 2000,
                    "max_price": 4000,
                    "bedrooms": 1,
                    "borough": "Manhattan"
                },
                "alert_frequency": "daily"
            }
            
            response = self.make_request("POST", "/users/saved-searches", search_data)
            if response.status_code == 200:
                data = response.json()
                self.test_saved_search_id = data.get("id")
                self.log_result("Create Saved Search", True, f"Created saved search: {data.get('name')}")
            else:
                self.log_result("Create Saved Search", False, f"Status code: {response.status_code}, Response: {response.text}")
            
            # Get saved searches
            response = self.make_request("GET", "/users/saved-searches")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Saved Searches", True, f"Retrieved {len(data)} saved searches")
                else:
                    self.log_result("Get Saved Searches", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Get Saved Searches", False, f"Status code: {response.status_code}")
            
            # Delete saved search
            if self.test_saved_search_id:
                response = self.make_request("DELETE", f"/users/saved-searches/{self.test_saved_search_id}")
                if response.status_code == 200:
                    self.log_result("Delete Saved Search", True, "Saved search deleted successfully")
                else:
                    self.log_result("Delete Saved Search", False, f"Status code: {response.status_code}")
            
        except Exception as e:
            self.log_result("Saved Searches", False, f"Exception: {str(e)}")
    
    def test_data_scraping(self):
        """Test data scraping endpoint"""
        print("\n=== Testing Data Scraping ===")
        try:
            response = self.make_request("POST", "/admin/scrape")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_result("Data Scraping", True, f"Scraping completed: {data['message']}")
                else:
                    self.log_result("Data Scraping", False, f"Unexpected response: {data}")
            else:
                self.log_result("Data Scraping", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Data Scraping", False, f"Exception: {str(e)}")
    
    def test_tfc_listings_count(self):
        """Test that we have 30 total apartment listings including TFC properties"""
        print("\n=== Testing TFC Listings Count ===")
        try:
            # First trigger scraping to ensure all data is populated
            scrape_response = self.make_request("POST", "/admin/scrape")
            if scrape_response.status_code != 200:
                self.log_result("TFC Scraping Setup", False, f"Scraping failed: {scrape_response.status_code}")
                return
            
            # Get all apartments with high limit to ensure we get all
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code == 200:
                apartments = response.json()
                total_count = len(apartments)
                
                if total_count == 30:
                    self.log_result("TFC Total Count", True, f"Found exactly 30 apartments as expected")
                else:
                    self.log_result("TFC Total Count", False, f"Expected 30 apartments, found {total_count}")
                
                # Count TFC listings specifically
                tfc_count = 0
                for apt in apartments:
                    if apt.get("source_url") == "https://tfc.com":
                        tfc_count += 1
                
                if tfc_count == 10:
                    self.log_result("TFC Specific Count", True, f"Found exactly 10 TF Cornerstone listings")
                else:
                    self.log_result("TFC Specific Count", False, f"Expected 10 TFC listings, found {tfc_count}")
                    
            else:
                self.log_result("TFC Listings Count", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("TFC Listings Count", False, f"Exception: {str(e)}")
    
    def test_tfc_listings_data_quality(self):
        """Test that TFC listings have proper data quality"""
        print("\n=== Testing TFC Listings Data Quality ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code != 200:
                self.log_result("TFC Data Quality", False, f"Failed to get apartments: {response.status_code}")
                return
            
            apartments = response.json()
            tfc_apartments = [apt for apt in apartments if apt.get("source_url") == "https://tfc.com"]
            
            if not tfc_apartments:
                self.log_result("TFC Data Quality", False, "No TFC apartments found")
                return
            
            # Check data quality for each TFC apartment
            quality_issues = []
            required_fields = ["title", "address", "price", "bedrooms", "bathrooms", "sqft", "neighborhood", "borough", "description", "amenities", "contact_info"]
            
            for apt in tfc_apartments:
                for field in required_fields:
                    if field not in apt:
                        quality_issues.append(f"Missing {field} in apartment: {apt.get('title', 'Unknown')}")
                    elif field == "bedrooms" and apt[field] is None:
                        quality_issues.append(f"Missing {field} in apartment: {apt.get('title', 'Unknown')}")
                    elif field != "bedrooms" and not apt[field]:  # Allow 0 bedrooms for studios
                        quality_issues.append(f"Missing {field} in apartment: {apt.get('title', 'Unknown')}")
                
                # Check contact info specifically
                contact_info = apt.get("contact_info", {})
                if contact_info.get("phone") != "(646) 408-8048":
                    quality_issues.append(f"Wrong phone in {apt.get('title')}: {contact_info.get('phone')}")
                if contact_info.get("email") != "info@places.nyc":
                    quality_issues.append(f"Wrong email in {apt.get('title')}: {contact_info.get('email')}")
                if contact_info.get("broker") != "Chris Trunell":
                    quality_issues.append(f"Wrong broker in {apt.get('title')}: {contact_info.get('broker')}")
            
            if not quality_issues:
                self.log_result("TFC Data Quality", True, f"All {len(tfc_apartments)} TFC listings have proper data quality")
            else:
                self.log_result("TFC Data Quality", False, f"Data quality issues: {'; '.join(quality_issues[:3])}...")
                
        except Exception as e:
            self.log_result("TFC Data Quality", False, f"Exception: {str(e)}")
    
    def test_tfc_neighborhoods_coverage(self):
        """Test that TFC listings cover expected neighborhoods"""
        print("\n=== Testing TFC Neighborhoods Coverage ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code != 200:
                self.log_result("TFC Neighborhoods", False, f"Failed to get apartments: {response.status_code}")
                return
            
            apartments = response.json()
            tfc_apartments = [apt for apt in apartments if apt.get("source_url") == "https://tfc.com"]
            
            # Expected neighborhoods for TFC listings
            expected_neighborhoods = {
                "West Village", "Midtown West", "Upper East Side", 
                "Long Island City", "Chelsea", "Murray Hill", "Prospect Heights"
            }
            
            found_neighborhoods = set()
            for apt in tfc_apartments:
                neighborhood = apt.get("neighborhood")
                if neighborhood:
                    found_neighborhoods.add(neighborhood)
            
            # Check coverage
            covered_neighborhoods = expected_neighborhoods.intersection(found_neighborhoods)
            missing_neighborhoods = expected_neighborhoods - found_neighborhoods
            
            if len(covered_neighborhoods) >= 5:  # At least 5 of the 7 expected neighborhoods
                self.log_result("TFC Neighborhoods Coverage", True, 
                              f"Good neighborhood coverage: {', '.join(sorted(covered_neighborhoods))}")
            else:
                self.log_result("TFC Neighborhoods Coverage", False, 
                              f"Poor coverage. Found: {', '.join(sorted(covered_neighborhoods))}, Missing: {', '.join(sorted(missing_neighborhoods))}")
                
        except Exception as e:
            self.log_result("TFC Neighborhoods Coverage", False, f"Exception: {str(e)}")
    
    def test_tfc_filtering_functionality(self):
        """Test that TFC listings can be properly filtered"""
        print("\n=== Testing TFC Filtering Functionality ===")
        try:
            # Test filtering by neighborhood that should include TFC listings
            response = self.make_request("GET", "/apartments", {"neighborhood": "West Village"})
            if response.status_code == 200:
                apartments = response.json()
                west_village_tfc = [apt for apt in apartments if apt.get("source_url") == "https://tfc.com"]
                if west_village_tfc:
                    self.log_result("TFC Neighborhood Filter", True, f"Found {len(west_village_tfc)} TFC listings in West Village")
                else:
                    self.log_result("TFC Neighborhood Filter", False, "No TFC listings found in West Village filter")
            else:
                self.log_result("TFC Neighborhood Filter", False, f"Neighborhood filter failed: {response.status_code}")
            
            # Test filtering by price range that should include some TFC listings
            response = self.make_request("GET", "/apartments", {"min_price": 5000, "max_price": 10000})
            if response.status_code == 200:
                apartments = response.json()
                price_filtered_tfc = [apt for apt in apartments if apt.get("source_url") == "https://tfc.com"]
                if price_filtered_tfc:
                    self.log_result("TFC Price Filter", True, f"Found {len(price_filtered_tfc)} TFC listings in $5K-$10K range")
                else:
                    self.log_result("TFC Price Filter", False, "No TFC listings found in $5K-$10K price range")
            else:
                self.log_result("TFC Price Filter", False, f"Price filter failed: {response.status_code}")
            
            # Test filtering by borough
            response = self.make_request("GET", "/apartments", {"borough": "Manhattan"})
            if response.status_code == 200:
                apartments = response.json()
                manhattan_tfc = [apt for apt in apartments if apt.get("source_url") == "https://tfc.com"]
                if manhattan_tfc:
                    self.log_result("TFC Borough Filter", True, f"Found {len(manhattan_tfc)} TFC listings in Manhattan")
                else:
                    self.log_result("TFC Borough Filter", False, "No TFC listings found in Manhattan filter")
            else:
                self.log_result("TFC Borough Filter", False, f"Borough filter failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("TFC Filtering Functionality", False, f"Exception: {str(e)}")
    
    def test_standardized_contact_info(self):
        """Test that all listings have standardized contact information"""
        print("\n=== Testing Standardized Contact Info ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code != 200:
                self.log_result("Standardized Contact Info", False, f"Failed to get apartments: {response.status_code}")
                return
            
            apartments = response.json()
            
            # Check that all apartments have the standardized contact info
            contact_issues = []
            expected_phone = "(646) 408-8048"
            expected_email = "info@places.nyc"
            expected_broker = "Chris Trunell"
            
            for apt in apartments:
                contact_info = apt.get("contact_info", {})
                title = apt.get("title", "Unknown")
                
                if contact_info.get("phone") != expected_phone:
                    contact_issues.append(f"Wrong phone in '{title}': {contact_info.get('phone')}")
                if contact_info.get("email") != expected_email:
                    contact_issues.append(f"Wrong email in '{title}': {contact_info.get('email')}")
                if contact_info.get("broker") != expected_broker:
                    contact_issues.append(f"Wrong broker in '{title}': {contact_info.get('broker')}")
            
            if not contact_issues:
                self.log_result("Standardized Contact Info", True, f"All {len(apartments)} listings have standardized contact info")
            else:
                self.log_result("Standardized Contact Info", False, f"Contact info issues found: {len(contact_issues)} problems")
                # Print first few issues for debugging
                for issue in contact_issues[:3]:
                    print(f"   • {issue}")
                    
        except Exception as e:
            self.log_result("Standardized Contact Info", False, f"Exception: {str(e)}")
    
    def test_scraping_and_image_updates(self):
        """Test scraping endpoint and verify image updates for specific apartments"""
        print("\n=== Testing Scraping and Image Updates ===")
        try:
            # First, trigger the scraping endpoint
            print("Triggering scraping endpoint...")
            scrape_response = self.make_request("POST", "/admin/scrape")
            if scrape_response.status_code == 200:
                scrape_data = scrape_response.json()
                self.log_result("Scraping Trigger", True, f"Scraping completed: {scrape_data.get('message', 'Success')}")
            else:
                self.log_result("Scraping Trigger", False, f"Scraping failed with status: {scrape_response.status_code}")
                return
            
            # Wait a moment for database updates
            time.sleep(2)
            
            # Get all apartments to verify count and images
            response = self.make_request("GET", "/apartments", {"limit": 50})
            if response.status_code != 200:
                self.log_result("Post-Scraping Apartment Count", False, f"Failed to get apartments: {response.status_code}")
                return
            
            apartments = response.json()
            total_count = len(apartments)
            
            # Verify we still have 30 apartments
            if total_count == 30:
                self.log_result("Post-Scraping Apartment Count", True, f"Confirmed 30 apartments exist after scraping")
            else:
                self.log_result("Post-Scraping Apartment Count", False, f"Expected 30 apartments, found {total_count}")
            
            # Check specific apartment: 201 E 69th St (should show modern apartment interior)
            fairfax_apt = None
            for apt in apartments:
                if "201 E 69th St" in apt.get("address", ""):
                    fairfax_apt = apt
                    break
            
            if fairfax_apt:
                images = fairfax_apt.get("images", [])
                if images and len(images) > 0:
                    # Check if images are proper apartment interiors (not house exteriors)
                    has_proper_images = any("pexels" in img or "unsplash" in img for img in images)
                    if has_proper_images:
                        self.log_result("201 E 69th St Images", True, f"Found proper apartment interior images: {len(images)} images")
                    else:
                        self.log_result("201 E 69th St Images", False, f"Images may not be proper apartment interiors: {images[:2]}")
                else:
                    self.log_result("201 E 69th St Images", False, "No images found for 201 E 69th St apartment")
            else:
                self.log_result("201 E 69th St Images", False, "Could not find 201 E 69th St apartment")
            
            # Check lower-priced apartments like $3,895 studio
            studio_apartments = [apt for apt in apartments if apt.get("price", 0) == 3895 and apt.get("bedrooms", -1) == 0]
            if studio_apartments:
                studio_apt = studio_apartments[0]
                studio_images = studio_apt.get("images", [])
                if studio_images and len(studio_images) > 0:
                    self.log_result("$3,895 Studio Images", True, f"Studio apartment has {len(studio_images)} images: {studio_apt.get('title', 'Unknown')}")
                else:
                    self.log_result("$3,895 Studio Images", False, f"Studio apartment missing images: {studio_apt.get('title', 'Unknown')}")
            else:
                # Look for any studio around that price range
                studios_near_price = [apt for apt in apartments if apt.get("bedrooms", -1) == 0 and 3800 <= apt.get("price", 0) <= 4000]
                if studios_near_price:
                    studio_apt = studios_near_price[0]
                    studio_images = studio_apt.get("images", [])
                    if studio_images:
                        self.log_result("Lower-Priced Studio Images", True, f"Found studio with images: ${studio_apt.get('price')} - {len(studio_images)} images")
                    else:
                        self.log_result("Lower-Priced Studio Images", False, f"Studio missing images: ${studio_apt.get('price')}")
                else:
                    self.log_result("Lower-Priced Studio Images", False, "Could not find $3,895 studio or similar priced studio")
            
            # Verify all apartments have proper images
            apartments_without_images = []
            apartments_with_proper_images = 0
            
            for apt in apartments:
                images = apt.get("images", [])
                title = apt.get("title", "Unknown")
                
                if not images or len(images) == 0:
                    apartments_without_images.append(title)
                else:
                    # Check if images are from proper sources (not generic/wrong images)
                    has_quality_images = any("unsplash.com" in img or "pexels.com" in img for img in images)
                    if has_quality_images:
                        apartments_with_proper_images += 1
            
            if len(apartments_without_images) == 0:
                self.log_result("All Apartments Have Images", True, f"All {total_count} apartments have images")
            else:
                self.log_result("All Apartments Have Images", False, f"{len(apartments_without_images)} apartments missing images")
            
            # Check image quality across all apartments
            if apartments_with_proper_images >= 25:  # At least 25 out of 30 should have quality images
                self.log_result("Image Quality Check", True, f"{apartments_with_proper_images} apartments have proper quality images")
            else:
                self.log_result("Image Quality Check", False, f"Only {apartments_with_proper_images} apartments have proper quality images")
            
            # Print summary of image sources for debugging
            image_sources = {}
            for apt in apartments:
                images = apt.get("images", [])
                for img in images:
                    if "unsplash.com" in img:
                        image_sources["unsplash"] = image_sources.get("unsplash", 0) + 1
                    elif "pexels.com" in img:
                        image_sources["pexels"] = image_sources.get("pexels", 0) + 1
                    else:
                        domain = img.split("/")[2] if len(img.split("/")) > 2 else "unknown"
                        image_sources[domain] = image_sources.get(domain, 0) + 1
            
            print(f"   Image sources breakdown: {image_sources}")
            
        except Exception as e:
            self.log_result("Scraping and Image Updates", False, f"Exception: {str(e)}")
    
    def test_appointment_creation(self):
        """Test appointment creation endpoint"""
        print("\n=== Testing Appointment Creation ===")
        try:
            if not self.test_apartment_id:
                self.log_result("Appointment Creation", False, "No apartment ID available for testing")
                return
            
            # Test valid appointment creation
            from datetime import datetime, timedelta
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            appointment_data = {
                "apartment_id": self.test_apartment_id,
                "visitor_name": "Sarah Johnson",
                "visitor_email": "sarah.johnson@email.com",
                "visitor_phone": "+1-555-123-4567",
                "appointment_date": tomorrow,
                "appointment_time": "2:00 PM",
                "notes": "Looking for a 1-bedroom apartment for immediate move-in"
            }
            
            response = self.make_request("POST", "/appointments", appointment_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("visitor_name") == "Sarah Johnson":
                    self.test_appointment_id = data["id"]
                    self.log_result("Appointment Creation (Valid)", True, f"Created appointment for {data['visitor_name']}")
                else:
                    self.log_result("Appointment Creation (Valid)", False, f"Unexpected response: {data}")
            else:
                self.log_result("Appointment Creation (Valid)", False, f"Status code: {response.status_code}, Response: {response.text}")
            
            # Test business hours constraint (before 10 AM)
            early_appointment = appointment_data.copy()
            early_appointment["appointment_time"] = "9:00 AM"
            
            response = self.make_request("POST", "/appointments", early_appointment)
            if response.status_code == 400:
                self.log_result("Business Hours Constraint (Early)", True, "Correctly rejected 9 AM appointment")
            else:
                self.log_result("Business Hours Constraint (Early)", False, f"Should reject 9 AM appointment, got: {response.status_code}")
            
            # Test business hours constraint (after 7 PM)
            late_appointment = appointment_data.copy()
            late_appointment["appointment_time"] = "8:00 PM"
            
            response = self.make_request("POST", "/appointments", late_appointment)
            if response.status_code == 400:
                self.log_result("Business Hours Constraint (Late)", True, "Correctly rejected 8 PM appointment")
            else:
                self.log_result("Business Hours Constraint (Late)", False, f"Should reject 8 PM appointment, got: {response.status_code}")
            
            # Test conflict detection (same time slot)
            if hasattr(self, 'test_appointment_id'):
                conflict_appointment = appointment_data.copy()
                conflict_appointment["visitor_name"] = "John Smith"
                conflict_appointment["visitor_email"] = "john.smith@email.com"
                
                response = self.make_request("POST", "/appointments", conflict_appointment)
                if response.status_code == 409:
                    self.log_result("Conflict Detection", True, "Correctly detected time slot conflict")
                else:
                    self.log_result("Conflict Detection", False, f"Should detect conflict, got: {response.status_code}")
            
        except Exception as e:
            self.log_result("Appointment Creation", False, f"Exception: {str(e)}")
    
    def test_available_time_slots(self):
        """Test available time slots endpoint"""
        print("\n=== Testing Available Time Slots ===")
        try:
            if not self.test_apartment_id:
                self.log_result("Available Time Slots", False, "No apartment ID available for testing")
                return
            
            # Test getting available slots for tomorrow
            from datetime import datetime, timedelta
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            response = self.make_request("GET", f"/apartments/{self.test_apartment_id}/available-slots", {"date": tomorrow})
            if response.status_code == 200:
                data = response.json()
                if "available_slots" in data and isinstance(data["available_slots"], list):
                    slots = data["available_slots"]
                    # Should have slots from 10 AM to 6 PM (9 total slots) minus any booked
                    if len(slots) >= 8:  # At least 8 slots should be available (allowing for 1 booked)
                        self.log_result("Available Time Slots (Valid Date)", True, f"Found {len(slots)} available slots")
                    else:
                        self.log_result("Available Time Slots (Valid Date)", False, f"Expected at least 8 slots, got {len(slots)}")
                else:
                    self.log_result("Available Time Slots (Valid Date)", False, f"Unexpected response format: {data}")
            else:
                self.log_result("Available Time Slots (Valid Date)", False, f"Status code: {response.status_code}")
            
            # Test getting slots for past date (should return empty)
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            response = self.make_request("GET", f"/apartments/{self.test_apartment_id}/available-slots", {"date": yesterday})
            if response.status_code == 200:
                data = response.json()
                if data.get("available_slots") == []:
                    self.log_result("Available Time Slots (Past Date)", True, "Correctly returned empty slots for past date")
                else:
                    self.log_result("Available Time Slots (Past Date)", False, f"Should return empty for past date, got: {data}")
            else:
                self.log_result("Available Time Slots (Past Date)", False, f"Status code: {response.status_code}")
            
            # Test invalid date format
            response = self.make_request("GET", f"/apartments/{self.test_apartment_id}/available-slots", {"date": "invalid-date"})
            if response.status_code == 400:
                self.log_result("Available Time Slots (Invalid Date)", True, "Correctly rejected invalid date format")
            else:
                self.log_result("Available Time Slots (Invalid Date)", False, f"Should reject invalid date, got: {response.status_code}")
            
        except Exception as e:
            self.log_result("Available Time Slots", False, f"Exception: {str(e)}")
    
    def test_appointment_retrieval(self):
        """Test appointment retrieval with filters"""
        print("\n=== Testing Appointment Retrieval ===")
        try:
            # Test getting all appointments
            response = self.make_request("GET", "/appointments")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get All Appointments", True, f"Retrieved {len(data)} appointments")
                else:
                    self.log_result("Get All Appointments", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Get All Appointments", False, f"Status code: {response.status_code}")
            
            # Test filtering by apartment ID
            if self.test_apartment_id:
                response = self.make_request("GET", "/appointments", {"apartment_id": self.test_apartment_id})
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_result("Filter by Apartment ID", True, f"Found {len(data)} appointments for apartment")
                    else:
                        self.log_result("Filter by Apartment ID", False, f"Expected list, got: {type(data)}")
                else:
                    self.log_result("Filter by Apartment ID", False, f"Status code: {response.status_code}")
            
            # Test filtering by status
            response = self.make_request("GET", "/appointments", {"status": "pending"})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Filter by Status", True, f"Found {len(data)} pending appointments")
                else:
                    self.log_result("Filter by Status", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Filter by Status", False, f"Status code: {response.status_code}")
            
            # Test date range filtering
            from datetime import datetime, timedelta
            today = datetime.now().strftime("%Y-%m-%d")
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            response = self.make_request("GET", "/appointments", {"date_from": today, "date_to": tomorrow})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Filter by Date Range", True, f"Found {len(data)} appointments in date range")
                else:
                    self.log_result("Filter by Date Range", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Filter by Date Range", False, f"Status code: {response.status_code}")
            
        except Exception as e:
            self.log_result("Appointment Retrieval", False, f"Exception: {str(e)}")
    
    def test_appointment_status_updates(self):
        """Test appointment status updates"""
        print("\n=== Testing Appointment Status Updates ===")
        try:
            if not hasattr(self, 'test_appointment_id') or not self.test_appointment_id:
                self.log_result("Appointment Status Updates", False, "No appointment ID available for testing")
                return
            
            # Test updating status to confirmed
            update_data = {
                "status": "confirmed",
                "notes": "Appointment confirmed by property manager"
            }
            
            response = self.make_request("PUT", f"/appointments/{self.test_appointment_id}", update_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "confirmed":
                    self.log_result("Update Status to Confirmed", True, "Successfully updated status to confirmed")
                else:
                    self.log_result("Update Status to Confirmed", False, f"Status not updated correctly: {data.get('status')}")
            else:
                self.log_result("Update Status to Confirmed", False, f"Status code: {response.status_code}")
            
            # Test updating status to completed
            update_data = {"status": "completed"}
            response = self.make_request("PUT", f"/appointments/{self.test_appointment_id}", update_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "completed":
                    self.log_result("Update Status to Completed", True, "Successfully updated status to completed")
                else:
                    self.log_result("Update Status to Completed", False, f"Status not updated correctly: {data.get('status')}")
            else:
                self.log_result("Update Status to Completed", False, f"Status code: {response.status_code}")
            
            # Test invalid status
            invalid_update = {"status": "invalid_status"}
            response = self.make_request("PUT", f"/appointments/{self.test_appointment_id}", invalid_update)
            if response.status_code == 400:
                self.log_result("Invalid Status Update", True, "Correctly rejected invalid status")
            else:
                self.log_result("Invalid Status Update", False, f"Should reject invalid status, got: {response.status_code}")
            
            # Test updating non-existent appointment
            fake_id = "fake-appointment-id-12345"
            response = self.make_request("PUT", f"/appointments/{fake_id}", {"status": "confirmed"})
            if response.status_code == 404:
                self.log_result("Update Non-existent Appointment", True, "Correctly returned 404 for non-existent appointment")
            else:
                self.log_result("Update Non-existent Appointment", False, f"Should return 404, got: {response.status_code}")
            
        except Exception as e:
            self.log_result("Appointment Status Updates", False, f"Exception: {str(e)}")
    
    def test_appointment_data_validation(self):
        """Test appointment data includes all required fields"""
        print("\n=== Testing Appointment Data Validation ===")
        try:
            if not hasattr(self, 'test_appointment_id') or not self.test_appointment_id:
                self.log_result("Appointment Data Validation", False, "No appointment ID available for testing")
                return
            
            # Get the appointment and verify all required fields
            response = self.make_request("GET", f"/appointments/{self.test_appointment_id}")
            if response.status_code == 200:
                data = response.json()
                
                required_fields = [
                    "id", "apartment_id", "visitor_name", "visitor_email", "visitor_phone",
                    "appointment_date", "appointment_time", "status", "created_at", "updated_at"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                if not missing_fields:
                    self.log_result("Appointment Required Fields", True, "All required fields present in appointment data")
                else:
                    self.log_result("Appointment Required Fields", False, f"Missing fields: {', '.join(missing_fields)}")
                
                # Verify data types and values
                validation_issues = []
                
                if not isinstance(data.get("visitor_name"), str) or not data.get("visitor_name"):
                    validation_issues.append("visitor_name should be non-empty string")
                
                if not isinstance(data.get("visitor_email"), str) or "@" not in data.get("visitor_email", ""):
                    validation_issues.append("visitor_email should be valid email")
                
                if not isinstance(data.get("visitor_phone"), str) or not data.get("visitor_phone"):
                    validation_issues.append("visitor_phone should be non-empty string")
                
                if data.get("status") not in ["pending", "confirmed", "completed", "cancelled"]:
                    validation_issues.append(f"status should be valid value, got: {data.get('status')}")
                
                if not validation_issues:
                    self.log_result("Appointment Data Types", True, "All appointment data types are valid")
                else:
                    self.log_result("Appointment Data Types", False, f"Validation issues: {'; '.join(validation_issues)}")
                
            else:
                self.log_result("Appointment Data Validation", False, f"Failed to get appointment: {response.status_code}")
            
        except Exception as e:
            self.log_result("Appointment Data Validation", False, f"Exception: {str(e)}")
    
    def test_appointment_cancellation(self):
        """Test appointment cancellation"""
        print("\n=== Testing Appointment Cancellation ===")
        try:
            if not hasattr(self, 'test_appointment_id') or not self.test_appointment_id:
                self.log_result("Appointment Cancellation", False, "No appointment ID available for testing")
                return
            
            # Test cancelling appointment
            response = self.make_request("DELETE", f"/appointments/{self.test_appointment_id}")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "cancelled" in data["message"].lower():
                    self.log_result("Cancel Appointment", True, "Successfully cancelled appointment")
                else:
                    self.log_result("Cancel Appointment", False, f"Unexpected response: {data}")
            else:
                self.log_result("Cancel Appointment", False, f"Status code: {response.status_code}")
            
            # Verify appointment is cancelled
            response = self.make_request("GET", f"/appointments/{self.test_appointment_id}")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "cancelled":
                    self.log_result("Verify Cancellation", True, "Appointment status updated to cancelled")
                else:
                    self.log_result("Verify Cancellation", False, f"Status not updated to cancelled: {data.get('status')}")
            else:
                self.log_result("Verify Cancellation", False, f"Failed to verify cancellation: {response.status_code}")
            
            # Test cancelling non-existent appointment
            fake_id = "fake-appointment-id-12345"
            response = self.make_request("DELETE", f"/appointments/{fake_id}")
            if response.status_code == 404:
                self.log_result("Cancel Non-existent Appointment", True, "Correctly returned 404 for non-existent appointment")
            else:
                self.log_result("Cancel Non-existent Appointment", False, f"Should return 404, got: {response.status_code}")
            
        except Exception as e:
            self.log_result("Appointment Cancellation", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting NoFeePlaces.com Backend API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Basic connectivity
        self.test_health_check()
        
        # Authentication tests
        self.test_user_registration()
        self.test_user_login()
        self.test_user_profile()
        self.test_jwt_validation()
        
        # Apartment listing tests
        self.test_apartments_listing()
        self.test_apartments_filtering()
        self.test_apartments_pagination()
        self.test_apartments_search()
        self.test_apartment_details()
        self.test_apartment_stats()
        
        # User features tests
        self.test_favorites_functionality()
        self.test_saved_searches()
        
        # Appointment scheduling tests
        self.test_appointment_creation()
        self.test_available_time_slots()
        self.test_appointment_retrieval()
        self.test_appointment_status_updates()
        self.test_appointment_data_validation()
        self.test_appointment_cancellation()
        
        # Data scraping tests
        self.test_data_scraping()
        
        # Scraping and image update verification (as requested)
        self.test_scraping_and_image_updates()
        
        # TF Cornerstone specific tests
        self.test_tfc_listings_count()
        self.test_tfc_listings_data_quality()
        self.test_tfc_neighborhoods_coverage()
        self.test_tfc_filtering_functionality()
        self.test_standardized_contact_info()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['passed'] + self.results['failed']}")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100 if (self.results['passed'] + self.results['failed']) > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        return self.results

if __name__ == "__main__":
    tester = NoFeePlacesAPITester()
    results = tester.run_all_tests()