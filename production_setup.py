"""
Production Setup for LLMPageRank V10

This script initializes and configures the LLMPageRank V10 system for production,
including database setup, agent registry initialization, and system health monitoring.
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
import psycopg2
import requests

# Import project modules
from config import DATA_DIR, SYSTEM_VERSION
from agent_monitor import get_registry
import agent_monitor
import dispatcher

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SYSTEM_FEEDBACK_DIR = f"{DATA_DIR}/system_feedback"
ADMIN_INSIGHT_DIR = f"{DATA_DIR}/admin_insight_console"

def create_required_directories():
    """Create all required directories."""
    logger.info("Creating required directories...")
    
    directories = [
        DATA_DIR,
        f"{DATA_DIR}/prompts",
        f"{DATA_DIR}/results",
        f"{DATA_DIR}/insights",
        f"{DATA_DIR}/trends",
        SYSTEM_FEEDBACK_DIR,
        ADMIN_INSIGHT_DIR,
        "agents/logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Create log directories for each agent
    registry = get_registry()
    agents = registry.get("agents", [])
    
    for agent in agents:
        agent_name = agent.get("agent_name", "")
        if agent_name:
            log_dir = f"agents/logs/{agent_name}"
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"Created log directory for {agent_name}: {log_dir}")

def validate_database_connection():
    """Validate database connection."""
    logger.info("Validating database connection...")
    
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL not found in environment variables")
        return False
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if db_version and len(db_version) > 0:
            logger.info(f"Successfully connected to database: {db_version[0]}")
        else:
            logger.info("Successfully connected to database, but version info not available")
        
        return True
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return False

def initialize_system_health():
    """Initialize system health monitoring."""
    logger.info("Initializing system health monitoring...")
    
    # Create initial system health file if it doesn't exist
    system_health_file = f"{ADMIN_INSIGHT_DIR}/system_health.json"
    
    if not os.path.exists(system_health_file):
        logger.info("Creating initial system health file...")
        
        registry = get_registry()
        agents = registry.get("agents", [])
        
        active_agents = sum(1 for a in agents if a.get("status") == "active")
        dormant_agents = sum(1 for a in agents if a.get("status") == "dormant")
        
        # Get cookie balances
        cookies = [a.get("cookies_last_7d", 0) for a in agents]
        cookie_balance_top = max(cookies) if cookies else 0
        cookie_balance_lowest = min(cookies) if cookies else 0
        
        system_health = {
            "active_agents": active_agents,
            "dormant_agents": dormant_agents,
            "dispatcher_success_rate": 100.0,  # Initial value
            "integration_test_pass_rate": 100.0,  # Initial value
            "cookie_balance_top_agent": cookie_balance_top,
            "cookie_balance_lowest_agent": cookie_balance_lowest,
            "average_run_time_ms": 0,  # Initial value
            "last_updated": time.time()
        }
        
        os.makedirs(os.path.dirname(system_health_file), exist_ok=True)
        with open(system_health_file, 'w') as f:
            json.dump(system_health, f, indent=2)
        
        logger.info(f"System health file created: {system_health_file}")

def initialize_integration_tester():
    """Initialize integration tester agent."""
    logger.info("Initializing integration tester agent...")
    
    # Run integration tester
    try:
        from agents.integration_tester import run
        
        result = run()
        logger.info(f"Integration tester executed: {result.get('status', 'unknown')}")
        
        if result.get("status") != "success":
            logger.warning(f"Integration test failed: {result.get('error', 'unknown error')}")
    except Exception as e:
        logger.error(f"Error running integration tester: {e}")

def initialize_api_validator():
    """Initialize API validator agent."""
    logger.info("Initializing API validator agent...")
    
    # Run API validator
    try:
        from agents.api_validator import run
        
        result = run()
        logger.info(f"API validator executed: {result.get('status', 'unknown')}")
        
        if result.get("status") != "success":
            logger.warning(f"API validation failed: {result.get('error', 'unknown error')}")
    except Exception as e:
        logger.error(f"Error running API validator: {e}")

def update_agent_strata():
    """Update agent strata based on cookies."""
    logger.info("Updating agent strata...")
    
    registry = get_registry()
    agents = registry.get("agents", [])
    updated = False
    
    for agent in agents:
        cookies = agent.get("cookies_last_7d", 0)
        current_strata = agent.get("runtime_strata", "")
        
        if cookies >= 8:
            new_strata = "Gold"
        elif cookies >= 6:
            new_strata = "Silver"
        else:
            new_strata = "Rust"
        
        if new_strata != current_strata:
            agent["runtime_strata"] = new_strata
            updated = True
            logger.info(f"Updated {agent.get('agent_name', '')} strata to {new_strata}")
    
    if updated:
        registry["last_updated"] = time.time()
        with open("agents/registry.json", 'w') as f:
            json.dump(registry, f, indent=2)
        
        logger.info("Agent strata updated in registry")

def setup_daily_scheduler():
    """Setup daily scheduler for agent execution."""
    logger.info("Setting up daily scheduler...")
    
    try:
        import schedule
        import threading
        
        # Schedule hourly integration tests
        def run_hourly_integration_test():
            logger.info("Running scheduled hourly integration test...")
            dispatcher.execute_agents_by_trigger("hourly")
        
        # Schedule bi-hourly API validation
        def run_bihourly_api_validation():
            logger.info("Running scheduled bi-hourly API validation...")
            dispatcher.execute_agents_by_trigger("bi-hourly")
        
        # Schedule daily scan
        def run_daily_scan():
            logger.info("Running scheduled daily scan...")
            dispatcher.execute_agents_by_trigger("daily")
        
        # Schedule weekly validation
        def run_weekly_validation():
            logger.info("Running scheduled weekly validation...")
            dispatcher.execute_agents_by_trigger("weekly")
        
        # Add jobs to schedule
        schedule.every().hour.do(run_hourly_integration_test)
        schedule.every(2).hours.do(run_bihourly_api_validation)
        schedule.every().day.at("02:00").do(run_daily_scan)
        schedule.every().monday.at("03:00").do(run_weekly_validation)
        
        # Run schedule in background thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("Scheduler started in background thread")
    except Exception as e:
        logger.error(f"Error setting up scheduler: {e}")

def run_production_setup():
    """Run production setup."""
    logger.info(f"Starting production setup for LLMPageRank V{SYSTEM_VERSION}...")
    
    # Create required directories
    create_required_directories()
    
    # Validate database connection
    db_valid = validate_database_connection()
    if not db_valid:
        logger.warning("Database validation failed. Some functionality may be limited.")
    
    # Initialize system health monitoring
    initialize_system_health()
    
    # Update agent strata
    update_agent_strata()
    
    # Initialize integration tester
    initialize_integration_tester()
    
    # Initialize API validator
    initialize_api_validator()
    
    # Setup daily scheduler
    setup_daily_scheduler()
    
    logger.info("Production setup completed successfully")

if __name__ == "__main__":
    run_production_setup()