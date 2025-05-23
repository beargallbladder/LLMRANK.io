"""
Initialize test domains for LLMPageRank V3 demonstration.

This script populates the database with test domains and results
to showcase the V3 dashboard capabilities.
"""

import json
import os
import time
import random
from datetime import datetime, timedelta
import logging

from config import DATA_DIR, CATEGORIES
import database as db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample domains by category
SAMPLE_DOMAINS = {
    "finance": [
        {"domain": "chase.com", "name": "Chase Bank", "priority": 9},
        {"domain": "bankofamerica.com", "name": "Bank of America", "priority": 8},
        {"domain": "wellsfargo.com", "name": "Wells Fargo", "priority": 7},
        {"domain": "citibank.com", "name": "Citibank", "priority": 7},
        {"domain": "capitalone.com", "name": "Capital One", "priority": 6},
        {"domain": "schwab.com", "name": "Charles Schwab", "priority": 6},
        {"domain": "fidelity.com", "name": "Fidelity Investments", "priority": 8}
    ],
    "healthcare": [
        {"domain": "mayoclinic.org", "name": "Mayo Clinic", "priority": 9},
        {"domain": "clevelandclinic.org", "name": "Cleveland Clinic", "priority": 8},
        {"domain": "hopkinsmedicine.org", "name": "Johns Hopkins Medicine", "priority": 9},
        {"domain": "webmd.com", "name": "WebMD", "priority": 7},
        {"domain": "nih.gov", "name": "National Institutes of Health", "priority": 8},
        {"domain": "healthline.com", "name": "Healthline", "priority": 6}
    ],
    "legal": [
        {"domain": "findlaw.com", "name": "FindLaw", "priority": 8},
        {"domain": "justia.com", "name": "Justia", "priority": 7},
        {"domain": "law.cornell.edu", "name": "Cornell Law School", "priority": 9},
        {"domain": "nolo.com", "name": "Nolo", "priority": 6},
        {"domain": "avvo.com", "name": "Avvo", "priority": 5}
    ],
    "saas": [
        {"domain": "salesforce.com", "name": "Salesforce", "priority": 9},
        {"domain": "hubspot.com", "name": "HubSpot", "priority": 8},
        {"domain": "zendesk.com", "name": "Zendesk", "priority": 7},
        {"domain": "slack.com", "name": "Slack", "priority": 8},
        {"domain": "dropbox.com", "name": "Dropbox", "priority": 7},
        {"domain": "notion.so", "name": "Notion", "priority": 6}
    ],
    "ai_infrastructure": [
        {"domain": "openai.com", "name": "OpenAI", "priority": 9},
        {"domain": "huggingface.co", "name": "Hugging Face", "priority": 9},
        {"domain": "anthropic.com", "name": "Anthropic", "priority": 8},
        {"domain": "tensorflow.org", "name": "TensorFlow", "priority": 7},
        {"domain": "pytorch.org", "name": "PyTorch", "priority": 7},
        {"domain": "databricks.com", "name": "Databricks", "priority": 6}
    ],
    "education": [
        {"domain": "edx.org", "name": "edX", "priority": 8},
        {"domain": "coursera.org", "name": "Coursera", "priority": 9},
        {"domain": "khanacademy.org", "name": "Khan Academy", "priority": 8},
        {"domain": "udemy.com", "name": "Udemy", "priority": 7},
        {"domain": "pluralsight.com", "name": "Pluralsight", "priority": 6},
        {"domain": "mit.edu", "name": "MIT", "priority": 9}
    ],
    "ecommerce": [
        {"domain": "amazon.com", "name": "Amazon", "priority": 9},
        {"domain": "walmart.com", "name": "Walmart", "priority": 8},
        {"domain": "bestbuy.com", "name": "Best Buy", "priority": 7},
        {"domain": "target.com", "name": "Target", "priority": 7},
        {"domain": "ebay.com", "name": "eBay", "priority": 7},
        {"domain": "etsy.com", "name": "Etsy", "priority": 6}
    ],
    "enterprise_tech": [
        {"domain": "microsoft.com", "name": "Microsoft", "priority": 9},
        {"domain": "oracle.com", "name": "Oracle", "priority": 9},
        {"domain": "ibm.com", "name": "IBM", "priority": 8},
        {"domain": "sap.com", "name": "SAP", "priority": 8},
        {"domain": "vmware.com", "name": "VMware", "priority": 7},
        {"domain": "cisco.com", "name": "Cisco", "priority": 7}
    ]
}

