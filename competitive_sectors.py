"""
Competitive Sectors Analysis Module

This module analyzes competitive sectors tracked by the Surface system,
providing insights into which categories have the highest memory vulnerability
and require priority monitoring.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SURFACE_DATA_DIR = "data/surface"
os.makedirs(SURFACE_DATA_DIR, exist_ok=True)

PRIORITY_CATEGORIES_PATH = os.path.join(SURFACE_DATA_DIR, "priority_categories.json")
CATEGORY_TRACKING_PATH = os.path.join(SURFACE_DATA_DIR, "category_tracking.json")


def load_competitive_categories() -> List[Dict]:
    """
    Load competitive categories from priority_categories.json.
    
    Returns:
        List of competitive category dictionaries
    """
    try:
        if os.path.exists(PRIORITY_CATEGORIES_PATH):
            with open(PRIORITY_CATEGORIES_PATH, 'r') as f:
                data = json.load(f)
                return data.get("fiercely_competitive_categories", [])
        else:
            logger.warning(f"Priority categories file not found at {PRIORITY_CATEGORIES_PATH}")
            return []
    except Exception as e:
        logger.error(f"Error loading competitive categories: {e}")
        return []


def load_vulnerability_factors() -> Dict:
    """
    Load vulnerability factors from priority_categories.json.
    
    Returns:
        Dictionary of vulnerability factors
    """
    try:
        if os.path.exists(PRIORITY_CATEGORIES_PATH):
            with open(PRIORITY_CATEGORIES_PATH, 'r') as f:
                data = json.load(f)
                return data.get("vulnerability_factors", {})
        else:
            logger.warning(f"Priority categories file not found at {PRIORITY_CATEGORIES_PATH}")
            return {}
    except Exception as e:
        logger.error(f"Error loading vulnerability factors: {e}")
        return {}


def load_high_risk_indicators() -> List[str]:
    """
    Load high risk indicators from priority_categories.json.
    
    Returns:
        List of high risk indicator strings
    """
    try:
        if os.path.exists(PRIORITY_CATEGORIES_PATH):
            with open(PRIORITY_CATEGORIES_PATH, 'r') as f:
                data = json.load(f)
                return data.get("high_risk_indicators", [])
        else:
            logger.warning(f"Priority categories file not found at {PRIORITY_CATEGORIES_PATH}")
            return []
    except Exception as e:
        logger.error(f"Error loading high risk indicators: {e}")
        return []


def get_category_tracking_data() -> Dict:
    """
    Get category tracking data from category_tracking.json.
    If the file doesn't exist, create default tracking data.
    
    Returns:
        Dictionary with category tracking data
    """
    try:
        if os.path.exists(CATEGORY_TRACKING_PATH):
            with open(CATEGORY_TRACKING_PATH, 'r') as f:
                return json.load(f)
        else:
            # Initialize tracking data with default values
            tracking_data = _initialize_tracking_data()
            
            # Save initialized data
            with open(CATEGORY_TRACKING_PATH, 'w') as f:
                json.dump(tracking_data, f, indent=2)
            
            return tracking_data
    except Exception as e:
        logger.error(f"Error getting category tracking data: {e}")
        return {}


def _initialize_tracking_data() -> Dict:
    """
    Initialize category tracking data for competitive categories.
    
    Returns:
        Dictionary with initialized tracking data
    """
    competitive_categories = load_competitive_categories()
    
    tracking_data = {
        "categories": {},
        "tracking_started": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "total_checks": 0,
        "tracked_metrics": [
            "memory_miss_rate",
            "citation_rate",
            "hallucination_rate",
            "accuracy_score",
            "pickup_rate"
        ]
    }
    
    # Initialize data for each category
    for category in competitive_categories:
        category_name = category["name"]
        
        # Initial tracking metrics
        tracking_data["categories"][category_name] = {
            "memory_vulnerability": category.get("memory_vulnerability", 0.5),
            "brands": category.get("brands", []),
            "key_attributes": category.get("key_attributes", []),
            "tracking_metrics": {
                "memory_miss_rate": round(random.uniform(0.15, 0.45), 2),
                "citation_rate": round(random.uniform(0.3, 0.9), 2),
                "hallucination_rate": round(random.uniform(0.05, 0.35), 2),
                "accuracy_score": round(random.uniform(0.55, 0.95), 2),
                "pickup_rate": round(random.uniform(0.35, 0.85), 2)
            },
            "check_history": [],
            "last_check": datetime.now().isoformat(),
            "next_check_priority": "medium" if category.get("memory_vulnerability", 0.5) < 0.8 else "high"
        }
        
        # Add a few check history entries
        for _ in range(3):
            check_date = datetime.now().isoformat()
            
            # Random metrics for historical checks
            check_data = {
                "timestamp": check_date,
                "metrics": {
                    "memory_miss_rate": round(random.uniform(0.15, 0.45), 2),
                    "citation_rate": round(random.uniform(0.3, 0.9), 2),
                    "hallucination_rate": round(random.uniform(0.05, 0.35), 2),
                    "accuracy_score": round(random.uniform(0.55, 0.95), 2),
                    "pickup_rate": round(random.uniform(0.35, 0.85), 2)
                },
                "issues_detected": random.randint(0, 3),
                "corrections_applied": random.randint(0, 2)
            }
            
            tracking_data["categories"][category_name]["check_history"].append(check_data)
    
    return tracking_data


def get_metrics_descriptions() -> Dict[str, str]:
    """
    Get descriptions for tracking metrics.
    
    Returns:
        Dictionary mapping metric names to descriptions
    """
    return {
        "memory_miss_rate": "Percentage of times when entities from this category are omitted or forgotten in LLM responses",
        "citation_rate": "Frequency with which entities from this category are properly cited in LLM outputs",
        "hallucination_rate": "Rate at which false or incorrect information is generated about entities in this category",
        "accuracy_score": "Overall accuracy of information recalled about entities in this category",
        "pickup_rate": "Rate at which Surface-generated corrections are adopted by LLMs in subsequent responses"
    }


def get_highest_risk_categories(limit: int = 5) -> List[Dict]:
    """
    Get highest risk categories based on memory vulnerability score.
    
    Args:
        limit: Maximum number of categories to return
        
    Returns:
        List of highest risk category dictionaries
    """
    competitive_categories = load_competitive_categories()
    
    # Sort by memory vulnerability (highest first)
    sorted_categories = sorted(
        competitive_categories,
        key=lambda x: x.get("memory_vulnerability", 0),
        reverse=True
    )
    
    # Return top N categories
    return sorted_categories[:limit]


def get_category_brands(category_name: str) -> List[str]:
    """
    Get brands for a specific category.
    
    Args:
        category_name: Name of the category
        
    Returns:
        List of brand names in the category
    """
    competitive_categories = load_competitive_categories()
    
    # Find matching category
    for category in competitive_categories:
        if category["name"] == category_name:
            return category.get("brands", [])
    
    return []


def get_brand_vulnerability_scores() -> List[Dict]:
    """
    Get vulnerability scores for all brands across categories.
    
    Returns:
        List of dictionaries with brand vulnerability data
    """
    competitive_categories = load_competitive_categories()
    tracking_data = get_category_tracking_data()
    
    brands_data = []
    
    for category in competitive_categories:
        category_name = category["name"]
        category_vulnerability = category.get("memory_vulnerability", 0.5)
        
        # Get brands for this category
        brands = category.get("brands", [])
        
        # Get category metrics
        category_metrics = {}
        if category_name in tracking_data.get("categories", {}):
            category_metrics = tracking_data["categories"][category_name].get("tracking_metrics", {})
        
        # Process each brand
        for brand in brands:
            # Calculate brand-specific vulnerability score
            # In a real system, this would use brand-specific data
            # Here we're using category vulnerability with a small random variation
            brand_vulnerability = min(
                1.0,
                max(0.0, category_vulnerability + random.uniform(-0.1, 0.1))
            )
            
            # Calculate brand-specific metrics
            # Again, in a real system these would be measured directly
            brand_metrics = {}
            for metric, value in category_metrics.items():
                brand_metrics[metric] = min(
                    1.0,
                    max(0.0, value + random.uniform(-0.15, 0.15))
                )
            
            # Add brand data
            brands_data.append({
                "brand": brand,
                "category": category_name,
                "vulnerability_score": round(brand_vulnerability, 2),
                "metrics": brand_metrics
            })
    
    # Sort by vulnerability score (highest first)
    brands_data.sort(key=lambda x: x["vulnerability_score"], reverse=True)
    
    return brands_data


def get_brand_detail(brand_name: str) -> Optional[Dict]:
    """
    Get detailed information for a specific brand.
    
    Args:
        brand_name: Name of the brand
        
    Returns:
        Dictionary with brand details or None if not found
    """
    brands_data = get_brand_vulnerability_scores()
    
    # Find matching brand
    for brand_data in brands_data:
        if brand_data["brand"] == brand_name:
            return brand_data
    
    return None


def simulate_check_cycle():
    """
    Simulate a check cycle for all categories, updating tracking data.
    """
    tracking_data = get_category_tracking_data()
    
    # Update last check time and increment total checks
    tracking_data["last_updated"] = datetime.now().isoformat()
    tracking_data["total_checks"] = tracking_data.get("total_checks", 0) + 1
    
    # Update each category
    for category_name, category_data in tracking_data.get("categories", {}).items():
        # Update last check time
        category_data["last_check"] = datetime.now().isoformat()
        
        # Slightly adjust tracking metrics
        metrics = category_data.get("tracking_metrics", {})
        for metric_name, metric_value in metrics.items():
            # Random slight adjustment
            new_value = min(1.0, max(0.0, metric_value + random.uniform(-0.05, 0.05)))
            metrics[metric_name] = round(new_value, 2)
        
        # Create new check history entry
        check_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics.copy(),
            "issues_detected": random.randint(0, 5),
            "corrections_applied": random.randint(0, 3)
        }
        
        # Add to check history
        category_data["check_history"] = category_data.get("check_history", []) + [check_data]
        
        # Update next check priority based on vulnerabilities and issues
        if metrics.get("memory_miss_rate", 0) > 0.4 or metrics.get("hallucination_rate", 0) > 0.3:
            category_data["next_check_priority"] = "high"
        elif check_data["issues_detected"] > 3:
            category_data["next_check_priority"] = "high"
        elif metrics.get("accuracy_score", 0) > 0.85 and check_data["issues_detected"] == 0:
            category_data["next_check_priority"] = "low"
        else:
            category_data["next_check_priority"] = "medium"
    
    # Save updated tracking data
    try:
        with open(CATEGORY_TRACKING_PATH, 'w') as f:
            json.dump(tracking_data, f, indent=2)
        logger.info("Updated category tracking data after check cycle")
    except Exception as e:
        logger.error(f"Error saving category tracking data: {e}")


def get_check_cycle_stats() -> Dict:
    """
    Get statistics about check cycles.
    
    Returns:
        Dictionary with check cycle statistics
    """
    tracking_data = get_category_tracking_data()
    
    # Count categories by priority
    priorities = {"high": 0, "medium": 0, "low": 0}
    
    for category_data in tracking_data.get("categories", {}).values():
        priority = category_data.get("next_check_priority", "medium")
        priorities[priority] = priorities.get(priority, 0) + 1
    
    # Calculate total issues and corrections
    total_issues = 0
    total_corrections = 0
    
    for category_data in tracking_data.get("categories", {}).values():
        for check in category_data.get("check_history", []):
            total_issues += check.get("issues_detected", 0)
            total_corrections += check.get("corrections_applied", 0)
    
    # Return stats
    return {
        "total_checks": tracking_data.get("total_checks", 0),
        "total_categories": len(tracking_data.get("categories", {})),
        "priority_distribution": priorities,
        "total_issues_detected": total_issues,
        "total_corrections_applied": total_corrections,
        "correction_rate": round(total_corrections / max(1, total_issues), 2),
        "last_updated": tracking_data.get("last_updated")
    }