"""
Production Social Authentication Module
Implements mixed approach:
- Emergent Authentication for Google (managed)
- Traditional OAuth for Facebook and Apple
"""

import os
import jwt
import requests
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
from fastapi import HTTPException, status
import hashlib
import hmac
import urllib.parse
import aiohttp
import json

# Configuration
EMERGENT_AUTH_ENABLED = os.environ.get('EMERGENT_AUTH_ENABLED', 'true').lower() == 'true'
EMERGENT_REDIRECT_URL = os.environ.get('EMERGENT_REDIRECT_URL', 'https://renteasy-nyc.preview.emergentagent.com/dashboard')
FACEBOOK_OAUTH_ENABLED = os.environ.get('FACEBOOK_OAUTH_ENABLED', 'false').lower() == 'true'
APPLE_OAUTH_ENABLED = os.environ.get('APPLE_OAUTH_ENABLED', 'false').lower() == 'true'

logger = logging.getLogger(__name__)

class EmergentGoogleAuth:
    """Emergent Authentication for Google OAuth"""
    
    def __init__(self):
        self.auth_url = "https://auth.emergentagent.com/"
        self.session_endpoint = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
        self.redirect_url = EMERGENT_REDIRECT_URL
    
    def get_login_url(self) -> str:
        """Get Emergent Auth login URL for Google OAuth"""
        return f"{self.auth_url}?redirect={urllib.parse.quote(self.redirect_url)}"
    
    async def validate_session(self, session_id: str) -> Dict[str, Any]:
        """Validate session ID and get user data from Emergent Auth"""
        try:
            headers = {"X-Session-ID": session_id}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.session_endpoint, headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        
                        # Transform to our standard format
                        standardized_data = {
                            "id": user_data.get("id"),
                            "email": user_data.get("email"),
                            "name": user_data.get("name"),
                            "picture": user_data.get("picture"),
                            "session_token": user_data.get("session_token"),
                            "provider": "google",
                            "provider_id": user_data.get("id"),
                            "email_verified": True  # Emergent Auth handles verification
                        }
                        
                        return standardized_data
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid session ID"
                        )
        except aiohttp.ClientError as e:
            logger.error(f"Emergent Auth session validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service temporarily unavailable"
            )

