import os
import sys
from pymongo import MongoClient
from datetime import datetime
import csv
from io import StringIO
sys.path.append('/app/backend')
from email_service import EmailService

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
apartments_collection = db['apartments']

print("=" * 80)
print("GENERATING APARTMENT LIST FOR EMAIL")
print("=" * 80)

# Fetch all apartments
apartments = list(apartments_collection.find({}, {
    'title': 1,
    'address': 1,
    'neighborhood': 1,
    'borough': 1,
    'price': 1,
    'bedrooms': 1,
    'bathrooms': 1,
    'sqft': 1,
    'building_name': 1,
    'broker_fee': 1,
    'available': 1,
    'available_date': 1,
    'amenities': 1,
    'contact_info': 1,
    'best_value': 1,
    'floor': 1,
    'unit_number': 1
}).sort('price', 1))

total_count = len(apartments)
print(f"\n📊 Total Apartments: {total_count}")

# Generate CSV
csv_buffer = StringIO()
csv_writer = csv.writer(csv_buffer)

# Write header
csv_writer.writerow([
    'Building Name',
    'Unit Number',
    'Address',
    'Neighborhood',
    'Borough',
    'Price/Month',
    'Bedrooms',
    'Bathrooms',
    'Sqft',
    'Price per Sqft',
    'Floor',
    'Broker Fee',
    'Available',
    'Available Date',
    'Amenity Count',
    'Best Value',
    'Contact Email',
    'Contact Phone'
])

# Write data
for apt in apartments:
    sqft = apt.get('sqft', 0)
    price = apt.get('price', 0)
    price_per_sqft = round(price / sqft, 2) if sqft > 0 else 0
    
    contact_info = apt.get('contact_info', {})
    
    csv_writer.writerow([
        apt.get('building_name', 'N/A'),
        apt.get('unit_number', 'N/A'),
        apt.get('address', 'N/A'),
        apt.get('neighborhood', 'N/A'),
        apt.get('borough', 'N/A'),
        f"${apt.get('price', 0):,}",
        apt.get('bedrooms', 'N/A'),
        apt.get('bathrooms', 'N/A'),
        sqft if sqft > 0 else 'N/A',
        f"${price_per_sqft}" if price_per_sqft > 0 else 'N/A',
        apt.get('floor', 'N/A'),
        apt.get('broker_fee', 'N/A'),
        'Yes' if apt.get('available', True) else 'No',
        apt.get('available_date', 'N/A'),
        len(apt.get('amenities', [])),
        'Yes' if apt.get('best_value', False) else 'No',
        contact_info.get('email', 'N/A'),
        contact_info.get('phone', 'N/A')
    ])

csv_content = csv_buffer.getvalue()
csv_buffer.close()

# Generate summary statistics
total_apartments = total_count
avg_price = sum(apt.get('price', 0) for apt in apartments) / total_apartments if total_apartments > 0 else 0
best_value_count = sum(1 for apt in apartments if apt.get('best_value', False))
budget_count = sum(1 for apt in apartments if apt.get('price', 0) < 4500)
smart_count = sum(1 for apt in apartments if 4500 <= apt.get('price', 0) <= 6500)
luxury_count = sum(1 for apt in apartments if apt.get('price', 0) > 6500)

# Count by borough
borough_counts = {}
for apt in apartments:
    borough = apt.get('borough', 'Unknown')
    borough_counts[borough] = borough_counts.get(borough, 0) + 1

