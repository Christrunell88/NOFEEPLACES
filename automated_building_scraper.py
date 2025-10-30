#!/usr/bin/env python3
"""
Automated Building Listing Scraper
Regularly checks building websites for new apartment listings
"""
import os
import sys
import json
import time
import logging
import requests
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from bs4 import BeautifulSoup
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/building_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_database')
client = MongoClient(MONGO_URL)
db = client["nofeeplaces_database"]
apartments_collection = db['apartments']
buildings_collection = db['buildings']
scraper_logs_collection = db['scraper_logs']

class BuildingScraper:
    """Base class for building-specific scrapers"""
    
    def __init__(self, config: Dict[str, Any], global_settings: Dict[str, Any]):
        self.config = config
        self.global_settings = global_settings
        self.building_id = config['building_id']
        self.building_name = config['building_name']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': global_settings['user_agent']
        })
        
    def should_scrape(self) -> bool:
        """Check if enough time has passed since last scrape"""
        last_scraped = self.config.get('last_scraped')
        if not last_scraped:
            return True
            
        try:
            last_time = datetime.fromisoformat(last_scraped)
            hours_since = (datetime.now(timezone.utc) - last_time).total_seconds() / 3600
            frequency = self.config.get('scrape_frequency_hours', 24)
            return hours_since >= frequency
        except:
            return True
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a web page with retry logic"""
        max_retries = self.global_settings.get('max_retries', 3)
        timeout = self.global_settings.get('timeout_seconds', 30)
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    return None
    
    def extract_listings(self) -> List[Dict[str, Any]]:
        """Extract listings from source (must be implemented by subclass)"""
        raise NotImplementedError("Subclass must implement extract_listings()")
    
    def find_new_listings(self, scraped_listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compare scraped listings with database to find new ones"""
        existing_units = set()
        existing_apartments = apartments_collection.find({
            'building_id': self.building_id
        }, {'unit_number': 1, 'price': 1})
        
        for apt in existing_apartments:
            unit_key = f"{apt.get('unit_number', '')}_{apt.get('price', 0)}"
            existing_units.add(unit_key)
        
        new_listings = []
        for listing in scraped_listings:
            unit_key = f"{listing.get('unit_number', '')}_{listing.get('price', 0)}"
            if unit_key not in existing_units:
                new_listings.append(listing)
        
        return new_listings
    
    def add_listing_to_database(self, listing: Dict[str, Any]) -> str:
        """Add a new listing to the database"""
        import uuid
        
        # Get building details
        building = buildings_collection.find_one({'building_id': self.building_id})
        if not building:
            logger.error(f"Building {self.building_id} not found in database")
            return None
        
        # Create apartment document
        apartment_data = {
            'id': str(uuid.uuid4()),
            'building_id': self.building_id,
            'building_name': building['building_name'],
            'address': building['address'],
            'neighborhood': building['neighborhood'],
            'borough': building['borough'],
            **listing,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'available': True,
            'contact_email': 'placesfirm@gmail.com',
            'contact_phone': '+1-646-408-8048',
            'featured': False,
            'is_verified': True,
            'priority': 5,
            'broker_fee': 'No fee',
            'auto_scraped': True
        }
        
        # Insert apartment
        result = apartments_collection.insert_one(apartment_data)
        
        # Update building stats
        self.update_building_stats()
        
        return apartment_data['id']
    
    def update_building_stats(self):
        """Update building statistics after adding listings"""
        all_units = list(apartments_collection.find({'building_id': self.building_id}))
        available_units = [u for u in all_units if u.get('available', True)]
        all_prices = [u['price'] for u in all_units if u.get('price')]
        bedroom_types = list(set([u.get('bedrooms') for u in all_units if u.get('bedrooms') is not None]))
        
        buildings_collection.update_one(
            {'building_id': self.building_id},
            {'$set': {
                'total_units': len(all_units),
                'available_units': len(available_units),
                'price_range': {
                    'min': min(all_prices) if all_prices else 0,
                    'max': max(all_prices) if all_prices else 0,
                    'avg': sum(all_prices) / len(all_prices) if all_prices else 0
                },
                'bedroom_types': sorted(bedroom_types),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }}
        )
    
    def log_scrape_run(self, status: str, new_listings: int, errors: List[str]):
        """Log the scrape run to database"""
        log_entry = {
            'building_id': self.building_id,
            'building_name': self.building_name,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': status,
            'new_listings_found': new_listings,
            'errors': errors
        }
        scraper_logs_collection.insert_one(log_entry)
    
    def run(self) -> Dict[str, Any]:
        """Execute the scraping process"""
        logger.info(f"Starting scrape for {self.building_name}")
        
        if not self.should_scrape():
            logger.info(f"Skipping {self.building_name} - not enough time since last scrape")
            return {'status': 'skipped', 'reason': 'frequency_limit'}
        
        errors = []
        new_listings = []
        
        try:
            # Extract listings from source
            scraped_listings = self.extract_listings()
            logger.info(f"Found {len(scraped_listings)} total listings for {self.building_name}")
            
            # Find new listings
            new_listings = self.find_new_listings(scraped_listings)
            logger.info(f"Identified {len(new_listings)} new listings")
            
            # Add new listings to database
            added_ids = []
            for listing in new_listings:
                try:
                    listing_id = self.add_listing_to_database(listing)
                    if listing_id:
                        added_ids.append(listing_id)
                        logger.info(f"Added listing: Unit {listing.get('unit_number')} - ${listing.get('price')}/mo")
                except Exception as e:
                    error_msg = f"Failed to add listing: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Log the scrape run
            status = 'success' if not errors else 'partial_success'
            self.log_scrape_run(status, len(added_ids), errors)
            
            return {
                'status': status,
                'scraped': len(scraped_listings),
                'new': len(added_ids),
                'errors': errors
            }
            
        except Exception as e:
            error_msg = f"Scraping failed: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            self.log_scrape_run('failed', 0, errors)
            return {'status': 'failed', 'errors': errors}


