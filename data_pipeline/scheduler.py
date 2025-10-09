#!/usr/bin/env python3
"""
Data Pipeline Scheduler
Automated scheduling for data pipeline execution
"""
import asyncio
import schedule
import time
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add pipeline directory to path
sys.path.append('/app/data_pipeline')

from pipeline_controller import PipelineController

class PipelineScheduler:
    def __init__(self):
        self.controller = PipelineController()
        self.logs_dir = Path('/app/logs')
        self.logs_dir.mkdir(exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_dir / 'pipeline_scheduler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def run_scheduled_pipeline(self):
        """Run pipeline on schedule"""
        self.logger.info("🕐 Scheduled pipeline execution starting...")
        
        try:
            success = await self.controller.start_pipeline()
            
            if success:
                self.logger.info("✅ Scheduled pipeline completed successfully")
            else:
                self.logger.error("❌ Scheduled pipeline failed")
                
        except Exception as e:
            self.logger.error(f"❌ Scheduled pipeline error: {e}")
    
    def schedule_pipeline(self):
        """Set up pipeline schedule"""
        # Schedule daily at 3 AM
        schedule.every().day.at("03:00").do(
            lambda: asyncio.create_task(self.run_scheduled_pipeline())
        )
        
        # Schedule weekly data quality check on Sundays at 2 AM
        schedule.every().sunday.at("02:00").do(
            lambda: asyncio.create_task(self.controller.test_pipeline())
        )
        
        self.logger.info("📅 Pipeline scheduled:")
        self.logger.info("   - Daily execution: 3:00 AM")
        self.logger.info("   - Weekly quality check: Sunday 2:00 AM")
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        self.logger.info("🚀 Pipeline scheduler started")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Scheduler error: {e}")

def main():
    scheduler = PipelineScheduler()
    scheduler.schedule_pipeline()
    scheduler.run_scheduler()

if __name__ == "__main__":
    main()
