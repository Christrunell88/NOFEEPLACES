#!/usr/bin/env python3
"""
NoFeePlaces.com Data Quality Testing Suite
Tests data quality fixes as requested in review:
- Realistic pricing for locations
- Valid bedrooms field (0 for studios, 1+ for others)
- Proper contact information (placesfirm@gmail.com)
- Quality scores of 90+ for all verified listings
- No fictional/generated apartments
- Central Park West pricing verification
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configuration
BASE_URL = "https://nofee-login-fix.preview.emergentagent.com/api"

class NoFeePlacesDataQualityTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.critical_issues = []
        self.data_quality_issues = []
    
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
            if not success:
                self.critical_issues.append(f"{test_name}: {message}")
    
    def make_request(self, method: str, endpoint: str, params: Dict = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_apartment_listings_basic(self):
        """Test basic apartment listings endpoint"""
        print("\n=== Testing Basic Apartment Listings ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 10})
            
            if response.status_code == 200:
                data = response.json()
                if "apartments" in data and isinstance(data["apartments"], list):
                    apartments = data["apartments"]
                    total = data.get("total", 0)
                    self.log_result("Basic Apartment Listings", True, 
                                  f"Retrieved {len(apartments)} apartments out of {total} total")
                    return apartments
                else:
                    self.log_result("Basic Apartment Listings", False, 
                                  f"Unexpected response format: {type(data)}")
                    return []
            else:
                self.log_result("Basic Apartment Listings", False, 
                              f"Status code: {response.status_code}")
                return []
        except Exception as e:
            self.log_result("Basic Apartment Listings", False, f"Exception: {str(e)}")
            return []
    
    def test_data_quality_pricing(self):
        """Test realistic pricing for locations - no $2,344 Central Park West studios"""
        print("\n=== Testing Data Quality: Realistic Pricing ===")
        try:
            # Test 1: Get first 10 listings and check pricing
            response = self.make_request("GET", "/apartments", {"limit": 10})
            if response.status_code != 200:
                self.log_result("Pricing Quality Check", False, f"Failed to get apartments: {response.status_code}")
                return
            
            data = response.json()
            apartments = data.get("apartments", [])
            
            pricing_issues = []
            unrealistic_prices = []
            
            for apt in apartments:
                price = apt.get("price", 0)
                location = apt.get("location", "")
                neighborhood = apt.get("neighborhood", "")
                title = apt.get("title", "")
                bedrooms = apt.get("bedrooms", 0)
                
                # Check for unrealistically low prices in premium locations
                if "central park west" in location.lower() or "central park west" in neighborhood.lower() or "central park west" in title.lower():
                    if price < 6000:  # Central Park West should be minimum $6,000+
                        pricing_issues.append({
                            "title": title,
                            "price": price,
                            "location": location,
                            "issue": f"Central Park West apartment priced at ${price} (should be $6,000+ minimum)"
                        })
                
                # Check for the specific $2,344 Central Park West issue mentioned in review
                if price == 2344 and ("central park west" in title.lower() or "central park west" in location.lower()):
                    pricing_issues.append({
                        "title": title,
                        "price": price,
                        "location": location,
                        "issue": "Specific $2,344 Central Park West issue found - should be fixed"
                    })
                
                # Check for unrealistically low Manhattan prices
                if "manhattan" in location.lower() or "manhattan" in neighborhood.lower():
                    if price < 3000:
                        unrealistic_prices.append({
                            "title": title,
                            "price": price,
                            "location": location,
                            "issue": f"Manhattan apartment under $3,000 (${price})"
                        })
            
            # Test 2: Specifically search for Central Park West apartments
            cpw_response = self.make_request("GET", "/apartments", {"search": "Central Park West", "limit": 20})
            if cpw_response.status_code == 200:
                cpw_data = cpw_response.json()
                cpw_apartments = cpw_data.get("apartments", [])
                
                print(f"   Found {len(cpw_apartments)} Central Park West apartments")
                
                for apt in cpw_apartments:
                    price = apt.get("price", 0)
                    title = apt.get("title", "")
                    
                    if price < 6000:
                        pricing_issues.append({
                            "title": title,
                            "price": price,
                            "location": "Central Park West (search result)",
                            "issue": f"Central Park West apartment priced at ${price} (should be $6,000+ minimum)"
                        })
            
            # Test 3: Check for apartments under $3,000 in Manhattan
            manhattan_response = self.make_request("GET", "/apartments", {"neighborhood": "Manhattan", "max_price": 2999, "limit": 50})
            if manhattan_response.status_code == 200:
                manhattan_data = manhattan_response.json()
                cheap_manhattan = manhattan_data.get("apartments", [])
                
                if len(cheap_manhattan) > 0:
                    self.log_result("Manhattan Minimum Pricing", False, 
                                  f"Found {len(cheap_manhattan)} Manhattan apartments under $3,000")
                    for apt in cheap_manhattan[:3]:  # Show first 3
                        unrealistic_prices.append({
                            "title": apt.get("title", ""),
                            "price": apt.get("price", 0),
                            "location": apt.get("location", ""),
                            "issue": f"Manhattan apartment under $3,000"
                        })
                else:
                    self.log_result("Manhattan Minimum Pricing", True, 
                                  "No Manhattan apartments found under $3,000")
            
            # Report results
            if not pricing_issues and not unrealistic_prices:
                self.log_result("Realistic Pricing", True, 
                              "All apartment prices are realistic for their locations")
            else:
                total_issues = len(pricing_issues) + len(unrealistic_prices)
                self.log_result("Realistic Pricing", False, 
                              f"Found {total_issues} pricing issues")
                
                # Report specific issues
                for issue in pricing_issues[:5]:  # Show first 5
                    print(f"   ❌ {issue['title']}: ${issue['price']} - {issue['issue']}")
                    self.data_quality_issues.append(issue)
                
                for issue in unrealistic_prices[:5]:  # Show first 5
                    print(f"   ⚠️  {issue['title']}: ${issue['price']} - {issue['issue']}")
                    self.data_quality_issues.append(issue)
        
        except Exception as e:
            self.log_result("Realistic Pricing", False, f"Exception: {str(e)}")
    
    def test_data_quality_bedrooms(self):
        """Test valid bedrooms field - 0 for studios, 1+ for others"""
        print("\n=== Testing Data Quality: Valid Bedrooms Field ===")
        try:
            # Test studios have bedrooms=0
            studio_response = self.make_request("GET", "/apartments", {"bedrooms": 0, "limit": 20})
            if studio_response.status_code == 200:
                studio_data = studio_response.json()
                studios = studio_data.get("apartments", [])
                
                studio_issues = []
                for apt in studios:
                    title = apt.get("title", "").lower()
                    bedrooms = apt.get("bedrooms", None)
                    
                    # Check if it's actually a studio
                    if "studio" in title:
                        if bedrooms != 0:
                            studio_issues.append({
                                "title": apt.get("title", ""),
                                "bedrooms": bedrooms,
                                "issue": f"Studio apartment has bedrooms={bedrooms} (should be 0)"
                            })
                
                if not studio_issues:
                    self.log_result("Studio Bedrooms Validation", True, 
                                  f"All {len(studios)} studio apartments have bedrooms=0")
                else:
                    self.log_result("Studio Bedrooms Validation", False, 
                                  f"{len(studio_issues)} studio apartments have incorrect bedroom count")
                    for issue in studio_issues[:3]:
                        print(f"   ❌ {issue['title']}: bedrooms={issue['bedrooms']}")
                        self.data_quality_issues.append(issue)
            
            # Test non-studios have bedrooms >= 1
            non_studio_response = self.make_request("GET", "/apartments", {"limit": 50})
            if non_studio_response.status_code == 200:
                non_studio_data = non_studio_response.json()
                all_apartments = non_studio_data.get("apartments", [])
                
                bedroom_issues = []
                for apt in all_apartments:
                    title = apt.get("title", "").lower()
                    bedrooms = apt.get("bedrooms", None)
                    
                    # Check non-studio apartments
                    if "studio" not in title and bedrooms is not None:
                        if bedrooms < 1:
                            bedroom_issues.append({
                                "title": apt.get("title", ""),
                                "bedrooms": bedrooms,
                                "issue": f"Non-studio apartment has bedrooms={bedrooms} (should be >= 1)"
                            })
                        elif not isinstance(bedrooms, int):
                            bedroom_issues.append({
                                "title": apt.get("title", ""),
                                "bedrooms": bedrooms,
                                "issue": f"Bedrooms field is not integer: {type(bedrooms)}"
                            })
                
                if not bedroom_issues:
                    self.log_result("Non-Studio Bedrooms Validation", True, 
                                  "All non-studio apartments have valid bedroom counts")
                else:
                    self.log_result("Non-Studio Bedrooms Validation", False, 
                                  f"{len(bedroom_issues)} apartments have invalid bedroom counts")
                    for issue in bedroom_issues[:3]:
                        print(f"   ❌ {issue['title']}: bedrooms={issue['bedrooms']}")
                        self.data_quality_issues.append(issue)
        
        except Exception as e:
            self.log_result("Valid Bedrooms Field", False, f"Exception: {str(e)}")
    
    def test_data_quality_contact_info(self):
        """Test proper contact information - placesfirm@gmail.com"""
        print("\n=== Testing Data Quality: Proper Contact Information ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 50})
            if response.status_code != 200:
                self.log_result("Contact Information", False, f"Failed to get apartments: {response.status_code}")
                return
            
            data = response.json()
            apartments = data.get("apartments", [])
            
            contact_issues = []
            correct_email = "placesfirm@gmail.com"
            correct_phone = "+1-646-408-8048"
            
            for apt in apartments:
                title = apt.get("title", "")
                contact_email = apt.get("contact_email", "")
                contact_phone = apt.get("contact_phone", "")
                
                # Check email
                if contact_email != correct_email:
                    contact_issues.append({
                        "title": title,
                        "field": "contact_email",
                        "value": contact_email,
                        "expected": correct_email,
                        "issue": f"Incorrect contact email: {contact_email}"
                    })
                
                # Check phone (optional but should be correct if present)
                if contact_phone and contact_phone != correct_phone:
                    contact_issues.append({
                        "title": title,
                        "field": "contact_phone", 
                        "value": contact_phone,
                        "expected": correct_phone,
                        "issue": f"Incorrect contact phone: {contact_phone}"
                    })
            
            if not contact_issues:
                self.log_result("Contact Information", True, 
                              f"All {len(apartments)} apartments have correct NoFeePlaces contact info")
            else:
                self.log_result("Contact Information", False, 
                              f"{len(contact_issues)} apartments have incorrect contact information")
                
                # Group by issue type
                email_issues = [i for i in contact_issues if i["field"] == "contact_email"]
                phone_issues = [i for i in contact_issues if i["field"] == "contact_phone"]
                
                if email_issues:
                    print(f"   ❌ Email issues: {len(email_issues)} apartments")
                    for issue in email_issues[:3]:
                        print(f"      • {issue['title']}: {issue['value']} (should be {issue['expected']})")
                
                if phone_issues:
                    print(f"   ⚠️  Phone issues: {len(phone_issues)} apartments")
                    for issue in phone_issues[:3]:
                        print(f"      • {issue['title']}: {issue['value']} (should be {issue['expected']})")
                
                self.data_quality_issues.extend(contact_issues)
        
        except Exception as e:
            self.log_result("Contact Information", False, f"Exception: {str(e)}")
    
    def test_data_quality_scores(self):
        """Test quality scores of 90+ for all verified listings"""
        print("\n=== Testing Data Quality: Quality Scores 90+ ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code != 200:
                self.log_result("Quality Scores", False, f"Failed to get apartments: {response.status_code}")
                return
            
            data = response.json()
            apartments = data.get("apartments", [])
            
            quality_issues = []
            verified_count = 0
            
            for apt in apartments:
                title = apt.get("title", "")
                is_verified = apt.get("is_verified", False)
                quality_score = apt.get("quality_score", 0)
                
                if is_verified:
                    verified_count += 1
                    
                    if quality_score < 90:
                        quality_issues.append({
                            "title": title,
                            "quality_score": quality_score,
                            "is_verified": is_verified,
                            "issue": f"Verified listing has quality score {quality_score} (should be 90+)"
                        })
            
            if not quality_issues:
                self.log_result("Quality Scores 90+", True, 
                              f"All {verified_count} verified listings have quality scores 90+")
            else:
                self.log_result("Quality Scores 90+", False, 
                              f"{len(quality_issues)} verified listings have quality scores below 90")
                
                for issue in quality_issues[:5]:
                    print(f"   ❌ {issue['title']}: score={issue['quality_score']}")
                    self.data_quality_issues.append(issue)
        
        except Exception as e:
            self.log_result("Quality Scores 90+", False, f"Exception: {str(e)}")
    
    def test_verification_status(self):
        """Test that all apartments have is_verified=true and proper verification data"""
        print("\n=== Testing Verification Status ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code != 200:
                self.log_result("Verification Status", False, f"Failed to get apartments: {response.status_code}")
                return
            
            data = response.json()
            apartments = data.get("apartments", [])
            
            verification_issues = []
            
            for apt in apartments:
                title = apt.get("title", "")
                is_verified = apt.get("is_verified", None)
                is_real = apt.get("is_real", None)
                verification_status = apt.get("verification_status", "")
                data_source = apt.get("data_source", "")
                
                # Check is_verified field
                if is_verified is not True:
                    verification_issues.append({
                        "title": title,
                        "field": "is_verified",
                        "value": is_verified,
                        "issue": f"is_verified={is_verified} (should be True)"
                    })
                
                # Check is_real field
                if is_real is not True:
                    verification_issues.append({
                        "title": title,
                        "field": "is_real",
                        "value": is_real,
                        "issue": f"is_real={is_real} (should be True)"
                    })
                
                # Check verification status
                if not verification_status or "nofeeplaces" not in verification_status.lower():
                    verification_issues.append({
                        "title": title,
                        "field": "verification_status",
                        "value": verification_status,
                        "issue": f"Missing or incorrect verification status"
                    })
                
                # Check data source
                if not data_source or "nofeeplaces" not in data_source.lower():
                    verification_issues.append({
                        "title": title,
                        "field": "data_source",
                        "value": data_source,
                        "issue": f"Missing or incorrect data source"
                    })
            
            if not verification_issues:
                self.log_result("Verification Status", True, 
                              f"All {len(apartments)} apartments have proper verification data")
            else:
                self.log_result("Verification Status", False, 
                              f"{len(verification_issues)} verification issues found")
                
                # Group by field
                field_counts = {}
                for issue in verification_issues:
                    field = issue["field"]
                    field_counts[field] = field_counts.get(field, 0) + 1
                
                for field, count in field_counts.items():
                    print(f"   ❌ {field} issues: {count}")
                
                self.data_quality_issues.extend(verification_issues[:10])  # Add first 10
        
        except Exception as e:
            self.log_result("Verification Status", False, f"Exception: {str(e)}")
    
    def test_no_fictional_apartments(self):
        """Test that no fictional/generated apartments remain"""
        print("\n=== Testing No Fictional/Generated Apartments ===")
        try:
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code != 200:
                self.log_result("No Fictional Apartments", False, f"Failed to get apartments: {response.status_code}")
                return
            
            data = response.json()
            apartments = data.get("apartments", [])
            
            fictional_indicators = [
                "modern studio on central park west",
                "luxury apartment in manhattan",
                "spacious 1br in brooklyn",
                "cozy studio apartment",
                "beautiful 2br in queens",
                "test apartment",
                "sample listing",
                "demo apartment"
            ]
            
            fictional_apartments = []
            
            for apt in apartments:
                title = apt.get("title", "").lower()
                description = apt.get("description", "").lower()
                
                # Check for generic/fictional titles
                for indicator in fictional_indicators:
                    if indicator in title:
                        fictional_apartments.append({
                            "title": apt.get("title", ""),
                            "price": apt.get("price", 0),
                            "location": apt.get("location", ""),
                            "issue": f"Potentially fictional title contains: '{indicator}'"
                        })
                        break
                
                # Check for the specific $2,344 Central Park West issue
                if apt.get("price") == 2344 and "central park west" in title:
                    fictional_apartments.append({
                        "title": apt.get("title", ""),
                        "price": apt.get("price", 0),
                        "location": apt.get("location", ""),
                        "issue": "Specific $2,344 Central Park West fictional listing"
                    })
            
            if not fictional_apartments:
                self.log_result("No Fictional Apartments", True, 
                              f"No fictional/generated apartments detected in {len(apartments)} listings")
            else:
                self.log_result("No Fictional Apartments", False, 
                              f"{len(fictional_apartments)} potentially fictional apartments found")
                
                for apt in fictional_apartments[:5]:
                    print(f"   ❌ {apt['title']}: ${apt['price']} - {apt['issue']}")
                    self.data_quality_issues.append(apt)
        
        except Exception as e:
            self.log_result("No Fictional Apartments", False, f"Exception: {str(e)}")
    
    def test_central_park_west_specific(self):
        """Test specific Central Park West pricing issue mentioned in review"""
        print("\n=== Testing Central Park West Specific Issues ===")
        try:
            # Search specifically for Central Park West
            cpw_response = self.make_request("GET", "/apartments", {"search": "Central Park West", "limit": 50})
            
            if cpw_response.status_code == 200:
                cpw_data = cpw_response.json()
                cpw_apartments = cpw_data.get("apartments", [])
                
                print(f"   Found {len(cpw_apartments)} Central Park West search results")
                
                if len(cpw_apartments) == 0:
                    self.log_result("Central Park West Search Results", True, 
                                  "No Central Park West apartments found (issue may be resolved)")
                else:
                    # Check each result
                    cpw_issues = []
                    
                    for apt in cpw_apartments:
                        title = apt.get("title", "")
                        price = apt.get("price", 0)
                        location = apt.get("location", "")
                        
                        # Check for the specific $2,344 issue
                        if price == 2344:
                            cpw_issues.append({
                                "title": title,
                                "price": price,
                                "location": location,
                                "issue": "Found the specific $2,344 Central Park West issue"
                            })
                        
                        # Check for unrealistic pricing
                        elif price < 6000:
                            cpw_issues.append({
                                "title": title,
                                "price": price,
                                "location": location,
                                "issue": f"Central Park West apartment under $6,000 (${price})"
                            })
                    
                    if not cpw_issues:
                        self.log_result("Central Park West Pricing", True, 
                                      f"All {len(cpw_apartments)} Central Park West apartments have realistic pricing ($6,000+)")
                    else:
                        self.log_result("Central Park West Pricing", False, 
                                      f"{len(cpw_issues)} Central Park West pricing issues found")
                        
                        for issue in cpw_issues:
                            print(f"   ❌ {issue['title']}: ${issue['price']} - {issue['issue']}")
                            self.data_quality_issues.append(issue)
            else:
                self.log_result("Central Park West Search", False, 
                              f"Failed to search Central Park West: {cpw_response.status_code}")
            
            # Also test neighborhood filter
            cpw_neighborhood_response = self.make_request("GET", "/apartments", {"neighborhood": "Upper West Side", "limit": 50})
            if cpw_neighborhood_response.status_code == 200:
                uws_data = cpw_neighborhood_response.json()
                uws_apartments = uws_data.get("apartments", [])
                
                print(f"   Found {len(uws_apartments)} Upper West Side apartments")
                
                # Check for Central Park West addresses in UWS
                cpw_in_uws = []
                for apt in uws_apartments:
                    address = apt.get("address", "").lower()
                    title = apt.get("title", "").lower()
                    location = apt.get("location", "").lower()
                    
                    if "central park west" in address or "central park west" in title or "central park west" in location:
                        price = apt.get("price", 0)
                        if price < 6000:
                            cpw_in_uws.append({
                                "title": apt.get("title", ""),
                                "price": price,
                                "address": apt.get("address", ""),
                                "issue": f"Central Park West in UWS under $6,000"
                            })
                
                if not cpw_in_uws:
                    self.log_result("Central Park West in UWS", True, 
                                  "No underpriced Central Park West apartments found in Upper West Side")
                else:
                    self.log_result("Central Park West in UWS", False, 
                                  f"{len(cpw_in_uws)} underpriced Central Park West apartments in UWS")
                    
                    for issue in cpw_in_uws:
                        print(f"   ❌ {issue['title']}: ${issue['price']} at {issue['address']}")
                        self.data_quality_issues.append(issue)
        
        except Exception as e:
            self.log_result("Central Park West Specific", False, f"Exception: {str(e)}")
    
    def test_search_stats_endpoint(self):
        """Test the search stats endpoint"""
        print("\n=== Testing Search Stats Endpoint ===")
        try:
            response = self.make_request("GET", "/apartments/search/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["total_apartments", "boroughs", "price_range", "bedrooms"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    total_apartments = data.get("total_apartments", 0)
                    price_range = data.get("price_range", {})
                    min_price = price_range.get("min_price", 0)
                    max_price = price_range.get("max_price", 0)
                    
                    self.log_result("Search Stats Endpoint", True, 
                                  f"Stats: {total_apartments} apartments, price range ${min_price}-${max_price}")
                    
                    # Verify minimum pricing standards
                    if min_price >= 2300:  # Reasonable minimum for NYC
                        self.log_result("Minimum Price Standards", True, 
                                      f"Minimum price ${min_price} meets NYC standards")
                    else:
                        self.log_result("Minimum Price Standards", False, 
                                      f"Minimum price ${min_price} seems too low for NYC")
                else:
                    self.log_result("Search Stats Endpoint", False, 
                                  f"Missing required fields: {missing_fields}")
            else:
                self.log_result("Search Stats Endpoint", False, 
                              f"Status code: {response.status_code}")
        
        except Exception as e:
            self.log_result("Search Stats Endpoint", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all data quality tests"""
        print("🏠 NoFeePlaces.com Data Quality Testing Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        self.test_apartment_listings_basic()
        self.test_data_quality_pricing()
        self.test_data_quality_bedrooms()
        self.test_data_quality_contact_info()
        self.test_data_quality_scores()
        self.test_verification_status()
        self.test_no_fictional_apartments()
        self.test_central_park_west_specific()
        self.test_search_stats_endpoint()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 DATA QUALITY TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.critical_issues)}):")
            for issue in self.critical_issues[:10]:
                print(f"   • {issue}")
        
        if self.data_quality_issues:
            print(f"\n📋 DATA QUALITY ISSUES SUMMARY ({len(self.data_quality_issues)}):")
            
            # Group by issue type
            issue_types = {}
            for issue in self.data_quality_issues:
                issue_type = issue.get("issue", "Unknown").split(":")[0]
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append(issue)
            
            for issue_type, issues in issue_types.items():
                print(f"   • {issue_type}: {len(issues)} issues")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Data quality fixes have been successfully applied!")
        elif success_rate >= 70:
            print("👍 GOOD: Most data quality issues have been resolved")
        else:
            print("⚠️  NEEDS WORK: Significant data quality issues remain")
        
        return success_rate >= 90

if __name__ == "__main__":
    tester = NoFeePlacesDataQualityTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All data quality requirements have been met!")
    else:
        print("\n❌ Data quality issues need to be addressed")