class MaltDriveScraper(BuildingScraper):
    """Scraper for Malt Drive buildings"""
    
    def extract_listings(self) -> List[Dict[str, Any]]:
        """Extract listings from Malt Drive website"""
        listings = []
        listings_url = self.config['source_config']['listings_url']
        building_filter = self.config['source_config']['building_filter']
        
        logger.info(f"Fetching Malt Drive listings from {listings_url}")
        
        # This is a placeholder - actual implementation would use web scraping
        # or API calls to extract listing data
        # For now, return empty list as demonstration
        
        # TODO: Implement actual scraping logic:
        # 1. Fetch the availability page
        # 2. Parse HTML/JSON for unit listings
        # 3. Filter by building (2-20 vs 2-21)
        # 4. Extract: unit_number, bedrooms, bathrooms, price, sqft, images, description
        
        logger.warning("MaltDriveScraper.extract_listings() not fully implemented yet")
        return listings


class DelecoScraper(BuildingScraper):
    """Scraper for The Delecor building"""
    
    def extract_listings(self) -> List[Dict[str, Any]]:
        """Extract listings from The Delecor website"""
        listings = []
        listings_url = self.config['source_config']['listings_url']
        
        logger.info(f"Fetching Delecor listings from {listings_url}")
        
        # TODO: Implement Delecor scraping logic
        # Similar structure to other buildings
        logger.warning("DelecoScraper.extract_listings() not fully implemented yet")
        return listings


class MercedesHouseScraper(BuildingScraper):
    """Scraper for Mercedes House"""
    
    def extract_listings(self) -> List[Dict[str, Any]]:
        """Extract listings from Mercedes House website"""
        listings = []
        listings_url = self.config['source_config']['listings_url']
        
        logger.info(f"Fetching Mercedes House listings from {listings_url}")
        
        # Note: This is a single-page app with hash navigation
        # May require JavaScript execution or API endpoint discovery
        # TODO: Implement Mercedes House scraping logic
        logger.warning("MercedesHouseScraper.extract_listings() not fully implemented yet")
        return listings


class FortySixFiftyScraper(BuildingScraper):
    """Scraper for Forty Six Fifty building"""
    
    def extract_listings(self) -> List[Dict[str, Any]]:
        """Extract listings from Forty Six Fifty website"""
        listings = []
        listings_url = self.config['source_config']['listings_url']
        
        logger.info(f"Fetching Forty Six Fifty listings from {listings_url}")
        
        # TODO: Implement Forty Six Fifty scraping logic
        logger.warning("FortySixFiftyScraper.extract_listings() not fully implemented yet")
        return listings


class ManhattanSkylineScraper(BuildingScraper):
    """Scraper for Manhattan Skyline properties (CD 280, 55 Thompson, etc.)"""
    
    def extract_listings(self) -> List[Dict[str, Any]]:
        """Extract listings from Manhattan Skyline website"""
        listings = []
        listings_url = self.config['source_config']['listings_url']
        building_slug = self.config['source_config']['building_slug']
        
        logger.info(f"Fetching {self.building_name} listings from {listings_url}")
        
        # Manhattan Skyline uses a consistent structure across properties
        # TODO: Implement Manhattan Skyline scraping logic
        # Note: May need to check for availability section or apartment listings
        logger.warning("ManhattanSkylineScraper.extract_listings() not fully implemented yet")
        return listings


class GreenpointScraper(BuildingScraper):
    """Scraper for The Greenpoint building"""
    
    def extract_listings(self) -> List[Dict[str, Any]]:
        """Extract listings from The Greenpoint website"""
        listings = []
        listings_url = self.config['source_config']['listings_url']
        
        logger.info(f"Fetching The Greenpoint listings from {listings_url}")
        
        # The Greenpoint has its own website with check-availability page
        # TODO: Implement The Greenpoint scraping logic
        logger.warning("GreenpointScraper.extract_listings() not fully implemented yet")
        return listings


