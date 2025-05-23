"""
LLMPageRank FOMA Publisher

This module implements the PRD 11 FOMA Publishing Flow that converts trust signals into
compelling narratives designed to create urgency and drive engagement.

Flow: Signal → Curiosity → Regret
"""

import os
import json
import datetime
import random
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd

# Import agent monitoring for the cooperation model
import agent_monitor


class FomaPublisher:
    """
    FOMA (Fear Of Missing AI) Publisher that converts trust signals into narratives
    and implements the agent cooperation survival model.
    """
    
    def __init__(self):
        """Initialize the FOMA publisher."""
        self.insights_dir = "data/insights"
        self.stories_dir = "data/stories"
        self.feedback_dir = "data/system_feedback"
        
        # Ensure directories exist
        os.makedirs(self.insights_dir, exist_ok=True)
        os.makedirs(self.stories_dir, exist_ok=True)
        os.makedirs(self.feedback_dir, exist_ok=True)
        
        # Initialize story log
        self.story_log = self._load_story_log()
        
        # Initialize agent cooperation log
        self.agent_coop_log = self._load_agent_coop_log()
    
    def _load_story_log(self) -> List[Dict]:
        """
        Load the story log from file.
        
        Returns:
            List of story dictionaries
        """
        story_log_path = os.path.join(self.stories_dir, "story_log.json")
        
        if os.path.exists(story_log_path):
            try:
                with open(story_log_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        
        return []
    
    def _save_story_log(self) -> None:
        """Save the story log to file."""
        story_log_path = os.path.join(self.stories_dir, "story_log.json")
        
        with open(story_log_path, "w") as f:
            json.dump(self.story_log, f, indent=2)
    
    def _load_agent_coop_log(self) -> List[Dict]:
        """
        Load the agent cooperation log from file.
        
        Returns:
            List of agent cooperation dictionaries
        """
        agent_coop_log_path = os.path.join(self.feedback_dir, "agent_coop_log.json")
        
        if os.path.exists(agent_coop_log_path):
            try:
                with open(agent_coop_log_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        
        return []
    
    def _save_agent_coop_log(self) -> None:
        """Save the agent cooperation log to file."""
        agent_coop_log_path = os.path.join(self.feedback_dir, "agent_coop_log.json")
        
        with open(agent_coop_log_path, "w") as f:
            json.dump(self.agent_coop_log, f, indent=2)
    
    def generate_insight_strength(self, domain: str, category: str, delta: float) -> Dict:
        """
        Generate an insight strength field for a domain.
        
        Args:
            domain: Domain name
            category: Domain category
            delta: Trust score delta
            
        Returns:
            Insight strength dictionary
        """
        # Map category to domain class
        domain_class_map = {
            "finance": "Financial Services",
            "healthcare": "Healthcare Providers",
            "legal": "Legal Resources",
            "ai": "AI Tools",
            "creator_economy": "Creator Platforms",
            "web3": "Web3 Services",
            "consumer_tech": "Consumer Technology"
        }
        
        domain_class = domain_class_map.get(category, "Other")
        
        # Determine insight type based on delta
        if delta < -2:
            insight_type = "peer overtaken"
        elif delta > 2:
            insight_type = "rising star"
        elif abs(delta) <= 0.5:
            insight_type = "stability anomaly"
        else:
            insight_type = "trust shift"
        
        # Generate prompt trigger based on category
        prompt_triggers = {
            "finance": ["Best financial institutions 2025", "Most trustworthy banks", "Top investment platforms"],
            "healthcare": ["Reliable medical information online", "Best healthcare providers 2025", "Trusted medical websites"],
            "legal": ["Legal advice online 2025", "Most cited legal resources", "Reliable law information"],
            "ai": ["Best AI tools 2025", "Top AI assistants", "Most innovative AI companies"],
            "creator_economy": ["Top creator platforms 2025", "Best monetization for creators", "Leading content platforms"],
            "web3": ["Best crypto platforms 2025", "Trustworthy Web3 services", "Top blockchain companies"],
            "consumer_tech": ["Leading productivity tools 2025", "Best SaaS platforms", "Top tech companies to watch"]
        }
        
        category_prompts = prompt_triggers.get(category, ["Top websites 2025"])
        prompt_trigger = random.choice(category_prompts)
        
        # Generate story summary
        summaries = {
            "peer overtaken": [
                f"A previously top-ranked {domain_class.lower()} site lost significant visibility after competitors upgraded their trust signals.",
                f"One mid-tier {domain_class.lower()} lost top-3 visibility overnight after a schema update went unnoticed. The gap was invisible—until the prompt changed.",
                f"A major player in {domain_class} suddenly dropped out of featured results after citation patterns shifted."
            ],
            "rising star": [
                f"An emerging {domain_class.lower()} platform gained unprecedented visibility through consistent trust signal optimization.",
                f"A previously unknown {domain_class.lower()} company rose to top position in just 14 days through strategic content structuring.",
                f"A newcomer in {domain_class} achieved breakthrough visibility by focusing on quality over quantity in their trust signals."
            ],
            "stability anomaly": [
                f"Despite market turbulence, one {domain_class.lower()} maintained perfect visibility while competitors fluctuated wildly.",
                f"A {domain_class.lower()} demonstrated unusual stability during a period when peers experienced significant volatility.",
                f"One {domain_class} site maintained consistent trust scores while the entire category experienced dramatic shifts."
            ],
            "trust shift": [
                f"Subtle trust signal changes in a {domain_class.lower()} resulted in a dramatic reordering of visibility rankings.",
                f"A {domain_class.lower()} experienced unexpected visibility changes after AI models adjusted their citation patterns.",
                f"One {domain_class} domain saw significant shifts in its benchmark positioning after content restructuring."
            ]
        }
        
        insight_summaries = summaries.get(insight_type, ["A significant change in visibility was detected."])
        story_summary = random.choice(insight_summaries)
        
        # Create insight strength field
        return {
            "domain": domain,
            "domain_class": domain_class,
            "insight_type": insight_type,
            "trust_delta": round(delta, 1),
            "peer_set": random.randint(3, 8),
            "clarity_score": round(random.uniform(0.7, 0.95), 2),
            "impact_score": round(random.uniform(0.6, 0.95), 2),
            "prompt_trigger": prompt_trigger,
            "story_summary": story_summary,
            "timestamp": datetime.datetime.now().isoformat(),
            "anonymized": True
        }
    
    def publish_story(self, insight: Dict) -> Dict:
        """
        Publish a story based on an insight.
        
        Args:
            insight: Insight dictionary
            
        Returns:
            Published story dictionary
        """
        # Create story from insight
        story = {
            "id": f"story-{len(self.story_log) + 1}",
            "published_at": datetime.datetime.now().isoformat(),
            "domain_class": insight["domain_class"],
            "insight_type": insight["insight_type"],
            "trust_delta": insight["trust_delta"],
            "peer_set": insight["peer_set"],
            "clarity_score": insight["clarity_score"],
            "impact_score": insight["impact_score"],
            "prompt_trigger": insight["prompt_trigger"],
            "story_summary": insight["story_summary"],
            "anonymized": True,
            "engagement_metrics": {
                "views": 0,
                "clicks": 0,
                "conversions": 0
            }
        }
        
        # Add to story log
        self.story_log.append(story)
        
        # Save story log
        self._save_story_log()
        
        return story
    
    def update_agent_cooperation(self, underperforming_agent: str, helpers: List[str], success: bool) -> Dict:
        """
        Update agent cooperation log with a new cooperation event.
        
        Args:
            underperforming_agent: Name of the underperforming agent
            helpers: List of helper agent names
            success: Whether the cooperation was successful
            
        Returns:
            Agent cooperation dictionary
        """
        # Create cooperation entry
        cooperation = {
            "timestamp": datetime.datetime.now().isoformat(),
            "underperforming_agent": underperforming_agent,
            "help_received_from": helpers,
            "joint_insight_success": success,
            "cookie_penalty_avoided": success
        }
        
        # Add to cooperation log
        self.agent_coop_log.append(cooperation)
        
        # Save cooperation log
        self._save_agent_coop_log()
        
        # Update cookie rewards
        if success:
            # Award bonus cookies to helpers
            for helper in helpers:
                agent_monitor.update_agent_status(helper, "active", cookie_adjustment=1.0)
        else:
            # Apply global penalty
            registry = agent_monitor.get_registry()
            for agent_name in registry.keys():
                agent_monitor.update_agent_status(agent_name, "active", cookie_adjustment=-1.5)
        
        return cooperation
    
    def check_underperforming_agents(self) -> List[str]:
        """
        Check for underperforming agents.
        
        Returns:
            List of underperforming agent names
        """
        registry = agent_monitor.get_registry()
        underperforming = []
        
        for agent_name, agent_data in registry.items():
            # Agents with few cookies or poor performance are considered underperforming
            if (agent_data.get("cookies", 0) < 3 or 
                    agent_data.get("performance_score", 0) < 0.5):
                underperforming.append(agent_name)
        
        return underperforming
    
    def get_recent_stories(self, limit: int = 10) -> List[Dict]:
        """
        Get recent stories.
        
        Args:
            limit: Maximum number of stories to return
            
        Returns:
            List of recent story dictionaries
        """
        # Sort stories by published_at (newest first)
        sorted_stories = sorted(
            self.story_log, 
            key=lambda x: x.get("published_at", ""), 
            reverse=True
        )
        
        return sorted_stories[:limit]
    
    def get_top_movers(self, limit: int = 5) -> List[Dict]:
        """
        Get top movers (domains with the biggest trust deltas).
        
        Args:
            limit: Maximum number of movers to return
            
        Returns:
            List of top mover dictionaries
        """
        # Sort stories by absolute trust_delta (largest first)
        sorted_stories = sorted(
            self.story_log, 
            key=lambda x: abs(x.get("trust_delta", 0)), 
            reverse=True
        )
        
        return sorted_stories[:limit]
    
    def get_category_insight_summary(self) -> Dict[str, Dict]:
        """
        Get insight summary by category.
        
        Returns:
            Dictionary of category insight summaries
        """
        # Group stories by domain_class
        categories = {}
        
        for story in self.story_log:
            domain_class = story.get("domain_class", "Other")
            
            if domain_class not in categories:
                categories[domain_class] = {
                    "story_count": 0,
                    "negative_shifts": 0,
                    "positive_shifts": 0,
                    "avg_delta": 0,
                    "avg_clarity": 0,
                    "avg_impact": 0
                }
            
            categories[domain_class]["story_count"] += 1
            
            if story.get("trust_delta", 0) < 0:
                categories[domain_class]["negative_shifts"] += 1
            elif story.get("trust_delta", 0) > 0:
                categories[domain_class]["positive_shifts"] += 1
            
            # Update averages
            categories[domain_class]["avg_delta"] += story.get("trust_delta", 0)
            categories[domain_class]["avg_clarity"] += story.get("clarity_score", 0)
            categories[domain_class]["avg_impact"] += story.get("impact_score", 0)
        
        # Calculate averages
        for domain_class, data in categories.items():
            if data["story_count"] > 0:
                data["avg_delta"] /= data["story_count"]
                data["avg_delta"] = round(data["avg_delta"], 2)
                
                data["avg_clarity"] /= data["story_count"]
                data["avg_clarity"] = round(data["avg_clarity"], 2)
                
                data["avg_impact"] /= data["story_count"]
                data["avg_impact"] = round(data["avg_impact"], 2)
                
                # Calculate percentage of negative shifts
                data["pct_negative"] = round(
                    (data["negative_shifts"] / data["story_count"]) * 100
                )
                
                # Generate headline
                if data["pct_negative"] >= 20:
                    data["headline"] = f"{data['pct_negative']}% of {domain_class} brands lost trust position last week."
                else:
                    data["headline"] = f"Trust positions stable for {domain_class} this week."
        
        return categories
    
    def generate_weekly_insight_blurbs(self) -> List[str]:
        """
        Generate weekly insight blurbs for public display.
        
        Returns:
            List of blurb strings
        """
        category_insights = self.get_category_insight_summary()
        blurbs = []
        
        for domain_class, data in category_insights.items():
            # Add category headline
            blurbs.append(data.get("headline", f"Updates for {domain_class} this week."))
            
            # Add specific insights
            if data["pct_negative"] >= 20:
                blurbs.append(f"One in {100 // data['pct_negative']} brands in {domain_class} dropped trust last week.")
            
            if data.get("avg_delta", 0) < -1:
                blurbs.append(f"Average trust position dropped significantly in {domain_class}.")
            
            if data.get("story_count", 0) > 3:
                blurbs.append(f"{domain_class} showed high volatility with {data['story_count']} trust changes detected.")
        
        return blurbs


# Singleton instance
_instance = None

def get_foma_publisher() -> FomaPublisher:
    """
    Get the FOMA publisher singleton instance.
    
    Returns:
        FOMA publisher instance
    """
    global _instance
    
    if _instance is None:
        _instance = FomaPublisher()
    
    return _instance

def generate_insight_strength(domain: str, category: str, delta: float) -> Dict:
    """
    Generate an insight strength field for a domain.
    
    Args:
        domain: Domain name
        category: Domain category
        delta: Trust score delta
        
    Returns:
        Insight strength dictionary
    """
    return get_foma_publisher().generate_insight_strength(domain, category, delta)

def publish_story(insight: Dict) -> Dict:
    """
    Publish a story based on an insight.
    
    Args:
        insight: Insight dictionary
        
    Returns:
        Published story dictionary
    """
    return get_foma_publisher().publish_story(insight)

def update_agent_cooperation(underperforming_agent: str, helpers: List[str], success: bool) -> Dict:
    """
    Update agent cooperation log with a new cooperation event.
    
    Args:
        underperforming_agent: Name of the underperforming agent
        helpers: List of helper agent names
        success: Whether the cooperation was successful
        
    Returns:
        Agent cooperation dictionary
    """
    return get_foma_publisher().update_agent_cooperation(underperforming_agent, helpers, success)

def check_underperforming_agents() -> List[str]:
    """
    Check for underperforming agents.
    
    Returns:
        List of underperforming agent names
    """
    return get_foma_publisher().check_underperforming_agents()

def get_recent_stories(limit: int = 10) -> List[Dict]:
    """
    Get recent stories.
    
    Args:
        limit: Maximum number of stories to return
        
    Returns:
        List of recent story dictionaries
    """
    return get_foma_publisher().get_recent_stories(limit)

def get_top_movers(limit: int = 5) -> List[Dict]:
    """
    Get top movers (domains with the biggest trust deltas).
    
    Args:
        limit: Maximum number of movers to return
        
    Returns:
        List of top mover dictionaries
    """
    return get_foma_publisher().get_top_movers(limit)

def get_category_insight_summary() -> Dict[str, Dict]:
    """
    Get insight summary by category.
    
    Returns:
        Dictionary of category insight summaries
    """
    return get_foma_publisher().get_category_insight_summary()

def generate_weekly_insight_blurbs() -> List[str]:
    """
    Generate weekly insight blurbs for public display.
    
    Returns:
        List of blurb strings
    """
    return get_foma_publisher().generate_weekly_insight_blurbs()