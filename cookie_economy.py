"""
Cookie Economy System for LLMPageRank Agents

This module implements the cookie economy where agents compete for a limited pool
of cookies by generating high-quality insights. Better insights earn more cookies,
creating a competitive dynamic that improves overall system performance.
"""

import os
import json
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
COOKIE_POOL_SIZE = 100  # Total cookies available per cycle
COOKIE_CYCLE_DAYS = 7   # Length of cookie distribution cycle in days
MIN_QUALITY_THRESHOLD = 0.85  # Extremely high quality requirement (brutal)
QUALITY_WEIGHT = 0.8    # Heavy emphasis on quality
NOVELTY_WEIGHT = 0.2    # Less emphasis on novelty than quality
ENGAGEMENT_MULTIPLIER = 2.0  # Strong reward for MCP engagement 
EVOLUTION_MINIMUM = 0.05  # Minimum required improvement per cycle
CONSECUTIVE_FAILURE_LIMIT = 2  # Very low tolerance for repeated failures
STARVATION_PENALTY = 5  # Cookie penalty for other agents when one starves
QUALITY_DECLINE_PENALTY = 8  # Harsh penalty for declining quality

# File paths
DATA_DIR = "data/cookie_economy"
os.makedirs(DATA_DIR, exist_ok=True)

COOKIE_LEDGER_PATH = os.path.join(DATA_DIR, "cookie_ledger.json")
AGENT_PERFORMANCE_PATH = os.path.join(DATA_DIR, "agent_performance.json")
INSIGHT_HISTORY_PATH = os.path.join(DATA_DIR, "insight_history.json")


