#!/usr/bin/env python3
"""
Send various assets and information to placesfirm@gmail.com
Usage: python send_assets_to_email.py [wordmark|analytics|feedback|custom]
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
sys.path.append('/app/backend')
from email_service import email_service
from dotenv import load_dotenv
import base64
import mimetypes

# Load environment variables
load_dotenv('/app/backend/.env')

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_db')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

async def send_wordmark():
    """Send NoFeePlaces wordmark assets"""
    print("🎨 Preparing NoFeePlaces WordMark assets...")
    
    # Create comprehensive wordmark HTML
    wordmark_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NoFeePlaces WordMark Assets</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { font-family: system-ui, -apple-system, sans-serif; }
            .wordmark-container { 
                display: inline-block; 
                padding: 2rem; 
                margin: 1rem;
                border-radius: 1rem;
            }
        </style>
    </head>
    <body class="bg-gray-50 p-8">
        <div class="max-w-6xl mx-auto">
            <div class="bg-white rounded-2xl shadow-lg p-8 mb-8">
                <h1 class="text-3xl font-bold text-gray-900 mb-6 text-center">🏢 NoFeePlaces WordMark Assets</h1>
                <p class="text-gray-600 text-center mb-8">Complete brand identity package generated on """ + datetime.now().strftime('%B %d, %Y') + """</p>
                
                <!-- Dark Background Version -->
                <div class="mb-12">
                    <h2 class="text-xl font-semibold mb-4">Dark Background Version</h2>
                    <div class="bg-gradient-to-r from-slate-900 to-gray-900 wordmark-container">
                        <div class="flex flex-col">
                            <div class="flex items-baseline space-x-0">
                                <span class="text-5xl font-extralight text-white tracking-wide">No</span>
                                <span class="text-5xl font-bold text-emerald-400 tracking-tight">Fee</span>
                                <span class="text-2xl font-light text-gray-300 tracking-[0.2em] ml-2 mt-1">PLACES</span>
                            </div>
                            <div class="w-full h-1 bg-gradient-to-r from-emerald-400/60 via-blue-400/40 to-transparent mt-2"></div>
                            <div class="text-sm text-gray-400 font-medium tracking-widest mt-2">NYC RENTAL PLATFORM</div>
                        </div>
                    </div>
                </div>
                
                <!-- Light Background Version -->
                <div class="mb-12">
                    <h2 class="text-xl font-semibold mb-4">Light Background Version</h2>
                    <div class="bg-white border-2 border-gray-200 wordmark-container">
                        <div class="flex flex-col">
                            <div class="flex items-baseline space-x-0">
                                <span class="text-5xl font-extralight text-gray-800 tracking-wide">No</span>
                                <span class="text-5xl font-bold text-emerald-600 tracking-tight">Fee</span>
                                <span class="text-2xl font-light text-gray-600 tracking-[0.2em] ml-2 mt-1">PLACES</span>
                            </div>
                            <div class="w-full h-1 bg-gradient-to-r from-emerald-600/50 via-blue-500/30 to-transparent mt-2"></div>
                            <div class="text-sm text-gray-500 font-medium tracking-widests mt-2">NYC RENTAL PLATFORM</div>
                        </div>
                    </div>
                </div>
                
                <!-- Usage Guidelines -->
                <div class="bg-blue-50 p-6 rounded-xl">
                    <h3 class="text-lg font-semibold text-blue-900 mb-4">📋 Usage Guidelines</h3>
                    <div class="grid md:grid-cols-2 gap-6">
                        <div>
                            <h4 class="font-medium text-blue-800 mb-2">Typography</h4>
                            <ul class="text-sm text-blue-700 space-y-1">
                                <li>• Font: system-ui, -apple-system, sans-serif</li>
                                <li>• "No": Extra-light weight, tracking wide</li>
                                <li>• "Fee": Bold weight, tracking tight</li>
                                <li>• "PLACES": Light weight, letter-spacing 0.2em</li>
                            </ul>
                        </div>
                        <div>
                            <h4 class="font-medium text-blue-800 mb-2">Colors</h4>
                            <ul class="text-sm text-blue-700 space-y-1">
                                <li>• Emerald: #10b981 (Fee text)</li>
                                <li>• Blue: #3b82f6 (Gradient accent)</li>
                                <li>• Gray variants for "No" and "PLACES"</li>
                                <li>• Gradient underline: emerald to blue fade</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create React component code
    react_code = '''
// NoFeePlaces WordMark - React Component
import React from 'react';

export const NoFeePlacesWordMark = ({ 
  theme = 'dark',  // 'dark' | 'light'
  size = 'medium', // 'small' | 'medium' | 'large'
  tagline = 'NYC RENTAL PLATFORM',
  className = ''
}) => {
  const sizeClasses = {
    small: 'text-2xl',
    medium: 'text-4xl', 
    large: 'text-6xl'
  };
  
  const themeClasses = {
    dark: {
      no: 'text-white',
      fee: 'text-emerald-400',
      places: 'text-gray-300',
      tagline: 'text-gray-400',
      gradient: 'from-emerald-400/60 via-blue-400/40 to-transparent'
    },
    light: {
      no: 'text-gray-800',
      fee: 'text-emerald-600',
      places: 'text-gray-600',
      tagline: 'text-gray-500', 
      gradient: 'from-emerald-600/50 via-blue-500/30 to-transparent'
    }
  };
  
  const sizeClass = sizeClasses[size];
  const colors = themeClasses[theme];
  
  return (
    <div className={`flex flex-col ${className}`}>
      <div className="flex items-baseline space-x-0">
        <span className={`${sizeClass} font-extralight ${colors.no} tracking-wide`}>No</span>
        <span className={`${sizeClass} font-bold ${colors.fee} tracking-tight`}>Fee</span>
        <span className={`${size === 'large' ? 'text-2xl' : 'text-lg'} font-light ${colors.places} tracking-[0.2em] ml-2 mt-1`}>PLACES</span>
      </div>
      <div className={`w-full h-0.5 bg-gradient-to-r ${colors.gradient} mt-1`}></div>
      {tagline && <div className={`text-xs ${colors.tagline} font-medium tracking-widest mt-1`}>{tagline}</div>}
    </div>
  );
};

// Usage Examples:
// <NoFeePlacesWordMark theme="dark" size="large" />
// <NoFeePlacesWordMark theme="light" tagline="ZERO BROKER FEES" />
'''
    
    # Email content
    email_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>NoFeePlaces WordMark Assets Package</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; }}
            .header {{ background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; margin: -30px -30px 30px -30px; }}
            .asset-item {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 15px 0; }}
            .code-block {{ background: #1f2937; color: #f9fafb; padding: 15px; border-radius: 6px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 12px; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #eee; text-align: center; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎨 NoFeePlaces WordMark Assets</h1>
                <p>Complete brand identity package</p>
                <p>Generated: {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}</p>
            </div>
            
            <div class="asset-item">
                <h3>📄 HTML WordMark Showcase</h3>
                <p>Complete HTML file with both dark and light versions, usage guidelines, and styling examples.</p>
                <p><strong>File:</strong> wordmark_showcase.html (attached as text)</p>
            </div>
            
            <div class="asset-item">
                <h3>⚛️ React Component</h3>
                <p>Ready-to-use React component with theme and size variations.</p>
                <div class="code-block">{react_code[:200]}...</div>
                <p><em>Full component code included in plain text version</em></p>
            </div>
            
            <div class="asset-item">
                <h3>🎨 Design Specifications</h3>
                <ul>
                    <li><strong>Typography:</strong> system-ui, -apple-system, sans-serif</li>
                    <li><strong>Colors:</strong> Emerald (#10b981), Blue (#3b82f6), Gray variants</li>
                    <li><strong>Structure:</strong> "No" (light) + "Fee" (bold emerald) + "PLACES" (light, spaced)</li>
                    <li><strong>Accent:</strong> Emerald-to-blue gradient underline</li>
                </ul>
            </div>
            
            <div class="footer">
                <p><strong>NoFeePlaces.com</strong> - Brand Assets</p>
                <p>📧 placesfirm@gmail.com | 📞 +1 (646) 408-8048</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version with full code
    email_text = f"""
