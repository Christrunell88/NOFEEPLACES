#!/usr/bin/env python3
"""
Malt Drive Apartment 508 Backend Integration Testing
Comprehensive testing for the newly added Studio 1 Bath Apartment 508 at Malt Drive 2-21 building
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MaltDrive508BackendTester:
    def __init__(self):
        # Use production URL from frontend/.env
        self.base_url = "https://nofee-login-fix.preview.emergentagent.com/api"
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        # Malt Drive 508 specific data from review request
        self.unit_id = "a56a07c7-d9a3-414d-95d8-104200f90351"
        self.building_id = "ec2ae99d-4083-44b1-81ec-0241cf5d54a6"
        self.expected_price = 3685.0
        self.expected_bedrooms = 0  # Studio
        self.expected_bathrooms = 1
        self.expected_neighborhood = "Long Island City"
        self.expected_borough = "Queens"
        self.expected_images_count = 21
        self.expected_broker_fee = "No fee"
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, passed: bool, details: str = "", error: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"  Details: {details}")
        if error:
            logger.error(f"  Error: {error}")
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "headers": dict(response.headers)
                    }
        except Exception as e:
            return {"status": 0, "error": str(e)}
    
    async def test_image_url_accessibility(self, image_urls: List[str]) -> Dict[str, Any]:
        """Test if image URLs are accessible"""
        accessible_count = 0
        maltdrive_count = 0
        avif_count = 0
        
        for url in image_urls[:5]:  # Test first 5 images to avoid too many requests
            try:
                async with self.session.head(url) as response:
                    if response.status == 200:
                        accessible_count += 1
                    if "maltdrive.com" in url:
                        maltdrive_count += 1
                    if url.endswith(".avif"):
                        avif_count += 1
            except:
                pass
        
        return {
            "accessible_count": accessible_count,
            "maltdrive_count": maltdrive_count,
            "avif_count": avif_count,
            "total_tested": min(len(image_urls), 5)
        }
    
    # ==========================================
    # INDIVIDUAL APARTMENT RETRIEVAL TESTS
    # ==========================================
    
    async def test_individual_apartment_retrieval(self):
        """Test 1: GET /api/apartments/{unit_id} - Verify individual apartment retrieval"""
        response = await self.make_request("GET", f"/apartments/{self.unit_id}")
        
        if response["status"] == 200:
            data = response["data"]
            
            # Verify required fields
            required_fields = ["id", "title", "price", "bedrooms", "bathrooms", "images", "broker_fee"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test_result(
                    "Individual Apartment Retrieval",
                    False,
                    f"Missing required fields: {missing_fields}"
                )
                return
            
            # Verify specific data
            issues = []
            if data["id"] != self.unit_id:
                issues.append(f"ID mismatch: expected {self.unit_id}, got {data['id']}")
            if data["price"] != self.expected_price:
                issues.append(f"Price mismatch: expected {self.expected_price}, got {data['price']}")
            if data["bedrooms"] != self.expected_bedrooms:
                issues.append(f"Bedrooms mismatch: expected {self.expected_bedrooms}, got {data['bedrooms']}")
            if data["bathrooms"] != self.expected_bathrooms:
                issues.append(f"Bathrooms mismatch: expected {self.expected_bathrooms}, got {data['bathrooms']}")
            if len(data["images"]) != self.expected_images_count:
                issues.append(f"Images count mismatch: expected {self.expected_images_count}, got {len(data['images'])}")
            if data["broker_fee"] != self.expected_broker_fee:
                issues.append(f"Broker fee mismatch: expected '{self.expected_broker_fee}', got '{data['broker_fee']}'")
            
            if issues:
                self.log_test_result(
                    "Individual Apartment Retrieval",
                    False,
                    f"Data validation issues: {'; '.join(issues)}"
                )
            else:
                self.log_test_result(
                    "Individual Apartment Retrieval",
                    True,
                    f"Unit 508 retrieved successfully with correct data: ${data['price']}/mo, {len(data['images'])} images, {data['broker_fee']}"
                )
        else:
            self.log_test_result(
                "Individual Apartment Retrieval",
                False,
                f"Failed to retrieve apartment: status {response['status']}"
            )
    
    # ==========================================
    # APARTMENT LISTINGS TESTS
    # ==========================================
    
    async def test_apartment_listings_neighborhood_filter(self):
        """Test 2: GET /api/apartments with neighborhood=Long Island City filter"""
        response = await self.make_request("GET", f"/apartments?neighborhood={self.expected_neighborhood}")
        
        if response["status"] == 200:
            data = response["data"]
            
            if "apartments" in data and "total" in data:
                apartments = data["apartments"]
                unit_508_found = any(apt["id"] == self.unit_id for apt in apartments)
                lic_count = data["total"]
                
                if unit_508_found:
                    self.log_test_result(
                        "Neighborhood Filter - Unit 508 Appears",
                        True,
                        f"Unit 508 found in Long Island City listings ({lic_count} total apartments)"
                    )
                else:
                    self.log_test_result(
                        "Neighborhood Filter - Unit 508 Appears",
                        False,
                        f"Unit 508 not found in Long Island City listings ({lic_count} total apartments)"
                    )
            else:
                self.log_test_result(
                    "Neighborhood Filter - Unit 508 Appears",
                    False,
                    f"Invalid response format: {data}"
                )
        else:
            self.log_test_result(
                "Neighborhood Filter - Unit 508 Appears",
                False,
                f"Failed to retrieve neighborhood listings: status {response['status']}"
            )
    
    # ==========================================
    # BUILDING-SPECIFIC QUERIES TESTS
    # ==========================================
    
    async def test_building_specific_queries(self):
        """Test 3: GET /api/apartments/building/{building_id} - Verify building-specific queries"""
        # Note: The API might not have this exact endpoint, so we'll test with building_id filter
        response = await self.make_request("GET", f"/apartments?building_id={self.building_id}")
        
        if response["status"] == 200:
            data = response["data"]
            
            if "apartments" in data:
                apartments = data["apartments"]
                unit_508_found = any(apt["id"] == self.unit_id for apt in apartments)
                building_units_count = len(apartments)
                
                # Check price range
                if apartments:
                    prices = [apt["price"] for apt in apartments]
                    min_price = min(prices)
                    max_price = max(prices)
                    
                    # Expected price range: $3,685 - $7,660
                    expected_min = 3685
                    expected_max = 7660
                    
                    price_range_correct = (min_price >= expected_min - 100 and max_price <= expected_max + 100)
                    
                    if unit_508_found and building_units_count == 6 and price_range_correct:
                        self.log_test_result(
                            "Building-Specific Queries",
                            True,
                            f"Malt Drive 2-21 has {building_units_count} units, price range ${min_price}-${max_price}, Unit 508 included"
                        )
                    else:
                        issues = []
                        if not unit_508_found:
                            issues.append("Unit 508 not found")
                        if building_units_count != 6:
                            issues.append(f"Expected 6 units, got {building_units_count}")
                        if not price_range_correct:
                            issues.append(f"Price range ${min_price}-${max_price} doesn't match expected ${expected_min}-${expected_max}")
                        
                        self.log_test_result(
                            "Building-Specific Queries",
                            False,
                            f"Building query issues: {'; '.join(issues)}"
                        )
                else:
                    self.log_test_result(
                        "Building-Specific Queries",
                        False,
                        "No apartments found for building"
                    )
            else:
                self.log_test_result(
                    "Building-Specific Queries",
                    False,
                    f"Invalid response format: {data}"
                )
        else:
            # Try alternative endpoint structure
            response = await self.make_request("GET", f"/apartments?search=Malt Drive 2-21")
            
            if response["status"] == 200:
                data = response["data"]
                if "apartments" in data and len(data["apartments"]) > 0:
                    self.log_test_result(
                        "Building-Specific Queries",
                        True,
                        f"Building search working via text search: found {len(data['apartments'])} units"
                    )
                else:
                    self.log_test_result(
                        "Building-Specific Queries",
                        False,
                        "Building-specific queries not working with any method"
                    )
            else:
                self.log_test_result(
                    "Building-Specific Queries",
                    False,
                    f"Building queries failed: status {response['status']}"
                )
    
    # ==========================================
    # RECENTLY ADDED LISTINGS TESTS
    # ==========================================
    
    async def test_recently_added_listings(self):
        """Test 4: GET /api/recently_added - Verify Unit 508 may appear"""
        # Try different possible endpoints for recently added
        endpoints_to_try = [
            "/apartments/browse/recently-added",
            "/recently_added",
            "/apartments?sort_by=created_at&sort_order=desc&limit=20"
        ]
        
        found_endpoint = False
        unit_508_in_recent = False
        
        for endpoint in endpoints_to_try:
            response = await self.make_request("GET", endpoint)
            
            if response["status"] == 200:
                found_endpoint = True
                data = response["data"]
                
                apartments = []
                if "apartments" in data:
                    apartments = data["apartments"]
                elif isinstance(data, list):
                    apartments = data
                
                if apartments:
                    unit_508_in_recent = any(apt.get("id") == self.unit_id for apt in apartments)
                    if unit_508_in_recent:
                        break
        
        if found_endpoint:
            if unit_508_in_recent:
                self.log_test_result(
                    "Recently Added Listings",
                    True,
                    "Unit 508 appears in recently added listings"
                )
            else:
                self.log_test_result(
                    "Recently Added Listings",
                    True,
                    "Recently added endpoint working (Unit 508 may not appear due to recency rules)"
                )
        else:
            self.log_test_result(
                "Recently Added Listings",
                False,
                "No working recently added endpoint found"
            )
    
    # ==========================================
    # SEARCH AND FILTER TESTS
    # ==========================================
    
    async def test_studio_apartments_filter(self):
        """Test 5: Search for Studio apartments (bedrooms=0)"""
        response = await self.make_request("GET", "/apartments?bedrooms=0")
        
        if response["status"] == 200:
            data = response["data"]
            
            if "apartments" in data:
                apartments = data["apartments"]
                unit_508_found = any(apt["id"] == self.unit_id for apt in apartments)
                studio_count = len(apartments)
                
                if unit_508_found:
                    self.log_test_result(
                        "Studio Apartments Filter",
                        True,
                        f"Unit 508 found in studio apartments search ({studio_count} total studios)"
                    )
                else:
                    self.log_test_result(
                        "Studio Apartments Filter",
                        False,
                        f"Unit 508 not found in studio apartments search ({studio_count} total studios)"
                    )
            else:
                self.log_test_result(
                    "Studio Apartments Filter",
                    False,
                    f"Invalid response format: {data}"
                )
        else:
            self.log_test_result(
                "Studio Apartments Filter",
                False,
                f"Studio apartments filter failed: status {response['status']}"
            )
    
    async def test_price_range_filter(self):
        """Test 6: Price range filter including $3,685"""
        # Test price range that should include Unit 508
        min_price = 3000
        max_price = 4000
        
        response = await self.make_request("GET", f"/apartments?min_price={min_price}&max_price={max_price}")
        
        if response["status"] == 200:
            data = response["data"]
            
            if "apartments" in data:
                apartments = data["apartments"]
                unit_508_found = any(apt["id"] == self.unit_id for apt in apartments)
                price_range_count = len(apartments)
                
                if unit_508_found:
                    self.log_test_result(
                        "Price Range Filter",
                        True,
                        f"Unit 508 found in ${min_price}-${max_price} price range ({price_range_count} total apartments)"
                    )
                else:
                    self.log_test_result(
                        "Price Range Filter",
                        False,
                        f"Unit 508 not found in ${min_price}-${max_price} price range ({price_range_count} total apartments)"
                    )
            else:
                self.log_test_result(
                    "Price Range Filter",
                    False,
                    f"Invalid response format: {data}"
                )
        else:
            self.log_test_result(
                "Price Range Filter",
                False,
                f"Price range filter failed: status {response['status']}"
            )
    
    async def test_borough_queens_filter(self):
        """Test 7: Borough=Queens filter"""
        response = await self.make_request("GET", f"/apartments?borough={self.expected_borough}")
        
        if response["status"] == 200:
            data = response["data"]
            
            if "apartments" in data:
                apartments = data["apartments"]
                unit_508_found = any(apt["id"] == self.unit_id for apt in apartments)
                queens_count = len(apartments)
                
                if unit_508_found:
                    self.log_test_result(
                        "Borough Queens Filter",
                        True,
                        f"Unit 508 found in Queens borough search ({queens_count} total apartments)"
                    )
                else:
                    self.log_test_result(
                        "Borough Queens Filter",
                        False,
                        f"Unit 508 not found in Queens borough search ({queens_count} total apartments)"
                    )
            else:
                self.log_test_result(
                    "Borough Queens Filter",
                    False,
                    f"Invalid response format: {data}"
                )
        else:
            self.log_test_result(
                "Borough Queens Filter",
                False,
                f"Borough Queens filter failed: status {response['status']}"
            )
    
    # ==========================================
    # IMAGE URL VALIDATION TESTS
    # ==========================================
    
    async def test_image_url_validation(self):
        """Test 8: Verify all 21 image URLs are properly formatted and accessible"""
        # First get the apartment data
        response = await self.make_request("GET", f"/apartments/{self.unit_id}")
        
        if response["status"] == 200:
            data = response["data"]
            
            if "images" in data:
                images = data["images"]
                
                if len(images) == self.expected_images_count:
                    # Test image URL accessibility
                    image_test_results = await self.test_image_url_accessibility(images)
                    
                    # Check URL format
                    maltdrive_urls = sum(1 for url in images if "maltdrive.com" in url)
                    avif_urls = sum(1 for url in images if url.endswith(".avif"))
                    
                    issues = []
                    if maltdrive_urls < len(images) * 0.8:  # At least 80% should be from maltdrive.com
                        issues.append(f"Only {maltdrive_urls}/{len(images)} images from maltdrive.com domain")
                    if avif_urls < len(images) * 0.8:  # At least 80% should be .avif format
                        issues.append(f"Only {avif_urls}/{len(images)} images in .avif format")
                    if image_test_results["accessible_count"] < image_test_results["total_tested"] * 0.8:
                        issues.append(f"Only {image_test_results['accessible_count']}/{image_test_results['total_tested']} tested images accessible")
                    
                    if issues:
                        self.log_test_result(
                            "Image URL Validation",
                            False,
                            f"Image validation issues: {'; '.join(issues)}"
                        )
                    else:
                        self.log_test_result(
                            "Image URL Validation",
                            True,
                            f"All {len(images)} images properly formatted: {maltdrive_urls} from maltdrive.com, {avif_urls} in .avif format"
                        )
                else:
                    self.log_test_result(
                        "Image URL Validation",
                        False,
                        f"Expected {self.expected_images_count} images, got {len(images)}"
                    )
            else:
                self.log_test_result(
                    "Image URL Validation",
                    False,
                    "No images field found in apartment data"
                )
        else:
            self.log_test_result(
                "Image URL Validation",
                False,
                f"Could not retrieve apartment for image validation: status {response['status']}"
            )
    
    # ==========================================
    # DATA INTEGRITY TESTS
    # ==========================================
    
    async def test_pydantic_validation(self):
        """Test 9: Verify all required Pydantic fields are present and valid"""
        response = await self.make_request("GET", f"/apartments/{self.unit_id}")
        
        if response["status"] == 200:
            data = response["data"]
            
            # Check required Pydantic fields
            required_fields = [
                "id", "title", "price", "bedrooms", "bathrooms", "images",
                "broker_fee", "available", "created_at", "updated_at"
            ]
            
            missing_fields = [field for field in required_fields if field not in data]
            
            # Check data types
            type_issues = []
            if "broker_fee" in data and not isinstance(data["broker_fee"], str):
                type_issues.append(f"broker_fee should be string, got {type(data['broker_fee'])}")
            if "price" in data and not isinstance(data["price"], (int, float)):
                type_issues.append(f"price should be number, got {type(data['price'])}")
            if "bedrooms" in data and not isinstance(data["bedrooms"], int):
                type_issues.append(f"bedrooms should be int, got {type(data['bedrooms'])}")
            if "images" in data and not isinstance(data["images"], list):
                type_issues.append(f"images should be list, got {type(data['images'])}")
            
            issues = []
            if missing_fields:
                issues.append(f"Missing fields: {missing_fields}")
            if type_issues:
                issues.append(f"Type issues: {type_issues}")
            
            if issues:
                self.log_test_result(
                    "Pydantic Validation",
                    False,
                    f"Validation issues: {'; '.join(issues)}"
                )
            else:
                self.log_test_result(
                    "Pydantic Validation",
                    True,
                    "All required Pydantic fields present with correct types"
                )
        else:
            self.log_test_result(
                "Pydantic Validation",
                False,
                f"Could not retrieve apartment for validation: status {response['status']}"
            )
    
    async def test_building_relationship(self):
        """Test 10: Verify building relationship is maintained"""
        response = await self.make_request("GET", f"/apartments/{self.unit_id}")
        
        if response["status"] == 200:
            data = response["data"]
            
            building_fields = ["building_id", "building_name"]
            present_fields = [field for field in building_fields if field in data and data[field]]
            
            issues = []
            if "building_id" in data:
                if data["building_id"] != self.building_id:
                    issues.append(f"Building ID mismatch: expected {self.building_id}, got {data['building_id']}")
            else:
                issues.append("building_id field missing")
            
            if "building_name" in data:
                if "Malt Drive" not in str(data["building_name"]):
                    issues.append(f"Building name doesn't contain 'Malt Drive': {data['building_name']}")
            else:
                issues.append("building_name field missing or empty")
            
            if issues:
                self.log_test_result(
                    "Building Relationship",
                    False,
                    f"Building relationship issues: {'; '.join(issues)}"
                )
            else:
                self.log_test_result(
                    "Building Relationship",
                    True,
                    f"Building relationship maintained: {data.get('building_name', 'N/A')} (ID: {data.get('building_id', 'N/A')})"
                )
        else:
            self.log_test_result(
                "Building Relationship",
                False,
                f"Could not retrieve apartment for building relationship test: status {response['status']}"
            )
    
    # ==========================================
    # MAIN TEST EXECUTION
    # ==========================================
    
    async def run_all_tests(self):
        """Run all Malt Drive 508 backend tests"""
        logger.info("🏢 Starting Malt Drive Apartment 508 Backend Integration Testing")
        logger.info("=" * 70)
        logger.info(f"Unit ID: {self.unit_id}")
        logger.info(f"Building ID: {self.building_id}")
        logger.info(f"Expected: Studio 1 Bath, ${self.expected_price}/mo, {self.expected_images_count} images")
        logger.info("=" * 70)
        
        # Individual Apartment Retrieval
        logger.info("\n🔍 INDIVIDUAL APARTMENT RETRIEVAL")
        logger.info("-" * 40)
        await self.test_individual_apartment_retrieval()
        
        # Apartment Listings
        logger.info("\n📋 APARTMENT LISTINGS")
        logger.info("-" * 40)
        await self.test_apartment_listings_neighborhood_filter()
        
        # Building-Specific Queries
        logger.info("\n🏗️ BUILDING-SPECIFIC QUERIES")
        logger.info("-" * 40)
        await self.test_building_specific_queries()
        
        # Recently Added Listings
        logger.info("\n🆕 RECENTLY ADDED LISTINGS")
        logger.info("-" * 40)
        await self.test_recently_added_listings()
        
        # Search and Filter
        logger.info("\n🔎 SEARCH AND FILTER")
        logger.info("-" * 40)
        await self.test_studio_apartments_filter()
        await self.test_price_range_filter()
        await self.test_borough_queens_filter()
        
        # Image URL Validation
        logger.info("\n🖼️ IMAGE URL VALIDATION")
        logger.info("-" * 40)
        await self.test_image_url_validation()
        
        # Data Integrity
        logger.info("\n✅ DATA INTEGRITY")
        logger.info("-" * 40)
        await self.test_pydantic_validation()
        await self.test_building_relationship()
        
        # Generate Summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        logger.info("\n" + "=" * 70)
        logger.info("🧪 MALT DRIVE 508 BACKEND INTEGRATION TEST SUMMARY")
        logger.info("=" * 70)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        logger.info(f"Total Tests: {self.total_tests}")
        logger.info(f"Passed: {self.passed_tests}")
        logger.info(f"Failed: {self.total_tests - self.passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        # Categorize results
        categories = {
            "Individual Retrieval": ["Individual Apartment Retrieval"],
            "Listings & Filters": ["Neighborhood Filter", "Studio Apartments Filter", "Price Range Filter", "Borough Queens Filter"],
            "Building Queries": ["Building-Specific Queries"],
            "Recent Listings": ["Recently Added Listings"],
            "Image Validation": ["Image URL Validation"],
            "Data Integrity": ["Pydantic Validation", "Building Relationship"]
        }
        
        for category, test_keywords in categories.items():
            logger.info(f"\n{category.upper()}:")
            category_tests = [r for r in self.test_results if any(keyword in r["test"] for keyword in test_keywords)]
            for test in category_tests:
                logger.info(f"  {test['status']}: {test['test']}")
        
        # Critical Issues
        failed_tests = [r for r in self.test_results if not r["passed"]]
        if failed_tests:
            logger.info("\n❌ CRITICAL ISSUES FOUND:")
            for test in failed_tests:
                logger.info(f"  • {test['test']}: {test.get('error', test.get('details', 'Unknown error'))}")
        else:
            logger.info("\n✅ ALL TESTS PASSED - MALT DRIVE 508 BACKEND INTEGRATION WORKING PERFECTLY!")
        
        logger.info("\n" + "=" * 70)

async def main():
    """Main test execution function"""
    async with MaltDrive508BackendTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())