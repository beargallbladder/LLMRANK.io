"""
LLMPageRank Database Module

This module provides database functions for storing domain data, test results, and trends.
"""

import os
import json
import time
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Import from project modules
from config import DATA_DIR, RESULTS_DIR, DOMAINS_FILE, TRENDS_FILE, CATEGORIES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure data directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def setup_database():
    """Setup database files if they don't exist."""
    # Create domains file
    if not os.path.exists(DOMAINS_FILE):
        with open(DOMAINS_FILE, 'w') as f:
            json.dump([], f)
    
    # Create trends file
    if not os.path.exists(TRENDS_FILE):
        with open(TRENDS_FILE, 'w') as f:
            json.dump({
                "categories": {},
                "global": {
                    "avg_score": 0,
                    "max_score": 0,
                    "min_score": 0,
                    "top_domains": [],
                    "rising_domains": [],
                    "falling_domains": []
                },
                "last_updated": time.time()
            }, f, indent=2)
    
    logger.info("Database setup complete")
    
    return True

def get_db_connection():
    """
    Get a connection to the database.
    This is a stub function to maintain compatibility with database_v2.py.
    In a production environment, this would return an actual database connection.
    
    Returns:
        Mock database connection for compatibility
    """
    # Create a mock connection object for compatibility
    class MockConnection:
        def cursor(self, cursor_factory=None):
            return MockCursor()
        
        def commit(self):
            pass
        
        def close(self):
            pass
    
    class MockCursor:
        def execute(self, query, params=None):
            pass
        
        def fetchone(self):
            return None
        
        def fetchall(self):
            return []
        
        def close(self):
            pass
        
        @property
        def rowcount(self):
            return 0
    
    logger.info("Using file-based database instead of SQL connection")
    return MockConnection()

