"""
Scheduled Domain Data Collection

This script sets up a scheduled job to collect domain ranking data from LLMs
on a regular basis. It uses the domain_data_collector module to gather data
and stores the results.
"""

import os
import json
import logging
import schedule
import time
import datetime
from typing import Dict, List, Optional
import domain_data_collector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/logs/domain_collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs("data/logs", exist_ok=True)

def run_collection_job():
    """Run a data collection job for all categories."""
    try:
        logger.info("Starting scheduled domain data collection")
        
        # Get timestamp for the collection
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Run collection for all default categories
        categories = domain_data_collector.CATEGORIES
        
        logger.info(f"Collecting data for {len(categories)} categories")
        
        results = domain_data_collector.collect_all_categories()
        
        # Save results to a timestamped file
        results_dir = "data/collection_results"
        os.makedirs(results_dir, exist_ok=True)
        
        results_file = f"{results_dir}/collection_{timestamp}.json"
        
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Collection completed successfully. Results saved to {results_file}")
        
        # Log summary statistics
        domain_count = 0
        for category_result in results:
            for model, model_result in category_result.get("results", {}).items():
                domain_count += len(model_result.get("domains", []))
        
        logger.info(f"Collected {domain_count} domain rankings across {len(categories)} categories")
        
        return True
    except Exception as e:
        logger.error(f"Error in collection job: {str(e)}")
        return False

def setup_schedule(daily_time="00:00", hourly=False, weekly_day=None):
    """
    Set up the collection schedule.
    
    Args:
        daily_time: Time of day for daily collection (HH:MM format)
        hourly: Whether to also collect hourly
        weekly_day: Day of week for weekly collection (0-6, where 0 is Monday)
    """
    logger.info(f"Setting up domain collection schedule: daily at {daily_time}, hourly: {hourly}, weekly_day: {weekly_day}")
    
    # Schedule daily collection
    schedule.every().day.at(daily_time).do(run_collection_job)
    logger.info(f"Scheduled daily collection at {daily_time}")
    
    # Schedule hourly collection if requested
    if hourly:
        schedule.every().hour.do(run_collection_job)
        logger.info("Scheduled hourly collection")
    
    # Schedule weekly collection if day specified
    if weekly_day is not None:
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if 0 <= weekly_day <= 6:
            day_name = days[weekly_day]
            getattr(schedule.every(), day_name).at(daily_time).do(run_collection_job)
            logger.info(f"Scheduled weekly collection on {day_name} at {daily_time}")
    
    logger.info("Schedule setup complete")

def run_scheduler():
    """Run the scheduler loop."""
    logger.info("Starting scheduler loop")
    
    # Run an initial collection
    logger.info("Running initial collection")
    run_collection_job()
    
    # Run the scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Configure the schedule
    setup_schedule(daily_time="00:00", hourly=False, weekly_day=0)  # Daily at midnight, weekly on Monday
    
    # Run the scheduler loop
    try:
        run_scheduler()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Error in scheduler: {str(e)}")