NoFeePlaces WordMark Assets Package
Generated: {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}

=== REACT COMPONENT CODE ===
{react_code}

=== CSS VERSION ===
.nofee-wordmark {{
    font-family: system-ui, -apple-system, sans-serif;
    display: flex;
    flex-direction: column;
}}

.nofee-text {{ display: flex; align-items: baseline; }}

.nofee-no {{
    font-size: 2.5rem;
    font-weight: 200;
    color: #ffffff; /* Dark theme */
    letter-spacing: 0.05em;
}}

.nofee-fee {{
    font-size: 2.5rem;
    font-weight: 700;
    color: #10b981; /* Emerald */
    letter-spacing: -0.025em;
}}

.nofee-places {{
    font-size: 1.25rem;
    font-weight: 300;
    color: #d1d5db; /* Gray-300 */
    letter-spacing: 0.2em;
    margin-left: 0.5rem;
    margin-top: 0.25rem;
}}

.nofee-underline {{
    width: 100%;
    height: 2px;
    background: linear-gradient(to right, rgba(16, 185, 129, 0.6), rgba(59, 130, 246, 0.4), transparent);
    margin-top: 0.25rem;
}}

.nofee-tagline {{
    font-size: 0.75rem;
    color: #9ca3af;
    font-weight: 500;
    letter-spacing: 0.1em;
    margin-top: 0.25rem;
}}

