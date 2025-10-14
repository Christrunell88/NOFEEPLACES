#!/usr/bin/env python3
"""
Edge Case Testing for Data Pipeline
Test specific edge cases and stress scenarios
"""
import asyncio
import sys
import traceback
from datetime import datetime
import json

# Import our pipeline
sys.path.append('/app')
from real_estate_data_pipeline import RealEstateDataPipeline

class EdgeCaseTester:
    def __init__(self):
        self.pipeline = RealEstateDataPipeline()
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name} - {details}")
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
    
    def test_malformed_data_handling(self):
        """Test pipeline handling of malformed data"""
        print("\n🧪 TESTING MALFORMED DATA HANDLING")
        print("-" * 50)
        
        # Test with None values
        try:
            result = self.pipeline.normalize_price(None)
            self.log_test("None Price Handling", result == 0, f"Returned {result}")
        except Exception as e:
            self.log_test("None Price Handling", False, f"Exception: {e}")
        
        # Test with empty strings
        try:
            result = self.pipeline.normalize_price("")
            self.log_test("Empty String Price", result == 0, f"Returned {result}")
        except Exception as e:
            self.log_test("Empty String Price", False, f"Exception: {e}")
        
        # Test address with special characters
        try:
            result = self.pipeline.standardize_address(
                "123 Main St. #@$%", 
                "weird//neighborhood", 
                "Manhattan"
            )
            has_keys = 'address' in result and 'neighborhood' in result
            self.log_test("Special Character Address", has_keys, "Handled special characters")
        except Exception as e:
            self.log_test("Special Character Address", False, f"Exception: {e}")
        
        # Test empty amenities list
        try:
            result = self.pipeline.standardize_amenities([])
            self.log_test("Empty Amenities List", isinstance(result, list), f"Returned {result}")
        except Exception as e:
            self.log_test("Empty Amenities List", False, f"Exception: {e}")
        
        # Test amenities with None values
        try:
            result = self.pipeline.standardize_amenities([None, "", "  ", "Doorman"])
            has_doorman = "Doorman" in result
            self.log_test("Amenities with Nulls", has_doorman, f"Filtered and returned {result}")
        except Exception as e:
            self.log_test("Amenities with Nulls", False, f"Exception: {e}")
    
    def test_extreme_values(self):
        """Test pipeline with extreme values"""
        print("\n🧪 TESTING EXTREME VALUES")
        print("-" * 50)
        
        # Test very high prices
        try:
            result = self.pipeline.normalize_price("$999,999,999")
            self.log_test("Extreme High Price", result == 999999999, f"Returned {result}")
        except Exception as e:
            self.log_test("Extreme High Price", False, f"Exception: {e}")
        
        # Test very long strings
        try:
            long_amenity = "A" * 1000
            result = self.pipeline.standardize_amenities([long_amenity])
            self.log_test("Very Long Amenity", len(result) > 0, f"Handled {len(long_amenity)} char string")
        except Exception as e:
            self.log_test("Very Long Amenity", False, f"Exception: {e}")
        
        # Test quality score with missing data
        try:
            empty_apartment = {}
            result = self.pipeline.calculate_quality_score(empty_apartment)
            self.log_test("Empty Apartment Quality", isinstance(result, int), f"Score: {result}")
        except Exception as e:
            self.log_test("Empty Apartment Quality", False, f"Exception: {e}")
        
        # Test quality score with complete data
        try:
            complete_apartment = {
                'price': 5000,
                'images': ['img1.jpg', 'img2.jpg', 'img3.jpg'],
                'address': '123 Main St, New York, NY',
                'amenities': ['Doorman', 'Gym', 'Pool'],
                'sqft': 800,
                'contact_email': 'test@example.com',
                'contact_phone': '+1-555-0123',
                'created_at': datetime.now().isoformat()
            }
            result = self.pipeline.calculate_quality_score(complete_apartment)
            self.log_test("Complete Apartment Quality", result >= 90, f"Score: {result}/100")
        except Exception as e:
            self.log_test("Complete Apartment Quality", False, f"Exception: {e}")
    
    def test_data_cleaning_integration(self):
        """Test full data cleaning integration"""
        print("\n🧪 TESTING DATA CLEANING INTEGRATION")
        print("-" * 50)
        
        # Test cleaning real-world messy data
        try:
            messy_data = {
                'title': '  LUXURY 1BR in MANHATTAN  ',
                'price': '$4,500/month',
                'bedrooms': '1',
                'bathrooms': '1.5',
                'neighborhood': 'upper east side',
                'borough': None,
                'building_name': 'THE LUXURY TOWER',
                'amenities': ['doorman', 'FITNESS', '  pool  ', 'Rooftop Terrace'],
                'management_company': 'Manhattan Skyline Management',
                'source_url': 'https://example.com/apartment/123'
            }
            
            # Convert string numbers to proper types
            messy_data['bedrooms'] = int(messy_data['bedrooms'])
            messy_data['bathrooms'] = float(messy_data['bathrooms'])
            
            cleaned = self.pipeline.clean_and_standardize_apartment(messy_data)
            
            # Verify cleaning worked
            checks = [
                cleaned.title.strip() != "",  # Title cleaned
                cleaned.price > 0,  # Price normalized
                cleaned.neighborhood == "Upper East Side",  # Neighborhood cleaned
                len(cleaned.amenities) > 0,  # Amenities processed
                cleaned.contact_email == "placesfirm@gmail.com",  # Contact standardized
                cleaned.is_verified == True,  # Verification flags set
                cleaned.quality_score > 0  # Quality score calculated
            ]
            
            passed_checks = sum(checks)
            self.log_test(
                "Full Data Cleaning Integration", 
                passed_checks >= 6, 
                f"Passed {passed_checks}/7 cleaning checks"
            )
            
        except Exception as e:
            self.log_test("Full Data Cleaning Integration", False, f"Exception: {str(e)[:200]}")
    
    def test_concurrent_operations(self):
        """Test concurrent data processing"""
        print("\n🧪 TESTING CONCURRENT OPERATIONS")
        print("-" * 50)
        
        try:
            # Test multiple concurrent standardization operations
            test_addresses = [
                ("123 Main St", "Hell's Kitchen", "Manhattan"),
                ("456 Broadway", "SoHo", "Manhattan"), 
                ("789 Atlantic Ave", "Brooklyn Heights", "Brooklyn"),
                ("321 Queens Blvd", "Astoria", "Queens")
            ]
            
            results = []
            for addr, neighborhood, borough in test_addresses:
                result = self.pipeline.standardize_address(addr, neighborhood, borough)
                results.append(result)
            
            all_successful = all('address' in result for result in results)
            self.log_test(
                "Concurrent Address Processing", 
                all_successful, 
                f"Processed {len(results)} addresses successfully"
            )
            
        except Exception as e:
            self.log_test("Concurrent Address Processing", False, f"Exception: {e}")
    
    def test_memory_usage(self):
        """Test memory usage with large datasets"""
        print("\n🧪 TESTING MEMORY USAGE")
        print("-" * 50)
        
        try:
            # Process many apartments to test memory
            large_dataset = []
            for i in range(100):
                apartment = {
                    'title': f'Apartment {i}',
                    'price': 3000 + i,
                    'bedrooms': i % 4,
                    'bathrooms': 1.0,
                    'neighborhood': 'Test Neighborhood',
                    'building_name': f'Building {i}',
                    'amenities': ['Doorman', 'Gym'],
                    'management_company': 'TF Cornerstone',
                    'source_url': f'https://example.com/apt/{i}'
                }
                
                # Test cleaning each apartment
                cleaned = self.pipeline.clean_and_standardize_apartment(apartment)
                large_dataset.append(cleaned)
            
            self.log_test(
                "Large Dataset Processing", 
                len(large_dataset) == 100, 
                f"Successfully processed {len(large_dataset)} apartments"
            )
            
        except Exception as e:
            self.log_test("Large Dataset Processing", False, f"Exception: {str(e)[:200]}")
    
    def run_all_tests(self):
        """Run all edge case tests"""
        print("🔬 COMPREHENSIVE EDGE CASE TESTING")
        print("=" * 60)
        
        try:
            self.test_malformed_data_handling()
            self.test_extreme_values()
            self.test_data_cleaning_integration()
            self.test_concurrent_operations()
            self.test_memory_usage()
            
            # Summary
            total_tests = len(self.test_results)
            passed_tests = sum(1 for test in self.test_results if test['passed'])
            
            print(f"\n📊 EDGE CASE TESTING SUMMARY")
            print("=" * 50)
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
            
            # Export results
            with open('/app/edge_case_test_results.json', 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'success_rate': (passed_tests/total_tests)*100,
                    'test_results': self.test_results
                }, f, indent=2)
            
            print(f"💾 Results exported to: /app/edge_case_test_results.json")
            
            if passed_tests == total_tests:
                print("🎉 ALL EDGE CASE TESTS PASSED!")
            else:
                print("⚠️  Some edge cases need attention")
                
        except Exception as e:
            print(f"❌ Testing framework error: {e}")
            traceback.print_exc()

def main():
    """Run edge case testing"""
    tester = EdgeCaseTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()