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

app = FastAPI(title="NoFeePlaces.com API", version="1.0.0")
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

class Appointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    apartment_id: str
    visitor_name: str
    visitor_email: str
    visitor_phone: str
    appointment_date: datetime
    appointment_time: str  # e.g., "10:00 AM", "2:30 PM"
    duration_minutes: int = 60  # default 1 hour
    status: str = "pending"  # pending, confirmed, completed, cancelled
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AppointmentCreate(BaseModel):
    apartment_id: str
    visitor_name: str
    visitor_email: str
    visitor_phone: str
    appointment_date: str  # YYYY-MM-DD format
    appointment_time: str  # e.g., "10:00 AM"
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

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
                "https://images.unsplash.com/photo-1714153542012-6164546db890?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxOWUMlMjBhcGFydG1lbnQlMjBpbnRlcmlvcnxlbnwwfHx8fDE3NTU2MzQ5NjV8MA&ixlib=rb-4.1.0&q=85",
                "https://images.unsplash.com/photo-1631049307290-bb947b114627"
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
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
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
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
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
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
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
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
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
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
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
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
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
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
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
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
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
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=25),
            "latitude": 40.6664,
            "longitude": -73.9814,
            "source_url": "https://streeteasy.com/building/145-7th-avenue"
        },
        {
            "title": "Luxury Studio at Forty Six Fifty - No Fee",
            "address": "4650 Broadway, New York, NY 10040",
            "price": 3150,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 501,
            "neighborhood": "Hudson Heights",
            "borough": "Manhattan",
            "description": "Brand new luxury studio with 9ft+ ceilings, luxury white oak vinyl flooring, oversized windows, in-home Bosch washer/dryer, and smart keyless entry. Kitchen features GE stainless steel appliances and Calacatta Capri quartz countertops. Bathroom includes custom oak vanity and Kohler fixtures.",
            "amenities": ["Gym", "Rooftop Terrace", "Game Room", "Pet Spa", "Parking", "Doorman", "Package Room", "Basketball Court"],
            "images": [
                "https://images.unsplash.com/photo-1643768664580-d0b82b710837",
                "https://images.unsplash.com/photo-1680503146454-0fe569cef4eb"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=45),
            "latitude": 40.8607,
            "longitude": -73.9218,
            "source_url": "https://www.fortysixfifty.com"
        },
        {
            "title": "Modern 1BR at Forty Six Fifty - No Fee",
            "address": "4650 Broadway, New York, NY 10040", 
            "price": 3695,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 647,
            "neighborhood": "Hudson Heights",
            "borough": "Manhattan",
            "description": "Stunning new 1-bedroom with floor-to-ceiling windows overlooking Fort Tryon Park. Features luxury finishes, in-unit washer/dryer, designer kitchen with quartz countertops, and spa-like bathroom. Smart home technology throughout.",
            "amenities": ["Fort Tryon Park Views", "Gym", "Rooftop Pool", "Co-working Space", "Pet Spa", "Yoga Room", "Parking"],
            "images": [
                "https://images.unsplash.com/photo-1662454419736-de132ff75638",
                "https://images.pexels.com/photos/33479043/pexels-photo-33479043.jpeg"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=60),
            "latitude": 40.8607,
            "longitude": -73.9218,
            "source_url": "https://www.fortysixfifty.com"
        },
        {
            "title": "Spacious 2BR at Forty Six Fifty - No Fee",
            "address": "4650 Broadway, New York, NY 10040",
            "price": 5295,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1103,
            "neighborhood": "Hudson Heights", 
            "borough": "Manhattan",
            "description": "Expansive 2-bedroom, 2-bathroom residence with stunning views of The Cloisters and Hudson River. Features premium white oak flooring, gourmet kitchen with GE appliances, master suite with walk-in closet, and private outdoor space access.",
            "amenities": ["Hudson River Views", "Fitness Center", "Rooftop Terrace", "BBQ Grills", "Children's Playroom", "Concierge", "Storage"],
            "images": [
                "https://images.unsplash.com/photo-1751998816246-c63d182770c0",
                "https://images.unsplash.com/photo-1715985160020-d8cd6fdc8ba9"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=1),
            "latitude": 40.8607,
            "longitude": -73.9218,
            "source_url": "https://www.fortysixfifty.com"
        },
        {
            "title": "Premium 2BR at Forty Six Fifty - No Fee",
            "address": "4650 Broadway, New York, NY 10040",
            "price": 5565,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1103,
            "neighborhood": "Hudson Heights",
            "borough": "Manhattan", 
            "description": "Top-floor premium 2-bedroom with panoramic city and park views. Luxury finishes include Calacatta Capri quartz, custom cabinetry, Bosch appliances, and designer bathroom fixtures. Access to exclusive rooftop amenities.",
            "amenities": ["Panoramic Views", "Rooftop Access", "Fitness Center", "Game Lounge", "Pet Friendly", "Parking", "Smart Home Tech"],
            "images": [
                "https://images.unsplash.com/photo-1638454668466-e8dbd5462f20",
                "https://images.pexels.com/photos/33479111/pexels-photo-33479111.jpeg"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc", 
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=25),
            "latitude": 40.8607,
            "longitude": -73.9218,
            "source_url": "https://www.fortysixfifty.com"
        },
        {
            "title": "Modern Studio at CD 280 - No Fee",
            "address": "280 E 2nd St, New York, NY 10009",
            "price": 2895,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 450,
            "neighborhood": "East Village",
            "borough": "Manhattan",
            "description": "Stylish studio in trendy East Village location. Features modern kitchen with stainless steel appliances, hardwood floors, high ceilings, and large windows for abundant natural light. Walking distance to restaurants, nightlife, and subway stations.",
            "amenities": ["Laundry", "Storage", "Rooftop Access", "Pet Friendly", "Bike Storage"],
            "images": [
                "https://images.unsplash.com/photo-1702014862053-946a122b920d",
                "https://images.unsplash.com/photo-1675279200694-8529c73b1fd0"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=15),
            "latitude": 40.7223,
            "longitude": -73.9874,
            "source_url": "https://manhattanskyline.com"
        },
        {
            "title": "Luxury 1BR at Saranac - No Fee",
            "address": "55 Murray St, New York, NY 10007",
            "price": 4295,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 680,
            "neighborhood": "Tribeca",
            "borough": "Manhattan",
            "description": "Sophisticated 1-bedroom in prestigious Tribeca building. Features floor-to-ceiling windows, granite countertops, stainless steel appliances, hardwood floors, and marble bathroom. Prime downtown location near subway and dining.",
            "amenities": ["Doorman", "Fitness Center", "Roof Deck", "Laundry", "Storage", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1632743441209-8a09b8a37e25",
                "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=40),
            "latitude": 40.7130,
            "longitude": -74.0094,
            "source_url": "https://manhattanskyline.com"
        },
        {
            "title": "Spacious 1BR at The Murray Hill - No Fee",
            "address": "145 E 35th St, New York, NY 10016",
            "price": 3895,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 720,
            "neighborhood": "Murray Hill",
            "borough": "Manhattan",
            "description": "Beautiful 1-bedroom apartment in convenient Murray Hill location. Modern kitchen, oversized windows, hardwood floors, and updated bathroom. Close to Grand Central, restaurants, and shopping. Perfect for professionals.",
            "amenities": ["Elevator", "Laundry", "Storage", "Pet Friendly", "Near Transit"],
            "images": [
                "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92",
                "https://images.unsplash.com/photo-1675279200694-8529c73b1fd0"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=20),
            "latitude": 40.7454,
            "longitude": -73.9778,
            "source_url": "https://manhattanskyline.com"
        },
        {
            "title": "Premium 2BR at Habitat Kips Bay - No Fee",
            "address": "154 E 29th St, New York, NY 10016",
            "price": 6295,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1150,
            "neighborhood": "Kips Bay",
            "borough": "Manhattan",
            "description": "Stunning 2-bedroom, 2-bathroom residence in modern Kips Bay building. Features chef's kitchen with quartz countertops, in-unit washer/dryer, floor-to-ceiling windows, and contemporary finishes throughout. Building offers luxury amenities.",
            "amenities": ["Concierge", "Fitness Center", "Rooftop Terrace", "Laundry In Unit", "Storage", "Pet Spa", "Parking"],
            "images": [
                "https://images.unsplash.com/photo-1675279200694-8529c73b1fd0",
                "https://images.unsplash.com/photo-1632743441209-8a09b8a37e25"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=5),
            "latitude": 40.7442,
            "longitude": -73.9821,
            "source_url": "https://manhattanskyline.com"
        },
        {
            "title": "Luxury 3BR at West Coast - No Fee",
            "address": "95 Horatio St, New York, NY 10014",
            "price": 14895,
            "bedrooms": 3,
            "bathrooms": 3.0,
            "sqft": 1650,
            "neighborhood": "West Village",
            "borough": "Manhattan",
            "description": "Stunning 3-bedroom penthouse in the heart of West Village. Features floor-to-ceiling windows, premium finishes, chef's kitchen with Miele appliances, and private outdoor space. Located in TF Cornerstone's premier building with luxury amenities.",
            "amenities": ["Doorman", "Fitness Center", "Rooftop Terrace", "Pet Friendly", "Storage", "Laundry In Unit", "Concierge"],
            "images": [
                "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c",
                "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=15),
            "latitude": 40.7335,
            "longitude": -74.0083,
            "source_url": "https://tfc.com"
        },
        {
            "title": "Modern 2BR at TFC Hudson Yards - No Fee",
            "address": "606 W 57th St, New York, NY 10019",
            "price": 9200,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1200,
            "neighborhood": "Midtown West",
            "borough": "Manhattan",
            "description": "Contemporary 2-bedroom apartment in Midtown West with stunning city views. Features modern kitchen, in-unit washer/dryer, and premium finishes throughout. Steps from Central Park and world-class dining.",
            "amenities": ["Doorman", "Fitness Center", "Rooftop Deck", "Concierge", "Storage", "Laundry In Unit", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1600607687644-aac4c3eac7f4",
                "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=30),
            "latitude": 40.7675,
            "longitude": -73.9781,
            "source_url": "https://tfc.com"
        },
        {
            "title": "Elegant 2BR at The Fairfax - No Fee",
            "address": "201 E 69th St, New York, NY 10021",
            "price": 8570,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1100,
            "neighborhood": "Upper East Side",
            "borough": "Manhattan",
            "description": "Sophisticated 2-bedroom residence on the prestigious Upper East Side. Features hardwood floors, marble bathrooms, and gourmet kitchen. Located near Central Park, museums, and fine dining establishments.",
            "amenities": ["Doorman", "Fitness Center", "Roof Garden", "Storage", "Laundry", "Pet Friendly"],
            "images": [
                "https://images.pexels.com/photos/9954175/pexels-photo-9954175.jpeg",
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=20),
            "latitude": 40.7682,
            "longitude": -73.9642,
            "source_url": "https://tfc.com"
        },
        {
            "title": "Waterfront 2BR at TFC LIC - No Fee",
            "address": "4720 Center Blvd, Long Island City, NY 11109",
            "price": 7950,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1050,
            "neighborhood": "Long Island City",
            "borough": "Queens",
            "description": "Stunning waterfront 2-bedroom with panoramic Manhattan skyline views. Features floor-to-ceiling windows, modern kitchen with quartz countertops, and access to luxury building amenities. Easy commute to Manhattan.",
            "amenities": ["Concierge", "Fitness Center", "Pool", "Rooftop Terrace", "River Views", "Pet Spa", "Parking"],
            "images": [
                "https://images.unsplash.com/photo-1600607688684-e54e2b60f477",
                "https://images.unsplash.com/photo-1600566753051-6a31aef4f932"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=10),
            "latitude": 40.7505,
            "longitude": -73.9445,
            "source_url": "https://tfc.com"
        },
        {
            "title": "Premium 2BR at TFC Center Blvd - No Fee",
            "address": "4610 Center Blvd, Long Island City, NY 11109",
            "price": 7925,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1075,
            "neighborhood": "Long Island City",
            "borough": "Queens",
            "description": "Luxury 2-bedroom residence with East River views and premium finishes. Features chef's kitchen, spa-like bathrooms, and in-unit washer/dryer. Building offers world-class amenities and waterfront lifestyle.",
            "amenities": ["Doorman", "Fitness Center", "Pool", "Rooftop Deck", "Concierge", "Storage", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1600607688893-c3d94ae24c1b",
                "https://images.unsplash.com/photo-1600566753237-740dd14c6023"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=25),
            "latitude": 40.7511,
            "longitude": -73.9441,
            "source_url": "https://tfc.com"
        },
        {
            "title": "Modern 2BR at TFC 5203 Center Blvd - No Fee",
            "address": "5203 Center Blvd, Long Island City, NY 11109",
            "price": 7545,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1025,
            "neighborhood": "Long Island City",
            "borough": "Queens",
            "description": "Contemporary 2-bedroom apartment with stunning city and water views. Features modern appliances, hardwood floors, and floor-to-ceiling windows. Located in TF Cornerstone's premier LIC building with exceptional amenities.",
            "amenities": ["Concierge", "Fitness Center", "Rooftop Pool", "BBQ Area", "Storage", "Pet Spa", "Parking"],
            "images": [
                "https://images.unsplash.com/photo-1600607688622-25782b8df980",
                "https://images.unsplash.com/photo-1600566752842-d2697d8db9e8"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=35),
            "latitude": 40.7518,
            "longitude": -73.9438,
            "source_url": "https://tfc.com"
        },
        {
            "title": "Luxury Studio at TFC Chelsea - No Fee",
            "address": "200 W 26th St, New York, NY 10001",
            "price": 4895,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 650,
            "neighborhood": "Chelsea",
            "borough": "Manhattan",
            "description": "Sophisticated studio in vibrant Chelsea neighborhood. Features high ceilings, modern kitchen with granite countertops, and premium finishes. Walking distance to High Line, Madison Square Garden, and excellent restaurants.",
            "amenities": ["Doorman", "Fitness Center", "Rooftop Terrace", "Storage", "Laundry", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1600607688458-9d4d34394d80",
                "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=5),
            "latitude": 40.7441,
            "longitude": -73.9928,
            "source_url": "https://tfc.com"
        },
        {
            "title": "Spacious 1BR at TFC Murray Hill - No Fee",
            "address": "340 E 34th St, New York, NY 10016",
            "price": 5295,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 750,
            "neighborhood": "Murray Hill",
            "borough": "Manhattan",
            "description": "Bright 1-bedroom apartment in convenient Murray Hill location. Features oversized windows, modern kitchen, hardwood floors, and updated bathroom. Close to Grand Central, restaurants, and shopping.",
            "amenities": ["Doorman", "Fitness Center", "Laundry", "Storage", "Pet Friendly", "Roof Deck"],
            "images": [
                "https://images.unsplash.com/photo-1600607688315-695c2369c847",
                "https://images.unsplash.com/photo-1600566752734-d5c717b5ff83"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=12),
            "latitude": 40.7454,
            "longitude": -73.9778,
            "source_url": "https://tfc.com"
        },
        {
            "title": "Premium Studio at TFC LIC Towers - No Fee",
            "address": "4540 Center Blvd, Long Island City, NY 11109",
            "price": 3895,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 525,
            "neighborhood": "Long Island City",
            "borough": "Queens",
            "description": "Modern studio with stunning Manhattan skyline views. Features efficient layout, premium finishes, stainless steel appliances, and floor-to-ceiling windows. Located in luxury building with resort-style amenities.",
            "amenities": ["Concierge", "Fitness Center", "Pool", "Rooftop Terrace", "Storage", "Pet Spa", "Parking"],
            "images": [
                "https://images.unsplash.com/photo-1600607688201-e90e0a60c5b7",
                "https://images.unsplash.com/photo-1600566752734-d5c717b5ff83"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=18),
            "latitude": 40.7502,
            "longitude": -73.9447,
            "source_url": "https://tfc.com"
        },
        {
            "title": "Elegant 2BR at TFC Prospect Heights - No Fee",
            "address": "595 Dean St, Brooklyn, NY 11238",
            "price": 6295,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1150,
            "neighborhood": "Prospect Heights",
            "borough": "Brooklyn",
            "description": "Beautiful 2-bedroom apartment in trendy Prospect Heights. Features modern kitchen with stainless steel appliances, hardwood floors, and large windows. Near Prospect Park, Barclays Center, and excellent dining options.",
            "amenities": ["Doorman", "Fitness Center", "Rooftop Garden", "Storage", "Laundry", "Pet Friendly", "Bike Storage"],
            "images": [
                "https://images.unsplash.com/photo-1600607688067-1c78f2c6ef86",
                "https://images.unsplash.com/photo-1600566752355-35792bedcfea"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "info@places.nyc",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=40),
            "latitude": 40.6823,
            "longitude": -73.9682,
            "source_url": "https://tfc.com"
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

# Appointment Routes
@api_router.post("/appointments", response_model=Appointment)
async def create_appointment(appointment_data: AppointmentCreate):
    # Check if apartment exists
    apartment = await db.apartments.find_one({"id": appointment_data.apartment_id})
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    
    # Parse the appointment date and time
    try:
        appointment_datetime = datetime.strptime(
            f"{appointment_data.appointment_date} {appointment_data.appointment_time}",
            "%Y-%m-%d %I:%M %p"
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date or time format")
    
    # Check if the time slot is available (10 AM to 7 PM)
    hour = appointment_datetime.hour
    if hour < 10 or hour >= 19:
        raise HTTPException(status_code=400, detail="Appointments are only available between 10 AM and 7 PM")
    
    # Check for conflicts (same apartment, same date/time)
    existing = await db.appointments.find_one({
        "apartment_id": appointment_data.apartment_id,
        "appointment_date": appointment_datetime,
        "status": {"$in": ["pending", "confirmed"]}
    })
    
    if existing:
        raise HTTPException(status_code=409, detail="Time slot is already booked")
    
    # Create appointment
    appointment = Appointment(
        apartment_id=appointment_data.apartment_id,
        visitor_name=appointment_data.visitor_name,
        visitor_email=appointment_data.visitor_email,
        visitor_phone=appointment_data.visitor_phone,
        appointment_date=appointment_datetime,
        appointment_time=appointment_data.appointment_time,
        notes=appointment_data.notes
    )
    
    await db.appointments.insert_one(appointment.dict())
    return appointment

@api_router.get("/appointments", response_model=List[Appointment])
async def get_appointments(
    apartment_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    # Build filter query
    query = {}
    
    if apartment_id:
        query["apartment_id"] = apartment_id
    
    if status:
        query["status"] = status
    
    if date_from or date_to:
        date_filter = {}
        if date_from:
            date_filter["$gte"] = datetime.strptime(date_from, "%Y-%m-%d")
        if date_to:
            date_filter["$lte"] = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
        query["appointment_date"] = date_filter
    
    # Calculate skip for pagination
    skip = (page - 1) * limit
    
    # Execute query
    appointments_cursor = db.appointments.find(query).skip(skip).limit(limit).sort("appointment_date", 1)
    appointments = await appointments_cursor.to_list(length=limit)
    
    return [Appointment(**apt) for apt in appointments]

@api_router.get("/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str):
    appointment = await db.appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return Appointment(**appointment)

@api_router.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: str, update_data: AppointmentUpdate):
    appointment = await db.appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Prepare update fields
    update_fields = {"updated_at": datetime.utcnow()}
    
    if update_data.status:
        if update_data.status not in ["pending", "confirmed", "completed", "cancelled"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        update_fields["status"] = update_data.status
    
    if update_data.notes is not None:
        update_fields["notes"] = update_data.notes
    
    # Update appointment
    await db.appointments.update_one(
        {"id": appointment_id},
        {"$set": update_fields}
    )
    
    # Return updated appointment
    updated_appointment = await db.appointments.find_one({"id": appointment_id})
    return Appointment(**updated_appointment)

@api_router.delete("/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: str):
    result = await db.appointments.update_one(
        {"id": appointment_id},
        {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {"message": "Appointment cancelled successfully"}

@api_router.get("/apartments/{apartment_id}/available-slots")
async def get_available_slots(
    apartment_id: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format")
):
    # Check if apartment exists
    apartment = await db.apartments.find_one({"id": apartment_id})
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Don't allow booking in the past
    if target_date.date() < datetime.now().date():
        return {"available_slots": []}
    
    # Get existing appointments for this apartment and date
    existing_appointments = await db.appointments.find({
        "apartment_id": apartment_id,
        "appointment_date": {
            "$gte": target_date,
            "$lt": target_date + timedelta(days=1)
        },
        "status": {"$in": ["pending", "confirmed"]}
    }).to_list(length=100)
    
    # Generate time slots from 10 AM to 7 PM (every hour)
    all_slots = []
    for hour in range(10, 19):  # 10 AM to 6 PM (last slot)
        time_str = f"{hour % 12 if hour % 12 != 0 else 12}:00 {'PM' if hour >= 12 else 'AM'}"
        all_slots.append(time_str)
    
    # Remove booked slots
    booked_times = set()
    for appointment in existing_appointments:
        booked_times.add(appointment["appointment_time"])
    
    available_slots = [slot for slot in all_slots if slot not in booked_times]
    
    return {"available_slots": available_slots}
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
    return {"message": "NoFeePlaces.com API - Your no-fee apartment finder"}

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
    logger.info("Starting NoFeePlaces.com API...")
    
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
    logger.info("NoFeePlaces.com API shutting down...")