"""
MISS Score Calculator

This module calculates the Model Influence Signal Score (MISS), which quantifies 
an entity's influence inside large language models (LLMs).

Formula:
MISS = Σ (Model Weight × Citation Confidence × Contextual Relevance × SIGNAL Score)

Components:
- Model Weight: Reflects the trust or user exposure of a given LLM
- Citation Confidence: How assertively an LLM refers to a brand or domain
- Contextual Relevance: Whether the mention occurs in the right context
- SIGNAL Score: How well a webpage emits machine-digestible semantic structure
"""

import os
import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple, Set
import random

# Import local modules
import domain_memory_tracker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MISSScoreCalculator:
    """
    Calculator for the Model Influence Signal Score (MISS).
    """
    
    def __init__(self):
        """Initialize the MISS Score calculator."""
        self.model_weights = {
            "gpt-4o": 0.95,      # Highest weight - widely used, trusted
            "claude-3-opus": 0.90,  # Very high quality
            "gemini-pro": 0.85,   # Good quality but less market share
            "llama-3": 0.80,      # Open source alternative
            "mixtral": 0.75,      # Open source but less refined
            # Add other models as needed
        }
        
        # Default SIGNAL scores by domain category
        self.default_signal_scores = {
            "Technology": 0.85,
            "Finance": 0.80,
            "Healthcare": 0.75,
            "Education": 0.82,
            "Entertainment": 0.78,
            "Travel": 0.76,
            "Food": 0.74,
            "Sports": 0.72,
            "News": 0.85,
            "Shopping": 0.70,
            "Social Media": 0.88,
            # Add other categories as needed
        }
        
        # Load data if available
        self.score_history = self._load_score_history()
    
    def _load_score_history(self) -> Dict:
        """
        Load score history from file.
        
        Returns:
            Dictionary with score history
        """
        history_path = "data/miss_scores/history.json"
        
        try:
            # Create directory if it doesn't exist
            os.makedirs("data/miss_scores", exist_ok=True)
            
            if os.path.exists(history_path):
                with open(history_path, "r") as f:
                    return json.load(f)
            else:
                # Initialize empty history
                return {
                    "domains": {},
                    "last_updated": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error loading score history: {e}")
            return {
                "domains": {},
                "last_updated": datetime.now().isoformat()
            }
    
    def _save_score_history(self) -> None:
        """Save score history to file."""
        history_path = "data/miss_scores/history.json"
        
        try:
            # Update last updated timestamp
            self.score_history["last_updated"] = datetime.now().isoformat()
            
            # Create directory if it doesn't exist
            os.makedirs("data/miss_scores", exist_ok=True)
            
            with open(history_path, "w") as f:
                json.dump(self.score_history, f, indent=2)
                
            logger.info("Score history saved successfully")
        except Exception as e:
            logger.error(f"Error saving score history: {e}")
    
    def calculate_citation_confidence(self, domain: str, model: str, 
                                    ranks: List[int]) -> float:
        """
        Calculate citation confidence based on domain ranks.
        
        Args:
            domain: Domain name
            model: Model name
            ranks: List of ranks for the domain
            
        Returns:
            Citation confidence score (0-1)
        """
        if not ranks:
            return 0.0
        
        # Average rank
        avg_rank = sum(ranks) / len(ranks)
        
        # Normalize rank to 0-1 (lower rank is better)
        # Assuming ranks range from 1 to 20
        normalized_rank = max(0, min(1, 1 - (avg_rank - 1) / 19))
        
        # Frequency of appearance
        frequency = min(1.0, len(ranks) / 10)  # Cap at 10 appearances
        
        # Consistency (lower standard deviation is better)
        if len(ranks) > 1:
            std_dev = math.sqrt(sum((r - avg_rank) ** 2 for r in ranks) / len(ranks))
            consistency = max(0, min(1, 1 - std_dev / 10))  # Assuming std_dev range 0-10
        else:
            consistency = 0.5  # Neutral consistency for single data point
        
        # Calculate overall citation confidence
        # Weight factors based on importance
        confidence = (
            normalized_rank * 0.5 +  # Rank is most important
            frequency * 0.3 +        # Frequency is next
            consistency * 0.2        # Consistency is least important
        )
        
        return confidence
    
    def calculate_contextual_relevance(self, domain: str, model: str, 
                                     category: str) -> float:
        """
        Calculate contextual relevance score.
        
        Args:
            domain: Domain name
            model: Model name
            category: Query category
            
        Returns:
            Contextual relevance score (0-1)
        """
        # In a production system, we would check if the domain is mentioned in the
        # right context (e.g., a tech company in tech discussions)
        # Here we'll use a simplified approach based on domain TLD and category
        
        # Extract TLD
        tld = domain.split(".")[-1].lower()
        
        # Domain-category match bonuses
        domain_category_matches = {
            # Tech domains
            "techcrunch.com": {"Technology": 1.0, "News": 0.8},
            "wired.com": {"Technology": 1.0, "News": 0.8},
            "theverge.com": {"Technology": 1.0, "Entertainment": 0.7},
            
            # Finance domains
            "bloomberg.com": {"Finance": 1.0, "News": 0.8},
            "wsj.com": {"Finance": 1.0, "News": 0.9},
            
            # News domains
            "nytimes.com": {"News": 1.0, "Politics": 0.9},
            "bbc.com": {"News": 1.0, "Entertainment": 0.7},
            
            # Education domains
            "khanacademy.org": {"Education": 1.0},
            "coursera.org": {"Education": 1.0},
            
            # Add more domain-category matches as needed
        }
        
        # Check if we have a predefined match
        if domain in domain_category_matches and category in domain_category_matches[domain]:
            return domain_category_matches[domain][category]
        
        # TLD-based heuristics
        tld_relevance = {
            "edu": {"Education": 0.9, "Research": 0.8},
            "gov": {"Government": 0.9, "Politics": 0.7},
            "org": {"Education": 0.6, "Healthcare": 0.6, "News": 0.5},
            "io": {"Technology": 0.7},
            # Add more TLD-category matches as needed
        }
        
        # Check TLD relevance
        if tld in tld_relevance and category in tld_relevance[tld]:
            return tld_relevance[tld][category]
        
        # Default: moderate relevance
        return 0.6
    
    def calculate_signal_score(self, domain: str, category: str) -> float:
        """
        Calculate SIGNAL score (Semantic Inference Grounding and Language).
        
        Args:
            domain: Domain name
            category: Domain category
            
        Returns:
            SIGNAL score (0-1)
        """
        # In a production system, we would scrape the domain and analyze its content
        # Here we'll use predefined scores based on domain category
        
        # Check if we have a custom signal score for this domain
        domain_signal_scores = {
            # Tech sites often have good structure
            "techcrunch.com": 0.88,
            "wired.com": 0.86,
            "arstechnica.com": 0.87,
            
            # News sites vary in quality
            "nytimes.com": 0.85,
            "wsj.com": 0.84,
            "bbc.com": 0.86,
            
            # Add more domain-specific scores as needed
        }
        
        if domain in domain_signal_scores:
            return domain_signal_scores[domain]
        
        # Use category default with small random variation
        if category in self.default_signal_scores:
            base_score = self.default_signal_scores[category]
            # Add small random variation (-0.05 to +0.05)
            variation = random.uniform(-0.05, 0.05)
            return max(0, min(1, base_score + variation))
        
        # Default score
        return 0.7
    
    def calculate_miss_score(self, domain: str, models: Optional[List[str]] = None, 
                           categories: Optional[List[str]] = None) -> Dict:
        """
        Calculate the MISS score for a domain.
        
        Formula: MISS = Σ (Model Weight × Citation Confidence × Contextual Relevance × SIGNAL Score)
        
        Args:
            domain: Domain name
            models: Optional list of models to include
            categories: Optional list of categories to include
            
        Returns:
            Dictionary with MISS score and components
        """
        # Default models and categories if not provided
        if not models:
            models = list(self.model_weights.keys())
        
        if not categories:
            categories = list(self.default_signal_scores.keys())
        
        # Filter models to those we have weights for
        models = [m for m in models if m in self.model_weights]
        
        # Initialize scores
        total_score = 0.0
        total_weight = 0.0
        components = []
        
        # Get domain ranks from memory tracker
        for model in models:
            model_weight = self.model_weights[model]
            
            for category in categories:
                # Get ranks for this domain, model and category
                ranks = []
                
                try:
                    rank_history = domain_memory_tracker.get_rank_history(domain, model, category)
                    ranks = [entry["rank"] for entry in rank_history if "rank" in entry]
                except Exception as e:
                    logger.warning(f"Error getting rank history for {domain}/{model}/{category}: {e}")
                
                # Skip if no ranks found
                if not ranks:
                    continue
                
                # Calculate component scores
                citation_confidence = self.calculate_citation_confidence(domain, model, ranks)
                contextual_relevance = self.calculate_contextual_relevance(domain, model, category)
                signal_score = self.calculate_signal_score(domain, category)
                
                # Calculate component score
                component_score = model_weight * citation_confidence * contextual_relevance * signal_score
                
                # Add to total
                total_score += component_score
                total_weight += model_weight
                
                # Record component details
                components.append({
                    "model": model,
                    "category": category,
                    "model_weight": model_weight,
                    "citation_confidence": citation_confidence,
                    "contextual_relevance": contextual_relevance,
                    "signal_score": signal_score,
                    "component_score": component_score
                })
        
        # Calculate final MISS score (normalized to 0-100)
        # If no data found, return 0
        if total_weight == 0:
            miss_score = 0
        else:
            # Normalize to 0-100 scale
            miss_score = round((total_score / total_weight) * 100)
        
        # Create result
        result = {
            "domain": domain,
            "miss_score": miss_score,
            "components": components,
            "timestamp": datetime.now().isoformat(),
            "models_included": models,
            "categories_included": categories
        }
        
        # Update score history
        self._update_score_history(domain, result)
        
        return result
    
    def _update_score_history(self, domain: str, result: Dict) -> None:
        """
        Update score history for a domain.
        
        Args:
            domain: Domain name
            result: Score result dictionary
        """
        # Initialize domain history if needed
        if domain not in self.score_history["domains"]:
            self.score_history["domains"][domain] = {
                "weekly_scores": [],
                "components": []
            }
        
        # Add to weekly scores
        weekly_entry = {
            "timestamp": result["timestamp"],
            "miss_score": result["miss_score"]
        }
        
        # Keep only last 52 weeks (approximately 1 year)
        self.score_history["domains"][domain]["weekly_scores"].append(weekly_entry)
        if len(self.score_history["domains"][domain]["weekly_scores"]) > 52:
            self.score_history["domains"][domain]["weekly_scores"] = \
                self.score_history["domains"][domain]["weekly_scores"][-52:]
        
        # Update components (overwrite with latest)
        self.score_history["domains"][domain]["components"] = result["components"]
        
        # Save score history
        self._save_score_history()
    
    def get_score_history(self, domain: str, weeks: int = 12) -> Dict:
        """
        Get score history for a domain.
        
        Args:
            domain: Domain name
            weeks: Number of weeks of history to return
            
        Returns:
            Dictionary with score history
        """
        if domain not in self.score_history["domains"]:
            return {
                "domain": domain,
                "weekly_scores": [],
                "components": []
            }
        
        domain_history = self.score_history["domains"][domain]
        
        # Limit to requested weeks
        weekly_scores = domain_history["weekly_scores"][-weeks:]
        
        return {
            "domain": domain,
            "weekly_scores": weekly_scores,
            "components": domain_history["components"]
        }
    
    def detect_score_drift(self, domain: str, threshold: float = 5.0) -> Dict:
        """
        Detect significant drift in MISS score.
        
        Args:
            domain: Domain name
            threshold: Threshold for significant drift
            
        Returns:
            Dictionary with drift information
        """
        if domain not in self.score_history["domains"]:
            return {
                "domain": domain,
                "drift_detected": False,
                "message": "No history available"
            }
        
        weekly_scores = self.score_history["domains"][domain]["weekly_scores"]
        
        if len(weekly_scores) < 2:
            return {
                "domain": domain,
                "drift_detected": False,
                "message": "Insufficient history for drift detection"
            }
        
        # Get current and previous scores
        current_score = weekly_scores[-1]["miss_score"]
        previous_score = weekly_scores[-2]["miss_score"]
        
        # Calculate drift
        drift = current_score - previous_score
        drift_pct = (drift / previous_score * 100) if previous_score > 0 else 0
        
        # Check if drift exceeds threshold
        drift_detected = abs(drift) >= threshold
        
        # Determine direction
        if drift > 0:
            direction = "positive"
            message = f"Improvement detected: +{drift:.1f} points (+{drift_pct:.1f}%)"
        else:
            direction = "negative"
            message = f"Decline detected: {drift:.1f} points ({drift_pct:.1f}%)"
        
        return {
            "domain": domain,
            "drift_detected": drift_detected,
            "direction": direction if drift_detected else "stable",
            "drift": drift,
            "drift_pct": drift_pct,
            "current_score": current_score,
            "previous_score": previous_score,
            "message": message if drift_detected else "No significant drift detected",
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_all_domains(self, top_n: int = 50) -> List[Dict]:
        """
        Calculate MISS scores for top domains.
        
        Args:
            top_n: Number of top domains to include
            
        Returns:
            List of score dictionaries
        """
        # Get top domains from memory tracker
        top_domains = domain_memory_tracker.get_top_domains(limit=top_n)
        
        results = []
        
        for domain_data in top_domains:
            domain = domain_data["domain"]
            
            try:
                score = self.calculate_miss_score(domain)
                results.append(score)
            except Exception as e:
                logger.error(f"Error calculating MISS score for {domain}: {e}")
        
        return results
    
    def get_score_benchmarks(self, category: Optional[str] = None) -> Dict:
        """
        Get score benchmarks across domains.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary with benchmark information
        """
        domains = list(self.score_history["domains"].keys())
        
        if not domains:
            return {
                "average": 0,
                "median": 0,
                "top_quartile": 0,
                "bottom_quartile": 0,
                "count": 0
            }
        
        # Get latest scores
        scores = []
        
        for domain in domains:
            weekly_scores = self.score_history["domains"][domain]["weekly_scores"]
            
            if weekly_scores:
                # Check if category filter applies
                if category:
                    # Check if any component matches the category
                    components = self.score_history["domains"][domain]["components"]
                    category_match = any(
                        comp["category"] == category for comp in components
                    )
                    
                    if not category_match:
                        continue
                
                scores.append(weekly_scores[-1]["miss_score"])
        
        if not scores:
            return {
                "average": 0,
                "median": 0,
                "top_quartile": 0,
                "bottom_quartile": 0,
                "count": 0
            }
        
        # Sort scores
        sorted_scores = sorted(scores)
        
        # Calculate benchmarks
        return {
            "average": sum(scores) / len(scores),
            "median": sorted_scores[len(sorted_scores) // 2],
            "top_quartile": sorted_scores[int(len(sorted_scores) * 0.75)],
            "bottom_quartile": sorted_scores[int(len(sorted_scores) * 0.25)],
            "count": len(scores)
        }

# Singleton instance
_calculator = None

def get_calculator() -> MISSScoreCalculator:
    """
    Get the singleton instance of the MISS Score calculator.
    
    Returns:
        MISS Score calculator instance
    """
    global _calculator
    
    if _calculator is None:
        _calculator = MISSScoreCalculator()
    
    return _calculator

def calculate_miss_score(domain: str, models: Optional[List[str]] = None, 
                     categories: Optional[List[str]] = None) -> Dict:
    """
    Calculate the MISS score for a domain.
    
    Args:
        domain: Domain name
        models: Optional list of models to include
        categories: Optional list of categories to include
        
    Returns:
        Dictionary with MISS score and components
    """
    return get_calculator().calculate_miss_score(domain, models, categories)

def get_score_history(domain: str, weeks: int = 12) -> Dict:
    """
    Get score history for a domain.
    
    Args:
        domain: Domain name
        weeks: Number of weeks of history to return
        
    Returns:
        Dictionary with score history
    """
    return get_calculator().get_score_history(domain, weeks)

def detect_score_drift(domain: str, threshold: float = 5.0) -> Dict:
    """
    Detect significant drift in MISS score.
    
    Args:
        domain: Domain name
        threshold: Threshold for significant drift
        
    Returns:
        Dictionary with drift information
    """
    return get_calculator().detect_score_drift(domain, threshold)

def calculate_all_domains(top_n: int = 50) -> List[Dict]:
    """
    Calculate MISS scores for top domains.
    
    Args:
        top_n: Number of top domains to include
        
    Returns:
        List of score dictionaries
    """
    return get_calculator().calculate_all_domains(top_n)

def get_score_benchmarks(category: Optional[str] = None) -> Dict:
    """
    Get score benchmarks across domains.
    
    Args:
        category: Optional category filter
        
    Returns:
        Dictionary with benchmark information
    """
    return get_calculator().get_score_benchmarks(category)

if __name__ == "__main__":
    # Test calculation for a few domains
    test_domains = ["techcrunch.com", "wired.com", "theverge.com"]
    
    for domain in test_domains:
        score = calculate_miss_score(domain)
        print(f"\nMISS Score for {domain}: {score['miss_score']}")
        
        for component in score["components"]:
            print(f"  - {component['model']}/{component['category']}: {component['component_score']:.3f}")
            print(f"    Citation confidence: {component['citation_confidence']:.3f}")
            print(f"    Contextual relevance: {component['contextual_relevance']:.3f}")
            print(f"    SIGNAL score: {component['signal_score']:.3f}")
    
    # Test drift detection
    for domain in test_domains:
        drift = detect_score_drift(domain)
        print(f"\nDrift for {domain}: {drift['message']}")
    
    # Test benchmarks
    benchmarks = get_score_benchmarks()
    print(f"\nBenchmarks:")
    print(f"  Average: {benchmarks['average']:.1f}")
    print(f"  Median: {benchmarks['median']:.1f}")
    print(f"  Top quartile: {benchmarks['top_quartile']:.1f}")
    print(f"  Bottom quartile: {benchmarks['bottom_quartile']:.1f}")
    print(f"  Count: {benchmarks['count']}")