import jwt
import httpx
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
import base64
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

class AppleAuthService:
    def __init__(self):
        self.client_id = os.getenv("APPLE_CLIENT_ID", "")
        self.team_id = os.getenv("APPLE_TEAM_ID", "")
        self.key_id = os.getenv("APPLE_KEY_ID", "")
        self.private_key_path = os.getenv("APPLE_PRIVATE_KEY_PATH", "")
        self.apple_keys_url = "https://appleid.apple.com/auth/keys"
        self._public_keys_cache = {}
        
        if not all([self.client_id, self.team_id, self.key_id]):
            logger.warning("Apple Sign-In credentials not configured")
    
    async def get_apple_public_keys(self) -> Dict[str, Any]:
        """Fetch Apple's public keys for token validation"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.apple_keys_url, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch Apple public keys: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to validate Apple authentication"
            )
    
    def _decode_public_key(self, key_data: Dict[str, str]) -> Any:
        """Convert JWK to RSA public key"""
        try:
            # Extract modulus and exponent from JWK
            n = int.from_bytes(
                base64.urlsafe_b64decode(key_data['n'] + '=='), 
                byteorder='big'
            )
            e = int.from_bytes(
                base64.urlsafe_b64decode(key_data['e'] + '=='), 
                byteorder='big'
            )
            
            # Create RSA public key
            public_numbers = RSAPublicNumbers(e, n)
            public_key = public_numbers.public_key(backend=default_backend())
            
            return public_key
        except Exception as e:
            logger.error(f"Failed to decode Apple public key: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Key decoding error"
            )
    
    async def validate_identity_token(self, identity_token: str) -> Dict[str, Any]:
        """Validate Apple identity token and extract user information"""
        if not all([self.client_id, self.team_id, self.key_id]):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Apple Sign-In not configured"
            )
        
        try:
            # Decode header to get key ID
            header = jwt.get_unverified_header(identity_token)
            key_id = header.get('kid')
            
            if not key_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format"
                )
            
            # Get Apple's public keys
            apple_keys = await self.get_apple_public_keys()
            
            # Find the matching public key
            public_key = None
            for key_data in apple_keys['keys']:
                if key_data['kid'] == key_id:
                    public_key = self._decode_public_key(key_data)
                    break
            
            if not public_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find matching public key"
                )
            
            # Verify and decode the token
            decoded_token = jwt.decode(
                identity_token,
                public_key,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer='https://appleid.apple.com'
            )
            
            # Validate required claims
            required_claims = ['sub', 'aud', 'iss', 'exp', 'iat']
            for claim in required_claims:
                if claim not in decoded_token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Missing required claim: {claim}"
                    )
            
            # Extract user information
            user_info = {
                'apple_id': decoded_token['sub'],
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'provider': 'apple'
            }
            
            return user_info
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid Apple token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Apple identity token"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Apple token validation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during authentication"
            )

# Global instance
apple_auth_service = AppleAuthService()