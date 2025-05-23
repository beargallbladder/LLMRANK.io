"""
Category Matrix Analysis for LLMPageRank V10

This module implements the special category analysis features for tracking
exceptional trust profiles, benchmarking outliers, and identifying emerging
patterns across domain categories.
"""

import os
import json
import time
import random
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Import project modules
from foma_insight_engine import start_foma_engine, get_elite_insights
from runtime_cadence import start_cadence_manager, get_categories, get_domains

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "data"
MATRIX_DIR = f"{DATA_DIR}/matrix"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MATRIX_DIR, exist_ok=True)

class CategoryMatrix:
    """
    Category Matrix Analysis for identifying exceptional trust signals
    and category-level patterns.
    """
    
    def __init__(self):
        """Initialize the category matrix analyzer."""
        # Start related engines
        self.foma_engine = start_foma_engine()
        self.cadence_manager = start_cadence_manager()
        
        # Load data
        self.categories = get_categories()
        self.domains = get_domains()
        self.category_matrix = self._load_category_matrix()
    
    def _load_category_matrix(self):
        """Load category matrix data."""
        matrix_file = f"{MATRIX_DIR}/category_matrix.json"
        
        try:
            if os.path.exists(matrix_file):
                with open(matrix_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading category matrix: {e}")
        
        # Create initial matrix data with placeholder values for now
        # These will be properly implemented later
        matrix = {
            "best_categories": [],
            "worst_categories": [],
            "rising_categories": [],
            "declining_categories": [],
            "cross_category_movers": [],
            "volatility_leaders": [],
            "stability_champions": [],
            "last_updated": time.time()
        }
        
        # Save matrix to file
        os.makedirs(os.path.dirname(matrix_file), exist_ok=True)
        with open(matrix_file, 'w') as f:
            json.dump(matrix, f, indent=2)
        
        return matrix
        
    def _identify_best_categories(self):
        """Identify categories with the highest trust scores."""
        # Will be implemented in future updates
        return []
        
    def _identify_worst_categories(self):
        """Identify categories with the lowest trust scores."""
        # Will be implemented in future updates
        return []
        
    def _identify_rising_categories(self):
        """Identify categories with the most positive trust score movement."""
        # Will be implemented in future updates
        return []
        
    def _identify_declining_categories(self):
        """Identify categories with the most negative trust score movement."""
        # Will be implemented in future updates
        return []
        
    def _identify_cross_category_movers(self):
        """Identify domains that excel across multiple categories."""
        # Will be implemented in future updates
        return []
        
    def _identify_volatility_leaders(self):
        """Identify domains with the highest trust volatility."""
        # Will be implemented in future updates
        return []
        
    def _identify_stability_champions(self):
        """Identify domains with exceptional trust stability and high scores."""
        # Will be implemented in future updates
        return []
        
    def _get_elite_domains(self, category):
        """Get elite domains for a specific category."""
        # Will be implemented in future updates
        return []
        
    def _get_top_performer(self, category):
        """Get the top performing domain in a category."""
        # Will be implemented in future updates
        return None
        
    def _get_lowest_trust_score(self, category):
        """Get the lowest trust score in a category."""
        # Will be implemented in future updates
        return None
        
    def _get_most_volatile_domain(self, category):
        """Get the most volatile domain in a category."""
        # Will be implemented in future updates
        return None
        
    def _get_top_riser(self, category):
        """Get the domain with the largest positive movement in a category."""
        # Will be implemented in future updates
        return None
        
    def _get_top_decliner(self, category):
        """Get the domain with the largest negative movement in a category."""
        # Will be implemented in future updates
        return None
        
    def _identify_volatility_pattern(self, trend):
        """Identify the volatility pattern from trend data."""
        # Will be implemented in future updates
        return "steady"

# The following functions are needed for dashboard_v3.py
def get_category_stats(category=None):
    """
    Get stats for a specific category or all categories.
    
    Args:
        category: Optional category name to filter for
        
    Returns:
        Dictionary of category statistics
    """
    try:
        # Load category data
        matrix = CategoryMatrix()
        
        if category:
            # Filter for specific category
            domains = [d for d, data in matrix.domains.items() 
                     if data.get("category") == category]
            
            if not domains:
                return {"error": f"Category '{category}' not found"}
            
            # Calculate stats for this category
            trust_scores = [matrix.domains[d].get("trust_score", 0) for d in domains]
            
            return {
                "category": category,
                "domain_count": len(domains),
                "average_trust_score": round(sum(trust_scores) / len(trust_scores), 1) if trust_scores else 0,
                "highest_trust_score": round(max(trust_scores), 1) if trust_scores else 0,
                "lowest_trust_score": round(min(trust_scores), 1) if trust_scores else 0,
                "elite_domains": [d for d in domains if matrix.domains[d].get("trust_score", 0) >= 90],
                "domains": domains
            }
        else:
            # Get stats for all categories
            categories = {}
            for domain, data in matrix.domains.items():
                cat = data.get("category", "unknown")
                if cat not in categories:
                    categories[cat] = {
                        "domain_count": 0,
                        "trust_scores": []
                    }
                categories[cat]["domain_count"] += 1
                categories[cat]["trust_scores"].append(data.get("trust_score", 0))
            
            # Calculate averages
            results = {}
            for cat, stats in categories.items():
                scores = stats["trust_scores"]
                results[cat] = {
                    "domain_count": stats["domain_count"],
                    "average_trust_score": round(sum(scores) / len(scores), 1) if scores else 0,
                    "highest_trust_score": round(max(scores), 1) if scores else 0,
                    "lowest_trust_score": round(min(scores), 1) if scores else 0
                }
            
            return results
    except Exception as e:
        logger.error(f"Error in get_category_stats: {e}")
        return {"error": str(e)}

def calculate_foma_score(domain):
    """
    Calculate FOMA (Fear of Missing Attention) score for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        FOMA score (0-100)
    """
    try:
        # Load domain data
        matrix = CategoryMatrix()
        
        if domain not in matrix.domains:
            return 0
        
        domain_data = matrix.domains[domain]
        
        # Trust score contribution
        trust_score = domain_data.get("trust_score", 0)
        trust_component = trust_score * 0.5  # 50% weight
        
        # Trend contribution (if available)
        trend_component = 0
        if "weekly_trust_trend" in domain_data:
            trends = domain_data["weekly_trust_trend"]
            if len(trends) >= 4:
                # Calculate growth over the last 4 weeks
                start = trends[-4]
                end = trends[-1]
                growth = end - start
                
                # Positive growth increases FOMA score
                if growth > 0:
                    trend_component = min(30, growth * 7.5)  # Up to 30 points for trend
        
        # Volatility contribution (if available)
        volatility_component = 0
        volatility = domain_data.get("trust_volatility", 0)
        if volatility > 0:
            volatility_component = min(20, volatility * 100)  # Up to 20 points for volatility
        
        # Calculate total FOMA score
        foma_score = trust_component + trend_component + volatility_component
        
        # Cap at 100
        return min(100, round(foma_score, 1))
    except Exception as e:
        logger.error(f"Error in calculate_foma_score: {e}")
        return 0

def get_peer_domains(domain, count=5):
    """
    Get peer domains for comparison.
    
    Args:
        domain: Domain name
        count: Number of peers to return
        
    Returns:
        List of peer domain info dictionaries
    """
    try:
        # Load domain data
        matrix = CategoryMatrix()
        
        if domain not in matrix.domains:
            return []
        
        domain_data = matrix.domains[domain]
        category = domain_data.get("category", "unknown")
        
        # Get domains in the same category
        peer_domains = [d for d in matrix.domains if matrix.domains[d].get("category") == category and d != domain]
        
        # Sort by trust score similarity
        domain_score = domain_data.get("trust_score", 0)
        peer_domains.sort(key=lambda d: abs(matrix.domains[d].get("trust_score", 0) - domain_score))
        
        # Build response data
        peers = []
        for peer in peer_domains[:count]:
            peer_data = matrix.domains[peer]
            peers.append({
                "domain": peer,
                "trust_score": peer_data.get("trust_score", 0),
                "citation_rate": peer_data.get("citation_rate", 0),
                "score_difference": round(peer_data.get("trust_score", 0) - domain_score, 1)
            })
        
        return peers
    except Exception as e:
        logger.error(f"Error in get_peer_domains: {e}")
        return []

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "data"
MATRIX_DIR = f"{DATA_DIR}/matrix"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MATRIX_DIR, exist_ok=True)