def get_all_domains() -> List[Dict]:
    """
    Get all domains from the database.
    
    Returns:
        List of domain dictionaries
    """
    if not os.path.exists(DOMAINS_FILE):
        setup_database()
        return []
    
    try:
        with open(DOMAINS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading domains: {e}")
        return []

def add_domain(domain_data: Dict) -> bool:
    """
    Add a domain to the database.
    
    Args:
        domain_data: Domain data dictionary
        
    Returns:
        Success flag
    """
    domains = get_all_domains()
    
    # Check if domain already exists
    domain_name = domain_data.get("domain", "")
    existing_domains = [d.get("domain", "") for d in domains]
    
    if domain_name in existing_domains:
        # Update existing domain
        for i, domain in enumerate(domains):
            if domain.get("domain", "") == domain_name:
                domains[i] = domain_data
                break
    else:
        # Add new domain
        domains.append(domain_data)
    
    try:
        with open(DOMAINS_FILE, 'w') as f:
            json.dump(domains, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving domain: {e}")
        return False

def get_domain_by_name(domain_name: str) -> Optional[Dict]:
    """
    Get a domain by name.
    
    Args:
        domain_name: Domain name
        
    Returns:
        Domain dictionary or None if not found
    """
    domains = get_all_domains()
    
    for domain in domains:
        if domain.get("domain", "") == domain_name:
            return domain
    
    return None

def get_domain_info(domain_name: str) -> Dict:
    """
    Get domain information by name.
    
    Args:
        domain_name: Domain name
        
    Returns:
        Domain information dictionary or default dictionary if not found
    """
    # Load domains data
    if os.path.exists(DOMAINS_FILE):
        try:
            with open(DOMAINS_FILE, 'r') as f:
                domains_data = json.load(f)
                
            # If the data is a dictionary with domain keys
            if isinstance(domains_data, dict):
                return domains_data.get(domain_name, {"domain": domain_name, "category": "unknown"})
                
            # If the data is a list of domain dictionaries
            elif isinstance(domains_data, list):
                for domain_obj in domains_data:
                    if isinstance(domain_obj, dict) and domain_obj.get("domain") == domain_name:
                        return domain_obj
                        
        except Exception as e:
            logger.error(f"Error loading domain info: {e}")
    
    # Return default if not found
    return {"domain": domain_name, "category": "unknown"}

def get_domains_by_category(category: str) -> List[Dict]:
    """
    Get domains by category.
    
    Args:
        category: Category name
        
    Returns:
        List of domain dictionaries
    """
    domains = get_all_domains()
    result = []
    
    for domain in domains:
        # Handle case where domain might be a string instead of dict
        if isinstance(domain, str):
            domain_obj = get_domain_info(domain)
        else:
            domain_obj = domain
            
        if domain_obj.get("category", "") == category:
            result.append(domain_obj)
            
    return result

def load_domains_by_category() -> Dict[str, List[Dict]]:
    """
    Load all domains organized by category.
    
    Returns:
        Dictionary with categories as keys and lists of domain dictionaries as values
    """
    domains = get_all_domains()
    domains_by_category = {}
    
    for domain in domains:
        # Handle case where domain might be a string instead of dict
        if isinstance(domain, str):
            domain_obj = get_domain_info(domain)
        else:
            domain_obj = domain
            
        category = domain_obj.get("category", "unknown")
        if category not in domains_by_category:
            domains_by_category[category] = []
        domains_by_category[category].append(domain_obj)
    
    return domains_by_category

def save_test_result(domain: str, test_result: Dict) -> bool:
    """
    Save a test result for a domain.
    
    Args:
        domain: Domain name
        test_result: Test result dictionary
        
    Returns:
        Success flag
    """
    domain_dir = os.path.join(RESULTS_DIR, domain)
    os.makedirs(domain_dir, exist_ok=True)
    
    timestamp = test_result.get("timestamp", time.time())
    date_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S")
    result_file = os.path.join(domain_dir, f"result_{date_str}.json")
    
    try:
        with open(result_file, 'w') as f:
            json.dump(test_result, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving test result: {e}")
        return False

def get_domain_history(domain: str) -> List[Dict]:
    """
    Get historical test results for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        List of test result dictionaries
    """
    domain_dir = os.path.join(RESULTS_DIR, domain)
    
    if not os.path.exists(domain_dir):
        return []
    
    try:
        result_files = [f for f in os.listdir(domain_dir) if f.startswith("result_") and f.endswith(".json")]
        result_files.sort(reverse=True)  # Most recent first
        
        results = []
        for file in result_files:
            with open(os.path.join(domain_dir, file), 'r') as f:
                result = json.load(f)
                results.append(result)
        
        return results
    except Exception as e:
        logger.error(f"Error loading domain history: {e}")
        return []

def get_latest_domain_result(domain: str) -> Optional[Dict]:
    """
    Get the latest test result for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        Latest test result dictionary or None if not found
    """
    history = get_domain_history(domain)
    
    if history:
        return history[0]
    
    return None

def update_trends_data(trend_data: Dict) -> bool:
    """
    Update the global trends data.
    
    Args:
        trend_data: Trend data dictionary
        
    Returns:
        Success flag
    """
    try:
        with open(TRENDS_FILE, 'w') as f:
            json.dump(trend_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving trends data: {e}")
        return False

def get_trends_data() -> Dict:
    """
    Get the global trends data.
    
    Returns:
        Trend data dictionary
    """
    if not os.path.exists(TRENDS_FILE):
        setup_database()
        return {
            "categories": {},
            "global": {
                "avg_score": 0,
                "max_score": 0,
                "min_score": 0,
                "top_domains": [],
                "rising_domains": [],
                "falling_domains": []
            },
            "last_updated": time.time()
        }
    
    try:
        with open(TRENDS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading trends data: {e}")
        return {
            "categories": {},
            "global": {
                "avg_score": 0,
                "max_score": 0,
                "min_score": 0,
                "top_domains": [],
                "rising_domains": [],
                "falling_domains": []
            },
            "last_updated": time.time()
        }

def get_all_tested_domains() -> List[str]:
    """
    Get all domains that have been tested.
    
    Returns:
        List of domain names
    """
    if not os.path.exists(RESULTS_DIR):
        return []
    
    try:
        return [d for d in os.listdir(RESULTS_DIR) if os.path.isdir(os.path.join(RESULTS_DIR, d))]
    except Exception as e:
        logger.error(f"Error getting tested domains: {e}")
        return []

def save_benchmark_set(category: str, benchmark_data: Dict) -> bool:
    """
    Save a benchmark set for a category.
    
    Args:
        category: Category name
        benchmark_data: Benchmark data dictionary
        
    Returns:
        Success flag
    """
    benchmark_dir = os.path.join(DATA_DIR, "benchmarks", "by_category")
    os.makedirs(benchmark_dir, exist_ok=True)
    
    benchmark_file = os.path.join(benchmark_dir, f"{category}.json")
    
    try:
        with open(benchmark_file, 'w') as f:
            json.dump(benchmark_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving benchmark set: {e}")
        return False

def get_benchmark_set(category: str) -> Optional[Dict]:
    """
    Get a benchmark set for a category.
    
    Args:
        category: Category name
        
    Returns:
        Benchmark data dictionary or None if not found
    """
    benchmark_file = os.path.join(DATA_DIR, "benchmarks", "by_category", f"{category}.json")
    
    if not os.path.exists(benchmark_file):
        return None
    
    try:
        with open(benchmark_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading benchmark set: {e}")
        return None

def save_trust_drift_event(domain: str, drift_event: Dict) -> bool:
    """
    Save a trust drift event for a domain.
    
    Args:
        domain: Domain name
        drift_event: Drift event dictionary
        
    Returns:
        Success flag
    """
    drift_dir = os.path.join(DATA_DIR, "trust_drift", "time_series")
    os.makedirs(drift_dir, exist_ok=True)
    
    drift_file = os.path.join(drift_dir, f"{domain}.json")
    
    # Load existing drift events
    drift_data = {
        "domain": domain,
        "drift_events": []
    }
    
    if os.path.exists(drift_file):
        try:
            with open(drift_file, 'r') as f:
                drift_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading drift events for {domain}: {e}")
    
    # Add new drift event
    drift_data["drift_events"].append(drift_event)
    
    # Save updated drift events
    try:
        with open(drift_file, 'w') as f:
            json.dump(drift_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving drift event for {domain}: {e}")
        return False

def get_trust_drift_events(domain: str) -> List[Dict]:
    """
    Get trust drift events for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        List of drift event dictionaries
    """
    drift_file = os.path.join(DATA_DIR, "trust_drift", "time_series", f"{domain}.json")
    
    if not os.path.exists(drift_file):
        return []
    
    try:
        with open(drift_file, 'r') as f:
            drift_data = json.load(f)
            return drift_data.get("drift_events", [])
    except Exception as e:
        logger.error(f"Error loading drift events for {domain}: {e}")
        return []