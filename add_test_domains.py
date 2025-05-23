"""
Add test domains and data for LLMPageRank V3 demonstration.

This script adds a minimal set of test domains to demonstrate the dashboards.
"""

import database as db
import json
import logging
import time
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Top domains for each category
TEST_DOMAINS = {
    "finance": ["chase.com", "bankofamerica.com", "fidelity.com"],
    "healthcare": ["mayoclinic.org", "clevelandclinic.org", "nih.gov"],
    "legal": ["findlaw.com", "justia.com", "law.cornell.edu"],
    "ai_infrastructure": ["openai.com", "huggingface.co", "anthropic.com"],
    "enterprise_tech": ["oracle.com", "microsoft.com", "ibm.com"]
}

def add_test_domains():
    """Add test domains to the database."""
    logger.info("Adding test domains...")
    
    # Prepare domains by category
    domains_by_category = {}
    for category, domains in TEST_DOMAINS.items():
        domains_by_category[category] = []
        for domain in domains:
            domains_by_category[category].append({
                "domain": domain,
                "name": domain.split('.')[0].capitalize(),
                "priority": 9
            })
    
    # Save domains
    db.save_domains(domains_by_category)
    logger.info("Test domains added to database")

def add_test_results():
    """Add test results for domains."""
    logger.info("Adding test results...")
    
    for category, domains in TEST_DOMAINS.items():
        for domain in domains:
            # Current result
            result = {
                "domain": domain,
                "category": category,
                "visibility_score": 75.0,
                "structure_score": 80.0,
                "consensus_score": 0.85,
                "citation_coverage": {
                    "gpt-4o": {
                        "direct_citations": 4,
                        "paraphrased_citations": 6,
                        "no_citations": 1
                    },
                    "claude-3-5-sonnet-20241022": {
                        "direct_citations": 3,
                        "paraphrased_citations": 5,
                        "no_citations": 2
                    }
                },
                "customer_likelihood": 8,
                "delta_info": {"weekly_change": 3.5},
                "prompt_version": "1.0",
                "model_versions": {"gpt-4o": "20230501", "claude-3-5-sonnet": "20241022"},
                "timestamp": time.time()
            }
            
            # Save current result
            db.save_test_results(result)
            
            # Add historical result from 7 days ago
            historical = result.copy()
            historical["visibility_score"] = 71.5
            historical["timestamp"] = time.time() - (7 * 86400)
            db.save_test_results(historical)
    
    logger.info("Test results added")

def add_trends_data():
    """Add trends data based on test results."""
    logger.info("Adding trends data...")
    
    # Simplified trends data
    trends_data = {
        "global_stats": {
            "total_domains_tested": 15,
            "avg_visibility_score": 75.0,
            "avg_structure_score": 80.0,
            "consensus_level": 0.85
        },
        "by_category": {
            "finance": {
                "domain_count": 3,
                "avg_visibility": 75.0,
                "avg_structure": 80.0,
                "avg_consensus": 0.85
            },
            "healthcare": {
                "domain_count": 3,
                "avg_visibility": 73.0,
                "avg_structure": 78.0,
                "avg_consensus": 0.82
            },
            "legal": {
                "domain_count": 3,
                "avg_visibility": 72.0,
                "avg_structure": 82.0,
                "avg_consensus": 0.80
            },
            "ai_infrastructure": {
                "domain_count": 3,
                "avg_visibility": 82.0,
                "avg_structure": 88.0,
                "avg_consensus": 0.90
            },
            "enterprise_tech": {
                "domain_count": 3,
                "avg_visibility": 76.0,
                "avg_structure": 84.0,
                "avg_consensus": 0.87
            }
        },
        "top_domains": [
            {"domain": "openai.com", "category": "ai_infrastructure", "visibility_score": 82.0},
            {"domain": "huggingface.co", "category": "ai_infrastructure", "visibility_score": 81.0},
            {"domain": "oracle.com", "category": "enterprise_tech", "visibility_score": 79.0}
        ],
        "bottom_domains": [
            {"domain": "justia.com", "category": "legal", "visibility_score": 71.0},
            {"domain": "clevelandclinic.org", "category": "healthcare", "visibility_score": 72.0},
            {"domain": "nih.gov", "category": "healthcare", "visibility_score": 73.0}
        ],
        "timestamp": time.time()
    }
    
    # Save trends data
    db.save_trends_data(trends_data)
    logger.info("Trends data added")

def initialize_v3_data():
    """Initialize V3 specific data files."""
    logger.info("Initializing V3 data structures...")
    
    # Create initial benchmark set for AI infrastructure
    from config import DATA_DIR
    import os
    
    # Directory for benchmark sets
    benchmark_dir = f"{DATA_DIR}/category_benchmark_sets"
    os.makedirs(benchmark_dir, exist_ok=True)
    
    # AI infrastructure benchmark
    ai_benchmark = {
        "benchmark_status": "valid",
        "primary_domain": "openai.com",
        "peer_set": ["huggingface.co", "anthropic.com"],
        "peer_set_size": 2,
        "last_updated": time.time()
    }
    
    with open(f"{benchmark_dir}/ai_infrastructure.json", 'w') as f:
        json.dump(ai_benchmark, f, indent=2)
    
    # Create directory for QA intensity
    qa_dir = f"{DATA_DIR}/qa_intensity"
    os.makedirs(qa_dir, exist_ok=True)
    
    # Sample QA intensity for AI infrastructure
    qa_intensity = {
        "total_prompts": 10,
        "invalid_prompts": 2,
        "issue_rate": 0.2,
        "model_disagreement": 0.15,
        "last_updated": time.time()
    }
    
    with open(f"{qa_dir}/ai_infrastructure_qa.json", 'w') as f:
        json.dump(qa_intensity, f, indent=2)
    
    logger.info("V3 data structures initialized")

if __name__ == "__main__":
    # Setup database
    db.setup_database()
    
    # Add domains and test data
    add_test_domains()
    add_test_results()
    add_trends_data()
    initialize_v3_data()
    
    logger.info("Demo data initialization complete!")