"""
Landlord Portal Models and Pydantic Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import uuid
from enum import Enum

# Subscription Plans
class SubscriptionPlan(str, Enum):
    # Small Landlords
    BASIC = "basic"              # $19.99/apartment/month
    FEATURED = "featured"        # $69/apartment/month  
    PREMIUM = "premium"          # $99/apartment/month
    
    # Large Property Managers
    PORTFOLIO = "portfolio"      # $99/month unlimited
    ENTERPRISE = "enterprise"    # $299/month unlimited

class SubscriptionStatus(str, Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELED = "canceled"
    EXPIRED = "expired"

# Landlord Registration
class LandlordRegistration(BaseModel):
    email: str = Field(..., description="Landlord email address")
    name: str = Field(..., description="Full name or company name")
    phone: Optional[str] = Field(None, description="Phone number")
    company_name: Optional[str] = Field(None, description="Property management company name")
    license_number: Optional[str] = Field(None, description="Real estate license number")
    property_count: int = Field(..., description="Number of properties managed")
    plan: SubscriptionPlan = Field(..., description="Selected subscription plan")
    trial_requested: bool = Field(True, description="Request free trial")

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email address')
        return v.lower()

    @validator('property_count')
    def validate_property_count(cls, v):
        if v < 1:
            raise ValueError('Property count must be at least 1')
        return v

# Landlord Profile
class LandlordProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    phone: Optional[str] = None
    company_name: Optional[str] = None
    license_number: Optional[str] = None
    property_count: int
    subscription_plan: SubscriptionPlan
    subscription_status: SubscriptionStatus = SubscriptionStatus.TRIAL
    trial_end_date: Optional[datetime] = None
    billing_start_date: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_verified: bool = False
    
    class Config:
        use_enum_values = True

# Listing Submission
class ListingSubmission(BaseModel):
    title: str = Field(..., description="Apartment title")
    description: str = Field(..., description="Apartment description")
    address: str = Field(..., description="Full address")
    neighborhood: str = Field(..., description="Neighborhood")
    borough: str = Field(..., description="Borough")
    price: float = Field(..., description="Monthly rent")
    bedrooms: int = Field(..., description="Number of bedrooms")
    bathrooms: float = Field(..., description="Number of bathrooms")
    square_feet: Optional[int] = None
    amenities: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list, description="Image URLs")
    available_date: str = Field(..., description="Available date")
    lease_terms: str = Field(default="12 months minimum")
    pet_policy: str = Field(default="No pets")
    utilities_included: List[str] = Field(default_factory=list)
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

    @validator('bedrooms')
    def validate_bedrooms(cls, v):
        if v < 0 or v > 10:
            raise ValueError('Bedrooms must be between 0 and 10')
        return v

# Payment Package Selection
class PaymentPackage(BaseModel):
    package_id: str = Field(..., description="Package identifier")
    apartment_count: int = Field(1, description="Number of apartments")
    origin_url: str = Field(..., description="Frontend origin URL")

# Subscription Billing
class SubscriptionBilling(BaseModel):
    landlord_id: str
    plan: SubscriptionPlan
    apartment_count: int
    monthly_rate: float
    billing_cycle_start: datetime
    billing_cycle_end: datetime
    stripe_subscription_id: Optional[str] = None
    payment_status: str = "pending"
    
# Payment Transaction
class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    landlord_id: str
    session_id: str
    payment_id: Optional[str] = None
    amount: float
    currency: str = "usd"
    plan: SubscriptionPlan
    apartment_count: int
    payment_status: str = "initiated"
    stripe_status: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# API Response Models
class LandlordRegistrationResponse(BaseModel):
    message: str
    landlord_id: str
    trial_end_date: Optional[datetime]
    next_step: str

class PaymentSessionResponse(BaseModel):
    checkout_url: str
    session_id: str
    amount: float
    plan: str

class LandlordDashboardData(BaseModel):
    profile: LandlordProfile
    active_listings: int
    total_inquiries: int
    this_month_inquiries: int
    subscription_status: str
    days_remaining: Optional[int]
    next_billing_date: Optional[datetime]

# Pricing Configuration
PRICING_PLANS = {
    # Small Landlords (per apartment/month)
    SubscriptionPlan.BASIC: {
        "name": "Basic Listing",
        "price": 19.99,
        "per_apartment": True,
        "features": [
            "Standard apartment listing",
            "Contact form integration", 
            "Basic listing analytics",
            "Email support"
        ],
        "max_apartments": 50
    },
    SubscriptionPlan.FEATURED: {
        "name": "Featured Listing", 
        "price": 69.0,
        "per_apartment": True,
        "features": [
            "All Basic features",
            "Featured placement (top 3 results)",
            "VERIFIED badge",
            "Priority customer support",
            "Enhanced listing analytics"
        ],
        "max_apartments": 50
    },
    SubscriptionPlan.PREMIUM: {
        "name": "Premium Listing",
        "price": 99.0, 
        "per_apartment": True,
        "features": [
            "All Featured features",
            "Priority contact routing",
            "Detailed performance analytics",
            "Custom branding options",
            "Dedicated account manager"
        ],
        "max_apartments": 50
    },
    
    # Large Property Managers (flat monthly rate)
    SubscriptionPlan.PORTFOLIO: {
        "name": "Portfolio Manager",
        "price": 99.0,
        "per_apartment": False,
        "features": [
            "Unlimited apartment listings",
            "Bulk upload tools",
            "Portfolio analytics dashboard", 
            "Multi-user account access",
            "Priority support"
        ],
        "max_apartments": None
    },
    SubscriptionPlan.ENTERPRISE: {
        "name": "Enterprise Solution",
        "price": 299.0,
        "per_apartment": False, 
        "features": [
            "All Portfolio features",
            "White-label options",
            "API access",
            "Custom integrations",
            "Dedicated success manager",
            "Advanced reporting"
        ],
        "max_apartments": None
    }
}

def calculate_monthly_cost(plan: SubscriptionPlan, apartment_count: int = 1) -> float:
    """Calculate monthly cost for a subscription plan"""
    plan_config = PRICING_PLANS[plan]
    
    if plan_config["per_apartment"]:
        return plan_config["price"] * apartment_count
    else:
        return plan_config["price"]

def get_plan_features(plan: SubscriptionPlan) -> List[str]:
    """Get features for a subscription plan"""
    return PRICING_PLANS[plan]["features"]