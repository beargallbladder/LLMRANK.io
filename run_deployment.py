"""
LLMPageRank Production Deployment Runner

This script launches the LLMPageRank production environment with all features:
- Competitive Sector Analysis
- FOMA Insight Engine
- Agent Runtime Monitoring
- Vibe Industry Analysis
- Runtime Cadence Management
"""

import os
import sys
import logging
import time
import json
from datetime import datetime
import threading

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Ensure required directories exist
DATA_DIR = "data"
SYSTEM_FEEDBACK_DIR = f"{DATA_DIR}/system_feedback"
INSIGHTS_DIR = f"{DATA_DIR}/insights"
STORIES_DIR = f"{DATA_DIR}/stories"
TRENDS_DIR = f"{DATA_DIR}/trends"
DOMAINS_DIR = f"{DATA_DIR}/domains"
COMPETITIVE_DIR = f"{DATA_DIR}/competitive_sectors"
AGENT_LOGS_DIR = "agents/logs"

# Create directories
for directory in [
    DATA_DIR, 
    SYSTEM_FEEDBACK_DIR, 
    INSIGHTS_DIR, 
    STORIES_DIR, 
    TRENDS_DIR, 
    DOMAINS_DIR,
    COMPETITIVE_DIR,
    AGENT_LOGS_DIR
]:
    os.makedirs(directory, exist_ok=True)


def initialize_database():
    """Initialize database connection."""
    try:
        import psycopg2
        from psycopg2 import sql
        import os
        
        # Get database URL from environment
        db_url = os.environ.get("DATABASE_URL")
        
        if not db_url:
            logger.error("DATABASE_URL not found in environment variables")
            return False
        
        # Connect to database
        conn = psycopg2.connect(db_url)
        
        logger.info("Successfully connected to database")
        
        # Create tables if they don't exist
        with conn.cursor() as cur:
            # Domains table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS domains (
                    id SERIAL PRIMARY KEY,
                    domain VARCHAR(255) NOT NULL UNIQUE,
                    category VARCHAR(50) NOT NULL,
                    trust_score REAL,
                    citation_rate REAL,
                    quality_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Trust signals table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS trust_signals (
                    id SERIAL PRIMARY KEY,
                    domain_id INTEGER REFERENCES domains(id),
                    trust_score REAL NOT NULL,
                    previous_score REAL,
                    delta REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insights table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS insights (
                    id SERIAL PRIMARY KEY,
                    domain_id INTEGER REFERENCES domains(id),
                    category VARCHAR(50) NOT NULL,
                    insight_type VARCHAR(50) NOT NULL,
                    trust_delta REAL,
                    clarity_score REAL,
                    impact_score REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Competitive sectors table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS competitive_sectors (
                    id SERIAL PRIMARY KEY,
                    sector_id VARCHAR(50) NOT NULL UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    critical_capabilities JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Commit changes
            conn.commit()
        
        logger.info("Database tables created or verified")
        
        return True
    
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def start_streamlit_server():
    """Start Streamlit server in a separate process."""
    try:
        import subprocess
        
        logger.info("Starting Streamlit server...")
        
        # Start Streamlit server
        process = subprocess.Popen(
            ["streamlit", "run", "app.py", "--server.port", "5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Monitor for startup
        for line in process.stdout:
            logger.info(f"Streamlit: {line.strip()}")
            if "You can now view your Streamlit app in your browser" in line:
                break
        
        logger.info("Streamlit server started successfully")
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to start Streamlit server: {e}")
        return False


def start_api_server():
    """Start FastAPI server in a separate process."""
    try:
        import subprocess
        
        logger.info("Starting API server...")
        
        # Start API server
        process = subprocess.Popen(
            ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8080"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it time to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            logger.info("API server started successfully")
            return True
        else:
            stdout, stderr = process.communicate()
            logger.error(f"API server failed to start: {stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        return False


def initialize_agents():
    """Initialize agent system."""
    try:
        import agent_monitor
        import agent_survival_loop
        
        logger.info("Initializing agent monitoring system...")
        
        # Simulate agent initialization
        agents = [
            "scan_scheduler.agent",
            "prompt_optimizer.agent",
            "benchmark_validator.agent",
            "insight_monitor.agent",
            "trust_drift.agent",
            "scorecard_writer.agent",
            "integration_tester.agent",
            "api_validator.agent",
            "revalidator.agent",
            "foma_writer.agent"
        ]
        
        # Create agent log directories
        for agent in agents:
            agent_log_dir = os.path.join(AGENT_LOGS_DIR, agent)
            os.makedirs(agent_log_dir, exist_ok=True)
            logger.info(f"Created log directory for {agent}: {agent_log_dir}")
        
        logger.info("Agent system initialized successfully")
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to initialize agent system: {e}")
        return False


def initialize_competitive_sectors():
    """Initialize competitive sector tracking."""
    try:
        import competitive_sectors
        
        logger.info("Initializing competitive sector tracking...")
        
        # Get sector tracker
        tracker = competitive_sectors.get_competitive_tracker()
        
        # Run initial scans
        scan_results = competitive_sectors.simulate_trust_scans(20)
        
        logger.info(f"Completed {len(scan_results)} initial trust scans")
        
        # Get overview of sectors
        all_domains = competitive_sectors.get_all_domains()
        
        logger.info(f"Tracking {len(all_domains)} domains across 10 competitive sectors")
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to initialize competitive sectors: {e}")
        return False


def run_health_check():
    """Run system health check."""
    try:
        # Verify directories
        for directory in [
            DATA_DIR, 
            SYSTEM_FEEDBACK_DIR, 
            INSIGHTS_DIR, 
            STORIES_DIR, 
            TRENDS_DIR, 
            DOMAINS_DIR,
            COMPETITIVE_DIR,
            AGENT_LOGS_DIR
        ]:
            if not os.path.exists(directory):
                logger.error(f"Directory not found: {directory}")
                return False
        
        # Check for required files
        required_modules = [
            "app.py",
            "api_server.py",
            "agent_monitor.py",
            "foma_publisher.py",
            "competitive_sectors.py"
        ]
        
        for module in required_modules:
            if not os.path.exists(module):
                logger.error(f"Required module not found: {module}")
                return False
        
        # Check environment variables
        required_env_vars = ["DATABASE_URL", "OPENAI_API_KEY"]
        
        for env_var in required_env_vars:
            if not os.environ.get(env_var):
                logger.error(f"Required environment variable not found: {env_var}")
                return False
        
        logger.info("System health check passed")
        
        return True
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False


def main():
    """Main deployment function."""
    logger.info("Starting LLMPageRank deployment")
    
    # Run health check
    if not run_health_check():
        logger.error("Health check failed, aborting deployment")
        return False
    
    # Initialize database
    if not initialize_database():
        logger.error("Database initialization failed, aborting deployment")
        return False
    
    # Initialize agents
    if not initialize_agents():
        logger.error("Agent initialization failed, aborting deployment")
        return False
    
    # Initialize competitive sectors
    if not initialize_competitive_sectors():
        logger.error("Competitive sector initialization failed, aborting deployment")
        return False
    
    # Start API server
    if not start_api_server():
        logger.error("API server failed to start, aborting deployment")
        return False
    
    # Start Streamlit server
    if not start_streamlit_server():
        logger.error("Streamlit server failed to start, aborting deployment")
        return False
    
    logger.info("LLMPageRank deployment completed successfully")
    
    # Keep running
    while True:
        time.sleep(60)
        logger.info("Deployment running...")


if __name__ == "__main__":
    main()