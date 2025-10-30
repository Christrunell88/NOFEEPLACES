# Automated Building Listing Scraper System

## Overview
A comprehensive system to automatically check building websites for new apartment listings on a regular basis and add them to the NoFeePlaces database.

---

## System Architecture

### Components

1. **Configuration File** (`building_scraper_config.json`)
   - Stores building URLs and scraping rules
   - Controls scraping frequency
   - Enable/disable scrapers
   - Global settings (user agent, delays, etc.)

2. **Main Scraper Service** (`automated_building_scraper.py`)
   - Coordinates all building scrapers
   - Compares scraped listings with database
   - Automatically adds new listings
   - Logs all activity

3. **Building-Specific Scrapers**
   - `MaltDriveScraper` - For Malt Drive buildings
   - `WindsorCommunitiesScraper` - For Windsor properties
   - Extensible for new buildings

4. **Scheduler** (`setup_scraper_cron.sh`)
   - Cron job to run scraper daily
   - Default: 3:00 AM every day
   - Logs to `/app/logs/scraper_cron.log`

---

## Setup Instructions

### 1. Review Configuration

Edit `/app/building_scraper_config.json`:

```json
{
  "scrapers": [
    {
      "building_id": "ec2ae99d-4083-44b1-81ec-0241cf5d54a6",
      "building_name": "Malt Drive 2-21",
      "enabled": true,
      "scrape_frequency_hours": 24,
      "source_config": {
        "listings_url": "https://maltdrive.com/availability/"
      }
    }
  ]
}
```

**Key fields:**
- `enabled`: Set to `true` to activate scraper
- `scrape_frequency_hours`: How often to check (in hours)
- `source_config`: Building-specific URLs and settings

### 2. Install Cron Job

```bash
cd /app
./setup_scraper_cron.sh
```

This sets up a daily job at 3:00 AM to automatically check for new listings.

### 3. Test Manually

```bash
python3 /app/automated_building_scraper.py
```

---

## How It Works

### Workflow

1. **Scheduled Run** (Daily at 3 AM)
   - Cron job triggers the scraper service

2. **For Each Enabled Building:**
   - Check if enough time has passed since last scrape
   - Fetch the building's availability page
   - Extract all current listings
   - Compare with database to find NEW listings
   - Add new listings automatically
   - Update building statistics

3. **Logging & Notifications**
   - All activity logged to `/app/logs/building_scraper.log`
   - Scrape results stored in MongoDB `scraper_logs` collection
   - Can be extended to send email notifications

---

## Adding New Buildings

### Step 1: Add to Configuration

Edit `building_scraper_config.json` and add a new building:

```json
{
  "building_id": "your-building-id",
  "building_name": "Your Building Name",
  "address": "123 Main St",
  "neighborhood": "Chelsea",
  "borough": "Manhattan",
  "enabled": true,
  "scrape_frequency_hours": 24,
  "source_type": "your_website_type",
  "source_config": {
    "base_url": "https://yourbuilding.com",
    "listings_url": "https://yourbuilding.com/availability/"
  }
}
```

### Step 2: Implement Building-Specific Scraper

Create a new scraper class in `automated_building_scraper.py`:

```python
class YourBuildingScraper(BuildingScraper):
    """Scraper for Your Building"""
    
    def extract_listings(self) -> List[Dict[str, Any]]:
        """Extract listings from website"""
        listings = []
        
        # 1. Fetch the availability page
        html = self.fetch_page(self.config['source_config']['listings_url'])
        
        # 2. Parse HTML to extract listings
        soup = BeautifulSoup(html, 'html.parser')
        
        # 3. Find listing elements (adjust selectors)
        listing_blocks = soup.find_all('div', class_='apartment-card')
        
        for block in listing_blocks:
            listing = {
                'unit_number': block.find('span', class_='unit').text,
                'bedrooms': int(block.find('span', class_='beds').text),
                'bathrooms': float(block.find('span', class_='baths').text),
                'price': float(block.find('span', class_='price').text.replace('$', '').replace(',', '')),
                'sqft': int(block.find('span', class_='sqft').text),
                'title': f"Apartment at {self.building_name}",
                'description': block.find('div', class_='description').text,
                'images': [img['src'] for img in block.find_all('img')],
                'amenities': [li.text for li in block.find('ul', class_='amenities').find_all('li')],
                'source_url': block.find('a')['href']
            }
            listings.append(listing)
        
        return listings
```

