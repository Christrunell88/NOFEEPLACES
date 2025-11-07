#!/usr/bin/env python3
"""
Generate sitemap.xml for NoFeePlaces
"""
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

DOMAIN = "https://nofeeplaces.com"
PREVIEW_DOMAIN = "https://rentauth-test.preview.emergentagent.com"

async def generate_sitemap():
    """Generate sitemap with all pages and apartment listings"""
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['nofeeplaces_database']
    
    # Get all apartments
    apartments = await db.apartments.find({'available': True}).to_list(length=None)
    
    # Start sitemap
    sitemap = []
    sitemap.append('<?xml version="1.0" encoding="UTF-8"?>')
    sitemap.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Homepage - highest priority
    sitemap.append('  <url>')
    sitemap.append(f'    <loc>{PREVIEW_DOMAIN}/</loc>')
    sitemap.append('    <changefreq>daily</changefreq>')
    sitemap.append('    <priority>1.0</priority>')
    sitemap.append('  </url>')
    
    # Static pages
    static_pages = [
        ('/about', '0.8', 'monthly'),
        ('/contact', '0.8', 'monthly'),
        ('/list', '0.9', 'weekly'),
        ('/apartments/budget', '0.9', 'daily'),
        ('/apartments/smart', '0.9', 'daily'),
        ('/apartments/luxury', '0.9', 'daily'),
        ('/apartments/best-value', '0.9', 'daily'),
        ('/borough/manhattan', '0.9', 'daily'),
        ('/borough/brooklyn', '0.9', 'daily'),
        ('/borough/queens', '0.9', 'daily'),
        ('/borough/bronx', '0.8', 'weekly'),
        ('/borough/staten-island', '0.8', 'weekly'),
    ]
    
    for path, priority, changefreq in static_pages:
        sitemap.append('  <url>')
        sitemap.append(f'    <loc>{PREVIEW_DOMAIN}{path}</loc>')
        sitemap.append(f'    <changefreq>{changefreq}</changefreq>')
        sitemap.append(f'    <priority>{priority}</priority>')
        sitemap.append('  </url>')
    
    # Individual apartment listings
    print(f'Adding {len(apartments)} apartment listings to sitemap...')
    for apt in apartments:
        apt_id = apt.get('id')
        if apt_id:
            sitemap.append('  <url>')
            sitemap.append(f'    <loc>{PREVIEW_DOMAIN}/apartment/{apt_id}</loc>')
            sitemap.append('    <changefreq>weekly</changefreq>')
            sitemap.append('    <priority>0.8</priority>')
            
            # Add last modified if available
            updated_at = apt.get('updated_at')
            if updated_at:
                try:
                    if isinstance(updated_at, str):
                        date_str = updated_at.split('T')[0]
                        sitemap.append(f'    <lastmod>{date_str}</lastmod>')
                except:
                    pass
            
            sitemap.append('  </url>')
    
    # Close sitemap
    sitemap.append('</urlset>')
    
    # Write to file
    sitemap_content = '\n'.join(sitemap)
    
    output_path = '/app/frontend/public/sitemap.xml'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    
    print(f'✅ Sitemap generated successfully!')
    print(f'   Total URLs: {len(apartments) + len(static_pages) + 1}')
    print(f'   Output: {output_path}')
    
    client.close()

if __name__ == '__main__':
    asyncio.run(generate_sitemap())