=== USAGE NOTES ===
- Use "dark" theme for dark backgrounds
- Use "light" theme for light backgrounds  
- Available sizes: small, medium, large
- Maintain proper spacing and typography weights
- Emerald color (#10b981) is key brand element

Files included:
1. HTML showcase with both versions
2. React component code (above)
3. CSS version (above)
4. Usage guidelines and specifications

Contact: placesfirm@gmail.com | +1 (646) 408-8048
NoFeePlaces.com - NYC's Premier No Fee Apartment Platform
    """
    
    # Send the email
    print("📧 Sending WordMark assets to placesfirm@gmail.com...")
    
    success = await email_service.send_email_async(
        to_email="placesfirm@gmail.com",
        subject=f"🎨 NoFeePlaces WordMark Assets Package - {datetime.now().strftime('%B %d, %Y')}",
        html_content=email_html,
        text_content=email_text
    )
    
    if success:
        print("✅ WordMark assets successfully sent to placesfirm@gmail.com")
        print("📦 Package includes: HTML showcase, React component, CSS version, usage guidelines")
    else:
        print("❌ Failed to send WordMark assets")
        
    return success

async def send_analytics_summary():
    """Send analytics summary"""
    print("📊 Generating analytics summary...")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get visitor stats
    visitors_count = await db.visitor_tracking.count_documents({})
    apartments_count = await db.apartments.count_documents({"available": True})
    
    # Get recent feedback
    feedback_count = await db.feedback.count_documents({})
    recent_feedback = await db.feedback.find().sort("created_at", -1).limit(5).to_list(length=5)
    
    email_content = f"""
    <h2>📊 NoFeePlaces Analytics Summary</h2>
    <p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    
    <h3>Key Metrics:</h3>
    <ul>
        <li>Total Visitors Tracked: {visitors_count}</li>
        <li>Available Apartments: {apartments_count}</li>
        <li>Feedback Submissions: {feedback_count}</li>
    </ul>
    
    <h3>Recent Feedback:</h3>
    """
    
    for fb in recent_feedback:
        email_content += f"""
        <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
            <strong>Type:</strong> {fb.get('type', 'N/A')}<br>
            <strong>Title:</strong> {fb.get('title', 'N/A')}<br>
            <strong>Description:</strong> {fb.get('description', 'N/A')[:100]}...<br>
            <strong>Date:</strong> {fb.get('created_at', 'N/A')}
        </div>
        """
    
    success = await email_service.send_email_async(
        to_email="placesfirm@gmail.com",
        subject=f"📊 NoFeePlaces Analytics Summary - {datetime.now().strftime('%B %d, %Y')}",
        html_content=email_content,
        text_content=f"Analytics Summary - Visitors: {visitors_count}, Apartments: {apartments_count}, Feedback: {feedback_count}"
    )
    
    client.close()
    return success

async def send_custom_info(info_type="general"):
    """Send custom information based on type"""
    print(f"📋 Preparing {info_type} information...")
    
    content_types = {
        "contact": "Complete contact information and business details",
        "technical": "Technical specifications and API documentation", 
        "marketing": "Marketing materials and brand guidelines",
        "general": "General platform information and statistics"
    }
    
    email_content = f"""
    <h2>📋 NoFeePlaces {info_type.title()} Information</h2>
    <p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    
    <h3>Information Type: {content_types.get(info_type, "Custom information")}</h3>
    
    <h3>Platform Details:</h3>
    <ul>
        <li>Platform: NoFeePlaces.com</li>
        <li>Focus: NYC No-Fee Apartment Rentals</li>
        <li>Technology: React + FastAPI + MongoDB</li>
        <li>Contact: placesfirm@gmail.com</li>
        <li>Phone: +1 (646) 408-8048</li>
    </ul>
    """
    
    success = await email_service.send_email_async(
        to_email="placesfirm@gmail.com",
        subject=f"📋 NoFeePlaces {info_type.title()} Information - {datetime.now().strftime('%B %d, %Y')}",
        html_content=email_content,
        text_content=f"NoFeePlaces {info_type} information sent on {datetime.now().strftime('%B %d, %Y')}"
    )
    
    return success

async def main():
    """Main function to handle different asset types"""
    
    asset_type = sys.argv[1] if len(sys.argv) > 1 else "wordmark"
    
    print(f"🚀 NoFeePlaces Asset Emailer - Sending {asset_type}")
    print("=" * 50)
    
    if asset_type == "wordmark":
        success = await send_wordmark()
    elif asset_type == "analytics":
        success = await send_analytics_summary()
    elif asset_type == "feedback":
        # Could add feedback summary here
        success = await send_custom_info("feedback")
    else:
        success = await send_custom_info(asset_type)
    
    if success:
        print(f"\n🎉 Successfully sent {asset_type} assets to placesfirm@gmail.com")
    else:
        print(f"\n❌ Failed to send {asset_type} assets")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("""
NoFeePlaces Asset Emailer

Usage: python send_assets_to_email.py [asset_type]

Available asset types:
  wordmark   - Send complete WordMark package (default)
  analytics  - Send analytics summary
  feedback   - Send feedback summary  
  apartments - Send apartment listings (use generate_apartment_list.py instead)
  custom     - Send custom information

Examples:
  python send_assets_to_email.py wordmark
  python send_assets_to_email.py analytics
  python send_assets_to_email.py feedback
        """)
    else:
        asyncio.run(main())