"""
Indexwide Category Agent Coordinator
Codename: "Go Wider"

This script coordinates the execution of the three agent classes:
1. IndexScan-A1: Collects company lists, metadata, and competitor graphs.
2. SurfaceSeed-B1: Generates minimal viable insight "Surface" pages.
3. DriftPulse-C1: Detects and benchmarks signal differentials.
"""

import os
import json
import logging
import datetime
import time
import argparse
from typing import Dict, List, Optional, Any

# Import agent modules
import agents.index_scan as index_scan
import agents.surface_seed as surface_seed
import agents.drift_pulse as drift_pulse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
RESULTS_DIR = "data/indexwide"
SUMMARY_PATH = f"{RESULTS_DIR}/execution_summary.json"

# Ensure directories exist
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_index_scan():
    """Run the IndexScan agent."""
    logger.info("==================== STARTING INDEX SCAN ====================")
    start_time = datetime.datetime.now()
    
    try:
        summary = index_scan.run()
        logger.info(f"IndexScan completed: {summary['total_companies_processed']} companies processed")
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "status": "success",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error running IndexScan: {e}")
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "status": "error",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "error": str(e)
        }

def run_surface_seed():
    """Run the SurfaceSeed agent."""
    logger.info("==================== STARTING SURFACE SEED ====================")
    start_time = datetime.datetime.now()
    
    try:
        summary = surface_seed.run()
        logger.info(f"SurfaceSeed completed: {summary.get('successful_surfaces', 0)} surfaces created")
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "status": "success",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error running SurfaceSeed: {e}")
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "status": "error",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "error": str(e)
        }

def run_drift_pulse():
    """Run the DriftPulse agent."""
    logger.info("==================== STARTING DRIFT PULSE ====================")
    start_time = datetime.datetime.now()
    
    try:
        summary = drift_pulse.run()
        logger.info(f"DriftPulse completed: {summary.get('rivalries_found', 0)} rivalries analyzed")
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "status": "success",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error running DriftPulse: {e}")
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "status": "error",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "error": str(e)
        }

def run_full_indexwide_scan(wait_period: int = 0):
    """
    Run the full indexwide scan process.
    
    Args:
        wait_period: Time to wait between agents (in seconds)
        
    Returns:
        Execution summary
    """
    overall_start_time = datetime.datetime.now()
    logger.info(f"Starting full indexwide scan at {overall_start_time.isoformat()}")
    
    # Run IndexScan-A1
    index_scan_result = run_index_scan()
    
    if wait_period > 0:
        logger.info(f"Waiting {wait_period} seconds before starting SurfaceSeed...")
        time.sleep(wait_period)
    
    # Run SurfaceSeed-B1
    surface_seed_result = run_surface_seed()
    
    if wait_period > 0:
        logger.info(f"Waiting {wait_period} seconds before starting DriftPulse...")
        time.sleep(wait_period)
    
    # Run DriftPulse-C1
    drift_pulse_result = run_drift_pulse()
    
    # Calculate overall statistics
    overall_end_time = datetime.datetime.now()
    overall_duration = (overall_end_time - overall_start_time).total_seconds()
    
    # Prepare execution summary
    execution_summary = {
        "overall_start_time": overall_start_time.isoformat(),
        "overall_end_time": overall_end_time.isoformat(),
        "overall_duration_seconds": overall_duration,
        "index_scan_result": index_scan_result,
        "surface_seed_result": surface_seed_result,
        "drift_pulse_result": drift_pulse_result,
        "wait_period_seconds": wait_period
    }
    
    # Save execution summary
    with open(SUMMARY_PATH, 'w') as f:
        json.dump(execution_summary, f, indent=2)
    
    logger.info(f"Full indexwide scan completed in {overall_duration:.2f} seconds")
    logger.info(f"Execution summary saved to {SUMMARY_PATH}")
    
    return execution_summary

def main():
    """Main function to parse arguments and run the indexwide scan."""
    parser = argparse.ArgumentParser(description="Run the Indexwide Category Agent Coordinator")
    parser.add_argument("--wait", type=int, default=0, help="Time to wait between agents (in seconds)")
    parser.add_argument("--index-scan-only", action="store_true", help="Run only the IndexScan agent")
    parser.add_argument("--surface-seed-only", action="store_true", help="Run only the SurfaceSeed agent")
    parser.add_argument("--drift-pulse-only", action="store_true", help="Run only the DriftPulse agent")
    
    args = parser.parse_args()
    
    if args.index_scan_only:
        run_index_scan()
    elif args.surface_seed_only:
        run_surface_seed()
    elif args.drift_pulse_only:
        run_drift_pulse()
    else:
        run_full_indexwide_scan(wait_period=args.wait)
    
    logger.info("Process completed")

if __name__ == "__main__":
    main()