class FacebookOAuth:
    """Traditional Facebook OAuth implementation"""
    
    def __init__(self):
        self.enabled = FACEBOOK_OAUTH_ENABLED
        if self.enabled:
            self.app_id = os.environ.get('FACEBOOK_APP_ID')
            self.app_secret = os.environ.get('FACEBOOK_APP_SECRET')
            self.api_version = "v18.0"
            self.redirect_uri = f"{os.environ.get('REACT_APP_BACKEND_URL', '')}/api/auth/facebook/callback"
            
            if not self.app_id or not self.app_secret:
                logger.warning("Facebook OAuth enabled but credentials missing")
                self.enabled = False
    
    def generate_auth_url(self, state: str) -> str:
        """Generate Facebook OAuth authorization URL"""
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Facebook OAuth not configured"
            )
        
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'email,public_profile',
            'response_type': 'code',
            'state': state
        }
        
        auth_url = f"https://www.facebook.com/{self.api_version}/dialog/oauth"
        return f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Facebook OAuth not configured"
            )
        
        token_url = f"https://graph.facebook.com/{self.api_version}/oauth/access_token"
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Facebook token exchange failed: {error_data.get('error', 'Unknown error')}"
                    )
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Facebook"""
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Facebook OAuth not configured"
            )
        
        # Generate App Secret Proof for enhanced security
        app_secret_proof = hmac.new(
            self.app_secret.encode(),
            access_token.encode(),
            hashlib.sha256
        ).hexdigest()
        
        user_url = f"https://graph.facebook.com/{self.api_version}/me"
        params = {
            'access_token': access_token,
            'appsecret_proof': app_secret_proof,
            'fields': 'id,name,email,first_name,last_name,picture.type(large)'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(user_url, params=params) as response:
                if response.status == 200:
                    user_data = await response.json()
                    
                    # Transform to standard format
                    return {
                        "id": user_data.get("id"),
                        "email": user_data.get("email"),
                        "name": user_data.get("name"),
                        "first_name": user_data.get("first_name"),
                        "last_name": user_data.get("last_name"),
                        "picture": user_data.get("picture", {}).get("data", {}).get("url"),
                        "provider": "facebook",
                        "provider_id": user_data.get("id"),
                        "email_verified": True  # Facebook handles verification
                    }
                else:
                    error_data = await response.json()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Facebook user info request failed: {error_data.get('error', 'Unknown error')}"
                    )

class AppleSignIn:
    """Traditional Apple Sign In implementation"""
    
    def __init__(self):
        self.enabled = APPLE_OAUTH_ENABLED
        if self.enabled:
            self.client_id = os.environ.get('APPLE_CLIENT_ID')
            self.team_id = os.environ.get('APPLE_TEAM_ID')
            self.key_id = os.environ.get('APPLE_KEY_ID')
            self.private_key_path = os.environ.get('APPLE_PRIVATE_KEY_PATH')
            self.redirect_uri = f"{os.environ.get('REACT_APP_BACKEND_URL', '')}/api/auth/apple/callback"
            
            if not all([self.client_id, self.team_id, self.key_id]):
                logger.warning("Apple Sign In enabled but credentials missing")
                self.enabled = False
    
    def generate_client_secret(self) -> str:
        """Generate Apple client secret JWT"""
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Apple Sign In not configured"
            )
        
        try:
            with open(self.private_key_path, 'r') as f:
                private_key = f.read()
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Apple private key file not found"
            )
        
        headers = {
            "kid": self.key_id,
            "alg": "ES256"
        }
        
        payload = {
            "iss": self.team_id,
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(days=180)).timestamp()),  # 6 months max
            "aud": "https://appleid.apple.com",
            "sub": self.client_id
        }
        
        return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
    
    def generate_auth_url(self, state: str) -> str:
        """Generate Apple authorization URL"""
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Apple Sign In not configured"
            )
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'name email',
            'response_mode': 'form_post',
            'state': state
        }
        
        auth_url = "https://appleid.apple.com/auth/authorize"
        return f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    async def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Verify Apple ID token"""
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Apple Sign In not configured"
            )
        
        # Get Apple's public keys
        keys_url = "https://appleid.apple.com/auth/keys"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(keys_url) as response:
                if response.status == 200:
                    keys_data = await response.json()
                else:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Failed to fetch Apple public keys"
                    )
        
        # Decode and verify token
        try:
            # Get key ID from token header
            unverified_header = jwt.get_unverified_header(id_token)
            kid = unverified_header.get("kid")
            
            # Find matching key
            matching_key = None
            for key in keys_data.get("keys", []):
                if key.get("kid") == kid:
                    matching_key = key
                    break
            
            if not matching_key:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No matching Apple key found"
                )
            
            # Convert JWK to public key and verify
            from jwt.algorithms import RSAAlgorithm
            public_key = RSAAlgorithm.from_jwk(json.dumps(matching_key))
            
            payload = jwt.decode(
                id_token,
                public_key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer="https://appleid.apple.com"
            )
            
            # Transform to standard format
            return {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "email_verified": payload.get("email_verified", False),
                "is_private_email": payload.get("is_private_email", False),
                "provider": "apple",
                "provider_id": payload.get("sub")
            }
            
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Apple token verification failed: {str(e)}"
            )

# Global instances
emergent_google_auth = EmergentGoogleAuth()
facebook_oauth = FacebookOAuth()
apple_signin = AppleSignIn()

class SocialAuthManager:
    """Unified social authentication manager"""
    
    def __init__(self):
        self.providers = {
            "google": emergent_google_auth if EMERGENT_AUTH_ENABLED else None,
            "facebook": facebook_oauth if FACEBOOK_OAUTH_ENABLED else None,
            "apple": apple_signin if APPLE_OAUTH_ENABLED else None
        }
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Get list of available authentication providers"""
        return {
            "google": EMERGENT_AUTH_ENABLED,
            "facebook": FACEBOOK_OAUTH_ENABLED,
            "apple": APPLE_OAUTH_ENABLED
        }
    
    def is_provider_enabled(self, provider: str) -> bool:
        """Check if a specific provider is enabled"""
        return self.providers.get(provider) is not None
    
    async def authenticate_user(self, provider: str, auth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user with specified provider"""
        if not self.is_provider_enabled(provider):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Authentication provider '{provider}' is not available"
            )
        
        provider_instance = self.providers[provider]
        
        if provider == "google" and isinstance(provider_instance, EmergentGoogleAuth):
            return await provider_instance.validate_session(auth_data.get("session_id"))
        elif provider == "facebook" and isinstance(provider_instance, FacebookOAuth):
            # Handle Facebook OAuth flow
            if "access_token" in auth_data:
                return await provider_instance.get_user_info(auth_data["access_token"])
            elif "code" in auth_data:
                token_data = await provider_instance.exchange_code_for_token(auth_data["code"])
                return await provider_instance.get_user_info(token_data["access_token"])
        elif provider == "apple" and isinstance(provider_instance, AppleSignIn):
            return await provider_instance.verify_id_token(auth_data.get("id_token"))
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authentication data for provider"
        )

# Global social auth manager
social_auth_manager = SocialAuthManager()