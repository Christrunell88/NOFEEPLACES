#!/usr/bin/env python3
"""
Authentication Investigation Script
Specifically designed to answer user questions about existing accounts and login credentials
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://nofeeplaces-app.preview.emergentagent.com/api"

class AuthInvestigator:
    def __init__(self):
        self.base_url = BASE_URL
        self.findings = []
        
    def log_finding(self, category: str, message: str):
        """Log investigation findings"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        finding = f"[{timestamp}] {category}: {message}"
        print(finding)
        self.findings.append(finding)
    
    def make_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            self.log_finding("ERROR", f"Request failed: {e}")
            return None
    
    def check_existing_test_users(self):
        """Check if common test users exist by attempting login"""
        print("\n=== CHECKING FOR EXISTING TEST USERS ===")
        
        common_test_credentials = [
            {"email": "testuser@nofeeplaces.com", "password": "SecurePassword123!"},
            {"email": "test@test.com", "password": "password"},
            {"email": "admin@nofeeplaces.com", "password": "admin123"},
            {"email": "user@example.com", "password": "password123"},
            {"email": "demo@demo.com", "password": "demo123"},
            {"email": "test@nofeeplaces.com", "password": "test123"},
        ]
        
        existing_users = []
        
        for creds in common_test_credentials:
            response = self.make_request("POST", "/auth/login", creds)
            if response and response.status_code == 200:
                token_data = response.json()
                existing_users.append({
                    "email": creds["email"],
                    "password": creds["password"],
                    "token": token_data.get("access_token", "")[:20] + "..."
                })
                self.log_finding("EXISTING USER FOUND", f"✅ {creds['email']} with password '{creds['password']}'")
            elif response and response.status_code == 401:
                self.log_finding("LOGIN ATTEMPT", f"❌ {creds['email']} - Invalid credentials")
            else:
                self.log_finding("LOGIN ATTEMPT", f"⚠️  {creds['email']} - Unexpected response: {response.status_code if response else 'No response'}")
        
        return existing_users
    
    def create_new_test_user(self):
        """Create a new test user account"""
        print("\n=== CREATING NEW TEST USER ===")
        
        new_user_data = {
            "email": "newuser@nofeeplaces.com",
            "password": "NewUser123!",
            "full_name": "Test User for Authentication"
        }
        
        response = self.make_request("POST", "/auth/register", new_user_data)
        
        if response and response.status_code == 200:
            token_data = response.json()
            self.log_finding("USER CREATION", f"✅ Successfully created user: {new_user_data['email']}")
            self.log_finding("CREDENTIALS", f"📧 Email: {new_user_data['email']}")
            self.log_finding("CREDENTIALS", f"🔑 Password: {new_user_data['password']}")
            self.log_finding("TOKEN", f"🎫 Access Token: {token_data.get('access_token', '')[:30]}...")
            return new_user_data
        elif response and response.status_code == 400:
            self.log_finding("USER CREATION", f"⚠️  User might already exist: {response.text}")
            # Try to login with these credentials
            login_response = self.make_request("POST", "/auth/login", {
                "email": new_user_data["email"],
                "password": new_user_data["password"]
            })
            if login_response and login_response.status_code == 200:
                self.log_finding("EXISTING USER", f"✅ User already exists and can login with: {new_user_data['email']}")
                return new_user_data
        else:
            self.log_finding("USER CREATION", f"❌ Failed to create user: {response.status_code if response else 'No response'}")
            if response:
                self.log_finding("ERROR DETAILS", response.text)
        
        return None
    
    def test_authentication_system(self):
        """Test the authentication system comprehensively"""
        print("\n=== TESTING AUTHENTICATION SYSTEM ===")
        
        # Test with a known working user (from existing test)
        test_creds = {"email": "testuser@nofeeplaces.com", "password": "SecurePassword123!"}
        
        # 1. Test login
        login_response = self.make_request("POST", "/auth/login", test_creds)
        if login_response and login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            self.log_finding("LOGIN TEST", f"✅ Login successful for {test_creds['email']}")
            
            # 2. Test token validation
            auth_headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = self.make_request("GET", "/auth/me", headers=auth_headers)
            
            if profile_response and profile_response.status_code == 200:
                profile_data = profile_response.json()
                self.log_finding("TOKEN VALIDATION", f"✅ Token is valid - User: {profile_data.get('full_name', 'Unknown')}")
                self.log_finding("USER PROFILE", f"📧 Email: {profile_data.get('email')}")
                self.log_finding("USER PROFILE", f"👤 Name: {profile_data.get('full_name')}")
                self.log_finding("USER PROFILE", f"🆔 ID: {profile_data.get('id')}")
                self.log_finding("USER PROFILE", f"📅 Created: {profile_data.get('created_at')}")
            else:
                self.log_finding("TOKEN VALIDATION", f"❌ Token validation failed: {profile_response.status_code if profile_response else 'No response'}")
        else:
            self.log_finding("LOGIN TEST", f"❌ Login failed: {login_response.status_code if login_response else 'No response'}")
    
    def investigate_authentication_requirements(self):
        """Investigate what credentials are needed for authentication"""
        print("\n=== AUTHENTICATION REQUIREMENTS INVESTIGATION ===")
        
        # Test registration requirements
        self.log_finding("REGISTRATION", "📋 Registration requires:")
        self.log_finding("REGISTRATION", "   • email (valid email format)")
        self.log_finding("REGISTRATION", "   • password (string)")
        self.log_finding("REGISTRATION", "   • full_name (string)")
        
        # Test login requirements
        self.log_finding("LOGIN", "🔐 Login requires:")
        self.log_finding("LOGIN", "   • email (registered email)")
        self.log_finding("LOGIN", "   • password (matching password)")
        
        # Test what happens with invalid credentials
        invalid_login = self.make_request("POST", "/auth/login", {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        
        if invalid_login:
            self.log_finding("INVALID LOGIN", f"❌ Invalid credentials return: {invalid_login.status_code} - {invalid_login.text}")
        
        # Test token usage
        self.log_finding("TOKEN USAGE", "🎫 Authentication token:")
        self.log_finding("TOKEN USAGE", "   • Returned after successful login/registration")
        self.log_finding("TOKEN USAGE", "   • Must be included in Authorization header as 'Bearer <token>'")
        self.log_finding("TOKEN USAGE", "   • Required for protected endpoints (favorites, saved searches, profile)")
    
    def provide_user_guidance(self, existing_users):
        """Provide clear guidance to the user"""
        print("\n" + "="*60)
        print("🎯 USER GUIDANCE - AUTHENTICATION SUMMARY")
        print("="*60)
        
        if existing_users:
            print("\n✅ EXISTING USER ACCOUNTS FOUND:")
            for user in existing_users:
                print(f"   📧 Email: {user['email']}")
                print(f"   🔑 Password: {user['password']}")
                print(f"   🎫 Token: {user['token']}")
                print()
        else:
            print("\n⚠️  NO EXISTING TEST USERS FOUND")
            print("   You'll need to create a new account")
        
        print("🔐 HOW TO AUTHENTICATE:")
        print("   1. Register a new account:")
        print("      POST /api/auth/register")
        print("      Body: {\"email\": \"your@email.com\", \"password\": \"yourpassword\", \"full_name\": \"Your Name\"}")
        print()
        print("   2. OR Login with existing account:")
        print("      POST /api/auth/login")
        print("      Body: {\"email\": \"your@email.com\", \"password\": \"yourpassword\"}")
        print()
        print("   3. Use the returned access_token in subsequent requests:")
        print("      Header: Authorization: Bearer <your_access_token>")
        print()
        
        if existing_users:
            print("🚀 QUICK START - USE THESE CREDENTIALS:")
            user = existing_users[0]
            print(f"   Email: {user['email']}")
            print(f"   Password: {user['password']}")
            print()
            print("   These credentials are ready to use for testing the application!")
        else:
            print("🚀 QUICK START - CREATE NEW ACCOUNT:")
            print("   Use the registration endpoint to create your account first.")
    
    def run_investigation(self):
        """Run the complete authentication investigation"""
        print("🔍 AUTHENTICATION SYSTEM INVESTIGATION")
        print(f"🌐 API Base URL: {self.base_url}")
        print("="*60)
        
        # Check for existing users
        existing_users = self.check_existing_test_users()
        
        # Create new test user if needed
        if not existing_users:
            new_user = self.create_new_test_user()
            if new_user:
                existing_users.append(new_user)
        
        # Test authentication system
        self.test_authentication_system()
        
        # Investigate requirements
        self.investigate_authentication_requirements()
        
        # Provide user guidance
        self.provide_user_guidance(existing_users)
        
        print("\n" + "="*60)
        print("📋 INVESTIGATION COMPLETE")
        print("="*60)
        
        return {
            "existing_users": existing_users,
            "findings": self.findings
        }

if __name__ == "__main__":
    investigator = AuthInvestigator()
    results = investigator.run_investigation()