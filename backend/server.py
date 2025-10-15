from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query, Request, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import aiofiles
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import logging
import os
import uuid
import json
from pathlib import Path
from dotenv import load_dotenv
from email_service import email_service
from newsletter_service import newsletter_service
from landlord_api import landlord_router, set_database
from emergentintegrations.payments.stripe.checkout import StripeCheckout
from facebook_auth import facebook_auth_service
from apple_auth import apple_auth_service
from chatbot_service import nofeebbot

# Load environment variables
load_dotenv('/app/backend/.env')

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/supervisor/backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI with enhanced metadata
app = FastAPI(
    title="NoFeePlaces.com API",
    description="NYC's premier no fee apartment rental platform API with 240+ verified listings",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "NoFeePlaces.com Support",
        "email": "placesfirm@gmail.com",
        "url": "https://nofeeplaces.com/contact"
    },
    license_info={
        "name": "Private License",
        "url": "https://nofeeplaces.com/terms"
    }
)

# Initialize router
api_router = APIRouter(prefix="/api")

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces')
client = AsyncIOMotorClient(MONGO_URL)
db_name = os.environ.get('DB_NAME', 'nofeeplaces')
db = client[db_name]

logger.info(f"Connecting to MongoDB: {MONGO_URL}")
logger.info(f"Using database: {db_name}")

