from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
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
    lease_terms: Optional[str] = None
    pet_policy: Optional[str] = None
    utilities_included: Union[List[str], bool, None] = []  # Handle both list and boolean
    parking_available: Optional[bool] = False
    laundry: Optional[str] = None
    elevator: Optional[bool] = False
    doorman: Optional[bool] = False
    gym: Optional[bool] = False
    rooftop: Optional[bool] = False
    address: Optional[str] = None
    
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
    search: Optional[str] = None
):
    """Get apartments with enhanced filtering and AI-friendly responses"""
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
    
    # Sort: Priority first, then image count, then featured, then newest
    pipeline.append({
        "$sort": {
            "priority_score": -1,
            "image_count": -1,
            "featured_score": -1,
            "created_at": -1
        }
    })
    
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

# Scraping functionality - removed mock data for production
def scrape_rentals(location: str = "NYC", limit: int = 50) -> List[Dict[str, Any]]:
    """Production scraping function - integrate with real data sources"""
    logger.info(f"Scraping request for {location} with limit {limit}")
    
    # For production deployment, integrate with actual rental APIs:
    # - StreetEasy API (when available)
    # - RentSpree API integration  
    # - Apartment list scrapers
    # - MLS data feeds
    
    logger.warning("Scraping function called but no external data sources configured")
    return []

@api_router.get("/scrape-rentals")
async def scrape_rentals_endpoint(location: str = "NYC", limit: int = 50):
    """Production scraping endpoint - ready for external API integration"""
    try:
        rentals = scrape_rentals(location, limit)
        
        if not rentals:
            return {
                "status": "info", 
                "message": "No external scraping sources configured. Using existing database apartments.",
                "count": 0, 
                "rentals": []
            }
            
        return {"status": "success", "count": len(rentals), "rentals": rentals}
        
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
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

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include router in main app
app.include_router(api_router)

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

# Configure logging
logger.info("NoFeePlaces.com API starting up...")
logger.info(f"API Documentation available at: /docs")
logger.info(f"Alternative docs at: /redoc")

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