#!/usr/bin/env python3
"""
Image Analysis Test for NoFeePlaces.com Backend API
Specifically tests apartment image arrays as requested in review
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "https://nofee-apartments.preview.emergentagent.com/api"

class ImageAnalysisTester:
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
            else:
                response = requests.post(url, json=data, headers=headers)
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_apartment_image_arrays_analysis(self):
        """Test apartment image arrays analysis as requested in review"""
        print("\n=== Testing Apartment Image Arrays Analysis ===")
        try:
            # Get a good sample of apartments (50 as requested)
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code != 200:
                self.log_result("Image Arrays Analysis", False, f"Failed to get apartments: {response.status_code}")
                return
            
            apartments = response.json()
            if not apartments:
                self.log_result("Image Arrays Analysis", False, "No apartments returned")
                return
            
            print(f"\n📊 Analyzing image arrays for {len(apartments)} apartments...")
            
            # Initialize counters and data structures
            image_stats = {
                "no_images": [],
                "single_image": [],
                "multiple_images": [],
                "broken_urls": [],
                "good_variety": [],
                "image_counts": {}
            }
            
            total_images = 0
            apartments_analyzed = 0
            
            # Analyze each apartment's images
            for i, apt in enumerate(apartments, 1):
                apt_id = apt.get("id", f"apartment_{i}")
                apt_title = apt.get("title", "Unknown Title")
                images = apt.get("images", [])
                
                apartments_analyzed += 1
                image_count = len(images) if images else 0
                total_images += image_count
                
                # Count apartments by image count
                if image_count not in image_stats["image_counts"]:
                    image_stats["image_counts"][image_count] = 0
                image_stats["image_counts"][image_count] += 1
                
                # Categorize apartments by image count
                if image_count == 0:
                    image_stats["no_images"].append({
                        "id": apt_id,
                        "title": apt_title,
                        "address": apt.get("address", "Unknown")
                    })
                elif image_count == 1:
                    image_stats["single_image"].append({
                        "id": apt_id,
                        "title": apt_title,
                        "address": apt.get("address", "Unknown"),
                        "image_url": images[0] if images else None
                    })
                else:
                    image_stats["multiple_images"].append({
                        "id": apt_id,
                        "title": apt_title,
                        "address": apt.get("address", "Unknown"),
                        "image_count": image_count
                    })
                
                # Check image quality and accessibility
                broken_images = []
                valid_images = []
                
                for img_url in images:
                    if not img_url or not isinstance(img_url, str):
                        broken_images.append("Invalid URL format")
                        continue
                    
                    # Check if URL is properly formatted
                    if not (img_url.startswith("http://") or img_url.startswith("https://")):
                        broken_images.append(f"Invalid protocol: {img_url[:50]}...")
                        continue
                    
                    # Check for common image domains
                    valid_domains = ["unsplash.com", "pexels.com", "images.unsplash.com", "images.pexels.com", 
                                   "nestiostatic.com", "waterline-square.com", "gothamwestnyc.com", "fortysixfifty.com"]
                    
                    is_valid_domain = any(domain in img_url for domain in valid_domains)
                    if is_valid_domain:
                        valid_images.append(img_url)
                    else:
                        # Still count as valid if it's a proper URL, just note the domain
                        valid_images.append(img_url)
                
                if broken_images:
                    image_stats["broken_urls"].append({
                        "id": apt_id,
                        "title": apt_title,
                        "broken_count": len(broken_images),
                        "total_images": image_count,
                        "issues": broken_images[:3]  # First 3 issues
                    })
                
                # Check for image variety (apartments with 3+ images are considered to have good variety)
                if image_count >= 3:
                    image_stats["good_variety"].append({
                        "id": apt_id,
                        "title": apt_title,
                        "image_count": image_count,
                        "sample_urls": images[:2]  # First 2 URLs as samples
                    })
            
            # Generate comprehensive analysis report
            print(f"\n📈 IMAGE ANALYSIS RESULTS:")
            print(f"   Total apartments analyzed: {apartments_analyzed}")
            print(f"   Total images across all apartments: {total_images}")
            print(f"   Average images per apartment: {total_images/apartments_analyzed:.1f}")
            
            print(f"\n📊 IMAGE COUNT DISTRIBUTION:")
            for count in sorted(image_stats["image_counts"].keys()):
                apartments_with_count = image_stats["image_counts"][count]
                percentage = (apartments_with_count / apartments_analyzed) * 100
                print(f"   {count} images: {apartments_with_count} apartments ({percentage:.1f}%)")
            
            # Report apartments needing more images
            print(f"\n🚨 APARTMENTS NEEDING MORE IMAGES:")
            
            if image_stats["no_images"]:
                print(f"   ❌ NO IMAGES ({len(image_stats['no_images'])} apartments):")
                for apt in image_stats["no_images"][:5]:  # Show first 5
                    print(f"      • {apt['title']} - {apt['address']}")
                if len(image_stats["no_images"]) > 5:
                    print(f"      ... and {len(image_stats['no_images']) - 5} more")
            
            if image_stats["single_image"]:
                print(f"   ⚠️  SINGLE IMAGE ({len(image_stats['single_image'])} apartments):")
                for apt in image_stats["single_image"][:5]:  # Show first 5
                    print(f"      • {apt['title']} - {apt['address']}")
                if len(image_stats["single_image"]) > 5:
                    print(f"      ... and {len(image_stats['single_image']) - 5} more")
            
            # Report apartments with good image variety
            print(f"\n✅ APARTMENTS WITH GOOD IMAGE VARIETY:")
            if image_stats["good_variety"]:
                print(f"   📸 MULTIPLE IMAGES (3+) ({len(image_stats['good_variety'])} apartments):")
                for apt in image_stats["good_variety"][:5]:  # Show first 5
                    print(f"      • {apt['title']} - {apt['image_count']} images")
                if len(image_stats["good_variety"]) > 5:
                    print(f"      ... and {len(image_stats['good_variety']) - 5} more")
            else:
                print("   ⚠️  No apartments found with 3+ images")
            
            # Report broken or problematic URLs
            print(f"\n🔗 IMAGE URL QUALITY:")
            if image_stats["broken_urls"]:
                print(f"   ❌ PROBLEMATIC URLS ({len(image_stats['broken_urls'])} apartments):")
                for apt in image_stats["broken_urls"][:3]:  # Show first 3
                    print(f"      • {apt['title']}: {apt['broken_count']}/{apt['total_images']} issues")
                    for issue in apt['issues']:
                        print(f"        - {issue}")
            else:
                print("   ✅ All image URLs appear to be properly formatted")
            
            # Summary and recommendations
            print(f"\n📋 SUMMARY & RECOMMENDATIONS:")
            
            apartments_needing_images = len(image_stats["no_images"]) + len(image_stats["single_image"])
            apartments_with_good_images = len(image_stats["multiple_images"])
            
            if apartments_needing_images == 0:
                print("   ✅ All apartments have multiple images")
                self.log_result("Image Coverage", True, f"All {apartments_analyzed} apartments have 2+ images")
            else:
                print(f"   📝 {apartments_needing_images} apartments need more images ({apartments_needing_images/apartments_analyzed*100:.1f}%)")
                self.log_result("Image Coverage", False, f"{apartments_needing_images}/{apartments_analyzed} apartments need more images")
            
            if apartments_with_good_images >= apartments_analyzed * 0.7:  # 70% have multiple images
                print("   ✅ Good overall image coverage")
                self.log_result("Image Variety", True, f"{apartments_with_good_images}/{apartments_analyzed} apartments have multiple images")
            else:
                print("   ⚠️  Image coverage could be improved")
                self.log_result("Image Variety", False, f"Only {apartments_with_good_images}/{apartments_analyzed} apartments have multiple images")
            
            if not image_stats["broken_urls"]:
                self.log_result("Image URL Quality", True, "All image URLs are properly formatted")
            else:
                self.log_result("Image URL Quality", False, f"{len(image_stats['broken_urls'])} apartments have URL issues")
            
            # Overall assessment
            overall_score = ((apartments_with_good_images / apartments_analyzed) * 100)
            print(f"\n🎯 OVERALL IMAGE QUALITY SCORE: {overall_score:.1f}%")
            
            if overall_score >= 80:
                self.log_result("Overall Image Analysis", True, f"Excellent image coverage: {overall_score:.1f}%")
            elif overall_score >= 60:
                self.log_result("Overall Image Analysis", True, f"Good image coverage: {overall_score:.1f}%")
            else:
                self.log_result("Overall Image Analysis", False, f"Poor image coverage: {overall_score:.1f}%")
            
            # Specific apartments that need more images
            print(f"\n📝 SPECIFIC APARTMENTS NEEDING MORE IMAGES:")
            all_needing_images = image_stats["no_images"] + image_stats["single_image"]
            for apt in all_needing_images[:10]:  # Show first 10
                current_count = 1 if apt in image_stats["single_image"] else 0
                print(f"   • {apt['title']} ({apt['address']}) - Currently has {current_count} image(s)")
            
            if len(all_needing_images) > 10:
                print(f"   ... and {len(all_needing_images) - 10} more apartments")
            
            # Examples of apartments with good image variety
            print(f"\n✨ EXAMPLES OF APARTMENTS WITH GOOD IMAGE VARIETY:")
            for apt in image_stats["good_variety"][:5]:  # Show first 5 examples
                print(f"   • {apt['title']} - {apt['image_count']} images")
                for i, url in enumerate(apt['sample_urls'], 1):
                    print(f"     {i}. {url}")
            
        except Exception as e:
            self.log_result("Apartment Image Arrays Analysis", False, f"Exception: {str(e)}")
    
    def print_final_results(self):
        """Print final test results"""
        print("\n" + "=" * 80)
        print("🏁 IMAGE ANALYSIS TEST RESULTS")
        print("=" * 80)
        
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.results["errors"]:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = ImageAnalysisTester()
    print("🚀 Starting Apartment Image Arrays Analysis")
    print(f"🔗 Testing API at: {tester.base_url}")
    print("=" * 80)
    
    tester.test_apartment_image_arrays_analysis()
    tester.print_final_results()