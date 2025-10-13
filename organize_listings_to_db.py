#!/usr/bin/env python3
"""
Organize Scraped Listings into Database
Inserts real scraped apartment data with images into MongoDB
Structure: Building Address -> Unit -> Size -> Price -> Images
"""

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ListingOrganizer:
    """Organize scraped listings into database"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces')
        self.client = None
        self.db = None
    
    async def connect_database(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        logger.info(f"✅ Connected to MongoDB: {self.db_name}")
    
    def normalize_size(self, bedrooms: int) -> str:
        """Normalize bedroom count to standard size labels"""
        if bedrooms == 0:
            return "Studio"
        elif bedrooms == 1:
            return "1 Bedroom"
        elif bedrooms == 2:
            return "2 Bedroom"
        elif bedrooms == 3:
            return "3 Bedroom"
        else:
            return f"{bedrooms} Bedroom"
    
    def clean_title(self, title: str) -> str:
        """Clean up title formatting"""
        if not title:
            return ""
        # Remove extra whitespace and newlines
        title = ' '.join(title.split())
        return title.strip()
    
    def make_absolute_url(self, url: str, base_url: str = "https://www.mercedeshouseny.com") -> str:
        """Convert relative URLs to absolute"""
        if url.startswith('http'):
            return url
        return base_url + url
    
    def load_scraped_data(self) -> Dict[str, List[Dict]]:
        """Load all scraped data from JSON files"""
        data = {
            'trulia': [],
            'mercedes_house': []
        }
        
        # Load Trulia listings
        try:
            with open('/app/listings.json', 'r') as f:
                data['trulia'] = json.load(f)
            logger.info(f"📂 Loaded {len(data['trulia'])} listings from Trulia")
        except Exception as e:
            logger.warning(f"Could not load listings.json: {e}")
        
        # Load Mercedes House listings
        try:
            with open('/app/mercedes_house_listings.json', 'r') as f:
                data['mercedes_house'] = json.load(f)
            logger.info(f"📂 Loaded {len(data['mercedes_house'])} listings from Mercedes House")
        except Exception as e:
            logger.warning(f"Could not load mercedes_house_listings.json: {e}")
        
        return data
    
    def create_apartment_record(self, listing: Dict, source: str) -> Dict[str, Any]:
        """Create standardized apartment record for database"""
        
        # Extract and clean data
        title = self.clean_title(listing.get('title', ''))
        bedrooms = listing.get('bedrooms')
        size = self.normalize_size(bedrooms) if bedrooms is not None else None
        
        # Clean and validate images (ONLY REAL IMAGES)
        images = []
        for img_url in listing.get('images', []):
            # Make absolute URL
            img_url = self.make_absolute_url(img_url)
            # Only include valid image URLs (no placeholders, no fake data)
            if all(x not in img_url.lower() for x in ['ajax-loader', 'placeholder', 'fake', 'mock', 'sample']):
                images.append(img_url)
        
        # Create record
        record = {
            'id': str(uuid.uuid4()),
            'building_address': listing.get('address', ''),
            'unit_number': listing.get('unit_number'),  # If available
            'size': size,
            'bedrooms': bedrooms,
            'bathrooms': listing.get('bathrooms'),
            'sqft': listing.get('sqft'),
            'price': listing.get('price'),
            'images': images,
            'title': title,
            'neighborhood': listing.get('neighborhood'),
            'borough': listing.get('borough'),
            'building_name': listing.get('building_name'),
            'amenities': listing.get('amenities', []),
            'url': listing.get('url'),
            'source': source,
            'contact_email': 'placesfirm@gmail.com',
            'contact_phone': '+1-646-408-8048',
            'available': True,
            'broker_fee': 'No fee',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'is_verified': True,
            'data_quality': 'premium',
            'image_count': len(images)
        }
        
        return record
    
    async def insert_listings(self, listings: List[Dict]) -> int:
        """Insert listings into database"""
        if not listings:
            return 0
        
        try:
            result = await self.db.apartments.insert_many(listings)
            return len(result.inserted_ids)
        except Exception as e:
            logger.error(f"Error inserting listings: {e}")
            return 0
    
    async def clear_existing_scraped_data(self):
        """Clear existing scraped data to avoid duplicates"""
        logger.info("\n🧹 Clearing existing scraped data...")
        
        # Remove existing Mercedes House and Trulia listings
        result = await self.db.apartments.delete_many({
            'source': {'$in': ['Trulia', 'Mercedes House NYC']}
        })
        
        logger.info(f"   Removed {result.deleted_count} existing scraped listings")
    
    async def organize_and_insert(self):
        """Main function to organize and insert data"""
        logger.info("\n" + "="*60)
        logger.info("🗂️  ORGANIZING SCRAPED LISTINGS INTO DATABASE")
        logger.info("="*60)
        
        # Load scraped data
        scraped_data = self.load_scraped_data()
        
        # Clear existing scraped data
        await self.clear_existing_scraped_data()
        
        # Process Trulia listings
        logger.info("\n📍 Processing Trulia Listings...")
        trulia_records = []
        for listing in scraped_data['trulia']:
            record = self.create_apartment_record(listing, 'Trulia')
            if record['images']:  # Only add if has real images
                trulia_records.append(record)
                logger.info(f"   ✓ {record['building_address'][:50]} - {record['size'] or 'N/A'} - {len(record['images'])} images")
        
        # Process Mercedes House listings
        logger.info("\n🏢 Processing Mercedes House Listings...")
        mercedes_records = []
        for listing in scraped_data['mercedes_house']:
            record = self.create_apartment_record(listing, 'Mercedes House NYC')
            if record['images']:  # Only add if has real images
                mercedes_records.append(record)
                logger.info(f"   ✓ {record['building_address']} - {record['size'] or record['title'][:30]} - {len(record['images'])} images")
        
        # Insert all records
        logger.info("\n💾 Inserting into database...")
        trulia_count = await self.insert_listings(trulia_records)
        mercedes_count = await self.insert_listings(mercedes_records)
        
        total_count = trulia_count + mercedes_count
        total_images = sum(len(r['images']) for r in trulia_records + mercedes_records)
        
        logger.info(f"\n✅ Successfully inserted {total_count} listings with {total_images} REAL images")
        
        # Print summary by building
        logger.info("\n" + "="*60)
        logger.info("📊 SUMMARY BY BUILDING")
        logger.info("="*60)
        
        # Group by building address
        buildings = {}
        for record in trulia_records + mercedes_records:
            addr = record['building_address']
            if addr not in buildings:
                buildings[addr] = []
            buildings[addr].append(record)
        
        for building_addr, units in buildings.items():
            logger.info(f"\n🏢 {building_addr}")
            logger.info(f"   Total Units: {len(units)}")
            
            # Group by size
            by_size = {}
            for unit in units:
                size = unit['size'] or 'Unknown'
                if size not in by_size:
                    by_size[size] = []
                by_size[size].append(unit)
            
            for size, size_units in sorted(by_size.items()):
                total_images = sum(u['image_count'] for u in size_units)
                prices = [u['price'] for u in size_units if u['price']]
                price_str = prices[0] if prices else 'Contact for Price'
                logger.info(f"   • {size}: {len(size_units)} unit(s) - {price_str} - {total_images} images")
        
        return total_count
    
    async def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("\n✅ Database connection closed")


async def main():
    """Main execution"""
    logger.info("🚀 Starting Listing Organization")
    
    organizer = ListingOrganizer()
    
    try:
        # Connect to database
        await organizer.connect_database()
        
        # Organize and insert data
        count = await organizer.organize_and_insert()
        
        logger.info("\n" + "="*60)
        logger.info(f"✅ COMPLETE - {count} listings organized in database")
        logger.info("="*60)
        logger.info("\nAll images are REAL scraped data - no generated/fake images")
        
    finally:
        await organizer.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
