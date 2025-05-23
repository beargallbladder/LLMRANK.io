"""
Domain Memory Tracker

This module implements the Domain Memory Tracker component of the LLMRank Insight Engine.
It tracks the presence and rank of domains across LLM-generated outputs and
calculates memory decay metrics over time.
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_RANK = 100  # Maximum rank to track
DECAY_HALF_LIFE_DAYS = 14  # Half-life for memory decay calculation in days
SIGNIFICANT_DELTA_THRESHOLD = 3  # Minimum rank change to be considered significant

# File paths
DATA_DIR = "data/domain_memory"
os.makedirs(DATA_DIR, exist_ok=True)

DOMAIN_MEMORY_PATH = os.path.join(DATA_DIR, "domain_memory.json")
MEMORY_SNAPSHOTS_PATH = os.path.join(DATA_DIR, "memory_snapshots.json")
DELTA_ALERTS_PATH = os.path.join(DATA_DIR, "delta_alerts.json")


class DomainMemoryTracker:
    """
    Tracks the memory of domains across multiple LLMs and queries over time.
    Calculates rank, trends, and memory decay.
    """
    
    def __init__(self):
        """Initialize the domain memory tracker."""
        self.domain_memory = {}  # Domain -> model -> query_category -> rank history
        self.memory_snapshots = []  # List of memory snapshots (timestamp, model, query, domain, rank)
        self.delta_alerts = []  # List of significant delta events
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self):
        """Load existing data from files."""
        try:
            if os.path.exists(DOMAIN_MEMORY_PATH):
                with open(DOMAIN_MEMORY_PATH, 'r') as f:
                    self.domain_memory = json.load(f)
                    
            if os.path.exists(MEMORY_SNAPSHOTS_PATH):
                with open(MEMORY_SNAPSHOTS_PATH, 'r') as f:
                    self.memory_snapshots = json.load(f)
                    
            if os.path.exists(DELTA_ALERTS_PATH):
                with open(DELTA_ALERTS_PATH, 'r') as f:
                    self.delta_alerts = json.load(f)
                    
            logger.info("Domain memory data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading domain memory data: {e}")
            # Initialize with empty data
            self.domain_memory = {}
            self.memory_snapshots = []
            self.delta_alerts = []
    
    def _save_data(self):
        """Save current data to files."""
        try:
            # Save domain memory
            with open(DOMAIN_MEMORY_PATH, 'w') as f:
                json.dump(self.domain_memory, f, indent=2)
                
            # Save memory snapshots
            with open(MEMORY_SNAPSHOTS_PATH, 'w') as f:
                json.dump(self.memory_snapshots, f, indent=2)
                
            # Save delta alerts
            with open(DELTA_ALERTS_PATH, 'w') as f:
                json.dump(self.delta_alerts, f, indent=2)
                
            logger.info("Domain memory data saved successfully")
        except Exception as e:
            logger.error(f"Error saving domain memory data: {e}")
    
    def _get_formatted_timestamp(self) -> str:
        """Get a formatted timestamp."""
        return datetime.now().isoformat()
    
    def update_domain_rank(self, domain: str, model: str, query_category: str, 
                         rank: int, query_text: Optional[str] = None) -> Dict:
        """
        Update the rank of a domain for a specific model and query category.
        
        Args:
            domain: Domain name (e.g., "example.com")
            model: LLM model name (e.g., "gpt-4", "claude", "gemini")
            query_category: Category of the query (e.g., "travel", "finance")
            rank: Current rank of the domain (1-100, where 1 is highest)
            query_text: Optional specific query text used
            
        Returns:
            Dictionary with update status and delta information
        """
        timestamp = self._get_formatted_timestamp()
        
        # Initialize domain hierarchy if needed
        if domain not in self.domain_memory:
            self.domain_memory[domain] = {}
            
        if model not in self.domain_memory[domain]:
            self.domain_memory[domain][model] = {}
            
        if query_category not in self.domain_memory[domain][model]:
            self.domain_memory[domain][model][query_category] = {
                "rank_history": [],
                "last_updated": timestamp
            }
        
        # Get current data
        domain_data = self.domain_memory[domain][model][query_category]
        rank_history = domain_data["rank_history"]
        
        # Calculate delta if we have previous ranks
        delta = 0
        previous_rank = None
        
        if rank_history:
            previous_rank = rank_history[-1]["rank"]
            delta = previous_rank - rank  # Positive means improvement (up in rank)
        
        # Add new rank entry
        rank_entry = {
            "timestamp": timestamp,
            "rank": rank,
            "delta": delta,
            "query_text": query_text
        }
        
        rank_history.append(rank_entry)
        
        # Limit history size (keep last 100 entries)
        if len(rank_history) > 100:
            rank_history = rank_history[-100:]
            self.domain_memory[domain][model][query_category]["rank_history"] = rank_history
        
        # Update last updated timestamp
        self.domain_memory[domain][model][query_category]["last_updated"] = timestamp
        
        # Add to snapshots
        snapshot = {
            "timestamp": timestamp,
            "domain": domain,
            "model": model,
            "query_category": query_category,
            "query_text": query_text,
            "rank": rank,
            "delta": delta
        }
        
        self.memory_snapshots.append(snapshot)
        
        # Limit snapshots (keep last 10000)
        if len(self.memory_snapshots) > 10000:
            self.memory_snapshots = self.memory_snapshots[-10000:]
        
        # Check for significant delta
        alert_data = None
        
        if abs(delta) >= SIGNIFICANT_DELTA_THRESHOLD:
            alert = {
                "timestamp": timestamp,
                "domain": domain,
                "model": model,
                "query_category": query_category,
                "query_text": query_text,
                "previous_rank": previous_rank,
                "current_rank": rank,
                "delta": delta,
                "is_improvement": delta > 0,
                "notified": False
            }
            
            self.delta_alerts.append(alert)
            alert_data = alert
            
            logger.info(f"Significant delta detected for {domain} in {model}/{query_category}: {delta}")
        
        # Save data
        self._save_data()
        
        return {
            "status": "updated",
            "domain": domain,
            "model": model,
            "query_category": query_category,
            "current_rank": rank,
            "previous_rank": previous_rank,
            "delta": delta,
            "alert": alert_data
        }
    
    def get_domain_ranks(self, domain: str, 
                        model: Optional[str] = None, 
                        query_category: Optional[str] = None) -> Dict:
        """
        Get the current rank data for a domain, optionally filtered by model and category.
        
        Args:
            domain: Domain name
            model: Optional model filter
            query_category: Optional query category filter
            
        Returns:
            Dictionary with rank data
        """
        if domain not in self.domain_memory:
            return {"status": "not_found", "domain": domain}
        
        domain_data = self.domain_memory[domain]
        
        # Filter by model if provided
        if model:
            if model not in domain_data:
                return {"status": "model_not_found", "domain": domain, "model": model}
            domain_data = {model: domain_data[model]}
        
        # Filter by category if provided
        result = {"domain": domain, "models": {}}
        
        for model_name, model_data in domain_data.items():
            if query_category:
                if query_category not in model_data:
                    continue
                    
                # Get most recent rank
                rank_history = model_data[query_category]["rank_history"]
                if not rank_history:
                    continue
                    
                latest = rank_history[-1]
                
                result["models"][model_name] = {
                    query_category: {
                        "current_rank": latest["rank"],
                        "delta": latest["delta"],
                        "last_updated": model_data[query_category]["last_updated"]
                    }
                }
            else:
                # Get data for all categories
                result["models"][model_name] = {}
                
                for cat, cat_data in model_data.items():
                    rank_history = cat_data["rank_history"]
                    if not rank_history:
                        continue
                        
                    latest = rank_history[-1]
                    
                    result["models"][model_name][cat] = {
                        "current_rank": latest["rank"],
                        "delta": latest["delta"],
                        "last_updated": cat_data["last_updated"]
                    }
        
        return result
    
    def get_rank_history(self, domain: str, model: str, query_category: str, 
                       days: int = 30) -> List[Dict]:
        """
        Get rank history for a domain in a specific model and category over time.
        
        Args:
            domain: Domain name
            model: Model name
            query_category: Query category
            days: Number of days of history to retrieve
            
        Returns:
            List of rank history entries
        """
        if domain not in self.domain_memory or \
           model not in self.domain_memory[domain] or \
           query_category not in self.domain_memory[domain][model]:
            return []
        
        rank_history = self.domain_memory[domain][model][query_category]["rank_history"]
        
        # Filter by date range
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        filtered_history = [entry for entry in rank_history 
                          if entry["timestamp"] >= cutoff_date]
        
        return filtered_history
    
    def get_memory_decay(self, domain: str, model: Optional[str] = None, 
                       query_category: Optional[str] = None) -> Dict:
        """
        Calculate memory decay metrics for a domain.
        
        Args:
            domain: Domain name
            model: Optional model filter
            query_category: Optional query category filter
            
        Returns:
            Dictionary with memory decay metrics
        """
        if domain not in self.domain_memory:
            return {"status": "not_found", "domain": domain}
        
        domain_data = self.domain_memory[domain]
        
        # Filter by model if provided
        if model:
            if model not in domain_data:
                return {"status": "model_not_found", "domain": domain, "model": model}
            domain_data = {model: domain_data[model]}
        
        # Calculate decay metrics
        now = datetime.now()
        result = {"domain": domain, "models": {}}
        
        for model_name, model_data in domain_data.items():
            model_result = {}
            
            for cat, cat_data in model_data.items():
                if query_category and cat != query_category:
                    continue
                    
                rank_history = cat_data["rank_history"]
                if not rank_history:
                    continue
                
                # Calculate decay based on rank history
                decay_score = self._calculate_decay_score(rank_history, now)
                
                # Get trend direction (improving, declining, stable)
                trend = self._calculate_trend(rank_history)
                
                model_result[cat] = {
                    "decay_score": decay_score,
                    "trend": trend,
                    "current_rank": rank_history[-1]["rank"] if rank_history else None,
                    "data_points": len(rank_history)
                }
            
            if model_result:
                result["models"][model_name] = model_result
        
        return result
    
    def _calculate_decay_score(self, rank_history: List[Dict], now: datetime) -> float:
        """
        Calculate a memory decay score based on rank history.
        
        Args:
            rank_history: List of rank history entries
            now: Current datetime
            
        Returns:
            Decay score between 0 and 1 (lower is more decay)
        """
        if not rank_history:
            return 0.0
        
        # Calculate weighted average based on recency
        weights = []
        ranks = []
        
        for entry in rank_history:
            entry_time = datetime.fromisoformat(entry["timestamp"])
            days_ago = (now - entry_time).total_seconds() / (24 * 3600)
            
            # Calculate weight using exponential decay
            weight = 2 ** (-days_ago / DECAY_HALF_LIFE_DAYS)
            weights.append(weight)
            
            # Normalize rank (higher rank = worse)
            normalized_rank = 1.0 - (min(entry["rank"], MAX_RANK) / MAX_RANK)
            ranks.append(normalized_rank)
        
        if not weights:
            return 0.0
            
        # Calculate weighted average
        decay_score = sum(w * r for w, r in zip(weights, ranks)) / sum(weights)
        
        return round(decay_score, 3)
    
    def _calculate_trend(self, rank_history: List[Dict]) -> str:
        """
        Calculate trend direction based on rank history.
        
        Args:
            rank_history: List of rank history entries
            
        Returns:
            Trend direction ("improving", "declining", "stable")
        """
        if len(rank_history) < 2:
            return "stable"
        
        # Look at the last 5 entries or all if fewer
        recent_history = rank_history[-min(5, len(rank_history)):]
        
        # Calculate average delta
        deltas = [entry["delta"] for entry in recent_history if "delta" in entry]
        
        if not deltas:
            return "stable"
            
        avg_delta = sum(deltas) / len(deltas)
        
        if avg_delta > 1.0:
            return "improving"
        elif avg_delta < -1.0:
            return "declining"
        else:
            return "stable"
    
    def get_significant_deltas(self, days: int = 7, 
                             domain: Optional[str] = None,
                             model: Optional[str] = None,
                             query_category: Optional[str] = None) -> List[Dict]:
        """
        Get significant delta events, optionally filtered.
        
        Args:
            days: Number of days to look back
            domain: Optional domain filter
            model: Optional model filter
            query_category: Optional query category filter
            
        Returns:
            List of delta alert dictionaries
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Filter alerts
        filtered_alerts = []
        
        for alert in self.delta_alerts:
            if alert["timestamp"] < cutoff_date:
                continue
                
            if domain and alert["domain"] != domain:
                continue
                
            if model and alert["model"] != model:
                continue
                
            if query_category and alert["query_category"] != query_category:
                continue
                
            filtered_alerts.append(alert)
        
        # Sort by timestamp (newest first)
        return sorted(filtered_alerts, key=lambda x: x["timestamp"], reverse=True)
    
    def mark_alerts_as_notified(self, alert_ids: List[str]) -> int:
        """
        Mark specified alerts as notified.
        
        Args:
            alert_ids: List of alert IDs (timestamps) to mark
            
        Returns:
            Number of alerts updated
        """
        count = 0
        
        for alert in self.delta_alerts:
            if alert["timestamp"] in alert_ids and not alert["notified"]:
                alert["notified"] = True
                count += 1
        
        if count > 0:
            self._save_data()
            
        return count
    
    def get_top_domains(self, model: str, query_category: str, limit: int = 100) -> List[Dict]:
        """
        Get top domains for a specific model and category.
        
        Args:
            model: Model name
            query_category: Query category
            limit: Maximum number of domains to return
            
        Returns:
            List of domain dictionaries with rank information
        """
        domains = []
        
        for domain, domain_data in self.domain_memory.items():
            if model in domain_data and query_category in domain_data[model]:
                rank_history = domain_data[model][query_category]["rank_history"]
                
                if rank_history:
                    latest = rank_history[-1]
                    
                    domains.append({
                        "domain": domain,
                        "rank": latest["rank"],
                        "delta": latest["delta"],
                        "last_updated": domain_data[model][query_category]["last_updated"]
                    })
        
        # Sort by rank (ascending)
        sorted_domains = sorted(domains, key=lambda x: x["rank"])
        
        return sorted_domains[:limit]


