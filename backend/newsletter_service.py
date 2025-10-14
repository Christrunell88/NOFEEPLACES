"""
Newsletter Service for NoFeePlaces.com
Handles newsletter subscriptions, email campaigns, and lead magnets
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from email_service import email_service
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class NewsletterService:
    def __init__(self):
        load_dotenv('/app/backend/.env')
        MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces')
        db_name = os.environ.get('DB_NAME', 'nofeeplaces')
        
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[db_name]
    
    async def subscribe_to_newsletter(self, email: str, full_name: str = "", 
                                    source: str = "website", 
                                    preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Subscribe user to newsletter"""
        try:
            # Check if email already exists
            existing = await self.db.newsletter_subscribers.find_one({"email": email})
            
            if existing:
                # Update existing subscription
                await self.db.newsletter_subscribers.update_one(
                    {"email": email},
                    {
                        "$set": {
                            "updated_at": datetime.now(timezone.utc),
                            "active": True,
                            "source": source,
                            "preferences": preferences or {}
                        }
                    }
                )
                return {"status": "updated", "message": "Subscription updated successfully"}
            
            # Create new subscription
            subscriber = {
                "email": email,
                "full_name": full_name,
                "source": source,
                "preferences": preferences or {
                    "weekly_digest": True,
                    "new_listings": True,
                    "market_reports": True,
                    "tips_guides": True
                },
                "active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "confirmed": False,
                "confirmation_token": None
            }
            
            await self.db.newsletter_subscribers.insert_one(subscriber)
            
            # Send welcome newsletter email
            await self._send_newsletter_welcome(email, full_name, source)
            
            logger.info(f"New newsletter subscriber: {email} from {source}")
            
            return {"status": "success", "message": "Successfully subscribed to newsletter"}
            
        except Exception as e:
            logger.error(f"Newsletter subscription failed for {email}: {str(e)}")
            return {"status": "error", "message": "Subscription failed"}
    
    async def _send_newsletter_welcome(self, email: str, name: str, source: str):
        """Send welcome email to newsletter subscribers"""
        subject = "🏙️ Welcome to NYC's Premier No Fee Apartment Newsletter!"
        
        html_content = self._get_newsletter_welcome_template(name, source)
        
        success = await email_service.send_email_async(
            to_email=email,
            subject=subject,
            html_content=html_content
        )
        
        if success:
            logger.info(f"Newsletter welcome email sent to {email}")
        
        return success
    
    def _get_newsletter_welcome_template(self, name: str, source: str) -> str:
        """Generate newsletter welcome email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to NoFeePlaces.com Newsletter</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: bold; }}
                .content {{ padding: 40px 30px; }}
                .highlight-box {{ background: #f0f4ff; border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .feature-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
                .feature-card {{ background: #f8fafc; padding: 20px; border-radius: 8px; text-align: center; }}
                .feature-icon {{ font-size: 32px; margin-bottom: 10px; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                .footer {{ background: #1a202c; color: #a0aec0; padding: 30px; text-align: center; }}
                .footer a {{ color: #667eea; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📧 Welcome to Our Newsletter!</h1>
                    <p>Your VIP Access to NYC's Best No Fee Apartments</p>
                </div>
                
                <div class="content">
                    <div class="highlight-box">
                        <h2>Hi{' ' + name if name else ''}! 🎉</h2>
                        <p>Thank you for subscribing to the NoFeePlaces.com newsletter! You're now part of our exclusive community of smart NYC renters who save thousands on broker fees.</p>
                    </div>
                    
                    <h3>What You'll Get Every Week:</h3>
                    <div class="feature-grid">
                        <div class="feature-card">
                            <div class="feature-icon">🏠</div>
                            <h4>New Listings First</h4>
                            <p>Get notified about new no fee apartments before they hit the public listings</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">📊</div>
                            <h4>Market Reports</h4>
                            <p>Weekly insights on NYC rental trends, pricing, and neighborhood updates</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">💡</div>
                            <h4>Expert Tips</h4>
                            <p>Insider strategies for apartment hunting, negotiating, and avoiding scams</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🎯</div>
                            <h4>Exclusive Deals</h4>
                            <p>Special promotions and early access to premium apartment listings</p>
                        </div>
                    </div>
                    
                    <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px; margin: 30px 0;">
                        <h4 style="color: #92400e; margin: 0 0 10px 0;">🎁 Exclusive Subscriber Benefits:</h4>
                        <ul style="color: #92400e; margin: 0; padding-left: 20px;">
                            <li>Early access to new no fee apartment listings</li>
                            <li>Free downloadable NYC neighborhood guides</li>
                            <li>Priority customer support for all inquiries</li>
                            <li>Invitation to exclusive virtual apartment tours</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 40px 0;">
                        <a href="https://nofeeplaces.com/apartments" class="cta-button">Browse 316+ No Fee Apartments</a>
                    </div>
                    
                    <div style="background: #f0fdf4; border: 1px solid #10b981; border-radius: 8px; padding: 20px; margin: 30px 0;">
                        <h4 style="color: #047857; margin: 0 0 10px 0;">📅 Coming This Week:</h4>
                        <ul style="color: #047857; margin: 0; padding-left: 20px;">
                            <li><strong>Monday:</strong> Hell's Kitchen Market Update - 19+ new listings</li>
                            <li><strong>Wednesday:</strong> Upper West Side Spotlight - Best deals near Columbia</li>
                            <li><strong>Friday:</strong> Weekend Open House Schedule + Virtual Tours</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <h4>Stay Connected</h4>
                    <p>📧 Questions? Reply to this email or contact us at placesfirm@gmail.com</p>
                    <p>📞 +1 (646) 408-8048 | 🌐 <a href="https://nofeeplaces.com">NoFeePlaces.com</a></p>
                    
                    <p style="font-size: 12px; color: #718096; margin-top: 30px;">
                        You subscribed via {source} • <a href="https://nofeeplaces.com/unsubscribe">Unsubscribe</a> • <a href="https://nofeeplaces.com/preferences">Email Preferences</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def get_subscriber_count(self) -> int:
        """Get total active subscriber count"""
        return await self.db.newsletter_subscribers.count_documents({"active": True})
    
    async def get_subscribers_by_source(self) -> Dict[str, int]:
        """Get subscriber breakdown by source"""
        pipeline = [
            {"$match": {"active": True}},
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        results = await self.db.newsletter_subscribers.aggregate(pipeline).to_list(length=None)
        return {result["_id"]: result["count"] for result in results}

# Global newsletter service instance
newsletter_service = NewsletterService()