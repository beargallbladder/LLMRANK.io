"""
Delta Tracker Module

This module is responsible for tracking changes in domain visibility and trust scores over time.
It implements the V2 requirements for time-series tracking and longitudinal analysis.
"""

import json
import os
import time
import logging
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import from project modules
from config import DATA_DIR

# Constants
TRENDS_DIR = f"{DATA_DIR}/trends"
WEEKLY_MOVERS_FILE = f"{TRENDS_DIR}/weekly_movers.json"
OPPORTUNITY_TARGETS_FILE = f"{TRENDS_DIR}/opportunity_targets.json"

# Ensure trends directory exists
os.makedirs(TRENDS_DIR, exist_ok=True)

def compare_scores(domain: str, current_score: float, previous_score: Optional[float] = None) -> Dict:
    """
    Compare the current score with a previous score and calculate the delta.
    
    Args:
        domain: The domain being compared
        current_score: The current LLMRank score
        previous_score: The previous LLMRank score (if available)
        
    Returns:
        Dictionary with delta information
    """
    if previous_score is None:
        return {
            "domain": domain,
            "llmrank_today": current_score,
            "llmrank_last_week": None,
            "delta": 0,
            "status": "New Entry",
            "percentage_change": 0
        }
    
    delta = current_score - previous_score
    
    # Determine status based on delta
    if delta > 5:
        status = "Trust Rising"
    elif delta < -5:
        status = "Trust Falling"
    else:
        status = "Trust Stable"
    
    # Calculate percentage change
    if previous_score > 0:
        percentage_change = (delta / previous_score) * 100
    else:
        percentage_change = 0
    
    return {
        "domain": domain,
        "llmrank_today": current_score,
        "llmrank_last_week": previous_score,
        "delta": delta,
        "status": status,
        "percentage_change": percentage_change
    }

def track_domain_delta(domain_data: Dict) -> Dict:
    """
    Track changes in a domain's visibility score and add delta information.
    
    Args:
        domain_data: Dictionary containing current domain test results
        
    Returns:
        Dictionary with added delta tracking information
    """
    # Extract key information
    domain = domain_data.get("domain", "")
    current_score = domain_data.get("visibility_score", 0)
    timestamp = domain_data.get("timestamp", time.time())
    
    # Get previous result for comparison (from database)
    # This would normally be pulled from the database for the same domain
    # from 7 days ago, but we'll simplify by using the previous entry
    import database as db
    domain_history = db.get_domain_history(domain)
    
    # Find the previous entry (excluding the current one)
    previous_score = None
    previous_entry = None
    
    if len(domain_history) > 1:
        # Skip the first entry (current) and use the second one
        previous_entry = domain_history[1]
        previous_score = previous_entry.get("visibility_score", 0)
    
    # Compare and get delta information
    delta_info = compare_scores(domain, current_score, previous_score)
    
    # Enrich the domain data with delta information
    enriched_data = domain_data.copy()
    enriched_data.update({
        "delta_info": delta_info,
        "previous_timestamp": previous_entry.get("timestamp") if previous_entry else None,
        "has_previous_data": previous_score is not None
    })
    
    return enriched_data

