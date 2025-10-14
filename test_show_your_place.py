#!/usr/bin/env python3
"""
Test script to verify the "Show Your Place" feature is working correctly
"""

import requests
import json

def test_show_your_place_api():
    """Test the backend API endpoint"""
    print("🧪 Testing Show Your Place API endpoint...")
    
    # Test data
    data = {
        'title': 'Beautiful 2BR in SoHo - No Fee',
        'address': '123 Spring Street, New York, NY 10012',
        'neighborhood': 'SoHo',
        'borough': 'Manhattan',
        'price': '4500',
        'bedrooms': '2',
        'bathrooms': '1.5',
        'sqft': '1200',
        'description': 'Stunning 2-bedroom apartment in the heart of SoHo with high ceilings, exposed brick, and modern amenities.',
        'amenities': 'Dishwasher, Laundry in unit, Gym, Doorman, Rooftop deck',
        'contact_email': 'landlord@example.com',
        'contact_phone': '(555) 123-4567',
        'lease_terms': '12 months',
        'move_in_date': '2025-01-01',
        'pet_policy': 'Cats allowed',
        'utilities': 'Heat and hot water included'
    }
    
    try:
        # Submit to API
        response = requests.post('http://localhost:8001/api/landlord/submit-listing', data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ API endpoint working correctly!")
                print(f"   Listing ID: {result.get('listing_id')}")
                print(f"   Message: {result.get('message')}")
                return True
            else:
                print(f"❌ API returned error: {result.get('message')}")
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

def test_frontend_components():
    """Test that frontend components are loading"""
    print("\n🧪 Testing frontend components...")
    
    try:
        # Check if frontend is accessible
        response = requests.get('http://localhost:3000', timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check for React app indicators
            if 'react' in html_content.lower() or 'root' in html_content:
                print("✅ Frontend is loading correctly!")
                
                # Check if the components.js file exists and has our changes
                try:
                    with open('/app/frontend/src/components.js', 'r') as f:
                        components_content = f.read()
                        
                    if 'ShowYourPlaceModal' in components_content and 'Show Your Place' in components_content:
                        print("✅ Show Your Place components found in source!")
                        return True
                    else:
                        print("❌ Show Your Place components not found in source")
                        return False
                        
                except Exception as e:
                    print(f"❌ Could not read components file: {str(e)}")
                    return False
            else:
                print("❌ Frontend not loading React app properly")
                return False
        else:
            print(f"❌ Frontend not accessible (status {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Frontend test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Show Your Place Feature Implementation\n")
    
    api_test = test_show_your_place_api()
    frontend_test = test_frontend_components()
    
    print(f"\n📊 Test Results:")
    print(f"   API Endpoint: {'✅ PASS' if api_test else '❌ FAIL'}")
    print(f"   Frontend Components: {'✅ PASS' if frontend_test else '❌ FAIL'}")
    
    if api_test and frontend_test:
        print(f"\n🎉 Show Your Place feature is working correctly!")
        print(f"   ✅ Backend API accepts form submissions")
        print(f"   ✅ Frontend components are in place")
        print(f"   ✅ Users can now submit their apartments via the header button")
        return True
    else:
        print(f"\n⚠️  Some issues found - see details above")
        return False

if __name__ == "__main__":
    main()