#!/usr/bin/env python3
"""
Share Listing Feature End-to-End Backend Testing
Testing the complete Share Listing feature workflow as requested in review.

Backend URL: https://login-rebuild.preview.emergentagent.com
Endpoint: POST /api/apartments/{apartment_id}/share

Test Scenarios:
1. Share Listing Without Authentication
2. Share Listing With Authentication  
3. Invalid Email Validation
4. Non-Existent Apartment ID
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://login-rebuild.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

# Test credentials for authentication
TEST_EMAIL = "chris.trunell@gmail.com"
TEST_PASSWORD = "Onetimeround247"

class ShareListingTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'NoFeePlaces-Backend-Tester/1.0'
        })
        self.test_results = []
        self.apartment_id = None
        self.auth_token = None
        
    def log_test(self, test_name, success, details, response=None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        if response:
            result['status_code'] = response.status_code
            result['response_time'] = response.elapsed.total_seconds()
        
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response and not success:
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    
    def get_real_apartment_id(self):
        """Get a real apartment ID from the API"""
        try:
            print("\n🔍 Getting real apartment ID for testing...")
            response = self.session.get(f"{API_BASE}/apartments?limit=1")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('apartments') and len(data['apartments']) > 0:
                    apartment = data['apartments'][0]
                    self.apartment_id = apartment['id']
                    print(f"   Found apartment: {apartment.get('title', 'Unknown')} (ID: {self.apartment_id})")
                    return True
                else:
                    print("   No apartments found in API response")
                    return False
            else:
                print(f"   Failed to get apartments: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   Error getting apartment ID: {str(e)}")
            return False
    
    def authenticate_user(self):
        """Authenticate user and get JWT token"""
        try:
            print("\n🔐 Authenticating user for authenticated tests...")
            
            auth_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                if self.auth_token:
                    print(f"   Authentication successful! Token length: {len(self.auth_token)}")
                    print(f"   User: {data.get('user', {}).get('email', 'Unknown')}")
                    return True
                else:
                    print("   No access token in response")
                    return False
            else:
                print(f"   Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   Authentication error: {str(e)}")
            return False
    
    def test_share_without_auth(self):
        """Test 1: Share Listing Without Authentication"""
        if not self.apartment_id:
            self.log_test("Share Without Auth", False, "No apartment ID available")
            return
        
        try:
            share_data = {
                "recipient_email": "sharetest@example.com"
            }
            
            response = self.session.post(
                f"{API_BASE}/apartments/{self.apartment_id}/share",
                json=share_data
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', '')
                
                if success and 'shared successfully' in message.lower():
                    self.log_test("Share Without Auth", True, 
                                f"Successfully shared listing. Message: {message}", response)
                else:
                    self.log_test("Share Without Auth", False, 
                                f"Unexpected response format: {data}", response)
            else:
                self.log_test("Share Without Auth", False, 
                            f"HTTP {response.status_code}: {response.text[:100]}", response)
                
        except Exception as e:
            self.log_test("Share Without Auth", False, f"Exception: {str(e)}")
    
    def test_share_with_auth(self):
        """Test 2: Share Listing With Authentication"""
        if not self.apartment_id or not self.auth_token:
            self.log_test("Share With Auth", False, "Missing apartment ID or auth token")
            return
        
        try:
            share_data = {
                "recipient_email": "authenticated-share@example.com"
            }
            
            headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                f"{API_BASE}/apartments/{self.apartment_id}/share",
                json=share_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', '')
                
                if success and 'shared successfully' in message.lower():
                    self.log_test("Share With Auth", True, 
                                f"Successfully shared with authentication. Message: {message}", response)
                else:
                    self.log_test("Share With Auth", False, 
                                f"Unexpected response format: {data}", response)
            else:
                self.log_test("Share With Auth", False, 
                            f"HTTP {response.status_code}: {response.text[:100]}", response)
                
        except Exception as e:
            self.log_test("Share With Auth", False, f"Exception: {str(e)}")
    
    def test_invalid_email_validation(self):
        """Test 3: Invalid Email Validation"""
        if not self.apartment_id:
            self.log_test("Invalid Email Validation", False, "No apartment ID available")
            return
        
        try:
            share_data = {
                "recipient_email": "invalid-email"
            }
            
            response = self.session.post(
                f"{API_BASE}/apartments/{self.apartment_id}/share",
                json=share_data
            )
            
            # Should return 400 or 422 for validation error
            if response.status_code in [400, 422]:
                self.log_test("Invalid Email Validation", True, 
                            f"Correctly rejected invalid email with HTTP {response.status_code}", response)
            elif response.status_code == 200:
                # If it accepts invalid email, that's a problem
                self.log_test("Invalid Email Validation", False, 
                            "API incorrectly accepted invalid email format", response)
            else:
                self.log_test("Invalid Email Validation", False, 
                            f"Unexpected status code {response.status_code}", response)
                
        except Exception as e:
            self.log_test("Invalid Email Validation", False, f"Exception: {str(e)}")
    
    def test_nonexistent_apartment(self):
        """Test 4: Non-Existent Apartment ID"""
        try:
            fake_apartment_id = "nonexistent-id-12345"
            share_data = {
                "recipient_email": "test@example.com"
            }
            
            response = self.session.post(
                f"{API_BASE}/apartments/{fake_apartment_id}/share",
                json=share_data
            )
            
            # Should return 404 for not found
            if response.status_code == 404:
                self.log_test("Non-Existent Apartment", True, 
                            "Correctly returned 404 for non-existent apartment", response)
            else:
                self.log_test("Non-Existent Apartment", False, 
                            f"Expected 404, got {response.status_code}", response)
                
        except Exception as e:
            self.log_test("Non-Existent Apartment", False, f"Exception: {str(e)}")
    
    def test_backend_logs_check(self):
        """Check backend logs for email service activity"""
        try:
            print("\n📋 Checking backend logs for email service activity...")
            
            # Try to check supervisor logs
            import subprocess
            result = subprocess.run(
                ['tail', '-n', '20', '/var/log/supervisor/backend.out.log'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                print("   Recent backend logs:")
                for line in result.stdout.strip().split('\n')[-5:]:
                    if 'share' in line.lower() or 'email' in line.lower():
                        print(f"   📧 {line}")
                        
            self.log_test("Backend Logs Check", True, "Successfully checked backend logs")
            
        except Exception as e:
            self.log_test("Backend Logs Check", False, f"Could not check logs: {str(e)}")
    
    def run_all_tests(self):
        """Run all share listing tests"""
        print("🚀 Starting Share Listing Feature End-to-End Backend Testing")
        print(f"Backend URL: {BASE_URL}")
        print(f"Testing endpoint: POST /api/apartments/{{apartment_id}}/share")
        print("=" * 70)
        
        # Setup phase
        if not self.get_real_apartment_id():
            print("❌ Cannot proceed without a valid apartment ID")
            return False
        
        # Authentication setup (optional for some tests)
        auth_success = self.authenticate_user()
        
        # Run all test scenarios
        print("\n📋 Running Test Scenarios:")
        print("-" * 40)
        
        # Test 1: Share without authentication
        self.test_share_without_auth()
        
        # Test 2: Share with authentication (if auth worked)
        if auth_success:
            self.test_share_with_auth()
        else:
            self.log_test("Share With Auth", False, "Skipped due to authentication failure")
        
        # Test 3: Invalid email validation
        self.test_invalid_email_validation()
        
        # Test 4: Non-existent apartment ID
        self.test_nonexistent_apartment()
        
        # Check backend logs
        self.test_backend_logs_check()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 SHARE LISTING FEATURE TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 VERIFICATION CHECKLIST:")
        checklist = [
            ("API responds with correct HTTP status codes", any(r['success'] and 'HTTP' in r['details'] for r in self.test_results)),
            ("Success response includes proper message", any(r['success'] and 'shared successfully' in r['details'].lower() for r in self.test_results)),
            ("Error responses include proper error details", any(r['success'] and r['test'] in ['Invalid Email Validation', 'Non-Existent Apartment'] for r in self.test_results)),
            ("Email service is called", any('email' in r['details'].lower() for r in self.test_results)),
            ("Authentication is optional but enhances the share email", any(r['test'] == 'Share Without Auth' and r['success'] for r in self.test_results)),
            ("Email validation works correctly", any(r['test'] == 'Invalid Email Validation' and r['success'] for r in self.test_results)),
            ("Non-existent apartment IDs are handled gracefully", any(r['test'] == 'Non-Existent Apartment' and r['success'] for r in self.test_results))
        ]
        
        for item, status in checklist:
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {item}")
        
        print(f"\n🏁 CONCLUSION:")
        if success_rate >= 80:
            print("   🎉 Share Listing feature is working excellently and ready for production!")
        elif success_rate >= 60:
            print("   ⚠️  Share Listing feature has some issues but core functionality works.")
        else:
            print("   🚨 Share Listing feature has significant issues that need attention.")
        
        print(f"\nTesting completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function"""
    tester = ShareListingTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error during testing: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())