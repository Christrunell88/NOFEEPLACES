#!/usr/bin/env python3
"""
Apartment Count Investigation Script
Specifically testing the missing apartment listings issue
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "https://9baa349b-86eb-4d82-b63e-aa2a6cd5417c.preview.emergentagent.com/api"

class ApartmentCountInvestigator:
    def __init__(self):
        self.base_url = BASE_URL
        self.results = []
    
    def log_result(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if data:
            print(f"   Data: {data}")
        
        self.results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "data": data
        })
    
    def make_request(self, method: str, endpoint: str, params: Dict = None) -> requests.Response:
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, json=params, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_basic_apartment_count(self):
        """Test basic apartment count with high limit"""
        print("\n=== Testing Basic Apartment Count ===")
        try:
            # Get apartments with high limit to ensure we get all
            response = self.make_request("GET", "/apartments", {"limit": 100})
            
            if response.status_code == 200:
                apartments = response.json()
                total_count = len(apartments)
                
                self.log_result("Basic Apartment Count", True, 
                              f"Found {total_count} apartments total", 
                              {"total_apartments": total_count})
                
                # Check if we have the expected 30 apartments
                if total_count == 30:
                    self.log_result("Expected Count Check", True, "Found exactly 30 apartments as expected")
                elif total_count == 20:
                    self.log_result("Expected Count Check", False, "Only found 20 apartments - missing 10 TFC listings")
                else:
                    self.log_result("Expected Count Check", False, f"Unexpected count: {total_count} (expected 30)")
                
                return apartments
            else:
                self.log_result("Basic Apartment Count", False, f"Status code: {response.status_code}")
                return []
        except Exception as e:
            self.log_result("Basic Apartment Count", False, f"Exception: {str(e)}")
            return []
    
    def test_pagination_limits(self):
        """Test if pagination is limiting results"""
        print("\n=== Testing Pagination Limits ===")
        try:
            # Test default pagination (should be 20 by default)
            response = self.make_request("GET", "/apartments")
            
            if response.status_code == 200:
                apartments_default = response.json()
                default_count = len(apartments_default)
                
                self.log_result("Default Pagination", True, 
                              f"Default request returned {default_count} apartments",
                              {"default_count": default_count})
                
                # Test with explicit limit of 50
                response = self.make_request("GET", "/apartments", {"limit": 50})
                if response.status_code == 200:
                    apartments_50 = response.json()
                    limit_50_count = len(apartments_50)
                    
                    self.log_result("Limit 50 Test", True, 
                                  f"Limit 50 request returned {limit_50_count} apartments",
                                  {"limit_50_count": limit_50_count})
                    
                    if limit_50_count > default_count:
                        self.log_result("Pagination Issue Found", False, 
                                      f"Default pagination is limiting results: {default_count} vs {limit_50_count}")
                    else:
                        self.log_result("Pagination Check", True, "No pagination limiting issue found")
                
            else:
                self.log_result("Pagination Test", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Pagination Test", False, f"Exception: {str(e)}")
    
    def test_scraping_endpoint(self):
        """Test the scraping endpoint to ensure data is populated"""
        print("\n=== Testing Scraping Endpoint ===")
        try:
            response = self.make_request("POST", "/admin/scrape")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Scraping Endpoint", True, 
                              f"Scraping completed: {data.get('message', 'No message')}")
                
                # Wait a moment for data to be inserted
                import time
                time.sleep(2)
                
                # Check count after scraping
                response = self.make_request("GET", "/apartments", {"limit": 100})
                if response.status_code == 200:
                    apartments = response.json()
                    post_scrape_count = len(apartments)
                    
                    self.log_result("Post-Scrape Count", True, 
                                  f"After scraping: {post_scrape_count} apartments",
                                  {"post_scrape_count": post_scrape_count})
                    
                    return apartments
            else:
                self.log_result("Scraping Endpoint", False, f"Status code: {response.status_code}")
                return []
        except Exception as e:
            self.log_result("Scraping Endpoint", False, f"Exception: {str(e)}")
            return []
    
    def analyze_apartment_sources(self, apartments):
        """Analyze apartment sources to identify TFC listings"""
        print("\n=== Analyzing Apartment Sources ===")
        try:
            if not apartments:
                self.log_result("Source Analysis", False, "No apartments to analyze")
                return
            
            # Count by source URL
            source_counts = {}
            tfc_apartments = []
            
            for apt in apartments:
                source = apt.get("source_url", "unknown")
                source_counts[source] = source_counts.get(source, 0) + 1
                
                if source == "https://tfc.com":
                    tfc_apartments.append(apt)
            
            self.log_result("Source Analysis", True, 
                          f"Found {len(source_counts)} different sources",
                          {"source_counts": source_counts})
            
            # Specifically check TFC count
            tfc_count = len(tfc_apartments)
            if tfc_count == 10:
                self.log_result("TFC Count Check", True, f"Found exactly 10 TFC listings")
            elif tfc_count == 0:
                self.log_result("TFC Count Check", False, "No TFC listings found - this is the issue!")
            else:
                self.log_result("TFC Count Check", False, f"Found {tfc_count} TFC listings (expected 10)")
            
            # List TFC apartment titles for verification
            if tfc_apartments:
                tfc_titles = [apt.get("title", "Unknown") for apt in tfc_apartments[:5]]  # First 5
                self.log_result("TFC Listings Sample", True, 
                              f"Sample TFC listings: {', '.join(tfc_titles)}")
            
            return tfc_apartments
            
        except Exception as e:
            self.log_result("Source Analysis", False, f"Exception: {str(e)}")
            return []
    
    def test_database_stats(self):
        """Test the database statistics endpoint"""
        print("\n=== Testing Database Statistics ===")
        try:
            response = self.make_request("GET", "/apartments/search/stats")
            
            if response.status_code == 200:
                stats = response.json()
                total_from_stats = stats.get("total_apartments", 0)
                
                self.log_result("Database Stats", True, 
                              f"Stats endpoint reports {total_from_stats} total apartments",
                              {"stats": stats})
                
                if total_from_stats == 30:
                    self.log_result("Stats Count Check", True, "Stats show 30 apartments as expected")
                elif total_from_stats == 20:
                    self.log_result("Stats Count Check", False, "Stats show only 20 apartments - missing 10")
                else:
                    self.log_result("Stats Count Check", False, f"Stats show {total_from_stats} apartments (expected 30)")
                
            else:
                self.log_result("Database Stats", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Database Stats", False, f"Exception: {str(e)}")
    
    def test_filtering_effects(self):
        """Test if any default filtering is affecting results"""
        print("\n=== Testing Filtering Effects ===")
        try:
            # Test with no filters
            response = self.make_request("GET", "/apartments", {"limit": 100})
            if response.status_code == 200:
                no_filter_count = len(response.json())
                self.log_result("No Filters", True, f"No filters: {no_filter_count} apartments")
            
            # Test with explicit is_no_fee filter (this might be applied by default)
            # Note: The API code shows it filters by is_no_fee: True by default
            
            # Test different boroughs to see if any are missing
            boroughs = ["Manhattan", "Brooklyn", "Queens"]
            borough_counts = {}
            
            for borough in boroughs:
                response = self.make_request("GET", "/apartments", {"borough": borough, "limit": 100})
                if response.status_code == 200:
                    count = len(response.json())
                    borough_counts[borough] = count
                    self.log_result(f"Borough Filter - {borough}", True, f"{borough}: {count} apartments")
            
            total_by_borough = sum(borough_counts.values())
            self.log_result("Borough Total", True, 
                          f"Total across boroughs: {total_by_borough}",
                          {"borough_counts": borough_counts})
            
        except Exception as e:
            self.log_result("Filtering Effects", False, f"Exception: {str(e)}")
    
    def run_investigation(self):
        """Run the complete investigation"""
        print("🔍 Starting Apartment Count Investigation")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Step 1: Check basic count
        apartments = self.test_basic_apartment_count()
        
        # Step 2: Test pagination limits
        self.test_pagination_limits()
        
        # Step 3: Test scraping endpoint
        apartments_after_scrape = self.test_scraping_endpoint()
        if apartments_after_scrape:
            apartments = apartments_after_scrape
        
        # Step 4: Analyze sources
        tfc_apartments = self.analyze_apartment_sources(apartments)
        
        # Step 5: Check database stats
        self.test_database_stats()
        
        # Step 6: Test filtering effects
        self.test_filtering_effects()
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_apartments = len(apartments) if apartments else 0
        print(f"📊 Total Apartments Found: {total_apartments}")
        print(f"🎯 Expected: 30 apartments")
        print(f"❓ Missing: {30 - total_apartments} apartments")
        
        if tfc_apartments:
            print(f"🏢 TFC Listings Found: {len(tfc_apartments)}")
        else:
            print("🏢 TFC Listings Found: 0 (THIS IS THE ISSUE!)")
        
        # Identify the root cause
        if total_apartments == 20:
            print("\n🔍 ROOT CAUSE ANALYSIS:")
            print("   • Frontend is showing 20 apartments")
            print("   • Backend API is returning 20 apartments")
            print("   • Expected 30 apartments (20 original + 10 TFC)")
            if not tfc_apartments:
                print("   • TFC listings are missing from database")
                print("   • Issue: Scraping endpoint may not be populating TFC data")
            else:
                print("   • TFC listings exist but may be filtered out")
        
        return self.results

if __name__ == "__main__":
    investigator = ApartmentCountInvestigator()
    results = investigator.run_investigation()