def update_weekly_movers(domains_with_deltas: List[Dict]) -> None:
    """
    Update the weekly movers file with domains that have significant changes.
    
    Args:
        domains_with_deltas: List of domain dictionaries with delta information
    """
    # Filter for domains with significant movement
    significant_movers = []
    
    for domain in domains_with_deltas:
        delta_info = domain.get("delta_info", {})
        delta = delta_info.get("delta", 0)
        
        # If the delta is significant (more than 5 points in either direction)
        if abs(delta) >= 5:
            # Get the list of models and prompts that triggered this change
            models = domain.get("models_used", [])
            
            # Extract prompts that generated citations
            triggering_prompts = []
            for prompt_result in domain.get("prompt_results", []):
                prompt_text = prompt_result.get("prompt_text", "")
                for model, result in prompt_result.get("results", {}).items():
                    if result.get("citation_type", "none") != "none":
                        if prompt_text not in triggering_prompts:
                            triggering_prompts.append(prompt_text)
            
            # Build the mover entry in the format specified in the V2 directive
            mover_entry = {
                "domain": domain.get("domain", ""),
                "llmrank_today": delta_info.get("llmrank_today", 0),
                "llmrank_last_week": delta_info.get("llmrank_last_week", 0),
                "delta": delta,
                "status": delta_info.get("status", ""),
                "models": models,
                "triggering_prompts": triggering_prompts
            }
            
            significant_movers.append(mover_entry)
    
    # Load existing data
    existing_movers = []
    if os.path.exists(WEEKLY_MOVERS_FILE):
        try:
            with open(WEEKLY_MOVERS_FILE, "r") as f:
                existing_movers = json.load(f)
        except Exception as e:
            logger.error(f"Error loading weekly movers file: {e}")
    
    # Add timestamp to the data
    current_data = {
        "timestamp": time.time(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "movers": significant_movers
    }
    
    # Add to existing data (keep last 4 weeks)
    updated_data = [current_data] + existing_movers
    if len(updated_data) > 4:
        updated_data = updated_data[:4]
    
    # Save the data
    try:
        with open(WEEKLY_MOVERS_FILE, "w") as f:
            json.dump(updated_data, f, indent=2)
        logger.info(f"Updated weekly movers file with {len(significant_movers)} significant movers")
    except Exception as e:
        logger.error(f"Error saving weekly movers file: {e}")

def identify_opportunity_targets(domains_with_deltas: List[Dict]) -> None:
    """
    Identify opportunity targets based on SEO Z-score vs LLMRank.
    
    Args:
        domains_with_deltas: List of domain dictionaries with delta information
    """
    opportunity_targets = []
    
    for domain in domains_with_deltas:
        # Extract key metrics
        structure_score = domain.get("structure_score", 0)  # SEO score proxy
        visibility_score = domain.get("visibility_score", 0)  # LLMRank
        
        # Simple opportunity calculation (high structure, low visibility)
        if structure_score > 70 and visibility_score < 50:
            # Calculate opportunity score 
            opportunity_score = (structure_score - visibility_score) / 100 * 10
            
            # Check for digital ad spend signals in metadata
            metadata = domain.get("metadata", {})
            has_ads = metadata.get("has_ads", False)
            has_schema = metadata.get("has_schema", False)
            has_seo_stack = metadata.get("has_seo_stack", False)
            
            # Calculate customer likelihood index (simple version)
            # This would be much more sophisticated in production
            customer_likelihood = 0
            if has_ads:
                customer_likelihood += 30
            if has_schema:
                customer_likelihood += 25
            if has_seo_stack:
                customer_likelihood += 25
            if structure_score > 80:
                customer_likelihood += 20
                
            # Cap at 100
            customer_likelihood = min(customer_likelihood, 100)
            
            # Only include if customer likelihood is above threshold
            if customer_likelihood >= 50:
                target = {
                    "domain": domain.get("domain", ""),
                    "category": domain.get("category", ""),
                    "opportunity_score": opportunity_score,
                    "customer_likelihood": customer_likelihood,
                    "structure_score": structure_score,
                    "visibility_score": visibility_score,
                    "delta": domain.get("delta_info", {}).get("delta", 0),
                    "has_ads": has_ads,
                    "has_schema": has_schema,
                    "has_seo_stack": has_seo_stack
                }
                
                opportunity_targets.append(target)
    
    # Sort by opportunity score (descending)
    opportunity_targets.sort(key=lambda x: x["opportunity_score"], reverse=True)
    
    # Load existing targets
    existing_targets = []
    if os.path.exists(OPPORTUNITY_TARGETS_FILE):
        try:
            with open(OPPORTUNITY_TARGETS_FILE, "r") as f:
                existing_targets = json.load(f)
        except Exception as e:
            logger.error(f"Error loading opportunity targets file: {e}")
    
    # Combine and deduplicate by domain
    domain_map = {target["domain"]: target for target in existing_targets}
    
    for target in opportunity_targets:
        domain = target["domain"]
        if domain in domain_map:
            # Update existing entry
            domain_map[domain].update(target)
        else:
            # Add new entry
            domain_map[domain] = target
    
    # Convert back to list and sort
    updated_targets = list(domain_map.values())
    updated_targets.sort(key=lambda x: x["opportunity_score"], reverse=True)
    
    # Limit to top 100
    if len(updated_targets) > 100:
        updated_targets = updated_targets[:100]
    
    # Save the data
    try:
        with open(OPPORTUNITY_TARGETS_FILE, "w") as f:
            json.dump({
                "timestamp": time.time(),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "targets": updated_targets
            }, f, indent=2)
        logger.info(f"Updated opportunity targets with {len(updated_targets)} domains")
    except Exception as e:
        logger.error(f"Error saving opportunity targets file: {e}")

def process_domain_deltas(domain_results: List[Dict]) -> List[Dict]:
    """
    Process multiple domains to track their deltas and update trend data.
    
    Args:
        domain_results: List of domain result dictionaries
        
    Returns:
        Enriched list of domain results with delta information
    """
    # Get delta information for each domain
    domains_with_deltas = []
    
    for domain_data in domain_results:
        enriched_data = track_domain_delta(domain_data)
        domains_with_deltas.append(enriched_data)
    
    # Update weekly movers file
    update_weekly_movers(domains_with_deltas)
    
    # Identify opportunity targets
    identify_opportunity_targets(domains_with_deltas)
    
    return domains_with_deltas

def get_weekly_movers() -> Dict:
    """
    Get the latest weekly movers data.
    
    Returns:
        Dictionary containing the latest weekly movers data
    """
    if os.path.exists(WEEKLY_MOVERS_FILE):
        try:
            with open(WEEKLY_MOVERS_FILE, "r") as f:
                movers_data = json.load(f)
                if movers_data:
                    return movers_data[0]  # Return the most recent entry
        except Exception as e:
            logger.error(f"Error loading weekly movers: {e}")
    
    return {"timestamp": time.time(), "date": datetime.now().strftime("%Y-%m-%d"), "movers": []}

def get_opportunity_targets() -> Dict:
    """
    Get the opportunity targets data.
    
    Returns:
        Dictionary containing opportunity targets data
    """
    if os.path.exists(OPPORTUNITY_TARGETS_FILE):
        try:
            with open(OPPORTUNITY_TARGETS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading opportunity targets: {e}")
    
    return {"timestamp": time.time(), "date": datetime.now().strftime("%Y-%m-%d"), "targets": []}