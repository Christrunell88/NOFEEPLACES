from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import os
from datetime import datetime, timedelta
import json
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Emergent LLM integration
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    EMERGENT_AVAILABLE = True
except ImportError:
    EMERGENT_AVAILABLE = False
    print("⚠️ Emergent integrations not available. Install emergentintegrations package.")

# Pydantic models for marketing automation
class LeadModel(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    apartment_interest: Optional[str] = None
    budget_range: Optional[str] = None
    preferred_neighborhood: Optional[str] = None
    move_date: Optional[str] = None
    source: Optional[str] = "website"
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None

class EmailCampaignModel(BaseModel):
    subject: str
    template_type: str
    personalization: Optional[Dict[str, Any]] = {}
    send_immediately: bool = False
    scheduled_time: Optional[datetime] = None

class MarketingAutomationService:
    def __init__(self):
        self.leads_database = []  # In production, use proper database
        self.email_templates = self.load_email_templates()
        self.llm_chat = self.initialize_llm() if EMERGENT_AVAILABLE else None
        
        # Email configuration
        self.email_config = {
            'host': os.getenv('EMAIL_HOST', 'smtp.gmail.com'),
            'port': int(os.getenv('EMAIL_PORT', 587)),
            'user': os.getenv('EMAIL_USER'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'use_tls': os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
        }
    
    def initialize_llm(self):
        """Initialize Emergent LLM for content generation"""
        try:
            api_key = os.getenv('EMERGENT_LLM_KEY')
            if not api_key:
                print("⚠️ EMERGENT_LLM_KEY not found in environment")
                return None
                
            chat = LlmChat(
                api_key=api_key,
                session_id="nofeeplaces_marketing",
                system_message="""You are a professional NYC real estate marketing expert for NoFeePlaces.com. 
                Create compelling, personalized email content for apartment seekers looking for no-fee rentals in NYC. 
                Focus on:
                - NYC neighborhoods and apartment types
                - No broker fee value proposition
                - Urgency and scarcity
                - Personal connection and local expertise
                - Clear call-to-actions
                
                Always maintain a professional yet friendly tone."""
            )
            chat.with_model("openai", "gpt-4o-mini")
            return chat
        except Exception as e:
            print(f"❌ Failed to initialize LLM: {e}")
            return None
    
    def load_email_templates(self):
        """Load email templates for different scenarios"""
        return {
            'welcome': {
                'subject': 'Welcome to NoFeePlaces.com - Your NYC No-Fee Apartment Journey Starts Here!',
                'template': '''
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #3B82F6, #8B5CF6); padding: 20px; text-align: center;">
                        <h1 style="color: white; margin: 0;">Welcome to NoFeePlaces.com!</h1>
                        <p style="color: white; margin: 10px 0 0 0;">NYC's #1 Platform for No-Fee Apartments</p>
                    </div>
                    
                    <div style="padding: 30px 20px;">
                        <h2 style="color: #1F2937;">Hi {name},</h2>
                        
                        <p>Welcome to the future of NYC apartment hunting! 🏠</p>
                        
                        <p>You've just joined thousands of smart renters who refuse to pay unnecessary broker fees. Here's what you can expect:</p>
                        
                        <div style="background: #F3F4F6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="color: #1F2937; margin-top: 0;">✅ What You Get:</h3>
                            <ul style="color: #4B5563;">
                                <li><strong>1000+ Verified No-Fee Apartments</strong> across Manhattan, Brooklyn, Queens</li>
                                <li><strong>Direct Owner Contact</strong> - No middleman fees</li>
                                <li><strong>Save $3,000-$8,000+</strong> in broker fees</li>
                                <li><strong>Personalized Apartment Alerts</strong> based on your preferences</li>
                                <li><strong>Expert NYC Guidance</strong> from Chris Trunell</li>
                            </ul>
                        </div>
                        
                        <div style="background: #EBF8FF; border-left: 4px solid #3B82F6; padding: 20px; margin: 20px 0;">
                            <h3 style="color: #1F2937; margin-top: 0;">🎯 Your Preferences:</h3>
                            <p><strong>Budget:</strong> {budget_range}</p>
                            <p><strong>Preferred Area:</strong> {preferred_neighborhood}</p>
                            <p><strong>Move-in Date:</strong> {move_date}</p>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://nofeeplaces.com/apartments" 
                               style="background: #3B82F6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                                Browse No-Fee Apartments Now
                            </a>
                        </div>
                        
                        <p><strong>Need immediate assistance?</strong></p>
                        <p>📞 Call/Text: <a href="tel:646-408-8048">(646) 408-8048</a></p>
                        <p>📧 Email: <a href="mailto:chris@places.nyc">chris@places.nyc</a></p>
                        <p><em>Response time: Under 2 hours</em></p>
                        
                        <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 30px 0;">
                        
                        <p style="color: #6B7280; font-size: 14px;">
                            Best regards,<br>
                            <strong>Chris Trunell</strong><br>
                            NYC No-Fee Apartment Specialist<br>
                            NoFeePlaces.com
                        </p>
                    </div>
                </body>
                </html>
                '''
            },
            'apartment_alert': {
                'subject': '🏠 New No-Fee Apartment Alert: {apartment_details}',
                'template': '''
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #EF4444; padding: 20px; text-align: center;">
                        <h1 style="color: white; margin: 0;">🚨 New Apartment Alert!</h1>
                    </div>
                    
                    <div style="padding: 20px;">
                        <h2>Hi {name},</h2>
                        
                        <p>A new no-fee apartment matching your criteria just became available!</p>
                        
                        <div style="border: 2px solid #EF4444; border-radius: 8px; padding: 20px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #1F2937;">{apartment_title}</h3>
                            <p><strong>📍 Location:</strong> {location}</p>
                            <p><strong>💰 Rent:</strong> ${rent}/month</p>
                            <p><strong>🛏️ Bedrooms:</strong> {bedrooms}</p>
                            <p><strong>🚫 Broker Fee:</strong> $0 (Save ${broker_fee_saved}!)</p>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{apartment_url}" 
                               style="background: #EF4444; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                                View Apartment Details
                            </a>
                        </div>
                        
                        <p style="color: #EF4444; font-weight: bold;">⏰ Act Fast: No-fee apartments get snatched up quickly!</p>
                        
                        <p>Questions? Call me directly: <a href="tel:646-408-8048">(646) 408-8048</a></p>
                    </div>
                </body>
                </html>
                '''
            },
            'follow_up': {
                'subject': 'Still Looking for Your Perfect NYC Apartment? 🏠',
                'template': '''
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="padding: 20px;">
                        <h2>Hi {name},</h2>
                        
                        <p>I noticed you've been browsing no-fee apartments on NoFeePlaces.com - how's your search going?</p>
                        
                        <p>As NYC's no-fee apartment specialist, I wanted to personally reach out to see if I can help you find your perfect place faster.</p>
                        
                        <div style="background: #F9FAFB; border-left: 4px solid #3B82F6; padding: 20px; margin: 20px 0;">
                            <h3 style="margin-top: 0;">🎯 Based on your preferences:</h3>
                            <ul>
                                <li><strong>Budget:</strong> {budget_range}</li>
                                <li><strong>Area:</strong> {preferred_neighborhood}</li>
                                <li><strong>Timeline:</strong> {move_date}</li>
                            </ul>
                        </div>
                        
                        <p>I can help you:</p>
                        <ul>
                            <li>✅ Get priority access to new listings</li>
                            <li>✅ Schedule same-day viewings</li>
                            <li>✅ Navigate the application process</li>
                            <li>✅ Negotiate terms with landlords</li>
                        </ul>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="tel:646-408-8048" 
                               style="background: #10B981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                                📞 Let's Talk - Call Now
                            </a>
                        </div>
                        
                        <p>Or reply to this email with your questions!</p>
                        
                        <p>
                            Best,<br>
                            <strong>Chris Trunell</strong><br>
                            (646) 408-8048
                        </p>
                    </div>
                </body>
                </html>
                '''
            }
        }
    
    async def generate_personalized_content(self, lead_data: Dict[str, Any], content_type: str) -> str:
        """Generate personalized content using Emergent LLM"""
        if not self.llm_chat:
            return self.get_fallback_content(content_type)
        
        try:
            prompt = f"""
            Create a personalized email {content_type} for a potential NYC apartment renter with these details:
            
            Name: {lead_data.get('name', 'there')}
            Budget: {lead_data.get('budget_range', 'Not specified')}
            Preferred Neighborhood: {lead_data.get('preferred_neighborhood', 'NYC')}
            Move Date: {lead_data.get('move_date', 'ASAP')}
            Source: {lead_data.get('source', 'website')}
            
            Requirements:
            - Write as Chris Trunell from NoFeePlaces.com
            - Focus on no broker fees and savings
            - Include specific NYC neighborhood insights
            - Create urgency but stay professional
            - Include call-to-action
            - Keep under 300 words
            - Format as plain text (no HTML)
            
            Content type: {content_type}
            """
            
            user_message = UserMessage(text=prompt)
            response = await self.llm_chat.send_message(user_message)
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ LLM content generation failed: {e}")
            return self.get_fallback_content(content_type)
    
    def get_fallback_content(self, content_type: str) -> str:
        """Fallback content when LLM is not available"""
        fallback_content = {
            'welcome': "Welcome to NoFeePlaces.com! We're excited to help you find your perfect no-fee apartment in NYC. Browse our listings and save thousands on broker fees!",
            'follow_up': "Still searching for your NYC apartment? Let me help you find the perfect no-fee place. Call Chris at (646) 408-8048 for personalized assistance!",
            'apartment_alert': "New no-fee apartment available matching your criteria! Don't miss out on this opportunity to save on broker fees."
        }
        return fallback_content.get(content_type, "Thank you for your interest in NoFeePlaces.com!")
    
    async def capture_lead(self, lead_data: LeadModel) -> Dict[str, Any]:
        """Capture and process new lead"""
        try:
            # Add timestamp and generate ID
            lead_dict = lead_data.dict()
            lead_dict['id'] = f"lead_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.leads_database)}"
            lead_dict['created_at'] = datetime.now().isoformat()
            lead_dict['status'] = 'new'
            
            # Store lead (in production, use proper database)
            self.leads_database.append(lead_dict)
            
            print(f"📧 New lead captured: {lead_data.email}")
            
            return {
                'success': True,
                'lead_id': lead_dict['id'],
                'message': 'Lead captured successfully'
            }
            
        except Exception as e:
            print(f"❌ Failed to capture lead: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def send_welcome_email(self, lead_data: Dict[str, Any]) -> bool:
        """Send personalized welcome email"""
        try:
            # Generate personalized content
            personalized_content = await self.generate_personalized_content(lead_data, 'welcome')
            
            # Prepare email
            template = self.email_templates['welcome']['template']
            
            # Fill template with lead data
            email_content = template.format(
                name=lead_data.get('name', 'there'),
                budget_range=lead_data.get('budget_range', 'Any budget'),
                preferred_neighborhood=lead_data.get('preferred_neighborhood', 'NYC'),
                move_date=lead_data.get('move_date', 'ASAP'),
                personalized_content=personalized_content
            )
            
            # Send email
            await self.send_email(
                to_email=lead_data['email'],
                subject=self.email_templates['welcome']['subject'],
                html_content=email_content,
                lead_data=lead_data
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send welcome email: {e}")
            return False
    
    async def send_email(self, to_email: str, subject: str, html_content: str, lead_data: Dict[str, Any] = None):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"Chris Trunell - NoFeePlaces.com <{self.email_config['user']}>"
            msg['To'] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.email_config['host'], self.email_config['port']) as server:
                if self.email_config['use_tls']:
                    server.starttls()
                server.login(self.email_config['user'], self.email_config['password'])
                server.send_message(msg)
            
            print(f"✅ Email sent to {to_email}: {subject}")
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            raise
    
    async def create_apartment_alert(self, apartment_data: Dict[str, Any], target_leads: List[Dict[str, Any]]):
        """Create and send apartment alerts to matching leads"""
        for lead in target_leads:
            try:
                # Customize apartment details for this lead
                alert_content = self.email_templates['apartment_alert']['template'].format(
                    name=lead.get('name', 'there'),
                    apartment_title=f"{apartment_data['bedrooms']}BR in {apartment_data['neighborhood']}",
                    location=f"{apartment_data['neighborhood']}, {apartment_data['borough']}",
                    rent=apartment_data['rent'],
                    bedrooms=apartment_data['bedrooms'],
                    broker_fee_saved=int(apartment_data['rent'] * 0.15 * 12),  # 15% annual rent
                    apartment_url=f"https://nofeeplaces.com/apartments/{apartment_data['id']}"
                )
                
                subject = self.email_templates['apartment_alert']['subject'].format(
                    apartment_details=f"{apartment_data['bedrooms']}BR {apartment_data['neighborhood']} - ${apartment_data['rent']}"
                )
                
                await self.send_email(
                    to_email=lead['email'],
                    subject=subject,
                    html_content=alert_content,
                    lead_data=lead
                )
                
            except Exception as e:
                print(f"❌ Failed to send apartment alert to {lead['email']}: {e}")
    
    async def send_follow_up_campaign(self, days_since_signup: int = 3):
        """Send follow-up emails to leads who haven't converted"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_since_signup)
            
            # Find leads to follow up with
            target_leads = [
                lead for lead in self.leads_database
                if datetime.fromisoformat(lead['created_at']) <= cutoff_date
                and lead['status'] == 'new'
            ]
            
            for lead in target_leads:
                # Generate personalized follow-up content
                personalized_content = await self.generate_personalized_content(lead, 'follow_up')
                
                # Send follow-up email
                follow_up_content = self.email_templates['follow_up']['template'].format(
                    name=lead.get('name', 'there'),
                    budget_range=lead.get('budget_range', 'Any budget'),
                    preferred_neighborhood=lead.get('preferred_neighborhood', 'NYC'),
                    move_date=lead.get('move_date', 'ASAP'),
                    personalized_content=personalized_content
                )
                
                await self.send_email(
                    to_email=lead['email'],
                    subject=self.email_templates['follow_up']['subject'],
                    html_content=follow_up_content,
                    lead_data=lead
                )
                
                # Update lead status
                lead['status'] = 'followed_up'
                
            print(f"📧 Follow-up campaign sent to {len(target_leads)} leads")
            
        except Exception as e:
            print(f"❌ Follow-up campaign failed: {e}")
    
    def get_lead_analytics(self) -> Dict[str, Any]:
        """Get marketing analytics and lead statistics"""
        total_leads = len(self.leads_database)
        
        if total_leads == 0:
            return {
                'total_leads': 0,
                'conversion_rate': 0,
                'top_sources': [],
                'top_neighborhoods': []
            }
        
        # Calculate metrics
        sources = [lead.get('source', 'unknown') for lead in self.leads_database]
        neighborhoods = [lead.get('preferred_neighborhood', 'unknown') for lead in self.leads_database]
        
        from collections import Counter
        
        return {
            'total_leads': total_leads,
            'new_leads': len([l for l in self.leads_database if l['status'] == 'new']),
            'followed_up': len([l for l in self.leads_database if l['status'] == 'followed_up']),
            'top_sources': dict(Counter(sources).most_common(5)),
            'top_neighborhoods': dict(Counter(neighborhoods).most_common(5)),
            'recent_leads': self.leads_database[-10:] if self.leads_database else []
        }

# Initialize the marketing automation service
marketing_service = MarketingAutomationService()