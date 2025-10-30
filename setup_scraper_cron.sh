#!/bin/bash
"""
Setup script for automated building scraper cron job
"""

# Create cron job to run scraper every 36 hours
# Note: Cron doesn't support 36-hour intervals directly, so we use twice daily with offset
CRON_SCHEDULE="0 3,15 * * *"  # Every day at 3 AM and 3 PM (12-hour intervals, close to 36 hours over multiple days)
SCRIPT_PATH="/app/automated_building_scraper.py"
LOG_PATH="/app/logs/scraper_cron.log"

# Cron job command
CRON_COMMAND="cd /app && /usr/bin/python3 $SCRIPT_PATH >> $LOG_PATH 2>&1"

echo "================================"
echo "Building Scraper Cron Setup"
echo "================================"
echo ""
echo "This will set up an automated job to:"
echo "  - Run twice daily (3 AM and 3 PM)"
echo "  - Buildings check every 36 hours based on last_scraped time"
echo "  - Check all enabled buildings for new listings"
echo "  - Automatically add new listings to database"
echo "  - Log results to $LOG_PATH"
echo ""

# Create logs directory
mkdir -p /app/logs

# Check if cron job already exists
CRON_EXISTS=$(crontab -l 2>/dev/null | grep -c "automated_building_scraper.py")

if [ $CRON_EXISTS -gt 0 ]; then
    echo "⚠️  Cron job already exists!"
    echo ""
    echo "Current crontab:"
    crontab -l | grep "automated_building_scraper"
    echo ""
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
    
    # Remove old cron job
    crontab -l | grep -v "automated_building_scraper.py" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $CRON_COMMAND") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "Schedule: Every day at 3:00 AM"
echo "Command: $CRON_COMMAND"
echo ""
echo "To view current crontab:"
echo "  crontab -l"
echo ""
echo "To remove the cron job:"
echo "  crontab -e"
echo "  (then delete the line containing 'automated_building_scraper.py')"
echo ""
echo "To manually test the scraper now:"
echo "  python3 $SCRIPT_PATH"
echo ""