### Step 3: Register the Scraper

Add to the `scraper_classes` dictionary in `AutomatedScraperService.initialize_scrapers()`:

```python
scraper_classes = {
    'maltdrive': MaltDriveScraper,
    'windsor': WindsorCommunitiesScraper,
    'your_website_type': YourBuildingScraper  # Add this line
}
```

---

## Configuration Options

### Global Settings

```json
"global_settings": {
  "user_agent": "Mozilla/5.0 ...",
  "request_delay_seconds": 2,
  "max_retries": 3,
  "timeout_seconds": 30,
  "notification_email": "placesfirm@gmail.com"
}
```

### Per-Building Settings

- `enabled`: Enable/disable scraper
- `scrape_frequency_hours`: Minimum hours between scrapes
- `source_type`: Scraper implementation to use
- `source_config`: Building-specific URLs and parameters

---

## Monitoring & Logs

### View Logs

```bash
# Real-time monitoring
tail -f /app/logs/building_scraper.log

# Cron job logs
tail -f /app/logs/scraper_cron.log
```

### Check Scraper History

Query MongoDB to see past scraper runs:

```python
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/nofeeplaces_database')
db = client["nofeeplaces_database"]

# Get last 10 scraper runs
logs = db.scraper_logs.find().sort('timestamp', -1).limit(10)
for log in logs:
    print(f"{log['timestamp']}: {log['building_name']} - {log['new_listings_found']} new listings")
```

---

## Cron Job Management

### View Current Cron Jobs
```bash
crontab -l
```

### Edit Cron Schedule
```bash
crontab -e
```

Common schedules:
- `0 3 * * *` - Daily at 3 AM
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 0` - Weekly on Sunday midnight
- `0 2 * * 1-5` - Weekdays at 2 AM

### Remove Cron Job
```bash
crontab -l | grep -v "automated_building_scraper" | crontab -
```

---

## Manual Operations

### Run Scraper Immediately
```bash
cd /app
python3 automated_building_scraper.py
```

### Test Specific Building
```python
from automated_building_scraper import AutomatedScraperService

service = AutomatedScraperService()
# Run specific scraper
result = service.scrapers[0].run()
print(result)
```

### Check Last Scrape Time
```python
import json
with open('/app/building_scraper_config.json', 'r') as f:
    config = json.load(f)
    
for scraper in config['scrapers']:
    print(f"{scraper['building_name']}: {scraper.get('last_scraped', 'Never')}")
```

---

## Troubleshooting

### Scraper Not Running
1. Check if cron job is installed: `crontab -l`
2. Check cron service: `service cron status`
3. Review logs: `tail -100 /app/logs/scraper_cron.log`

### No New Listings Found
1. Check if scraper is enabled in config
2. Verify `scrape_frequency_hours` - may be too recent
3. Check if website structure changed
4. Review scraper logs for errors

### Website Changed Structure
1. Inspect the website HTML
2. Update CSS selectors in scraper implementation
3. Test with manual run
4. Update configuration if needed

---

## Future Enhancements

### Potential Features
- Email notifications for new listings
- Slack/Discord webhooks
- Web dashboard to view scraper status
- Image downloading and storage
- Price change detection
- Listing removal detection (no longer available)
- Multi-language support
- API endpoint to trigger scraping

---

## Example: Complete Building Addition

Let's say you want to add "The Chelsea" building:

1. **Get Building ID from Database**
```python
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/nofeeplaces_database')
db = client["nofeeplaces_database"]

building = db.buildings.find_one({'building_name': 'The Chelsea'})
building_id = building['building_id']
```

2. **Add to Config**
```json
{
  "building_id": "chelsea-building-id",
  "building_name": "The Chelsea",
  "address": "123 Chelsea St",
  "neighborhood": "Chelsea",
  "borough": "Manhattan",
  "enabled": true,
  "scrape_frequency_hours": 24,
  "source_type": "chelsea_website",
  "source_config": {
    "base_url": "https://thechelseanyc.com",
    "listings_url": "https://thechelseanyc.com/apartments/"
  }
}
```

3. **Implement Scraper**
4. **Test**
5. **Enable Cron Job**

---

## Support

For questions or issues:
- Review logs: `/app/logs/building_scraper.log`
- Check configuration: `/app/building_scraper_config.json`
- Test manually: `python3 /app/automated_building_scraper.py`
