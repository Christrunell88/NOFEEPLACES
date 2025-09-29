"""
Landlord Portal API Endpoints
"""

import os
import asyncio
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from typing import Optional, List
import uuid
import logging

from landlord_models import *
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from email_service import email_service

# Setup logging
logger = logging.getLogger(__name__)

# Create router
landlord_router = APIRouter(prefix="/api/landlord", tags=["landlord"])

# Stripe configuration
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# Database (imported from main server)
db = None  # Will be set by main server

def set_database(database):
    """Set database connection from main server"""
    global db
    db = database

@landlord_router.post("/register", response_model=LandlordRegistrationResponse)
async def register_landlord(registration: LandlordRegistration):
    """Register new landlord with free trial"""
    try:
        # Check if email already exists
        existing = await db.landlords.find_one({"email": registration.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create landlord profile
        trial_days = 14  # 14-day free trial
        trial_end = datetime.utcnow() + timedelta(days=trial_days)
        
        landlord = LandlordProfile(
            email=registration.email,
            name=registration.name,
            phone=registration.phone,
            company_name=registration.company_name,
            license_number=registration.license_number,
            property_count=registration.property_count,
            subscription_plan=registration.plan,
            subscription_status=SubscriptionStatus.TRIAL,
            trial_end_date=trial_end
        )
        
        # Save to database
        await db.landlords.insert_one(landlord.dict())
        
        # Send welcome email
        try:
            await send_welcome_email(landlord)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
        
        # Determine next step based on plan
        if registration.plan in [SubscriptionPlan.BASIC, SubscriptionPlan.FEATURED, SubscriptionPlan.PREMIUM]:
            next_step = "list_apartments"
        else:
            next_step = "setup_payment"
        
        return LandlordRegistrationResponse(
            message=f"Registration successful! You have a {trial_days}-day free trial.",
            landlord_id=landlord.id,
            trial_end_date=trial_end,
            next_step=next_step
        )
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@landlord_router.get("/dashboard/{landlord_id}")
async def get_landlord_dashboard(landlord_id: str):
    """Get landlord dashboard data"""
    try:
        # Get landlord profile
        landlord = await db.landlords.find_one({"id": landlord_id})
        if not landlord:
            raise HTTPException(status_code=404, detail="Landlord not found")
        
        # Get listing statistics
        active_listings = await db.apartments.count_documents({
            "landlord_id": landlord_id,
            "available": True
        })
        
        # Get inquiry statistics
        total_inquiries = await db.contacts.count_documents({
            "landlord_id": landlord_id
        })
        
        # Get this month's inquiries
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month_inquiries = await db.contacts.count_documents({
            "landlord_id": landlord_id,
            "created_at": {"$gte": month_start.isoformat()}
        })
        
        # Calculate days remaining in trial/subscription
        days_remaining = None
        next_billing_date = None
        
        if landlord["subscription_status"] == "trial" and landlord.get("trial_end_date"):
            trial_end = datetime.fromisoformat(landlord["trial_end_date"].replace("Z", "+00:00"))
            days_remaining = max(0, (trial_end - datetime.utcnow()).days)
        elif landlord.get("billing_start_date"):
            billing_start = datetime.fromisoformat(landlord["billing_start_date"].replace("Z", "+00:00"))
            next_billing_date = billing_start + timedelta(days=30)
        
        return LandlordDashboardData(
            profile=LandlordProfile(**landlord),
            active_listings=active_listings,
            total_inquiries=total_inquiries,
            this_month_inquiries=this_month_inquiries,
            subscription_status=landlord["subscription_status"],
            days_remaining=days_remaining,
            next_billing_date=next_billing_date
        )
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")

@landlord_router.post("/payment/checkout")
async def create_checkout_session(package: PaymentPackage, request: Request):
    """Create Stripe checkout session for landlord subscription"""
    try:
        # Get landlord
        landlord = await db.landlords.find_one({"id": package.package_id})
        if not landlord:
            raise HTTPException(status_code=404, detail="Landlord not found")
        
        # Initialize Stripe
        host_url = str(request.base_url).rstrip('/')
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Calculate pricing
        plan = SubscriptionPlan(landlord["subscription_plan"])
        monthly_cost = calculate_monthly_cost(plan, package.apartment_count)
        
        # Create checkout session URLs
        success_url = f"{package.origin_url}/landlord/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{package.origin_url}/landlord/cancel"
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=monthly_cost,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "landlord_id": package.package_id,
                "plan": plan.value,
                "apartment_count": str(package.apartment_count),
                "type": "landlord_subscription"
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Store payment transaction
        transaction = PaymentTransaction(
            landlord_id=package.package_id,
            session_id=session.session_id,
            amount=monthly_cost,
            plan=plan,
            apartment_count=package.apartment_count,
            metadata=checkout_request.metadata
        )
        
        await db.payment_transactions.insert_one(transaction.dict())
        
        return PaymentSessionResponse(
            checkout_url=session.url,
            session_id=session.session_id,
            amount=monthly_cost,
            plan=plan.value
        )
        
    except Exception as e:
        logger.error(f"Checkout creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@landlord_router.get("/payment/status/{session_id}")
async def check_payment_status(session_id: str):
    """Check payment status and update subscription"""
    try:
        # Initialize Stripe
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        
        # Get checkout status
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Get transaction
        transaction = await db.payment_transactions.find_one({"session_id": session_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Update transaction status
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "payment_status": status.payment_status,
                    "stripe_status": status.status,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # If payment successful, activate subscription
        if status.payment_status == "paid" and transaction["payment_status"] != "paid":
            await activate_landlord_subscription(transaction["landlord_id"], transaction)
        
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount": status.amount_total / 100,  # Convert from cents
            "currency": status.currency
        }
        
    except Exception as e:
        logger.error(f"Payment status check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check payment status")

@landlord_router.post("/listings/submit")
async def submit_listing(landlord_id: str, listing: ListingSubmission):
    """Submit new apartment listing"""
    try:
        # Verify landlord exists and has active subscription
        landlord = await db.landlords.find_one({"id": landlord_id})
        if not landlord:
            raise HTTPException(status_code=404, detail="Landlord not found")
        
        if landlord["subscription_status"] not in ["trial", "active"]:
            raise HTTPException(status_code=403, detail="Active subscription required")
        
        # Check apartment limit for per-apartment plans
        plan = SubscriptionPlan(landlord["subscription_plan"])
        plan_config = PRICING_PLANS[plan]
        
        if plan_config["per_apartment"]:
            current_listings = await db.apartments.count_documents({
                "landlord_id": landlord_id,
                "available": True
            })
            
            if plan_config["max_apartments"] and current_listings >= plan_config["max_apartments"]:
                raise HTTPException(status_code=403, detail=f"Maximum {plan_config['max_apartments']} apartments allowed for {plan.value} plan")
        
        # Create apartment listing
        apartment_data = listing.dict()
        apartment_data.update({
            "id": str(uuid.uuid4()),
            "landlord_id": landlord_id,
            "available": True,
            "featured": plan in [SubscriptionPlan.FEATURED, SubscriptionPlan.PREMIUM, SubscriptionPlan.PORTFOLIO, SubscriptionPlan.ENTERPRISE],
            "priority": 2 if plan in [SubscriptionPlan.FEATURED, SubscriptionPlan.PREMIUM] else 1,
            "verified": plan in [SubscriptionPlan.FEATURED, SubscriptionPlan.PREMIUM, SubscriptionPlan.PORTFOLIO, SubscriptionPlan.ENTERPRISE],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "contact_info": {
                "email": landlord["email"],
                "phone": landlord.get("phone", ""),
                "company": landlord.get("company_name", landlord["name"])
            }
        })
        
        # Insert apartment
        await db.apartments.insert_one(apartment_data)
        
        # Send listing confirmation email
        try:
            await send_listing_confirmation_email(landlord, apartment_data)
        except Exception as e:
            logger.error(f"Failed to send listing confirmation: {str(e)}")
        
        return {
            "message": "Listing submitted successfully",
            "apartment_id": apartment_data["id"],
            "featured": apartment_data["featured"],
            "priority": apartment_data["priority"]
        }
        
    except Exception as e:
        logger.error(f"Listing submission error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit listing")

@landlord_router.get("/pricing")
async def get_pricing_plans():
    """Get all available pricing plans"""
    return {
        "plans": PRICING_PLANS,
        "trial_days": 14,
        "features_comparison": {
            "small_landlords": [SubscriptionPlan.BASIC, SubscriptionPlan.FEATURED, SubscriptionPlan.PREMIUM],
            "large_managers": [SubscriptionPlan.PORTFOLIO, SubscriptionPlan.ENTERPRISE]
        }
    }

# Helper Functions
async def activate_landlord_subscription(landlord_id: str, transaction: dict):
    """Activate landlord subscription after successful payment"""
    billing_start = datetime.utcnow()
    billing_end = billing_start + timedelta(days=30)
    
    await db.landlords.update_one(
        {"id": landlord_id},
        {
            "$set": {
                "subscription_status": SubscriptionStatus.ACTIVE.value,
                "billing_start_date": billing_start.isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        }
    )
    
    # Create billing record
    billing = SubscriptionBilling(
        landlord_id=landlord_id,
        plan=SubscriptionPlan(transaction["plan"]),
        apartment_count=transaction["apartment_count"],
        monthly_rate=transaction["amount"],
        billing_cycle_start=billing_start,
        billing_cycle_end=billing_end,
        payment_status="paid"
    )
    
    await db.subscription_billing.insert_one(billing.dict())

async def send_welcome_email(landlord: LandlordProfile):
    """Send welcome email to new landlord"""
    subject = f"Welcome to NoFeePlaces.com Landlord Portal - {landlord.name}"
    
    plan_config = PRICING_PLANS[landlord.subscription_plan]
    features_list = "\n".join([f"• {feature}" for feature in plan_config["features"]])
    
    html_content = f"""
    <h2>Welcome to NoFeePlaces.com Landlord Portal!</h2>
    
    <p>Dear {landlord.name},</p>
    
    <p>Thank you for joining NoFeePlaces.com! Your account has been created with the <strong>{plan_config["name"]}</strong> plan.</p>
    
    <h3>Your 14-Day Free Trial Includes:</h3>
    {features_list}
    
    <p><strong>Trial Period:</strong> 14 days (ends {landlord.trial_end_date.strftime('%B %d, %Y')})</p>
    
    <p>During your trial, you can list apartments and start receiving inquiries immediately. No payment required until your trial ends!</p>
    
    <p><strong>Next Steps:</strong></p>
    <ol>
        <li>Complete your profile setup</li>
        <li>Upload your first apartment listing</li>
        <li>Start receiving tenant inquiries</li>
    </ol>
    
    <p>If you have any questions, reply to this email or contact our support team.</p>
    
    <p>Best regards,<br>The NoFeePlaces.com Team</p>
    """
    
    await email_service.send_email_async(
        to_email=landlord.email,
        subject=subject,
        html_content=html_content
    )

async def send_listing_confirmation_email(landlord: dict, apartment: dict):
    """Send listing confirmation email"""
    subject = f"Listing Confirmed: {apartment['title']}"
    
    html_content = f"""
    <h2>Your Apartment Listing is Live!</h2>
    
    <p>Dear {landlord['name']},</p>
    
    <p>Your apartment listing has been successfully posted to NoFeePlaces.com:</p>
    
    <p><strong>{apartment['title']}</strong><br>
    📍 {apartment['address']}<br>
    💰 ${apartment['price']:,.0f}/month<br>
    🛏️ {apartment['bedrooms']} bedroom(s)</p>
    
    <p>Your listing is now visible to thousands of apartment seekers in NYC!</p>
    
    <p>You'll receive email notifications when prospective tenants contact you about this listing.</p>
    
    <p>Best regards,<br>The NoFeePlaces.com Team</p>
    """
    
    await email_service.send_email_async(
        to_email=landlord['email'],
        subject=subject,
        html_content=html_content
    )