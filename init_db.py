"""
Initialize the LLMPageRank Database

This script initializes the database and sets up the necessary files and directories.
"""

import os
import json
import time
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Import from project modules
import database as db
from config import DATA_DIR, CATEGORIES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database(skip_migration: bool = False):
    """
    Initialize the database and set up necessary files and directories.
    
    Args:
        skip_migration: Flag to skip data migration
    """
    logger.info("Initializing database...")
    
    # Setup database
    db.setup_database()
    
    # Create necessary directories
    os.makedirs(f"{DATA_DIR}/system_feedback", exist_ok=True)
    os.makedirs(f"{DATA_DIR}/admin_insight_console", exist_ok=True)
    os.makedirs(f"{DATA_DIR}/trust_drift/time_series", exist_ok=True)
    os.makedirs(f"{DATA_DIR}/benchmarks/by_category", exist_ok=True)
    
    # Create database schema
    logger.info("Database schema created successfully")
    
    # Run data migration if needed
    if not skip_migration:
        migrate_data()
    else:
        logger.info("Skipping data migration")
    
    logger.info("Database initialization complete")

def migrate_data():
    """Migrate data from old format to new format if needed."""
    logger.info("Running data migration...")
    
    # Add sample domains if none exist
    if not db.get_all_domains():
        add_sample_domains()
    
    # Add benchmark sets if none exist
    for category in CATEGORIES:
        if not db.get_benchmark_set(category):
            create_benchmark_set(category)
    
    logger.info("Data migration complete")

def add_sample_domains():
    """Add sample domains to the database."""
    sample_domains = [
        {
            "domain": "stripe.com",
            "category": "finance",
            "discovery_date": datetime.now().strftime("%Y-%m-%d"),
            "target_score": random.randint(70, 95),
            "customer_likelihood": random.uniform(0.7, 0.9),
            "last_tested": time.time() - random.randint(0, 7*24*60*60)
        },
        {
            "domain": "asana.com",
            "category": "saas",
            "discovery_date": datetime.now().strftime("%Y-%m-%d"),
            "target_score": random.randint(70, 95),
            "customer_likelihood": random.uniform(0.7, 0.9),
            "last_tested": time.time() - random.randint(0, 7*24*60*60)
        },
        {
            "domain": "mayoclinic.org",
            "category": "healthcare",
            "discovery_date": datetime.now().strftime("%Y-%m-%d"),
            "target_score": random.randint(70, 95),
            "customer_likelihood": random.uniform(0.7, 0.9),
            "last_tested": time.time() - random.randint(0, 7*24*60*60)
        },
        {
            "domain": "lawfirm.com",
            "category": "legal",
            "discovery_date": datetime.now().strftime("%Y-%m-%d"),
            "target_score": random.randint(70, 95),
            "customer_likelihood": random.uniform(0.7, 0.9),
            "last_tested": time.time() - random.randint(0, 7*24*60*60)
        },
        {
            "domain": "hubspot.com",
            "category": "saas",
            "discovery_date": datetime.now().strftime("%Y-%m-%d"),
            "target_score": random.randint(70, 95),
            "customer_likelihood": random.uniform(0.7, 0.9),
            "last_tested": time.time() - random.randint(0, 7*24*60*60)
        },
        {
            "domain": "monday.com",
            "category": "saas",
            "discovery_date": datetime.now().strftime("%Y-%m-%d"),
            "target_score": random.randint(70, 95),
            "customer_likelihood": random.uniform(0.7, 0.9),
            "last_tested": time.time() - random.randint(0, 7*24*60*60)
        },
        {
            "domain": "zendesk.com",
            "category": "saas",
            "discovery_date": datetime.now().strftime("%Y-%m-%d"),
            "target_score": random.randint(70, 95),
            "customer_likelihood": random.uniform(0.7, 0.9),
            "last_tested": time.time() - random.randint(0, 7*24*60*60)
        },
        {
            "domain": "openai.com",
            "category": "ai_infrastructure",
            "discovery_date": datetime.now().strftime("%Y-%m-%d"),
            "target_score": random.randint(70, 95),
            "customer_likelihood": random.uniform(0.7, 0.9),
            "last_tested": time.time() - random.randint(0, 7*24*60*60)
        },
        {
            "domain": "anthropic.com",
            "category": "ai_infrastructure",
            "discovery_date": datetime.now().strftime("%Y-%m-%d"),
            "target_score": random.randint(70, 95),
            "customer_likelihood": random.uniform(0.7, 0.9),
            "last_tested": time.time() - random.randint(0, 7*24*60*60)
        },
        {
            "domain": "salesforce.com",
            "category": "enterprise_tech",
            "discovery_date": datetime.now().strftime("%Y-%m-%d"),
            "target_score": random.randint(70, 95),
            "customer_likelihood": random.uniform(0.7, 0.9),
            "last_tested": time.time() - random.randint(0, 7*24*60*60)
        }
    ]
    
    for domain in sample_domains:
        db.add_domain(domain)
        
        # Add sample test results
        add_sample_results(domain["domain"], domain["category"])
    
    logger.info(f"Added {len(sample_domains)} sample domains")

