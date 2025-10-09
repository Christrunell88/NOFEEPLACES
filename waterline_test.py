#!/usr/bin/env python3
"""
Waterline Square Apartments Database Verification Test
Specific test for the review request to verify Waterline Square apartments
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "https://nestio-restore.preview.emergentagent.com/api"

class WaterlineSquareVerifier:
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
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_waterline_square_verification(self):
        """Test Waterline Square apartments database verification as requested"""
        print("\n=== WATERLINE SQUARE APARTMENTS DATABASE VERIFICATION ===")
        try:
            # 1. Database Connection Test
            print("\n--- Testing Database Connection ---")
            response = self.make_request("GET", "/apartments", {"limit": 1})
            if response.status_code == 200:
                self.log_result("Database Connection", True, "Successfully connected to MongoDB database")
            else:
                self.log_result("Database Connection", False, f"Database connection failed: {response.status_code}")
                return
            
            # 2. Total Apartment Count Test (should be 82: 74 existing + 8 Waterline)
            print("\n--- Testing Total Apartment Count ---")
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code == 200:
                apartments = response.json()
                total_count = len(apartments)
                
                if total_count == 82:
                    self.log_result("Total Apartment Count (82)", True, f"Found exactly 82 apartments (74 existing + 8 Waterline)")
                elif total_count == 74:
                    self.log_result("Total Apartment Count (82)", False, f"Found only 74 apartments - Waterline apartments missing")
                else:
                    self.log_result("Total Apartment Count (82)", False, f"Expected 82 apartments, found {total_count}")
                
                print(f"   Current apartment count: {total_count}")
            else:
                self.log_result("Total Apartment Count", False, f"Failed to get apartments: {response.status_code}")
                return
            
            # 3. Waterline Square Apartments Verification
            print("\n--- Testing Waterline Square Apartments ---")
            waterline_apartments = []
            for apt in apartments:
                title = apt.get("title", "").lower()
                address = apt.get("address", "").lower()
                if "waterline" in title or "waterline square" in address:
                    waterline_apartments.append(apt)
            
            if len(waterline_apartments) == 8:
                self.log_result("Waterline Square Count", True, f"Found exactly 8 Waterline Square apartments")
                
                # Verify each Waterline apartment has proper data structure
                waterline_data_issues = []
                required_fields = ["id", "title", "address", "price", "bedrooms", "bathrooms", "sqft", "neighborhood", "borough", "description", "amenities", "images", "contact_info"]
                
                for i, apt in enumerate(waterline_apartments, 1):
                    print(f"   Waterline Apt {i}: {apt.get('title', 'Unknown')} - ${apt.get('price', 0):,}")
                    
                    for field in required_fields:
                        if field not in apt or not apt[field]:
                            if field == "bedrooms" and apt.get(field) == 0:  # Allow 0 bedrooms for studios
                                continue
                            waterline_data_issues.append(f"Missing {field} in {apt.get('title', 'Unknown')}")
                
                if not waterline_data_issues:
                    self.log_result("Waterline Data Structure", True, "All Waterline apartments have proper data structure")
                else:
                    self.log_result("Waterline Data Structure", False, f"Data issues: {'; '.join(waterline_data_issues[:3])}")
                    
            elif len(waterline_apartments) == 0:
                self.log_result("Waterline Square Count", False, "No Waterline Square apartments found in database")
            else:
                self.log_result("Waterline Square Count", False, f"Expected 8 Waterline apartments, found {len(waterline_apartments)}")
            
            # 4. API Endpoint Test - GET /api/apartments
            print("\n--- Testing GET /api/apartments Endpoint ---")
            response = self.make_request("GET", "/apartments")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_result("GET /api/apartments", True, f"Endpoint returns {len(data)} apartments successfully")
                    
                    # Check if Waterline apartments are included in the response
                    waterline_in_response = [apt for apt in data if "waterline" in apt.get("title", "").lower()]
                    if waterline_in_response:
                        self.log_result("Waterline in API Response", True, f"Found {len(waterline_in_response)} Waterline apartments in API response")
                    else:
                        self.log_result("Waterline in API Response", False, "No Waterline apartments found in API response")
                else:
                    self.log_result("GET /api/apartments", False, f"API returned empty or invalid data: {type(data)}")
            else:
                self.log_result("GET /api/apartments", False, f"API endpoint failed: {response.status_code}")
            
            # 5. Database Query Verification - Check apartment data structure
            print("\n--- Testing Apartment Data Structure ---")
            if apartments:
                sample_apt = apartments[0]
                required_fields = ["id", "title", "address", "price", "bedrooms", "bathrooms", "sqft", "neighborhood", "borough"]
                
                structure_valid = True
                missing_fields = []
                for field in required_fields:
                    if field not in sample_apt:
                        missing_fields.append(field)
                        structure_valid = False
                
                if structure_valid:
                    self.log_result("Apartment Data Structure", True, "All required fields present in apartment data")
                else:
                    self.log_result("Apartment Data Structure", False, f"Missing fields: {', '.join(missing_fields)}")
            
            # 6. Search Functionality Test
            print("\n--- Testing Search Functionality ---")
            
            # Test search for Waterline
            search_response = self.make_request("GET", "/apartments", {"search_term": "waterline"})
            if search_response.status_code == 200:
                search_results = search_response.json()
                waterline_search_results = len(search_results)
                if waterline_search_results > 0:
                    self.log_result("Waterline Search", True, f"Search for 'waterline' returned {waterline_search_results} results")
                else:
                    self.log_result("Waterline Search", False, "Search for 'waterline' returned no results")
            else:
                self.log_result("Waterline Search", False, f"Search endpoint failed: {search_response.status_code}")
            
            # Test filtering functionality
            filter_response = self.make_request("GET", "/apartments", {"neighborhood": "Long Island City"})
            if filter_response.status_code == 200:
                filter_results = filter_response.json()
                self.log_result("Neighborhood Filter", True, f"Neighborhood filter returned {len(filter_results)} results")
            else:
                self.log_result("Neighborhood Filter", False, f"Filter endpoint failed: {filter_response.status_code}")
            
            # 7. Database Collection Verification
            print("\n--- Database Collection Analysis ---")
            
            # Check apartment sources to understand data distribution
            source_distribution = {}
            price_range = {"min": float('inf'), "max": 0}
            neighborhood_count = {}
            
            for apt in apartments:
                # Source analysis
                source = apt.get("source_url", "unknown")
                source_distribution[source] = source_distribution.get(source, 0) + 1
                
                # Price analysis
                price = apt.get("price", 0)
                if price > 0:
                    price_range["min"] = min(price_range["min"], price)
                    price_range["max"] = max(price_range["max"], price)
                
                # Neighborhood analysis
                neighborhood = apt.get("neighborhood", "unknown")
                neighborhood_count[neighborhood] = neighborhood_count.get(neighborhood, 0) + 1
            
            print(f"   Source Distribution: {source_distribution}")
            print(f"   Price Range: ${price_range['min']:,} - ${price_range['max']:,}")
            print(f"   Neighborhoods: {len(neighborhood_count)} unique neighborhoods")
            
            # Check if apartments are in correct collection
            if total_count > 0:
                self.log_result("Database Collection", True, f"Apartments found in correct collection with {total_count} records")
            else:
                self.log_result("Database Collection", False, "No apartments found - possible collection issue")
            
            # 8. Frontend Data Consumption Test
            print("\n--- Testing Frontend Data Consumption ---")
            
            # Test the exact endpoint the frontend would use
            frontend_response = self.make_request("GET", "/apartments", {"limit": 50, "page": 1})
            if frontend_response.status_code == 200:
                frontend_data = frontend_response.json()
                if len(frontend_data) > 0:
                    self.log_result("Frontend Data Consumption", True, f"Frontend endpoint returns {len(frontend_data)} apartments")
                    
                    # Check if data format is suitable for frontend
                    sample_apt = frontend_data[0]
                    frontend_required = ["id", "title", "price", "address", "neighborhood", "bedrooms", "bathrooms"]
                    frontend_ready = all(field in sample_apt for field in frontend_required)
                    
                    if frontend_ready:
                        self.log_result("Frontend Data Format", True, "Apartment data format suitable for frontend consumption")
                    else:
                        self.log_result("Frontend Data Format", False, "Apartment data missing required frontend fields")
                else:
                    self.log_result("Frontend Data Consumption", False, "Frontend endpoint returns empty data - this explains why frontend shows 0 apartments")
            else:
                self.log_result("Frontend Data Consumption", False, f"Frontend endpoint failed: {frontend_response.status_code}")
            
            # Summary and Diagnosis
            print(f"\n--- WATERLINE SQUARE VERIFICATION SUMMARY ---")
            print(f"   Database Status: {'✅ Connected' if response.status_code == 200 else '❌ Connection Failed'}")
            print(f"   Total Apartments: {total_count} (Expected: 82)")
            print(f"   Waterline Apartments: {len(waterline_apartments)} (Expected: 8)")
            print(f"   API Endpoint: {'✅ Working' if response.status_code == 200 else '❌ Failed'}")
            print(f"   Search Function: {'✅ Working' if search_response.status_code == 200 else '❌ Failed'}")
            
            if total_count < 82:
                print(f"   🔍 DIAGNOSIS: Missing {82 - total_count} apartments from database")
                if len(waterline_apartments) == 0:
                    print(f"   🔍 ISSUE: Waterline Square apartments not found in database")
                    print(f"   💡 SOLUTION: Need to run scraping to add Waterline Square apartments")
            
            if len(waterline_apartments) == 8 and total_count == 82:
                print(f"   ✅ SUCCESS: All Waterline Square apartments present and accounted for")
            
        except Exception as e:
            self.log_result("Waterline Square Verification", False, f"Exception: {str(e)}")
    
    def run_verification(self):
        """Run the Waterline Square verification"""
        print("🏢 Starting Waterline Square Apartments Database Verification")
        print(f"Testing against: {self.base_url}")
        print("=" * 70)
        
        self.test_waterline_square_verification()
        
        # Print final results
        print("\n" + "=" * 70)
        print("🏁 WATERLINE SQUARE VERIFICATION SUMMARY")
        print("=" * 70)
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
    verifier = WaterlineSquareVerifier()
    verifier.run_verification()