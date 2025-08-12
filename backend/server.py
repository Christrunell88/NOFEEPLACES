from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import uuid
import bcrypt
import jwt
import asyncio
import aiohttp
import json
from bs4 import BeautifulSoup
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-this-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

app = FastAPI(title="EasyRent.NYC API", version="1.0.0")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Pydantic Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    saved_searches: List[Dict] = []
    favorite_apartments: List[str] = []

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Apartment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    address: str
    price: int
    bedrooms: int
    bathrooms: float
    sqft: int
    neighborhood: str
    borough: str
    description: str
    amenities: List[str]
    images: List[str]
    contact_info: Dict[str, Any]
    available_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_no_fee: bool = True
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source_url: Optional[str] = None

class SearchFilters(BaseModel):
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    bedrooms: Optional[int] = None
    neighborhood: Optional[str] = None
    borough: Optional[str] = None
    search_term: Optional[str] = None
    min_sqft: Optional[int] = None
    max_sqft: Optional[int] = None
    amenities: Optional[List[str]] = None
    available_from: Optional[datetime] = None

class SavedSearch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    filters: SearchFilters
    created_at: datetime = Field(default_factory=datetime.utcnow)
    alert_frequency: str = "daily"  # daily, weekly, instant
    is_active: bool = True

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: str, email: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Web Scraping Functions
async def scrape_streeteasy_apartments():
    """Scrape StreetEasy for no-fee apartments"""
    apartments = []
    
    # Mock data for now - in production, you'd implement actual scraping
    mock_apartments = [
        {
            "title": "Luxury 1BR in Financial District - No Fee",
            "address": "125 Greenwich St, New York, NY 10006",
            "price": 3200,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 650,
            "neighborhood": "Financial District",
            "borough": "Manhattan",
            "description": "Stunning 1-bedroom apartment with floor-to-ceiling windows and premium finishes. Located in the heart of the Financial District with easy access to all major subway lines.",
            "amenities": ["Gym", "Doorman", "Rooftop Deck", "Pet Friendly", "Laundry", "Parking"],
            "images": [
                "https://images.unsplash.com/photo-1594295800284-990f74bb6928",
                "https://images.unsplash.com/photo-1568486776380-bf9c4e93347a"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=7),
            "latitude": 40.7074,
            "longitude": -74.0113,
            "source_url": "https://streeteasy.com/building/125-greenwich-street"
        },
        {
            "title": "Modern 2BR in Midtown East - No Broker Fee",
            "address": "300 E 55th St, New York, NY 10022",
            "price": 4500,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 900,
            "neighborhood": "Midtown East",
            "borough": "Manhattan",
            "description": "Spacious 2-bedroom apartment with modern kitchen, washer/dryer in unit, and stunning city views. Located near Grand Central and top restaurants.",
            "amenities": ["Concierge", "Pool", "Laundry In Unit", "Parking", "Gym", "Storage"],
            "images": [
                "https://images.pexels.com/photos/4090093/pexels-photo-4090093.jpeg",
                "https://images.unsplash.com/photo-1551250930-ace1ad395cea"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=30),
            "latitude": 40.7589,
            "longitude": -73.9647,
            "source_url": "https://streeteasy.com/building/300-east-55th-street"
        },
        {
            "title": "Spacious Studio in Brooklyn Heights - No Fee",
            "address": "85 Livingston St, Brooklyn, NY 11201",
            "price": 2800,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 500,
            "neighborhood": "Brooklyn Heights",
            "borough": "Brooklyn",
            "description": "Charming studio apartment with high ceilings and original hardwood floors. Located in historic Brooklyn Heights with easy access to Manhattan.",
            "amenities": ["Gym", "Garden", "Storage", "Pet Friendly", "Laundry"],
            "images": [
                "https://images.unsplash.com/photo-1553287222-da8a77d59c5c",
                "https://images.unsplash.com/photo-1618861138969-0d7a9d315b1f"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow(),
            "latitude": 40.6928,
            "longitude": -73.9939,
            "source_url": "https://streeteasy.com/building/85-livingston-street"
        },
        {
            "title": "Bright 1BR in Williamsburg - No Fee",
            "address": "200 Grand St, Brooklyn, NY 11249",
            "price": 3400,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 750,
            "neighborhood": "Williamsburg",
            "borough": "Brooklyn",
            "description": "Contemporary 1-bedroom with exposed brick walls and modern appliances. Steps from trendy restaurants and nightlife in Williamsburg.",
            "amenities": ["Rooftop", "Gym", "Pet Friendly", "Storage", "Bike Storage"],
            "images": [
                "https://images.unsplash.com/photo-1594295800284-990f74bb6928",
                "https://images.unsplash.com/photo-1568486776380-bf9c4e93347a"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "leasing@williamsburgplaces.com",
                "broker": "Urban Living NYC"
            },
            "available_date": datetime.utcnow() + timedelta(days=14),
            "latitude": 40.7081,
            "longitude": -73.9571,
            "source_url": "https://streeteasy.com/building/200-grand-street"
        },
        {
            "title": "Elegant 2BR in Upper West Side - No Fee",
            "address": "150 W 85th St, New York, NY 10024",
            "price": 5200,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1100,
            "neighborhood": "Upper West Side",
            "borough": "Manhattan",
            "description": "Classic pre-war charm meets modern luxury in this stunning 2-bedroom. Near Central Park and excellent restaurants.",
            "amenities": ["Doorman", "Elevator", "Storage", "Laundry", "Near Park"],
            "images": [
                "https://images.pexels.com/photos/4090093/pexels-photo-4090093.jpeg",
                "https://images.unsplash.com/photo-1551250930-ace1ad395cea"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@upperwestliving.com",
                "broker": "Manhattan Premium"
            },
            "available_date": datetime.utcnow() + timedelta(days=21),
            "latitude": 40.7851,
            "longitude": -73.9761,
            "source_url": "https://streeteasy.com/building/150-west-85th-street"
        },
        {
            "title": "Modern Studio in Long Island City - No Fee",
            "address": "42-12 28th St, Long Island City, NY 11101",
            "price": 2900,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 480,
            "neighborhood": "Long Island City",
            "borough": "Queens",
            "description": "Brand new studio with stunning Manhattan skyline views. Modern amenities and quick commute to Midtown Manhattan.",
            "amenities": ["River Views", "Gym", "Rooftop", "Concierge", "Pool"],
            "images": [
                "https://images.unsplash.com/photo-1553287222-da8a77d59c5c",
                "https://images.unsplash.com/photo-1618861138969-0d7a9d315b1f"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "leasing@licviews.com",
                "broker": "Queens Modern Living"
            },
            "available_date": datetime.utcnow() + timedelta(days=10),
            "latitude": 40.7505,
            "longitude": -73.9376,
            "source_url": "https://streeteasy.com/building/42-12-28th-street"
        },
        {
            "title": "Cozy 1BR in Chelsea - No Fee",
            "address": "150 W 26th St, New York, NY 10001",
            "price": 3800,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 600,
            "neighborhood": "Chelsea",
            "borough": "Manhattan",
            "description": "Charming 1-bedroom in the heart of Chelsea. Walking distance to High Line, Madison Square Garden, and amazing dining.",
            "amenities": ["Rooftop", "Gym", "Pet Friendly", "Laundry", "Storage"],
            "images": [
                "https://images.unsplash.com/photo-1594295800284-990f74bb6928",
                "https://images.unsplash.com/photo-1568486776380-bf9c4e93347a"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "rentals@chelseaplaces.com",
                "broker": "Chelsea Realty Group"
            },
            "available_date": datetime.utcnow() + timedelta(days=5),
            "latitude": 40.7441,
            "longitude": -73.9964,
            "source_url": "https://streeteasy.com/building/150-west-26th-street"
        },
        {
            "title": "Luxury 3BR in Upper East Side - No Fee",
            "address": "200 E 89th St, New York, NY 10128",
            "price": 6800,
            "bedrooms": 3,
            "bathrooms": 2.0,
            "sqft": 1400,
            "neighborhood": "Upper East Side",
            "borough": "Manhattan",
            "description": "Spacious 3-bedroom perfect for families or roommates. Classic NYC apartment with modern updates and great natural light.",
            "amenities": ["Doorman", "Gym", "Laundry", "Storage", "Near Museums"],
            "images": [
                "https://images.pexels.com/photos/4090093/pexels-photo-4090093.jpeg",
                "https://images.unsplash.com/photo-1551250930-ace1ad395cea"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "leasing@uesplaces.com",
                "broker": "Upper East Realty"
            },
            "available_date": datetime.utcnow() + timedelta(days=28),
            "latitude": 40.7823,
            "longitude": -73.9531,
            "source_url": "https://streeteasy.com/building/200-east-89th-street"
        },
        {
            "title": "Trendy 2BR in SoHo - No Fee",
            "address": "75 Spring St, New York, NY 10012",
            "price": 5800,
            "bedrooms": 2,
            "bathrooms": 1.5,
            "sqft": 950,
            "neighborhood": "SoHo",
            "borough": "Manhattan",
            "description": "Loft-style 2-bedroom in the heart of SoHo. Exposed brick, high ceilings, and steps from the best shopping and dining in NYC.",
            "amenities": ["Loft Style", "High Ceilings", "Exposed Brick", "Shopping District"],
            "images": [
                "https://images.unsplash.com/photo-1553287222-da8a77d59c5c",
                "https://images.unsplash.com/photo-1618861138969-0d7a9d315b1f"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@sohoplaces.com",
                "broker": "SoHo Living NYC"
            },
            "available_date": datetime.utcnow() + timedelta(days=35),
            "latitude": 40.7241,
            "longitude": -74.0027,
            "source_url": "https://streeteasy.com/building/75-spring-street"
        },
        {
            "title": "Affordable 1BR in Astoria - No Fee",
            "address": "25-15 31st Ave, Astoria, NY 11106",
            "price": 2600,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 650,
            "neighborhood": "Astoria",
            "borough": "Queens",
            "description": "Great value 1-bedroom in vibrant Astoria. Easy commute to Manhattan and surrounded by excellent Greek restaurants and cafes.",
            "amenities": ["Laundry", "Storage", "Pet Friendly", "Near Subway"],
            "images": [
                "https://images.unsplash.com/photo-1594295800284-990f74bb6928",
                "https://images.unsplash.com/photo-1568486776380-bf9c4e93347a"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "rentals@astoriaplaces.com",
                "broker": "Queens Affordable Living"
            },
            "available_date": datetime.utcnow() + timedelta(days=12),
            "latitude": 40.7661,
            "longitude": -73.9197,
            "source_url": "https://streeteasy.com/building/25-15-31st-avenue"
        },
        {
            "title": "Waterfront Studio in DUMBO - No Fee",
            "address": "85 Jay St, Brooklyn, NY 11201",
            "price": 3100,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 520,
            "neighborhood": "DUMBO",
            "borough": "Brooklyn",
            "description": "Stunning waterfront studio with Manhattan and bridge views. Located in trendy DUMBO with cobblestone streets and artisanal shops.",
            "amenities": ["Water Views", "Gym", "Rooftop", "Concierge", "Near Bridge"],
            "images": [
                "https://images.pexels.com/photos/4090093/pexels-photo-4090093.jpeg",
                "https://images.unsplash.com/photo-1551250930-ace1ad395cea"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "leasing@dumboplaces.com",
                "broker": "Waterfront Brooklyn Realty"
            },
            "available_date": datetime.utcnow() + timedelta(days=18),
            "latitude": 40.7033,
            "longitude": -73.9886,
            "source_url": "https://streeteasy.com/building/85-jay-street"
        },
        {
            "title": "Classic 2BR in Park Slope - No Fee",
            "address": "145 7th Ave, Brooklyn, NY 11215",
            "price": 4200,
            "bedrooms": 2,
            "bathrooms": 1.0,
            "sqft": 850,
            "neighborhood": "Park Slope",
            "borough": "Brooklyn",
            "description": "Beautiful pre-war 2-bedroom in coveted Park Slope. Near Prospect Park, great schools, and family-friendly neighborhood.",
            "amenities": ["Near Park", "Family Friendly", "Pre-war Charm", "Laundry", "Storage"],
            "images": [
                "https://images.unsplash.com/photo-1553287222-da8a77d59c5c",
                "https://images.unsplash.com/photo-1618861138969-0d7a9d315b1f"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@parkslopeplaces.com",
                "broker": "Park Slope Family Realty"
            },
            "available_date": datetime.utcnow() + timedelta(days=25),
            "latitude": 40.6664,
            "longitude": -73.9814,
            "source_url": "https://streeteasy.com/building/145-7th-avenue"
        }
    ]
    
    for apt_data in mock_apartments:
        apartment = Apartment(**apt_data)
        apartments.append(apartment)
    
    return apartments

async def scrape_rentals():
    """Main scraping function that aggregates from multiple sources"""
    all_apartments = []
    
    # Scrape from different sources
    streeteasy_apartments = await scrape_streeteasy_apartments()
    all_apartments.extend(streeteasy_apartments)
    
    # Store in database
    for apartment in all_apartments:
        existing = await db.apartments.find_one({"address": apartment.address, "price": apartment.price})
        if not existing:
            await db.apartments.insert_one(apartment.dict())
    
    return len(all_apartments)

# API Routes

# Authentication Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and create user
    hashed_password = hash_password(user_data.password)
    user = User(email=user_data.email, full_name=user_data.full_name)
    user_dict = user.dict()
    user_dict['password'] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Create and return token
    access_token = create_access_token(user.id, user.email)
    return Token(access_token=access_token, token_type="bearer")

@api_router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(user['id'], user['email'])
    return Token(access_token=access_token, token_type="bearer")

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Apartment Routes
@api_router.get("/apartments", response_model=List[Apartment])
async def get_apartments(
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    bedrooms: Optional[int] = Query(None),
    neighborhood: Optional[str] = Query(None),
    borough: Optional[str] = Query(None),
    search_term: Optional[str] = Query(None),
    min_sqft: Optional[int] = Query(None),
    max_sqft: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    # Build filter query
    query = {"is_no_fee": True}
    
    if min_price:
        query["price"] = {"$gte": min_price}
    if max_price:
        if "price" in query:
            query["price"]["$lte"] = max_price
        else:
            query["price"] = {"$lte": max_price}
    
    if bedrooms is not None:
        query["bedrooms"] = bedrooms
    
    if neighborhood:
        query["neighborhood"] = {"$regex": neighborhood, "$options": "i"}
    
    if borough:
        query["borough"] = {"$regex": borough, "$options": "i"}
    
    if min_sqft:
        query["sqft"] = {"$gte": min_sqft}
    if max_sqft:
        if "sqft" in query:
            query["sqft"]["$lte"] = max_sqft
        else:
            query["sqft"] = {"$lte": max_sqft}
    
    if search_term:
        query["$or"] = [
            {"title": {"$regex": search_term, "$options": "i"}},
            {"address": {"$regex": search_term, "$options": "i"}},
            {"neighborhood": {"$regex": search_term, "$options": "i"}},
            {"description": {"$regex": search_term, "$options": "i"}}
        ]
    
    # Calculate skip for pagination
    skip = (page - 1) * limit
    
    # Execute query
    apartments_cursor = db.apartments.find(query).skip(skip).limit(limit).sort("created_at", -1)
    apartments = await apartments_cursor.to_list(length=limit)
    
    return [Apartment(**apt) for apt in apartments]

@api_router.get("/apartments/{apartment_id}", response_model=Apartment)
async def get_apartment(apartment_id: str):
    apartment = await db.apartments.find_one({"id": apartment_id})
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return Apartment(**apartment)

@api_router.get("/apartments/search/stats")
async def get_search_stats():
    total_apartments = await db.apartments.count_documents({"is_no_fee": True})
    
    # Get neighborhood stats
    pipeline = [
        {"$match": {"is_no_fee": True}},
        {"$group": {"_id": "$neighborhood", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    neighborhood_stats = await db.apartments.aggregate(pipeline).to_list(10)
    
    # Get price stats
    price_pipeline = [
        {"$match": {"is_no_fee": True}},
        {"$group": {
            "_id": None,
            "avg_price": {"$avg": "$price"},
            "min_price": {"$min": "$price"},
            "max_price": {"$max": "$price"}
        }}
    ]
    price_stats = await db.apartments.aggregate(price_pipeline).to_list(1)
    
    return {
        "total_apartments": total_apartments,
        "top_neighborhoods": neighborhood_stats,
        "price_stats": price_stats[0] if price_stats else {}
    }

# User Favorites Routes
@api_router.post("/users/favorites/{apartment_id}")
async def add_favorite(apartment_id: str, current_user: User = Depends(get_current_user)):
    # Check if apartment exists
    apartment = await db.apartments.find_one({"id": apartment_id})
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    
    # Add to favorites if not already there
    if apartment_id not in current_user.favorite_apartments:
        await db.users.update_one(
            {"id": current_user.id},
            {"$addToSet": {"favorite_apartments": apartment_id}}
        )
    
    return {"message": "Apartment added to favorites"}

@api_router.delete("/users/favorites/{apartment_id}")
async def remove_favorite(apartment_id: str, current_user: User = Depends(get_current_user)):
    await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"favorite_apartments": apartment_id}}
    )
    return {"message": "Apartment removed from favorites"}

@api_router.get("/users/favorites", response_model=List[Apartment])
async def get_favorites(current_user: User = Depends(get_current_user)):
    if not current_user.favorite_apartments:
        return []
    
    apartments_cursor = db.apartments.find({"id": {"$in": current_user.favorite_apartments}})
    apartments = await apartments_cursor.to_list(length=100)
    return [Apartment(**apt) for apt in apartments]

# Saved Searches Routes
@api_router.post("/users/saved-searches", response_model=SavedSearch)
async def create_saved_search(
    search_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    saved_search = SavedSearch(
        user_id=current_user.id,
        name=search_data.get("name", "My Search"),
        filters=SearchFilters(**search_data.get("filters", {})),
        alert_frequency=search_data.get("alert_frequency", "daily")
    )
    
    await db.saved_searches.insert_one(saved_search.dict())
    return saved_search

@api_router.get("/users/saved-searches", response_model=List[SavedSearch])
async def get_saved_searches(current_user: User = Depends(get_current_user)):
    searches_cursor = db.saved_searches.find({"user_id": current_user.id, "is_active": True})
    searches = await searches_cursor.to_list(length=100)
    return [SavedSearch(**search) for search in searches]

@api_router.delete("/users/saved-searches/{search_id}")
async def delete_saved_search(search_id: str, current_user: User = Depends(get_current_user)):
    result = await db.saved_searches.delete_one({"id": search_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Saved search not found")
    return {"message": "Saved search deleted"}

# Scraping Routes
@api_router.post("/admin/scrape")
async def trigger_scraping():
    """Trigger apartment scraping (admin only in production)"""
    count = await scrape_rentals()
    return {"message": f"Scraping completed. Found {count} new apartments."}

# Basic routes
@api_router.get("/")
async def root():
    return {"message": "EasyRent.NYC API - Your no-fee apartment finder"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Include router in main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize database and populate with sample data"""
    logger.info("Starting EasyRent.NYC API...")
    
    # Create indexes for better performance
    await db.apartments.create_index([("neighborhood", 1), ("price", 1)])
    await db.apartments.create_index([("borough", 1)])
    await db.apartments.create_index([("bedrooms", 1)])
    await db.users.create_index([("email", 1)], unique=True)
    
    # Populate with initial data if empty
    apartment_count = await db.apartments.count_documents({})
    if apartment_count == 0:
        await scrape_rentals()
        logger.info("Populated database with initial apartment data")

@app.on_event("shutdown")
async def shutdown_event():
    client.close()
    logger.info("EasyRent.NYC API shutting down...")