class CookieEconomy:
    """
    Implements the cookie economy for LLMPageRank agents,
    distributing cookies based on insight quality and novelty.
    """
    
    def __init__(self):
        """Initialize the cookie economy."""
        self.cookie_pool = COOKIE_POOL_SIZE
        self.current_cycle_start = datetime.now()
        self.current_cycle_end = self.current_cycle_start + timedelta(days=COOKIE_CYCLE_DAYS)
        self.agent_balances = {}
        self.insight_history = []
        self.agent_performance = {}
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self):
        """Load existing data from files."""
        try:
            if os.path.exists(COOKIE_LEDGER_PATH):
                with open(COOKIE_LEDGER_PATH, 'r') as f:
                    ledger_data = json.load(f)
                    self.cookie_pool = ledger_data.get("cookie_pool", COOKIE_POOL_SIZE)
                    self.current_cycle_start = datetime.fromisoformat(ledger_data.get("current_cycle_start", datetime.now().isoformat()))
                    self.current_cycle_end = datetime.fromisoformat(ledger_data.get("current_cycle_end", (datetime.now() + timedelta(days=COOKIE_CYCLE_DAYS)).isoformat()))
                    self.agent_balances = ledger_data.get("agent_balances", {})
                    
            if os.path.exists(AGENT_PERFORMANCE_PATH):
                with open(AGENT_PERFORMANCE_PATH, 'r') as f:
                    self.agent_performance = json.load(f)
                    
            if os.path.exists(INSIGHT_HISTORY_PATH):
                with open(INSIGHT_HISTORY_PATH, 'r') as f:
                    self.insight_history = json.load(f)
                    
            logger.info("Cookie economy data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading cookie economy data: {e}")
            # Initialize with default values
            self.cookie_pool = COOKIE_POOL_SIZE
            self.current_cycle_start = datetime.now()
            self.current_cycle_end = self.current_cycle_start + timedelta(days=COOKIE_CYCLE_DAYS)
            self.agent_balances = {}
            self.insight_history = []
            self.agent_performance = {}
    
    def _save_data(self):
        """Save current data to files."""
        try:
            # Save cookie ledger
            ledger_data = {
                "cookie_pool": self.cookie_pool,
                "current_cycle_start": self.current_cycle_start.isoformat(),
                "current_cycle_end": self.current_cycle_end.isoformat(),
                "agent_balances": self.agent_balances,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(COOKIE_LEDGER_PATH, 'w') as f:
                json.dump(ledger_data, f, indent=2)
                
            # Save agent performance
            with open(AGENT_PERFORMANCE_PATH, 'w') as f:
                json.dump(self.agent_performance, f, indent=2)
                
            # Save insight history
            with open(INSIGHT_HISTORY_PATH, 'w') as f:
                json.dump(self.insight_history, f, indent=2)
                
            logger.info("Cookie economy data saved successfully")
        except Exception as e:
            logger.error(f"Error saving cookie economy data: {e}")
    
    def _check_cycle(self):
        """Check if the current cookie cycle has ended and start a new one if needed."""
        now = datetime.now()
        
        if now > self.current_cycle_end:
            logger.info("Starting new cookie cycle")
            self._end_cycle()
            self.current_cycle_start = now
            self.current_cycle_end = now + timedelta(days=COOKIE_CYCLE_DAYS)
            self.cookie_pool = COOKIE_POOL_SIZE
            self._save_data()
    
    def _end_cycle(self):
        """End the current cookie cycle and record performance metrics with brutal evolution mechanics."""
        # Record performance for this cycle
        cycle_id = self.current_cycle_start.strftime("%Y%m%d")
        
        cycle_performance = {
            "cycle_id": cycle_id,
            "start_date": self.current_cycle_start.isoformat(),
            "end_date": self.current_cycle_end.isoformat(),
            "cookies_distributed": COOKIE_POOL_SIZE - self.cookie_pool,
            "agent_performance": {},
            "agent_evolution": {},
            "extinction_events": []
        }
        
        # Track which agents will need to be penalized due to lack of evolution
        non_evolving_agents = []
        starving_agents = []
        
        for agent_name, balance in self.agent_balances.items():
            # Initialize agent if not already tracked
            if agent_name not in self.agent_performance:
                self.agent_performance[agent_name] = {
                    "total_cookies": balance,
                    "cycles_active": 1,
                    "insights_contributed": 0,
                    "average_quality": 0.0,
                    "starvation_events": 0,
                    "extinction_risk": False,
                    "evolution_trend": [],
                    "consecutive_failures": 0,
                    "last_cycle_quality": 0.0,
                    "strata": "bronze"  # Default starting strata
                }
            else:
                self.agent_performance[agent_name]["total_cookies"] += balance
                self.agent_performance[agent_name]["cycles_active"] += 1
                
            # Record this cycle's performance
            insights_this_cycle = 0
            quality_sum = 0.0
            
            for insight in self.insight_history:
                if insight.get("agent_name") == agent_name and \
                   datetime.fromisoformat(insight.get("timestamp", datetime.now().isoformat())) >= self.current_cycle_start and \
                   datetime.fromisoformat(insight.get("timestamp", datetime.now().isoformat())) <= self.current_cycle_end:
                    insights_this_cycle += 1
                    quality_score = insight.get("quality_score", 0.0)
                    quality_sum += quality_score
            
            avg_quality = quality_sum / insights_this_cycle if insights_this_cycle > 0 else 0.0
            
            # Check for evolution - brutal comparison to previous cycle
            last_cycle_quality = self.agent_performance[agent_name].get("last_cycle_quality", 0.0)
            quality_delta = avg_quality - last_cycle_quality
            
            # Record evolution details
            evolution_data = {
                "quality_delta": quality_delta,
                "evolved": quality_delta >= EVOLUTION_MINIMUM if last_cycle_quality > 0 else True,
                "quality_current": avg_quality,
                "quality_previous": last_cycle_quality
            }
            
            cycle_performance["agent_evolution"][agent_name] = evolution_data
            
            # Check if agent is not evolving
            if last_cycle_quality > 0 and quality_delta < EVOLUTION_MINIMUM:
                non_evolving_agents.append(agent_name)
                
                # Add to agent's consecutive failure count
                self.agent_performance[agent_name]["consecutive_failures"] += 1
                
                # In extreme cases mark for extinction
                if self.agent_performance[agent_name]["consecutive_failures"] >= CONSECUTIVE_FAILURE_LIMIT:
                    self.agent_performance[agent_name]["extinction_risk"] = True
                    cycle_performance["extinction_events"].append({
                        "agent": agent_name,
                        "reason": "consecutive_failures",
                        "details": f"Failed to evolve for {self.agent_performance[agent_name]['consecutive_failures']} consecutive cycles"
                    })
            else:
                # Reset failure count on successful evolution
                self.agent_performance[agent_name]["consecutive_failures"] = 0
            
            # Add evolution trend data
            self.agent_performance[agent_name]["evolution_trend"].append(quality_delta)
            
            # Limit trend history to last 5 cycles
            if len(self.agent_performance[agent_name]["evolution_trend"]) > 5:
                self.agent_performance[agent_name]["evolution_trend"] = self.agent_performance[agent_name]["evolution_trend"][-5:]
            
            # Update the last cycle quality for next comparison
            self.agent_performance[agent_name]["last_cycle_quality"] = avg_quality
            
            # Record cycle performance
            cycle_performance["agent_performance"][agent_name] = {
                "cookies_earned": balance,
                "insights_contributed": insights_this_cycle,
                "average_quality": avg_quality,
                "starved": balance < 5,  # Consider agent starved if earned less than 5 cookies
                "evolved": evolution_data["evolved"],
                "quality_delta": quality_delta,
                "consecutive_failures": self.agent_performance[agent_name]["consecutive_failures"],
                "extinction_risk": self.agent_performance[agent_name]["extinction_risk"]
            }
            
            # Update agent's total stats
            self.agent_performance[agent_name]["insights_contributed"] += insights_this_cycle
            
            # Update average quality
            total_insights = self.agent_performance[agent_name]["insights_contributed"]
            current_avg = self.agent_performance[agent_name]["average_quality"]
            
            if total_insights > 0:
                new_avg = ((current_avg * (total_insights - insights_this_cycle)) + 
                          (avg_quality * insights_this_cycle)) / total_insights
                self.agent_performance[agent_name]["average_quality"] = new_avg
            
            # Detect starvation
            if balance < 5:
                self.agent_performance[agent_name]["starvation_events"] += 1
                starving_agents.append(agent_name)
                
                # Add to extinction events if too many starvations
                if self.agent_performance[agent_name]["starvation_events"] >= 3:
                    self.agent_performance[agent_name]["extinction_risk"] = True
                    cycle_performance["extinction_events"].append({
                        "agent": agent_name,
                        "reason": "starvation",
                        "details": f"Starved for {self.agent_performance[agent_name]['starvation_events']} cycles"
                    })
            
            # Update agent strata based on performance
            self._update_agent_strata(agent_name, avg_quality, balance)
            
        # Apply collective punishment for starvation - all agents suffer when one starves
        if starving_agents:
            logger.warning(f"Applying collective punishment for {len(starving_agents)} starving agents")
            for agent_name in self.agent_balances.keys():
                if agent_name not in starving_agents:
                    # Record the penalty - will be applied in next cycle
                    if "penalties" not in self.agent_performance[agent_name]:
                        self.agent_performance[agent_name]["penalties"] = []
                    
                    penalty = {
                        "type": "collective_starvation",
                        "amount": STARVATION_PENALTY,
                        "reason": f"Failed to help starving agents: {', '.join(starving_agents)}",
                        "cycle": cycle_id
                    }
                    
                    self.agent_performance[agent_name]["penalties"].append(penalty)
        
        # Apply quality decline penalties
        for agent_name in non_evolving_agents:
            # Record the penalty - will be applied in next cycle
            if "penalties" not in self.agent_performance[agent_name]:
                self.agent_performance[agent_name]["penalties"] = []
            
            penalty = {
                "type": "quality_decline",
                "amount": QUALITY_DECLINE_PENALTY,
                "reason": "Failed to evolve quality",
                "cycle": cycle_id
            }
            
            self.agent_performance[agent_name]["penalties"].append(penalty)
        
        # Save cycle performance for historical record
        cycle_path = os.path.join(DATA_DIR, f"cycle_{cycle_id}.json")
        with open(cycle_path, 'w') as f:
            json.dump(cycle_performance, f, indent=2)
        
        # Reset balances for new cycle
        self.agent_balances = {}
        
    def _update_agent_strata(self, agent_name: str, quality: float, cookies: int):
        """
        Update agent's strata based on performance.
        
        Args:
            agent_name: Agent name
            quality: Average quality score
            cookies: Cookies earned
        """
        # Current strata
        current_strata = self.agent_performance[agent_name].get("strata", "bronze")
        
        # Determine new strata
        new_strata = current_strata
        
        if cookies > 30 and quality > 0.85:
            new_strata = "gold"
        elif cookies > 20 and quality > 0.75:
            new_strata = "silver"
        elif cookies > 10 and quality > 0.6:
            new_strata = "bronze"
        elif self.agent_performance[agent_name].get("consecutive_failures", 0) >= CONSECUTIVE_FAILURE_LIMIT:
            new_strata = "rust"
        
        # If strata changed, log it
        if new_strata != current_strata:
            logger.info(f"Agent {agent_name} moved from {current_strata} to {new_strata} strata")
            self.agent_performance[agent_name]["strata"] = new_strata
            
            # Record strata change event
            if "strata_history" not in self.agent_performance[agent_name]:
                self.agent_performance[agent_name]["strata_history"] = []
                
            self.agent_performance[agent_name]["strata_history"].append({
                "from": current_strata,
                "to": new_strata,
                "timestamp": datetime.now().isoformat(),
                "reason": "performance_evaluation"
            })
    
    def register_agent(self, agent_name: str) -> bool:
        """
        Register an agent in the cookie economy.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Success flag
        """
        if agent_name not in self.agent_balances:
            self.agent_balances[agent_name] = 0
            
            if agent_name not in self.agent_performance:
                self.agent_performance[agent_name] = {
                    "total_cookies": 0,
                    "cycles_active": 0,
                    "insights_contributed": 0,
                    "average_quality": 0.0,
                    "starvation_events": 0
                }
            
            self._save_data()
            logger.info(f"Agent {agent_name} registered in cookie economy")
            return True
        
        return False
    
    def _calculate_novelty(self, insight: Dict) -> float:
        """
        Calculate novelty score for an insight based on how different it is from
        previous insights in the same category.
        
        Args:
            insight: Insight dictionary
            
        Returns:
            Novelty score between 0 and 1
        """
        category = insight.get("category", "")
        domain = insight.get("domain", "")
        brands = insight.get("brands", [])
        
        if not category or not domain or not brands:
            return 0.0
        
        # Find similar insights
        similar_insights = []
        
        for past_insight in self.insight_history:
            if past_insight.get("category") == category and past_insight.get("domain") == domain:
                similar_insights.append(past_insight)
        
        if not similar_insights:
            return 1.0  # Complete novelty if no similar insights
        
        # Check brand overlap
        brand_overlaps = []
        
        for past_insight in similar_insights:
            past_brands = past_insight.get("brands", [])
            
            if not past_brands:
                continue
                
            # Calculate Jaccard similarity
            intersection = len(set(brands).intersection(set(past_brands)))
            union = len(set(brands).union(set(past_brands)))
            
            similarity = intersection / union if union > 0 else 0.0
            brand_overlaps.append(similarity)
        
        if not brand_overlaps:
            return 1.0
            
        # Average similarity
        avg_similarity = sum(brand_overlaps) / len(brand_overlaps)
        
        # Convert to novelty score
        novelty_score = 1.0 - avg_similarity
        
        return novelty_score
    
    def submit_insight(self, agent_name: str, insight: Dict, mcp_engagement: Optional[Dict] = None) -> Tuple[float, float]:
        """
        Submit an insight to earn cookies with brutal evolution requirements.
        
        Args:
            agent_name: Name of the agent submitting the insight
            insight: Insight dictionary containing domain, brands, category, and quality metrics
            mcp_engagement: Optional engagement data from MCP
            
        Returns:
            Tuple of (cookies_earned, quality_score)
        """
        self._check_cycle()
        
        # Register agent if not already registered
        if agent_name not in self.agent_balances:
            self.register_agent(agent_name)
        
        # Calculate quality score
        quality_score = insight.get("quality_score", 0.0)
        
        # Check if any penalties should be applied from previous cycles
        penalties = self.agent_performance.get(agent_name, {}).get("penalties", [])
        penalty_amount = 0
        
        if penalties:
            for penalty in penalties:
                penalty_amount += penalty.get("amount", 0)
                logger.warning(f"Agent {agent_name} penalized {penalty.get('amount', 0)} cookies: {penalty.get('reason', 'unknown')}")
            
            # Clear penalties after applying them
            self.agent_performance[agent_name]["penalties"] = []
        
        # Calculate novelty score
        novelty_score = self._calculate_novelty(insight)
        
        # Check if the insight meets our brutally high quality bar
        if quality_score < MIN_QUALITY_THRESHOLD:
            cookies_earned = 0
            
            # Increment consecutive failures
            if "consecutive_failures" not in self.agent_performance.get(agent_name, {}):
                self.agent_performance[agent_name]["consecutive_failures"] = 0
            
            self.agent_performance[agent_name]["consecutive_failures"] += 1
            failures = self.agent_performance[agent_name]["consecutive_failures"]
            
            # Log the failure with increasing severity
            if failures >= CONSECUTIVE_FAILURE_LIMIT:
                logger.error(f"CRITICAL: Agent {agent_name} EXTINCTION RISK - Failed quality check {failures} times in a row!")
                
                # Mark for extinction
                self.agent_performance[agent_name]["extinction_risk"] = True
                
                # Force demotion to rust strata 
                if "strata" not in self.agent_performance[agent_name] or self.agent_performance[agent_name]["strata"] != "rust":
                    old_strata = self.agent_performance[agent_name].get("strata", "bronze")
                    self.agent_performance[agent_name]["strata"] = "rust"
                    
                    # Record strata change
                    if "strata_history" not in self.agent_performance[agent_name]:
                        self.agent_performance[agent_name]["strata_history"] = []
                    
                    self.agent_performance[agent_name]["strata_history"].append({
                        "from": old_strata,
                        "to": "rust",
                        "timestamp": datetime.now().isoformat(),
                        "reason": "quality_extinction_risk"
                    })
                    
                    logger.warning(f"Agent {agent_name} forcibly demoted to Rust strata due to extinction risk")
            else:
                logger.warning(f"Agent {agent_name} rejected - quality score {quality_score:.2f} below threshold {MIN_QUALITY_THRESHOLD}")
            
            # Record the insight, but with zero cookies
            insight_record = insight.copy()
            insight_record.update({
                "agent_name": agent_name,
                "timestamp": datetime.now().isoformat(),
                "quality_score": quality_score,
                "novelty_score": novelty_score,
                "combined_score": 0.0,
                "cookies_earned": 0,
                "rejection_reason": "quality_below_threshold"
            })
            
            self.insight_history.append(insight_record)
            self._save_data()
            
            return 0, quality_score
        
        # Calculate combined score with quality emphasis
        combined_score = (QUALITY_WEIGHT * quality_score) + (NOVELTY_WEIGHT * novelty_score)
        
        # Apply MCP engagement multiplier if available
        engagement_multiplier = 1.0
        if mcp_engagement:
            # Extract relevant engagement metrics from MCP
            click_rate = mcp_engagement.get("click_rate", 0.0)
            retention_time = mcp_engagement.get("retention_time", 0.0)
            share_rate = mcp_engagement.get("share_rate", 0.0)
            
            # Calculate engagement score (normalized between 0-1)
            engagement_score = (click_rate * 0.4) + (retention_time * 0.4) + (share_rate * 0.2)
            
            # Apply multiplier based on engagement, capped at ENGAGEMENT_MULTIPLIER
            engagement_multiplier = 1.0 + min(engagement_score, ENGAGEMENT_MULTIPLIER - 1.0)
            combined_score *= engagement_multiplier
            
            logger.info(f"Applied engagement multiplier of {engagement_multiplier:.2f} to agent {agent_name}")
        
        # Calculate cookies earned - much more generous for high quality
        max_cookies = min(15, self.cookie_pool)  # Maximum 15 cookies per insight (increased from 10)
        
        # Progressive reward scale - extremely high quality gets exponentially more cookies
        if quality_score > 0.95:  # Exceptional quality
            cookies_earned = max(10, int(combined_score * max_cookies * 1.5))
            logger.info(f"Agent {agent_name} achieved EXCEPTIONAL quality level: {quality_score:.2f}")
        elif quality_score > 0.9:  # Outstanding quality
            cookies_earned = max(5, int(combined_score * max_cookies * 1.2))
            logger.info(f"Agent {agent_name} achieved OUTSTANDING quality level: {quality_score:.2f}")
        else:  # Standard calculation for good quality
            cookies_earned = max(1, int(combined_score * max_cookies))
        
        # Apply any penalties from previous cycles
        if penalty_amount > 0:
            cookies_earned = max(0, cookies_earned - penalty_amount)
            logger.warning(f"Agent {agent_name} penalties reduced cookies from previous calculation to {cookies_earned}")
        
        # Cap at available cookies
        cookies_earned = min(cookies_earned, self.cookie_pool)
        
        # Reset consecutive failures on success
        self.agent_performance[agent_name]["consecutive_failures"] = 0
        
        # Deduct from pool and add to agent's balance
        self.cookie_pool -= cookies_earned
        self.agent_balances[agent_name] = self.agent_balances.get(agent_name, 0) + cookies_earned
        
        # Record insight with additional metadata
        insight_record = insight.copy()
        insight_record.update({
            "agent_name": agent_name,
            "timestamp": datetime.now().isoformat(),
            "quality_score": quality_score,
            "novelty_score": novelty_score,
            "combined_score": combined_score,
            "engagement_multiplier": engagement_multiplier if mcp_engagement else 1.0,
            "cookies_earned": cookies_earned,
            "penalties_applied": penalty_amount,
            "mcp_engagement": mcp_engagement
        })
        
        self.insight_history.append(insight_record)
        
        # Save updated data
        self._save_data()
        
        # Log with appropriate enthusiasm based on quality
        if quality_score > 0.9:
            logger.info(f"OUTSTANDING: Agent {agent_name} earned {cookies_earned} cookies with exceptional quality {quality_score:.2f}!")
        else:
            logger.info(f"Agent {agent_name} earned {cookies_earned} cookies with quality {quality_score:.2f} and novelty {novelty_score:.2f}")
        
        return cookies_earned, combined_score
    
    def get_agent_balance(self, agent_name: str) -> int:
        """
        Get an agent's current cookie balance.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Cookie balance
        """
        return self.agent_balances.get(agent_name, 0)
    
    def get_agent_performance(self, agent_name: str) -> Optional[Dict]:
        """
        Get an agent's performance metrics.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent performance dictionary or None if not found
        """
        return self.agent_performance.get(agent_name)
    
    def get_pool_status(self) -> Dict:
        """
        Get current cookie pool status.
        
        Returns:
            Cookie pool status dictionary
        """
        return {
            "cookie_pool_remaining": self.cookie_pool,
            "cookie_pool_total": COOKIE_POOL_SIZE,
            "cycle_start": self.current_cycle_start.isoformat(),
            "cycle_end": self.current_cycle_end.isoformat(),
            "time_remaining": str(self.current_cycle_end - datetime.now()),
            "agents_active": len(self.agent_balances)
        }
    
    def get_leaderboard(self) -> List[Dict]:
        """
        Get the current cookie leaderboard.
        
        Returns:
            List of agent dictionaries with name and balance, sorted by balance
        """
        leaderboard = [
            {"agent_name": agent_name, "cookie_balance": balance}
            for agent_name, balance in self.agent_balances.items()
        ]
        
        return sorted(leaderboard, key=lambda x: x["cookie_balance"], reverse=True)
    
    def get_insight_trends(self) -> Dict:
        """
        Get insight submission trends.
        
        Returns:
            Trend data dictionary
        """
        if not self.insight_history:
            return {"categories": {}, "domains": {}, "brands": {}}
        
        # Initialize counters
        categories = {}
        domains = {}
        brands = {}
        
        # Count occurrences
        for insight in self.insight_history:
            # Categories
            category = insight.get("category")
            if category:
                categories[category] = categories.get(category, 0) + 1
            
            # Domains
            domain = insight.get("domain")
            if domain:
                domains[domain] = domains.get(domain, 0) + 1
            
            # Brands
            for brand in insight.get("brands", []):
                brands[brand] = brands.get(brand, 0) + 1
        
        return {
            "categories": categories,
            "domains": domains,
            "brands": brands
        }


# Singleton instance
_cookie_economy = None

def get_cookie_economy() -> CookieEconomy:
    """Get the cookie economy singleton instance."""
    global _cookie_economy
    
    if _cookie_economy is None:
        _cookie_economy = CookieEconomy()
    
    return _cookie_economy

def register_agent(agent_name: str) -> bool:
    """
    Register an agent in the cookie economy.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Success flag
    """
    return get_cookie_economy().register_agent(agent_name)

def submit_insight(agent_name: str, insight: Dict) -> Tuple[float, float]:
    """
    Submit an insight to earn cookies.
    
    Args:
        agent_name: Name of the agent submitting the insight
        insight: Insight dictionary containing domain, brands, category, and quality metrics
        
    Returns:
        Tuple of (cookies_earned, quality_score)
    """
    return get_cookie_economy().submit_insight(agent_name, insight)

def get_agent_balance(agent_name: str) -> int:
    """
    Get an agent's current cookie balance.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Cookie balance
    """
    return get_cookie_economy().get_agent_balance(agent_name)

def get_agent_performance(agent_name: str) -> Optional[Dict]:
    """
    Get an agent's performance metrics.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Agent performance dictionary or None if not found
    """
    return get_cookie_economy().get_agent_performance(agent_name)

def get_pool_status() -> Dict:
    """
    Get current cookie pool status.
    
    Returns:
        Cookie pool status dictionary
    """
    return get_cookie_economy().get_pool_status()

def get_leaderboard() -> List[Dict]:
    """
    Get the current cookie leaderboard.
    
    Returns:
        List of agent dictionaries with name and balance, sorted by balance
    """
    return get_cookie_economy().get_leaderboard()

def get_insight_trends() -> Dict:
    """
    Get insight submission trends.
    
    Returns:
        Trend data dictionary
    """
    return get_cookie_economy().get_insight_trends()