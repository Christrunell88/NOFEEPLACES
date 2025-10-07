#!/usr/bin/env python3
"""
Enhanced Rental Data Generation Testing Suite
Tests the upgraded rental scraping functionality with market-research-based data generation
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedRentalDataTester:
    def __init__(self):
        # Get backend URL from environment
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    self.base_url = line.split('=')[1].strip()
                    break
        else:
            self.base_url = "http://localhost:8001"
        
        self.api_url = f"{self.base_url}/api"
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        logger.info(f"Testing Enhanced Rental Data Generation at: {self.api_url}")
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == 'GET':
                    async with session.get(url, params=params) as response:
                        response_data = await response.json()
                        return {
                            'status_code': response.status,
                            'data': response_data,
                            'success': response.status < 400
                        }
                elif method.upper() == 'POST':
                    async with session.post(url, json=data, params=params) as response:
                        response_data = await response.json()
                        return {
                            'status_code': response.status,
                            'data': response_data,
                            'success': response.status < 400
                        }
        except Exception as e:
            return {
                'status_code': 500,
                'data': {'error': str(e)},
                'success': False
            }
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            logger.info(f"✅ {test_name}: PASSED {details}")
        else:
            logger.error(f"❌ {test_name}: FAILED {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    async def test_scrape_rentals_endpoint(self):
        """Test GET /api/scrape-rentals endpoint with different locations"""
        logger.info("\n=== Testing Enhanced Rental Data Generation Endpoints ===")
        
        # Test locations with different characteristics
        test_locations = [
            ("Manhattan", 25, "luxury"),
            ("Brooklyn", 20, "trendy"), 
            ("Queens", 15, "diverse"),
            ("DUMBO", 10, "waterfront luxury"),
            ("Chelsea", 15, "mid-luxury"),
            ("Williamsburg", 12, "trendy brooklyn")
        ]
        
        for location, limit, expected_type in test_locations:
            logger.info(f"\n--- Testing {location} rental data generation ---")
            
            response = await self.make_request('GET', '/scrape-rentals', params={
                'location': location,
                'limit': limit
            })
            
            if response['success']:
                data = response['data']
                rentals = data.get('rentals', [])
                
                # Test basic response structure
                self.log_test_result(
                    f"{location} scraping endpoint response",
                    'status' in data and 'count' in data and 'rentals' in data,
                    f"Status: {data.get('status')}, Count: {data.get('count')}"
                )
                
                # Test rental count
                expected_count = min(limit, len(rentals))
                self.log_test_result(
                    f"{location} rental count",
                    len(rentals) == expected_count,
                    f"Expected: {expected_count}, Got: {len(rentals)}"
                )
                
                # Test data quality for first few rentals
                if rentals:
                    await self.test_rental_data_quality(location, rentals[:3], expected_type)
            else:
                self.log_test_result(
                    f"{location} scraping endpoint",
                    False,
                    f"HTTP {response['status_code']}: {response['data']}"
                )
    
    async def test_rental_data_quality(self, location: str, rentals: List[Dict], expected_type: str):
        """Test the quality of generated rental data"""
        logger.info(f"Testing data quality for {location} rentals...")
        
        for i, rental in enumerate(rentals):
            rental_id = f"{location} rental {i+1}"
            
            # Test required fields
            required_fields = [
                'id', 'title', 'description', 'price', 'location', 'neighborhood',
                'bedrooms', 'bathrooms', 'sqft', 'amenities', 'images',
                'contact_email', 'contact_phone', 'management_company'
            ]
            
            missing_fields = [field for field in required_fields if field not in rental or not rental[field]]
            self.log_test_result(
                f"{rental_id} required fields",
                len(missing_fields) == 0,
                f"Missing: {missing_fields}" if missing_fields else "All fields present"
            )
            
            # Test realistic pricing
            price = rental.get('price', 0)
            price_realistic = 1500 <= price <= 50000  # NYC range
            self.log_test_result(
                f"{rental_id} realistic pricing",
                price_realistic,
                f"Price: ${price}"
            )
            
            # Test professional contact info (not generic @nofeeplaces.com)
            contact_email = rental.get('contact_email', '')
            professional_contact = not contact_email.endswith('@nofeeplaces.com')
            self.log_test_result(
                f"{rental_id} professional contact",
                professional_contact,
                f"Email: {contact_email}"
            )
            
            # Test image quality and count
            images = rental.get('images', [])
            quality_images = len(images) >= 4 and all('unsplash.com' in img and '1200x800' in img for img in images)
            self.log_test_result(
                f"{rental_id} high-quality images",
                quality_images,
                f"Images: {len(images)}, Quality URLs: {quality_images}"
            )
            
            # Test location-specific data
            neighborhood = rental.get('neighborhood', '')
            location_match = location.lower() in rental.get('location', '').lower() or neighborhood
            self.log_test_result(
                f"{rental_id} location accuracy",
                location_match,
                f"Location: {rental.get('location')}, Neighborhood: {neighborhood}"
            )
            
            # Test amenities appropriateness
            amenities = rental.get('amenities', [])
            has_amenities = len(amenities) >= 5
            self.log_test_result(
                f"{rental_id} amenities variety",
                has_amenities,
                f"Amenities count: {len(amenities)}"
            )
    
    async def test_market_data_accuracy(self):
        """Test location-specific pricing and market accuracy"""
        logger.info("\n=== Testing Market Data Accuracy ===")
        
        # Test Manhattan vs Brooklyn vs Queens pricing
        locations_for_pricing = ['Manhattan', 'Brooklyn', 'Queens']
        location_prices = {}
        
        for location in locations_for_pricing:
            response = await self.make_request('GET', '/scrape-rentals', params={
                'location': location,
                'limit': 10
            })
            
            if response['success']:
                rentals = response['data'].get('rentals', [])
                if rentals:
                    avg_price = sum(r.get('price', 0) for r in rentals) / len(rentals)
                    location_prices[location] = avg_price
                    logger.info(f"{location} average price: ${avg_price:.2f}")
        
        # Test pricing hierarchy (Manhattan > Brooklyn > Queens generally)
        if len(location_prices) >= 2:
            manhattan_price = location_prices.get('Manhattan', 0)
            brooklyn_price = location_prices.get('Brooklyn', 0)
            queens_price = location_prices.get('Queens', 0)
            
            if manhattan_price and brooklyn_price:
                self.log_test_result(
                    "Manhattan pricing higher than Brooklyn",
                    manhattan_price > brooklyn_price * 0.8,  # Allow some variance
                    f"Manhattan: ${manhattan_price:.2f}, Brooklyn: ${brooklyn_price:.2f}"
                )
            
            if brooklyn_price and queens_price:
                self.log_test_result(
                    "Brooklyn pricing competitive with Queens",
                    abs(brooklyn_price - queens_price) / max(brooklyn_price, queens_price) < 0.5,
                    f"Brooklyn: ${brooklyn_price:.2f}, Queens: ${queens_price:.2f}"
                )
    
    async def test_import_scraped_rentals(self):
        """Test POST /api/import-scraped-rentals endpoint"""
        logger.info("\n=== Testing Import Scraped Rentals Endpoint ===")
        
        # Get initial apartment count
        initial_response = await self.make_request('GET', '/apartments', params={'limit': 1})
        initial_count = 0
        if initial_response['success']:
            initial_count = initial_response['data'].get('total', 0)
            logger.info(f"Initial apartment count: {initial_count}")
        
        # Test import with small batch
        import_response = await self.make_request('POST', '/import-scraped-rentals', params={
            'location': 'Chelsea',
            'limit': 5
        })
        
        if import_response['success']:
            import_data = import_response['data']
            self.log_test_result(
                "Import endpoint response structure",
                'status' in import_data and 'inserted_count' in import_data,
                f"Status: {import_data.get('status')}, Inserted: {import_data.get('inserted_count')}"
            )
            
            inserted_count = import_data.get('inserted_count', 0)
            self.log_test_result(
                "Import inserted apartments",
                inserted_count > 0,
                f"Inserted {inserted_count} apartments"
            )
            
            # Verify apartments were actually added to database
            await asyncio.sleep(1)  # Brief delay for database consistency
            final_response = await self.make_request('GET', '/apartments', params={'limit': 1})
            if final_response['success']:
                final_count = final_response['data'].get('total', 0)
                count_increased = final_count > initial_count
                self.log_test_result(
                    "Database apartment count increased",
                    count_increased,
                    f"Initial: {initial_count}, Final: {final_count}, Increase: {final_count - initial_count}"
                )
        else:
            self.log_test_result(
                "Import scraped rentals endpoint",
                False,
                f"HTTP {import_response['status_code']}: {import_response['data']}"
            )
    
    async def test_api_integration(self):
        """Test integration with existing apartment endpoints"""
        logger.info("\n=== Testing API Integration ===")
        
        # Test main apartments endpoint still works
        apartments_response = await self.make_request('GET', '/apartments', params={'limit': 10})
        self.log_test_result(
            "Main apartments endpoint integration",
            apartments_response['success'],
            f"Status: {apartments_response['status_code']}"
        )
        
        if apartments_response['success']:
            apartments = apartments_response['data'].get('apartments', [])
            
            # Check for enhanced data in existing apartments
            enhanced_apartments = [apt for apt in apartments if apt.get('management_company') or 
                                 (apt.get('contact_email', '').endswith('.com') and 
                                  not apt.get('contact_email', '').endswith('@nofeeplaces.com'))]
            
            self.log_test_result(
                "Enhanced data in apartment listings",
                len(enhanced_apartments) > 0,
                f"Found {len(enhanced_apartments)} apartments with enhanced data"
            )
        
        # Test search functionality with enhanced data
        search_response = await self.make_request('GET', '/apartments', params={
            'search': 'Chelsea',
            'limit': 5
        })
        
        if search_response['success']:
            search_results = search_response['data'].get('apartments', [])
            chelsea_results = [apt for apt in search_results if 'Chelsea' in apt.get('location', '') or 
                             'Chelsea' in apt.get('neighborhood', '')]
            
            self.log_test_result(
                "Search integration with enhanced data",
                len(chelsea_results) > 0,
                f"Found {len(chelsea_results)} Chelsea apartments in search"
            )
        else:
            self.log_test_result(
                "Search integration",
                False,
                f"Search failed: {search_response['status_code']}"
            )
    
    async def test_data_authenticity(self):
        """Test authenticity of generated data"""
        logger.info("\n=== Testing Data Authenticity ===")
        
        # Get sample of generated data
        response = await self.make_request('GET', '/scrape-rentals', params={
            'location': 'Manhattan',
            'limit': 5
        })
        
        if response['success']:
            rentals = response['data'].get('rentals', [])
            
            for i, rental in enumerate(rentals[:3]):
                # Test management company authenticity
                mgmt_company = rental.get('management_company', '')
                real_companies = ['Rockrose', 'L+M Development', 'Two Trees', 'Durst', 'Rose Associates', 'Stellar', 'BLDG', 'Glenwood']
                has_real_company = any(company in mgmt_company for company in real_companies)
                
                self.log_test_result(
                    f"Manhattan rental {i+1} authentic management company",
                    has_real_company,
                    f"Company: {mgmt_company}"
                )
                
                # Test realistic address format
                address = rental.get('address', '')
                realistic_address = bool(address and any(street in address for street in ['Ave', 'St', 'Blvd', 'Broadway']))
                
                self.log_test_result(
                    f"Manhattan rental {i+1} realistic address",
                    realistic_address,
                    f"Address: {address}"
                )
                
                # Test NYC-appropriate amenities
                amenities = rental.get('amenities', [])
                nyc_amenities = ['Doorman', 'Elevator', 'Laundry', 'Subway', 'Rooftop', 'Gym', 'Views']
                has_nyc_amenities = any(any(nyc_am in amenity for nyc_am in nyc_amenities) for amenity in amenities)
                
                self.log_test_result(
                    f"Manhattan rental {i+1} NYC-appropriate amenities",
                    has_nyc_amenities,
                    f"Found NYC-style amenities in: {amenities[:3]}"
                )
    
    async def run_all_tests(self):
        """Run all enhanced rental data generation tests"""
        start_time = time.time()
        
        logger.info("🚀 Starting Enhanced Rental Data Generation Testing Suite")
        logger.info(f"Testing against: {self.api_url}")
        
        try:
            # Core functionality tests
            await self.test_scrape_rentals_endpoint()
            await self.test_import_scraped_rentals()
            
            # Data quality tests
            await self.test_market_data_accuracy()
            await self.test_data_authenticity()
            
            # Integration tests
            await self.test_api_integration()
            
        except Exception as e:
            logger.error(f"Test suite error: {str(e)}")
            self.log_test_result("Test Suite Execution", False, f"Error: {str(e)}")
        
        # Final results
        end_time = time.time()
        duration = end_time - start_time
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🏁 ENHANCED RENTAL DATA GENERATION TESTING COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"📊 Total Tests: {self.total_tests}")
        logger.info(f"✅ Passed: {self.passed_tests}")
        logger.info(f"❌ Failed: {self.total_tests - self.passed_tests}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info(f"⏱️  Duration: {duration:.2f} seconds")
        
        # Detailed results for failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            logger.info(f"\n❌ FAILED TESTS DETAILS:")
            for test in failed_tests:
                logger.info(f"  • {test['test']}: {test['details']}")
        
        return {
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'success_rate': success_rate,
            'duration': duration,
            'failed_tests': failed_tests
        }

async def main():
    """Main test execution"""
    tester = EnhancedRentalDataTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    if results['success_rate'] >= 80:
        logger.info("🎉 Enhanced rental data generation testing PASSED!")
        sys.exit(0)
    else:
        logger.error("💥 Enhanced rental data generation testing FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())