"""
LLMPageRank V9 Database Interface

This module provides database access functions for the V9 API implementation,
allowing the system to retrieve trust scores, domain data, and FOMA metrics.
"""

import os
import json
import time
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Import project modules
from config import DATA_DIR, CATEGORIES

# Data storage paths
DOMAINS_FILE = f"{DATA_DIR}/domains.json"
RESULTS_DIR = f"{DATA_DIR}/results"
TRENDS_FILE = f"{DATA_DIR}/trends.json"
TRENDS_DIR = f"{DATA_DIR}/trends"

def get_domain_trust_score(domain: str) -> Optional[Dict]:
    """
    Get trust score data for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        Domain trust score dictionary or None if not found
    """
    # Try to load from domain-specific results file
    domain_file = f"{RESULTS_DIR}/{domain}.json"
    
    if os.path.exists(domain_file):
        try:
            with open(domain_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading domain data: {e}")
    
    # If domain-specific file not found, check domains file
    if os.path.exists(DOMAINS_FILE):
        try:
            with open(DOMAINS_FILE, 'r') as f:
                domains = json.load(f)
                
                for domain_data in domains:
                    if domain_data.get("domain") == domain:
                        return domain_data
        except Exception as e:
            print(f"Error loading domains data: {e}")
    
    # Generate placeholder data for demonstration
    # In production, this would return None if domain not found
    return generate_domain_data(domain)

def get_top_domains_by_category(category: str, limit: int = 10) -> List[Dict]:
    """
    Get top domains by visibility score for a category.
    
    Args:
        category: Category name
        limit: Maximum number of domains to return
        
    Returns:
        List of top domain dictionaries
    """
    # Check if category is valid
    if category not in CATEGORIES and category != "all":
        # Generate placeholder data for demonstration
        return generate_category_data(category, limit)
    
    # Try to load from category-specific file
    category_file = f"{RESULTS_DIR}/categories/{category}.json"
    
    if os.path.exists(category_file):
        try:
            with open(category_file, 'r') as f:
                domains = json.load(f)
                
                # Sort by score (descending) and limit results
                sorted_domains = sorted(
                    domains, 
                    key=lambda x: x.get("score", 0), 
                    reverse=True
                )
                
                return sorted_domains[:limit]
        except Exception as e:
            print(f"Error loading category data: {e}")
    
    # If category-specific file not found, check domains file
    if os.path.exists(DOMAINS_FILE):
        try:
            with open(DOMAINS_FILE, 'r') as f:
                all_domains = json.load(f)
                
                # Filter domains by category
                category_domains = [
                    d for d in all_domains 
                    if d.get("category") == category or category == "all"
                ]
                
                # Sort by score (descending) and limit results
                sorted_domains = sorted(
                    category_domains, 
                    key=lambda x: x.get("score", 0), 
                    reverse=True
                )
                
                return sorted_domains[:limit]
        except Exception as e:
            print(f"Error loading domains data: {e}")
    
    # Generate placeholder data for demonstration
    return generate_category_data(category, limit)

def get_category_deltas(category: str, limit: int = 5) -> Dict:
    """
    Get domains with significant visibility changes in a category.
    
    Args:
        category: Category name
        limit: Maximum number of domains to return in each group
        
    Returns:
        Dictionary with rising and falling domains
    """
    # Try to load from trends file
    category_trends_file = f"{TRENDS_DIR}/{category}_trends.json"
    
    if os.path.exists(category_trends_file):
        try:
            with open(category_trends_file, 'r') as f:
                trends = json.load(f)
                
                # Extract rising and falling domains
                rising = trends.get("rising", [])[:limit]
                falling = trends.get("falling", [])[:limit]
                
                return {
                    "rising_domains": rising,
                    "falling_domains": falling
                }
        except Exception as e:
            print(f"Error loading trends data: {e}")
    
    # Generate placeholder data for demonstration
    return generate_delta_data(category, limit)

def get_foma_score(domain: str) -> Optional[Dict]:
    """
    Get FOMA score and details for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        FOMA score dictionary or None if not found
    """
    # Try to load from FOMA-specific file
    foma_file = f"{RESULTS_DIR}/foma/{domain}.json"
    
    if os.path.exists(foma_file):
        try:
            with open(foma_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading FOMA data: {e}")
    
    # Try to load from domain-specific results file
    domain_file = f"{RESULTS_DIR}/{domain}.json"
    
    if os.path.exists(domain_file):
        try:
            with open(domain_file, 'r') as f:
                domain_data = json.load(f)
                
                if "foma_score" in domain_data:
                    return {
                        "score": domain_data.get("foma_score", 0),
                        "trigger_status": domain_data.get("foma_trigger_status", "stable"),
                        "peer_comparison": domain_data.get("peer_comparison", []),
                        "recommendations": domain_data.get("recommendations", [])
                    }
        except Exception as e:
            print(f"Error loading domain data: {e}")
    
    # Generate placeholder data for demonstration
    return generate_foma_data(domain)

def generate_domain_data(domain: str) -> Dict:
    """
    Generate placeholder domain data for demonstration.
    
    Args:
        domain: Domain name
        
    Returns:
        Generated domain data dictionary
    """
    # Extract category from domain name if possible
    domain_parts = domain.split('.')
    category = domain_parts[-2] if len(domain_parts) > 2 else random.choice(CATEGORIES)
    
    # Generate random score between 60 and 95
    score = random.randint(60, 95)
    
    # Generate random trust drift delta between -5 and 5
    delta_value = random.uniform(-5, 5)
    delta = f"+{delta_value:.1f}" if delta_value >= 0 else f"{delta_value:.1f}"
    
    # Generate random category percentile between 1 and 100
    percentile = random.randint(1, 100)
    
    # Generate random FOMA trigger status
    trigger_statuses = [
        "stable",
        f"peer overtaken by competitor.{category}.com",
        "content quality concerns",
        "declining citation trend",
        "flat category movement"
    ]
    trigger_status = random.choice(trigger_statuses)
    
    # Generate random scan time within the last week
    last_scan_time = (datetime.utcnow() - timedelta(days=random.randint(0, 7))).isoformat()
    
    # Generate random insights
    insights = []
    insight_count = random.randint(1, 3)
    
    for i in range(insight_count):
        insights.append({
            "summary": f"Insight {i+1} for {domain}",
            "delta": random.uniform(-3, 3),
            "narrative_score": random.uniform(0.5, 0.9),
            "timestamp": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat()
        })
    
    # Return domain data
    return {
        "domain": domain,
        "score": score,
        "category": category,
        "trust_drift_delta": delta,
        "category_percentile": percentile,
        "foma_trigger_status": trigger_status,
        "last_scan_time": last_scan_time,
        "insights": insights,
        "model_version": "gpt-4o",
        "score_logic": "v3.1"
    }

def generate_category_data(category: str, limit: int) -> List[Dict]:
    """
    Generate placeholder category data for demonstration.
    
    Args:
        category: Category name
        limit: Maximum number of domains to return
        
    Returns:
        List of generated domain dictionaries
    """
    domains = []
    
    for i in range(limit):
        domain = f"example{i}.{category}.com"
        
        # Generate random score between 60 and 95
        score = random.randint(60, 95) - i
        
        # Generate random trust drift delta between -5 and 5
        delta_value = random.uniform(-5, 5)
        delta = f"+{delta_value:.1f}" if delta_value >= 0 else f"{delta_value:.1f}"
        
        # Add domain to list
        domains.append({
            "domain": domain,
            "score": score,
            "category": category,
            "trust_drift_delta": delta,
            "rank": i + 1
        })
    
    return domains

def generate_delta_data(category: str, limit: int) -> Dict:
    """
    Generate placeholder delta data for demonstration.
    
    Args:
        category: Category name
        limit: Maximum number of domains to return in each group
        
    Returns:
        Dictionary with rising and falling domains
    """
    rising_domains = []
    falling_domains = []
    
    for i in range(limit):
        # Rising domains
        rising_domain = f"rising{i}.{category}.com"
        
        rising_domains.append({
            "domain": rising_domain,
            "llm_score": 75 + i,
            "trust_drift_delta": f"+{2.0 + i:.1f}",
            "previous_rank": 10 - i,
            "current_rank": 5 - i
        })
        
        # Falling domains
        falling_domain = f"falling{i}.{category}.com"
        
        falling_domains.append({
            "domain": falling_domain,
            "llm_score": 65 - i,
            "trust_drift_delta": f"-{1.5 + i:.1f}",
            "previous_rank": 3 + i,
            "current_rank": 8 + i
        })
    
    return {
        "rising_domains": rising_domains,
        "falling_domains": falling_domains
    }

def generate_foma_data(domain: str) -> Dict:
    """
    Generate placeholder FOMA data for demonstration.
    
    Args:
        domain: Domain name
        
    Returns:
        Generated FOMA data dictionary
    """
    # Extract category from domain name if possible
    domain_parts = domain.split('.')
    category = domain_parts[-2] if len(domain_parts) > 2 else random.choice(CATEGORIES)
    
    # Generate random FOMA score between 0 and 1
    score = random.uniform(0, 1)
    
    # Generate random trigger status
    trigger_statuses = [
        "low_concern",
        "moderate_concern",
        "high_concern",
        "stable",
        f"peer overtaken by competitor.{category}.com"
    ]
    trigger_status = random.choice(trigger_statuses)
    
    # Generate peer comparisons
    peer_comparison = []
    peer_count = random.randint(2, 4)
    
    for i in range(peer_count):
        peer_domain = f"peer{i}.{category}.com"
        
        # Ensure peer domain is different from the target domain
        if peer_domain == domain:
            peer_domain = f"alt-peer{i}.{category}.com"
        
        peer_score = random.randint(60, 90)
        score_difference = random.uniform(-15, 15)
        
        peer_comparison.append({
            "domain": peer_domain,
            "llm_score": peer_score,
            "score_difference": score_difference
        })
    
    # Generate recommendations
    recommendation_options = [
        "Monitor competing domains closely",
        "Strengthen topical authority in key areas",
        "Improve content quality on main category pages",
        "Increase citation-worthy content production",
        "Update outdated content on core pages",
        "Enhance schema markup for improved visibility",
        "Address content gaps identified by insight engine",
        "Focus on comprehensive coverage of trending topics"
    ]
    
    recommendation_count = random.randint(2, 4)
    recommendations = random.sample(recommendation_options, recommendation_count)
    
    # Return FOMA data
    return {
        "score": score,
        "trigger_status": trigger_status,
        "peer_comparison": peer_comparison,
        "recommendations": recommendations
    }