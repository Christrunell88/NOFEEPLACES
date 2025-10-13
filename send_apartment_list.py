#!/usr/bin/env python3
"""
Generate and email apartment list with real scraped data
"""

import asyncio
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import sys
sys.path.append('/app/backend')
from email_service import email_service

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

async def generate_and_send_list():
    """Generate apartment list and email it"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("📋 Generating apartment list from database...")
    
    # Fetch all available apartments
    apartments = await db.apartments.find(
        {"available": True}
    ).sort("price", 1).to_list(length=None)
    
    print(f"📊 Found {len(apartments)} available apartments")
    
    if not apartments:
        print("⚠️  No apartments found in database")
        return False
    
    # Generate HTML content
    html_parts = []
    html_parts.append("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #667eea; color: white; padding: 20px; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
        .price { font-weight: bold; color: #28a745; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NoFeePlaces.com Apartment List</h1>
        <p>Generated: """ + datetime.now(timezone.utc).strftime('%B %d, %Y') + """</p>
    </div>
    
    <h2>Available Apartments: """ + str(len(apartments)) + """</h2>
    
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Building Address</th>
                <th>Size</th>
                <th>Price</th>
                <th>Images</th>
                <th>Contact</th>
            </tr>
        </thead>
        <tbody>
    """)
    
    # Add each apartment
    for i, apt in enumerate(apartments, 1):
        size = apt.get('size') or f"{apt.get('bedrooms', '?')} BR"
        price = apt.get('price', 'N/A')
        if isinstance(price, (int, float)):
            price = f"${price:,.0f}"
        
        building_addr = apt.get('building_address', apt.get('address', 'N/A'))
        image_count = len(apt.get('images', []))
        contact = apt.get('contact_email', 'placesfirm@gmail.com')
        
        html_parts.append(f"""
            <tr>
                <td>{i}</td>
                <td>{building_addr}</td>
                <td>{size}</td>
                <td class="price">{price}</td>
                <td>{image_count} images</td>
                <td>{contact}</td>
            </tr>
        """)
    
    html_parts.append("""
        </tbody>
    </table>
    
    <div style="margin-top: 40px; padding: 20px; background: #f5f5f5; text-align: center;">
        <p><strong>NoFeePlaces.com</strong></p>
        <p>📧 placesfirm@gmail.com | 📞 +1-646-408-8048</p>
    </div>
</body>
</html>
    """)
    
    html_content = ''.join(html_parts)
    
    # Generate text version
    text_parts = []
    text_parts.append(f"\nNoFeePlaces.com Apartment List\n")
    text_parts.append(f"Generated: {datetime.now(timezone.utc).strftime('%B %d, %Y')}\n")
    text_parts.append(f"\nTotal Apartments: {len(apartments)}\n")
    text_parts.append("\n" + "="*60 + "\n\n")
    
    for i, apt in enumerate(apartments, 1):
        size = apt.get('size') or f"{apt.get('bedrooms', '?')} BR"
        price = apt.get('price', 'N/A')
        if isinstance(price, (int, float)):
            price = f"${price:,.0f}"
        
        building_addr = apt.get('building_address', apt.get('address', 'N/A'))
        image_count = len(apt.get('images', []))
        
        text_parts.append(f"{i}. {building_addr}\n")
        text_parts.append(f"   Size: {size}\n")
        text_parts.append(f"   Price: {price}/month\n")
        text_parts.append(f"   Images: {image_count}\n")
        text_parts.append(f"   Neighborhood: {apt.get('neighborhood', 'N/A')}\n\n")
    
    text_parts.append("\n" + "="*60 + "\n")
    text_parts.append("NoFeePlaces.com\n")
    text_parts.append("📧 placesfirm@gmail.com | 📞 +1-646-408-8048\n")
    
    text_content = ''.join(text_parts)
    
    # Send email
    print("📧 Sending email to placesfirm@gmail.com...")
    
    success = await email_service.send_email_async(
        to_email="placesfirm@gmail.com",
        subject=f"NoFeePlaces.com Apartment List - {len(apartments)} Listings ({datetime.now().strftime('%b %d, %Y')})",
        html_content=html_content,
        text_content=text_content
    )
    
    if success:
        print("✅ Email sent successfully!")
        print(f"📋 List contains {len(apartments)} apartments")
    else:
        print("❌ Failed to send email")
    
    client.close()
    return success

if __name__ == "__main__":
    asyncio.run(generate_and_send_list())