# Generate HTML email content
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px; }}
        .summary {{ background: #f7fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .stat {{ display: inline-block; margin: 10px 20px; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .stat-label {{ font-size: 0.9em; color: #666; }}
        .section {{ margin: 30px 0; }}
        .highlight {{ background: #edf2f7; padding: 15px; border-left: 4px solid #667eea; margin: 15px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; }}
        .footer {{ text-align: center; color: #666; margin-top: 40px; padding-top: 20px; border-top: 2px solid #e2e8f0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 NoFeePlaces Apartment List</h1>
            <p>Complete Database Export</p>
            <p style="font-size: 0.9em; opacity: 0.9;">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Database Summary</h2>
            <div style="text-align: center;">
                <div class="stat">
                    <div class="stat-value">{total_apartments}</div>
                    <div class="stat-label">Total Apartments</div>
                </div>
                <div class="stat">
                    <div class="stat-value">${avg_price:,.0f}</div>
                    <div class="stat-label">Average Rent</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{best_value_count}</div>
                    <div class="stat-label">Best Value</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h3>📈 Category Breakdown</h3>
            <div class="highlight">
                <p><strong>💰 Budget (Under $4,500):</strong> {budget_count} apartments</p>
                <p><strong>🎯 Smart ($4,500-$6,500):</strong> {smart_count} apartments</p>
                <p><strong>✨ Luxury (Over $6,500):</strong> {luxury_count} apartments</p>
                <p><strong>⭐ Best Value:</strong> {best_value_count} apartments</p>
            </div>
        </div>
        
        <div class="section">
            <h3>🗺️ By Borough</h3>
            <table>
                <tr>
                    <th>Borough</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
"""

for borough, count in sorted(borough_counts.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total_apartments * 100) if total_apartments > 0 else 0
    html_content += f"""
                <tr>
                    <td><strong>{borough}</strong></td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
    """

html_content += f"""
            </table>
        </div>
        
        <div class="section">
            <h3>📎 Attached Files</h3>
            <div class="highlight">
                <p><strong>apartments_list.csv</strong> - Complete apartment database in CSV format</p>
                <p>Includes: Building names, addresses, pricing, amenities, contact info, and more</p>
            </div>
        </div>
        
        <div class="section">
            <h3>🏆 Top 5 Best Value Apartments</h3>
            <table>
                <tr>
                    <th>Building</th>
                    <th>Unit</th>
                    <th>Price</th>
                    <th>Sqft</th>
                    <th>$/Sqft</th>
                </tr>
"""

best_value_apts = [apt for apt in apartments if apt.get('best_value', False)][:5]
for apt in best_value_apts:
    sqft = apt.get('sqft', 0)
    price = apt.get('price', 0)
    price_per_sqft = round(price / sqft, 2) if sqft > 0 else 0
    html_content += f"""
                <tr>
                    <td>{apt.get('building_name', 'N/A')}</td>
                    <td>{apt.get('unit_number', 'N/A')}</td>
                    <td>${price:,}/mo</td>
                    <td>{sqft} sqft</td>
                    <td>${price_per_sqft}/sqft</td>
                </tr>
    """

html_content += """
            </table>
        </div>
        
        <div class="footer">
            <p><strong>NoFeePlaces.com</strong></p>
            <p>Helping New Yorkers find no-fee apartments</p>
            <p style="font-size: 0.8em; color: #999;">This is an automated report generated from the NoFeePlaces database</p>
        </div>
    </div>
</body>
</html>
"""

# Send email with CSV attachment
print("\n📧 Sending email to placesfirm@gmail.com...")

try:
    email_service = EmailService()
    
    # Create attachment
    attachments = [{
        'content': csv_content.encode('utf-8'),
        'filename': f'apartments_list_{datetime.now().strftime("%Y%m%d")}.csv',
        'content_type': 'text/csv'
    }]
    
    # Send email synchronously (not async)
    import asyncio
    
    async def send():
        success = await email_service.send_email_async(
            to_email='placesfirm@gmail.com',
            subject=f'NoFeePlaces Apartment List - {total_apartments} Apartments ({datetime.now().strftime("%B %d, %Y")})',
            html_content=html_content,
            text_content=f"Complete apartment list attached. Total: {total_apartments} apartments.",
            attachments=attachments
        )
        return success
    
    # Run async function
    success = asyncio.run(send())
    
    if success:
        print("✅ Email sent successfully to placesfirm@gmail.com!")
        print(f"   - Subject: NoFeePlaces Apartment List - {total_apartments} Apartments")
        print(f"   - Attachment: apartments_list_{datetime.now().strftime('%Y%m%d')}.csv")
        print(f"   - Total apartments: {total_apartments}")
    else:
        print("❌ Failed to send email")
        print("   Please check email service configuration")
        
except Exception as e:
    print(f"❌ Error sending email: {str(e)}")
    print("   Email service may not be configured properly")
    print(f"\n📄 CSV content preview (first 500 chars):")
    print(csv_content[:500])

client.close()
print("\n" + "=" * 80)
print("SCRIPT COMPLETED")
print("=" * 80)