class CategoryMatrix:
    """
    Category Matrix Analysis for identifying exceptional trust signals
    and category-level patterns.
    """
    
    def __init__(self):
        """Initialize the category matrix analyzer."""
        # Start related engines
        self.foma_engine = start_foma_engine()
        self.cadence_manager = start_cadence_manager()
        
        # Load data
        self.categories = get_categories()
        self.domains = get_domains()
        self.category_matrix = self._load_category_matrix()
    
    def _load_category_matrix(self):
        """Load category matrix data."""
        matrix_file = f"{MATRIX_DIR}/category_matrix.json"
        
        try:
            if os.path.exists(matrix_file):
                with open(matrix_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading category matrix: {e}")
        
        # Create initial matrix data
        matrix = {
            "best_categories": self._identify_best_categories(),
            "worst_categories": self._identify_worst_categories(),
            "rising_categories": self._identify_rising_categories(),
            "declining_categories": self._identify_declining_categories(),
            "cross_category_movers": self._identify_cross_category_movers(),
            "volatility_leaders": self._identify_volatility_leaders(),
            "stability_champions": self._identify_stability_champions(),
            "last_updated": time.time()
        }
        
        # Save matrix to file
        os.makedirs(os.path.dirname(matrix_file), exist_ok=True)
        with open(matrix_file, 'w') as f:
            json.dump(matrix, f, indent=2)
        
        return matrix
    
    def _identify_best_categories(self):
        """Identify categories with the highest trust scores."""
        category_scores = {}
        
        # Calculate average score for each category
        for domain, data in self.domains.items():
            category = data.get("category", "unknown")
            trust_score = data.get("trust_score", 0)
            
            if category not in category_scores:
                category_scores[category] = {"total": 0, "count": 0}
            
            category_scores[category]["total"] += trust_score
            category_scores[category]["count"] += 1
        
        # Calculate averages
        best_categories = []
        for category, scores in category_scores.items():
            if scores["count"] > 0:
                avg_score = scores["total"] / scores["count"]
                best_categories.append({
                    "category": category,
                    "average_trust_score": round(avg_score, 1),
                    "domain_count": scores["count"],
                    "elite_domain_count": len(self._get_elite_domains(category)),
                    "top_performer": self._get_top_performer(category)
                })
        
        # Sort by average trust score
        best_categories.sort(key=lambda x: x["average_trust_score"], reverse=True)
        
        # Keep top 3
        return best_categories[:3]
    
    def _identify_worst_categories(self):
        """Identify categories with the lowest trust scores."""
        category_scores = {}
        
        # Calculate average score for each category
        for domain, data in self.domains.items():
            category = data.get("category", "unknown")
            trust_score = data.get("trust_score", 0)
            
            if category not in category_scores:
                category_scores[category] = {"total": 0, "count": 0}
            
            category_scores[category]["total"] += trust_score
            category_scores[category]["count"] += 1
        
        # Calculate averages
        worst_categories = []
        for category, scores in category_scores.items():
            if scores["count"] > 0:
                avg_score = scores["total"] / scores["count"]
                worst_categories.append({
                    "category": category,
                    "average_trust_score": round(avg_score, 1),
                    "domain_count": scores["count"],
                    "lowest_trust_score": self._get_lowest_trust_score(category),
                    "most_volatile_domain": self._get_most_volatile_domain(category)
                })
        
        # Sort by average trust score
        worst_categories.sort(key=lambda x: x["average_trust_score"])
        
        # Keep top 3
        return worst_categories[:3]
    
    def _identify_rising_categories(self):
        """Identify categories with the most positive trust score movement."""
        category_movements = {}
        
        # Calculate average movement for each category
        for domain, data in self.domains.items():
            category = data.get("category", "unknown")
            
            if "weekly_trust_trend" in data and len(data["weekly_trust_trend"]) >= 4:
                # Calculate 4-week movement
                start = data["weekly_trust_trend"][-4]
                end = data["weekly_trust_trend"][-1]
                movement = end - start
                
                if category not in category_movements:
                    category_movements[category] = {"total": 0, "count": 0}
                
                category_movements[category]["total"] += movement
                category_movements[category]["count"] += 1
        
        # Calculate averages
        rising_categories = []
        for category, movements in category_movements.items():
            if movements["count"] > 0:
                avg_movement = movements["total"] / movements["count"]
                if avg_movement > 0:  # Only include categories with positive movement
                    rising_categories.append({
                        "category": category,
                        "average_movement": round(avg_movement, 1),
                        "domain_count": movements["count"],
                        "top_riser": self._get_top_riser(category),
                        "movement_velocity": round(avg_movement / 4, 1)  # Per week
                    })
        
        # Sort by average movement
        rising_categories.sort(key=lambda x: x["average_movement"], reverse=True)
        
        # Keep top 3
        return rising_categories[:3]
    
    def _identify_declining_categories(self):
        """Identify categories with the most negative trust score movement."""
        category_movements = {}
        
        # Calculate average movement for each category
        for domain, data in self.domains.items():
            category = data.get("category", "unknown")
            
            if "weekly_trust_trend" in data and len(data["weekly_trust_trend"]) >= 4:
                # Calculate 4-week movement
                start = data["weekly_trust_trend"][-4]
                end = data["weekly_trust_trend"][-1]
                movement = end - start
                
                if category not in category_movements:
                    category_movements[category] = {"total": 0, "count": 0}
                
                category_movements[category]["total"] += movement
                category_movements[category]["count"] += 1
        
        # Calculate averages
        declining_categories = []
        for category, movements in category_movements.items():
            if movements["count"] > 0:
                avg_movement = movements["total"] / movements["count"]
                if avg_movement < 0:  # Only include categories with negative movement
                    declining_categories.append({
                        "category": category,
                        "average_movement": round(avg_movement, 1),
                        "domain_count": movements["count"],
                        "top_decliner": self._get_top_decliner(category),
                        "decline_velocity": round(abs(avg_movement) / 4, 1)  # Per week, absolute value
                    })
        
        # Sort by average movement (most negative first)
        declining_categories.sort(key=lambda x: x["average_movement"])
        
        # Keep top 3
        return declining_categories[:3]
    
    def _identify_cross_category_movers(self):
        """Identify domains that excel across multiple categories."""
        # Find domains with multiple category tags or that benchmark well against other categories
        cross_category_domains = []
        
        for domain, data in self.domains.items():
            category = data.get("category", "unknown")
            trust_score = data.get("trust_score", 0)
            
            # For this simulation, we'll create some synthetic cross-category metrics
            # In a real implementation, this would come from actual cross-category analysis
            if trust_score > 85:
                # High-scoring domains are candidates for cross-category influence
                cross_category_influence = []
                
                # Simulate influence on other categories
                for other_category in self.categories:
                    if other_category != category:
                        influence_score = random.uniform(0.3, 0.9)
                        if influence_score > 0.7:  # Only include significant influence
                            cross_category_influence.append({
                                "category": other_category,
                                "influence_score": round(influence_score, 2),
                                "strength": "Citation authority" if influence_score > 0.8 else "Methodology clarity" if influence_score > 0.75 else "Factual consistency"
                            })
                
                if cross_category_influence:
                    cross_category_domains.append({
                        "domain": domain,
                        "primary_category": category,
                        "trust_score": trust_score,
                        "cross_category_influence": cross_category_influence,
                        "insight": f"{domain} demonstrates exceptional cross-category influence, particularly in {cross_category_influence[0]['category']} where it scores {cross_category_influence[0]['influence_score']} on {cross_category_influence[0]['strength']}."
                    })
        
        # Sort by number of influenced categories, then by primary trust score
        cross_category_domains.sort(key=lambda x: (len(x["cross_category_influence"]), x["trust_score"]), reverse=True)
        
        # Keep top 5
        return cross_category_domains[:5]
    
    def _identify_volatility_leaders(self):
        """Identify domains with the highest trust volatility."""
        volatility_domains = []
        
        for domain, data in self.domains.items():
            volatility = data.get("trust_volatility", 0)
            if volatility > 0.2:  # Only include domains with significant volatility
                category = data.get("category", "unknown")
                trust_score = data.get("trust_score", 0)
                
                volatility_domains.append({
                    "domain": domain,
                    "category": category,
                    "volatility": round(volatility, 2),
                    "trust_score": trust_score,
                    "pattern": self._identify_volatility_pattern(data.get("weekly_trust_trend", [])),
                    "insight": f"{domain} shows high trust volatility ({round(volatility, 2)}), which provides insight into dynamic trust factors in the {category} space."
                })
        
        # Sort by volatility
        volatility_domains.sort(key=lambda x: x["volatility"], reverse=True)
        
        # Keep top 5
        return volatility_domains[:5]
    
    def _identify_stability_champions(self):
        """Identify domains with exceptional trust stability and high scores."""
        stability_domains = []
        
        for domain, data in self.domains.items():
            volatility = data.get("trust_volatility", 1)
            trust_score = data.get("trust_score", 0)
            
            # Look for high trust score with low volatility
            if trust_score > 85 and volatility < 0.1:
                category = data.get("category", "unknown")
                
                stability_domains.append({
                    "domain": domain,
                    "category": category,
                    "volatility": round(volatility, 2),
                    "trust_score": trust_score,
                    "stability_period": random.randint(8, 24),  # Simulated weeks of stability
                    "insight": f"{domain} maintains exceptional trust stability with a high score of {trust_score} and low volatility of {round(volatility, 2)}."
                })
        
        # Sort by trust score, then by volatility (lowest first)
        stability_domains.sort(key=lambda x: (x["trust_score"], -x["volatility"]), reverse=True)
        
        # Keep top 5
        return stability_domains[:5]
    
    def _get_elite_domains(self, category):
        """Get elite domains for a specific category."""
        elite_domains = []
        
        for domain, data in self.domains.items():
            if data.get("category", "") == category and data.get("trust_score", 0) >= 90:
                elite_domains.append(domain)
        
        return elite_domains
    
    def _get_top_performer(self, category):
        """Get the top performing domain in a category."""
        top_domain = None
        top_score = 0
        
        for domain, data in self.domains.items():
            if data.get("category", "") == category and data.get("trust_score", 0) > top_score:
                top_domain = domain
                top_score = data.get("trust_score", 0)
        
        if top_domain:
            return {
                "domain": top_domain,
                "trust_score": top_score,
                "citation_rate": self.domains[top_domain].get("citation_rate", 0)
            }
        
        return None
    
    def _get_lowest_trust_score(self, category):
        """Get the lowest trust score in a category."""
        lowest_domain = None
        lowest_score = 100
        
        for domain, data in self.domains.items():
            if data.get("category", "") == category and data.get("trust_score", 100) < lowest_score:
                lowest_domain = domain
                lowest_score = data.get("trust_score", 100)
        
        if lowest_domain:
            return {
                "domain": lowest_domain,
                "trust_score": lowest_score
            }
        
        return None
    
    def _get_most_volatile_domain(self, category):
        """Get the most volatile domain in a category."""
        most_volatile_domain = None
        highest_volatility = 0
        
        for domain, data in self.domains.items():
            if data.get("category", "") == category and data.get("trust_volatility", 0) > highest_volatility:
                most_volatile_domain = domain
                highest_volatility = data.get("trust_volatility", 0)
        
        if most_volatile_domain:
            return {
                "domain": most_volatile_domain,
                "volatility": round(highest_volatility, 2)
            }
        
        return None
    
    def _get_top_riser(self, category):
        """Get the domain with the largest positive movement in a category."""
        top_riser = None
        largest_rise = 0
        
        for domain, data in self.domains.items():
            if data.get("category", "") == category and "weekly_trust_trend" in data and len(data["weekly_trust_trend"]) >= 4:
                # Calculate 4-week movement
                start = data["weekly_trust_trend"][-4]
                end = data["weekly_trust_trend"][-1]
                movement = end - start
                
                if movement > largest_rise:
                    top_riser = domain
                    largest_rise = movement
        
        if top_riser:
            return {
                "domain": top_riser,
                "movement": round(largest_rise, 1),
                "current_score": self.domains[top_riser]["weekly_trust_trend"][-1]
            }
        
        return None
    
    def _get_top_decliner(self, category):
        """Get the domain with the largest negative movement in a category."""
        top_decliner = None
        largest_decline = 0
        
        for domain, data in self.domains.items():
            if data.get("category", "") == category and "weekly_trust_trend" in data and len(data["weekly_trust_trend"]) >= 4:
                # Calculate 4-week movement
                start = data["weekly_trust_trend"][-4]
                end = data["weekly_trust_trend"][-1]
                movement = start - end  # Reverse to get positive value for decline
                
                if movement > largest_decline:
                    top_decliner = domain
                    largest_decline = movement
        
        if top_decliner:
            return {
                "domain": top_decliner,
                "movement": round(-largest_decline, 1),  # Negative to show decline
                "current_score": self.domains[top_decliner]["weekly_trust_trend"][-1]
            }
        
        return None
    
    def _identify_volatility_pattern(self, trend):
        """Identify the volatility pattern from trend data."""
        if not trend or len(trend) < 3:
            return "insufficient data"
        
        # Calculate differences between consecutive points
        diffs = [trend[i] - trend[i-1] for i in range(1, len(trend))]
        
        # Check for alternating pattern (up-down-up or down-up-down)
        alternating = True
        for i in range(1, len(diffs)):
            if (diffs[i] > 0 and diffs[i-1] > 0) or (diffs[i] < 0 and diffs[i-1] < 0):
                alternating = False
                break
        
        if alternating:
            return "alternating"
        
        # Check for sudden spike or drop
        max_abs_diff = max(abs(d) for d in diffs)
        if max_abs_diff > 10:
            if diffs[diffs.index(max(diffs, key=abs))] > 0:
                return "sudden spike"
            else:
                return "sudden drop"
        
        # Check for consistent trend
        if all(d > 0 for d in diffs):
            return "consistent rise"
        elif all(d < 0 for d in diffs):
            return "consistent decline"
        
        # Check for recent reversal
        if len(diffs) >= 3:
            earlier_direction = sum(diffs[:-2]) > 0  # True if rising, False if falling
            recent_direction = sum(diffs[-2:]) > 0
            if earlier_direction != recent_direction:
                return "recent reversal"
        
        # Default
        return "irregular"
    
    def update_category_matrix(self):
        """Update the category matrix with fresh data."""
        logger.info("Updating category matrix...")
        
        # Refresh data from other components
        self.categories = get_categories()
        self.domains = get_domains()
        
        # Update matrix components
        self.category_matrix = {
            "best_categories": self._identify_best_categories(),
            "worst_categories": self._identify_worst_categories(),
            "rising_categories": self._identify_rising_categories(),
            "declining_categories": self._identify_declining_categories(),
            "cross_category_movers": self._identify_cross_category_movers(),
            "volatility_leaders": self._identify_volatility_leaders(),
            "stability_champions": self._identify_stability_champions(),
            "last_updated": time.time()
        }
        
        # Save updated matrix
        matrix_file = f"{MATRIX_DIR}/category_matrix.json"
        os.makedirs(os.path.dirname(matrix_file), exist_ok=True)
        with open(matrix_file, 'w') as f:
            json.dump(self.category_matrix, f, indent=2)
        
        logger.info("Category matrix updated successfully")
        
        return self.category_matrix
    
    def get_category_matrix(self):
        """Get the current category matrix."""
        return self.category_matrix
    
    def generate_special_category_insight(self):
        """Generate a special insight for an exceptional category."""
        # For this example, we'll generate an insight about the best or most volatile category
        
        if random.random() > 0.5 and self.category_matrix["best_categories"]:
            # Generate insight about best category
            category = self.category_matrix["best_categories"][0]["category"]
            
            return {
                "category": category,
                "title": f"{category.title()}: The Gold Standard for Trust Signals",
                "summary": f"The {category} category has established itself as the benchmark for trust signals, with an average score of {self.category_matrix['best_categories'][0]['average_trust_score']} across {self.category_matrix['best_categories'][0]['domain_count']} domains. What makes this category exceptional is not just high scores, but the consistency and citation patterns across its domains.",
                "insights": [
                    f"Average trust score of {self.category_matrix['best_categories'][0]['average_trust_score']} leads all categories",
                    f"{self.category_matrix['best_categories'][0]['elite_domain_count']} elite domains establish category-wide benchmarks",
                    f"{self.category_matrix['best_categories'][0]['top_performer']['domain']} sets the gold standard with {self.category_matrix['best_categories'][0]['top_performer']['trust_score']} trust score",
                    "Citation patterns show strong inter-domain reinforcement"
                ],
                "recommendation": f"Study the {category} domain ecosystem as a model for trust signal optimization across categories"
            }
        elif self.category_matrix["volatility_leaders"]:
            # Generate insight about most volatile domain/category
            domain = self.category_matrix["volatility_leaders"][0]["domain"]
            category = self.category_matrix["volatility_leaders"][0]["category"]
            
            return {
                "domain": domain,
                "category": category,
                "title": f"{domain}: When Volatility Reveals Trust Signal Mechanics",
                "summary": f"{domain} demonstrates a {self.category_matrix['volatility_leaders'][0]['pattern']} volatility pattern with a score of {self.category_matrix['volatility_leaders'][0]['volatility']}, providing unique insights into how trust signals respond to external factors in the {category} category. This volatility creates a natural experiment in trust signal dynamics.",
                "insights": [
                    f"Volatility of {self.category_matrix['volatility_leaders'][0]['volatility']} reveals trust signal sensitivity",
                    f"{self.category_matrix['volatility_leaders'][0]['pattern']} pattern indicates systematic rather than random variance",
                    f"Current trust score of {self.category_matrix['volatility_leaders'][0]['trust_score']} shows baseline potential",
                    "Volatility creates opportunities for studying trust signal recovery mechanisms"
                ],
                "recommendation": f"Implement special monitoring protocol for {domain} to extract maximum insight from trust signal patterns"
            }
        else:
            # Fallback insight
            return {
                "title": "Category Matrix Analysis Reveals Trust Signal Patterns",
                "summary": "Analysis of category-level trust signals shows distinct patterns across verticals, with specialized domain ecosystems developing unique trust characteristics. These patterns provide opportunities for cross-category learning and benchmark development.",
                "insights": [
                    "Category differences reveal domain-specific trust mechanics",
                    "Elite domains demonstrate cross-category influence",
                    "Volatility patterns provide natural experiments in trust recovery",
                    "Stability champions create category benchmarks"
                ],
                "recommendation": "Develop category-specific trust signal monitoring to capture unique vertical dynamics"
            }

# Global category matrix instance
_category_matrix = None

def start_category_matrix():
    """Start the category matrix analyzer."""
    global _category_matrix
    
    if _category_matrix is None:
        _category_matrix = CategoryMatrix()
    
    return _category_matrix

def get_category_matrix():
    """Get the current category matrix."""
    global _category_matrix
    
    if _category_matrix is None:
        _category_matrix = start_category_matrix()
    
    return _category_matrix.get_category_matrix()

def update_category_matrix():
    """Update the category matrix with fresh data."""
    global _category_matrix
    
    if _category_matrix is None:
        _category_matrix = start_category_matrix()
    
    return _category_matrix.update_category_matrix()

def generate_special_category_insight():
    """Generate a special insight for an exceptional category."""
    global _category_matrix
    
    if _category_matrix is None:
        _category_matrix = start_category_matrix()
    
    return _category_matrix.generate_special_category_insight()

# Main execution for testing
if __name__ == "__main__":
    logger.info("Starting category matrix analysis...")
    
    # Start matrix analyzer
    matrix = start_category_matrix()
    
    # Update matrix
    updated_matrix = matrix.update_category_matrix()
    
    # Generate special insight
    insight = matrix.generate_special_category_insight()
    
    if insight:
        logger.info(f"Generated special insight: {insight['title']}")
    
    logger.info("Category matrix analysis complete")