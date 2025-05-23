"""
PRD-24.2: Insight Integrity, Scoring & Story-Driven Signal System

This module defines the schema and data structures for the insight integrity system.
"""

import os
import json
import time
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory structure
DATA_DIR = "data"
INSIGHTS_DIR = f"{DATA_DIR}/insights"
LOGS_DIR = f"{DATA_DIR}/logs"
STORIES_DIR = f"{DATA_DIR}/stories"

# Ensure directories exist
os.makedirs(INSIGHTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(STORIES_DIR, exist_ok=True)

# File paths
INSIGHT_LOG_FILE = f"{INSIGHTS_DIR}/insight_log.json"
INTEGRITY_REPORT_FILE = f"{LOGS_DIR}/integrity_report.json"
HOT_STORIES_FILE = f"{LOGS_DIR}/hot_stories_by_category.json"
TREND_ANOMALIES_FILE = f"{LOGS_DIR}/trend_anomalies_detected.json"
WEEKLY_SUMMARY_FILE = f"{STORIES_DIR}/weekly_summary.md"

# Schema constants
INSIGHT_TYPES = [
    "trust_spike", "trust_drop", "model_disagreement", 
    "volatility_surge", "category_shift", "peer_overtaken",
    "new_challenger", "industry_disruption", "benchmark_movement"
]

HEAT_INDEX_VALUES = ["low", "medium", "high", "critical"]

def generate_insight_id() -> str:
    """Generate a unique ID for an insight."""
    return f"insight_{str(uuid.uuid4())[:8]}"

def get_current_version_tag() -> str:
    """Get the current version tag based on date."""
    return f"mcp_sync_{datetime.now().strftime('%Y_%m_%d')}"

def create_insight(
    domain: str,
    category: str,
    insight_type: str,
    trust_delta: float,
    prompt_id: str,
    source_model: str,
    agent_id: str,
    score: float,
    heat_index: str,
    additional_data: Optional[Dict] = None
) -> Dict:
    """
    Create a new insight entry following the schema.
    
    Args:
        domain: The domain name
        category: The category of the domain
        insight_type: The type of insight
        trust_delta: The change in trust score
        prompt_id: The ID of the prompt
        source_model: The source model
        agent_id: The ID of the agent
        score: The calculated insight score
        heat_index: The heat index
        additional_data: Additional data to include
        
    Returns:
        The created insight dictionary
    """
    # Validate input parameters
    if insight_type not in INSIGHT_TYPES:
        logger.warning(f"Invalid insight type: {insight_type}")
        insight_type = "trust_spike"  # Default
    
    if heat_index not in HEAT_INDEX_VALUES:
        logger.warning(f"Invalid heat index: {heat_index}")
        heat_index = "medium"  # Default
    
    # Create insight
    insight = {
        "id": generate_insight_id(),
        "domain": domain,
        "category": category,
        "type": insight_type,
        "trust_delta": round(trust_delta, 2),
        "prompt_id": prompt_id,
        "source_model": source_model,
        "agent_id": agent_id,
        "score": round(score, 1),
        "heat_index": heat_index,
        "timestamp": datetime.now().isoformat() + "Z",
        "version_tag": get_current_version_tag()
    }
    
    # Add additional data if provided
    if additional_data:
        insight.update(additional_data)
    
    return insight

def save_insight(insight: Dict) -> bool:
    """
    Save an insight to the insight log file.
    
    Args:
        insight: The insight dictionary
        
    Returns:
        Success flag
    """
    # Load existing insights
    insights = load_insights()
    
    # Add new insight
    insights.append(insight)
    
    # Save insights
    try:
        with open(INSIGHT_LOG_FILE, 'w') as f:
            json.dump(insights, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving insight: {e}")
        return False

def load_insights() -> List[Dict]:
    """
    Load insights from the insight log file.
    
    Returns:
        List of insight dictionaries
    """
    if not os.path.exists(INSIGHT_LOG_FILE):
        return []
    
    try:
        with open(INSIGHT_LOG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading insights: {e}")
        return []

def calculate_insight_score(
    trust_delta: float,
    model_disagreement: float,
    volatility: float,
    rarity: float
) -> float:
    """
    Calculate the insight score using the PRD-24.2 formula.
    
    Args:
        trust_delta: The change in trust score
        model_disagreement: The disagreement between models
        volatility: The week-to-week signal instability
        rarity: The uniqueness of movement in category
        
    Returns:
        The calculated score
    """
    score = (
        (trust_delta * 1.5) + 
        (model_disagreement * 2.0) + 
        (volatility * 1.2) + 
        (rarity * 1.3)
    )
    
    # Normalize score between 0 and 100
    return min(max(score, 0), 100)

def determine_heat_index(score: float) -> str:
    """
    Determine the heat index based on the score.
    
    Args:
        score: The insight score
        
    Returns:
        The heat index
    """
    if score < 30:
        return "low"
    elif score < 60:
        return "medium"
    elif score < 85:
        return "high"
    else:
        return "critical"

def save_integrity_report(report: Dict) -> bool:
    """
    Save an integrity report to the integrity report file.
    
    Args:
        report: The integrity report dictionary
        
    Returns:
        Success flag
    """
    try:
        with open(INTEGRITY_REPORT_FILE, 'w') as f:
            json.dump(report, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving integrity report: {e}")
        return False

def save_hot_stories(stories: Dict) -> bool:
    """
    Save hot stories to the hot stories file.
    
    Args:
        stories: The hot stories dictionary
        
    Returns:
        Success flag
    """
    try:
        with open(HOT_STORIES_FILE, 'w') as f:
            json.dump(stories, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving hot stories: {e}")
        return False

def save_trend_anomalies(anomalies: List[Dict]) -> bool:
    """
    Save trend anomalies to the trend anomalies file.
    
    Args:
        anomalies: The list of trend anomaly dictionaries
        
    Returns:
        Success flag
    """
    try:
        with open(TREND_ANOMALIES_FILE, 'w') as f:
            json.dump(anomalies, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving trend anomalies: {e}")
        return False

def save_weekly_summary(summary: str) -> bool:
    """
    Save a weekly summary to the weekly summary file.
    
    Args:
        summary: The weekly summary
        
    Returns:
        Success flag
    """
    try:
        with open(WEEKLY_SUMMARY_FILE, 'w') as f:
            f.write(summary)
        return True
    except Exception as e:
        logger.error(f"Error saving weekly summary: {e}")
        return False