# Singleton instance
_domain_memory_tracker = None

def get_tracker() -> DomainMemoryTracker:
    """Get the domain memory tracker singleton instance."""
    global _domain_memory_tracker
    
    if _domain_memory_tracker is None:
        _domain_memory_tracker = DomainMemoryTracker()
    
    return _domain_memory_tracker

def update_domain_rank(domain: str, model: str, query_category: str, 
                     rank: int, query_text: Optional[str] = None) -> Dict:
    """
    Update the rank of a domain for a specific model and query category.
    
    Args:
        domain: Domain name (e.g., "example.com")
        model: LLM model name (e.g., "gpt-4", "claude", "gemini")
        query_category: Category of the query (e.g., "travel", "finance")
        rank: Current rank of the domain (1-100, where 1 is highest)
        query_text: Optional specific query text used
        
    Returns:
        Dictionary with update status and delta information
    """
    return get_tracker().update_domain_rank(domain, model, query_category, rank, query_text)

def get_domain_ranks(domain: str, 
                    model: Optional[str] = None, 
                    query_category: Optional[str] = None) -> Dict:
    """
    Get the current rank data for a domain, optionally filtered by model and category.
    
    Args:
        domain: Domain name
        model: Optional model filter
        query_category: Optional query category filter
        
    Returns:
        Dictionary with rank data
    """
    return get_tracker().get_domain_ranks(domain, model, query_category)