def add_sample_results(domain: str, category: str):
    """
    Add sample test results for a domain.
    
    Args:
        domain: Domain name
        category: Category name
    """
    # Number of historical results to generate (1-10)
    history_count = random.randint(1, 10)
    
    for i in range(history_count):
        # Generate test result
        timestamp = time.time() - (i * 7 * 24 * 60 * 60)  # Weekly intervals
        visibility_score = random.randint(60, 95)
        
        result = {
            "domain": domain,
            "category": category,
            "visibility_score": visibility_score,
            "citation_count": random.randint(10, 100),
            "direct_mentions": random.randint(5, 50),
            "implied_mentions": random.randint(5, 50),
            "positive_sentiment": random.uniform(0.6, 0.9),
            "negative_sentiment": random.uniform(0.1, 0.3),
            "models_tested": ["gpt-4o", "claude-3-5-sonnet-20241022", "mixtral-8x7b"],
            "prompt_count": random.randint(10, 30),
            "prompt_version": "1.0",
            "details": {
                "informational_score": random.randint(60, 95),
                "transactional_score": random.randint(60, 95),
                "decision_score": random.randint(60, 95)
            },
            "timestamp": timestamp
        }
        
        db.save_test_result(domain, result)
    
    # Add trust drift events
    drift_event_count = random.randint(0, 3)
    
    for i in range(drift_event_count):
        timestamp = time.time() - (i * 14 * 24 * 60 * 60)  # Bi-weekly intervals
        drift_magnitude = random.uniform(-15, 15)
        
        drift_event = {
            "timestamp": timestamp,
            "magnitude": drift_magnitude,
            "type": random.choice(["model_update", "content_change", "prompt_shift", "peer_movement"]),
            "description": f"Trust shift of {drift_magnitude:.1f} points detected",
            "models_affected": random.sample(["gpt-4o", "claude-3-5-sonnet-20241022", "mixtral-8x7b"], random.randint(1, 3))
        }
        
        db.save_trust_drift_event(domain, drift_event)

def create_benchmark_set(category: str):
    """
    Create a benchmark set for a category.
    
    Args:
        category: Category name
    """
    # Get domains in category
    domains = db.get_domains_by_category(category)
    
    if not domains:
        return
    
    # Sort by visibility score (assuming each has at least one result)
    domains_with_scores = []
    
    for domain in domains:
        latest_result = db.get_latest_domain_result(domain["domain"])
        
        if latest_result:
            domains_with_scores.append({
                "domain": domain["domain"],
                "score": latest_result.get("visibility_score", 0)
            })
    
    # Sort by score (descending)
    domains_with_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Create benchmark set
    benchmark_data = {
        "category": category,
        "benchmark_domain": domains_with_scores[0]["domain"] if domains_with_scores else "",
        "peer_set": [d["domain"] for d in domains_with_scores[1:min(6, len(domains_with_scores))]],
        "description": f"Benchmark set for {category}",
        "last_updated": time.time(),
        "last_shift": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
    }
    
    db.save_benchmark_set(category, benchmark_data)

if __name__ == "__main__":
    initialize_database(skip_migration=False)