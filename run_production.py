"""
Production Runner for LLMPageRank V10

This script starts the LLMPageRank V10 system in production mode,
initializing all required components and launching the server.
"""

import os
import sys
import threading
import time
import logging
import subprocess
import importlib

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_step(step_name, step_function, *args, **kwargs):
    """Run a setup step with proper logging."""
    logger.info(f"Starting {step_name}...")
    try:
        result = step_function(*args, **kwargs)
        logger.info(f"Completed {step_name} successfully")
        return result
    except Exception as e:
        logger.error(f"Error in {step_name}: {e}")
        return None

def initialize_database():
    """Initialize the database."""
    from init_db import initialize_database
    return initialize_database()

def initialize_production():
    """Initialize production environment."""
    logger.info("Initializing production environment...")
    
    # Run production setup
    try:
        from production_setup import run_production_setup
        run_production_setup()
    except ImportError:
        logger.error("Production setup module not found")
        return False
    except Exception as e:
        logger.error(f"Error running production setup: {e}")
        return False
    
    return True

def start_api_server():
    """Start the API server in the background."""
    logger.info("Starting API server...")
    
    try:
        from api_server import app
        import uvicorn
        
        # Start API server in a background thread
        def api_server_thread():
            uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
        
        thread = threading.Thread(target=api_server_thread, daemon=True)
        thread.start()
        
        # Give API server time to start
        time.sleep(2)
        
        logger.info("API server started on port 8080")
        return True
    except Exception as e:
        logger.error(f"Error starting API server: {e}")
        return False

def start_streamlit_server():
    """Start the Streamlit server."""
    logger.info("Starting Streamlit server...")
    
    # Start Streamlit server
    try:
        import streamlit.web.cli as stcli
        
        # Use sys.argv to pass arguments to Streamlit
        # Use port 7000 instead of 5000 to avoid conflicts with other workflows
        sys.argv = ["streamlit", "run", "app.py", "--server.port=7000", "--server.address=0.0.0.0"]
        
        # Run Streamlit
        stcli.main()
        
        return True
    except Exception as e:
        logger.error(f"Error starting Streamlit server: {e}")
        return False

def main():
    """Main function to run LLMPageRank in production mode."""
    logger.info("Starting LLMPageRank V10 in production mode...")
    
    # Step 1: Initialize database
    run_step("database initialization", initialize_database)
    
    # Step 2: Initialize production environment
    production_ready = run_step("production initialization", initialize_production)
    if not production_ready:
        logger.error("Failed to initialize production environment. Exiting.")
        return
    
    # Step 3: Start API server
    api_ready = run_step("API server startup", start_api_server)
    if not api_ready:
        logger.warning("API server failed to start. Continuing with limited functionality.")
    
    # Step 4: Start Streamlit server
    run_step("Streamlit server startup", start_streamlit_server)

if __name__ == "__main__":
    main()