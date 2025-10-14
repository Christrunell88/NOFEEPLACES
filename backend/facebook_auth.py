import httpx
import logging
import os
from typing import Dict, Any, Optional
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class FacebookAuthService:
    def __init__(self):
        self.app_id = os.getenv("FACEBOOK_APP_ID", "")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET", "")
        self.graph_api_base = "https://graph.facebook.com"
        
        if not self.app_id or not self.app_secret:
            logger.warning("Facebook credentials not configured")
    
    async def validate_access_token(self, access_token: str) -> Dict[str, Any]:
        """
        Validate Facebook access token and return user information
        """
        if not self.app_id or not self.app_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Facebook authentication not configured"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                # Verify token with Facebook's debug endpoint
                debug_response = await client.get(
                    f"{self.graph_api_base}/debug_token",
                    params={
                        "input_token": access_token,
                        "access_token": f"{self.app_id}|{self.app_secret}"
                    },
                    timeout=10.0
                )
                
                if debug_response.status_code != 200:
                    logger.error(f"Facebook debug token failed: {debug_response.status_code}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Failed to validate Facebook token"
                    )
                
                debug_data = debug_response.json()
                
                if not debug_data.get("data", {}).get("is_valid"):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Facebook access token"
                    )
                
                # Verify the token belongs to our app
                if debug_data["data"]["app_id"] != self.app_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token does not belong to this application"
                    )
                
                # Get user information
                user_response = await client.get(
                    f"{self.graph_api_base}/me",
                    params={
                        "access_token": access_token,
                        "fields": "id,name,email,picture.type(large)"
                    },
                    timeout=10.0
                )
                
                if user_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Failed to retrieve user information from Facebook"
                    )
                
                user_data = user_response.json()
                
                return {
                    "facebook_id": user_data["id"],
                    "name": user_data.get("name"),
                    "email": user_data.get("email"),
                    "picture": user_data.get("picture", {}).get("data", {}).get("url"),
                    "provider": "facebook"
                }
                
        except httpx.RequestError as e:
            logger.error(f"Network error during Facebook token validation: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to connect to Facebook services"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Facebook token validation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during authentication"
            )

# Global instance
facebook_auth_service = FacebookAuthService()