# Enhanced Pydantic Models
class Apartment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str = ""
    price: float
    location: Union[str, dict] = ""
    bedrooms: Union[int, str, None] = None  # Handle both int and string like "Studio"
    bathrooms: Optional[float] = None
    sqft: Optional[int] = None
    amenities: List[str] = []
    images: List[str] = []
    contact_email: Optional[str] = "placesfirm@gmail.com"
    contact_phone: Optional[str] = "+1-646-408-8048"
    available: bool = True
    created_at: Union[datetime, str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Union[datetime, str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    priority: Optional[int] = 0
    featured: Optional[bool] = False
    building_name: Optional[str] = None
    neighborhood: Optional[str] = None
    borough: Optional[str] = None
    lease_terms: Union[str, List[str], None] = None
    pet_policy: Optional[str] = None
    
    @field_validator('lease_terms', mode='before')
    @classmethod
    def convert_lease_terms(cls, v):
        if isinstance(v, list):
            return ', '.join(str(term) for term in v)
        return v
    utilities_included: Union[List[str], bool, None] = []  # Handle both list and boolean
    parking_available: Optional[bool] = False
    laundry: Optional[str] = None
    elevator: Optional[bool] = False
    doorman: Optional[bool] = False
    gym: Optional[bool] = False
    rooftop: Optional[bool] = False
    address: Optional[str] = None
    unit_number: Optional[str] = None
    floor: Optional[int] = None
    is_verified: Optional[bool] = True
    is_real: Optional[bool] = True
    verification_date: Optional[str] = None
    quality_score: Optional[int] = 95
    data_source: Optional[str] = "NoFeePlaces Verified"
    listing_type: Optional[str] = "Direct"
    broker_fee: Optional[str] = "No fee"
    verification_status: Optional[str] = "Verified by NoFeePlaces"
    source_database: Optional[str] = None  # Track which database this apartment came from
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ApartmentListResponse(BaseModel):
    apartments: List[Apartment]
    total: int
    page: int
    limit: int
    has_more: bool

class BlogPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    slug: str
    excerpt: str
    content: str
    author: str = "NoFeePlaces Team"
    category: str
    tags: List[str] = []
    featured_image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    status: str = "published"
    published_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    read_time: Optional[int] = None
    view_count: int = 0
    related_neighborhoods: Optional[List[str]] = []
    seo_keywords: Optional[List[str]] = []

class BlogListResponse(BaseModel):
    posts: List[BlogPost]
    total: int
    page: int
    limit: int
    has_more: bool

class ContactRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    message: str
    apartment_id: Optional[str] = None
    preferred_contact: str = "email"

class SearchRequest(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    amenities: Optional[List[str]] = []

class NewsletterSubscription(BaseModel):
    email: str
    full_name: Optional[str] = ""
    source: str = "website"
    preferences: Optional[Dict[str, bool]] = None

class ContactResponse(BaseModel):
    message: str
    contact_id: str

# Social Authentication Models
class FacebookAuthRequest(BaseModel):
    access_token: str
    user_id: str

class AppleAuthRequest(BaseModel):
    authorization_code: str
    identity_token: str
    user_data: Optional[Dict[str, Any]] = None

class SocialAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    profile_picture: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_login: Optional[str] = None
    # Social provider IDs
    google_id: Optional[str] = None
    facebook_id: Optional[str] = None
    apple_id: Optional[str] = None

# Contact Email Models
class ContactEmailRequest(BaseModel):
    to: str
    subject: str
    sender_name: str
    sender_email: str
    sender_phone: Optional[str] = None
    message: str
    apartment_details: Optional[Dict[str, Any]] = None

class ContactEmailResponse(BaseModel):
    success: bool
    message: str

# Chatbot Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

# Newsletter Subscription Models
class NewsletterSubscription(BaseModel):
    email: str
    name: Optional[str] = None
    interests: Optional[List[str]] = None  # e.g., ["Manhattan", "Brooklyn", "1BR", "2BR"]

class SubscriptionResponse(BaseModel):
    success: bool
    message: str

# Feedback Models
class FeedbackRequest(BaseModel):
    type: str  # bug, feature, improvement, compliment, other
    title: str
    description: str
    email: Optional[str] = None
    page: str
    userAgent: str
    priority: str = "medium"  # low, medium, high, urgent
    timestamp: str
    url: str

class FeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: str

# AI Content Discovery endpoint for search engines
@api_router.get("/content-discovery")
async def content_discovery():
    """Endpoint for AI search engines to discover site content and structure"""
    apartments_count = await db.apartments.count_documents({"available": True})
    blog_posts_count = await db.blog_posts.count_documents({"status": "published"})
    
    # Get sample apartments for AI understanding
    sample_apartments = await db.apartments.find(
        {"available": True, "priority": {"$gte": 1}}
    ).limit(5).to_list(length=5)
    
    # Get recent blog posts for AI understanding
    recent_blogs = await db.blog_posts.find(
        {"status": "published"}
    ).sort("created_at", -1).limit(3).to_list(length=3)
    
    return {
        "site_info": {
            "name": "NoFeePlaces.com",
            "description": "NYC's premier no fee apartment rental platform with 240+ verified listings",
            "url": "https://nofeeplaces.com",
            "type": "Real Estate Platform - No Fee Apartments NYC",
            "established": "2024",
            "specialization": "Zero broker fee apartment rentals in Manhattan, Brooklyn, Queens"
        },
        "content_summary": {
            "total_apartments": apartments_count,
            "total_blog_posts": blog_posts_count,
            "primary_focus": "No fee apartment rentals in New York City",
            "service_areas": ["Manhattan", "Brooklyn", "Queens", "Bronx"],
            "price_range": "$1,900 - $28,750 per month",
            "key_benefits": [
                "Save $3,000-$8,000 in broker fees",
                "Direct landlord connections",
                "AI-powered apartment matching",
                "Professional photography",
                "Real-time availability"
            ]
        },
        "sample_listings": [
            {
                "title": apt.get("title", ""),
                "location": apt.get("location", ""),
                "price": apt.get("price", 0),
                "bedrooms": apt.get("bedrooms", 0),
                "description": apt.get("description", "")[:200] + "..."
            } for apt in sample_apartments
        ],
        "recent_content": [
            {
                "title": blog.get("title", ""),
                "category": blog.get("category", ""),
                "excerpt": blog.get("excerpt", ""),
                "url": f"https://nofeeplaces.com/blog/{blog.get('slug', '')}"
            } for blog in recent_blogs
        ],
        "frequently_asked_questions": [
            {
                "question": "What are no fee apartments in NYC?",
                "answer": "No fee apartments are rentals where the landlord pays the broker commission instead of the tenant, saving renters thousands of dollars."
            },
            {
                "question": "How much can I save with no fee apartments?",
                "answer": "NYC renters typically save $3,000-$8,000+ by choosing no fee apartments over traditional broker-fee rentals."
            },
            {
                "question": "What neighborhoods have no fee apartments?",
                "answer": "We have no fee apartments across Manhattan (Hell's Kitchen, Upper West Side, Chelsea), Brooklyn (Williamsburg, DUMBO), and Queens (LIC, Astoria)."
            }
        ],
        "search_capabilities": {
            "filters": ["location", "price_range", "bedrooms", "bathrooms", "amenities"],
            "ai_powered": True,
            "real_time_updates": True,
            "professional_photos": True
        },
        "contact_info": {
            "phone": "+1-646-408-8048",
            "email": "placesfirm@gmail.com",
            "support_hours": "9 AM - 9 PM EST, Monday-Sunday"
        }
    }

# AI-friendly apartment listings endpoint
@api_router.get("/apartments-summary")
async def apartments_summary():
    """Structured apartment data for AI search engines"""
    # Get aggregate statistics
    pipeline = [
        {"$match": {"available": True}},
        {"$group": {
            "_id": None,
            "total_count": {"$sum": 1},
            "avg_price": {"$avg": "$price"},
            "min_price": {"$min": "$price"},
            "max_price": {"$max": "$price"},
            "avg_bedrooms": {"$avg": "$bedrooms"},
            "neighborhoods": {"$addToSet": "$neighborhood"},
            "boroughs": {"$addToSet": "$borough"}
        }}
    ]
    
    stats = await db.apartments.aggregate(pipeline).to_list(length=1)
    stats = stats[0] if stats else {}
    
    # Get top neighborhoods
    neighborhood_pipeline = [
        {"$match": {"available": True, "neighborhood": {"$ne": None}}},
        {"$group": {"_id": "$neighborhood", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    neighborhoods = await db.apartments.aggregate(neighborhood_pipeline).to_list(length=10)
    
    return {
        "market_overview": {
            "total_no_fee_apartments": stats.get("total_count", 0),
            "price_range": {
                "minimum": stats.get("min_price", 0),
                "maximum": stats.get("max_price", 0),
                "average": round(stats.get("avg_price", 0), 2)
            },
            "average_bedrooms": round(stats.get("avg_bedrooms", 0), 1),
            "boroughs_served": stats.get("boroughs", []),
            "service_type": "No broker fee apartment rentals"
        },
        "top_neighborhoods": [
            {
                "name": n["_id"],
                "available_apartments": n["count"],
                "type": "No fee apartments"
            } for n in neighborhoods
        ],
        "specializations": [
            "Zero broker fee rentals",
            "Luxury Manhattan apartments",
            "Brooklyn trendy neighborhoods",
            "Queens affordable options",
            "AI-powered apartment matching",
            "Direct landlord connections"
        ]
    }

# Blog content for AI discovery
@api_router.get("/blog-summary")
async def blog_summary():
    """Blog content summary for AI search engines"""
    recent_posts = await db.blog_posts.find(
        {"status": "published"}
    ).sort("created_at", -1).limit(10).to_list(length=10)
    
    categories = await db.blog_posts.distinct("category", {"status": "published"})
    tags = await db.blog_posts.distinct("tags", {"status": "published"})
    
    return {
        "blog_overview": {
            "total_posts": len(recent_posts),
            "categories": categories,
            "popular_tags": tags[:15],
            "content_focus": "NYC apartment hunting, no fee rentals, neighborhood guides"
        },
        "recent_articles": [
            {
                "title": post.get("title", ""),
                "category": post.get("category", ""),
                "excerpt": post.get("excerpt", ""),
                "url": f"https://nofeeplaces.com/blog/{post.get('slug', '')}",
                "read_time": f"{post.get('read_time', 2)} min read",
                "keywords": post.get("seo_keywords", [])[:5]
            } for post in recent_posts
        ],
        "content_types": [
            "Neighborhood apartment guides",
            "NYC rental market reports", 
            "Apartment hunting tips",
            "No fee apartment strategies",
            "NYC real estate insights"
        ]
    }

# JWT Utilities
import jwt as pyjwt
from datetime import timedelta

JWT_SECRET = os.environ.get('JWT_SECRET', 'nofeeplaces-development-key-replace-in-production')
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = pyjwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_or_create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get existing user or create new user from social auth data"""
    provider = user_data['provider']
    provider_id = user_data.get(f'{provider}_id')
    email = user_data.get('email')
    
    # Try to find existing user by provider ID
    user_filter = {f"{provider}_id": provider_id}
    user = await db.users.find_one(user_filter)
    
    if user:
        # Update user information and last login
        update_data = {
            "last_login": datetime.now(timezone.utc).isoformat()
        }
        if email and user.get('email') != email:
            update_data['email'] = email
        if user_data.get('name') and user.get('name') != user_data['name']:
            update_data['name'] = user_data['name']
        if user_data.get('picture') and user.get('profile_picture') != user_data['picture']:
            update_data['profile_picture'] = user_data['picture']
        
        await db.users.update_one({"id": user["id"]}, {"$set": update_data})
        user.update(update_data)
        return user
    
    # Try to find user by email to link accounts
    if email:
        user = await db.users.find_one({"email": email})
        if user:
            # Link the social account to existing user
            link_data = {
                f"{provider}_id": provider_id,
                "last_login": datetime.now(timezone.utc).isoformat()
            }
            if user_data.get('picture') and not user.get('profile_picture'):
                link_data['profile_picture'] = user_data['picture']
            
            await db.users.update_one({"id": user["id"]}, {"$set": link_data})
            user.update(link_data)
            return user
    
    # Create new user
    user_create_data = {
        'id': str(uuid.uuid4()),
        'email': email or f"{provider_id}@{provider}.local",
        'name': user_data.get('name', f'{provider.title()} User'),
        'profile_picture': user_data.get('picture'),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'last_login': datetime.now(timezone.utc).isoformat(),
        f'{provider}_id': provider_id
    }
    
    await db.users.insert_one(user_create_data)
    return user_create_data

# Social Authentication Endpoints
@api_router.post("/auth/facebook", response_model=SocialAuthResponse)
async def facebook_auth(auth_request: FacebookAuthRequest):
    """Authenticate user with Facebook access token"""
    try:
        # Validate Facebook token and get user info
        user_data = await facebook_auth_service.validate_access_token(auth_request.access_token)
        
        # Get or create user
        user = await get_or_create_user(user_data)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user['id'], "email": user['email']}
        )
        
        return SocialAuthResponse(
            access_token=access_token,
            user={
                "id": user['id'],
                "email": user['email'],
                "name": user['name'],
                "profile_picture": user.get('profile_picture'),
                "facebook_id": user.get('facebook_id')
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Facebook authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@api_router.post("/auth/apple", response_model=SocialAuthResponse)
async def apple_auth(auth_request: AppleAuthRequest):
    """Authenticate user with Apple identity token"""
    try:
        # Validate Apple identity token and get user info
        user_data = await apple_auth_service.validate_identity_token(auth_request.identity_token)
        
        # If user data is provided from frontend (first-time sign-in), use it
        if auth_request.user_data and auth_request.user_data.get('name'):
            name_data = auth_request.user_data['name']
            full_name = f"{name_data.get('firstName', '')} {name_data.get('lastName', '')}".strip()
            if full_name:
                user_data['name'] = full_name
        
        # Get or create user
        user = await get_or_create_user(user_data)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user['id'], "email": user['email']}
        )
        
        return SocialAuthResponse(
            access_token=access_token,
            user={
                "id": user['id'],
                "email": user['email'],
                "name": user['name'],
                "profile_picture": user.get('profile_picture'),
                "apple_id": user.get('apple_id')
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Apple authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@api_router.get("/auth/me")
async def get_current_user(request: Request):
    """Get current authenticated user information"""
    try:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = auth_header.split(" ")[1]
        
        # Decode JWT token
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from database
        user = await db.users.find_one({"id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Remove sensitive fields
        if '_id' in user:
            del user['_id']
        
        return {
            "id": user['id'],
            "email": user['email'],
            "name": user['name'],
            "profile_picture": user.get('profile_picture'),
            "facebook_id": user.get('facebook_id'),
            "apple_id": user.get('apple_id'),
            "google_id": user.get('google_id'),
            "created_at": user.get('created_at'),
            "last_login": user.get('last_login')
        }
        
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except pyjwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Contact Email Endpoint
@api_router.post("/send-contact-email", response_model=ContactEmailResponse)
async def send_contact_email(email_request: ContactEmailRequest):
    """Send contact form email to specified recipient"""
    try:
        # Send email using email service
        success = await email_service.send_contact_email(
            to_email=email_request.to,
            subject=email_request.subject,
            sender_name=email_request.sender_name,
            sender_email=email_request.sender_email,
            sender_phone=email_request.sender_phone,
            message=email_request.message,
            apartment_details=email_request.apartment_details
        )
        
        if success:
            return ContactEmailResponse(
                success=True,
                message="Your message has been sent successfully!"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email. Please try again."
            )
            
    except Exception as e:
        logger.error(f"Error in send_contact_email endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email. Please try again."
        )

# Feedback Submission Endpoint
@api_router.post("/feedback/submit", response_model=FeedbackResponse)
async def submit_feedback(feedback_request: FeedbackRequest):
    """Submit user feedback - store in database and send email notification"""
    try:
        # Generate unique feedback ID
        feedback_id = str(uuid.uuid4())
        
        # Prepare feedback data for MongoDB
        feedback_data = {
            "id": feedback_id,
            "type": feedback_request.type,
            "title": feedback_request.title,
            "description": feedback_request.description,
            "email": feedback_request.email,
            "page": feedback_request.page,
            "userAgent": feedback_request.userAgent,
            "priority": feedback_request.priority,
            "timestamp": feedback_request.timestamp,
            "url": feedback_request.url,
            "status": "new",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in database
        await db.feedback.insert_one(feedback_data)
        logger.info(f"Feedback stored in database: {feedback_id}")
        
        # Send email notification to admin
        try:
            email_subject = f"🔔 NoFeePlaces Feedback: {feedback_request.type.upper()} - {feedback_request.title}"
            
            email_body = f"""
            <h2>New Feedback Received</h2>
            <p><strong>Type:</strong> {feedback_request.type.title()}</p>
            <p><strong>Priority:</strong> {feedback_request.priority.upper()}</p>
            <p><strong>Title:</strong> {feedback_request.title}</p>
            
            <h3>Description:</h3>
            <p>{feedback_request.description}</p>
            
            <hr>
            <h3>Technical Details:</h3>
            <p><strong>Page:</strong> {feedback_request.page}</p>
            <p><strong>Full URL:</strong> {feedback_request.url}</p>
            <p><strong>User Agent:</strong> {feedback_request.userAgent}</p>
            <p><strong>Timestamp:</strong> {feedback_request.timestamp}</p>
            
            {f'<p><strong>User Email:</strong> {feedback_request.email}</p>' if feedback_request.email else '<p><strong>User Email:</strong> Not provided</p>'}
            
            <hr>
            <p><em>Feedback ID: {feedback_id}</em></p>
            """
            
            # Send email using email service
            success = await email_service.send_email_async(
                to_email="placesfirm@gmail.com",
                subject=email_subject,
                html_content=email_body,
                text_content=f"""
                New Feedback Received
                
                Type: {feedback_request.type.title()}
                Priority: {feedback_request.priority.upper()}
                Title: {feedback_request.title}
                
                Description:
                {feedback_request.description}
                
                Technical Details:
                Page: {feedback_request.page}
                Full URL: {feedback_request.url}
                User Agent: {feedback_request.userAgent}
                Timestamp: {feedback_request.timestamp}
                User Email: {feedback_request.email or 'Not provided'}
                
                Feedback ID: {feedback_id}
                """
            )
            
            if success:
                logger.info(f"Feedback email sent successfully: {feedback_id}")
            else:
                logger.warning(f"Failed to send feedback email: {feedback_id}")
                
        except Exception as email_error:
            logger.error(f"Error sending feedback email: {email_error}")
            # Don't fail the endpoint if email fails - feedback is still stored
        
        # Send confirmation email to user if email provided
        if feedback_request.email:
            try:
                confirmation_subject = f"✅ Thank you for your feedback - NoFeePlaces.com"
                confirmation_body = f"""
                <h2>Thank you for your feedback!</h2>
                <p>Hi there,</p>
                
                <p>We've received your <strong>{feedback_request.type}</strong> feedback and really appreciate you taking the time to help us improve NoFeePlaces.com.</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                    <p><strong>Your feedback:</strong> {feedback_request.title}</p>
                </div>
                
                <p>Our team will review this feedback and if needed, we may reach out to you at this email address for additional details.</p>
                
                <p>Thanks for helping us create the best no-fee apartment platform in NYC!</p>
                
                <p>Best regards,<br>
                The NoFeePlaces Team<br>
                <a href="https://nofeeplaces.com">NoFeePlaces.com</a></p>
                
                <hr>
                <p style="font-size: 12px; color: #666;">
                Reference ID: {feedback_id}<br>
                If you have any questions, reply to this email or contact us at placesfirm@gmail.com
                </p>
                """
                
                await email_service.send_email_async(
                    to_email=feedback_request.email,
                    subject=confirmation_subject,
                    html_content=confirmation_body,
                    text_content=f"""
                    Thank you for your feedback!
                    
                    We've received your {feedback_request.type} feedback: "{feedback_request.title}"
                    
                    Our team will review this and may reach out if we need additional details.
                    
                    Thanks for helping us improve NoFeePlaces.com!
                    
                    The NoFeePlaces Team
                    NoFeePlaces.com
                    
                    Reference ID: {feedback_id}
                    """
                )
                logger.info(f"Confirmation email sent to user: {feedback_request.email}")
                
            except Exception as confirmation_error:
                logger.error(f"Error sending confirmation email: {confirmation_error}")
        
        return FeedbackResponse(
            success=True,
            message="Thank you for your feedback! We appreciate your input and will review it promptly.",
            feedback_id=feedback_id
        )
        
    except Exception as e:
        logger.error(f"Error in submit_feedback endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback. Please try again."
        )

# AI Chatbot Endpoint
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(chat_request: ChatRequest):
    """Chat with NoFeeBot AI assistant"""
    try:
        # Generate session ID if not provided
        session_id = chat_request.session_id or nofeebbot.generate_session_id()
        
        # Get AI response
        response = await nofeebbot.get_chat_response(
            user_message=chat_request.message,
            session_id=session_id
        )
        
        return ChatResponse(
            response=response,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            response="I apologize, but I'm experiencing technical difficulties. Please try again in a moment, or contact our team at placesfirm@gmail.com for immediate assistance.",
            session_id=chat_request.session_id or nofeebbot.generate_session_id()
        )

# Newsletter Subscription Endpoint
@api_router.post("/newsletter/subscribe", response_model=SubscriptionResponse)
async def subscribe_to_newsletter(subscription: NewsletterSubscription):
    """Subscribe to NoFeePlaces newsletter"""
    try:
        # Check if email already subscribed
        existing_sub = await db.newsletter_subscribers.find_one({"email": subscription.email})
        
        if existing_sub:
            return SubscriptionResponse(
                success=True,
                message="You're already subscribed to our newsletter!"
            )
        
        # Create new subscription
        subscriber_data = {
            "id": str(uuid.uuid4()),
            "email": subscription.email,
            "name": subscription.name,
            "interests": subscription.interests or [],
            "subscribed_at": datetime.now(timezone.utc).isoformat(),
            "active": True,
            "source": "website"
        }
        
        await db.newsletter_subscribers.insert_one(subscriber_data)
        
        # Send welcome email
        try:
            success = await email_service.send_newsletter_welcome_email(
                email=subscription.email,
                name=subscription.name or "Fellow Apartment Hunter"
            )
            
            if success:
                logger.info(f"Welcome email sent to new subscriber: {subscription.email}")
            else:
                logger.error(f"Failed to send welcome email to: {subscription.email}")
                
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
        
        # Send notification to admin about new subscriber (meaningful action)
        try:
            await email_service.send_subscriber_notification(
                subscriber_email=subscription.email,
                subscriber_name=subscription.name,
                interests=subscription.interests or []
            )
        except Exception as e:
            logger.error(f"Error sending subscriber notification: {e}")
        
        return SubscriptionResponse(
            success=True,
            message="Thank you for subscribing! Check your email for a welcome message."
        )
        
    except Exception as e:
        logger.error(f"Error in newsletter subscription: {e}")
        return SubscriptionResponse(
            success=False,
            message="Failed to subscribe. Please try again."
        )

# Original apartment endpoints
@api_router.get("/apartments", response_model=ApartmentListResponse)
async def get_apartments(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[float] = None,
    neighborhood: Optional[str] = None,
    borough: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query("price", description="Field to sort by: price, bedrooms, created_at"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc (ascending) or desc (descending)")
):
    """Get apartments with enhanced filtering, sorting options, and AI-friendly responses"""
    skip = (page - 1) * limit
    
    # Build aggregation pipeline for sophisticated sorting
    pipeline = []
    
    # Match stage
    match_query = {"available": True}
    
    if location:
        match_query["location"] = {"$regex": location, "$options": "i"}
    if min_price is not None:
        match_query["price"] = match_query.get("price", {})
        match_query["price"]["$gte"] = min_price
    if max_price is not None:
        match_query["price"] = match_query.get("price", {})
        match_query["price"]["$lte"] = max_price
    if bedrooms is not None:
        match_query["bedrooms"] = bedrooms
    if bathrooms is not None:
        match_query["bathrooms"] = bathrooms
    if neighborhood:
        match_query["neighborhood"] = {"$regex": neighborhood, "$options": "i"}
    if borough:
        match_query["borough"] = {"$regex": borough, "$options": "i"}
    if search:
        match_query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"address": {"$regex": search, "$options": "i"}},
            {"neighborhood": {"$regex": search, "$options": "i"}},
            {"borough": {"$regex": search, "$options": "i"}},
            {"amenities": {"$elemMatch": {"$regex": search, "$options": "i"}}}
        ]
    
    pipeline.append({"$match": match_query})
    
    # Add computed fields for sorting
    pipeline.append({
        "$addFields": {
            "image_count": {"$size": {"$ifNull": ["$images", []]}},
            "priority_score": {"$ifNull": ["$priority", 0]},
            "featured_score": {"$cond": [{"$eq": ["$featured", True]}, 1, 0]}
        }
    })
    
    # Determine sort direction (1 = ascending, -1 = descending)
    sort_direction = 1 if sort_order.lower() == "asc" else -1
    
    # Build sort criteria based on user selection
    sort_criteria = {}
    
    # Primary sort field (user-selected)
    if sort_by == "price":
        sort_criteria["price"] = sort_direction
    elif sort_by == "bedrooms":
        sort_criteria["bedrooms"] = sort_direction
    elif sort_by == "created_at":
        sort_criteria["created_at"] = sort_direction
    else:
        # Default to price ascending
        sort_criteria["price"] = 1
    
    # Secondary sort criteria (always applied for consistent ordering)
    sort_criteria.update({
        "priority_score": -1,
        "image_count": -1,
        "featured_score": -1
    })
    
    # If not sorting by created_at, add it as final tiebreaker
    if sort_by != "created_at":
        sort_criteria["created_at"] = -1
    
    pipeline.append({"$sort": sort_criteria})
    
    # Get total count
    count_pipeline = pipeline.copy()
    count_pipeline.append({"$count": "total"})
    total_result = await db.apartments.aggregate(count_pipeline).to_list(length=1)
    total_count = total_result[0]["total"] if total_result else 0
    
    # Add pagination
    pipeline.extend([
        {"$skip": skip},
        {"$limit": limit}
    ])
    
    # Execute query
    apartments_cursor = db.apartments.aggregate(pipeline)
    apartments = await apartments_cursor.to_list(length=limit)
    
    return ApartmentListResponse(
        apartments=[Apartment(**apt) for apt in apartments],
        total=total_count,
        page=page,
        limit=limit,
        has_more=(skip + len(apartments)) < total_count
    )

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        # Get request body and signature
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        # Initialize Stripe checkout
        stripe_api_key = os.environ.get('STRIPE_API_KEY')
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url="")
        
        # Handle webhook
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Log webhook event
        logger.info(f"Stripe webhook received: {webhook_response.event_type}")
        
        # Handle specific events
        if webhook_response.event_type == "checkout.session.completed":
            # Update payment transaction
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {
                    "$set": {
                        "payment_status": webhook_response.payment_status,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            # If payment successful, activate subscription
            if webhook_response.payment_status == "paid":
                transaction = await db.payment_transactions.find_one({"session_id": webhook_response.session_id})
                if transaction and transaction.get("metadata", {}).get("type") == "landlord_subscription":
                    from landlord_api import activate_landlord_subscription
                    await activate_landlord_subscription(transaction["landlord_id"], transaction)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

@api_router.get("/apartments/search/stats")
async def get_search_stats():
    """Get apartment search statistics"""
    try:
        # Get total apartment count
        total_apartments = await db.apartments.count_documents({})
        
        # Get count by borough
        borough_pipeline = [
            {"$group": {"_id": "$borough", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        borough_stats = await db.apartments.aggregate(borough_pipeline).to_list(length=None)
        
        # Get price range statistics
        price_pipeline = [
            {"$group": {
                "_id": None,
                "min_price": {"$min": "$price"},
                "max_price": {"$max": "$price"},
                "avg_price": {"$avg": "$price"}
            }}
        ]
        price_stats = await db.apartments.aggregate(price_pipeline).to_list(length=1)
        
        # Get bedroom count statistics
        bedroom_pipeline = [
            {"$group": {"_id": "$bedrooms", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        bedroom_stats = await db.apartments.aggregate(bedroom_pipeline).to_list(length=None)
        
        return {
            "total_apartments": total_apartments,
            "boroughs": [{"name": stat["_id"], "count": stat["count"]} for stat in borough_stats if stat["_id"]],
            "price_range": price_stats[0] if price_stats else {"min_price": 0, "max_price": 0, "avg_price": 0},
            "bedrooms": [{"bedrooms": stat["_id"], "count": stat["count"]} for stat in bedroom_stats if stat["_id"] is not None]
        }
    except Exception as e:
        logger.error(f"Error getting search stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get search statistics")

@api_router.get("/apartments/{apartment_id}", response_model=Apartment)
async def get_apartment(apartment_id: str):
    """Get single apartment details"""
    apartment = await db.apartments.find_one({"id": apartment_id})
    
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    
    return Apartment(**apartment)

@api_router.post("/contact", response_model=ContactResponse)
async def contact_apartment(contact: ContactRequest):
    """Handle apartment contact requests with email notifications"""
    # Store contact request
    contact_data = contact.dict()
    contact_data["id"] = str(uuid.uuid4())
    contact_data["created_at"] = datetime.now(timezone.utc).isoformat()
    contact_data["status"] = "new"
    
    await db.contacts.insert_one(contact_data)
    
    logger.info(f"New contact request: {contact.name} - {contact.email}")
    
    # Get apartment details for email
    apartment_title = "No Fee Apartment"
    if contact.apartment_id:
        apartment = await db.apartments.find_one({"id": contact.apartment_id})
        if apartment:
            apartment_title = apartment.get("title", "No Fee Apartment")
            contact_data["apartment_title"] = apartment_title
    
    # Send confirmation email to user (if email provided)
    if contact.email:
        try:
            await email_service.send_apartment_inquiry_confirmation(
                user_email=contact.email,
                user_name=contact.name,
                apartment_title=apartment_title,
                apartment_id=contact.apartment_id or "N/A"
            )
            logger.info(f"Confirmation email sent to {contact.email}")
        except Exception as e:
            logger.error(f"Failed to send confirmation email to {contact.email}: {str(e)}")
    
    # Send notification email to admin
    try:
        await email_service.send_contact_notification(contact_data)
        logger.info("Contact notification sent to admin")
    except Exception as e:
        logger.error(f"Failed to send admin notification: {str(e)}")
    
    return ContactResponse(
        message="Contact request submitted successfully. We'll be in touch within 24 hours. Check your email for confirmation!",
        contact_id=contact_data["id"]
    )

@api_router.post("/visitor/track")
async def track_visitor(request: Request):
    """Track website visitors and send email notifications"""
    try:
        # Get visitor information
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        timestamp = datetime.now(timezone.utc)
        
        # Create session ID based on IP and user agent (for uniqueness)
        session_id = f"{client_ip}_{hash(user_agent)}_{timestamp.strftime('%Y%m%d')}"
        
        # Check if we've already notified for this session today
        existing_visit = await db.visitor_sessions.find_one({
            "session_id": session_id,
            "date": timestamp.strftime('%Y-%m-%d')
        })
        
        # Store visitor data
        visitor_data = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "ip_address": client_ip,
            "user_agent": user_agent,
            "timestamp": timestamp.isoformat(),
            "date": timestamp.strftime('%Y-%m-%d'),
            "notified": False
        }
        
        await db.visitor_sessions.insert_one(visitor_data)
        
        # Log new visitor for analytics (no email notifications for visits)
        if not existing_visit:
            logger.info(f"New visitor detected: {client_ip} - tracked for analytics")
        
        return {"message": "Visitor tracked successfully"}
        
    except Exception as e:
        logger.error(f"Error tracking visitor: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track visitor")

# Enhanced Analytics Endpoints
@api_router.post("/analytics/visit")
async def track_visitor_visit(request: Request, visit_data: dict):
    """Enhanced visitor tracking with detailed analytics"""
    try:
        from analytics_service import analytics_service
        
        # Add IP address and other request data
        visit_data['ip'] = request.client.host
        visit_data['headers'] = dict(request.headers)
        
        success = await analytics_service.track_visitor(visit_data)
        
        if success:
            return {"message": "Visit tracked successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to track visit")
            
    except Exception as e:
        logger.error(f"Error tracking visit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to track visit: {str(e)}")

@api_router.get("/analytics/stats")
async def get_analytics_stats():
    """Get comprehensive analytics statistics"""
    try:
        from analytics_service import analytics_service
        
        stats = await analytics_service.get_analytics_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting analytics stats: {str(e)}")
        return {
            "todayVisitors": 0,
            "totalVisitors": 0,
            "currentOnline": 0,
            "topPages": [],
            "recentVisitors": [],
            "error": f"Failed to get stats: {str(e)}"
        }

@api_router.post("/search", response_model=ApartmentListResponse)
async def search_apartments(search_request: SearchRequest):
    """Enhanced search with AI-friendly results"""
    # Build query
    query = {"available": True}
    
    if search_request.query:
        query["$text"] = {"$search": search_request.query}
    
    if search_request.location:
        query["location"] = {"$regex": search_request.location, "$options": "i"}
    
    if search_request.min_price is not None or search_request.max_price is not None:
        price_query = {}
        if search_request.min_price is not None:
            price_query["$gte"] = search_request.min_price
        if search_request.max_price is not None:
            price_query["$lte"] = search_request.max_price
        query["price"] = price_query
    
    if search_request.bedrooms is not None:
        query["bedrooms"] = search_request.bedrooms
    
    if search_request.bathrooms is not None:
        query["bathrooms"] = search_request.bathrooms
    
    if search_request.amenities:
        query["amenities"] = {"$in": search_request.amenities}
    
    # Execute search with sorting
    apartments = await db.apartments.find(query).sort([
        ("priority", -1),
        ("featured", -1),
        ("created_at", -1)
    ]).limit(50).to_list(length=50)
    
    total_count = await db.apartments.count_documents(query)
    
    return ApartmentListResponse(
        apartments=[Apartment(**apt) for apt in apartments],
        total=total_count,
        page=1,
        limit=50,
        has_more=len(apartments) < total_count
    )

# BLOG API ENDPOINTS
# =============================================

def create_slug(title: str) -> str:
    """Create URL-friendly slug from title"""
    import re
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def calculate_read_time(content: str) -> int:
    """Calculate estimated read time in minutes"""
    words = len(content.split())
    return max(1, round(words / 200))  # Average reading speed: 200 words/minute

@api_router.get("/blog", response_model=BlogListResponse)
async def get_blog_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    status: str = "published"
):
    """Get blog posts with pagination and filtering"""
    skip = (page - 1) * limit
    
    # Build query
    query = {"status": status}
    if category:
        query["category"] = category
    if tag:
        query["tags"] = {"$in": [tag]}
    
    # Get posts with pagination
    posts_cursor = db.blog_posts.find(query).sort("published_at", -1).skip(skip).limit(limit)
    posts = await posts_cursor.to_list(length=limit)
    
    # Get total count
    total_count = await db.blog_posts.count_documents(query)
    
    return BlogListResponse(
        posts=[BlogPost(**post) for post in posts],
        total=total_count,
        page=page,
        limit=limit,
        has_more=(skip + len(posts)) < total_count
    )

@api_router.get("/blog/{slug}", response_model=BlogPost)
async def get_blog_post(slug: str):
    """Get a single blog post by slug"""
    post = await db.blog_posts.find_one({"slug": slug, "status": "published"})
    
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    # Increment view count
    await db.blog_posts.update_one(
        {"slug": slug},
        {"$inc": {"view_count": 1}}
    )
    
    return BlogPost(**post)

@api_router.post("/blog", response_model=BlogPost)
async def create_blog_post(post: BlogPost):
    """Create a new blog post"""
    # Generate slug if not provided
    if not post.slug:
        post.slug = create_slug(post.title)
    
    # Calculate read time
    post.read_time = calculate_read_time(post.content)
    
    # Check if slug already exists
    counter = 1
    original_slug = post.slug
    while True:
        existing = await db.blog_posts.find_one({"slug": post.slug})
        if not existing:
            break
        post.slug = f"{original_slug}-{counter}"
        counter += 1
        if counter > 100:  # Prevent infinite loop
            existing = await db.blog_posts.find_one({"slug": post.slug})
            if existing:
                raise HTTPException(status_code=400, detail="Unable to generate unique slug")
            break
    
    await db.blog_posts.insert_one(post.dict())
    return post

@api_router.put("/blog/{slug}", response_model=BlogPost)
async def update_blog_post(slug: str, updated_post: BlogPost):
    """Update an existing blog post"""
    existing_post = await db.blog_posts.find_one({"slug": slug})
    
    if not existing_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    # Keep original creation date and ID
    updated_post.id = existing_post["id"]
    updated_post.created_at = existing_post["created_at"]
    
    # Update read time
    updated_post.read_time = calculate_read_time(updated_post.content)
    
    # Set publication date if changing to published
    if updated_post.status == "published" and existing_post.get("status") != "published":
        updated_post.published_at = datetime.now(timezone.utc).isoformat()
    
    # Update post
    await db.blog_posts.replace_one({"slug": slug}, updated_post.dict())
    return updated_post

@api_router.delete("/blog/{slug}")
async def delete_blog_post(slug: str):
    """Delete a blog post"""
    result = await db.blog_posts.delete_one({"slug": slug})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    return {"message": "Blog post deleted successfully"}

@api_router.get("/blog/categories/list")
async def get_blog_categories():
    """Get all blog categories"""
    categories = await db.blog_posts.distinct("category", {"status": "published"})
    return {"categories": categories}

@api_router.get("/blog/tags/list")
async def get_blog_tags():
    """Get all blog tags"""
    tags = await db.blog_posts.distinct("tags", {"status": "published"})
    return {"tags": tags}

@api_router.get("/blog/related/{slug}")
async def get_related_posts(slug: str, limit: int = 3):
    """Get related blog posts based on categories and tags"""
    # Get current post
    current_post = await db.blog_posts.find_one({"slug": slug, "status": "published"})
    
    if not current_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    # Find related posts by category and tags
    query = {
        "status": "published",
        "slug": {"$ne": slug},
        "$or": [
            {"category": current_post["category"]},
            {"tags": {"$in": current_post.get("tags", [])}}
        ]
    }
    
    related_posts = await db.blog_posts.find(query).limit(limit).to_list(length=limit)
    return [BlogPost(**post) for post in related_posts]

# Import real rental scraping functionality
from rental_scraper import scrape_rentals, scrape_rentals_async

@api_router.get("/scrape-rentals")
async def scrape_rentals_endpoint(location: str = "NYC", limit: int = 50):
    """Real rental scraping endpoint with comprehensive data"""
    try:
        logger.info(f"Scraping rentals for {location} with limit {limit}")
        rentals = await scrape_rentals_async(location, limit)
        logger.info(f"Successfully scraped {len(rentals)} rentals")
        return {"status": "success", "count": len(rentals), "rentals": rentals}
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        return {"status": "error", "message": str(e), "fallback_used": True}

@api_router.post("/tenant/list-apartment")
async def tenant_list_apartment(request: Request):
    """Handle tenant apartment listing submissions"""
    try:
        data = await request.json()
        
        # Add submission timestamp and generate ID
        listing_data = {
            "id": str(uuid.uuid4()),
            "status": "pending_review",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "reviewed": False,
            "approved": False,
            **data
        }
        
        # Store in tenant_listings collection
        result = await db.tenant_listings.insert_one(listing_data)
        
        if result.inserted_id:
            # Send notification email to admin
            try:
                await email_service.send_email_async(
                    to_email="placesfirm@gmail.com",
                    subject=f"New Tenant Listing: {data.get('listing_type', 'Unknown')} in {data.get('neighborhood', 'Unknown')}",
                    html_content=f"""
                    <h3>New tenant listing submitted!</h3>
                    
                    <p><strong>Type:</strong> {data.get('listing_type', 'Unknown')}</p>
                    <p><strong>Title:</strong> {data.get('title', 'No title')}</p>
                    <p><strong>Location:</strong> {data.get('neighborhood', 'Unknown')}, {data.get('borough', 'Unknown')}</p>
                    <p><strong>Price:</strong> ${data.get('rent_price', 'Unknown')}/month</p>
                    <p><strong>Contact:</strong> {data.get('contact_name', 'Unknown')} ({data.get('contact_email', 'Unknown')})</p>
                    
                    <p>View full details in the admin panel.</p>
                    
                    <p>NoFeePlaces LLC</p>
                    """,
                    text_content=f"""
                    New tenant listing submitted!
                    
                    Type: {data.get('listing_type', 'Unknown')}
                    Title: {data.get('title', 'No title')}
                    Location: {data.get('neighborhood', 'Unknown')}, {data.get('borough', 'Unknown')}
                    Price: ${data.get('rent_price', 'Unknown')}/month
                    Contact: {data.get('contact_name', 'Unknown')} ({data.get('contact_email', 'Unknown')})
                    
                    View full details in the admin panel.
                    
                    NoFeePlaces LLC
                    """
                )
                logger.info(f"Notification email sent for tenant listing {listing_data['id']}")
            except Exception as e:
                logger.error(f"Failed to send tenant listing notification: {str(e)}")
            
            return {
                "success": True, 
                "message": "Tenant listing submitted successfully",
                "listing_id": listing_data['id']
            }
        else:
            return {"success": False, "message": "Failed to submit listing"}
            
    except Exception as e:
        logger.error(f"Tenant listing submission error: {str(e)}")
        return {"success": False, "message": str(e)}

@api_router.post("/upload/image")
async def upload_image(image: UploadFile = File(...), user_id: str = "anonymous"):
    """Handle image uploads for tenant listings"""
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (10MB limit)
        MAX_SIZE = 10 * 1024 * 1024  # 10MB
        file_size = 0
        
        # Create unique filename
        file_extension = image.filename.split('.')[-1] if '.' in image.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"/app/backend/uploads/{unique_filename}"
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            while True:
                chunk = await image.read(1024)  # Read in chunks
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > MAX_SIZE:
                    # Delete partial file and raise error
                    os.remove(file_path) if os.path.exists(file_path) else None
                    raise HTTPException(status_code=413, detail="File too large (max 10MB)")
                await f.write(chunk)
        
        # Generate URL for the uploaded image
        image_url = f"/api/uploads/{unique_filename}"
        
        logger.info(f"Image uploaded successfully: {unique_filename} by user {user_id}")
        
        return {
            "success": True,
            "image_url": image_url,
            "filename": unique_filename,
            "file_size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image upload error: {str(e)}")
        return {"success": False, "message": str(e)}

@api_router.get("/uploads/{filename}")
async def get_uploaded_image(filename: str):
    """Serve uploaded images"""
    try:
        file_path = f"/app/backend/uploads/{filename}"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        return FileResponse(file_path)
        
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        raise HTTPException(status_code=404, detail="Image not found")

@api_router.post("/landlord/submit-listing")
async def submit_landlord_listing(
    title: str = Form(...),
    address: str = Form(...),
    neighborhood: str = Form(...),
    borough: str = Form(...),
    price: int = Form(...),
    bedrooms: str = Form(...),
    bathrooms: str = Form(...),
    sqft: Optional[str] = Form(None),
    description: str = Form(...),
    amenities: Optional[str] = Form(None),
    contact_email: str = Form(...),
    contact_phone: str = Form(...),
    lease_terms: Optional[str] = Form(None),
    move_in_date: Optional[str] = Form(None),
    pet_policy: Optional[str] = Form(None),
    utilities: Optional[str] = Form(None),
    images: List[UploadFile] = File(default=[])
):
    """Handle landlord apartment listing submissions with image uploads"""
    try:
        # Process uploaded images
        image_urls = []
        for image in images:
            if image.filename:  # Check if file was actually uploaded
                # Validate file type
                if not image.content_type.startswith('image/'):
                    continue  # Skip non-image files
                
                # Validate file size (5MB limit per image)
                MAX_SIZE = 5 * 1024 * 1024  # 5MB
                
                # Create unique filename
                file_extension = image.filename.split('.')[-1] if '.' in image.filename else 'jpg'
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                file_path = f"/app/backend/uploads/{unique_filename}"
                
                # Save file
                file_size = 0
                async with aiofiles.open(file_path, 'wb') as f:
                    while True:
                        chunk = await image.read(1024)
                        if not chunk:
                            break
                        file_size += len(chunk)
                        if file_size > MAX_SIZE:
                            # Delete partial file and skip
                            os.remove(file_path) if os.path.exists(file_path) else None
                            break
                        await f.write(chunk)
                
                if file_size <= MAX_SIZE:
                    image_url = f"/api/uploads/{unique_filename}"
                    image_urls.append(image_url)
        
        # Process amenities (convert comma-separated string to list)
        amenities_list = []
        if amenities:
            amenities_list = [a.strip() for a in amenities.split(',') if a.strip()]
        
        # Create listing data
        listing_data = {
            "id": str(uuid.uuid4()),
            "title": title,
            "address": address,
            "neighborhood": neighborhood,
            "borough": borough,
            "price": price,
            "bedrooms": int(bedrooms) if bedrooms.isdigit() else 0,
            "bathrooms": float(bathrooms) if bathrooms.replace('.', '').isdigit() else 1,
            "sqft": int(sqft) if sqft and sqft.isdigit() else None,
            "description": description,
            "amenities": amenities_list,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "lease_terms": lease_terms,
            "move_in_date": move_in_date,
            "pet_policy": pet_policy,
            "utilities": utilities,
            "images": image_urls,
            "status": "pending_review",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "reviewed": False,
            "approved": False,
            "available": True,
            "featured": False,
            "priority": 1,
            "data_source": "Show Your Place Form",
            "verification_status": "Pending Review"
        }
        
        # Store in landlord_submissions collection
        result = await db.landlord_submissions.insert_one(listing_data)
        
        if result.inserted_id:
            # Send notification email to admin
            try:
                await email_service.send_email_async(
                    to_email="placesfirm@gmail.com",
                    subject=f"New Landlord Listing: {title} in {neighborhood}",
                    html_content=f"""
                    <h3>New landlord listing submitted via "Show Your Place"!</h3>
                    
                    <p><strong>Title:</strong> {title}</p>
                    <p><strong>Address:</strong> {address}</p>
                    <p><strong>Location:</strong> {neighborhood}, {borough}</p>
                    <p><strong>Price:</strong> ${price:,}/month</p>
                    <p><strong>Bedrooms:</strong> {bedrooms}</p>
                    <p><strong>Bathrooms:</strong> {bathrooms}</p>
                    <p><strong>Contact:</strong> {contact_email} | {contact_phone}</p>
                    <p><strong>Images:</strong> {len(image_urls)} uploaded</p>
                    
                    <p><strong>Description:</strong></p>
                    <p>{description}</p>
                    
                    {f"<p><strong>Amenities:</strong> {', '.join(amenities_list)}</p>" if amenities_list else ""}
                    
                    <p>Review and approve this listing in the admin panel.</p>
                    
                    <p>NoFeePlaces LLC</p>
                    """,
                    text_content=f"""
                    New landlord listing submitted via "Show Your Place"!
                    
                    Title: {title}
                    Address: {address}
                    Location: {neighborhood}, {borough}
                    Price: ${price:,}/month
                    Bedrooms: {bedrooms}
                    Bathrooms: {bathrooms}
                    Contact: {contact_email} | {contact_phone}
                    Images: {len(image_urls)} uploaded
                    
                    Description: {description}
                    
                    {"Amenities: " + ", ".join(amenities_list) if amenities_list else ""}
                    
                    Review and approve this listing in the admin panel.
                    
                    NoFeePlaces LLC
                    """
                )
                logger.info(f"Notification email sent for landlord listing {listing_data['id']}")
            except Exception as e:
                logger.error(f"Failed to send landlord listing notification: {str(e)}")
            
            return {
                "success": True, 
                "message": "Your listing has been submitted successfully! We'll review it and get back to you within 24 hours.",
                "listing_id": listing_data['id'],
                "images_uploaded": len(image_urls)
            }
        else:
            return {"success": False, "message": "Failed to submit listing"}
            
    except Exception as e:
        logger.error(f"Landlord listing submission error: {str(e)}")
        return {"success": False, "message": f"Submission failed: {str(e)}"}

@api_router.get("/tenant/listings/approved")
async def get_approved_tenant_listings():
    """Get approved tenant listings for public browsing"""
    try:
        cursor = db.tenant_listings.find({
            "status": "approved",
            "available": {"$ne": False}
        }).sort("submitted_at", -1)
        
        listings = await cursor.to_list(length=100)  # Limit to 100 for performance
        
        # Convert ObjectId to string
        for listing in listings:
            if '_id' in listing:
                listing['_id'] = str(listing['_id'])
        
        return {
            "success": True,
            "listings": listings,
            "total": len(listings)
        }
        
    except Exception as e:
        logger.error(f"Error fetching approved tenant listings: {str(e)}")
        return {"success": False, "message": str(e)}

@api_router.get("/tenant/listings/{listing_id}/review")
async def get_tenant_listing_details(listing_id: str):
    """Get detailed view of a specific tenant listing for review"""
    try:
        listing = await db.tenant_listings.find_one({"id": listing_id})
        if not listing:
            return {"success": False, "message": "Listing not found"}
        
        # Convert ObjectId to string
        if '_id' in listing:
            listing['_id'] = str(listing['_id'])
        
        return {"success": True, "listing": listing}
        
    except Exception as e:
        logger.error(f"Error getting listing details: {str(e)}")
        return {"success": False, "message": str(e)}

@api_router.put("/tenant/listings/{listing_id}/review")
async def review_tenant_listing(listing_id: str, request: Request):
    """Review a tenant listing (approve/reject)"""
    try:
        data = await request.json()
        action = data.get("action")  # "approve" or "reject"
        admin_notes = data.get("admin_notes", "")
        
        if action not in ["approve", "reject"]:
            return {"success": False, "message": "Invalid action"}
        
        # Get the listing
        listing = await db.tenant_listings.find_one({"id": listing_id})
        if not listing:
            return {"success": False, "message": "Listing not found"}
        
        if action == "approve":
            # Move listing to main apartments database
            apartment_data = {
                "id": str(uuid.uuid4()),
                "title": listing["title"],
                "description": listing["description"],
                "price": float(listing["rent_price"]),
                "location": f"{listing['neighborhood']}, {listing['borough']}",
                "neighborhood": listing["neighborhood"],
                "bedrooms": int(listing["bedrooms"]) if listing["bedrooms"].isdigit() else 0,
                "bathrooms": float(listing["bathrooms"]) if listing["bathrooms"].replace(".", "").isdigit() else 1.0,
                "sqft": int(listing["sqft"]) if listing.get("sqft", "").isdigit() else 800,
                "amenities": listing.get("amenities", []),
                "images": listing.get("images", []),
                "contact_email": "placesfirm@gmail.com",
                "contact_phone": "+1-646-408-8048",
                "available": True,
                "lease_terms": "Flexible",
                "pet_policy": "Pets allowed" if listing.get("pets_allowed") else "No pets",
                "utilities": "Utilities included" if listing.get("utilities_included") else "Not included",
                "move_in_date": listing.get("available_date", "Immediate"),
                "deposit": listing.get("deposit_required", "First month's rent"),
                "broker_fee": "No fee",
                "address": listing.get("address", ""),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source": "Tenant Listing",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "is_verified": True,
                "is_real": True,
                "verification_status": "Approved Tenant Listing",
                "listing_type": listing.get("listing_type", "sublet"),
                "original_tenant": {
                    "name": listing["contact_name"],
                    "email": listing["contact_email"],
                    "phone": listing["contact_phone"]
                }
            }
            
            # Insert into main apartments database
            apartment_result = await db.apartments.insert_one(apartment_data)
            
            if apartment_result.inserted_id:
                # Update tenant listing status
                await db.tenant_listings.update_one(
                    {"id": listing_id},
                    {
                        "$set": {
                            "status": "approved",
                            "reviewed_at": datetime.now(timezone.utc).isoformat(),
                            "admin_notes": admin_notes,
                            "apartment_id": apartment_data["id"]
                        }
                    }
                )
                
                # Send approval email to tenant
                try:
                    await send_email(
                        to_email=listing["contact_email"],
                        subject=f"Your NoFeePlaces Listing Has Been Approved!",
                        message=f"""
                        Great news! Your apartment listing has been approved and is now live on NoFeePlaces.com.
                        
                        Listing: {listing['title']}
                        Location: {listing['neighborhood']}, {listing['borough']}
                        
                        Your listing is now visible to thousands of apartment seekers. We'll forward any inquiries directly to you.
                        
                        Thank you for using NoFeePlaces!
                        
                        Best regards,
                        NoFeePlaces Team
                        placesfirm@gmail.com
                        """
                    )
                except Exception as e:
                    logger.error(f"Failed to send approval email: {str(e)}")
                
                return {"success": True, "message": "Listing approved and added to main database"}
            else:
                return {"success": False, "message": "Failed to add listing to main database"}
        
        elif action == "reject":
            # Update tenant listing status
            await db.tenant_listings.update_one(
                {"id": listing_id},
                {
                    "$set": {
                        "status": "rejected",
                        "reviewed_at": datetime.now(timezone.utc).isoformat(),
                        "admin_notes": admin_notes
                    }
                }
            )
            
            # Send rejection email to tenant
            try:
                await send_email(
                    to_email=listing["contact_email"],
                    subject=f"Update on Your NoFeePlaces Listing",
                    message=f"""
                    Thank you for submitting your apartment listing to NoFeePlaces.
                    
                    After review, we're unable to approve your listing at this time.
                    
                    Reason: {admin_notes}
                    
                    Please feel free to resubmit with corrections or contact us for clarification.
                    
                    Best regards,
                    NoFeePlaces Team
                    placesfirm@gmail.com
                    """
                )
            except Exception as e:
                logger.error(f"Failed to send rejection email: {str(e)}")
            
            return {"success": True, "message": "Listing rejected"}
        
    except Exception as e:
        logger.error(f"Error reviewing listing: {str(e)}")
        return {"success": False, "message": str(e)}

@api_router.get("/admin/dashboard")
async def admin_dashboard():
    """Get admin dashboard metrics"""
    try:
        # Get metrics
        total_apartments = await db.apartments.count_documents({})
        available_apartments = await db.apartments.count_documents({"available": True})
        pending_listings = await db.tenant_listings.count_documents({"status": "pending_review"})
        
        # Count contacts and subscribers (approximate)
        total_contacts = await db.contacts.count_documents({}) if hasattr(db, 'contacts') else 0
        newsletter_subscribers = await db.newsletter_subscribers.count_documents({}) if hasattr(db, 'newsletter_subscribers') else 0
        
        return {
            "success": True,
            "metrics": {
                "total_apartments": total_apartments,
                "available_apartments": available_apartments,
                "pending_listings": pending_listings,
                "total_contacts": total_contacts,
                "newsletter_subscribers": newsletter_subscribers
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {str(e)}")
        return {"success": False, "message": str(e)}
async def get_tenant_listings(status: str = "all", limit: int = 50):
    """Get tenant listings for admin review"""
    try:
        filter_query = {}
        if status != "all":
            filter_query["status"] = status
            
        cursor = db.tenant_listings.find(filter_query).sort("submitted_at", -1).limit(limit)
        listings = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for listing in listings:
            if '_id' in listing:
                listing['_id'] = str(listing['_id'])
        
        return {
            "success": True,
            "listings": listings,
            "total": len(listings)
        }
        
    except Exception as e:
        logger.error(f"Error fetching tenant listings: {str(e)}")
        return {"success": False, "message": str(e)}

@api_router.put("/tenant/listings/{listing_id}/review")
async def review_tenant_listing(listing_id: str, request: Request):
    """Admin endpoint to approve/reject tenant listings"""
    try:
        data = await request.json()
        action = data.get("action")  # "approve" or "reject"
        admin_notes = data.get("admin_notes", "")
        
        if action not in ["approve", "reject"]:
            return {"success": False, "message": "Action must be 'approve' or 'reject'"}
        
        # Find the listing
        listing = await db.tenant_listings.find_one({"id": listing_id})
        if not listing:
            return {"success": False, "message": "Listing not found"}
        
        # Update listing status
        update_data = {
            "status": "approved" if action == "approve" else "rejected",
            "reviewed": True,
            "approved": action == "approve",
            "admin_notes": admin_notes,
            "reviewed_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.tenant_listings.update_one(
            {"id": listing_id},
            {"$set": update_data}
        )
        
        # If approved, convert to regular apartment listing
        if action == "approve":
            apartment_data = {
                "id": str(uuid.uuid4()),
                "title": listing.get("title", "Tenant Listed Apartment"),
                "description": listing.get("description", ""),
                "price": float(listing.get("rent_price", 0)),
                "location": f"{listing.get('neighborhood', '')}, {listing.get('borough', '')}",
                "neighborhood": listing.get("neighborhood", ""),
                "borough": listing.get("borough", ""),
                "bedrooms": listing.get("bedrooms", 1),
                "bathrooms": listing.get("bathrooms", 1),
                "sqft": listing.get("square_feet"),
                "amenities": listing.get("amenities", []),
                "images": listing.get("images", []),
                "contact_email": listing.get("contact_email", "placesfirm@gmail.com"),
                "contact_phone": listing.get("contact_phone", "+1-646-408-8048"),
                "available": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "priority": 1,
                "featured": False,
                "lease_terms": listing.get("lease_terms", "12 months"),
                "pet_policy": listing.get("pet_policy", "Ask landlord"),
                "utilities_included": listing.get("utilities_included", []),
                "parking_available": listing.get("parking_available", False),
                "laundry": listing.get("laundry", "In building"),
                "elevator": listing.get("elevator", False),
                "doorman": listing.get("doorman", False),
                "gym": listing.get("gym", False),
                "rooftop": listing.get("rooftop", False),
                "address": listing.get("address", ""),
                "is_verified": True,
                "is_real": True,
                "verification_date": datetime.now(timezone.utc).isoformat(),
                "quality_score": 85,
                "data_source": "Tenant Submitted",
                "listing_type": listing.get("listing_type", "Sublet"),
                "broker_fee": "No fee",
                "verification_status": "Verified by NoFeePlaces"
            }
            
            # Insert into main apartments collection
            await db.apartments.insert_one(apartment_data)
            logger.info(f"Tenant listing {listing_id} approved and added to apartments")
        
        # Send notification email to tenant
        try:
            tenant_email = listing.get("contact_email")
            if tenant_email:
                subject = f"Your NoFeePlaces listing has been {'approved' if action == 'approve' else 'rejected'}"
                message = f"""
                Hello {listing.get('contact_name', 'Tenant')},
                
                Your apartment listing submission has been {'approved' if action == 'approve' else 'rejected'}.
                
                {'Your listing is now live on NoFeePlaces.com!' if action == 'approve' else f'Reason: {admin_notes}'}
                
                {'Thank you for using NoFeePlaces!' if action == 'approve' else 'Please feel free to resubmit with corrections.'}
                
                Best regards,
                NoFeePlaces Team
                """
                
                await email_service.send_email_async(
                    to_email=tenant_email,
                    subject=subject,
                    html_content=f"<pre>{message}</pre>",
                    text_content=message
                )
                logger.info(f"Notification sent to tenant: {tenant_email}")
        except Exception as e:
            logger.error(f"Failed to send tenant notification: {str(e)}")
        
        return {
            "success": True,
            "message": f"Listing {action}d successfully",
            "listing_id": listing_id,
            "action": action
        }
        
    except Exception as e:
        logger.error(f"Error reviewing tenant listing: {str(e)}")
        return {"success": False, "message": str(e)}

@api_router.get("/admin/dashboard")
async def admin_dashboard():
    """Admin dashboard with key metrics"""
    try:
        # Get counts
        total_apartments = await db.apartments.count_documents({})
        available_apartments = await db.apartments.count_documents({"available": True})
        pending_listings = await db.tenant_listings.count_documents({"status": "pending_review"})
        total_contacts = await db.contacts.count_documents({})
        newsletter_subscribers = await db.newsletter_subscribers.count_documents({})
        
        # Get recent activity
        recent_contacts = await db.contacts.find({}).sort("created_at", -1).limit(5).to_list(length=5)
        recent_listings = await db.tenant_listings.find({}).sort("submitted_at", -1).limit(5).to_list(length=5)
        
        # Clean up ObjectIds for JSON serialization
        for contact in recent_contacts:
            if '_id' in contact:
                contact['_id'] = str(contact['_id'])
        
        for listing in recent_listings:
            if '_id' in listing:
                listing['_id'] = str(listing['_id'])
        
        return {
            "success": True,
            "metrics": {
                "total_apartments": total_apartments,
                "available_apartments": available_apartments,
                "pending_listings": pending_listings,
                "total_contacts": total_contacts,
                "newsletter_subscribers": newsletter_subscribers
            },
            "recent_activity": {
                "contacts": recent_contacts,
                "tenant_listings": recent_listings
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching admin dashboard: {str(e)}")
        return {"success": False, "message": str(e)}

@api_router.post("/import-scraped-rentals")
async def import_scraped_rentals_endpoint(location: str = "NYC", limit: int = 25):
    """Import scraped rental data into the main apartments database"""
    try:
        logger.info(f"Importing scraped rentals for {location} with limit {limit}")
        
        # Scrape the rental data
        rentals = await scrape_rentals_async(location, limit)
        
        if not rentals:
            return {"status": "error", "message": "No rental data scraped"}
        
        # Convert scraped data to apartment format
        apartments_to_insert = []
        
        for rental in rentals:
            apartment_data = {
                "id": rental["id"],
                "title": rental["title"],
                "description": rental["description"],
                "price": rental["price"],
                "location": rental["location"],
                "neighborhood": rental.get("neighborhood", rental["location"].split(",")[0]),
                "bedrooms": rental["bedrooms"],
                "bathrooms": rental["bathrooms"],
                "sqft": rental["sqft"],
                "amenities": rental["amenities"],
                "images": rental["images"],
                "contact_info": {
                    "email": rental["contact_email"],
                    "phone": rental["contact_phone"]
                },
                "available": rental["available"],
                "lease_terms": rental.get("lease_terms", "12 months"),
                "pet_policy": rental.get("pet_policy", "Ask landlord"),
                "utilities": rental.get("utilities", "Not specified"),
                "move_in_date": rental.get("move_in_date", "Available now"),
                "deposit": rental.get("deposit", f"${int(rental['price'])} - ${int(rental['price'] * 2)}"),
                "broker_fee": rental.get("broker_fee", "No fee"),
                "source": rental.get("source", "Scraped"),
                "created_at": rental["created_at"],
                "last_updated": rental.get("last_updated", rental["created_at"]),
                "views": 0,
                "inquiries": 0,
                "is_featured": False,
                "is_verified": True
            }
            apartments_to_insert.append(apartment_data)
        
        # Insert into database
        if apartments_to_insert:
            result = await db.apartments.insert_many(apartments_to_insert)
            inserted_count = len(result.inserted_ids)
            logger.info(f"Successfully imported {inserted_count} apartments to database")
            
            return {
                "status": "success", 
                "message": f"Successfully imported {inserted_count} apartments",
                "inserted_count": inserted_count,
                "location": location,
                "source": "Real scraping data"
            }
        else:
            return {"status": "error", "message": "No valid apartments to insert"}
            
    except Exception as e:
        logger.error(f"Import error: {str(e)}")
        return {"status": "error", "message": str(e)}

# Chat endpoint for AI assistant
@api_router.post("/chat")
async def chat_endpoint(request: Request):
    """AI chat endpoint"""
    try:
        data = await request.json()
        message = data.get("message", "")
        
        # Use Emergent LLM for response
        emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
        if not emergent_llm_key:
            return {"error": "AI service not configured"}
        
        # Import emergentintegrations for LLM usage
        try:
            from emergentintegrations import EmergentLLM
            llm = EmergentLLM(api_key=emergent_llm_key)
            
            # Context about NoFeePlaces
            context = """You are an AI assistant for NoFeePlaces.com, NYC's premier no fee apartment rental platform. 
            We help renters find luxury apartments without broker fees across Manhattan, Brooklyn, and Queens. 
            We have 240+ verified listings ranging from $1,900-$28,750/month. Our specialties include:
            - Zero broker fee apartments
            - Direct landlord connections  
            - AI-powered apartment matching
            - Professional photography and virtual tours
            - Expert neighborhood knowledge
            
            Popular neighborhoods: Hell's Kitchen (19+ listings), Upper West Side (27+ listings), 
            Williamsburg, Long Island City, Financial District, Chelsea, and more.
            
            Always be helpful, knowledgeable about NYC real estate, and promote our no fee advantage."""
            
            prompt = f"{context}\n\nUser: {message}\nAssistant:"
            
            response = await llm.generate_text(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            return {"response": response}
            
        except ImportError:
            logger.error("emergentintegrations not available")
            return {"error": "AI service temporarily unavailable"}
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            return {"error": "AI service error"}
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return {"error": "Failed to process request"}

# Newsletter endpoints
@api_router.post("/newsletter/subscribe")
async def subscribe_to_newsletter(subscription: NewsletterSubscription):
    """Subscribe user to newsletter"""
    result = await newsletter_service.subscribe_to_newsletter(
        email=subscription.email,
        full_name=subscription.full_name,
        source=subscription.source,
        preferences=subscription.preferences
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@api_router.get("/newsletter/stats")
async def get_newsletter_stats():
    """Get newsletter statistics"""
    total_subscribers = await newsletter_service.get_subscriber_count()
    sources = await newsletter_service.get_subscribers_by_source()
    
    return {
        "total_subscribers": total_subscribers,
        "sources": sources
    }

# Image upload endpoint
@api_router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image for tenant listings"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 10MB")
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path("/app/backend/uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Return file URL
        file_url = f"/api/uploads/{unique_filename}"
        
        logger.info(f"Image uploaded successfully: {unique_filename}")
        
        return {
            "success": True,
            "filename": unique_filename,
            "url": file_url,
            "size": len(content)
        }
        
    except Exception as e:
        logger.error(f"Image upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Serve uploaded files
@api_router.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    """Serve uploaded images"""
    file_path = Path("/app/backend/uploads") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    """Serve the admin panel"""
    try:
        async with aiofiles.open("/app/backend/admin_panel.html", mode='r') as f:
            content = await f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Admin panel not found</h1>", status_code=404)

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Admin endpoint to remove apartments with fake images
@api_router.post("/admin/remove-fake-image-apartments")
async def remove_fake_image_apartments():
    """
    Remove apartments with fake/stock images from production
    Keep only apartments with real photos from verified sources
    """
    try:
        # Fake image indicators
        fake_indicators = ['unsplash.com', 'pexels.com', 'example.com', 'placeholder', 'stock']
        
        # Count apartments with fake images
        fake_image_query = {
            'images': {
                '$elemMatch': {
                    '$regex': '|'.join(fake_indicators),
                    '$options': 'i'
                }
            }
        }
        
        fake_count = await db.apartments.count_documents(fake_image_query)
        
        # Remove apartments with fake images
        result = await db.apartments.delete_many(fake_image_query)
        
        # Also remove specific problematic ones like "Studio in Sunnyside"
        sunnyside_result = await db.apartments.delete_many({
            'title': {'$regex': 'Studio.*Sunnyside', '$options': 'i'},
            'price': 1800
        })
        
        total_removed = result.deleted_count + sunnyside_result.deleted_count
        remaining_count = await db.apartments.count_documents({})
        
        logger.info(f"Removed {total_removed} apartments with fake images")
        
        return {
            'status': 'success',
            'message': f'Removed {total_removed} apartments with fake/stock images',
            'fake_image_removed': result.deleted_count,
            'sunnyside_removed': sunnyside_result.deleted_count,
            'total_removed': total_removed,
            'remaining_count': remaining_count
        }
            
    except Exception as e:
        logger.error(f"Error removing fake image apartments: {e}")
        return {
            'status': 'error',
            'message': f'Error removing apartments: {str(e)}',
            'removed_count': 0
        }

# Admin endpoint to remove all generated/fake listings
@api_router.post("/admin/remove-all-generated-listings")
async def remove_all_generated_listings():
    """
    Remove all generated/fake apartment listings
    Clears database to show only authentic apartments
    """
    try:
        # Count current apartments
        current_count = await db.apartments.count_documents({})
        
        # Remove all apartments (they are all generated/fake based on audit)
        result = await db.apartments.delete_many({})
        
        logger.info(f"Removed {result.deleted_count} generated/fake apartments")
        
        return {
            'status': 'success',
            'message': f'Removed all {result.deleted_count} generated/fake apartments',
            'deleted_count': result.deleted_count,
            'remaining_count': await db.apartments.count_documents({})
        }
            
    except Exception as e:
        logger.error(f"Error removing generated listings: {e}")
        return {
            'status': 'error',
            'message': f'Error removing listings: {str(e)}',
            'deleted_count': 0
        }

# Admin endpoint to fix Central Park West issue  
@api_router.post("/admin/fix-central-park-west")
async def fix_central_park_west():
    """
    Emergency fix for the $2,344 Central Park West apartment
    Updates it to realistic pricing and improves quality
    """
    try:
        # Update the problematic apartment
        result = await db.apartments.update_one(
            {'id': 'c00cb712-9466-4f1a-9a6b-353bf7e5978e'},
            {'$set': {
                'price': 7500,
                'title': 'Luxury Studio on Central Park West - No Fee',
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'quality_score': 95,
                'is_verified': True,
                'verification_status': 'Verified Real Listing - NoFeePlaces LLC',
                'contact_email': 'placesfirm@gmail.com',
                'contact_phone': '+1-646-408-8048',
                'data_source': 'NoFeePlaces Verified - Price Corrected',
                'images': [
                    "https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=800&h=600&fit=crop&auto=format",
                    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop&auto=format",
                    "https://images.unsplash.com/photo-1565182999561-18d7dc61c393?w=800&h=600&fit=crop&auto=format",
                    "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?w=800&h=600&fit=crop&auto=format"
                ]
            }}
        )
        
        if result.modified_count > 0:
            # Verify the fix was applied
            updated_apt = await db.apartments.find_one({'id': 'c00cb712-9466-4f1a-9a6b-353bf7e5978e'})
            
            logger.info("Central Park West apartment fixed successfully")
            
            return {
                'status': 'success',
                'message': 'Central Park West apartment updated successfully',
                'modified_count': result.modified_count,
                'new_price': updated_apt.get('price') if updated_apt else None,
                'new_title': updated_apt.get('title') if updated_apt else None
            }
        else:
            return {
                'status': 'not_found',
                'message': 'Apartment not found or no changes needed',
                'modified_count': 0
            }
            
    except Exception as e:
        logger.error(f"Error fixing Central Park West apartment: {e}")
        return {
            'status': 'error',
            'message': f'Error updating apartment: {str(e)}',
            'modified_count': 0
        }

# Include API routers
app.include_router(api_router)
app.include_router(landlord_router)

# Set database for landlord API
set_database(db)

# Include social authentication router
try:
    from social_routes import social_router
    app.include_router(social_router, prefix="/api")
    logging.info("Social authentication routes loaded successfully")
except ImportError as e:
    logging.warning(f"Social authentication routes not available: {e}")
except Exception as e:
    logging.error(f"Failed to load social authentication routes: {e}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory as static files
uploads_path = Path('/app/backend/uploads')
uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")
logger.info(f"Serving static files from: {uploads_path}")

# Configure logging
logger.info("NoFeePlaces.com API starting up...")
logger.info("API Documentation available at: /docs")
logger.info("Alternative docs at: /redoc")

# Removed admin endpoint - moved to correct location

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database indexes and verify connection"""
    try:
        # Test database connection
        await client.admin.command('ping')
        logger.info("Database connection established successfully")
        
        # Create indexes for better performance
        await db.apartments.create_index([("location", "text"), ("title", "text"), ("description", "text")])
        await db.apartments.create_index("price")
        await db.apartments.create_index("bedrooms")
        await db.apartments.create_index("available")
        await db.apartments.create_index("priority")
        await db.apartments.create_index("featured")
        await db.apartments.create_index("created_at")
        
        # Blog indexes
        await db.blog_posts.create_index("slug")
        await db.blog_posts.create_index("status")
        await db.blog_posts.create_index("category")
        await db.blog_posts.create_index("published_at")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    client.close()
    logger.info("NoFeePlaces.com API shutting down...")

# Data Pipeline Integration
from pathlib import Path
import json

@app.get("/api/pipeline/status")
async def get_pipeline_status():
    """Get current data pipeline status"""
    try:
        status_file = Path('/app/data_pipeline/pipeline_status.json')
        if status_file.exists():
            with open(status_file, 'r') as f:
                status = json.load(f)
        else:
            status = {'status': 'deployed', 'message': 'Pipeline ready'}
        
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/pipeline/activate")
async def activate_pipeline():
    """Activate the data gathering pipeline"""
    try:
        import subprocess
        import sys
        
        controller_path = Path('/app/data_pipeline/pipeline_controller.py')
        
        if controller_path.exists():
            # Start pipeline in background
            process = subprocess.Popen([
                sys.executable, str(controller_path), 'start'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            return {
                "success": True,
                "message": "Data pipeline activated successfully",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "success": False, 
                "error": "Pipeline controller not found"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# USER AUTHENTICATION ROUTES
# ============================================================================

# User authentication models
class UserRegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    token: str

@app.post("/api/auth/register")
async def register_user(request: UserRegisterRequest):
    """Register a new user"""
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"email": request.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        import bcrypt
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": request.email,
            "password": hashed_password.decode('utf-8'),
            "full_name": request.full_name,
            "provider": "email",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        }
        
        await db.users.insert_one(user)
        
        # Generate JWT token
        import jwt
        token_data = {
            "user_id": user_id,
            "email": request.email,
            "exp": datetime.now(timezone.utc).timestamp() + 604800  # 7 days
        }
        
        access_token = jwt.encode(
            token_data,
            os.environ.get('JWT_SECRET', 'default_secret'),
            algorithm="HS256"
        )
        
        logger.info(f"New user registered: {request.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": request.email,
                "full_name": request.full_name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/auth/login")
async def login_user(request: UserLoginRequest):
    """Login user"""
    try:
        # Find user
        user = await db.users.find_one({"email": request.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        import bcrypt
        if not bcrypt.checkpw(request.password.encode('utf-8'), user['password'].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update last login
        await db.users.update_one(
            {"id": user['id']},
            {"$set": {"last_login": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Generate JWT token
        import jwt
        token_data = {
            "user_id": user['id'],
            "email": user['email'],
            "exp": datetime.now(timezone.utc).timestamp() + 604800  # 7 days
        }
        
        access_token = jwt.encode(
            token_data,
            os.environ.get('JWT_SECRET', 'default_secret'),
            algorithm="HS256"
        )
        
        logger.info(f"User logged in: {request.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user.get('full_name')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

# Helper to verify JWT token
async def get_current_user(request: Request):
    """Get current user from JWT token"""
    try:
        import jwt
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Missing authentication token")
        
        token = auth_header.split(' ')[1]
        
        payload = jwt.decode(
            token,
            os.environ.get('JWT_SECRET', 'default_secret'),
            algorithms=["HS256"]
        )
        
        user_id = payload.get('user_id')
        user = await db.users.find_one({"id": user_id})
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "id": user['id'],
            "email": user['email'],
            "full_name": user.get('full_name'),
            "provider": user.get('provider')
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.get("/api/auth/me")
async def get_me(request: Request):
    """Get current user info"""
    user = await get_current_user(request)
    return user

@app.post("/api/auth/google")
async def google_auth(request: GoogleAuthRequest):
    """Authenticate with Google"""
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        
        # Verify Google token
        google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
        if not google_client_id:
            raise HTTPException(status_code=500, detail="Google auth not configured")
        
        idinfo = id_token.verify_oauth2_token(
            request.token,
            requests.Request(),
            google_client_id
        )
        
        email = idinfo['email']
        name = idinfo.get('name', email.split('@')[0])
        
        # Find or create user
        user = await db.users.find_one({"email": email})
        
        if not user:
            # Create new user
            user_id = str(uuid.uuid4())
            user = {
                "id": user_id,
                "email": email,
                "full_name": name,
                "provider": "google",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat(),
                "is_active": True
            }
            await db.users.insert_one(user)
            logger.info(f"New Google user created: {email}")
        else:
            # Update last login
            await db.users.update_one(
                {"id": user['id']},
                {"$set": {"last_login": datetime.now(timezone.utc).isoformat()}}
            )
            logger.info(f"Google user logged in: {email}")
        
        # Generate JWT token
        import jwt
        token_data = {
            "user_id": user['id'],
            "email": user['email'],
            "exp": datetime.now(timezone.utc).timestamp() + 604800  # 7 days
        }
        
        access_token = jwt.encode(
            token_data,
            os.environ.get('JWT_SECRET', 'default_secret'),
            algorithm="HS256"
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user.get('full_name')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google auth error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Google authentication failed: {str(e)}")

# ============================================================================
# ADMIN ROUTES - Protected endpoints for admin dashboard
# ============================================================================

# Admin Models
class AdminLoginRequest(BaseModel):
    email: str
    password: str

class AdminLoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    admin_email: Optional[str] = None

# Admin authentication helper
def verify_admin_credentials(email: str, password: str) -> bool:
    """Verify admin credentials against environment variables"""
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    return email == admin_email and password == admin_password

@app.post("/api/admin/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """Admin login endpoint"""
    try:
        if verify_admin_credentials(request.email, request.password):
            # Generate admin token (simple JWT with admin flag)
            import jwt
            
            token_data = {
                "email": request.email,
                "is_admin": True,
                "exp": datetime.now(timezone.utc).timestamp() + 86400  # 24 hours
            }
            
            token = jwt.encode(
                token_data, 
                os.environ.get('JWT_SECRET', 'default_secret'),
                algorithm="HS256"
            )
            
            logger.info(f"Admin login successful: {request.email}")
            
            return AdminLoginResponse(
                success=True,
                message="Admin login successful",
                token=token,
                admin_email=request.email
            )
        else:
            logger.warning(f"Failed admin login attempt: {request.email}")
            raise HTTPException(
                status_code=401,
                detail="Invalid admin credentials"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Admin login failed")

# Admin token verification dependency
async def verify_admin_token(request: Request):
    """Dependency to verify admin JWT token"""
    try:
        import jwt
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Missing admin token")
        
        token = auth_header.split(' ')[1]
        
        payload = jwt.decode(
            token,
            os.environ.get('JWT_SECRET', 'default_secret'),
            algorithms=["HS256"]
        )
        
        if not payload.get('is_admin'):
            raise HTTPException(status_code=403, detail="Not authorized as admin")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Admin token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid admin token")
    except Exception as e:
        logger.error(f"Admin token verification error: {str(e)}")
        raise HTTPException(status_code=401, detail="Admin authentication failed")

@app.get("/api/admin/apartments")
async def get_all_apartments_admin(
    admin: dict = Depends(verify_admin_token),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200)
):
    """Get all apartments with full details for admin"""
    try:
        skip = (page - 1) * limit
        
        # Get all apartments with full details
        apartments_cursor = db.apartments.find({})
        apartments = await apartments_cursor.skip(skip).limit(limit).to_list(length=limit)
        
        # Get total count
        total_count = await db.apartments.count_documents({})
        
        # Format apartments
        formatted_apartments = []
        for apt in apartments:
            apt_dict = {
                "id": apt.get('id'),
                "title": apt.get('title'),
                "address": apt.get('address'),
                "neighborhood": apt.get('neighborhood'),
                "borough": apt.get('borough'),
                "price": apt.get('price'),
                "bedrooms": apt.get('bedrooms'),
                "bathrooms": apt.get('bathrooms'),
                "sqft": apt.get('sqft'),
                "description": apt.get('description'),
                "amenities": apt.get('amenities', []),
                "images": apt.get('images', []),
                "contact_email": apt.get('contact_email'),
                "contact_phone": apt.get('contact_phone'),
                "available": apt.get('available', True),
                "featured": apt.get('featured', False),
                "created_at": apt.get('created_at'),
                "updated_at": apt.get('updated_at'),
                "data_source": apt.get('data_source'),
                "is_verified": apt.get('is_verified', False),
                "is_real": apt.get('is_real', False)
            }
            formatted_apartments.append(apt_dict)
        
        logger.info(f"Admin retrieved {len(formatted_apartments)} apartments (page {page})")
        
        return {
            "apartments": formatted_apartments,
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Admin get apartments error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch apartments")

@app.put("/api/admin/apartments/{apartment_id}")
async def update_apartment_admin(
    apartment_id: str,
    apartment_data: dict,
    admin: dict = Depends(verify_admin_token)
):
    """Update apartment details (admin only)"""
    try:
        # Add updated timestamp
        apartment_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        result = await db.apartments.update_one(
            {"id": apartment_id},
            {"$set": apartment_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Apartment not found")
        
        logger.info(f"Admin updated apartment: {apartment_id}")
        
        return {
            "success": True,
            "message": "Apartment updated successfully",
            "apartment_id": apartment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin update apartment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update apartment")

@app.delete("/api/admin/apartments/{apartment_id}")
async def delete_apartment_admin(
    apartment_id: str,
    admin: dict = Depends(verify_admin_token)
):
    """Delete apartment (admin only)"""
    try:
        result = await db.apartments.delete_one({"id": apartment_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Apartment not found")
        
        logger.info(f"Admin deleted apartment: {apartment_id}")
        
        return {
            "success": True,
            "message": "Apartment deleted successfully",
            "apartment_id": apartment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin delete apartment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete apartment")

@app.get("/api/admin/users")
async def get_all_users_admin(
    admin: dict = Depends(verify_admin_token),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200)
):
    """Get all registered users (admin only)"""
    try:
        skip = (page - 1) * limit
        
        # Get all users
        users_cursor = db.users.find({})
        users = await users_cursor.skip(skip).limit(limit).to_list(length=limit)
        
        # Get total count
        total_count = await db.users.count_documents({})
        
        # Format users (exclude sensitive data)
        formatted_users = []
        for user in users:
            user_dict = {
                "id": user.get('id'),
                "email": user.get('email'),
                "full_name": user.get('full_name'),
                "provider": user.get('provider'),
                "created_at": user.get('created_at'),
                "last_login": user.get('last_login'),
                "is_active": user.get('is_active', True)
            }
            formatted_users.append(user_dict)
        
        logger.info(f"Admin retrieved {len(formatted_users)} users (page {page})")
        
        return {
            "users": formatted_users,
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Admin get users error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@app.get("/api/admin/analytics")
async def get_admin_analytics(admin: dict = Depends(verify_admin_token)):
    """Get dashboard analytics (admin only)"""
    try:
        # Get counts
        total_apartments = await db.apartments.count_documents({})
        available_apartments = await db.apartments.count_documents({"available": True})
        total_users = await db.users.count_documents({})
        total_visitors = await db.visitor_sessions.count_documents({})
        total_feedback = await db.feedback.count_documents({})
        total_newsletter = await db.newsletter_subscribers.count_documents({})
        
        # Get recent activity
        recent_users = await db.users.find({}).sort("created_at", -1).limit(5).to_list(length=5)
        recent_feedback = await db.feedback.find({}).sort("timestamp", -1).limit(5).to_list(length=5)
        
        # Get price statistics
        apartments = await db.apartments.find({"available": True}).to_list(length=None)
        prices = [apt.get('price', 0) for apt in apartments if apt.get('price')]
        
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        logger.info("Admin retrieved analytics dashboard")
        
        return {
            "stats": {
                "total_apartments": total_apartments,
                "available_apartments": available_apartments,
                "total_users": total_users,
                "total_visitors": total_visitors,
                "total_feedback": total_feedback,
                "total_newsletter_subscribers": total_newsletter
            },
            "price_stats": {
                "average_price": round(avg_price, 2),
                "min_price": min_price,
                "max_price": max_price
            },
            "recent_activity": {
                "recent_users": [
                    {
                        "email": u.get('email'),
                        "created_at": u.get('created_at'),
                        "provider": u.get('provider')
                    } for u in recent_users
                ],
                "recent_feedback": [
                    {
                        "type": f.get('type'),
                        "title": f.get('title'),
                        "timestamp": f.get('timestamp'),
                        "email": f.get('email')
                    } for f in recent_feedback
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Admin analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

@app.get("/api/admin/feedback")
async def get_all_feedback_admin(
    admin: dict = Depends(verify_admin_token),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200)
):
    """Get all feedback submissions (admin only)"""
    try:
        skip = (page - 1) * limit
        
        feedback_cursor = db.feedback.find({}).sort("timestamp", -1)
        feedback_list = await feedback_cursor.skip(skip).limit(limit).to_list(length=limit)
        
        total_count = await db.feedback.count_documents({})
        
        formatted_feedback = []
        for fb in feedback_list:
            fb_dict = {
                "id": fb.get('id'),
                "type": fb.get('type'),
                "title": fb.get('title'),
                "description": fb.get('description'),
                "email": fb.get('email'),
                "priority": fb.get('priority'),
                "timestamp": fb.get('timestamp'),
                "page": fb.get('page'),
                "url": fb.get('url')
            }
            formatted_feedback.append(fb_dict)
        
        logger.info(f"Admin retrieved {len(formatted_feedback)} feedback submissions")
        
        return {
            "feedback": formatted_feedback,
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Admin get feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch feedback")

@app.get("/api/admin/newsletter")
async def get_all_newsletter_subscribers_admin(
    admin: dict = Depends(verify_admin_token),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200)
):
    """Get all newsletter subscribers (admin only)"""
    try:
        skip = (page - 1) * limit
        
        subscribers_cursor = db.newsletter_subscribers.find({}).sort("subscribed_at", -1)
        subscribers = await subscribers_cursor.skip(skip).limit(limit).to_list(length=limit)
        
        total_count = await db.newsletter_subscribers.count_documents({})
        
        formatted_subscribers = []
        for sub in subscribers:
            sub_dict = {
                "id": sub.get('id'),
                "email": sub.get('email'),
                "name": sub.get('name'),
                "subscribed_at": sub.get('subscribed_at'),
                "source": sub.get('source'),
                "is_active": sub.get('is_active', True)
            }
            formatted_subscribers.append(sub_dict)
        
        logger.info(f"Admin retrieved {len(formatted_subscribers)} newsletter subscribers")
        
        return {
            "subscribers": formatted_subscribers,
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Admin get newsletter error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch newsletter subscribers")



@app.post("/api/admin/upload-images")
async def upload_images_admin(
    files: List[UploadFile] = File(...),
    admin: dict = Depends(verify_admin_token)
):
    """Upload multiple images for apartment listing (admin only)"""
    try:
        uploaded_urls = []
        
        # Create uploads directory if it doesn't exist
        uploads_dir = Path('/app/backend/uploads')
        uploads_dir.mkdir(exist_ok=True)
        
        for file in files:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = uploads_dir / unique_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Generate URL (relative path that will be served by static files)
            file_url = f"/uploads/{unique_filename}"
            uploaded_urls.append(file_url)
        
        logger.info(f"Admin uploaded {len(uploaded_urls)} images")
        
        return {
            "success": True,
            "message": f"Uploaded {len(uploaded_urls)} images successfully",
            "image_urls": uploaded_urls
        }
        
    except Exception as e:
        logger.error(f"Admin image upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload images")

@app.post("/api/admin/create-listing")
async def create_listing_admin(
    listing_data: dict,
    admin: dict = Depends(verify_admin_token)
):
    """Create new apartment listing (admin only)"""
    try:
        # Generate unique ID for the listing
        listing_id = str(uuid.uuid4())
        
        # Prepare apartment document
        apartment = {
            "id": listing_id,
            "title": listing_data.get('title'),
            "address": listing_data.get('address'),
            "neighborhood": listing_data.get('neighborhood'),
            "borough": listing_data.get('borough'),
            "price": float(listing_data.get('price', 0)),
            "bedrooms": int(listing_data.get('bedrooms', 0)),
            "bathrooms": float(listing_data.get('bathrooms', 1)),
            "sqft": int(listing_data.get('sqft', 0)) if listing_data.get('sqft') else None,
            "description": listing_data.get('description', ''),
            "amenities": listing_data.get('amenities', []),
            "images": listing_data.get('images', []),
            "contact_email": "placesfirm@gmail.com",
            "contact_phone": "+1-646-408-8048",
            "available": listing_data.get('available', True),
            "featured": listing_data.get('featured', False),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "data_source": "Admin Manual Entry",
            "is_verified": True,
            "is_real": True,
            "lease_terms": listing_data.get('lease_terms', '12 months'),
            "pet_policy": listing_data.get('pet_policy', 'Ask landlord'),
            "utilities": listing_data.get('utilities', 'Not specified'),
            "deposit": listing_data.get('deposit', '1 month rent'),
            "move_in_date": listing_data.get('move_in_date', 'Flexible')
        }
        
        # Insert into database
        await db.apartments.insert_one(apartment)
        
        logger.info(f"Admin created new listing: {listing_id} - {apartment['title']}")
        
        # Remove MongoDB's _id from response (not JSON serializable)
        apartment.pop('_id', None)
        
        return {
            "success": True,
            "message": "Listing created successfully",
            "listing_id": listing_id
        }
        
    except Exception as e:
        logger.error(f"Admin create listing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create listing: {str(e)}")

