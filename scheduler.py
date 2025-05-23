import asyncio
import threading
import time
import datetime
import logging
from typing import List, Dict, Any
import json
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from domain_discovery import discover_and_categorize_domains, get_domains_for_testing
from llm_testing import test_domains
from citation_analysis import process_test_results
from data_storage import save_domain_test_results, ensure_data_directories, save_trends_data
from config import DAILY_RUN_HOUR, DOMAINS_PER_RUN, DATA_DIR

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler
scheduler = None

# File to store job status
JOB_STATUS_FILE = f"{DATA_DIR}/job_status.json"

def save_job_status(status: Dict) -> None:
    """Save job status to the database."""
    try:
        # Use the database module to save job status
        import database as db
        db.save_job_status(status)
    except Exception as e:
        logger.error(f"Error saving job status: {e}")

def load_job_status() -> Dict:
    """Load job status from the database."""
    try:
        # Use the database module to load job status
        import database as db
        return db.load_job_status()
    except Exception as e:
        logger.error(f"Error loading job status: {e}")
        return {
            "last_run": None,
            "next_run": None,
            "status": "error",
            "domains_discovered": 0,
            "domains_tested": 0,
            "last_error": str(e)
        }

async def run_discovery_job():
    """
    Job to discover and categorize new domains.
    """
    logger.info("Starting domain discovery job")
    
    job_status = load_job_status()
    job_status["status"] = "running_discovery"
    save_job_status(job_status)
    
    try:
        # Discover domains (100 per category)
        discovered_domains = discover_and_categorize_domains(limit_per_category=100)
        
        # Count discovered domains
        total_discovered = sum(len(domains) for category, domains in discovered_domains.items())
        
        # Update job status
        job_status = load_job_status()
        job_status["status"] = "discovery_complete"
        job_status["domains_discovered"] = total_discovered
        job_status["last_run"] = time.time()
        save_job_status(job_status)
        
        logger.info(f"Domain discovery complete. Discovered {total_discovered} domains")
        
    except Exception as e:
        logger.error(f"Error in domain discovery job: {e}")
        
        # Update job status with error
        job_status = load_job_status()
        job_status["status"] = "error"
        job_status["last_error"] = str(e)
        save_job_status(job_status)

async def run_testing_job():
    """
    Job to test domains with LLMs.
    """
    logger.info("Starting domain testing job")
    
    job_status = load_job_status()
    job_status["status"] = "running_testing"
    save_job_status(job_status)
    
    try:
        # Get domains for testing
        domains = get_domains_for_testing(limit=DOMAINS_PER_RUN)
        
        if not domains:
            logger.warning("No domains available for testing")
            job_status["status"] = "no_domains"
            save_job_status(job_status)
            return
        
        logger.info(f"Testing {len(domains)} domains")
        
        # Test domains
        test_results = await test_domains(domains)
        
        # Process results and update trends
        processed_results = process_test_results(test_results)
        
        # Update job status
        job_status = load_job_status()
        job_status["status"] = "testing_complete"
        job_status["domains_tested"] = len(domains)
        job_status["last_run"] = time.time()
        save_job_status(job_status)
        
        logger.info(f"Domain testing complete. Tested {len(domains)} domains")
        
    except Exception as e:
        logger.error(f"Error in domain testing job: {e}")
        
        # Update job status with error
        job_status = load_job_status()
        job_status["status"] = "error"
        job_status["last_error"] = str(e)
        save_job_status(job_status)

def run_discovery_task():
    """
    Run the discovery job in the event loop.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_discovery_job())
    loop.close()

def run_testing_task():
    """
    Run the testing job in the event loop.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_testing_job())
    loop.close()

def setup_scheduler():
    """
    Set up the scheduler for automated tasks.
    """
    global scheduler
    
    # Ensure data directories exist
    ensure_data_directories()
    
    # Create a job status file if it doesn't exist
    if not os.path.exists(JOB_STATUS_FILE):
        initial_status = {
            "last_run": None,
            "next_run": None,
            "status": "idle",
            "domains_discovered": 0,
            "domains_tested": 0,
            "last_error": None
        }
        save_job_status(initial_status)
    
    # Create scheduler if it doesn't exist
    if scheduler is None:
        scheduler = BackgroundScheduler()
        
        # Add discovery job (runs daily at specified hour)
        discovery_trigger = CronTrigger(hour=DAILY_RUN_HOUR, minute=0)
        scheduler.add_job(
            run_discovery_task,
            trigger=discovery_trigger,
            id='discovery_job',
            replace_existing=True
        )
        
        # Add testing job (runs every 4 hours)
        testing_trigger = IntervalTrigger(hours=4)
        scheduler.add_job(
            run_testing_task,
            trigger=testing_trigger,
            id='testing_job',
            replace_existing=True
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info("Scheduler started with discovery and testing jobs")
        
        # Update next run time in job status
        job_status = load_job_status()
        discovery_job = scheduler.get_job('discovery_job')
        testing_job = scheduler.get_job('testing_job')
        
        if discovery_job and testing_job:
            next_discovery = discovery_job.next_run_time.timestamp() if discovery_job.next_run_time else None
            next_testing = testing_job.next_run_time.timestamp() if testing_job.next_run_time else None
            
            # Set next run to the earlier of the two jobs
            if next_discovery and next_testing:
                job_status["next_run"] = min(next_discovery, next_testing)
            elif next_discovery:
                job_status["next_run"] = next_discovery
            elif next_testing:
                job_status["next_run"] = next_testing
            
            save_job_status(job_status)
    
    return scheduler

def get_scheduler_status():
    """
    Get the current status of the scheduler and jobs.
    """
    if scheduler is None:
        return {
            "scheduler_running": False,
            "job_status": load_job_status()
        }
    
    discovery_job = scheduler.get_job('discovery_job')
    testing_job = scheduler.get_job('testing_job')
    
    return {
        "scheduler_running": scheduler.running,
        "discovery_job": {
            "id": discovery_job.id if discovery_job else None,
            "next_run": discovery_job.next_run_time.timestamp() if discovery_job and discovery_job.next_run_time else None
        },
        "testing_job": {
            "id": testing_job.id if testing_job else None,
            "next_run": testing_job.next_run_time.timestamp() if testing_job and testing_job.next_run_time else None
        },
        "job_status": load_job_status()
    }

def run_manual_discovery_job():
    """
    Manually trigger a domain discovery job.
    """
    threading.Thread(target=run_discovery_task).start()
    return {"status": "started", "job": "discovery"}

def run_manual_testing_job():
    """
    Manually trigger a domain testing job.
    """
    threading.Thread(target=run_testing_task).start()
    return {"status": "started", "job": "testing"}

if __name__ == "__main__":
    # Test functionality
    setup_scheduler()
    status = get_scheduler_status()
    print(f"Scheduler status: {json.dumps(status, indent=2)}")
    
    # Run a discovery job manually for testing
    run_manual_discovery_job()
