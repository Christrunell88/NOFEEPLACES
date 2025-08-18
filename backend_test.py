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
BASE_URL = "https://nycapartments.preview.emergentagent.com/api"
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
                    if field not in apt or not apt[field]:
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
        
        # Data scraping tests
        self.test_data_scraping()
        
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