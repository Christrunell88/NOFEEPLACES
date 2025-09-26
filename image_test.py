#!/usr/bin/env python3
"""
Image Enhancement Verification Test
Tests that apartments now have 4 images each instead of 2 images
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "https://nofeeapt.preview.emergentagent.com/api"

class ImageEnhancementTester:
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
    
    def test_apartment_image_enhancement_verification(self):
        """Test apartment image enhancement - verify 4 images per apartment as requested in review"""
        print("\n=== Testing Apartment Image Enhancement Verification ===")
        try:
            # Test GET /api/apartments?limit=10 to check first 10 listings have 4 images each
            print("\n🔍 Testing first 10 apartment listings for 4 images each...")
            response = self.make_request("GET", "/apartments", {"limit": 10})
            if response.status_code != 200:
                self.log_result("Image Enhancement - First 10 Listings", False, f"Failed to get apartments: {response.status_code}")
                return
            
            apartments = response.json()
            if not apartments:
                self.log_result("Image Enhancement - First 10 Listings", False, "No apartments returned")
                return
            
            # Check first 10 apartments for 4 images each
            apartments_with_4_images = 0
            image_count_distribution = {}
            
            for i, apt in enumerate(apartments[:10], 1):
                images = apt.get("images", [])
                image_count = len(images)
                
                if image_count not in image_count_distribution:
                    image_count_distribution[image_count] = 0
                image_count_distribution[image_count] += 1
                
                if image_count == 4:
                    apartments_with_4_images += 1
                    print(f"   ✅ Apartment {i}: {apt.get('title', 'Unknown')[:50]}... - {image_count} images")
                else:
                    print(f"   ❌ Apartment {i}: {apt.get('title', 'Unknown')[:50]}... - {image_count} images (expected 4)")
            
            if apartments_with_4_images == 10:
                self.log_result("Image Enhancement - First 10 Listings", True, f"All 10 apartments have exactly 4 images")
            else:
                self.log_result("Image Enhancement - First 10 Listings", False, 
                              f"Only {apartments_with_4_images}/10 apartments have 4 images. Distribution: {image_count_distribution}")
            
            # Test different apartment types (studios, 1BR, 2BR) to ensure all got updated
            print("\n🏠 Testing different apartment types for image enhancement...")
            apartment_types = [
                {"bedrooms": 0, "type": "Studio"},
                {"bedrooms": 1, "type": "1BR"},
                {"bedrooms": 2, "type": "2BR"}
            ]
            
            for apt_type in apartment_types:
                response = self.make_request("GET", "/apartments", {"bedrooms": apt_type["bedrooms"], "limit": 5})
                if response.status_code == 200:
                    type_apartments = response.json()
                    if type_apartments:
                        type_with_4_images = 0
                        for apt in type_apartments:
                            if len(apt.get("images", [])) == 4:
                                type_with_4_images += 1
                        
                        if type_with_4_images == len(type_apartments):
                            self.log_result(f"Image Enhancement - {apt_type['type']} Apartments", True, 
                                          f"All {len(type_apartments)} {apt_type['type']} apartments have 4 images")
                        else:
                            self.log_result(f"Image Enhancement - {apt_type['type']} Apartments", False, 
                                          f"Only {type_with_4_images}/{len(type_apartments)} {apt_type['type']} apartments have 4 images")
                    else:
                        self.log_result(f"Image Enhancement - {apt_type['type']} Apartments", True, 
                                      f"No {apt_type['type']} apartments found (acceptable)")
                else:
                    self.log_result(f"Image Enhancement - {apt_type['type']} Apartments", False, 
                                  f"Failed to get {apt_type['type']} apartments: {response.status_code}")
            
            # Verify image URLs are properly formatted and from quality sources
            print("\n🔗 Testing image URL quality and formatting...")
            all_apartments_response = self.make_request("GET", "/apartments", {"limit": 50})
            if all_apartments_response.status_code == 200:
                all_apartments = all_apartments_response.json()
                
                url_quality_issues = []
                image_sources = {}
                total_images_checked = 0
                
                for apt in all_apartments:
                    images = apt.get("images", [])
                    for img_url in images:
                        total_images_checked += 1
                        
                        # Check URL format
                        if not img_url or not isinstance(img_url, str):
                            url_quality_issues.append(f"Invalid URL format in {apt.get('title', 'Unknown')}")
                            continue
                        
                        if not (img_url.startswith("http://") or img_url.startswith("https://")):
                            url_quality_issues.append(f"Invalid protocol in {apt.get('title', 'Unknown')}: {img_url[:50]}")
                            continue
                        
                        # Track image sources
                        if "unsplash.com" in img_url:
                            image_sources["Unsplash"] = image_sources.get("Unsplash", 0) + 1
                        elif "pexels.com" in img_url:
                            image_sources["Pexels"] = image_sources.get("Pexels", 0) + 1
                        elif "nestiostatic.com" in img_url:
                            image_sources["Nestio"] = image_sources.get("Nestio", 0) + 1
                        elif "waterline-square.com" in img_url:
                            image_sources["Waterline Square"] = image_sources.get("Waterline Square", 0) + 1
                        elif "gothamwestnyc.com" in img_url:
                            image_sources["Gotham West"] = image_sources.get("Gotham West", 0) + 1
                        else:
                            image_sources["Other"] = image_sources.get("Other", 0) + 1
                
                if not url_quality_issues:
                    self.log_result("Image URL Quality", True, f"All {total_images_checked} image URLs properly formatted")
                else:
                    self.log_result("Image URL Quality", False, f"{len(url_quality_issues)} URL quality issues found")
                
                # Report image source distribution
                print(f"\n📊 Image Source Distribution ({total_images_checked} total images):")
                for source, count in sorted(image_sources.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_images_checked) * 100
                    print(f"   • {source}: {count} images ({percentage:.1f}%)")
                
                self.log_result("Image Source Variety", True, f"Images from {len(image_sources)} different sources")
            
            # Overall assessment of image enhancement
            print("\n📋 OVERALL IMAGE ENHANCEMENT ASSESSMENT:")
            
            # Get comprehensive sample for final assessment
            final_response = self.make_request("GET", "/apartments", {"limit": 100})
            if final_response.status_code == 200:
                final_apartments = final_response.json()
                
                apartments_with_4_images = sum(1 for apt in final_apartments if len(apt.get("images", [])) == 4)
                apartments_with_less_than_4 = sum(1 for apt in final_apartments if len(apt.get("images", [])) < 4)
                apartments_with_more_than_4 = sum(1 for apt in final_apartments if len(apt.get("images", [])) > 4)
                
                total_apartments = len(final_apartments)
                enhancement_success_rate = (apartments_with_4_images / total_apartments) * 100
                
                print(f"   📊 Sample Size: {total_apartments} apartments")
                print(f"   ✅ Apartments with exactly 4 images: {apartments_with_4_images} ({enhancement_success_rate:.1f}%)")
                print(f"   ⚠️  Apartments with less than 4 images: {apartments_with_less_than_4}")
                print(f"   📈 Apartments with more than 4 images: {apartments_with_more_than_4}")
                
                if enhancement_success_rate >= 90:
                    self.log_result("Image Enhancement Success", True, f"Excellent: {enhancement_success_rate:.1f}% of apartments have 4 images")
                elif enhancement_success_rate >= 70:
                    self.log_result("Image Enhancement Success", True, f"Good: {enhancement_success_rate:.1f}% of apartments have 4 images")
                else:
                    self.log_result("Image Enhancement Success", False, f"Poor: Only {enhancement_success_rate:.1f}% of apartments have 4 images")
            
        except Exception as e:
            self.log_result("Apartment Image Enhancement Verification", False, f"Exception: {str(e)}")
    
    def run_tests(self):
        """Run image enhancement tests"""
        print("🚀 Starting Apartment Image Enhancement Verification")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        self.test_apartment_image_enhancement_verification()
        
        print("\n" + "=" * 60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100 if (self.results['passed'] + self.results['failed']) > 0 else 0
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")

if __name__ == "__main__":
    tester = ImageEnhancementTester()
    tester.run_tests()