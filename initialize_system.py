"""
Initialize LLMPageRank V2 System

This script will trigger the domain discovery and testing jobs
to populate the system with initial data.
"""

import asyncio
import time
import logging
from datetime import datetime

from scheduler import run_discovery_job, run_testing_job
from database import get_domain_status_summary

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def initialize_system():
    """Run initial discovery and testing jobs"""
    logger.info("Starting LLMPageRank V2 system initialization")
    
    # Get initial status
    initial_status = get_domain_status_summary()
    logger.info(f"Initial status: {initial_status}")
    
    # Run domain discovery job
    logger.info("Running domain discovery job...")
    try:
        await run_discovery_job()
        logger.info("Domain discovery job completed")
    except Exception as e:
        logger.error(f"Error in domain discovery job: {e}")
    
    # Get status after discovery
    discovery_status = get_domain_status_summary()
    logger.info(f"Status after discovery: {discovery_status}")
    
    # Run domain testing job
    logger.info("Running domain testing job...")
    try:
        await run_testing_job()
        logger.info("Domain testing job completed")
    except Exception as e:
        logger.error(f"Error in domain testing job: {e}")
    
    # Get final status
    final_status = get_domain_status_summary()
    logger.info(f"Final status: {final_status}")
    
    # Display summary
    print("\n" + "="*50)
    print("LLMPageRank V2 System Initialization Summary")
    print("="*50)
    print(f"Domains discovered: {final_status.get('total_discovered', 0)}")
    print(f"Domains tested: {final_status.get('total_tested', 0)}")
    print(f"Initialization completed at: {datetime.now()}")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(initialize_system())