class BushburgScraper(BuildingScraper):
    """Scraper for Bushburg properties (PLG, etc.)"""
    
    def extract_listings(self) -> List[Dict[str, Any]]:
        """Extract listings from Bushburg website"""
        listings = []
        listings_url = self.config['source_config']['listings_url']
        property_name = self.config['source_config'].get('property_name', '')
        
        logger.info(f"Fetching {self.building_name} listings from {listings_url}")
        
        # Bushburg manages multiple residential properties
        # Need to filter for specific property (PLG)
        # TODO: Implement Bushburg scraping logic
        logger.warning("BushburgScraper.extract_listings() not fully implemented yet")
        return listings


class AriaScraper(BuildingScraper):
    """Scraper for The Aria building"""
    
    def extract_listings(self) -> List[Dict[str, Any]]:
        """Extract listings from The Aria website"""
        listings = []
        listings_url = self.config['source_config']['listings_url']
        
        logger.info(f"Fetching The Aria listings from {listings_url}")
        
        # The Aria has floorplans page at liveatarianyc.com
        # TODO: Implement The Aria scraping logic
        logger.warning("AriaScraper.extract_listings() not fully implemented yet")
        return listings


class WindsorCommunitiesScraper(BuildingScraper):
    """Scraper for Windsor Communities properties (e.g., Waterline Square)"""
    
    def extract_listings(self) -> List[Dict[str, Any]]:
        """Extract listings from Windsor Communities website"""
        listings = []
        
        # TODO: Implement Windsor Communities scraping logic
        logger.warning("WindsorCommunitiesScraper.extract_listings() not fully implemented yet")
        return listings


class AutomatedScraperService:
    """Main service to coordinate all building scrapers"""
    
    def __init__(self, config_file: str = '/app/building_scraper_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.scrapers = []
        self.initialize_scrapers()
    
    def load_config(self) -> Dict[str, Any]:
        """Load scraper configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {'scrapers': [], 'global_settings': {}}
    
    def initialize_scrapers(self):
        """Initialize scraper instances for each building"""
        scraper_classes = {
            'maltdrive': MaltDriveScraper,
            'delecor': DelecoScraper,
            'mercedes_house': MercedesHouseScraper,
            'forty_six_fifty': FortySixFiftyScraper,
            'manhattan_skyline': ManhattanSkylineScraper,
            'greenpoint': GreenpointScraper,
            'bushburg': BushburgScraper,
            'aria': AriaScraper,
            'windsor': WindsorCommunitiesScraper
        }
        
        for scraper_config in self.config.get('scrapers', []):
            if not scraper_config.get('enabled', False):
                logger.info(f"Scraper for {scraper_config['building_name']} is disabled")
                continue
            
            source_type = scraper_config.get('source_type')
            scraper_class = scraper_classes.get(source_type)
            
            if scraper_class:
                scraper = scraper_class(scraper_config, self.config.get('global_settings', {}))
                self.scrapers.append(scraper)
            else:
                logger.warning(f"Unknown source type: {source_type} for {scraper_config['building_name']}")
    
    def run_all(self) -> Dict[str, Any]:
        """Run all enabled scrapers"""
        logger.info("=" * 70)
        logger.info("STARTING AUTOMATED BUILDING SCRAPER SERVICE")
        logger.info("=" * 70)
        
        results = []
        total_new = 0
        total_errors = 0
        
        for scraper in self.scrapers:
            result = scraper.run()
            results.append({
                'building': scraper.building_name,
                **result
            })
            total_new += result.get('new', 0)
            total_errors += len(result.get('errors', []))
            
            # Delay between scrapers to be respectful
            delay = self.config.get('global_settings', {}).get('request_delay_seconds', 2)
            time.sleep(delay)
        
        logger.info("=" * 70)
        logger.info(f"SCRAPING COMPLETE: {len(results)} buildings processed")
        logger.info(f"New listings found: {total_new}")
        logger.info(f"Total errors: {total_errors}")
        logger.info("=" * 70)
        
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'buildings_processed': len(results),
            'total_new_listings': total_new,
            'total_errors': total_errors,
            'results': results
        }


def main():
    """Main entry point"""
    # Create logs directory if it doesn't exist
    os.makedirs('/app/logs', exist_ok=True)
    
    # Initialize and run the scraper service
    service = AutomatedScraperService()
    results = service.run_all()
    
    # Print summary
    print("\n" + "=" * 70)
    print("AUTOMATED SCRAPER SERVICE - RUN SUMMARY")
    print("=" * 70)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Buildings processed: {results['buildings_processed']}")
    print(f"New listings found: {results['total_new_listings']}")
    print(f"Errors: {results['total_errors']}")
    print("\nPer-building results:")
    for result in results['results']:
        status_emoji = "✅" if result['status'] in ['success', 'skipped'] else "⚠️"
        print(f"  {status_emoji} {result['building']}: {result['status']}")
        if result.get('new', 0) > 0:
            print(f"     New listings: {result['new']}")
    
    client.close()


if __name__ == "__main__":
    main()
