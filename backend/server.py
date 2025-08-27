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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from icalendar import Calendar, Event
import pytz
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

# Email Configuration
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USER = os.environ.get('EMAIL_USER', 'placesnyc88@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'

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

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    message: str
    response: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    apartment_context: Optional[str] = None

class ContactRequest(BaseModel):
    apartment_id: str
    apartment_title: str
    apartment_address: str
    apartment_price: int
    name: str
    email: str
    phone: str
    message: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    apartment_id: Optional[str] = None
    context: Optional[str] = None

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
async def scrape_relatedrentals_apartments():
    """Scrape Related Rentals for no-fee luxury apartments in NYC"""
    apartments = []
    
    # Related Rentals apartments in the $3,800-$5,400 range
    related_apartments = [
        {
            "title": "Luxury Studio at The Tate Chelsea - No Fee",
            "address": "535 W 23rd St, New York, NY 10011",
            "price": 4495,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 580,
            "neighborhood": "Chelsea",
            "borough": "Manhattan",
            "description": "Stunning studio featuring walk-in closet, in-home washer/dryer, upgraded strip wood floors, solar shades, and northern exposure. Located in the heart of Chelsea near High Line and Hudson River Park.",
            "amenities": ["Doorman", "Fitness Center", "Roof Garden", "Laundry In Unit", "Storage", "Pet Friendly", "Concierge"],
            "images": [
                "https://images.unsplash.com/photo-1631049307290-bb947b114627?crop=entropy&cs=srgb&fm=jpg&q=80",
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e?crop=entropy&cs=srgb&fm=jpg&q=80"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=5),
            "latitude": 40.7456,
            "longitude": -74.0072,
            "source_url": "https://relatedrentals.com"
        },
        {
            "title": "Oversized Alcove Studio at Abington House - No Fee",
            "address": "515 W 29th St, New York, NY 10001",
            "price": 4495,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 650,
            "neighborhood": "Hudson Yards",
            "borough": "Manhattan",
            "description": "Oversized alcove studio with high ceilings, floor-to-ceiling windows, and western exposure with views of the High Line. Premium luxury building with world-class amenities.",
            "amenities": ["High Line Views", "Floor-to-Ceiling Windows", "Fitness Center", "Rooftop Terrace", "Concierge", "Pet Spa", "Storage"],
            "images": [
                "https://images.unsplash.com/photo-1632119580908-ae947d4c7691?crop=entropy&cs=srgb&fm=jpg&q=80",
                "https://images.unsplash.com/photo-1714153542012-6164546db890?crop=entropy&cs=srgb&fm=jpg&q=80"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=12),
            "latitude": 40.7505,
            "longitude": -74.0014,
            "source_url": "https://relatedrentals.com"
        },
        {
            "title": "Spacious 1BR at The Westport Midtown - No Fee",
            "address": "500 W 43rd St, New York, NY 10036",
            "price": 4650,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 720,
            "neighborhood": "Midtown West",
            "borough": "Manhattan",
            "description": "Bright 1-bedroom with eastern exposure, customized walk-in closet, and gourmet kitchen. Located in prime Midtown location near Times Square and Hell's Kitchen dining scene.",
            "amenities": ["Gourmet Kitchen", "Walk-in Closet", "Doorman", "Fitness Center", "Rooftop Deck", "Storage", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec?crop=entropy&cs=srgb&fm=jpg&q=80",
                "https://images.pexels.com/photos/6970025/pexels-photo-6970025.jpeg?auto=compress&cs=srgb&dpr=1&w=500"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=18),
            "latitude": 40.7580,
            "longitude": -73.9855,
            "source_url": "https://relatedrentals.com"
        },
        {
            "title": "Premium 1BR at Riverwalk Heights Roosevelt Island - No Fee",
            "address": "405 Main St, Roosevelt Island, NY 10044",
            "price": 4400,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 750,
            "neighborhood": "Roosevelt Island",
            "borough": "Manhattan",
            "description": "Elegant 1-bedroom with southern exposure, open kitchen with custom natural oak cabinetry, quartz countertops, Italian Statuary Marble tile backsplashes, and top-tier Fisher Paykel appliances.",
            "amenities": ["Quartz Countertops", "Italian Marble", "Fisher Paykel Appliances", "Waterfront Views", "Fitness Center", "Pool", "Pet Friendly"],
            "images": [
                "https://images.pexels.com/photos/9954175/pexels-photo-9954175.jpeg?auto=compress&cs=srgb&dpr=1&w=500",
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec?crop=entropy&cs=srgb&fm=jpg&q=80"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=25),
            "latitude": 40.7614,
            "longitude": -73.9508,
            "source_url": "https://relatedrentals.com"
        },
        {
            "title": "Luxury 1BR at Hudson Point - No Fee",
            "address": "625 W 42nd St, New York, NY 10036",
            "price": 5200,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 800,
            "neighborhood": "Hell's Kitchen",
            "borough": "Manhattan",
            "description": "Sophisticated 1-bedroom with Hudson River views, premium finishes, and chef's kitchen. Located in Related's flagship building with resort-style amenities.",
            "amenities": ["Hudson River Views", "Chef's Kitchen", "Doorman", "Pool", "Spa", "Fitness Center", "Concierge", "Pet Spa"],
            "images": [
                "https://images.unsplash.com/photo-1714153542012-6164546db890?crop=entropy&cs=srgb&fm=jpg&q=80",
                "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?crop=entropy&cs=srgb&fm=jpg&q=80"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=8),
            "latitude": 40.7589,
            "longitude": -73.9925,
            "source_url": "https://relatedrentals.com"
        },
        {
            "title": "Modern 1BR at West Side - No Fee",
            "address": "1865 Broadway, New York, NY 10023",
            "price": 5100,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 780,
            "neighborhood": "Lincoln Square",
            "borough": "Manhattan",
            "description": "Contemporary 1-bedroom near Lincoln Center with oversized windows, hardwood floors, and modern kitchen. Walking distance to Central Park and world-class cultural venues.",
            "amenities": ["Lincoln Center Proximity", "Hardwood Floors", "Modern Kitchen", "Doorman", "Fitness Center", "Roof Garden", "Storage"],
            "images": [
                "https://images.unsplash.com/photo-1632119580908-ae947d4c7691?crop=entropy&cs=srgb&fm=jpg&q=80",
                "https://images.pexels.com/photos/6970025/pexels-photo-6970025.jpeg?auto=compress&cs=srgb&dpr=1&w=500"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=15),
            "latitude": 40.7736,
            "longitude": -73.9834,
            "source_url": "https://relatedrentals.com"
        },
        {
            "title": "Elegant 1BR at Tribeca Park - No Fee",
            "address": "225 Rector Pl, New York, NY 10280",
            "price": 5300,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 820,
            "neighborhood": "Tribeca",
            "borough": "Manhattan",
            "description": "Sophisticated 1-bedroom in prestigious Tribeca with marble bathrooms, chef's kitchen, and river views. Premium building with luxury amenities and concierge services.",
            "amenities": ["River Views", "Marble Bathrooms", "Chef's Kitchen", "Concierge", "Pool", "Spa", "Fitness Center", "Pet Friendly"],
            "images": [
                "https://images.pexels.com/photos/9954175/pexels-photo-9954175.jpeg?auto=compress&cs=srgb&dpr=1&w=500",
                "https://images.unsplash.com/photo-1600607688893-c3d94ae24c1b?crop=entropy&cs=srgb&fm=jpg&q=80"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=22),
            "latitude": 40.7137,
            "longitude": -74.0164,
            "source_url": "https://relatedrentals.com"
        },
        {
            "title": "Luxury Studio at Chelsea Point - No Fee",
            "address": "515 W 18th St, New York, NY 10011",
            "price": 3950,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 550,
            "neighborhood": "Chelsea",
            "borough": "Manhattan",
            "description": "Designer studio in trendy Chelsea with high ceilings, premium appliances, and custom finishes. Steps from Chelsea Market, Meatpacking District, and High Line park.",
            "amenities": ["High Ceilings", "Premium Appliances", "Designer Finishes", "Doorman", "Fitness Center", "Roof Deck", "Storage"],
            "images": [
                "https://images.unsplash.com/photo-1631049307290-bb947b114627?crop=entropy&cs=srgb&fm=jpg&q=80",
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e?crop=entropy&cs=srgb&fm=jpg&q=80"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=10),
            "latitude": 40.7435,
            "longitude": -74.0067,
            "source_url": "https://relatedrentals.com"
        },
        {
            "title": "Premium 1BR at Columbus Circle - No Fee",
            "address": "200 W 60th St, New York, NY 10023",
            "price": 5350,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 850,
            "neighborhood": "Columbus Circle",
            "borough": "Manhattan",
            "description": "Luxurious 1-bedroom with Central Park views, floor-to-ceiling windows, and premium finishes. Located directly on Columbus Circle with unparalleled access to Manhattan's best.",
            "amenities": ["Central Park Views", "Floor-to-Ceiling Windows", "Premium Finishes", "Doorman", "Concierge", "Spa", "Pool", "Storage"],
            "images": [
                "https://images.unsplash.com/photo-1600607688067-1c78f2c6ef86?crop=entropy&cs=srgb&fm=jpg&q=80",
                "https://images.unsplash.com/photo-1714153542012-6164546db890?crop=entropy&cs=srgb&fm=jpg&q=80"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=30),
            "latitude": 40.7677,
            "longitude": -73.9820,
            "source_url": "https://relatedrentals.com"
        },
        {
            "title": "Sophisticated 1BR at Greenwich Village - No Fee",
            "address": "85 4th Ave, New York, NY 10003",
            "price": 4850,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 760,
            "neighborhood": "Greenwich Village",
            "borough": "Manhattan",
            "description": "Charming 1-bedroom in historic Greenwich Village with exposed brick, hardwood floors, and modern amenities. Walking distance to Washington Square Park and NYU campus.",
            "amenities": ["Exposed Brick", "Hardwood Floors", "Modern Amenities", "Doorman", "Fitness Center", "Laundry", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec?crop=entropy&cs=srgb&fm=jpg&q=80",
                "https://images.unsplash.com/photo-1632119580908-ae947d4c7691?crop=entropy&cs=srgb&fm=jpg&q=80"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=20),
            "latitude": 40.7305,
            "longitude": -73.9910,
            "source_url": "https://relatedrentals.com"
        }
    ]
    
    # Convert to Apartment objects
    for apt_data in related_apartments:
        apartment = Apartment(**apt_data)
        apartments.append(apartment)
    
    return apartments

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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com", 
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
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
                "https://images.unsplash.com/photo-1631049307290-bb947b114627",
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
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
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec",
                "https://images.pexels.com/photos/6970025/pexels-photo-6970025.jpeg"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
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
                "https://images.unsplash.com/photo-1632119580908-ae947d4c7691",
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
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
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=40),
            "latitude": 40.6823,
            "longitude": -73.9682,
            "source_url": "https://tfc.com"
        },
        {
            "title": "Luxury 1BR at The Orchard LIC - No Fee",
            "address": "2748 Jackson Ave, Long Island City, NY 11101",
            "price": 4695,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 720,
            "neighborhood": "Long Island City",
            "borough": "Queens",
            "description": "Modern 1-bedroom at the prestigious Orchard tower. Floor-to-ceiling windows with Manhattan skyline views. Premium amenities including pool, fitness center, and rooftop terrace. Direct leasing office.",
            "amenities": ["Concierge", "Pool", "Fitness Center", "Rooftop Terrace", "Dog Park", "Game Room", "Basketball Court", "Theater"],
            "images": [
                "https://images.unsplash.com/photo-1714153542012-6164546db890",
                "https://images.unsplash.com/photo-1632119580908-ae947d4c7691"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=14),
            "latitude": 40.7505,
            "longitude": -73.9320,
            "source_url": "https://theorchardlic.com"
        },
        {
            "title": "Spacious 2BR at SoMa Financial District - No Fee",
            "address": "25 Water St, New York, NY 10004",
            "price": 7295,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1250,
            "neighborhood": "Financial District",
            "borough": "Manhattan",
            "description": "Stunning 2-bedroom in NYC's largest office-to-residential conversion. Features premium finishes, spa-like amenities, and convenient FiDi location. Leasing office on-site with owner-paid commission.",
            "amenities": ["Spa", "Sauna", "Indoor Pool", "Outdoor Pool", "Fitness Center", "Game Lounge", "Atrium", "Storage"],
            "images": [
                "https://images.pexels.com/photos/9954175/pexels-photo-9954175.jpeg",
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=21),
            "latitude": 40.7047,
            "longitude": -74.0089,
            "source_url": "https://25waterstreet.com"
        },
        {
            "title": "Modern Studio at The Bold LIC - No Fee",
            "address": "2701 Jackson Ave, Long Island City, NY 11101",
            "price": 3495,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 520,
            "neighborhood": "Long Island City",
            "borough": "Queens",
            "description": "Contemporary studio in The Bold with climbing wall gym and golf simulator. Brand new building with direct leasing office. Owner pays all commissions. Perfect for young professionals.",
            "amenities": ["Climbing Wall", "Golf Simulator", "Coworking Lounge", "Party Room", "Media Room", "Clubhouse", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1631049307290-bb947b114627",
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=8),
            "latitude": 40.7511,
            "longitude": -73.9315,
            "source_url": "https://theboldlic.com"
        },
        {
            "title": "Premium 3BR at Alloy Block Brooklyn - No Fee",
            "address": "505 State St, Brooklyn, NY 11217",
            "price": 12895,
            "bedrooms": 3,
            "bathrooms": 2.5,
            "sqft": 1650,
            "neighborhood": "Boerum Hill",
            "borough": "Brooklyn",
            "description": "Luxury 3-bedroom in NYC's first all-electric skyscraper. Features roof terrace with swimming pool, yoga room, and screening room. Direct leasing office with owner-paid commissions.",
            "amenities": ["Swimming Pool", "Roof Terrace", "Yoga Room", "Screening Room", "Children's Playroom", "Fitness Center", "Lounge"],
            "images": [
                "https://images.pexels.com/photos/9954175/pexels-photo-9954175.jpeg",
                "https://images.unsplash.com/photo-1600607688969-a5bfcd646154"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=35),
            "latitude": 40.6890,
            "longitude": -73.9758,
            "source_url": "https://alloyblock.com"
        },
        {
            "title": "Sophisticated 1BR at Sven LIC - No Fee",
            "address": "29-59 Northern Blvd, Long Island City, NY 11101",
            "price": 4295,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 680,
            "neighborhood": "Long Island City",
            "borough": "Queens",
            "description": "Designer 1-bedroom at Sven tower with East River views. Features private library, co-working space, and children's playroom. Direct leasing with owner-paid commission structure.",
            "amenities": ["Outdoor Pool", "Private Library", "Co-working Space", "Children's Playroom", "Fitness Center", "Concierge", "Storage"],
            "images": [
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec",
                "https://images.pexels.com/photos/6970025/pexels-photo-6970025.jpeg"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=16),
            "latitude": 40.7525,
            "longitude": -73.9291,
            "source_url": "https://svenlic.com"
        },
        {
            "title": "Elegant 2BR at Essex Crossing LES - No Fee",
            "address": "145 Clinton St, New York, NY 10002",
            "price": 8195,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1180,
            "neighborhood": "Lower East Side",
            "borough": "Manhattan",
            "description": "Beautiful 2-bedroom in the vibrant Essex Crossing development. Walking distance to food hall, cinema, and museum. On-site leasing office with owner-paid commission policy.",
            "amenities": ["Rooftop Terrace", "Fitness Center", "Lounge", "Storage", "Bike Storage", "Pet Friendly", "Doorman"],
            "images": [
                "https://images.unsplash.com/photo-1714153542012-6164546db890",
                "https://images.unsplash.com/photo-1632119580908-ae947d4c7691"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=28),
            "latitude": 40.7184,
            "longitude": -73.9857,
            "source_url": "https://essexcrossing.com"
        },
        {
            "title": "Luxury Studio at One Manhattan Square - No Fee",
            "address": "252 South St, New York, NY 10002",
            "price": 5495,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 610,
            "neighborhood": "Two Bridges",
            "borough": "Manhattan",
            "description": "Exquisite studio at the prestigious One Manhattan Square. Features world-class amenities including spa, multiple pools, and panoramic city views. Direct leasing office available.",
            "amenities": ["Spa", "Multiple Pools", "Tennis Court", "Golf Simulator", "Rock Climbing Wall", "Bowling Alley", "Movie Theater", "Concierge"],
            "images": [
                "https://images.pexels.com/photos/9954175/pexels-photo-9954175.jpeg",
                "https://images.unsplash.com/photo-1631049307290-bb947b114627"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=19),
            "latitude": 40.7103,
            "longitude": -73.9969,
            "source_url": "https://onemanhattansquare.com"
        },
        {
            "title": "Modern 1BR at 520 Fifth Avenue - No Fee",
            "address": "520 Fifth Ave, New York, NY 10036",
            "price": 6895,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 750,
            "neighborhood": "Midtown",
            "borough": "Manhattan",
            "description": "Sophisticated 1-bedroom in the iconic 520 Fifth Avenue supertall. Premium finishes with Central Park proximity. Leasing office handles all rentals with owner-paid commissions.",
            "amenities": ["Doorman", "Fitness Center", "Rooftop Terrace", "Storage", "Concierge", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec",
                "https://images.unsplash.com/photo-1714153542012-6164546db890"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=42),
            "latitude": 40.7527,
            "longitude": -73.9772,
            "source_url": "https://520fifthavenue.com"
        },
        {
            "title": "Spacious 2BR at 262 Fifth Avenue - No Fee",
            "address": "262 Fifth Ave, New York, NY 10001",
            "price": 9595,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1320,
            "neighborhood": "NoMad",
            "borough": "Manhattan",
            "description": "Luxury 2-bedroom in the prestigious 262 Fifth Avenue with Madison Square Park views. Premium amenities and finishes throughout. Direct leasing with owner-paid broker fees.",
            "amenities": ["Doorman", "Fitness Center", "Roof Deck", "Storage", "Laundry", "Pet Friendly", "Concierge"],
            "images": [
                "https://images.pexels.com/photos/9954175/pexels-photo-9954175.jpeg",
                "https://images.unsplash.com/photo-1632119580908-ae947d4c7691"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=33),
            "latitude": 40.7447,
            "longitude": -73.9883,
            "source_url": "https://262fifthavenue.com"
        },
        {
            "title": "Premium 1BR at 55 Broad Street - No Fee",
            "address": "55 Broad St, New York, NY 10004",
            "price": 5895,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 780,
            "neighborhood": "Financial District",
            "borough": "Manhattan",
            "description": "Contemporary 1-bedroom in converted office building in FiDi. Features modern amenities and convenient location near South Street Seaport. On-site leasing office.",
            "amenities": ["Fitness Center", "Lounge", "Rooftop Terrace", "Storage", "Laundry", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1714153542012-6164546db890",
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=26),
            "latitude": 40.7056,
            "longitude": -74.0097,
            "source_url": "https://55broadstreet.com"
        },
        {
            "title": "Luxury Studio at 10 Nevins Brooklyn - No Fee",
            "address": "10 Nevins St, Brooklyn, NY 11217",
            "price": 4195,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 580,
            "neighborhood": "Fort Greene",
            "borough": "Brooklyn",
            "description": "Designer studio at 10 Nevins with premium finishes and Brooklyn Bridge views. Features rooftop terrace and fitness center. Direct leasing office with no broker fees.",
            "amenities": ["Rooftop Terrace", "Fitness Center", "Doorman", "Storage", "Laundry", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1631049307290-bb947b114627",
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=11),
            "latitude": 40.6895,
            "longitude": -73.9808,
            "source_url": "https://10nevins.com"
        },
        {
            "title": "Modern 2BR at The Harrison LIC - No Fee",
            "address": "26-26 Jackson Ave, Long Island City, NY 11101",
            "price": 6795,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1100,
            "neighborhood": "Long Island City",
            "borough": "Queens",
            "description": "Contemporary 2-bedroom at The Harrison with Manhattan skyline views. Features premium amenities and waterfront location. Leasing office on-site with owner-paid commissions.",
            "amenities": ["Waterfront", "Fitness Center", "Rooftop Deck", "Concierge", "Storage", "Pet Spa", "Parking"],
            "images": [
                "https://images.pexels.com/photos/9954175/pexels-photo-9954175.jpeg",
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=38),
            "latitude": 40.7501,
            "longitude": -73.9445,
            "source_url": "https://theharrisonlic.com"
        },
        {
            "title": "Elegant 1BR at Brooklyn Point - No Fee",
            "address": "138 Willoughby St, Brooklyn, NY 11201",
            "price": 5595,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 720,
            "neighborhood": "Downtown Brooklyn",
            "borough": "Brooklyn",
            "description": "Sophisticated 1-bedroom at Brooklyn Point with Manhattan views. Features infinity pool, spa, and premium amenities. Direct leasing office with owner-paid broker fees.",
            "amenities": ["Infinity Pool", "Spa", "Fitness Center", "Rooftop Garden", "Doorman", "Storage", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1714153542012-6164546db890",
                "https://images.unsplash.com/photo-1632119580908-ae947d4c7691"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=24),
            "latitude": 40.6934,
            "longitude": -73.9857,
            "source_url": "https://brooklynpoint.com"
        },
        {
            "title": "Premium Studio at The Dime Brooklyn - No Fee",
            "address": "85 Flatbush Ave, Brooklyn, NY 11217",
            "price": 3795,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 490,
            "neighborhood": "Downtown Brooklyn",
            "borough": "Brooklyn",
            "description": "Chic studio at The Dime with industrial design and modern amenities. Features rooftop terrace and fitness center. On-site leasing office handles all rentals directly.",
            "amenities": ["Rooftop Terrace", "Fitness Center", "Lounge", "Storage", "Laundry", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1631049307290-bb947b114627",
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=9),
            "latitude": 40.6914,
            "longitude": -73.9826,
            "source_url": "https://thedimebrooklyn.com"
        },
        {
            "title": "Modern Studio at Astoria Cove Queens - No Fee",
            "address": "21-10 45th Ave, Astoria, NY 11105", 
            "price": 3295,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 520,
            "neighborhood": "Astoria",
            "borough": "Queens",
            "description": "Contemporary studio in vibrant Astoria with Manhattan skyline views. Features modern kitchen, high ceilings, and access to building amenities. Leasing office on-site with owner-paid commissions.",
            "amenities": ["Fitness Center", "Rooftop Deck", "Doorman", "Storage", "Laundry", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1631049307290-bb947b114627",
                "https://images.unsplash.com/photo-1632119580908-ae947d4c7691"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com", 
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=12),
            "latitude": 40.7589,
            "longitude": -73.9442,
            "source_url": "https://astoriacove.com"
        },
        {
            "title": "Spacious Studio at Williamsburg Edge - No Fee",
            "address": "22 N 6th St, Brooklyn, NY 11249",
            "price": 3595,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 580,
            "neighborhood": "Williamsburg", 
            "borough": "Brooklyn",
            "description": "Designer studio in trendy Williamsburg with exposed brick and modern finishes. Walking distance to Manhattan Bridge and vibrant nightlife. Direct leasing office with no broker fees.",
            "amenities": ["Rooftop Terrace", "Fitness Center", "Storage", "Laundry", "Pet Friendly", "Bike Storage"],
            "images": [
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e",
                "https://images.unsplash.com/photo-1631049307290-bb947b114627"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=18),
            "latitude": 40.7130,
            "longitude": -73.9618,
            "source_url": "https://williamsburgedge.com"
        },
        {
            "title": "Cozy 1BR at Forest Hills Gardens - No Fee",
            "address": "112-20 72nd Dr, Forest Hills, NY 11375",
            "price": 3395,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 650,
            "neighborhood": "Forest Hills",
            "borough": "Queens",
            "description": "Charming 1-bedroom in prestigious Forest Hills Gardens. Features hardwood floors, updated kitchen, and garden views. Quiet residential setting with easy Manhattan access.",
            "amenities": ["Garden", "Doorman", "Storage", "Laundry", "Pet Friendly", "Parking"],
            "images": [
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec",
                "https://images.pexels.com/photos/6970025/pexels-photo-6970025.jpeg"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=25),
            "latitude": 40.7187,
            "longitude": -73.8448,
            "source_url": "https://foresthillsgardens.com"
        },
        {
            "title": "Bright Studio at Greenpoint Loft - No Fee",
            "address": "67 West St, Brooklyn, NY 11222",
            "price": 3695,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 550,
            "neighborhood": "Greenpoint",
            "borough": "Brooklyn", 
            "description": "Industrial-style studio in artistic Greenpoint with high ceilings and large windows. Near waterfront parks and trendy cafes. Leasing office offers owner-paid commission structure.",
            "amenities": ["High Ceilings", "Fitness Center", "Rooftop Access", "Storage", "Laundry", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1631049307290-bb947b114627",
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=15),
            "latitude": 40.7309,
            "longitude": -73.9537,
            "source_url": "https://greenpointloft.com"
        },
        {
            "title": "Modern 1BR at Sunnyside Plaza - No Fee",
            "address": "43-10 Queens Blvd, Sunnyside, NY 11104",
            "price": 3495,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 680,
            "neighborhood": "Sunnyside",
            "borough": "Queens",
            "description": "Updated 1-bedroom in convenient Sunnyside location. Features modern appliances, hardwood floors, and great natural light. Easy subway access to Manhattan with direct leasing office.",
            "amenities": ["Doorman", "Fitness Center", "Storage", "Laundry", "Pet Friendly", "Parking"],
            "images": [
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec",
                "https://images.unsplash.com/photo-1714153542012-6164546db890"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=22),
            "latitude": 40.7506,
            "longitude": -73.9219,
            "source_url": "https://sunnysideplaza.com"
        },
        {
            "title": "Stylish Studio at Bed-Stuy Lofts - No Fee",
            "address": "455 Marcus Garvey Blvd, Brooklyn, NY 11216",
            "price": 3795,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 500,
            "neighborhood": "Bedford-Stuyvesant",
            "borough": "Brooklyn",
            "description": "Hip studio in trendy Bed-Stuy with exposed brick walls and modern amenities. Great neighborhood restaurants and nightlife. Building managed directly by owner with no broker fees.",
            "amenities": ["Exposed Brick", "Fitness Center", "Rooftop Deck", "Storage", "Laundry", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e",
                "https://images.unsplash.com/photo-1631049307290-bb947b114627"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=19),
            "latitude": 40.6892,
            "longitude": -73.9441,
            "source_url": "https://bedstuylofts.com"
        },
        {
            "title": "Comfortable 1BR at Ridgewood Heights - No Fee", 
            "address": "60-15 Palmetto St, Ridgewood, NY 11385",
            "price": 3395,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 700,
            "neighborhood": "Ridgewood",
            "borough": "Queens",
            "description": "Spacious 1-bedroom in up-and-coming Ridgewood. Features updated kitchen, good closet space, and quiet residential street. Great value with owner-managed building.",
            "amenities": ["Updated Kitchen", "Storage", "Laundry", "Pet Friendly", "Parking", "Garden Access"],
            "images": [
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec",
                "https://images.pexels.com/photos/6970025/pexels-photo-6970025.jpeg"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=31),
            "latitude": 40.7022,
            "longitude": -73.8962,
            "source_url": "https://ridgewoodheights.com"
        },
        {
            "title": "Renovated Studio at Crown Heights Modern - No Fee",
            "address": "1205 Eastern Pkwy, Brooklyn, NY 11213",
            "price": 3595,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 520,
            "neighborhood": "Crown Heights",
            "borough": "Brooklyn",
            "description": "Newly renovated studio in vibrant Crown Heights near Prospect Park. Features modern finishes, stainless steel appliances, and great natural light. Direct leasing office available.",
            "amenities": ["Near Prospect Park", "Fitness Center", "Storage", "Laundry", "Pet Friendly", "Bike Storage"],
            "images": [
                "https://images.unsplash.com/photo-1631049307290-bb947b114627",
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=13),
            "latitude": 40.6643,
            "longitude": -73.9424,
            "source_url": "https://crownheightsmodern.com"
        },
        {
            "title": "Bright 1BR at Elmhurst Gardens - No Fee",
            "address": "86-12 Broadway, Elmhurst, NY 11373",
            "price": 3295,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 650,
            "neighborhood": "Elmhurst",
            "borough": "Queens",
            "description": "Well-maintained 1-bedroom in diverse Elmhurst neighborhood. Features hardwood floors, updated bathroom, and excellent transportation access. Owner-managed building with no fees.",
            "amenities": ["Hardwood Floors", "Storage", "Laundry", "Pet Friendly", "Parking", "Garden"],
            "images": [
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec",
                "https://images.unsplash.com/photo-1714153542012-6164546db890"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=27),
            "latitude": 40.7424,
            "longitude": -73.8821,
            "source_url": "https://elmhurstgardens.com"
        },
        {
            "title": "Luxury Studio at The Paris UWS - No Fee",
            "address": "752 West End Ave, New York, NY 10025",
            "price": 3795,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 480,
            "neighborhood": "Upper West Side",
            "borough": "Manhattan",
            "description": "Elegant studio at The Paris with modern finishes and 24-hour attended lobby. Near Riverside Park and Central Park. Direct leasing office with owner-paid commission structure.",
            "amenities": ["24-Hour Lobby", "Fitness Center", "Children's Playroom", "Rooftop Terrace", "Storage", "Laundry"],
            "images": [
                "https://images.unsplash.com/photo-1631049307290-bb947b114627",
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=16),
            "latitude": 40.7905,
            "longitude": -73.9729,
            "source_url": "https://stellarmanagement.com/theparisnewyork"
        },
        {
            "title": "Modern 1BR at Ocean Financial District - No Fee",
            "address": "1 West St, New York, NY 10004",
            "price": 3150,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 720,
            "neighborhood": "Financial District",
            "borough": "Manhattan",
            "description": "Contemporary 1-bedroom at Ocean with fitness center and outdoor plaza. Features modern appliances and stunning harbor views. Leasing office offers no-fee rentals with owner-paid commissions.",
            "amenities": ["Harbor Views", "Fitness Center", "Outdoor Plaza", "Laundry on Every Floor", "Storage", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec",
                "https://images.pexels.com/photos/6970025/pexels-photo-6970025.jpeg"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=21),
            "latitude": 40.7047,
            "longitude": -74.0149,
            "source_url": "https://oceanapartments.com"
        },
        {
            "title": "Spacious 1BR at PLG Linden - No Fee",
            "address": "123 Linden Blvd, Brooklyn, NY 11226",
            "price": 2894,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 680,
            "neighborhood": "Prospect-Lefferts Gardens",
            "borough": "Brooklyn",
            "description": "Beautiful 1-bedroom at PLG with indoor pool and golf simulator. Premium amenities and rooftop lounge with neighborhood views. Direct leasing with no broker fees.",
            "amenities": ["Indoor Pool", "Golf Simulator", "Fitness Center", "Rooftop Lounge", "Storage", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1714153542012-6164546db890",
                "https://images.unsplash.com/photo-1632119580908-ae947d4c7691"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=18),
            "latitude": 40.6596,
            "longitude": -73.9442,
            "source_url": "https://plglinden.com"
        },
        {
            "title": "Designer 1BR at The Caroline Chelsea - No Fee",
            "address": "60 W 23rd St, New York, NY 10010",
            "price": 4195,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 750,
            "neighborhood": "Chelsea",
            "borough": "Manhattan",
            "description": "Luxury 1-bedroom at The Caroline with open living spaces and high-end appliances. Features concierge service, game room, and landscaped roof deck. Owner-paid commission structure.",
            "amenities": ["Concierge", "Game Room", "Children's Playroom", "Courtyard", "Landscaped Roof Deck", "Fitness Center"],
            "images": [
                "https://images.pexels.com/photos/9954175/pexels-photo-9954175.jpeg",
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=29),
            "latitude": 40.7433,
            "longitude": -73.9927,
            "source_url": "https://thecarolinechelsea.com"
        },
        {
            "title": "Modern 2BR at 60 Water DUMBO - No Fee",
            "address": "60 Water St, Brooklyn, NY 11201",
            "price": 4195,
            "bedrooms": 2,
            "bathrooms": 1.0,
            "sqft": 950,
            "neighborhood": "DUMBO",
            "borough": "Brooklyn",
            "description": "Luxury 2-bedroom in DUMBO with floor-to-ceiling windows and panoramic views. Features high-end appliances, fitness center, and 24-hour concierge. Direct leasing office available.",
            "amenities": ["Panoramic Views", "24-Hour Concierge", "Fitness Center", "Roof Deck", "High-End Appliances", "Storage"],
            "images": [
                "https://images.unsplash.com/photo-1714153542012-6164546db890",
                "https://images.pexels.com/photos/9954175/pexels-photo-9954175.jpeg"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=33),
            "latitude": 40.7022,
            "longitude": -73.9897,
            "source_url": "https://60waterstreet.com"
        },
        {
            "title": "Bright Studio at 420 West 42nd - No Fee",
            "address": "420 W 42nd St, New York, NY 10036",
            "price": 3495,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 520,
            "neighborhood": "Midtown West",
            "borough": "Manhattan",
            "description": "Renovated studio in Midtown West with modern finishes and landscaped outdoor space. Features fitness center and central laundry. Owner-managed building with no broker fees.",
            "amenities": ["Landscaped Outdoor Space", "Fitness Center", "Central Laundry", "Storage", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1631049307290-bb947b114627",
                "https://images.unsplash.com/photo-1742226789249-32cfaac0ff5e"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=12),
            "latitude": 40.7589,
            "longitude": -73.9891,
            "source_url": "https://420west42nd.com"
        },
        {
            "title": "Spacious 1BR at 50 Clarkson PLG - No Fee",
            "address": "50 Clarkson Ave, Brooklyn, NY 11226",
            "price": 2935,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 700,
            "neighborhood": "Prospect-Lefferts Gardens",
            "borough": "Brooklyn",
            "description": "Modern 1-bedroom in Prospect-Lefferts Gardens with co-working space and media lounge. Features fitness center and rooftop courtyard. Direct leasing with owner-paid commissions.",
            "amenities": ["Co-working Space", "Media Lounge", "Fitness Center", "Rooftop Courtyard", "Storage", "Pet Friendly"],
            "images": [
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec",
                "https://images.pexels.com/photos/6970025/pexels-photo-6970025.jpeg"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=25),
            "latitude": 40.6547,
            "longitude": -73.9514,
            "source_url": "https://50clarksonave.com"
        },
        {
            "title": "Luxury 1BR at Glenwood Manhattan - No Fee",
            "address": "301 E 22nd St, New York, NY 10010",
            "price": 3895,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 680,
            "neighborhood": "Gramercy",
            "borough": "Manhattan",
            "description": "Premium 1-bedroom by Glenwood Management with resident lounge and landscaped gardens. Features fitness center and 24-hour doorman. No-fee luxury living in prime location.",
            "amenities": ["24-Hour Doorman", "Resident Lounge", "Landscaped Gardens", "Fitness Center", "Storage", "Pet Friendly"],
            "images": [
                "https://images.pexels.com/photos/9954175/pexels-photo-9954175.jpeg",
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=19),
            "latitude": 40.7371,
            "longitude": -73.9834,
            "source_url": "https://glenwoodnyc.com"
        },
        {
            "title": "Modern 1BR at 1134 Fulton Bed-Stuy - No Fee",
            "address": "1134 Fulton St, Brooklyn, NY 11238",
            "price": 3163,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 650,
            "neighborhood": "Bedford-Stuyvesant",
            "borough": "Brooklyn",
            "description": "Contemporary 1-bedroom in Bedford-Stuyvesant with pet spa and media room. Features fitness center, courtyard, and roof deck. Leasing office offers owner-paid commission structure.",
            "amenities": ["Pet Spa", "Media Room", "Fitness Center", "Package Room", "Courtyard", "Roof Deck"],
            "images": [
                "https://images.unsplash.com/photo-1714153542012-6164546db890",
                "https://images.unsplash.com/photo-1632119580908-ae947d4c7691"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=31),
            "latitude": 40.6815,
            "longitude": -73.9442,
            "source_url": "https://1134fulton.com"
        },
        {
            "title": "Designer 2BR at 100 Ainslie Williamsburg - No Fee",
            "address": "100 Ainslie St, Brooklyn, NY 11249",
            "price": 3926,
            "bedrooms": 2,
            "bathrooms": 1.0,
            "sqft": 900,
            "neighborhood": "East Williamsburg",
            "borough": "Brooklyn",
            "description": "Stylish 2-bedroom in East Williamsburg with furnished roof deck and bike room. Features fitness center and laundry facilities. Direct leasing office with no broker fees.",
            "amenities": ["Furnished Roof Deck", "Bike Room", "Fitness Center", "Laundry Room", "Storage", "Pet Friendly"],
            "images": [
                "https://images.pexels.com/photos/9954175/pexels-photo-9954175.jpeg",
                "https://images.unsplash.com/photo-1714153542012-6164546db890"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=38),
            "latitude": 40.7151,
            "longitude": -73.9486,
            "source_url": "https://100ainslie.com"
        },
        {
            "title": "Elegant 1BR at Flatbush Beverley - No Fee",
            "address": "2201 Beverley Rd, Brooklyn, NY 11226",
            "price": 2950,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 620,
            "neighborhood": "Flatbush",
            "borough": "Brooklyn",
            "description": "Beautiful 1-bedroom in Flatbush with updated kitchen and hardwood floors. Features laundry facilities and storage options. Owner-managed building with direct leasing office.",
            "amenities": ["Updated Kitchen", "Hardwood Floors", "Laundry Facilities", "Storage", "Pet Friendly", "Garden Access"],
            "images": [
                "https://images.unsplash.com/photo-1632830025328-cce71800b9ec",
                "https://images.pexels.com/photos/6970025/pexels-photo-6970025.jpeg"
            ],
            "contact_info": {
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=14),
            "latitude": 40.6418,
            "longitude": -73.9614,
            "source_url": "https://flatbushbeverley.com"
        },
        # Gotham West Apartments from Scraped Data
        {
            "title": "Luxury Alcove Studio at Gotham West - Hell's Kitchen Premium",
            "address": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
            "price": 3863,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 550,
            "neighborhood": "Hell's Kitchen",
            "borough": "Manhattan", 
            "description": "Exquisite alcove studio in Hell's Kitchen's most coveted luxury building. Features wide plank oak flooring, floor-to-ceiling windows, custom energy-efficient lighting, and views of landscaped courtyard and Hudson River.",
            "amenities": ["Wide plank oak flooring", "Floor-to-ceiling windows", "Hudson River views", "Granite countertops", "KitchenAid appliances", "In-unit washer/dryer", "32nd floor roof deck", "Fitness center with Peloton", "Concierge services", "24-hour doorman"],
            "images": ["https://assets.nestiostatic.com/unit_photos/originals/6ebde14bba55a2f05e8248ab515c6806.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-1-1.jpg"],
            "contact_info": {
                "phone": "(917) 451-5592",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=7),
            "latitude": 40.7589,
            "longitude": -73.9925,
            "source_url": "https://www.gothamwestnyc.com/"
        },
        {
            "title": "Bright Studio at Gotham West - No Fee Hell's Kitchen Living",
            "address": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
            "price": 3962,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 485,
            "neighborhood": "Hell's Kitchen",
            "borough": "Manhattan",
            "description": "Bright and airy studio apartment with meticulous interiors and thoughtful finishes sourced from Italy. Features premium materials, built-in pantries, oversized bathroom vanities, and full-length mirrored medicine cabinets.",
            "amenities": ["Italian-sourced finishes", "Built-in pantries", "Oversized bathroom vanities", "Energy-efficient lighting", "Bosch appliances", "Resident lounge with fireplace", "Business center", "Billiard room"],
            "images": ["https://assets.nestiostatic.com/unit_photos/originals/3dcd495c0c2dd42451dae58eb4b95c64.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-2-1.jpg"],
            "contact_info": {
                "phone": "(917) 451-5592",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=12),
            "latitude": 40.7589,
            "longitude": -73.9925,
            "source_url": "https://www.gothamwestnyc.com/"
        },
        {
            "title": "Premium Alcove Studio - Gotham West Luxury with Hudson Views",
            "address": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
            "price": 4108,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "sqft": 620,
            "neighborhood": "Hell's Kitchen",
            "borough": "Manhattan",
            "description": "Premium alcove studio with spectacular Hudson River and Midtown Manhattan skyline views. Refined interiors feature wide plank oak flooring, granite countertops, stainless steel appliances, and spacious walk-in closets.",
            "amenities": ["Hudson River views", "Manhattan skyline views", "Wide plank oak flooring", "Spacious walk-in closets", "Granite countertops", "Stainless steel appliances", "Gotham Living program", "Monthly resident events"],
            "images": ["https://assets.nestiostatic.com/unit_photos/originals/a0fa55fe5bc6a2bd66a092c053dc5428.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-3-1.jpg"],
            "contact_info": {
                "phone": "(917) 451-5592",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=18),
            "latitude": 40.7589,
            "longitude": -73.9925,
            "source_url": "https://www.gothamwestnyc.com/"
        },
        {
            "title": "Sophisticated 1BR at Gotham West - Hell's Kitchen No Fee Luxury",
            "address": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
            "price": 4695,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 725,
            "neighborhood": "Hell's Kitchen",
            "borough": "Manhattan",
            "description": "Sophisticated one-bedroom residence with bright, airy interiors and premium materials throughout. Features custom energy-efficient lighting, linen-textured backsplash, and tailored finishes that create a welcoming and timeless living experience.",
            "amenities": ["Custom energy-efficient lighting", "Linen-textured backsplash", "Premium materials", "Demonstration kitchen", "Fitness center with movement studio", "Complimentary bike storage", "Indoor parking garage"],
            "images": ["https://assets.nestiostatic.com/unit_photos/originals/ca0292e7fe613a349fd7e1cd484ad0bc.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-4-1.jpg"],
            "contact_info": {
                "phone": "(917) 451-5592", 
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=25),
            "latitude": 40.7589,
            "longitude": -73.9925,
            "source_url": "https://www.gothamwestnyc.com/"
        },
        {
            "title": "Elegant 1BR with Modern Finishes - Gotham West Hell's Kitchen",
            "address": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
            "price": 4721,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 750,
            "neighborhood": "Hell's Kitchen",
            "borough": "Manhattan",
            "description": "Elegant one-bedroom apartment with modern finishes and thoughtful design elements. Spacious layout features floor-to-ceiling windows, built-in storage solutions, and high-end appliances.",
            "amenities": ["Floor-to-ceiling windows", "Built-in storage", "High-end appliances", "Modern finishes", "Landscaped courtyard", "32nd floor roof deck", "Panoramic city views", "Dry-cleaning valet"],
            "images": ["https://assets.nestiostatic.com/unit_photos/originals/d44aeb1d1cef0ecf6bbece052f1c5203.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-5-1.jpg"],
            "contact_info": {
                "phone": "(917) 451-5592",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=30),
            "latitude": 40.7589,
            "longitude": -73.9925,
            "source_url": "https://www.gothamwestnyc.com/"
        },
        {
            "title": "Spacious 1BR with River Views - Gotham West Manhattan Premium",
            "address": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
            "price": 4787,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 780,
            "neighborhood": "Hell's Kitchen", 
            "borough": "Manhattan",
            "description": "Spacious one-bedroom residence with stunning river views and refined finishes. Features include honed absolute black granite countertops, oversized bathroom vanities, and select Italian design elements.",
            "amenities": ["River views", "Honed granite countertops", "Oversized bathroom vanities", "Italian design elements", "Prime location", "Times Square proximity", "Bryant Park access", "Curated art gallery"],
            "images": ["https://assets.funnelstatic.com/unit_photos/originals/87b4ea3da488c84542919ca427fd9154.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-6-1.jpg"],
            "contact_info": {
                "phone": "(917) 451-5592",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=35),
            "latitude": 40.7589,
            "longitude": -73.9925,
            "source_url": "https://www.gothamwestnyc.com/"
        },
        {
            "title": "High-Floor 1BR with Manhattan Skyline Views - Gotham West",
            "address": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
            "price": 5194,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "sqft": 825,
            "neighborhood": "Hell's Kitchen",
            "borough": "Manhattan", 
            "description": "High-floor one-bedroom with breathtaking Manhattan skyline views from floor-to-ceiling windows. Luxury finishes throughout including wide plank oak flooring and custom lighting.",
            "amenities": ["Manhattan skyline views", "High-floor location", "Wide plank oak flooring", "Custom lighting", "Complimentary shuttle to Grand Central", "Multiple subway lines", "A,C,E at Port Authority"],
            "images": ["https://assets.nestiostatic.com/unit_photos/originals/2a83fe99a1d6725ef9d61dd6c5eb2814.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-residences-gallery-7-1.jpg"],
            "contact_info": {
                "phone": "(917) 451-5592",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=40),
            "latitude": 40.7589,
            "longitude": -73.9925,
            "source_url": "https://www.gothamwestnyc.com/"
        },
        {
            "title": "Luxury 2BR/2BA Corner Unit - Gotham West Hell's Kitchen",
            "address": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
            "price": 6890,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1150,
            "neighborhood": "Hell's Kitchen",
            "borough": "Manhattan",
            "description": "Luxury two-bedroom corner unit with dual exposures and abundant natural light. Features two full bathrooms, spacious living areas, and premium finishes throughout.",
            "amenities": ["Corner unit", "Dual exposures", "Two full bathrooms", "Spacious living areas", "Premium finishes", "Fitness center with Peloton", "Resident lounge", "Rooftop entertainment", "Bike valet service"],
            "images": ["https://assets.nestiostatic.com/unit_photos/originals/ea2df7ab4e87c542fb169c148e0b8916.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-amenities-gallery-1-2.jpg"],
            "contact_info": {
                "phone": "(917) 451-5592", 
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=45),
            "latitude": 40.7589,
            "longitude": -73.9925,
            "source_url": "https://www.gothamwestnyc.com/"
        },
        {
            "title": "Presidential 3BR/2BA Penthouse Style - Gotham West Luxury",
            "address": "550 West 45th Street, Hell's Kitchen, Manhattan, NY 10036",
            "price": 9345,
            "bedrooms": 3,
            "bathrooms": 2.0,
            "sqft": 1650,
            "neighborhood": "Hell's Kitchen",
            "borough": "Manhattan",
            "description": "Presidential three-bedroom penthouse-style residence with panoramic Manhattan views and luxury finishes throughout. Features spacious living and dining areas, gourmet kitchen with premium appliances, master bedroom suite, and two additional bedrooms.",
            "amenities": ["Penthouse-style living", "Panoramic Manhattan views", "Luxury finishes", "Spacious living areas", "Gourmet kitchen", "Premium appliances", "Master bedroom suite", "Rooftop deck access", "Gotham Living program"],
            "images": ["https://assets.nestiostatic.com/unit_photos/originals/45135edfbbd09f4fa07a3bb09e024778.jpg", "https://www.gothamwestnyc.com/wp-content/uploads/2025/06/gotham-west-amenities-gallery-16-1.jpg"],
            "contact_info": {
                "phone": "(917) 451-5592",
                "email": "placesnyc88@gmail.com",
                "broker": "Chris Trunell"
            },
            "available_date": datetime.utcnow() + timedelta(days=50),
            "latitude": 40.7589,
            "longitude": -73.9925,
            "source_url": "https://www.gothamwestnyc.com/"
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
    
    # Add Related Rentals apartments
    relatedrentals_apartments = await scrape_relatedrentals_apartments()
    all_apartments.extend(relatedrentals_apartments)
    
    # Clear existing apartments to ensure fresh data with updated email addresses
    await db.apartments.delete_many({})
    
    # Store in database
    for apartment in all_apartments:
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
    
    # Send new user notification email to placesnyc88@gmail.com
    try:
        registration_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Email content for new user notification
        notification_subject = f"New User Registration - {user_data.full_name}"
        notification_body = f"""
        🎉 NEW USER REGISTRATION 🎉
        
        A new user has just signed up for NoFeePlaces.com!
        
        📋 User Details:
        👤 Full Name: {user_data.full_name}
        ✉️ Email: {user_data.email}
        🕐 Registration Time: {registration_time}
        🆔 User ID: {user.id}
        
        🌐 Platform: NoFeePlaces.com
        📱 User can now:
        • Browse no-fee apartments
        • Save favorites
        • Schedule viewings
        • Contact agents directly
        
        This user is now part of our growing community of NYC apartment hunters!
        
        ---
        Sent automatically from NoFeePlaces.com Registration System
        """

        # Send notification email
        await send_email(
            to_email='placesnyc88@gmail.com',
            subject=notification_subject,
            body=notification_body
        )
        
        print(f"New user registration notification sent for: {user_data.full_name} ({user_data.email})")
        
    except Exception as e:
        print(f"Failed to send registration notification email: {e}")
        # Don't fail registration if email fails - just log the error
    
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
    # Build filter query - updated to handle both is_no_fee and no_fee fields
    query = {
        "$or": [
            {"is_no_fee": True},
            {"no_fee": True}
        ]
    }
    
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
        query["square_feet"] = {"$gte": min_sqft}
    if max_sqft:
        if "square_feet" in query:
            query["square_feet"]["$lte"] = max_sqft
        else:
            query["square_feet"] = {"$lte": max_sqft}
    
    if search_term:
        query["$or"] = [
            {"title": {"$regex": search_term, "$options": "i"}},
            {"location": {"$regex": search_term, "$options": "i"}},
            {"address": {"$regex": search_term, "$options": "i"}},
            {"neighborhood": {"$regex": search_term, "$options": "i"}},
            {"description": {"$regex": search_term, "$options": "i"}}
        ]
    
    # Calculate skip for pagination
    skip = (page - 1) * limit
    
    # Execute query with custom sorting - Waterline Square apartments last
    apartments_cursor = db.apartments.find(query).skip(skip).limit(limit)
    
    # Custom sort: Non-Waterline apartments first (by created_at desc), then Waterline apartments (by created_at desc)
    apartments_cursor = apartments_cursor.sort([
        ("title", 1),  # This will put Waterline Square apartments last (since "Waterline" comes after most other titles alphabetically)
        ("created_at", -1)  # Then sort by creation date within each group
    ])
    
    apartments = await apartments_cursor.to_list(length=limit)
    
    # Additional sorting logic: ensure Waterline Square apartments are definitely at the end
    waterline_apartments = []
    other_apartments = []
    
    for apt in apartments:
        if "waterline" in apt.get("title", "").lower():
            waterline_apartments.append(apt)
        else:
            other_apartments.append(apt)
    
    # Combine lists: other apartments first, then Waterline apartments
    sorted_apartments = other_apartments + waterline_apartments
    
    return [Apartment(**apt) for apt in sorted_apartments]

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

# Enhanced Email service for appointment confirmations with calendar invites
async def send_appointment_confirmation_email(appointment_data: dict, apartment_data: dict):
    """Send appointment confirmation email with calendar invites to visitor and broker"""
    
    if not EMAIL_PASSWORD or EMAIL_PASSWORD == '':
        # Email not configured, use mock email
        print("[MOCK EMAIL] Appointment confirmation emails would be sent")
        print(f"[MOCK EMAIL] Visitor: {appointment_data['visitor_name']} ({appointment_data['visitor_email']})")
        print(f"[MOCK EMAIL] Apartment: {apartment_data['title']}")
        print(f"[MOCK EMAIL] Date: {appointment_data['appointment_date']}")
        return

    def create_calendar_event(appointment_data: dict, apartment_data: dict):
        """Create an iCal calendar event"""
        cal = Calendar()
        cal.add('prodid', '-//PLACES No Fee//Apartment Viewing//EN')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')

        event = Event()
        
        # Event details
        event.add('uid', f"appointment-{appointment_data['id']}@nofeeplaces.com")
        event.add('summary', f"Apartment Viewing - {apartment_data['title']}")
        
        # Parse the appointment date and time
        appointment_datetime = appointment_data['appointment_date']
        if isinstance(appointment_datetime, str):
            appointment_datetime = datetime.fromisoformat(appointment_datetime.replace('Z', '+00:00'))
        
        # Set timezone to Eastern Time (NYC)
        eastern = pytz.timezone('US/Eastern')
        if appointment_datetime.tzinfo is None:
            appointment_datetime = eastern.localize(appointment_datetime)
        
        # Event duration (1 hour)
        end_time = appointment_datetime + timedelta(hours=1)
        
        event.add('dtstart', appointment_datetime)
        event.add('dtend', end_time)
        event.add('location', apartment_data['address'])
        
        # Detailed description
        description = f"""
Apartment Viewing Details:

Property: {apartment_data['title']}
Address: {apartment_data['address']}
Rent: ${apartment_data['price']:,}/month
Bedrooms: {apartment_data.get('bedrooms', 'N/A')}
Bathrooms: {apartment_data.get('bathrooms', 'N/A')}

Visitor: {appointment_data['visitor_name']}
Phone: {appointment_data['visitor_phone']}
Email: {appointment_data['visitor_email']}

Notes: {appointment_data.get('notes', 'No additional notes')}

Contact Chris Trunell at (646) 408-8048 if you need to reschedule.

Best regards,
PLACES No Fee
        """.strip()
        
        event.add('description', description)
        
        # Add attendees
        event.add('attendee', f"MAILTO:{appointment_data['visitor_email']}")
        event.add('attendee', f"MAILTO:placesnyc88@gmail.com")
        
        # Organizer
        event.add('organizer', f"MAILTO:placesnyc88@gmail.com")
        
        # Add event to calendar
        cal.add_component(event)
        
        return cal.to_ical()

    async def send_email_with_calendar(to_email: str, subject: str, body: str, calendar_data: bytes):
        """Send email with calendar attachment"""
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add calendar attachment
            cal_attachment = MIMEBase('text', 'calendar')
            cal_attachment.set_payload(calendar_data)
            encoders.encode_base64(cal_attachment)
            cal_attachment.add_header(
                'Content-Disposition',
                'attachment; filename="appointment.ics"'
            )
            cal_attachment.add_header('Content-Type', 'text/calendar; method=REQUEST')
            msg.attach(cal_attachment)
            
            # Send email
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            if EMAIL_USE_TLS:
                server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_USER, to_email, text)
            server.quit()
            
            print(f"Email with calendar invite sent successfully to {to_email}")
        except Exception as e:
            print(f"Failed to send email with calendar to {to_email}: {e}")
            raise
    
    try:
        # Create calendar invite
        calendar_data = create_calendar_event(appointment_data, apartment_data)
        
        # Email content for visitor
        visitor_subject = f"🏠 Apartment Viewing Confirmed - {apartment_data['title']}"
        visitor_body = f"""
Dear {appointment_data['visitor_name']},

Your apartment viewing has been confirmed! Here are the details:

🏠 Property: {apartment_data['title']}
📍 Address: {apartment_data['address']}
📅 Date: {appointment_data['appointment_date'].strftime('%A, %B %d, %Y')}
🕐 Time: {appointment_data['appointment_time']}
💰 Rent: ${apartment_data['price']:,}/month
📋 Status: {appointment_data['status'].title()}

📅 CALENDAR INVITE: Please find the calendar invite (.ics file) attached to this email. 
Add it to your calendar to receive reminders!

Please arrive on time and bring a valid ID. If you need to reschedule or cancel, please contact us as soon as possible.

Contact Information:
📞 Phone: (646) 408-8048
✉️ Email: placesnyc88@gmail.com

Looking forward to showing you this amazing no-fee apartment!

Best regards,
Chris Trunell
PLACES No Fee
NoFeePlaces.com
        """

        # Email content for broker
        broker_subject = f"📅 New Apartment Viewing Scheduled - {apartment_data['title']}"
        broker_body = f"""
New apartment viewing scheduled:

🏠 Property: {apartment_data['title']}
📍 Address: {apartment_data['address']}
📅 Date: {appointment_data['appointment_date'].strftime('%A, %B %d, %Y')}
🕐 Time: {appointment_data['appointment_time']}

Visitor Information:
👤 Name: {appointment_data['visitor_name']}
📞 Phone: {appointment_data['visitor_phone']}
✉️ Email: {appointment_data['visitor_email']}
📝 Notes: {appointment_data.get('notes', 'No additional notes')}

📅 CALENDAR INVITE: Calendar event attached for your scheduling system.

Appointment ID: {appointment_data['id']}
Status: {appointment_data['status'].title()}

Created via NoFeePlaces.com
        """

        # Send email with calendar invite to visitor
        await send_email_with_calendar(
            to_email=appointment_data['visitor_email'],
            subject=visitor_subject,
            body=visitor_body,
            calendar_data=calendar_data
        )

        # Send email with calendar invite to broker
        await send_email_with_calendar(
            to_email='placesnyc88@gmail.com',
            subject=broker_subject,
            body=broker_body,
            calendar_data=calendar_data
        )
        
    except Exception as e:
        print(f"Failed to send appointment confirmation email: {e}")

async def send_email(to_email: str, subject: str, body: str):
    """Send email using SMTP - Mock implementation for testing"""
    try:
        # Check if email is properly configured
        if not EMAIL_PASSWORD or EMAIL_PASSWORD == '':
            # Mock email sending - log instead of actually sending
            print(f"[MOCK EMAIL] Email would be sent to: {to_email}")
            print(f"[MOCK EMAIL] Subject: {subject}")
            print(f"[MOCK EMAIL] Body: {body}")
            print(f"[MOCK EMAIL] Email sent successfully (mocked)")
            return
        
        # Real email sending code (if credentials are configured)
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        # Don't raise exception for mock email - just log and continue
        if not EMAIL_PASSWORD or EMAIL_PASSWORD == '':
            print(f"[MOCK EMAIL] Continuing with mock email (no real credentials configured)")
        else:
            raise

# Contact/Email Routes
@api_router.post("/contact/apartment")
async def send_apartment_inquiry(request: ContactRequest):
    """Send apartment inquiry email to agent"""
    try:
        # Email content for the agent (Chris)
        agent_subject = f"New Inquiry - {request.apartment_title}"
        agent_body = f"""
        New apartment inquiry from {request.name}:

        🏠 Property: {request.apartment_title}
        📍 Address: {request.apartment_address}
        💰 Price: ${request.apartment_price:,}/month
        
        Contact Information:
        👤 Name: {request.name}
        📞 Phone: {request.phone}
        ✉️ Email: {request.email}
        
        Message:
        {request.message}
        
        Please respond to {request.email} or call {request.phone}.
        
        Sent via NoFeePlaces.com
        """

        # Email content for the prospective tenant
        tenant_subject = f"We received your inquiry about {request.apartment_title}"
        tenant_body = f"""
        Hi {request.name},

        Thank you for your interest in {request.apartment_title}!

        We have received your inquiry and Chris will get back to you within 24 hours. Here are the details of your inquiry:

        🏠 Property: {request.apartment_title}
        📍 Address: {request.apartment_address}
        💰 Rent: ${request.apartment_price:,}/month
        
        Your Message: {request.message}

        In the meantime, feel free to:
        • Browse more apartments at NoFeePlaces.com
        • Call us directly at (646) 408-8048
        • Email us at placesnyc88@gmail.com

        We look forward to helping you find your perfect no-fee apartment!

        Best regards,
        Chris Trunell
        NoFeePlaces.com
        (646) 408-8048
        """

        # Send email to agent
        await send_email(
            to_email='placesnyc88@gmail.com',
            subject=agent_subject,
            body=agent_body
        )

        # Send confirmation email to tenant
        await send_email(
            to_email=request.email,
            subject=tenant_subject,
            body=tenant_body
        )

        return {"message": "Email sent successfully"}
        
    except Exception as e:
        print(f"Failed to send contact email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

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
    
    # Send email confirmation
    try:
        await send_appointment_confirmation_email(appointment.dict(), apartment)
    except Exception as e:
        print(f"Failed to send email confirmation: {e}")
        # Don't fail the appointment creation if email fails
    
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

# Chat Routes
@api_router.post("/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get apartment context if apartment_id is provided
        apartment_context = ""
        if request.apartment_id:
            apartment = await db.apartments.find_one({"id": request.apartment_id})
            if apartment:
                apartment_context = f"""
Current apartment context:
- Title: {apartment['title']}
- Address: {apartment['address']}
- Price: ${apartment['price']}/month
- Bedrooms: {apartment['bedrooms']} {'Studio' if apartment['bedrooms'] == 0 else 'bedroom(s)'}
- Bathrooms: {apartment['bathrooms']}
- Square feet: {apartment['sqft']}
- Neighborhood: {apartment['neighborhood']}, {apartment['borough']}
- Amenities: {', '.join(apartment.get('amenities', []))}
- Contact: {apartment['contact_info']['broker']} at {apartment['contact_info']['phone']} or {apartment['contact_info']['email']}
"""

        # Create system message for real estate assistant
        system_message = request.context or f"""You are a helpful AI assistant for NoFeePlaces.com, a premium no-fee apartment rental platform in NYC. 

Your role is to help potential tenants with leasing questions about our luxury apartments across Manhattan, Brooklyn, and Queens. 

Key Information:
- We specialize in NO BROKER FEE apartments
- All our properties have on-site leasing offices with owner-paid commissions
- We have 64+ luxury apartments ranging from $2,600-$14,895/month
- Contact person: Chris Trunell at (646) 408-8048 or placesnyc88@gmail.com
- Users can schedule viewings directly through our website calendar

Common Questions & Answers:
- Documents needed: Photo ID, proof of income (3 recent pay stubs or employment letter), bank statements, references
- Application process: Submit application online, income verification, background check, lease signing
- Guarantors: Yes, we accept guarantors with 80x monthly rent annual income
- Pets: Most buildings are pet-friendly with additional deposit
- Move-in costs: First month, security deposit, broker fee is WAIVED
- Viewing availability: 10 AM to 7 PM daily through our booking system

Be conversational, helpful, and professional. Always encourage users to contact Chris Trunell for specific questions or to schedule viewings.

{apartment_context}"""

        # Initialize LLM chat
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
            
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o-mini")

        # Create user message
        user_message = UserMessage(text=request.message)
        
        # Get AI response
        ai_response = await chat.send_message(user_message)
        
        # Save chat message to database
        chat_message = ChatMessage(
            session_id=session_id,
            message=request.message,
            response=ai_response,
            apartment_context=request.apartment_id
        )
        
        await db.chat_messages.insert_one(chat_message.dict())
        
        return {
            "response": ai_response,
            "session_id": session_id,
            "message_id": chat_message.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

@api_router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        messages = await db.chat_messages.find(
            {"session_id": session_id}
        ).sort("created_at", 1).to_list(length=50)
        
        return [ChatMessage(**msg) for msg in messages]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")

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