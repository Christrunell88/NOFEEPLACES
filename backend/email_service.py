"""
Email Service for NoFeePlaces.com
Handles all email operations including welcome emails, confirmations, and notifications.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from jinja2 import Template
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('EMAIL_PORT', '587'))
        self.email_user = os.environ.get('EMAIL_USER', 'placesfirm@gmail.com')
        self.email_password = os.environ.get('EMAIL_PASSWORD', '')
        self.use_tls = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Validate configuration
        if not self.email_password:
            logger.warning("Email password not configured. Email sending will fail.")
    
    async def send_email_async(self, to_email: str, subject: str, html_content: str, 
                              text_content: Optional[str] = None, 
                              attachments: Optional[List[Dict]] = None) -> bool:
        """Send email asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self._send_email_sync, 
            to_email, subject, html_content, text_content, attachments
        )
    
    def _send_email_sync(self, to_email: str, subject: str, html_content: str, 
                        text_content: Optional[str] = None, 
                        attachments: Optional[List[Dict]] = None) -> bool:
        """Send email synchronously"""
        try:
            # Create message container
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"NoFeePlaces.com <{self.email_user}>"
            msg['To'] = to_email
            msg['Reply-To'] = self.email_user
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    if attachment.get('type') == 'image' and attachment.get('data'):
                        img = MIMEImage(attachment['data'])
                        img.add_header('Content-ID', f"<{attachment.get('cid', 'image')}>")
                        msg.attach(img)
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls(context=ssl.create_default_context())
            
            server.login(self.email_user, self.email_password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_welcome_email(self, user_email: str, user_name: str, 
                                signup_method: str = "website") -> bool:
        """Send welcome email to new users"""
        subject = "Welcome to NoFeePlaces.com - Your NYC No Fee Apartment Journey Starts Here! 🏙️"
        
        # Get welcome email template
        html_content = self._get_welcome_email_template(user_name, signup_method)
        text_content = self._get_welcome_email_text(user_name, signup_method)
        
        success = await self.send_email_async(user_email, subject, html_content, text_content)
        
        # Log email attempt
        await self._log_email_attempt(user_email, subject, "welcome", success)
        
        return success
    
    async def send_apartment_inquiry_confirmation(self, user_email: str, user_name: str, 
                                                apartment_title: str, apartment_id: str) -> bool:
        """Send confirmation email when user inquires about an apartment"""
        subject = f"Your inquiry about {apartment_title} - NoFeePlaces.com"
        
        html_content = self._get_inquiry_confirmation_template(user_name, apartment_title, apartment_id)
        text_content = self._get_inquiry_confirmation_text(user_name, apartment_title)
        
        success = await self.send_email_async(user_email, subject, html_content, text_content)
        
        await self._log_email_attempt(user_email, subject, "inquiry_confirmation", success)
        
        return success
    
    async def send_contact_notification(self, contact_request: Dict[str, Any]) -> bool:
        """Send notification email when someone contacts about an apartment"""
        subject = f"New Contact Request - {contact_request.get('apartment_title', 'NoFeePlaces.com')}"
        
        html_content = self._get_contact_notification_template(contact_request)
        
        # Send to admin email
        admin_email = self.email_user
        success = await self.send_email_async(admin_email, subject, html_content)
        
        await self._log_email_attempt(admin_email, subject, "contact_notification", success)
        
        return success
    
    def _get_welcome_email_template(self, user_name: str, signup_method: str) -> str:
        """Generate HTML welcome email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to NoFeePlaces.com</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: bold; }}
                .header p {{ color: #e2e8f0; margin: 10px 0 0 0; font-size: 16px; }}
                .content {{ padding: 40px 30px; }}
                .welcome-box {{ background: #f0f4ff; border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .feature-list {{ margin: 30px 0; }}
                .feature-item {{ display: flex; align-items: flex-start; margin: 15px 0; }}
                .feature-icon {{ background: #10b981; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; margin-right: 15px; font-size: 14px; flex-shrink: 0; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                .stats {{ background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; text-align: center; }}
                .stat-item {{ background: white; padding: 15px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
                .stat-number {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .stat-label {{ font-size: 12px; color: #64748b; margin-top: 5px; }}
                .footer {{ background: #1a202c; color: #a0aec0; padding: 30px; text-align: center; }}
                .footer a {{ color: #667eea; text-decoration: none; }}
                .social-links {{ margin: 20px 0; }}
                .social-links a {{ display: inline-block; margin: 0 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏙️ Welcome to NoFeePlaces.com!</h1>
                    <p>NYC's Premier No Fee Apartment Platform</p>
                </div>
                
                <div class="content">
                    <div class="welcome-box">
                        <h2>Hi {user_name}! 👋</h2>
                        <p>Welcome to the future of NYC apartment hunting! You've joined thousands of smart renters who choose to save money on broker fees.</p>
                    </div>
                    
                    <p>Thank you for signing up via <strong>{signup_method.title()}</strong>. You now have access to our complete inventory of no fee apartments across Manhattan, Brooklyn, and Queens.</p>
                    
                    <div class="stats">
                        <h3>What You Get Access To:</h3>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-number">316+</div>
                                <div class="stat-label">No Fee Apartments</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">$3K-8K</div>
                                <div class="stat-label">Average Savings</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">3</div>
                                <div class="stat-label">NYC Boroughs</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">24/7</div>
                                <div class="stat-label">Support</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="feature-list">
                        <h3>Your Benefits Include:</h3>
                        <div class="feature-item">
                            <div class="feature-icon">✓</div>
                            <div>
                                <strong>Full Address Access</strong><br>
                                See complete apartment addresses and contact information
                            </div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon">✓</div>
                            <div>
                                <strong>AI-Powered Search</strong><br>
                                Smart recommendations based on your preferences
                            </div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon">✓</div>
                            <div>
                                <strong>Direct Landlord Connections</strong><br>
                                Skip the middleman and contact building management directly
                            </div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon">✓</div>
                            <div>
                                <strong>Instant Alerts</strong><br>
                                Get notified when new apartments match your criteria
                            </div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon">✓</div>
                            <div>
                                <strong>Professional Photography</strong><br>
                                High-quality images and virtual tours
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 40px 0;">
                        <a href="https://nofeeplaces.com/apartments" class="cta-button">Start Browsing Apartments</a>
                    </div>
                    
                    <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px; margin: 30px 0;">
                        <h4 style="color: #92400e; margin: 0 0 10px 0;">💡 Pro Tips for Success:</h4>
                        <ul style="color: #92400e; margin: 0; padding-left: 20px;">
                            <li>Browse during weekdays for the best selection</li>
                            <li>Have your documents ready (pay stubs, bank statements)</li>
                            <li>Act fast - no fee apartments get snatched up quickly!</li>
                            <li>Check our blog for NYC apartment hunting tips</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <h4>Need Help Getting Started?</h4>
                    <p>Our team is here to help you find your perfect NYC apartment.</p>
                    <p>📧 <a href="mailto:placesfirm@gmail.com">placesfirm@gmail.com</a> | 📞 <a href="tel:+16464088048">+1 (646) 408-8048</a></p>
                    
                    <div class="social-links">
                        <a href="https://nofeeplaces.com">Website</a> |
                        <a href="https://nofeeplaces.com/blog">Blog</a> |
                        <a href="https://nofeeplaces.com/about">About Us</a>
                    </div>
                    
                    <p style="font-size: 12px; color: #718096; margin-top: 30px;">
                        © 2025 NoFeePlaces.com - NYC's Premier No Fee Apartment Platform<br>
                        You're receiving this email because you signed up for NoFeePlaces.com
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_welcome_email_text(self, user_name: str, signup_method: str) -> str:
        """Generate plain text welcome email"""
        return f"""
Welcome to NoFeePlaces.com, {user_name}!

Thank you for signing up via {signup_method.title()}. You now have access to 316+ no fee apartments across NYC.

Your Benefits:
- Full address access for all listings
- AI-powered apartment search
- Direct landlord connections
- Save $3,000-$8,000 on broker fees
- Professional photography and virtual tours

Get Started: https://nofeeplaces.com/apartments

Need help? Contact us:
Email: placesfirm@gmail.com
Phone: +1 (646) 408-8048

Happy apartment hunting!
The NoFeePlaces.com Team
        """
    
    def _get_inquiry_confirmation_template(self, user_name: str, apartment_title: str, apartment_id: str) -> str:
        """Generate inquiry confirmation email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Inquiry Confirmation - NoFeePlaces.com</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ padding: 30px; }}
                .apartment-info {{ background: #f0fdf4; border: 1px solid #10b981; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .next-steps {{ background: #fef3c7; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .cta-button {{ display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; }}
                .footer {{ background: #1a202c; color: #a0aec0; padding: 20px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Inquiry Confirmed!</h1>
                </div>
                
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    <p>We've received your inquiry and will get back to you within 24 hours!</p>
                    
                    <div class="apartment-info">
                        <h3>🏠 Apartment Details:</h3>
                        <p><strong>{apartment_title}</strong></p>
                        <p>Reference ID: {apartment_id}</p>
                    </div>
                    
                    <div class="next-steps">
                        <h4>⏰ What Happens Next:</h4>
                        <ol>
                            <li>We'll contact the building management</li>
                            <li>Schedule a viewing if you're interested</li>
                            <li>Provide application assistance if needed</li>
                        </ol>
                    </div>
                    
                    <p style="text-align: center;">
                        <a href="https://nofeeplaces.com/apartments/{apartment_id}" class="cta-button">View Apartment Details</a>
                    </p>
                </div>
                
                <div class="footer">
                    <p>Questions? Contact us at placesfirm@gmail.com or +1 (646) 408-8048</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_inquiry_confirmation_text(self, user_name: str, apartment_title: str) -> str:
        """Generate plain text inquiry confirmation"""
        return f"""
Hi {user_name},

Your inquiry about "{apartment_title}" has been confirmed!

We'll get back to you within 24 hours with next steps.

What happens next:
1. We'll contact the building management
2. Schedule a viewing if you're interested  
3. Provide application assistance if needed

Questions? Contact us:
Email: placesfirm@gmail.com
Phone: +1 (646) 408-8048

Thanks,
NoFeePlaces.com Team
        """
    
    def _get_contact_notification_template(self, contact: Dict[str, Any]) -> str:
        """Generate contact notification email for admin"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>New Contact Request - NoFeePlaces.com</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; }}
                .header {{ background: #dc2626; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 20px 0; }}
                .contact-details {{ background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .urgent {{ background: #fef2f2; border: 1px solid #fecaca; padding: 15px; border-radius: 6px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 New Contact Request</h1>
                </div>
                
                <div class="content">
                    <div class="urgent">
                        <strong>⚠️ URGENT:</strong> New apartment inquiry requires response within 24 hours
                    </div>
                    
                    <div class="contact-details">
                        <h3>Contact Information:</h3>
                        <p><strong>Name:</strong> {contact.get('name', 'Not provided')}</p>
                        <p><strong>Email:</strong> {contact.get('email', 'Not provided')}</p>
                        <p><strong>Phone:</strong> {contact.get('phone', 'Not provided')}</p>
                        <p><strong>Preferred Contact:</strong> {contact.get('preferred_contact', 'email').title()}</p>
                        <p><strong>Apartment ID:</strong> {contact.get('apartment_id', 'Not specified')}</p>
                        <p><strong>Date:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    </div>
                    
                    <div class="contact-details">
                        <h3>Message:</h3>
                        <p>{contact.get('message', 'No message provided')}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def _log_email_attempt(self, recipient: str, subject: str, 
                                email_type: str, success: bool) -> None:
        """Log email sending attempts for tracking"""
        # This would typically save to a database, for now just log
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"Email {status}: {email_type} to {recipient} - {subject}")
        
        # In a production system, you'd save this to a database:
        # await db.email_logs.insert_one({
        #     "recipient": recipient,
        #     "subject": subject,
        #     "email_type": email_type,
        #     "success": success,
        #     "timestamp": datetime.now(timezone.utc),
        #     "smtp_server": self.smtp_server
        # })


# Global email service instance
email_service = EmailService()