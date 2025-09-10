"""
Social Authentication API Routes
Handles Google (Emergent), Facebook, and Apple Sign-In
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Request, Response, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
import jwt

from social_auth import social_auth_manager, emergent_google_auth, facebook_oauth, apple_signin

logger = logging.getLogger(__name__)

# Router setup
social_router = APIRouter(prefix="/auth", tags=["Social Authentication"])

# Pydantic models
class SocialAuthRequest(BaseModel):
    provider: str
    session_id: Optional[str] = None  # For Emergent Auth
    code: Optional[str] = None        # For traditional OAuth
    id_token: Optional[str] = None    # For Apple Sign In
    access_token: Optional[str] = None # For Facebook
    state: Optional[str] = None       # CSRF protection
    user_data: Optional[Dict[str, Any]] = None  # Additional user data

class SocialAuthResponse(BaseModel):
    success: bool
    user: Dict[str, Any]
    access_token: str
    refresh_token: str
    provider: str
    message: str

class AuthProviderStatus(BaseModel):
    google: bool
    facebook: bool
    apple: bool
    message: str

# Helper functions
def generate_state_token() -> str:
    """Generate secure state token for CSRF protection"""
    return secrets.token_urlsafe(32)

def generate_jwt_token(user_data: Dict[str, Any]) -> Dict[str, str]:
    """Generate JWT tokens for authenticated user"""
    from server import jwt_handler
    
    token_data = {
        "sub": str(user_data.get("id", user_data.get("provider_id"))),
        "email": user_data.get("email"),
        "provider": user_data.get("provider"),
        "provider_id": user_data.get("provider_id")
    }
    
    access_token = jwt_handler.create_access_token(token_data)
    refresh_token = jwt_handler.create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes
    }

async def create_or_update_social_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create or update user from social auth data"""
    from server import db
    import uuid
    
    provider_id = user_data.get("provider_id") or user_data.get("id")
    provider = user_data.get("provider")
    
    # Check if user exists by provider ID
    existing_user = await db.users.find_one({
        f"{provider}_id": provider_id
    })
    
    if existing_user:
        # Update existing user
        update_data = {
            "updated_at": datetime.utcnow(),
            "last_login": datetime.utcnow()
        }
        
        # Update email if changed
        if user_data.get("email") and user_data["email"] != existing_user.get("email"):
            update_data["email"] = user_data["email"]
        
        # Update profile picture if available
        if user_data.get("picture"):
            update_data["profile_picture"] = user_data["picture"]
        
        await db.users.update_one(
            {"_id": existing_user["_id"]},
            {"$set": update_data}
        )
        
        # Return updated user data
        updated_user = await db.users.find_one({"_id": existing_user["_id"]})
        return {
            "id": str(updated_user["_id"]),
            "email": updated_user.get("email"),
            "full_name": updated_user.get("full_name"),
            "profile_picture": updated_user.get("profile_picture"),
            "provider": provider,
            "provider_id": provider_id,
            "created_at": updated_user.get("created_at"),
            "last_login": updated_user.get("last_login")
        }
    else:
        # Create new user
        new_user = {
            "id": str(uuid.uuid4()),
            "email": user_data.get("email"),
            "full_name": user_data.get("name"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "profile_picture": user_data.get("picture"),
            f"{provider}_id": provider_id,
            "provider": provider,
            "email_verified": user_data.get("email_verified", True),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": datetime.utcnow(),
            "saved_searches": [],
            "favorite_apartments": []
        }
        
        result = await db.users.insert_one(new_user)
        new_user["_id"] = result.inserted_id
        
        return {
            "id": new_user["id"],
            "email": new_user.get("email"),
            "full_name": new_user.get("full_name"),
            "profile_picture": new_user.get("profile_picture"),
            "provider": provider,
            "provider_id": provider_id,
            "created_at": new_user.get("created_at"),
            "last_login": new_user.get("last_login")
        }

# API Routes
@social_router.get("/providers/status")
async def get_auth_providers() -> AuthProviderStatus:
    """Get available authentication providers"""
    providers = social_auth_manager.get_available_providers()
    
    return AuthProviderStatus(
        google=providers["google"],
        facebook=providers["facebook"],
        apple=providers["apple"],
        message="Authentication providers status"
    )

@social_router.get("/google/login")
async def google_login_redirect():
    """Redirect to Emergent Auth for Google login"""
    if not social_auth_manager.is_provider_enabled("google"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google authentication not available"
        )
    
    login_url = emergent_google_auth.get_login_url()
    return RedirectResponse(url=login_url)

@social_router.post("/google/callback")
async def google_auth_callback(request: Request, auth_request: SocialAuthRequest):
    """Handle Google authentication via Emergent Auth"""
    try:
        if not auth_request.session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing session_id parameter"
            )
        
        # Validate session with Emergent Auth
        user_data = await social_auth_manager.authenticate_user("google", {
            "session_id": auth_request.session_id
        })
        
        # Create or update user in our database
        app_user = await create_or_update_social_user(user_data)
        
        # Generate our JWT tokens
        tokens = generate_jwt_token(app_user)
        
        return SocialAuthResponse(
            success=True,
            user=app_user,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            provider="google",
            message="Google authentication successful"
        )
        
    except Exception as e:
        logger.error(f"Google auth callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google authentication failed: {str(e)}"
        )