def generate_test_results(domain, category, backdated=False):
    """
    Generate test results for a domain.
    
    Args:
        domain: Domain name
        category: Domain category
        backdated: Whether to backdate the results for historical data
        
    Returns:
        Dictionary with test results
    """
    # Base timestamp for the result
    if backdated:
        # Random date within the last 30 days
        days_back = random.randint(7, 30)
        timestamp = time.time() - days_back * 86400
    else:
        timestamp = time.time()
    
    # Generate base scores
    base_scores = {
        "finance": {"visibility": 75, "structure": 85, "consensus": 0.9},
        "healthcare": {"visibility": 70, "structure": 75, "consensus": 0.85},
        "legal": {"visibility": 65, "structure": 80, "consensus": 0.8},
        "saas": {"visibility": 60, "structure": 70, "consensus": 0.75},
        "ai_infrastructure": {"visibility": 80, "structure": 90, "consensus": 0.95},
        "education": {"visibility": 65, "structure": 75, "consensus": 0.8},
        "ecommerce": {"visibility": 70, "structure": 65, "consensus": 0.75},
        "enterprise_tech": {"visibility": 75, "structure": 85, "consensus": 0.9}
    }
    
    # Get base scores for the category
    base = base_scores.get(category, {"visibility": 60, "structure": 70, "consensus": 0.8})
    
    # Random variations
    visibility_var = random.uniform(-15, 15)
    structure_var = random.uniform(-10, 10)
    consensus_var = random.uniform(-0.1, 0.1)
    
    # Domain-specific adjustments for well-known domains
    premium_domains = [
        "chase.com", "mayoclinic.org", "openai.com", "oracle.com", 
        "microsoft.com", "amazon.com", "huggingface.co", "coursera.org", 
        "findlaw.com", "salesforce.com"
    ]
    
    if domain in premium_domains:
        visibility_var += 10
        structure_var += 5
        consensus_var += 0.05
    
    # Calculate scores
    visibility_score = max(min(base["visibility"] + visibility_var, 100), 0)
    structure_score = max(min(base["structure"] + structure_var, 100), 0)
    consensus_score = max(min(base["consensus"] + consensus_var, 1.0), 0.0)
    
    # QA score (0-1, lower is better)
    qa_score = max(min(random.uniform(0.2, 0.8), 1.0), 0.0)
    
    # Generate citation coverage
    citation_models = ["gpt-4o", "claude-3-5-sonnet-20241022", "mixtral-8x7b"]
    citation_coverage = {}
    
    for model in citation_models:
        citation_coverage[model] = {
            "direct_citations": random.randint(1, 5),
            "paraphrased_citations": random.randint(2, 8),
            "no_citations": random.randint(0, 3)
        }
    
    # Generate test result
    result = {
        "domain": domain,
        "category": category,
        "visibility_score": round(visibility_score, 2),
        "structure_score": round(structure_score, 2),
        "consensus_score": round(consensus_score, 2),
        "citation_coverage": citation_coverage,
        "customer_likelihood": int(random.uniform(1, 10)),
        "delta_info": {"weekly_change": random.uniform(-5, 5)},
        "prompt_version": "1.0",
        "model_versions": {"gpt-4o": "20230501", "claude-3-5-sonnet": "20241022"},
        "timestamp": timestamp,
        "formatted_timestamp": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return result

def initialize_domains():
    """Initialize domains and test results in the database."""
    logger.info("Initializing test domains and results...")
    
    # Save domains by category
    domains_by_category = {}
    
    for category, domains in SAMPLE_DOMAINS.items():
        domains_by_category[category] = domains
    
    # Save domains to database
    db.save_domains(domains_by_category)
    logger.info(f"Saved {sum(len(domains) for domains in domains_by_category.values())} domains to database")
    
    # Generate and save test results for each domain
    results_created = 0
    
    for category, domains in SAMPLE_DOMAINS.items():
        for domain_info in domains:
            domain = domain_info["domain"]
            
            # Create current result
            result = generate_test_results(domain, category)
            db.save_test_results(result)
            results_created += 1
            
            # Create some historical results (random number 1-3)
            history_count = random.randint(1, 3)
            
            for i in range(history_count):
                historical_result = generate_test_results(domain, category, backdated=True)
                db.save_test_results(historical_result)
                results_created += 1
    
    logger.info(f"Created {results_created} test results")
    
    # Create initial trends data
    generate_trends_data()
    
    logger.info("Domain initialization complete")

def generate_trends_data():
    """Generate trends data from test results."""
    logger.info("Generating trends data...")
    
    # Get all tested domains
    tested_domains = db.get_all_tested_domains()
    
    # Initialize trends data
    trends_data = {
        "global_stats": {
            "total_domains_tested": len(tested_domains),
            "avg_visibility_score": 0,
            "avg_structure_score": 0,
            "consensus_level": 0
        },
        "by_category": {},
        "top_domains": [],
        "bottom_domains": [],
        "timestamp": time.time()
    }
    
    # Calculate global averages
    visibility_scores = []
    structure_scores = []
    consensus_scores = []
    
    domain_results = []
    
    for domain in tested_domains:
        result = db.get_latest_domain_result(domain)
        if result:
            visibility_scores.append(result.get("visibility_score", 0))
            structure_scores.append(result.get("structure_score", 0))
            consensus_scores.append(result.get("consensus_score", 0))
            
            domain_results.append({
                "domain": domain,
                "category": result.get("category", ""),
                "visibility_score": result.get("visibility_score", 0),
                "structure_score": result.get("structure_score", 0),
                "consensus_score": result.get("consensus_score", 0)
            })
    
    # Calculate global averages
    if visibility_scores:
        trends_data["global_stats"]["avg_visibility_score"] = sum(visibility_scores) / len(visibility_scores)
    
    if structure_scores:
        trends_data["global_stats"]["avg_structure_score"] = sum(structure_scores) / len(structure_scores)
    
    if consensus_scores:
        trends_data["global_stats"]["consensus_level"] = sum(consensus_scores) / len(consensus_scores)
    
    # Calculate category stats
    for category in CATEGORIES:
        category_results = [r for r in domain_results if r["category"] == category]
        
        if not category_results:
            continue
        
        cat_visibility = [r["visibility_score"] for r in category_results]
        cat_structure = [r["structure_score"] for r in category_results]
        cat_consensus = [r["consensus_score"] for r in category_results]
        
        trends_data["by_category"][category] = {
            "domain_count": len(category_results),
            "avg_visibility": sum(cat_visibility) / len(cat_visibility) if cat_visibility else 0,
            "avg_structure": sum(cat_structure) / len(cat_structure) if cat_structure else 0,
            "avg_consensus": sum(cat_consensus) / len(cat_consensus) if cat_consensus else 0
        }
    
    # Get top and bottom domains
    domain_results.sort(key=lambda x: x["visibility_score"], reverse=True)
    trends_data["top_domains"] = domain_results[:10]
    
    domain_results.sort(key=lambda x: x["visibility_score"])
    trends_data["bottom_domains"] = domain_results[:10]
    
    # Save trends data
    db.save_trends_data(trends_data)
    logger.info("Trends data generated and saved")


if __name__ == "__main__":
    # Setup database
    db.setup_database()
    
    # Initialize domains and test results
    initialize_domains()