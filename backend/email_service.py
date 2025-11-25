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
        # Load environment variables when initializing
        from dotenv import load_dotenv
        load_dotenv('/app/backend/.env')
        
        self.smtp_server = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('EMAIL_PORT', '587'))
        self.email_user = os.environ.get('EMAIL_USER', 'placesfirm@gmail.com')
        self.email_password = os.environ.get('EMAIL_PASSWORD', '')
        self.use_tls = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'
        self.admin_email = os.environ.get('ADMIN_EMAIL', 'placesfirm@gmail.com')
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Log configuration for debugging
        logger.info(f"Email service initialized: {self.email_user} via {self.smtp_server}:{self.smtp_port}")
        
        # Validate configuration
        if not self.email_password:
            logger.warning("Email password not configured. Email sending will fail.")
        else:
            logger.info("Email password configured successfully")
    
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
                from email.mime.base import MIMEBase
                from email import encoders
                
                for attachment in attachments:
                    if attachment.get('type') == 'image' and attachment.get('data'):
                        img = MIMEImage(attachment['data'])
                        img.add_header('Content-ID', f"<{attachment.get('cid', 'image')}>")
                        msg.attach(img)
                    elif attachment.get('type') == 'calendar' and attachment.get('data'):
                        # Add calendar invite attachment
                        cal_part = MIMEBase('text', 'calendar', method='REQUEST', name=attachment.get('filename', 'invite.ics'))
                        cal_part.set_payload(attachment['data'])
                        encoders.encode_base64(cal_part)
                        cal_part.add_header('Content-Disposition', f'attachment; filename="{attachment.get("filename", "invite.ics")}"')
                        msg.attach(cal_part)
            
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
            <title>New Apartment Inquiry - NoFeePlaces.com</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 30px; }}
                .contact-details {{ background: #f0f4ff; padding: 25px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
                .business-info {{ background: #f0fdf4; border: 1px solid #10b981; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .contact-item {{ margin: 12px 0; display: flex; align-items: center; }}
                .contact-label {{ font-weight: 600; color: #374151; min-width: 140px; }}
                .contact-value {{ color: #111827; }}
                .message-box {{ background: #fffbeb; border: 1px solid #f59e0b; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ background: #f9fafb; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; color: #6b7280; }}
                .cta-button {{ display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 15px 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏠 New Apartment Inquiry</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">A potential tenant is interested in your listing</p>
                </div>
                
                <div class="content">
                    <div class="business-info">
                        <h3 style="margin: 0 0 15px 0; color: #065f46;">📈 Business Opportunity</h3>
                        <p style="margin: 0; color: #047857;">A qualified prospect has expressed interest in one of your no-fee apartment listings. Please respond within 24 hours to maintain service quality.</p>
                    </div>
                    
                    <div class="contact-details">
                        <h3 style="margin: 0 0 20px 0; color: #4338ca;">👤 Contact Information</h3>
                        <div class="contact-item">
                            <span class="contact-label">Name:</span>
                            <span class="contact-value">{contact.get('name', 'Not provided')}</span>
                        </div>
                        <div class="contact-item">
                            <span class="contact-label">Email:</span>
                            <span class="contact-value">{contact.get('email', 'Not provided')}</span>
                        </div>
                        <div class="contact-item">
                            <span class="contact-label">Phone:</span>
                            <span class="contact-value">{contact.get('phone', 'Not provided')}</span>
                        </div>
                        <div class="contact-item">
                            <span class="contact-label">Preferred Contact:</span>
                            <span class="contact-value">{contact.get('preferred_contact', 'email').title()}</span>
                        </div>
                        <div class="contact-item">
                            <span class="contact-label">Apartment ID:</span>
                            <span class="contact-value">{contact.get('apartment_id', 'Not specified')}</span>
                        </div>
                        <div class="contact-item">
                            <span class="contact-label">Inquiry Date:</span>
                            <span class="contact-value">{datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}</span>
                        </div>
                    </div>
                    
                    {f'''
                    <div class="message-box">
                        <h4 style="margin: 0 0 12px 0; color: #92400e;">💬 Prospect's Message:</h4>
                        <p style="margin: 0; color: #78350f; line-height: 1.6;">{contact.get('message', 'No message provided')}</p>
                    </div>
                    ''' if contact.get('message') else ''}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="mailto:{contact.get('email', '')}" class="cta-button">📧 Reply via Email</a>
                        {f'<a href="tel:{contact.get("phone", "")}" class="cta-button">📞 Call Now</a>' if contact.get('phone') else ''}
                    </div>
                </div>
                
                <div class="footer">
                    <p style="margin: 0 0 10px 0;"><strong>NoFeePlaces.com</strong> - NYC's Premier No Fee Apartment Platform</p>
                    <p style="margin: 0; font-size: 14px;">This inquiry was generated from your apartment listing. Please respond promptly to maintain high service standards.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_visitor_notification_template(self, ip_address: str, user_agent: str, timestamp: datetime) -> str:
        """Generate visitor notification email for admin"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>New Website Visitor - NoFeePlaces.com</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 30px; }}
                .visitor-details {{ background: #f0fdf4; padding: 25px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981; }}
                .stats-info {{ background: #eff6ff; border: 1px solid #3b82f6; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .visitor-item {{ margin: 12px 0; display: flex; align-items: center; }}
                .visitor-label {{ font-weight: 600; color: #374151; min-width: 120px; }}
                .visitor-value {{ color: #111827; }}
                .footer {{ background: #f9fafb; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; color: #6b7280; }}
                .cta-button {{ display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 15px 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>👋 New Website Visitor</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Someone just visited NoFeePlaces.com</p>
                </div>
                
                <div class="content">
                    <div class="stats-info">
                        <h3 style="margin: 0 0 15px 0; color: #1e40af;">📈 Visitor Activity</h3>
                        <p style="margin: 0; color: #1e3a8a;">A new visitor has arrived on your no-fee apartment platform. This could be a potential tenant searching for apartments!</p>
                    </div>
                    
                    <div class="visitor-details">
                        <h3 style="margin: 0 0 20px 0; color: #059669;">🔍 Visitor Information</h3>
                        <div class="visitor-item">
                            <span class="visitor-label">Visit Time:</span>
                            <span class="visitor-value">{timestamp.strftime('%B %d, %Y at %I:%M %p UTC')}</span>
                        </div>
                        <div class="visitor-item">
                            <span class="visitor-label">IP Address:</span>
                            <span class="visitor-value">{ip_address}</span>
                        </div>
                        <div class="visitor-item">
                            <span class="visitor-label">Browser/Device:</span>
                            <span class="visitor-value">{user_agent[:100]}{'...' if len(user_agent) > 100 else ''}</span>
                        </div>
                        <div class="visitor-item">
                            <span class="visitor-label">Platform:</span>
                            <span class="visitor-value">NoFeePlaces.com</span>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://login-rebuild.preview.emergentagent.com" class="cta-button">🏠 View Live Site</a>
                        <a href="https://analytics.google.com" class="cta-button">📊 Check Analytics</a>
                    </div>
                </div>
                
                <div class="footer">
                    <p style="margin: 0 0 10px 0;"><strong>NoFeePlaces.com</strong> - Visitor Tracking System</p>
                    <p style="margin: 0; font-size: 14px;">You're receiving this because visitor notifications are enabled. This helps you track real-time interest in your apartment listings.</p>
                </div>
            </div>
        </body>
        </html>
        """

    async def send_visitor_notification(self, ip_address: str, user_agent: str, timestamp: datetime) -> bool:
        """Send visitor notification email to admin"""
        try:
            subject = f"🏠 New Visitor on NoFeePlaces.com - {timestamp.strftime('%I:%M %p')}"
            
            html_content = self._get_visitor_notification_template(ip_address, user_agent, timestamp)
            
            text_content = f"""
New Website Visitor - NoFeePlaces.com

A new visitor has arrived on your no-fee apartment platform!

Visitor Details:
- Visit Time: {timestamp.strftime('%B %d, %Y at %I:%M %p UTC')}
- IP Address: {ip_address}
- Browser/Device: {user_agent}
- Platform: NoFeePlaces.com

This could be a potential tenant searching for apartments. Check your Google Analytics for more details about their activity.

---
NoFeePlaces.com Visitor Tracking System
"""
            
            success = await self.send_email_async(
                to_email=self.admin_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                await self._log_email_attempt(self.admin_email, subject, "visitor_notification", True)
                print(f"✅ Visitor notification sent for IP: {ip_address}")
            else:
                await self._log_email_attempt(self.admin_email, subject, "visitor_notification", False)
                print(f"❌ Failed to send visitor notification for IP: {ip_address}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error in send_visitor_notification: {str(e)}")
            await self._log_email_attempt(self.admin_email, "Visitor Notification", "visitor_notification", False)
            return False
    
    async def send_contact_email(self, to_email: str, subject: str, 
                               sender_name: str, sender_email: str, 
                               sender_phone: str, message: str, 
                               apartment_details: Optional[Dict] = None) -> bool:
        """Send contact form email from website visitors"""
        try:
            html_content = self._get_contact_email_template(
                sender_name, sender_email, sender_phone, message, apartment_details
            )
            
            text_content = self._get_contact_email_text(
                sender_name, sender_email, sender_phone, message, apartment_details
            )
            
            success = await self.send_email_async(
                to_email=to_email,
                subject=f"NoFeePlaces Contact: {subject}",
                html_content=html_content,
                text_content=text_content
            )
            
            await self._log_email_attempt(to_email, subject, "contact_form", success)
            return success
            
        except Exception as e:
            logger.error(f"Error sending contact email: {str(e)}")
            await self._log_email_attempt(to_email, subject, "contact_form", False)
            return False
    
    def _get_contact_email_template(self, sender_name: str, sender_email: str, 
                                  sender_phone: str, message: str, 
                                  apartment_details: Optional[Dict] = None) -> str:
        """Generate HTML contact email template"""
        apartment_section = ""
        if apartment_details:
            apartment_section = f"""
                <div style="background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #007bff;">
                    <h3 style="color: #007bff; margin: 0 0 10px 0;">Apartment Inquiry Details:</h3>
                    <p style="margin: 5px 0;"><strong>Property:</strong> {apartment_details.get('title', 'N/A')}</p>
                    {f'<p style="margin: 5px 0;"><strong>Neighborhood:</strong> {apartment_details.get("neighborhood", "N/A")}</p>' if apartment_details.get('neighborhood') else ''}
                    {f'<p style="margin: 5px 0;"><strong>Price:</strong> ${apartment_details.get("price", "N/A")}/month</p>' if apartment_details.get('price') else ''}
                    {f'<p style="margin: 5px 0;"><strong>Bedrooms:</strong> {apartment_details.get("bedrooms", "N/A")}</p>' if apartment_details.get('bedrooms') else ''}
                </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Contact Form Submission - NoFeePlaces.com</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">🏢 NoFeePlaces.com</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">New Contact Form Submission</p>
            </div>
            
            <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">Contact Information:</h2>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="margin: 8px 0;"><strong>👤 Name:</strong> {sender_name}</p>
                    <p style="margin: 8px 0;"><strong>📧 Email:</strong> <a href="mailto:{sender_email}" style="color: #007bff;">{sender_email}</a></p>
                    {f'<p style="margin: 8px 0;"><strong>📞 Phone:</strong> <a href="tel:{sender_phone}" style="color: #007bff;">{sender_phone}</a></p>' if sender_phone else ''}
                    <p style="margin: 8px 0;"><strong>⏰ Submitted:</strong> {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}</p>
                </div>
                
                {apartment_section}
                
                <h3 style="color: #333; margin-bottom: 15px;">💬 Message:</h3>
                <div style="background-color: #fff; border: 1px solid #e9ecef; padding: 20px; border-radius: 8px; white-space: pre-wrap;">
{message}
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e9ecef; text-align: center;">
                    <p style="color: #666; margin-bottom: 15px;">Ready to respond?</p>
                    <a href="mailto:{sender_email}?subject=Re: NoFeePlaces Inquiry" 
                       style="display: inline-block; background-color: #007bff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                        📧 Reply to {sender_name}
                    </a>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
                <p>This email was sent from NoFeePlaces.com contact form</p>
                <p>© {datetime.now().year} NoFeePlaces.com - NYC's Premier No-Fee Apartment Platform</p>
            </div>
        </body>
        </html>
        """
    
    def _get_contact_email_text(self, sender_name: str, sender_email: str, 
                              sender_phone: str, message: str, 
                              apartment_details: Optional[Dict] = None) -> str:
        """Generate plain text contact email"""
        apartment_section = ""
        if apartment_details:
            apartment_section = f"""
APARTMENT INQUIRY DETAILS:
Property: {apartment_details.get('title', 'N/A')}
{f"Neighborhood: {apartment_details.get('neighborhood', 'N/A')}" if apartment_details.get('neighborhood') else ''}
{f"Price: ${apartment_details.get('price', 'N/A')}/month" if apartment_details.get('price') else ''}
{f"Bedrooms: {apartment_details.get('bedrooms', 'N/A')}" if apartment_details.get('bedrooms') else ''}

"""
        
        return f"""
NoFeePlaces.com - New Contact Form Submission

CONTACT INFORMATION:
Name: {sender_name}
Email: {sender_email}
{f"Phone: {sender_phone}" if sender_phone else ''}
Submitted: {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}

{apartment_section}MESSAGE:
{message}

---
Reply directly to this email to respond to {sender_name}
© {datetime.now().year} NoFeePlaces.com - NYC's Premier No-Fee Apartment Platform
        """
    
    async def send_newsletter_welcome_email(self, email: str, name: str) -> bool:
        """Send welcome email to new newsletter subscriber"""
        try:
            subject = "Welcome to NoFeePlaces.com - NYC's Premier No-Fee Apartment Platform!"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Welcome to NoFeePlaces.com</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #14b8a6 0%, #0891b2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px;">
                    <h1 style="margin: 0; font-size: 28px;">🏢 Welcome to NoFeePlaces.com</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">NYC's Premier No-Fee Apartment Platform</p>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 10px; margin-top: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #14b8a6; margin-bottom: 20px;">Hi {name}! 👋</h2>
                    
                    <p>Thank you for subscribing to NoFeePlaces.com! We're excited to help you find your perfect no-fee apartment in NYC.</p>
                    
                    <div style="background: #f0fdfa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #14b8a6;">
                        <h3 style="color: #14b8a6; margin: 0 0 15px 0;">What you can expect:</h3>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li>Weekly updates on the best no-fee apartments</li>
                            <li>Exclusive listings before they hit the market</li>
                            <li>NYC rental market insights and tips</li>
                            <li>Neighborhood guides and price trends</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://nofeeplaces.com" 
                           style="display: inline-block; background: #14b8a6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            🔍 Start Browsing Apartments
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666; border-top: 1px solid #e5e7eb; padding-top: 20px; margin-top: 30px;">
                        Need help? Reply to this email or contact us at placesfirm@gmail.com<br>
                        © {datetime.now().year} NoFeePlaces.com - All rights reserved
                    </p>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Welcome to NoFeePlaces.com!
            
            Hi {name}!
            
            Thank you for subscribing to NoFeePlaces.com! We're excited to help you find your perfect no-fee apartment in NYC.
            
            What you can expect:
            - Weekly updates on the best no-fee apartments
            - Exclusive listings before they hit the market
            - NYC rental market insights and tips
            - Neighborhood guides and price trends
            
            Start browsing apartments: https://nofeeplaces.com
            
            Need help? Reply to this email or contact us at placesfirm@gmail.com
            © {datetime.now().year} NoFeePlaces.com - All rights reserved
            """
            
            success = await self.send_email_async(
                to_email=email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            await self._log_email_attempt(email, subject, "welcome_email", success)
            return success
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            await self._log_email_attempt(email, "Welcome Email", "welcome_email", False)
            return False
    
    async def send_subscriber_notification(self, subscriber_email: str, subscriber_name: Optional[str], interests: List[str]) -> bool:
        """Send notification about new newsletter subscriber"""
        try:
            subject = f"New Newsletter Subscriber - {subscriber_email}"
            
            interests_text = ", ".join(interests) if interests else "No specific interests selected"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>New Newsletter Subscriber</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #14b8a6 0%, #0891b2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px;">
                    <h1 style="margin: 0; font-size: 24px;">📧 New Newsletter Subscriber</h1>
                </div>
                
                <div style="background: #f9fafb; padding: 20px; margin: 20px 0; border-radius: 8px;">
                    <h3 style="color: #14b8a6; margin: 0 0 15px 0;">Subscriber Details:</h3>
                    <p style="margin: 5px 0;"><strong>Email:</strong> {subscriber_email}</p>
                    <p style="margin: 5px 0;"><strong>Name:</strong> {subscriber_name or 'Not provided'}</p>
                    <p style="margin: 5px 0;"><strong>Interests:</strong> {interests_text}</p>
                    <p style="margin: 5px 0;"><strong>Subscribed:</strong> {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}</p>
                </div>
                
                <p style="color: #666; font-size: 14px;">This is a meaningful engagement - someone actively subscribed to your newsletter!</p>
            </body>
            </html>
            """
            
            text_content = f"""
            New Newsletter Subscriber - NoFeePlaces.com
            
            Subscriber Details:
            Email: {subscriber_email}
            Name: {subscriber_name or 'Not provided'}
            Interests: {interests_text}
            Subscribed: {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}
            
            This is a meaningful engagement - someone actively subscribed to your newsletter!
            """
            
            success = await self.send_email_async(
                to_email="placesfirm@gmail.com",
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            await self._log_email_attempt("placesfirm@gmail.com", subject, "subscriber_notification", success)
            return success
            
        except Exception as e:
            logger.error(f"Error sending subscriber notification: {str(e)}")
            await self._log_email_attempt("placesfirm@gmail.com", "Subscriber Notification", "subscriber_notification", False)
            return False

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


    async def send_showing_confirmation(
        self,
        visitor_email: str,
        visitor_name: str,
        visitor_phone: str,
        apartment_title: str,
        apartment_address: str,
        apartment_price: float,
        showing_date: str,
        showing_time: str,
        showing_datetime: any,
        special_notes: str = ""
    ) -> bool:
        """Send showing confirmation email to visitor with calendar invite"""
        try:
            # Generate .ics calendar file
            ics_content = self._generate_calendar_invite(
                summary=f"Apartment Showing: {apartment_title}",
                description=f"Showing for {apartment_title} at {apartment_address}\nPrice: ${apartment_price:,.0f}/month\nContact: {visitor_phone}",
                location=apartment_address,
                start_datetime=showing_datetime,
                duration_hours=1
            )
            
            subject = f"Showing Confirmed: {apartment_title} on {showing_date}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
                    .detail-row {{ margin: 10px 0; }}
                    .label {{ font-weight: bold; color: #667eea; }}
                    .button {{ display: inline-block; padding: 12px 30px; background: #10b981; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏠 Your Showing is Confirmed!</h1>
                    </div>
                    <div class="content">
                        <p>Hi {visitor_name},</p>
                        <p>Great news! Your apartment showing has been confirmed. We're excited to show you this property.</p>
                        
                        <div class="details">
                            <h3 style="color: #667eea; margin-top: 0;">Showing Details</h3>
                            <div class="detail-row">
                                <span class="label">Property:</span> {apartment_title}
                            </div>
                            <div class="detail-row">
                                <span class="label">Address:</span> {apartment_address}
                            </div>
                            <div class="detail-row">
                                <span class="label">Price:</span> ${apartment_price:,.0f}/month
                            </div>
                            <div class="detail-row">
                                <span class="label">Date:</span> {showing_date}
                            </div>
                            <div class="detail-row">
                                <span class="label">Time:</span> {showing_time}
                            </div>
                            <div class="detail-row">
                                <span class="label">Your Phone:</span> {visitor_phone}
                            </div>
                            {f'<div class="detail-row"><span class="label">Notes:</span> {special_notes}</div>' if special_notes else ''}
                        </div>
                        
                        <p><strong>Important:</strong></p>
                        <ul>
                            <li>Please arrive 5 minutes early</li>
                            <li>Bring a valid photo ID</li>
                            <li>Add this showing to your calendar using the attached invite</li>
                            <li>If you need to reschedule, contact us at least 24 hours in advance</li>
                        </ul>
                        
                        <p>We look forward to showing you this apartment!</p>
                        
                        <div class="footer">
                            <p>NoFeePlaces.com - Your No Fee Apartment Experts</p>
                            <p>Email: placesfirm@gmail.com | Phone: +1-646-408-8048</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
Showing Confirmed!

Hi {visitor_name},

Your apartment showing has been confirmed:

Property: {apartment_title}
Address: {apartment_address}
Price: ${apartment_price:,.0f}/month
Date: {showing_date}
Time: {showing_time}
Your Phone: {visitor_phone}
{f'Notes: {special_notes}' if special_notes else ''}

Important Reminders:
- Please arrive 5 minutes early
- Bring a valid photo ID
- Add this showing to your calendar using the attached invite
- If you need to reschedule, contact us at least 24 hours in advance

We look forward to showing you this apartment!

NoFeePlaces.com
placesfirm@gmail.com | +1-646-408-8048
            """
            
            # Send email with calendar attachment
            success = await self.send_email_async(
                to_email=visitor_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                attachments=[{
                    'type': 'calendar',
                    'data': ics_content.encode('utf-8'),
                    'filename': 'apartment_showing.ics',
                    'content_type': 'text/calendar'
                }]
            )
            
            await self._log_email_attempt(visitor_email, subject, "showing_confirmation", success)
            return success
            
        except Exception as e:
            logger.error(f"Error sending showing confirmation: {str(e)}")
            return False
    
    async def send_showing_admin_notification(
        self,
        visitor_name: str,
        visitor_email: str,
        visitor_phone: str,
        apartment_title: str,
        apartment_address: str,
        apartment_price: float,
        showing_date: str,
        showing_time: str,
        special_notes: str = ""
    ) -> bool:
        """Send showing notification to admin"""
        try:
            subject = f"New Showing Scheduled: {apartment_title} - {showing_date}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #1f2937; color: white; padding: 20px; text-align: center; }}
                    .content {{ background: #f9f9f9; padding: 30px; }}
                    .details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .detail-row {{ margin: 10px 0; padding: 8px; border-bottom: 1px solid #e5e7eb; }}
                    .label {{ font-weight: bold; color: #6366f1; display: inline-block; width: 150px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>📅 New Showing Scheduled</h2>
                    </div>
                    <div class="content">
                        <div class="details">
                            <h3>Visitor Information</h3>
                            <div class="detail-row">
                                <span class="label">Name:</span> {visitor_name}
                            </div>
                            <div class="detail-row">
                                <span class="label">Email:</span> {visitor_email}
                            </div>
                            <div class="detail-row">
                                <span class="label">Phone:</span> {visitor_phone}
                            </div>
                            
                            <h3>Apartment Details</h3>
                            <div class="detail-row">
                                <span class="label">Property:</span> {apartment_title}
                            </div>
                            <div class="detail-row">
                                <span class="label">Address:</span> {apartment_address}
                            </div>
                            <div class="detail-row">
                                <span class="label">Price:</span> ${apartment_price:,.0f}/month
                            </div>
                            
                            <h3>Showing Schedule</h3>
                            <div class="detail-row">
                                <span class="label">Date:</span> {showing_date}
                            </div>
                            <div class="detail-row">
                                <span class="label">Time:</span> {showing_time}
                            </div>
                            {f'<div class="detail-row"><span class="label">Special Notes:</span> {special_notes}</div>' if special_notes else ''}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
New Showing Scheduled

Visitor Information:
Name: {visitor_name}
Email: {visitor_email}
Phone: {visitor_phone}

Apartment Details:
Property: {apartment_title}
Address: {apartment_address}
Price: ${apartment_price:,.0f}/month

Showing Schedule:
Date: {showing_date}
Time: {showing_time}
{f'Special Notes: {special_notes}' if special_notes else ''}
            """
            
            success = await self.send_email_async(
                to_email=self.admin_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            await self._log_email_attempt(self.admin_email, subject, "showing_admin_notification", success)
            return success
            
        except Exception as e:
            logger.error(f"Error sending showing admin notification: {str(e)}")
            return False
    

    async def send_share_listing_email(
        self,
        recipient_email: str,
        sharer_name: str,
        apartment_title: str,
        apartment_price: float,
        apartment_url: str,
        apartment_image: Optional[str] = None,
        apartment_neighborhood: str = "NYC",
        apartment_bedrooms: int = 0,
        apartment_bathrooms: float = 1
    ) -> bool:
        """Send listing share email to a friend"""
        try:
            # Format bedroom/bathroom text
            bed_text = "Studio" if apartment_bedrooms == 0 else f"{apartment_bedrooms} Bedroom{'s' if apartment_bedrooms > 1 else ''}"
            bath_text = f"{int(apartment_bathrooms)} Bath{'s' if apartment_bathrooms > 1 else ''}"
            
            subject = f"{sharer_name} shared an apartment with you on NoFeePlaces.com"
            
            # HTML Email Content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); color: white; padding: 30px 20px; text-align: center;">
                        <h1 style="margin: 0; font-size: 28px; font-weight: bold;">NoFeePlaces.com</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">NYC's No Fee Apartment Marketplace</p>
                    </div>
                    
                    <!-- Main Content -->
                    <div style="padding: 30px 20px;">
                        <p style="font-size: 18px; color: #2563eb; font-weight: 600; margin: 0 0 20px 0;">
                            🏠 {sharer_name} thought you'd be interested in this apartment
                        </p>
                        
                        <!-- Apartment Image -->
                        {f'''
                        <div style="margin-bottom: 20px; border-radius: 8px; overflow: hidden;">
                            <img src="{apartment_image}" alt="{apartment_title}" style="width: 100%; height: auto; display: block; max-height: 300px; object-fit: cover;" />
                        </div>
                        ''' if apartment_image else ''}
                        
                        <!-- Apartment Details -->
                        <div style="background-color: #f9fafb; border-left: 4px solid #2563eb; padding: 20px; border-radius: 4px; margin-bottom: 25px;">
                            <h2 style="margin: 0 0 15px 0; font-size: 22px; color: #1f2937;">
                                {bed_text}, {bath_text}
                            </h2>
                            <div style="margin-bottom: 10px;">
                                <span style="font-size: 14px; color: #6b7280;">📍 Location:</span>
                                <span style="font-size: 16px; color: #1f2937; font-weight: 500;"> {apartment_neighborhood}</span>
                            </div>
                            <div style="margin-bottom: 10px;">
                                <span style="font-size: 14px; color: #6b7280;">💰 Rent:</span>
                                <span style="font-size: 24px; color: #2563eb; font-weight: bold;"> ${apartment_price:,.0f}</span>
                                <span style="font-size: 14px; color: #6b7280;">/month</span>
                            </div>
                            <div style="display: inline-block; background-color: #fbbf24; color: #78350f; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-top: 10px;">
                                ⭐ NO FEE
                            </div>
                        </div>
                        
                        <p style="font-size: 16px; color: #4b5563; margin-bottom: 25px;">
                            {sharer_name} found this apartment on NoFeePlaces.com and wanted to share it with you. Click below to view the full listing with photos, amenities, and schedule a showing!
                        </p>
                        
                        <!-- CTA Button -->
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{apartment_url}" style="display: inline-block; background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); color: white; text-decoration: none; padding: 16px 40px; border-radius: 8px; font-size: 18px; font-weight: bold; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.3);">
                                View Full Listing
                            </a>
                        </div>
                        
                        <p style="font-size: 14px; color: #6b7280; text-align: center; margin: 25px 0 0 0;">
                            Or copy this link: <a href="{apartment_url}" style="color: #2563eb; text-decoration: none;">{apartment_url}</a>
                        </p>
                    </div>
                    
                    <!-- Footer -->
                    <div style="background-color: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                        <p style="margin: 0 0 10px 0; font-size: 14px; color: #6b7280;">
                            Browse thousands of no-fee apartments in NYC
                        </p>
                        <p style="margin: 0 0 15px 0;">
                            <a href="https://nofeeplaces.com" style="color: #2563eb; text-decoration: none; font-weight: 600;">NoFeePlaces.com</a>
                        </p>
                        <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                            © 2025 NoFeePlaces.com - NYC's Premier No Fee Apartment Platform
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = f"""
{sharer_name} shared an apartment with you on NoFeePlaces.com

{bed_text}, {bath_text}
Location: {apartment_neighborhood}
Rent: ${apartment_price:,.0f}/month
NO FEE

{sharer_name} found this apartment on NoFeePlaces.com and wanted to share it with you.

View the full listing here: {apartment_url}

Browse more no-fee apartments at NoFeePlaces.com
            """
            
            success = await self.send_email_async(
                to_email=recipient_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                logger.info(f"Share listing email sent successfully to {recipient_email} from {sharer_name}")
            else:
                logger.error(f"Failed to send share listing email to {recipient_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending share listing email: {str(e)}")
            return False

    def _generate_calendar_invite(
        self,
        summary: str,
        description: str,
        location: str,
        start_datetime: any,
        duration_hours: int = 1
    ) -> str:
        """Generate iCalendar (.ics) file content"""
        from datetime import timedelta
        
        end_datetime = start_datetime + timedelta(hours=duration_hours)
        
        # Format datetime for iCalendar (YYYYMMDDTHHMMSS)
        dtstart = start_datetime.strftime("%Y%m%dT%H%M%S")
        dtend = end_datetime.strftime("%Y%m%dT%H%M%S")
        dtstamp = start_datetime.strftime("%Y%m%dT%H%M%SZ")
        
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//NoFeePlaces.com//Apartment Showing//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
UID:{dtstamp}@nofeeplaces.com
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{location}
STATUS:CONFIRMED
SEQUENCE:0
ORGANIZER:mailto:placesfirm@gmail.com
END:VEVENT
END:VCALENDAR"""
        
        return ics_content


# Global email service instance
email_service = EmailService()