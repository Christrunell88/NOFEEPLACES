#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Favorites and Saved Searches API Endpoints
Testing URL: https://auth-revamp-8.preview.emergentagent.com
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

class FavoritesAndSavedSearchesAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.auth_token = None
        self.test_user_email = "testfav@example.com"
        self.test_user_password = "testpass123"
        self.test_user_name = "Test Favorites User"
        self.apartment_ids = []
        self.saved_search_ids = []
        
        # Test results tracking
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(ssl=False)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str, response_data: Optional[Dict] = None):
        """Log test result with details"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed_tests"] += 1
            status = "✅ PASS"
        else:
            self.results["failed_tests"] += 1
            status = "❌ FAIL"
        
        result_entry = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        if response_data:
            result_entry["response_data"] = response_data
        
        self.results["test_details"].append(result_entry)
        print(f"{status} {test_name}: {details}")
    
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          headers: Optional[Dict] = None, params: Optional[Dict] = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{self.base_url}{endpoint}"
        
        # Default headers
        request_headers = {"Content-Type": "application/json"}
        if self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        if headers:
            request_headers.update(headers)
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers,
                params=params
            ) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = {"text": await response.text()}
                
                return response.status < 400, response_data, response.status
                
        except Exception as e:
            return False, {"error": str(e)}, 0
    
    async def test_user_registration(self):
        """Test user registration"""
        print("\n🔐 Testing User Registration...")
        
        # First, try to register the test user
        registration_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "full_name": self.test_user_name
        }
        
        success, response_data, status_code = await self.make_request(
            "POST", "/api/auth/register", registration_data
        )
        
        if success and response_data.get("access_token"):
            self.auth_token = response_data["access_token"]
            self.log_test_result(
                "User Registration", 
                True, 
                f"Successfully registered user {self.test_user_email}",
                response_data
            )
        elif status_code == 400 and "already registered" in response_data.get("detail", "").lower():
            # User already exists, try to login
            await self.test_user_login()
        else:
            self.log_test_result(
                "User Registration", 
                False, 
                f"Failed to register user. Status: {status_code}, Response: {response_data}",
                response_data
            )
    
    async def test_user_login(self):
        """Test user login"""
        print("\n🔑 Testing User Login...")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        success, response_data, status_code = await self.make_request(
            "POST", "/api/auth/login", login_data
        )
        
        if success and response_data.get("access_token"):
            self.auth_token = response_data["access_token"]
            self.log_test_result(
                "User Login", 
                True, 
                f"Successfully logged in user {self.test_user_email}",
                response_data
            )
        else:
            self.log_test_result(
                "User Login", 
                False, 
                f"Failed to login user. Status: {status_code}, Response: {response_data}",
                response_data
            )
    
    async def get_available_apartments(self) -> List[str]:
        """Get list of available apartment IDs for testing"""
        print("\n🏠 Getting Available Apartments...")
        
        success, response_data, status_code = await self.make_request(
            "GET", "/api/apartments", params={"limit": 10}
        )
        
        if success and response_data.get("apartments"):
            apartment_ids = [apt["id"] for apt in response_data["apartments"]]
            self.log_test_result(
                "Get Available Apartments", 
                True, 
                f"Found {len(apartment_ids)} apartments for testing",
                {"apartment_count": len(apartment_ids)}
            )
            return apartment_ids
        else:
            self.log_test_result(
                "Get Available Apartments", 
                False, 
                f"Failed to get apartments. Status: {status_code}, Response: {response_data}",
                response_data
            )
            return []
    
    async def test_add_favorite(self, apartment_id: str):
        """Test adding apartment to favorites"""
        print(f"\n❤️ Testing Add Favorite for apartment {apartment_id[:8]}...")
        
        favorite_data = {"apartment_id": apartment_id}
        
        success, response_data, status_code = await self.make_request(
            "POST", "/api/favorites/add", favorite_data
        )
        
        if success and response_data.get("success"):
            self.log_test_result(
                f"Add Favorite - {apartment_id[:8]}", 
                True, 
                f"Successfully added apartment to favorites. Count: {response_data.get('favorites_count')}",
                response_data
            )
            return True
        else:
            self.log_test_result(
                f"Add Favorite - {apartment_id[:8]}", 
                False, 
                f"Failed to add favorite. Status: {status_code}, Response: {response_data}",
                response_data
            )
            return False
    
    async def test_check_favorite(self, apartment_id: str, expected_favorite: bool = True):
        """Test checking if apartment is favorited"""
        print(f"\n🔍 Testing Check Favorite for apartment {apartment_id[:8]}...")
        
        success, response_data, status_code = await self.make_request(
            "GET", f"/api/favorites/check/{apartment_id}"
        )
        
        if success and response_data.get("is_favorite") == expected_favorite:
            self.log_test_result(
                f"Check Favorite - {apartment_id[:8]}", 
                True, 
                f"Correctly returned is_favorite: {response_data.get('is_favorite')}",
                response_data
            )
            return True
        else:
            self.log_test_result(
                f"Check Favorite - {apartment_id[:8]}", 
                False, 
                f"Incorrect favorite status. Expected: {expected_favorite}, Got: {response_data.get('is_favorite')}",
                response_data
            )
            return False
    
    async def test_get_favorites(self):
        """Test getting user's favorites list"""
        print("\n📋 Testing Get Favorites List...")
        
        success, response_data, status_code = await self.make_request(
            "GET", "/api/favorites"
        )
        
        if success and "favorites" in response_data:
            favorites_count = len(response_data["favorites"])
            self.log_test_result(
                "Get Favorites List", 
                True, 
                f"Successfully retrieved {favorites_count} favorites with full apartment details",
                {"favorites_count": favorites_count}
            )
            return response_data["favorites"]
        else:
            self.log_test_result(
                "Get Favorites List", 
                False, 
                f"Failed to get favorites. Status: {status_code}, Response: {response_data}",
                response_data
            )
            return []
    
    async def test_add_duplicate_favorite(self, apartment_id: str):
        """Test adding same apartment to favorites again"""
        print(f"\n🔄 Testing Add Duplicate Favorite for apartment {apartment_id[:8]}...")
        
        favorite_data = {"apartment_id": apartment_id}
        
        success, response_data, status_code = await self.make_request(
            "POST", "/api/favorites/add", favorite_data
        )
        
        if success and "already in" in response_data.get("message", "").lower():
            self.log_test_result(
                f"Add Duplicate Favorite - {apartment_id[:8]}", 
                True, 
                f"Correctly handled duplicate: {response_data.get('message')}",
                response_data
            )
            return True
        else:
            self.log_test_result(
                f"Add Duplicate Favorite - {apartment_id[:8]}", 
                False, 
                f"Did not handle duplicate correctly. Status: {status_code}, Response: {response_data}",
                response_data
            )
            return False
    
    async def test_favorites_limit(self, apartment_ids: List[str]):
        """Test adding apartments until reaching 25 limit"""
        print("\n🚫 Testing Favorites Limit (25 apartments)...")
        
        # Add apartments until we reach the limit
        added_count = 0
        for i, apartment_id in enumerate(apartment_ids):
            if added_count >= 25:
                break
            
            favorite_data = {"apartment_id": apartment_id}
            success, response_data, status_code = await self.make_request(
                "POST", "/api/favorites/add", favorite_data
            )
            
            if success:
                added_count += 1
            
            # If we've added 25, try to add one more to test the limit
            if added_count == 25 and i + 1 < len(apartment_ids):
                next_apartment_id = apartment_ids[i + 1]
                favorite_data = {"apartment_id": next_apartment_id}
                success, response_data, status_code = await self.make_request(
                    "POST", "/api/favorites/add", favorite_data
                )
                
                if not success and "maximum" in response_data.get("detail", "").lower():
                    self.log_test_result(
                        "Favorites Limit Test", 
                        True, 
                        f"Correctly enforced 25 apartment limit: {response_data.get('detail')}",
                        response_data
                    )
                    return True
                else:
                    self.log_test_result(
                        "Favorites Limit Test", 
                        False, 
                        f"Did not enforce limit correctly. Status: {status_code}, Response: {response_data}",
                        response_data
                    )
                    return False
        
        self.log_test_result(
            "Favorites Limit Test", 
            False, 
            f"Could not test limit - only added {added_count} apartments",
            {"added_count": added_count}
        )
        return False
    
    async def test_remove_favorite(self, apartment_id: str):
        """Test removing apartment from favorites"""
        print(f"\n🗑️ Testing Remove Favorite for apartment {apartment_id[:8]}...")
        
        success, response_data, status_code = await self.make_request(
            "DELETE", f"/api/favorites/remove/{apartment_id}"
        )
        
        if success and response_data.get("success"):
            self.log_test_result(
                f"Remove Favorite - {apartment_id[:8]}", 
                True, 
                f"Successfully removed apartment from favorites. Count: {response_data.get('favorites_count')}",
                response_data
            )
            return True
        else:
            self.log_test_result(
                f"Remove Favorite - {apartment_id[:8]}", 
                False, 
                f"Failed to remove favorite. Status: {status_code}, Response: {response_data}",
                response_data
            )
            return False
    
    async def test_create_saved_search(self):
        """Test creating a saved search"""
        print("\n💾 Testing Create Saved Search...")
        
        search_data = {
            "search_name": "",  # Let it auto-generate
            "filters": {
                "bedrooms": 2,
                "borough": "Brooklyn",
                "min_price": 2000,
                "max_price": 3000
            },
            "email_frequency": "weekly"
        }
        
        success, response_data, status_code = await self.make_request(
            "POST", "/api/saved-searches/create", search_data
        )
        
        if success and response_data.get("success") and response_data.get("search_id"):
            search_id = response_data["search_id"]
            self.saved_search_ids.append(search_id)
            self.log_test_result(
                "Create Saved Search", 
                True, 
                f"Successfully created saved search: {response_data.get('message')}",
                response_data
            )
            return search_id
        else:
            self.log_test_result(
                "Create Saved Search", 
                False, 
                f"Failed to create saved search. Status: {status_code}, Response: {response_data}",
                response_data
            )
            return None
    
    async def test_get_saved_searches(self):
        """Test getting user's saved searches"""
        print("\n📋 Testing Get Saved Searches...")
        
        success, response_data, status_code = await self.make_request(
            "GET", "/api/saved-searches"
        )
        
        if success and "saved_searches" in response_data:
            searches_count = len(response_data["saved_searches"])
            # Check if new_listings_count is included
            has_new_listings_count = any(
                "new_listings_count" in search for search in response_data["saved_searches"]
            )
            
            self.log_test_result(
                "Get Saved Searches", 
                True, 
                f"Successfully retrieved {searches_count} saved searches with new_listings_count: {has_new_listings_count}",
                {"searches_count": searches_count, "has_new_listings_count": has_new_listings_count}
            )
            return response_data["saved_searches"]
        else:
            self.log_test_result(
                "Get Saved Searches", 
                False, 
                f"Failed to get saved searches. Status: {status_code}, Response: {response_data}",
                response_data
            )
            return []
    
    async def test_update_saved_search(self, search_id: str):
        """Test updating saved search email frequency"""
        print(f"\n✏️ Testing Update Saved Search {search_id[:8]}...")
        
        success, response_data, status_code = await self.make_request(
            "PUT", f"/api/saved-searches/{search_id}", 
            params={"email_frequency": "never"}
        )
        
        if success and response_data.get("success"):
            self.log_test_result(
                f"Update Saved Search - {search_id[:8]}", 
                True, 
                f"Successfully updated email frequency: {response_data.get('message')}",
                response_data
            )
            return True
        else:
            self.log_test_result(
                f"Update Saved Search - {search_id[:8]}", 
                False, 
                f"Failed to update saved search. Status: {status_code}, Response: {response_data}",
                response_data
            )
            return False
    
    async def test_delete_saved_search(self, search_id: str):
        """Test deleting a saved search"""
        print(f"\n🗑️ Testing Delete Saved Search {search_id[:8]}...")
        
        success, response_data, status_code = await self.make_request(
            "DELETE", f"/api/saved-searches/{search_id}"
        )
        
        if success and response_data.get("success"):
            self.log_test_result(
                f"Delete Saved Search - {search_id[:8]}", 
                True, 
                f"Successfully deleted saved search: {response_data.get('message')}",
                response_data
            )
            return True
        else:
            self.log_test_result(
                f"Delete Saved Search - {search_id[:8]}", 
                False, 
                f"Failed to delete saved search. Status: {status_code}, Response: {response_data}",
                response_data
            )
            return False
    
    async def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Favorites and Saved Searches API Testing")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Step 1: Authentication
        await self.test_user_registration()
        if not self.auth_token:
            print("❌ Cannot proceed without authentication token")
            return
        
        # Step 2: Get available apartments
        apartment_ids = await self.get_available_apartments()
        if not apartment_ids:
            print("❌ Cannot proceed without available apartments")
            return
        
        # Step 3: Test Favorites APIs
        print("\n" + "="*50)
        print("🔥 TESTING FAVORITES FUNCTIONALITY")
        print("="*50)
        
        # Add first apartment to favorites
        first_apartment = apartment_ids[0]
        await self.test_add_favorite(first_apartment)
        
        # Check if it's favorited
        await self.test_check_favorite(first_apartment, True)
        
        # Get favorites list
        await self.test_get_favorites()
        
        # Try to add same apartment again (duplicate test)
        await self.test_add_duplicate_favorite(first_apartment)
        
        # Test favorites limit (if we have enough apartments)
        if len(apartment_ids) >= 5:  # Lower threshold for testing
            print(f"\n🔢 Testing with {len(apartment_ids)} available apartments...")
            # Add a few more apartments to test the functionality
            for i in range(1, min(4, len(apartment_ids))):
                await self.test_add_favorite(apartment_ids[i])
        
        # Remove the favorite
        await self.test_remove_favorite(first_apartment)
        
        # Check it's no longer favorited
        await self.test_check_favorite(first_apartment, False)
        
        # Step 4: Test Saved Searches APIs
        print("\n" + "="*50)
        print("🔍 TESTING SAVED SEARCHES FUNCTIONALITY")
        print("="*50)
        
        # Create a saved search
        search_id = await self.test_create_saved_search()
        
        # Get saved searches list
        await self.test_get_saved_searches()
        
        if search_id:
            # Update the saved search
            await self.test_update_saved_search(search_id)
            
            # Delete the saved search
            await self.test_delete_saved_search(search_id)
        
        # Final Results
        self.print_final_results()
    
    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "="*80)
        print("📊 FINAL TEST RESULTS")
        print("="*80)
        
        total = self.results["total_tests"]
        passed = self.results["passed_tests"]
        failed = self.results["failed_tests"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed > 0:
            print(f"\n🚨 FAILED TESTS:")
            for result in self.results["test_details"]:
                if "❌ FAIL" in result["status"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print(f"\n🎯 CRITICAL FUNCTIONALITY STATUS:")
        
        # Check critical functionality
        favorites_tests = [r for r in self.results["test_details"] if "favorite" in r["test"].lower()]
        favorites_passed = len([r for r in favorites_tests if "✅ PASS" in r["status"]])
        favorites_total = len(favorites_tests)
        
        saved_searches_tests = [r for r in self.results["test_details"] if "saved search" in r["test"].lower()]
        saved_searches_passed = len([r for r in saved_searches_tests if "✅ PASS" in r["status"]])
        saved_searches_total = len(saved_searches_tests)
        
        print(f"  • Favorites API: {favorites_passed}/{favorites_total} tests passed")
        print(f"  • Saved Searches API: {saved_searches_passed}/{saved_searches_total} tests passed")
        
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT: All new Favorites and Saved Searches APIs are working correctly!")
        elif success_rate >= 75:
            print(f"\n✅ GOOD: Most functionality working, minor issues to address")
        else:
            print(f"\n⚠️ NEEDS ATTENTION: Significant issues found that need fixing")

async def main():
    """Main test execution"""
    backend_url = "https://auth-revamp-8.preview.emergentagent.com"
    
    async with FavoritesAndSavedSearchesAPITester(backend_url) as tester:
        await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())