#!/usr/bin/env python3
"""
Public Real Estate Scraper for NoFeePlaces.com
Crawls major real estate websites: Zumper, Apartments.com, Trulia
Uses Requests and BeautifulSoup to extract listing data
Respects robots.txt and skips login-gated content
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import logging
import signal
from urllib.parse import urljoin, urlparse, parse_qs
from urllib.robotparser import RobotFileParser
import re
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TimeoutException(Exception):
    """Custom timeout exception"""
    pass


def timeout_handler(signum, frame):
    """Handle timeout signals"""
    raise TimeoutException("Operation timed out")


class PublicRealEstateScraper:
    """
    Scrapes public real estate listing websites
    Respects robots.txt and ethical scraping practices
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        self.delay_between_requests = 2  # Respectful delay
        self.robot_parsers = {}
        self.all_listings = []
        
    def check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed per robots.txt"""
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            # Check cached parser
            if base_url not in self.robot_parsers:
                rp = RobotFileParser()
                rp.set_url(f"{base_url}/robots.txt")
                try:
                    rp.read()
                    self.robot_parsers[base_url] = rp
                    logger.info(f"✓ Loaded robots.txt for {base_url}")
                except Exception as e:
                    logger.warning(f"⚠ Could not load robots.txt for {base_url}: {e}")
                    # Allow if robots.txt unavailable (be conservative)
                    return True
            
            # Check if URL is allowed
            is_allowed = self.robot_parsers[base_url].can_fetch(self.session.headers['User-Agent'], url)
            
            if not is_allowed:
                logger.warning(f"⛔ Blocked by robots.txt: {url}")
            
            return is_allowed
            
        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")
            return False
    
    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch page content with error handling"""
        try:
            # Check robots.txt
            if not self.check_robots_txt(url):
                return None
            
            # Add delay for respectful scraping
            time.sleep(self.delay_between_requests + random.uniform(0, 1))
            
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            
            # Check for login walls or blocks
            if response.status_code == 403:
                logger.warning(f"⚠ 403 Forbidden - Skipping: {url}")
                return None
            
            if response.status_code == 401:
                logger.warning(f"⚠ 401 Unauthorized (login required) - Skipping: {url}")
                return None
                
            if response.status_code != 200:
                logger.warning(f"⚠ Status {response.status_code} - Skipping: {url}")
                return None
            
            # Check for login redirects
            if 'login' in response.url.lower() or 'signin' in response.url.lower():
                logger.warning(f"⚠ Login redirect detected - Skipping: {url}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except requests.exceptions.Timeout:
            logger.error(f"⏱ Timeout fetching: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching {url}: {e}")
            return None
    
    def extract_price(self, text: str) -> str:
        """Extract price from text"""
        if not text:
            return None
        
        # Look for price patterns like $2,500 or $2500 or 2,500
        price_pattern = r'\$?[\d,]+(?:\.\d{2})?'
        matches = re.findall(price_pattern, text)
        
        if matches:
            # Return first match, clean it up
            price = matches[0].replace('$', '').replace(',', '')
            try:
                # Validate it's a reasonable rent price (500-20000)
                price_int = int(float(price))
                if 500 <= price_int <= 20000:
                    return f"${price_int:,}"
            except:
                pass
        
        return None
    
    def scrape_zumper(self, location: str = "new-york-ny") -> List[Dict[str, Any]]:
        """Scrape Zumper.com for apartment listings"""
        logger.info("\n" + "="*60)
        logger.info("🏢 SCRAPING ZUMPER.COM")
        logger.info("="*60)
        
        listings = []
        base_url = "https://www.zumper.com"
        search_url = f"{base_url}/apartments-for-rent/{location}"
        
        try:
            soup = self.fetch_page(search_url)
            if not soup:
                logger.warning("⚠ Could not fetch Zumper page")
                return listings
            
            # Zumper structure: Look for listing cards
            # Common selectors (may need adjustment based on current site structure)
            listing_cards = soup.find_all(['div', 'article'], class_=re.compile(r'(listing|property|card)', re.I))
            
            logger.info(f"Found {len(listing_cards)} potential listing elements")
            
            for card in listing_cards[:15]:  # Limit to first 15
                try:
                    # Extract title
                    title_elem = card.find(['h2', 'h3', 'a'], class_=re.compile(r'title|name|address', re.I))
                    title = title_elem.get_text(strip=True) if title_elem else None
                    
                    # Extract link
                    link_elem = card.find('a', href=re.compile(r'(listing|apartment|building)', re.I))
                    if not link_elem:
                        link_elem = card.find('a', href=True)
                    
                    listing_url = urljoin(base_url, link_elem['href']) if link_elem and link_elem.get('href') else None
                    
                    # Extract price
                    price_elem = card.find(['span', 'div'], class_=re.compile(r'price|rent', re.I))
                    price_text = price_elem.get_text(strip=True) if price_elem else None
                    price = self.extract_price(price_text)
                    
                    # Extract address/location
                    address_elem = card.find(['span', 'div', 'p'], class_=re.compile(r'address|location', re.I))
                    address = address_elem.get_text(strip=True) if address_elem else None
                    
                    # Only add if we have minimum required data
                    if title and listing_url:
                        listing = {
                            'title': title,
                            'address': address or 'New York, NY',
                            'price': price or 'Contact for Price',
                            'url': listing_url,
                            'source': 'Zumper'
                        }
                        listings.append(listing)
                        logger.info(f"  ✓ {title} - {price or 'N/A'}")
                
                except Exception as e:
                    logger.debug(f"Error parsing Zumper card: {e}")
                    continue
            
            logger.info(f"✅ Extracted {len(listings)} listings from Zumper")
            
        except Exception as e:
            logger.error(f"❌ Error scraping Zumper: {e}")
        
        return listings
    
    def scrape_apartments_com(self, location: str = "new-york-ny") -> List[Dict[str, Any]]:
        """Scrape Apartments.com for apartment listings"""
        logger.info("\n" + "="*60)
        logger.info("🏢 SCRAPING APARTMENTS.COM")
        logger.info("="*60)
        
        listings = []
        base_url = "https://www.apartments.com"
        search_url = f"{base_url}/{location}/"
        
        try:
            # Set timeout alarm
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)  # 30 second timeout
            
            soup = self.fetch_page(search_url)
            
            # Cancel alarm
            signal.alarm(0)
            
            if not soup:
                logger.warning("⚠ Could not fetch Apartments.com page")
                return listings
            
            # Apartments.com structure: placard class for listings
            listing_cards = soup.find_all(['article', 'div'], class_=re.compile(r'(placard|mortar|property)', re.I))
            
            logger.info(f"Found {len(listing_cards)} potential listing elements")
            
            for card in listing_cards[:15]:  # Limit to first 15
                try:
                    # Extract title
                    title_elem = card.find(['a', 'span'], class_=re.compile(r'(property-title|name)', re.I))
                    if not title_elem:
                        title_elem = card.find('a', attrs={'data-label': re.compile(r'property', re.I)})
                    
                    title = title_elem.get_text(strip=True) if title_elem else None
                    
                    # Extract link
                    link_elem = title_elem if title_elem and title_elem.name == 'a' else card.find('a', href=True)
                    listing_url = urljoin(base_url, link_elem['href']) if link_elem and link_elem.get('href') else None
                    
                    # Extract price
                    price_elem = card.find(['p', 'span'], class_=re.compile(r'(price|rent)', re.I))
                    price_text = price_elem.get_text(strip=True) if price_elem else None
                    price = self.extract_price(price_text)
                    
                    # Extract address
                    address_elem = card.find(['div', 'span'], class_=re.compile(r'(address|location)', re.I))
                    address = address_elem.get_text(strip=True) if address_elem else None
                    
                    # Only add if we have minimum required data
                    if title and listing_url:
                        listing = {
                            'title': title,
                            'address': address or 'New York, NY',
                            'price': price or 'Contact for Price',
                            'url': listing_url,
                            'source': 'Apartments.com'
                        }
                        listings.append(listing)
                        logger.info(f"  ✓ {title} - {price or 'N/A'}")
                
                except Exception as e:
                    logger.debug(f"Error parsing Apartments.com card: {e}")
                    continue
            
            logger.info(f"✅ Extracted {len(listings)} listings from Apartments.com")
            
        except TimeoutException:
            logger.error("⏱ Apartments.com scraping timed out (30s limit)")
        except Exception as e:
            logger.error(f"❌ Error scraping Apartments.com: {e}")
        finally:
            signal.alarm(0)  # Ensure alarm is cancelled
        
        return listings
    
    def scrape_trulia(self, location: str = "New_York,NY") -> List[Dict[str, Any]]:
        """Scrape Trulia.com for apartment listings"""
        logger.info("\n" + "="*60)
        logger.info("🏢 SCRAPING TRULIA.COM")
        logger.info("="*60)
        
        listings = []
        base_url = "https://www.trulia.com"
        
        # Try multiple search URLs for better coverage
        search_urls = [
            f"{base_url}/for_rent/{location}",
            f"{base_url}/for_rent/Manhattan,New_York,NY",
            f"{base_url}/for_rent/Brooklyn,New_York,NY"
        ]
        
        for search_url in search_urls:
            try:
                logger.info(f"Trying: {search_url}")
                soup = self.fetch_page(search_url)
                if not soup:
                    logger.warning(f"⚠ Could not fetch Trulia page: {search_url}")
                    continue
                
                # Trulia structure: Look for listing cards
                listing_cards = soup.find_all(['li', 'div'], attrs={'data-testid': re.compile(r'(property|home|listing)', re.I)})
                
                if not listing_cards:
                    # Fallback: look for common card classes
                    listing_cards = soup.find_all(['div', 'article'], class_=re.compile(r'(card|property|listing)', re.I))
                
                logger.info(f"Found {len(listing_cards)} potential listing elements")
                
                for card in listing_cards[:50]:  # Increase limit to get more listings
                    try:
                        # Extract title/address
                        title_elem = card.find(['div', 'a'], attrs={'data-testid': re.compile(r'(property-address|home-address)', re.I)})
                        if not title_elem:
                            title_elem = card.find(['h2', 'h3', 'a'], class_=re.compile(r'(address|title)', re.I))
                        
                        title = title_elem.get_text(strip=True) if title_elem else None
                        
                        # Extract link
                        link_elem = card.find('a', href=re.compile(r'/c/', re.I))
                        if not link_elem:
                            link_elem = card.find('a', href=True)
                        
                        listing_url = urljoin(base_url, link_elem['href']) if link_elem and link_elem.get('href') else None
                        
                        # Extract price
                        price_elem = card.find(['div', 'span'], attrs={'data-testid': re.compile(r'price', re.I)})
                        if not price_elem:
                            price_elem = card.find(['div', 'span'], class_=re.compile(r'price|rent', re.I))
                        
                        price_text = price_elem.get_text(strip=True) if price_elem else None
                        price = self.extract_price(price_text)
                        
                        # Extract address
                        address = title  # Trulia often uses address as title
                        
                        # Only add if we have minimum required data and not duplicate
                        if title and listing_url:
                            # Check for duplicates
                            is_duplicate = any(l['url'] == listing_url for l in listings)
                            if not is_duplicate:
                                listing = {
                                    'title': title,
                                    'address': address or 'New York, NY',
                                    'price': price or 'Contact for Price',
                                    'url': listing_url,
                                    'source': 'Trulia'
                                }
                                listings.append(listing)
                                logger.info(f"  ✓ {title[:70]} - {price or 'N/A'}")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing Trulia card: {e}")
                        continue
                
                # If we got listings from this URL, we can stop trying others
                if listings:
                    logger.info(f"✅ Found {len(listings)} unique listings from this page")
                    break
                    
            except Exception as e:
                logger.error(f"❌ Error scraping Trulia page {search_url}: {e}")
                continue
        
        logger.info(f"✅ Extracted total of {len(listings)} unique listings from Trulia")
        return listings
    
    def scrape_all_sites(self) -> List[Dict[str, Any]]:
        """Scrape all three real estate websites - REAL DATA ONLY"""
        logger.info("\n" + "🎯 " + "="*58)
        logger.info("   PUBLIC REAL ESTATE SCRAPER - MULTI-SITE CRAWLER")
        logger.info("="*60 + "\n")
        
        all_listings = []
        
        # Scrape each site with timeout protection
        try:
            zumper_listings = self.scrape_zumper()
            if zumper_listings:
                all_listings.extend(zumper_listings)
        except Exception as e:
            logger.error(f"Zumper scraping failed: {e}")
        
        try:
            apartments_listings = self.scrape_apartments_com()
            if apartments_listings:
                all_listings.extend(apartments_listings)
        except Exception as e:
            logger.error(f"Apartments.com scraping failed: {e}")
        
        try:
            trulia_listings = self.scrape_trulia()
            if trulia_listings:
                all_listings.extend(trulia_listings)
        except Exception as e:
            logger.error(f"Trulia scraping failed: {e}")
        
        # Log results - NO FAKE DATA
        if len(all_listings) == 0:
            logger.warning("\n" + "="*60)
            logger.warning("⚠️  NO LISTINGS EXTRACTED")
            logger.warning("="*60)
            logger.warning("These sites use advanced protections:")
            logger.warning("  • JavaScript-rendered content (React/Vue)")
            logger.warning("  • CloudFlare anti-bot protection")
            logger.warning("  • Login walls for full listings")
            logger.warning("  • Dynamic class names and structure")
            logger.warning("\nFor production use, consider:")
            logger.warning("  • Official APIs (if available)")
            logger.warning("  • Playwright/Selenium for JS rendering")
            logger.warning("  • Paid data providers")
            logger.warning("  • Partnership agreements with listing sites")
            logger.warning("="*60 + "\n")
        else:
            logger.info(f"\n✅ Successfully scraped {len(all_listings)} REAL listings")
        
        self.all_listings = all_listings
        return all_listings
    
    def save_to_json(self, filename: str = "listings.json") -> bool:
        """Save scraped listings to JSON file - REAL DATA ONLY"""
        try:
            if len(self.all_listings) == 0:
                logger.warning(f"\n⚠️  No listings to save - {filename} not created")
                return False
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.all_listings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"\n💾 Saved {len(self.all_listings)} REAL listings to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving to JSON: {e}")
            return False
    
    def print_summary(self):
        """Print scraping summary - REAL DATA ONLY"""
        logger.info("\n" + "="*60)
        logger.info("📊 SCRAPING SUMMARY")
        logger.info("="*60)
        
        if len(self.all_listings) == 0:
            logger.info("  ⚠️  No real listings extracted")
            logger.info("  All sites blocked or returned no data")
        else:
            # Count by source
            sources = {}
            for listing in self.all_listings:
                source = listing.get('source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1
            
            for source, count in sources.items():
                logger.info(f"  • {source}: {count} REAL listings")
            
            logger.info(f"\n  📦 Total REAL listings: {len(self.all_listings)}")
        
        logger.info("="*60 + "\n")


def main():
    """Main execution function - REAL DATA ONLY"""
    logger.info("🚀 Starting Public Real Estate Scraper (REAL DATA ONLY)")
    
    scraper = PublicRealEstateScraper()
    
    # Scrape all sites
    listings = scraper.scrape_all_sites()
    
    # Save to JSON (only if we have real data)
    scraper.save_to_json("listings.json")
    
    # Print summary
    scraper.print_summary()
    
    # Print sample listings (only real data)
    if listings:
        logger.info("📋 REAL Listings Extracted:\n")
        for i, listing in enumerate(listings[:5], 1):
            logger.info(f"{i}. {listing['title']}")
            logger.info(f"   Address: {listing['address']}")
            logger.info(f"   Price: {listing['price']}")
            logger.info(f"   URL: {listing['url']}")
            logger.info(f"   Source: {listing['source']}\n")
    else:
        logger.warning("⚠️  No real listings were extracted from any site")
    
    logger.info("✅ Scraping complete!")
    
    return listings


if __name__ == "__main__":
    main()
