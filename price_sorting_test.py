#!/usr/bin/env python3
"""
Price Sorting Test for NoFeePlaces.com Backend API
Tests the apartment listings API after implementing price sorting from lowest to highest
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://nyfee-free.preview.emergentagent.com/api"

class PriceSortingTester:
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
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_api_availability(self):
        """Test if GET /api/apartments endpoint is accessible"""
        print("\n=== Testing API Availability ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 10})
            if response.status_code == 200:
                data = response.json()
                if "apartments" in data and "total" in data:
                    self.log_result("API Availability", True, f"GET /api/apartments endpoint accessible, returns ApartmentListResponse format")
                else:
                    self.log_result("API Availability", False, f"Unexpected response format: {list(data.keys())}")
            else:
                self.log_result("API Availability", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("API Availability", False, f"Exception: {str(e)}")
    
    def test_price_sorting(self):
        """Test that apartments are sorted by price from lowest to highest"""
        print("\n=== Testing Price Sorting (Lowest to Highest) ===")
        try:
            # Get first 50 apartments to test sorting
            response = self.make_request("GET", "/apartments", {"limit": 50})
            if response.status_code != 200:
                self.log_result("Price Sorting", False, f"Failed to get apartments: {response.status_code}")
                return
            
            data = response.json()
            apartments = data.get("apartments", [])
            
            if len(apartments) < 2:
                self.log_result("Price Sorting", False, f"Not enough apartments to test sorting: {len(apartments)}")
                return
            
            # Extract prices and check sorting
            prices = []
            for apt in apartments:
                price = apt.get("price")
                if price is not None:
                    prices.append(float(price))
                else:
                    self.log_result("Price Sorting", False, f"Apartment missing price: {apt.get('title', 'Unknown')}")
                    return
            
            # Check if prices are sorted in ascending order (lowest to highest)
            is_sorted_asc = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
            
            if is_sorted_asc:
                self.log_result("Price Sorting", True, 
                              f"Apartments correctly sorted by price (lowest to highest). Range: ${prices[0]:,.0f} - ${prices[-1]:,.0f}")
                
                # Show first 10 prices to demonstrate progression
                print(f"   First 10 apartment prices: {[f'${p:,.0f}' for p in prices[:10]]}")
            else:
                # Find where sorting breaks
                for i in range(len(prices)-1):
                    if prices[i] > prices[i+1]:
                        self.log_result("Price Sorting", False, 
                                      f"Sorting breaks at position {i}: ${prices[i]:,.0f} > ${prices[i+1]:,.0f}")
                        break
        except Exception as e:
            self.log_result("Price Sorting", False, f"Exception: {str(e)}")
    
    def test_data_integrity(self):
        """Test that apartment data is complete and valid"""
        print("\n=== Testing Data Integrity ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 20})
            if response.status_code != 200:
                self.log_result("Data Integrity", False, f"Failed to get apartments: {response.status_code}")
                return
            
            data = response.json()
            apartments = data.get("apartments", [])
            
            if not apartments:
                self.log_result("Data Integrity", False, "No apartments returned")
                return
            
            # Check required fields
            required_fields = ["id", "title", "price", "bedrooms", "bathrooms", "images"]
            missing_fields = []
            invalid_data = []
            
            for i, apt in enumerate(apartments):
                for field in required_fields:
                    if field not in apt or apt[field] is None:
                        missing_fields.append(f"Apartment {i+1}: missing {field}")
                
                # Validate specific field types
                if "price" in apt:
                    try:
                        price = float(apt["price"])
                        if price <= 0:
                            invalid_data.append(f"Apartment {i+1}: invalid price ${price}")
                    except (ValueError, TypeError):
                        invalid_data.append(f"Apartment {i+1}: price not numeric")
                
                if "images" in apt and not isinstance(apt["images"], list):
                    invalid_data.append(f"Apartment {i+1}: images not a list")
            
            if not missing_fields and not invalid_data:
                self.log_result("Data Integrity", True, f"All {len(apartments)} apartments have complete and valid data")
            else:
                error_msg = f"Data issues found: {len(missing_fields)} missing fields, {len(invalid_data)} invalid values"
                self.log_result("Data Integrity", False, error_msg)
                
                # Show first few issues
                for issue in (missing_fields + invalid_data)[:5]:
                    print(f"   • {issue}")
        except Exception as e:
            self.log_result("Data Integrity", False, f"Exception: {str(e)}")
    
    def test_response_format(self):
        """Test that ApartmentListResponse format is correct"""
        print("\n=== Testing Response Format ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 10})
            if response.status_code != 200:
                self.log_result("Response Format", False, f"Failed to get apartments: {response.status_code}")
                return
            
            data = response.json()
            
            # Check ApartmentListResponse structure
            required_response_fields = ["apartments", "total", "page", "limit", "has_more"]
            missing_response_fields = []
            
            for field in required_response_fields:
                if field not in data:
                    missing_response_fields.append(field)
            
            if missing_response_fields:
                self.log_result("Response Format", False, f"Missing response fields: {missing_response_fields}")
                return
            
            # Validate field types
            if not isinstance(data["apartments"], list):
                self.log_result("Response Format", False, "apartments field is not a list")
                return
            
            if not isinstance(data["total"], int):
                self.log_result("Response Format", False, "total field is not an integer")
                return
            
            if not isinstance(data["page"], int):
                self.log_result("Response Format", False, "page field is not an integer")
                return
            
            if not isinstance(data["limit"], int):
                self.log_result("Response Format", False, "limit field is not an integer")
                return
            
            if not isinstance(data["has_more"], bool):
                self.log_result("Response Format", False, "has_more field is not a boolean")
                return
            
            self.log_result("Response Format", True, "ApartmentListResponse format is correct")
            print(f"   • apartments: {len(data['apartments'])} items")
            print(f"   • total: {data['total']}")
            print(f"   • page: {data['page']}")
            print(f"   • limit: {data['limit']}")
            print(f"   • has_more: {data['has_more']}")
            
        except Exception as e:
            self.log_result("Response Format", False, f"Exception: {str(e)}")
    
    def test_total_count(self):
        """Test that total apartment count is still 316+"""
        print("\n=== Testing Total Count ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 1})
            if response.status_code != 200:
                self.log_result("Total Count", False, f"Failed to get apartments: {response.status_code}")
                return
            
            data = response.json()
            total_count = data.get("total", 0)
            
            if total_count >= 316:
                self.log_result("Total Count", True, f"Total apartment count is {total_count} (meets 316+ requirement)")
            else:
                self.log_result("Total Count", False, f"Total apartment count is {total_count} (below 316 requirement)")
                
        except Exception as e:
            self.log_result("Total Count", False, f"Exception: {str(e)}")
    
    def test_sample_price_range(self):
        """Test first 10 apartments to show price progression"""
        print("\n=== Testing Sample Price Range (First 10 Apartments) ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 10})
            if response.status_code != 200:
                self.log_result("Sample Price Range", False, f"Failed to get apartments: {response.status_code}")
                return
            
            data = response.json()
            apartments = data.get("apartments", [])
            
            if len(apartments) < 10:
                self.log_result("Sample Price Range", False, f"Only {len(apartments)} apartments returned, expected 10")
                return
            
            # Extract first 10 prices and show progression
            prices = []
            apartment_details = []
            
            for i, apt in enumerate(apartments[:10]):
                price = apt.get("price")
                title = apt.get("title", "Unknown")
                bedrooms = apt.get("bedrooms", "Unknown")
                
                if price is not None:
                    prices.append(float(price))
                    apartment_details.append({
                        "position": i + 1,
                        "price": float(price),
                        "title": title[:50] + "..." if len(title) > 50 else title,
                        "bedrooms": bedrooms
                    })
                else:
                    self.log_result("Sample Price Range", False, f"Apartment {i+1} missing price")
                    return
            
            # Check if prices are in ascending order
            is_ascending = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
            
            if is_ascending:
                self.log_result("Sample Price Range", True, f"First 10 apartments show proper price progression")
                
                # Show detailed progression
                print(f"\n   📊 Price Progression (First 10 Apartments):")
                for apt in apartment_details:
                    print(f"   {apt['position']:2d}. ${apt['price']:>7,.0f} - {apt['bedrooms']}BR - {apt['title']}")
                
                # Check if first apartment is around expected cheapest price
                cheapest_price = prices[0]
                if 2000 <= cheapest_price <= 3000:
                    print(f"\n   ✅ Cheapest apartment price ${cheapest_price:,.0f} is in expected range ($2,000-$3,000)")
                else:
                    print(f"\n   ⚠️  Cheapest apartment price ${cheapest_price:,.0f} differs from expected ~$2,344")
                
                # Show price increase
                price_increase = prices[-1] - prices[0]
                print(f"   📈 Price range in first 10: ${prices[0]:,.0f} - ${prices[-1]:,.0f} (${price_increase:,.0f} increase)")
                
            else:
                self.log_result("Sample Price Range", False, "First 10 apartments are not sorted by price")
                
        except Exception as e:
            self.log_result("Sample Price Range", False, f"Exception: {str(e)}")
    
    def test_price_sorting_with_filters(self):
        """Test that price sorting works with other filters"""
        print("\n=== Testing Price Sorting with Filters ===")
        try:
            # Test price sorting with bedroom filter
            response = self.make_request("GET", "/apartments", {"bedrooms": 1, "limit": 20})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", [])
                
                if len(apartments) >= 2:
                    prices = [float(apt.get("price", 0)) for apt in apartments]
                    is_sorted = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
                    
                    if is_sorted:
                        self.log_result("Price Sorting with Bedroom Filter", True, 
                                      f"1BR apartments sorted by price: ${prices[0]:,.0f} - ${prices[-1]:,.0f}")
                    else:
                        self.log_result("Price Sorting with Bedroom Filter", False, "1BR apartments not sorted by price")
                else:
                    self.log_result("Price Sorting with Bedroom Filter", True, f"Only {len(apartments)} 1BR apartments found")
            else:
                self.log_result("Price Sorting with Bedroom Filter", False, f"Failed to get 1BR apartments: {response.status_code}")
            
            # Test price sorting with price range filter
            response = self.make_request("GET", "/apartments", {"min_price": 3000, "max_price": 5000, "limit": 15})
            if response.status_code == 200:
                data = response.json()
                apartments = data.get("apartments", [])
                
                if len(apartments) >= 2:
                    prices = [float(apt.get("price", 0)) for apt in apartments]
                    is_sorted = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
                    in_range = all(3000 <= price <= 5000 for price in prices)
                    
                    if is_sorted and in_range:
                        self.log_result("Price Sorting with Price Range Filter", True, 
                                      f"$3K-$5K apartments sorted by price: ${prices[0]:,.0f} - ${prices[-1]:,.0f}")
                    elif not is_sorted:
                        self.log_result("Price Sorting with Price Range Filter", False, "Price range apartments not sorted by price")
                    else:
                        self.log_result("Price Sorting with Price Range Filter", False, "Some apartments outside price range")
                else:
                    self.log_result("Price Sorting with Price Range Filter", True, f"Only {len(apartments)} apartments in $3K-$5K range")
            else:
                self.log_result("Price Sorting with Price Range Filter", False, f"Failed to get price range apartments: {response.status_code}")
                
        except Exception as e:
            self.log_result("Price Sorting with Filters", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all price sorting tests"""
        print("🏠 NoFeePlaces.com Price Sorting API Testing Suite")
        print("=" * 60)
        print(f"Testing API: {self.base_url}")
        print(f"Test Focus: Price sorting from lowest to highest")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        self.test_api_availability()
        self.test_price_sorting()
        self.test_data_integrity()
        self.test_response_format()
        self.test_total_count()
        self.test_sample_price_range()
        self.test_price_sorting_with_filters()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 PRICE SORTING TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.results['passed']}")
        print(f"❌ Tests Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = PriceSortingTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)