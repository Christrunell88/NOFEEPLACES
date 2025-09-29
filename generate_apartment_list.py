#!/usr/bin/env python3
"""
Generate complete apartment list and email to placesfirm@gmail.com
"""

import asyncio
import csv
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import sys
sys.path.append('/app/backend')
from email_service import email_service
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_db')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

async def generate_and_email_apartment_list():
    """Generate apartment list and email to placesfirm@gmail.com"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("📋 Generating complete apartment list...")
    
    # Fetch all apartments with required fields
    apartments = await db.apartments.find(
        {"available": True},
        {
            "address": 1,
            "bedrooms": 1, 
            "price": 1,
            "contact_info": 1,
            "contact_phone": 1,
            "contact_email": 1,
            "title": 1,
            "neighborhood": 1,
            "borough": 1,
            "square_feet": 1,
            "amenities": 1,
            "lease_terms": 1,
            "pet_policy": 1
        }
    ).sort("price", 1).to_list(length=None)  # Sort by price ascending
    
    print(f"📊 Found {len(apartments)} available apartments")
    
    # Generate HTML email content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>NoFeePlaces.com - Complete Apartment Listing</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; margin: -30px -30px 30px -30px; }}
            .stats {{ background: #f0f4ff; padding: 20px; border-radius: 8px; margin: 20px 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
            .stat-item {{ text-align: center; }}
            .stat-number {{ font-size: 28px; font-weight: bold; color: #667eea; }}
            .stat-label {{ color: #666; font-size: 14px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8f9fa; font-weight: bold; color: #333; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .price {{ font-weight: bold; color: #28a745; }}
            .bedrooms {{ color: #667eea; font-weight: bold; }}
            .contact {{ color: #dc3545; }}
            .address {{ color: #333; }}
            .neighborhood {{ color: #6c757d; font-style: italic; }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #eee; text-align: center; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏠 NoFeePlaces.com Complete Apartment List</h1>
                <p>Generated on {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">{len(apartments)}</div>
                    <div class="stat-label">Total Apartments</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${apartments[0]['price']:,.0f}</div>
                    <div class="stat-label">Lowest Rent</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${apartments[-1]['price']:,.0f}</div>
                    <div class="stat-label">Highest Rent</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${sum(apt['price'] for apt in apartments) / len(apartments):,.0f}</div>
                    <div class="stat-label">Average Rent</div>
                </div>
            </div>
            
            <h2>📋 Complete Apartment Listing (Sorted by Price)</h2>
            
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Address</th>
                        <th>Bedrooms</th>
                        <th>Monthly Rent</th>
                        <th>Contact Information</th>
                        <th>Neighborhood</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add each apartment to the table
    for i, apt in enumerate(apartments, 1):
        # Format bedrooms
        bedrooms = apt.get('bedrooms', 'N/A')
        if bedrooms == 0 or bedrooms == "0":
            bedrooms_display = "Studio"
        elif isinstance(bedrooms, str) and 'studio' in bedrooms.lower():
            bedrooms_display = "Studio"
        else:
            bedrooms_display = f"{bedrooms} BR"
        
        # Get contact info
        contact_info = apt.get('contact_info', {})
        contact_phone = contact_info.get('phone') or apt.get('contact_phone', '+1 (646) 408-8048')
        contact_email = contact_info.get('email') or apt.get('contact_email', 'placesfirm@gmail.com')
        
        # Format contact display
        contact_display = f"📧 {contact_email}<br>📞 {contact_phone}"
        if contact_info.get('company'):
            contact_display += f"<br>🏢 {contact_info['company']}"
        
        # Get address and neighborhood
        address = apt.get('address', 'Address not specified')
        neighborhood = apt.get('neighborhood', 'N/A')
        borough = apt.get('borough', '')
        location_display = f"{neighborhood}"
        if borough:
            location_display += f", {borough}"
        
        html_content += f"""
                    <tr>
                        <td>{i}</td>
                        <td class="address">{address}</td>
                        <td class="bedrooms">{bedrooms_display}</td>
                        <td class="price">${apt['price']:,.0f}/month</td>
                        <td class="contact">{contact_display}</td>
                        <td class="neighborhood">{location_display}</td>
                    </tr>
        """
    
    html_content += f"""
                </tbody>
            </table>
            
            <div class="footer">
                <p><strong>NoFeePlaces.com</strong> - NYC's Premier No Fee Apartment Platform</p>
                <p>This list contains all {len(apartments)} available no-fee apartments in our database</p>
                <p>📧 placesfirm@gmail.com | 📞 +1 (646) 408-8048</p>
                <p style="font-size: 12px; color: #999; margin-top: 20px;">
                    Generated automatically from NoFeePlaces.com database on {datetime.now(timezone.utc).strftime('%B %d, %Y')}
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Generate plain text version
    text_content = f"""
NoFeePlaces.com Complete Apartment List
Generated on {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}

SUMMARY STATISTICS:
- Total Apartments: {len(apartments)}
- Lowest Rent: ${apartments[0]['price']:,.0f}/month
- Highest Rent: ${apartments[-1]['price']:,.0f}/month  
- Average Rent: ${sum(apt['price'] for apt in apartments) / len(apartments):,.0f}/month

COMPLETE APARTMENT LISTING (Sorted by Price):

"""
    
    for i, apt in enumerate(apartments, 1):
        # Format bedrooms for text
        bedrooms = apt.get('bedrooms', 'N/A')
        if bedrooms == 0 or bedrooms == "0":
            bedrooms_display = "Studio"
        elif isinstance(bedrooms, str) and 'studio' in bedrooms.lower():
            bedrooms_display = "Studio"
        else:
            bedrooms_display = f"{bedrooms} BR"
        
        # Get contact info for text
        contact_info = apt.get('contact_info', {})
        contact_phone = contact_info.get('phone') or apt.get('contact_phone', '+1 (646) 408-8048')
        contact_email = contact_info.get('email') or apt.get('contact_email', 'placesfirm@gmail.com')
        
        address = apt.get('address', 'Address not specified')
        neighborhood = apt.get('neighborhood', 'N/A')
        borough = apt.get('borough', '')
        
        text_content += f"""
{i}. {address}
   Bedrooms: {bedrooms_display}
   Monthly Rent: ${apt['price']:,.0f}
   Contact: {contact_email} | {contact_phone}
   Location: {neighborhood}, {borough}
   
"""
    
    text_content += f"""
---
NoFeePlaces.com - NYC's Premier No Fee Apartment Platform
This list contains all {len(apartments)} available no-fee apartments in our database
Contact: placesfirm@gmail.com | +1 (646) 408-8048
"""
    
    # Send email
    print("📧 Sending apartment list to placesfirm@gmail.com...")
    
    success = await email_service.send_email_async(
        to_email="placesfirm@gmail.com",
        subject=f"NoFeePlaces.com Complete Apartment List - {len(apartments)} Listings ({datetime.now().strftime('%B %d, %Y')})",
        html_content=html_content,
        text_content=text_content
    )
    
    if success:
        print("✅ Apartment list successfully sent to placesfirm@gmail.com")
        print(f"📋 Email contains {len(apartments)} apartments with complete contact information")
        print(f"💰 Price range: ${apartments[0]['price']:,.0f} - ${apartments[-1]['price']:,.0f}")
    else:
        print("❌ Failed to send email")
    
    client.close()
    return success

if __name__ == "__main__":
    asyncio.run(generate_and_email_apartment_list())