import json
import os
import time
from typing import Dict, List, Any
import logging
import datetime

from config import DATA_DIR, RESULTS_DIR
import database as db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_data_directories():
    """Ensure all required data directories exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Setup database
    db.setup_database()

def save_domain_test_results(results: Dict) -> bool:
    """
    Save domain test results to the database.
    
    Args:
        results: Dictionary containing test results for a domain
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        # Use database module to save results
        success = db.save_test_results(results)
        
        if success:
            domain = results.get("domain", "unknown")
            logger.info(f"Saved test results for domain: {domain}")
        
        return success
    
    except Exception as e:
        logger.error(f"Error saving test results: {e}")
        return False

def load_domain_test_results(domain: str) -> List[Dict]:
    """
    Load all test results for a specific domain.
    
    Args:
        domain: The domain name to load results for
        
    Returns:
        List of result dictionaries sorted by timestamp (newest first)
    """
    try:
        # Use database module to get domain history
        results = db.get_domain_history(domain)
        
        if not results:
            logger.warning(f"No test results found for domain: {domain}")
            return []
        
        return results
    
    except Exception as e:
        logger.error(f"Error loading test results for {domain}: {e}")
        return []

def get_latest_domain_result(domain: str) -> Dict:
    """
    Get the most recent test result for a domain.
    
    Args:
        domain: The domain name
        
    Returns:
        Dictionary with the latest result or empty dict if none found
    """
    try:
        # Use database module to get latest result
        return db.get_latest_domain_result(domain)
    except Exception as e:
        logger.error(f"Error getting latest result for {domain}: {e}")
        return {}

def save_trends_data(trends_data: Dict) -> bool:
    """
    Save global trends data to the database.
    
    Args:
        trends_data: Dictionary containing trend data
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        # Use database module to save trends data
        return db.save_trends_data(trends_data)
    
    except Exception as e:
        logger.error(f"Error saving trends data: {e}")
        return False

def load_trends_data() -> Dict:
    """
    Load global trends data from the database.
    
    Returns:
        Dictionary containing trend data
    """
    try:
        # Use database module to load trends data
        return db.load_trends_data()
    
    except Exception as e:
        logger.error(f"Error loading trends data: {e}")
        return {
            "last_updated": time.time(),
            "error": str(e),
            "top_domains": [],
            "movers": [],
            "invisible_sites": [],
            "category_stats": {}
        }

def load_all_domains() -> Dict[str, List[Dict]]:
    """
    Load all domains from the database.
    
    Returns:
        Dictionary mapping categories to lists of domain dictionaries
    """
    try:
        # Use database module to load domains by category
        return db.load_domains_by_category()
    
    except Exception as e:
        logger.error(f"Error loading domains: {e}")
        return {}

def get_all_tested_domains() -> List[str]:
    """
    Get a list of all domains that have been tested.
    
    Returns:
        List of domain names
    """
    try:
        # Use database module to get all tested domains
        return db.get_all_tested_domains()
    
    except Exception as e:
        logger.error(f"Error getting tested domains: {e}")
        return []

def get_domain_status_summary() -> Dict:
    """
    Get a summary of domain testing status.
    
    Returns:
        Dictionary with counts of domains discovered, tested, etc.
    """
    try:
        # Use database module to get domain status summary
        return db.get_domain_status_summary()
    
    except Exception as e:
        logger.error(f"Error getting domain status summary: {e}")
        return {
            "error": str(e),
            "total_discovered": 0,
            "total_tested": 0,
            "categories": {},
            "last_updated": time.time()
        }

def format_timestamp(timestamp: float) -> str:
    """
    Format a timestamp for display.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Formatted date/time string
    """
    try:
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Unknown"

if __name__ == "__main__":
    # Test the module
    ensure_data_directories()
    
    # Test saving and loading
    sample_result = {
        "domain": "example.com",
        "category": "electronics",
        "visibility_score": 75,
        "timestamp": time.time()
    }
    
    save_domain_test_results(sample_result)
    loaded = load_domain_test_results("example.com")
    print(f"Saved and loaded result for example.com: {json.dumps(loaded, indent=2)}")
    
    # Test trends
    sample_trends = {
        "top_domains": [{"domain": "example.com", "score": 75}],
        "movers": [{"domain": "example.com", "delta": 5.0}],
        "last_updated": time.time()
    }
    
    save_trends_data(sample_trends)
    loaded_trends = load_trends_data()
    print(f"Saved and loaded trends: {json.dumps(loaded_trends, indent=2)}")
