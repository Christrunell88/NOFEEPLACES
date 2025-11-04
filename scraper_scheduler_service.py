#!/usr/bin/env python3
"""
Building Scraper Scheduler Service
Runs as a background service managed by supervisor
Executes the automated building scraper every 36 hours
"""

import sys
import time
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/scraper_scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def run_scraper():
    """Execute the automated building scraper"""
    try:
        logger.info("=" * 60)
        logger.info("Starting automated building scraper run")
        logger.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        logger.info("=" * 60)
        
        # Import and run the scraper
        import subprocess
        result = subprocess.run(
            [sys.executable, '/app/automated_building_scraper.py'],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )
        
        # Log output
        if result.stdout:
            logger.info("Scraper Output:")
            logger.info(result.stdout)
        
        if result.stderr:
            logger.error("Scraper Errors:")
            logger.error(result.stderr)
        
        if result.returncode == 0:
            logger.info("✅ Scraper completed successfully")
        else:
            logger.error(f"❌ Scraper failed with return code: {result.returncode}")
            
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error running scraper: {str(e)}", exc_info=True)


def main():
    """Main scheduler service"""
    try:
        # Create logs directory
        import os
        os.makedirs('/app/logs', exist_ok=True)
        
        logger.info("🚀 Starting Building Scraper Scheduler Service")
        logger.info("Schedule: Every 36 hours")
        logger.info("=" * 60)
        
        # Create scheduler
        scheduler = BlockingScheduler()
        
        # Add job to run every 36 hours
        scheduler.add_job(
            run_scraper,
            trigger=IntervalTrigger(hours=36),
            id='building_scraper',
            name='Automated Building Scraper',
            replace_existing=True,
            next_run_time=datetime.now(timezone.utc)  # Run immediately on startup
        )
        
        logger.info("📅 Scheduler configured successfully")
        logger.info("Next run scheduled immediately, then every 36 hours")
        logger.info("Press Ctrl+C to stop (but don't - supervisor manages this)")
        logger.info("=" * 60)
        
        # Start the scheduler (blocking)
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"❌ Scheduler error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