def get_rank_history(domain: str, model: str, query_category: str, 
                   days: int = 30) -> List[Dict]:
    """
    Get rank history for a domain in a specific model and category over time.
    
    Args:
        domain: Domain name
        model: Model name
        query_category: Query category
        days: Number of days of history to retrieve
        
    Returns:
        List of rank history entries
    """
    return get_tracker().get_rank_history(domain, model, query_category, days)

def get_memory_decay(domain: str, model: Optional[str] = None, 
                   query_category: Optional[str] = None) -> Dict:
    """
    Calculate memory decay metrics for a domain.
    
    Args:
        domain: Domain name
        model: Optional model filter
        query_category: Optional query category filter
        
    Returns:
        Dictionary with memory decay metrics
    """
    return get_tracker().get_memory_decay(domain, model, query_category)

def get_significant_deltas(days: int = 7, 
                         domain: Optional[str] = None,
                         model: Optional[str] = None,
                         query_category: Optional[str] = None) -> List[Dict]:
    """
    Get significant delta events, optionally filtered.
    
    Args:
        days: Number of days to look back
        domain: Optional domain filter
        model: Optional model filter
        query_category: Optional query category filter
        
    Returns:
        List of delta alert dictionaries
    """
    return get_tracker().get_significant_deltas(days, domain, model, query_category)

def get_top_domains(model: str, query_category: str, limit: int = 100) -> List[Dict]:
    """
    Get top domains for a specific model and category.
    
    Args:
        model: Model name
        query_category: Query category
        limit: Maximum number of domains to return
        
    Returns:
        List of domain dictionaries with rank information
    """
    return get_tracker().get_top_domains(model, query_category, limit)