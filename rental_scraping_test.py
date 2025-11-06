#!/usr/bin/env python3
"""
Comprehensive Rental Scraping Functionality Test
Tests the new real rental scraping endpoints and data quality
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from frontend .env
BACKEND_URL = "https://nofee-login-fix.preview.emergentagent.com/api"

class RentalScrapingTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.scraped_data = {}
        self.original_apartment_count = 0
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_scrape_rentals_default(self):
        """Test GET /api/scrape-rentals with default parameters"""
        try:
            url = f"{BACKEND_URL}/scrape-rentals"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    if "status" in data and "count" in data and "rentals" in data:
                        rentals = data["rentals"]
                        count = data["count"]
                        
                        if count > 0 and len(rentals) > 0:
                            # Store for later tests
                            self.scraped_data["default"] = rentals
                            
                            # Validate first rental structure
                            first_rental = rentals[0]
                            required_fields = ["id", "title", "price", "location", "bedrooms", "bathrooms", "amenities", "images"]
                            
                            missing_fields = [field for field in required_fields if field not in first_rental]
                            if not missing_fields:
                                self.log_test(
                                    "Scrape Rentals Default Parameters",
                                    True,
                                    f"Successfully scraped {count} rentals with proper structure"
                                )
                                return True
                            else:
                                self.log_test(
                                    "Scrape Rentals Default Parameters",
                                    False,
                                    f"Missing required fields: {missing_fields}"
                                )
                        else:
                            self.log_test(
                                "Scrape Rentals Default Parameters",
                                False,
                                f"No rentals returned (count: {count})"
                            )
                    else:
                        self.log_test(
                            "Scrape Rentals Default Parameters",
                            False,
                            "Invalid response structure"
                        )
                else:
                    self.log_test(
                        "Scrape Rentals Default Parameters",
                        False,
                        f"HTTP {response.status}: {await response.text()}"
                    )
        except Exception as e:
            self.log_test(
                "Scrape Rentals Default Parameters",
                False,
                f"Exception: {str(e)}"
            )
        return False
    
    async def test_scrape_rentals_locations(self):
        """Test GET /api/scrape-rentals with different locations"""
        locations = ["Manhattan", "Brooklyn", "Queens"]
        
        for location in locations:
            try:
                url = f"{BACKEND_URL}/scrape-rentals?location={location}&limit=25"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "rentals" in data and len(data["rentals"]) > 0:
                            rentals = data["rentals"]
                            
                            # Verify location-specific data
                            location_matches = 0
                            for rental in rentals:
                                if location.lower() in rental.get("location", "").lower():
                                    location_matches += 1
                            
                            # Store for later analysis
                            self.scraped_data[location] = rentals
                            
                            success_rate = (location_matches / len(rentals)) * 100
                            self.log_test(
                                f"Scrape Rentals Location: {location}",
                                success_rate >= 80,  # At least 80% should match location
                                f"Scraped {len(rentals)} rentals, {location_matches} match location ({success_rate:.1f}%)"
                            )
                        else:
                            self.log_test(
                                f"Scrape Rentals Location: {location}",
                                False,
                                "No rentals returned"
                            )
                    else:
                        self.log_test(
                            f"Scrape Rentals Location: {location}",
                            False,
                            f"HTTP {response.status}"
                        )
            except Exception as e:
                self.log_test(
                    f"Scrape Rentals Location: {location}",
                    False,
                    f"Exception: {str(e)}"
                )
    
    async def test_scrape_rentals_limits(self):
        """Test GET /api/scrape-rentals with different limit values"""
        limits = [10, 25, 50]
        
        for limit in limits:
            try:
                url = f"{BACKEND_URL}/scrape-rentals?location=NYC&limit={limit}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "rentals" in data and "count" in data:
                            actual_count = len(data["rentals"])
                            reported_count = data["count"]
                            
                            # Allow some flexibility (within 10% or exact match)
                            count_matches = (actual_count == reported_count == limit) or \
                                          (abs(actual_count - limit) <= max(2, limit * 0.1))
                            
                            self.log_test(
                                f"Scrape Rentals Limit: {limit}",
                                count_matches,
                                f"Requested {limit}, got {actual_count} rentals (reported: {reported_count})"
                            )
                        else:
                            self.log_test(
                                f"Scrape Rentals Limit: {limit}",
                                False,
                                "Invalid response structure"
                            )
                    else:
                        self.log_test(
                            f"Scrape Rentals Limit: {limit}",
                            False,
                            f"HTTP {response.status}"
                        )
            except Exception as e:
                self.log_test(
                    f"Scrape Rentals Limit: {limit}",
                    False,
                    f"Exception: {str(e)}"
                )
    
    async def get_current_apartment_count(self):
        """Get current apartment count before import"""
        try:
            url = f"{BACKEND_URL}/apartments?limit=1"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    self.original_apartment_count = data.get("total", 0)
                    print(f"📊 Current apartment count: {self.original_apartment_count}")
                    return True
        except Exception as e:
            print(f"❌ Failed to get apartment count: {str(e)}")
        return False
    
    async def test_import_scraped_rentals(self):
        """Test POST /api/import-scraped-rentals endpoint"""
        try:
            # Test with Manhattan data
            url = f"{BACKEND_URL}/import-scraped-rentals"
            payload = {"location": "Manhattan", "limit": 15}
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success" and "inserted_count" in data:
                        inserted_count = data["inserted_count"]
                        
                        if inserted_count > 0:
                            self.log_test(
                                "Import Scraped Rentals",
                                True,
                                f"Successfully imported {inserted_count} apartments from Manhattan"
                            )
                            
                            # Wait a moment for database to update
                            await asyncio.sleep(2)
                            return True
                        else:
                            self.log_test(
                                "Import Scraped Rentals",
                                False,
                                "No apartments were imported"
                            )
                    else:
                        self.log_test(
                            "Import Scraped Rentals",
                            False,
                            f"Import failed: {data.get('message', 'Unknown error')}"
                        )
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Import Scraped Rentals",
                        False,
                        f"HTTP {response.status}: {error_text}"
                    )
        except Exception as e:
            self.log_test(
                "Import Scraped Rentals",
                False,
                f"Exception: {str(e)}"
            )
        return False
    
    async def test_apartment_count_increase(self):
        """Verify that apartment count increased after import"""
        try:
            url = f"{BACKEND_URL}/apartments?limit=1"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    new_count = data.get("total", 0)
                    
                    increase = new_count - self.original_apartment_count
                    
                    if increase > 0:
                        self.log_test(
                            "Apartment Count Increase",
                            True,
                            f"Apartment count increased by {increase} (from {self.original_apartment_count} to {new_count})"
                        )
                        return True
                    else:
                        self.log_test(
                            "Apartment Count Increase",
                            False,
                            f"No increase detected (was {self.original_apartment_count}, now {new_count})"
                        )
                else:
                    self.log_test(
                        "Apartment Count Increase",
                        False,
                        f"HTTP {response.status}"
                    )
        except Exception as e:
            self.log_test(
                "Apartment Count Increase",
                False,
                f"Exception: {str(e)}"
            )
        return False
    
    async def test_data_quality(self):
        """Test data quality of scraped rentals"""
        if not self.scraped_data:
            self.log_test(
                "Data Quality Check",
                False,
                "No scraped data available for quality testing"
            )
            return
        
        # Test realistic pricing
        all_rentals = []
        for location_data in self.scraped_data.values():
            all_rentals.extend(location_data)
        
        if not all_rentals:
            self.log_test(
                "Data Quality Check",
                False,
                "No rental data to analyze"
            )
            return
        
        # Check pricing realism
        prices = [rental.get("price", 0) for rental in all_rentals]
        valid_prices = [p for p in prices if 1500 <= p <= 50000]  # Reasonable NYC range
        
        price_quality = (len(valid_prices) / len(prices)) * 100 if prices else 0
        
        # Check image URLs
        image_count = 0
        working_images = 0
        
        for rental in all_rentals[:10]:  # Sample first 10
            images = rental.get("images", [])
            image_count += len(images)
            
            for img_url in images:
                if "unsplash.com" in img_url and "w=" in img_url:
                    working_images += 1
        
        image_quality = (working_images / image_count) * 100 if image_count > 0 else 0
        
        # Check amenities variety
        all_amenities = set()
        for rental in all_rentals:
            all_amenities.update(rental.get("amenities", []))
        
        amenity_variety = len(all_amenities)
        
        # Check neighborhood appropriateness
        neighborhood_matches = 0
        for rental in all_rentals:
            location = rental.get("location", "")
            neighborhood = rental.get("neighborhood", "")
            
            if neighborhood and neighborhood in location:
                neighborhood_matches += 1
        
        neighborhood_quality = (neighborhood_matches / len(all_rentals)) * 100
        
        # Overall quality assessment
        overall_quality = (price_quality + image_quality + neighborhood_quality) / 3
        
        self.log_test(
            "Data Quality - Pricing",
            price_quality >= 90,
            f"{price_quality:.1f}% of prices are realistic ($1,500-$50,000)"
        )
        
        self.log_test(
            "Data Quality - Images",
            image_quality >= 80,
            f"{image_quality:.1f}% of images are working Unsplash URLs ({working_images}/{image_count})"
        )
        
        self.log_test(
            "Data Quality - Amenities",
            amenity_variety >= 15,
            f"{amenity_variety} unique amenities found (variety check)"
        )
        
        self.log_test(
            "Data Quality - Neighborhoods",
            neighborhood_quality >= 80,
            f"{neighborhood_quality:.1f}% have appropriate neighborhood-location matching"
        )
        
        self.log_test(
            "Overall Data Quality",
            overall_quality >= 85,
            f"Overall quality score: {overall_quality:.1f}%"
        )
    
    async def test_search_with_imported_data(self):
        """Test that search functionality works with newly imported apartments"""
        try:
            # Test search for Manhattan apartments
            url = f"{BACKEND_URL}/apartments?search=Manhattan&limit=20"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    manhattan_results = data.get("apartments", [])
                    manhattan_count = len(manhattan_results)
                    
                    if manhattan_count > 0:
                        # Check if any results contain Manhattan
                        manhattan_matches = 0
                        for apt in manhattan_results:
                            location = apt.get("location", "").lower()
                            neighborhood = apt.get("neighborhood", "").lower()
                            title = apt.get("title", "").lower()
                            
                            if "manhattan" in location or "manhattan" in neighborhood or "manhattan" in title:
                                manhattan_matches += 1
                        
                        match_rate = (manhattan_matches / manhattan_count) * 100
                        
                        self.log_test(
                            "Search with Imported Data",
                            match_rate >= 50,  # At least 50% should be relevant
                            f"Manhattan search returned {manhattan_count} results, {manhattan_matches} relevant ({match_rate:.1f}%)"
                        )
                    else:
                        self.log_test(
                            "Search with Imported Data",
                            False,
                            "No Manhattan search results found"
                        )
                else:
                    self.log_test(
                        "Search with Imported Data",
                        False,
                        f"HTTP {response.status}"
                    )
        except Exception as e:
            self.log_test(
                "Search with Imported Data",
                False,
                f"Exception: {str(e)}"
            )
    
    async def run_all_tests(self):
        """Run all rental scraping tests"""
        print("🏠 RENTAL SCRAPING FUNCTIONALITY TESTING")
        print("=" * 50)
        
        await self.setup_session()
        
        try:
            # Get baseline apartment count
            await self.get_current_apartment_count()
            
            # Test scraping endpoints
            print("\n📡 Testing Scraping Endpoints...")
            await self.test_scrape_rentals_default()
            await self.test_scrape_rentals_locations()
            await self.test_scrape_rentals_limits()
            
            # Test data quality
            print("\n🔍 Testing Data Quality...")
            await self.test_data_quality()
            
            # Test import functionality
            print("\n📥 Testing Import Functionality...")
            import_success = await self.test_import_scraped_rentals()
            
            if import_success:
                await self.test_apartment_count_increase()
                await self.test_search_with_imported_data()
            
            # Summary
            print("\n" + "=" * 50)
            print("📊 TEST SUMMARY")
            print("=" * 50)
            
            total_tests = len(self.test_results)
            passed_tests = sum(1 for result in self.test_results if result["success"])
            failed_tests = total_tests - passed_tests
            
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests} ✅")
            print(f"Failed: {failed_tests} ❌")
            print(f"Success Rate: {success_rate:.1f}%")
            
            if failed_tests > 0:
                print("\n❌ FAILED TESTS:")
                for result in self.test_results:
                    if not result["success"]:
                        print(f"  • {result['test']}: {result['details']}")
            
            print(f"\n🎯 RENTAL SCRAPING FUNCTIONALITY: {'✅ WORKING' if success_rate >= 80 else '❌ NEEDS ATTENTION'}")
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = RentalScrapingTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())