@social_router.get("/facebook/login")
async def facebook_login_redirect(request: Request):
    """Redirect to Facebook OAuth"""
    if not social_auth_manager.is_provider_enabled("facebook"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Facebook authentication not available"
        )
    
    # Generate and store state token
    state = generate_state_token()
    request.session["facebook_oauth_state"] = state
    
    auth_url = facebook_oauth.generate_auth_url(state)
    return RedirectResponse(url=auth_url)

@social_router.get("/facebook/callback")
async def facebook_auth_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    """Handle Facebook OAuth callback"""
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Facebook authentication error: {error}"
        )
    
    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required OAuth parameters"
        )
    
    # Verify state token (CSRF protection)
    stored_state = request.session.get("facebook_oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    try:
        # Exchange code for access token and get user data
        user_data = await social_auth_manager.authenticate_user("facebook", {
            "code": code
        })
        
        # Create or update user in our database
        app_user = await create_or_update_social_user(user_data)
        
        # Generate our JWT tokens
        tokens = generate_jwt_token(app_user)
        
        # Clear session state
        request.session.pop("facebook_oauth_state", None)
        
        # Return success response or redirect to frontend
        return SocialAuthResponse(
            success=True,
            user=app_user,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            provider="facebook",
            message="Facebook authentication successful"
        )
        
    except Exception as e:
        logger.error(f"Facebook auth callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Facebook authentication failed: {str(e)}"
        )

@social_router.get("/apple/login")
async def apple_login_redirect(request: Request):
    """Redirect to Apple Sign In"""
    if not social_auth_manager.is_provider_enabled("apple"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Apple Sign In not available"
        )
    
    # Generate and store state token
    state = generate_state_token()
    request.session["apple_oauth_state"] = state
    
    auth_url = apple_signin.generate_auth_url(state)
    return RedirectResponse(url=auth_url)

@social_router.post("/apple/callback")
async def apple_auth_callback(
    request: Request,
    code: str = Form(...),
    id_token: str = Form(...),
    state: str = Form(...),
    user: Optional[str] = Form(None)  # Apple sends user data as JSON string on first auth
):
    """Handle Apple Sign In callback"""
    # Verify state token (CSRF protection)
    stored_state = request.session.get("apple_oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    try:
        # Verify ID token and extract user data
        user_data = await social_auth_manager.authenticate_user("apple", {
            "id_token": id_token
        })
        
        # Add user data from form if available (first-time sign in)
        if user:
            import json
            try:
                user_info = json.loads(user)
                if "name" in user_info:
                    user_data["name"] = f"{user_info['name'].get('firstName', '')} {user_info['name'].get('lastName', '')}".strip()
                    user_data["first_name"] = user_info['name'].get('firstName')
                    user_data["last_name"] = user_info['name'].get('lastName')
            except json.JSONDecodeError:
                pass  # Ignore malformed user data
        
        # Create or update user in our database
        app_user = await create_or_update_social_user(user_data)
        
        # Generate our JWT tokens
        tokens = generate_jwt_token(app_user)
        
        # Clear session state
        request.session.pop("apple_oauth_state", None)
        
        return SocialAuthResponse(
            success=True,
            user=app_user,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            provider="apple",
            message="Apple authentication successful"
        )
        
    except Exception as e:
        logger.error(f"Apple auth callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Apple authentication failed: {str(e)}"
        )

@social_router.post("/social/authenticate")
async def social_authenticate(request: Request, auth_request: SocialAuthRequest):
    """Universal social authentication endpoint"""
    try:
        # Authenticate with specified provider
        user_data = await social_auth_manager.authenticate_user(
            auth_request.provider,
            auth_request.dict(exclude_none=True)
        )
        
        # Create or update user in our database
        app_user = await create_or_update_social_user(user_data)
        
        # Generate our JWT tokens
        tokens = generate_jwt_token(app_user)
        
        return SocialAuthResponse(
            success=True,
            user=app_user,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            provider=auth_request.provider,
            message=f"{auth_request.provider.title()} authentication successful"
        )
        
    except Exception as e:
        logger.error(f"Social auth error for {auth_request.provider}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{auth_request.provider.title()} authentication failed: {str(e)}"
        )

@social_router.post("/logout")
async def social_logout(request: Request, response: Response):
    """Logout from social authentication"""
    # Clear session data
    if hasattr(request, 'session'):
        request.session.clear()
    
    # Clear any authentication cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    
    return {"success": True, "message": "Logged out successfully"}

@social_router.get("/test/demo")
async def test_demo_auth():
    """Demo endpoint for testing social auth (development only)"""
    from server import settings
    
    if settings.environment != "development":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo endpoint not available in production"
        )
    
    demo_user = {
        "id": "demo-social-user-123",
        "email": "demo@nofeeplaces.com",
        "name": "Demo Social User",
        "provider": "demo",
        "provider_id": "demo-123"
    }
    
    app_user = await create_or_update_social_user(demo_user)
    tokens = generate_jwt_token(app_user)
    
    return SocialAuthResponse(
        success=True,
        user=app_user,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        provider="demo",
        message="Demo authentication successful"
    )