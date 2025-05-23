"""
LLMPageRank Cookie Award Dispatcher

This module implements the dispatcher for awarding cookies to agents based on their
performance and the Cookie Combat Runtime Economy rules.
"""

import os
import json
import time
import datetime
import logging
from typing import Dict, List, Optional, Any

import cookie_economy

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class CookieAward:
    """
    Cookie Award Dispatcher that handles cookie allocation to agents based on
    performance metrics and runtime economy rules.
    """
    
    def __init__(self):
        """Initialize the cookie award dispatcher."""
        logger.info("Initializing Cookie Award Dispatcher")
        
        # Initialize cookie economy
        self.cookie_economy = cookie_economy.get_cookie_economy()
        
        # Get initial cookie pool status
        self.cookie_pool = self.cookie_economy.get_cookie_pool_status()
        
        logger.info(f"Cookie pool initialized with {self.cookie_pool.get('remaining_cookies', 0)} cookies")
    
    def award_for_trust_drift(self, agent_name: str, domain: str, drift_magnitude: float,
                             runtime_ms: int, token_count: int) -> Dict:
        """
        Award cookies for detecting trust drift.
        
        Args:
            agent_name: Name of the agent
            domain: Domain where drift was detected
            drift_magnitude: Magnitude of the drift
            runtime_ms: Runtime in milliseconds
            token_count: Token count
            
        Returns:
            Cookie award dictionary
        """
        # Calculate clarity and impact scores based on drift
        abs_drift = abs(drift_magnitude)
        
        # Clarity: Higher for larger drifts
        clarity_score = min(0.95, abs_drift / 10)
        
        # Impact: Higher for larger drifts in important domains
        # In a real implementation, domain importance would be factored in
        impact_score = min(0.95, abs_drift / 8)
        
        logger.info(f"Awarding cookies to {agent_name} for trust drift of {drift_magnitude} on {domain}")
        
        # Award cookies
        award_result = cookie_economy.award_cookies(
            agent_name=agent_name,
            clarity_score=clarity_score,
            impact_score=impact_score,
            runtime_ms=runtime_ms,
            token_count=token_count,
            event_type="trust_drift"
        )
        
        logger.info(f"Awarded {award_result.get('total_cookies', 0)} cookies to {agent_name}")
        
        return award_result
    
    def award_for_peer_overtake(self, agent_name: str, domain: str, overtaken_domain: str,
                               position_change: int, runtime_ms: int, token_count: int) -> Dict:
        """
        Award cookies for detecting peer overtake.
        
        Args:
            agent_name: Name of the agent
            domain: Domain that overtook peer
            overtaken_domain: Domain that was overtaken
            position_change: Change in position
            runtime_ms: Runtime in milliseconds
            token_count: Token count
            
        Returns:
            Cookie award dictionary
        """
        # Calculate clarity and impact scores based on position change
        abs_change = abs(position_change)
        
        # Clarity: Higher for larger position changes
        clarity_score = min(0.95, abs_change / 5)
        
        # Impact: Higher for larger position changes
        # In a real implementation, domain importance would be factored in
        impact_score = min(0.95, abs_change / 4)
        
        logger.info(f"Awarding cookies to {agent_name} for peer overtake: {domain} overtook {overtaken_domain}")
        
        # Award cookies
        award_result = cookie_economy.award_cookies(
            agent_name=agent_name,
            clarity_score=clarity_score,
            impact_score=impact_score,
            runtime_ms=runtime_ms,
            token_count=token_count,
            event_type="peer_overtake"
        )
        
        logger.info(f"Awarded {award_result.get('total_cookies', 0)} cookies to {agent_name}")
        
        return award_result
    
    def award_for_benchmark_movement(self, agent_name: str, category: str, movement_magnitude: float,
                                   runtime_ms: int, token_count: int) -> Dict:
        """
        Award cookies for detecting benchmark movement.
        
        Args:
            agent_name: Name of the agent
            category: Category where benchmark moved
            movement_magnitude: Magnitude of the movement
            runtime_ms: Runtime in milliseconds
            token_count: Token count
            
        Returns:
            Cookie award dictionary
        """
        # Calculate clarity and impact scores based on movement
        abs_movement = abs(movement_magnitude)
        
        # Clarity: Higher for larger movements
        clarity_score = min(0.95, abs_movement / 8)
        
        # Impact: Higher for larger movements
        # In a real implementation, category importance would be factored in
        impact_score = min(0.95, abs_movement / 6)
        
        logger.info(f"Awarding cookies to {agent_name} for benchmark movement of {movement_magnitude} in {category}")
        
        # Award cookies
        award_result = cookie_economy.award_cookies(
            agent_name=agent_name,
            clarity_score=clarity_score,
            impact_score=impact_score,
            runtime_ms=runtime_ms,
            token_count=token_count,
            event_type="benchmark_movement"
        )
        
        logger.info(f"Awarded {award_result.get('total_cookies', 0)} cookies to {agent_name}")
        
        return award_result
    
    def award_for_insight(self, agent_name: str, insight_type: str, clarity_score: float,
                          impact_score: float, runtime_ms: int, token_count: int) -> Dict:
        """
        Award cookies for generating insight.
        
        Args:
            agent_name: Name of the agent
            insight_type: Type of insight
            clarity_score: Clarity score (0-1)
            impact_score: Impact score (0-1)
            runtime_ms: Runtime in milliseconds
            token_count: Token count
            
        Returns:
            Cookie award dictionary
        """
        logger.info(f"Awarding cookies to {agent_name} for {insight_type} insight")
        
        # Award cookies
        award_result = cookie_economy.award_cookies(
            agent_name=agent_name,
            clarity_score=clarity_score,
            impact_score=impact_score,
            runtime_ms=runtime_ms,
            token_count=token_count,
            event_type=f"insight_{insight_type}"
        )
        
        logger.info(f"Awarded {award_result.get('total_cookies', 0)} cookies to {agent_name}")
        
        return award_result
    
    def award_for_prompt_optimization(self, agent_name: str, category: str, improvement: float,
                                     runtime_ms: int, token_count: int) -> Dict:
        """
        Award cookies for prompt optimization.
        
        Args:
            agent_name: Name of the agent
            category: Category where prompts were optimized
            improvement: Improvement in prompt effectiveness
            runtime_ms: Runtime in milliseconds
            token_count: Token count
            
        Returns:
            Cookie award dictionary
        """
        # Calculate clarity and impact scores based on improvement
        # Clarity: Higher for larger improvements
        clarity_score = min(0.95, improvement)
        
        # Impact: Higher for larger improvements
        # In a real implementation, category importance would be factored in
        impact_score = min(0.95, improvement * 1.2)
        
        logger.info(f"Awarding cookies to {agent_name} for prompt optimization in {category}")
        
        # Award cookies
        award_result = cookie_economy.award_cookies(
            agent_name=agent_name,
            clarity_score=clarity_score,
            impact_score=impact_score,
            runtime_ms=runtime_ms,
            token_count=token_count,
            event_type="prompt_optimization"
        )
        
        logger.info(f"Awarded {award_result.get('total_cookies', 0)} cookies to {agent_name}")
        
        return award_result
    
    def award_for_validation(self, agent_name: str, validation_type: str, issues_found: int,
                            runtime_ms: int, token_count: int) -> Dict:
        """
        Award cookies for validation tasks.
        
        Args:
            agent_name: Name of the agent
            validation_type: Type of validation
            issues_found: Number of issues found
            runtime_ms: Runtime in milliseconds
            token_count: Token count
            
        Returns:
            Cookie award dictionary
        """
        # Calculate clarity and impact scores based on issues found
        # Clarity: Higher for finding issues
        clarity_score = min(0.95, issues_found * 0.2 + 0.5)
        
        # Impact: Higher for finding more issues
        impact_score = min(0.95, issues_found * 0.15 + 0.6)
        
        logger.info(f"Awarding cookies to {agent_name} for {validation_type} validation")
        
        # Award cookies
        award_result = cookie_economy.award_cookies(
            agent_name=agent_name,
            clarity_score=clarity_score,
            impact_score=impact_score,
            runtime_ms=runtime_ms,
            token_count=token_count,
            event_type=f"validation_{validation_type}"
        )
        
        logger.info(f"Awarded {award_result.get('total_cookies', 0)} cookies to {agent_name}")
        
        return award_result
    
    def award_for_story_generation(self, agent_name: str, story_type: str, clarity_score: float,
                                  impact_score: float, runtime_ms: int, token_count: int) -> Dict:
        """
        Award cookies for story generation.
        
        Args:
            agent_name: Name of the agent
            story_type: Type of story
            clarity_score: Clarity score (0-1)
            impact_score: Impact score (0-1)
            runtime_ms: Runtime in milliseconds
            token_count: Token count
            
        Returns:
            Cookie award dictionary
        """
        logger.info(f"Awarding cookies to {agent_name} for {story_type} story generation")
        
        # Award cookies
        award_result = cookie_economy.award_cookies(
            agent_name=agent_name,
            clarity_score=clarity_score,
            impact_score=impact_score,
            runtime_ms=runtime_ms,
            token_count=token_count,
            event_type=f"story_{story_type}"
        )
        
        logger.info(f"Awarded {award_result.get('total_cookies', 0)} cookies to {agent_name}")
        
        return award_result
    
    def award_for_agent_rescue(self, agent_name: str, rescued_agent: str, contribution_level: float,
                              runtime_ms: int, token_count: int) -> Dict:
        """
        Award cookies for rescuing a failing agent.
        
        Args:
            agent_name: Name of the agent
            rescued_agent: Name of the rescued agent
            contribution_level: Level of contribution (0-1)
            runtime_ms: Runtime in milliseconds
            token_count: Token count
            
        Returns:
            Cookie award dictionary
        """
        # Calculate clarity and impact scores based on contribution
        # Clarity: Fixed for rescue operations
        clarity_score = 0.8
        
        # Impact: Based on contribution level
        impact_score = min(0.95, contribution_level)
        
        logger.info(f"Awarding cookies to {agent_name} for rescuing {rescued_agent}")
        
        # Award cookies
        award_result = cookie_economy.award_cookies(
            agent_name=agent_name,
            clarity_score=clarity_score,
            impact_score=impact_score,
            runtime_ms=runtime_ms,
            token_count=token_count,
            event_type="agent_rescue"
        )
        
        logger.info(f"Awarded {award_result.get('total_cookies', 0)} cookies to {agent_name}")
        
        return award_result
    
    def check_pool_status(self) -> Dict:
        """
        Check current cookie pool status.
        
        Returns:
            Cookie pool status dictionary
        """
        # Refresh cookie pool status
        self.cookie_pool = self.cookie_economy.get_cookie_pool_status()
        
        logger.info(f"Cookie pool has {self.cookie_pool.get('remaining_cookies', 0)} cookies remaining")
        
        return self.cookie_pool
    
    def check_failover_conditions(self) -> Dict:
        """
        Check failover conditions.
        
        Returns:
            Failover condition dictionary
        """
        failover_report = self.cookie_economy.check_failover_conditions()
        
        if failover_report.get("signal_degradation_detected", False):
            logger.warning(f"Signal degradation detected: {failover_report.get('failover_reason', '')}")
        
        return failover_report
    
    def reset_cookie_pool(self) -> bool:
        """
        Reset the cookie pool (typically called daily).
        
        Returns:
            Success flag
        """
        logger.info("Resetting cookie pool")
        
        result = self.cookie_economy.reset_daily_cookie_pool()
        
        if result:
            logger.info("Cookie pool reset successfully")
            
            # Refresh cookie pool status
            self.cookie_pool = self.cookie_economy.get_cookie_pool_status()
        else:
            logger.error("Failed to reset cookie pool")
        
        return result


# Singleton instance
_instance = None

def get_cookie_award() -> CookieAward:
    """
    Get the cookie award dispatcher singleton instance.
    
    Returns:
        Cookie award dispatcher instance
    """
    global _instance
    
    if _instance is None:
        _instance = CookieAward()
    
    return _instance

def award_for_trust_drift(agent_name: str, domain: str, drift_magnitude: float,
                         runtime_ms: int, token_count: int) -> Dict:
    """
    Award cookies for detecting trust drift.
    
    Args:
        agent_name: Name of the agent
        domain: Domain where drift was detected
        drift_magnitude: Magnitude of the drift
        runtime_ms: Runtime in milliseconds
        token_count: Token count
        
    Returns:
        Cookie award dictionary
    """
    return get_cookie_award().award_for_trust_drift(agent_name, domain, drift_magnitude,
                                                 runtime_ms, token_count)

def award_for_peer_overtake(agent_name: str, domain: str, overtaken_domain: str,
                           position_change: int, runtime_ms: int, token_count: int) -> Dict:
    """
    Award cookies for detecting peer overtake.
    
    Args:
        agent_name: Name of the agent
        domain: Domain that overtook peer
        overtaken_domain: Domain that was overtaken
        position_change: Change in position
        runtime_ms: Runtime in milliseconds
        token_count: Token count
        
    Returns:
        Cookie award dictionary
    """
    return get_cookie_award().award_for_peer_overtake(agent_name, domain, overtaken_domain,
                                                   position_change, runtime_ms, token_count)

def award_for_benchmark_movement(agent_name: str, category: str, movement_magnitude: float,
                               runtime_ms: int, token_count: int) -> Dict:
    """
    Award cookies for detecting benchmark movement.
    
    Args:
        agent_name: Name of the agent
        category: Category where benchmark moved
        movement_magnitude: Magnitude of the movement
        runtime_ms: Runtime in milliseconds
        token_count: Token count
        
    Returns:
        Cookie award dictionary
    """
    return get_cookie_award().award_for_benchmark_movement(agent_name, category, movement_magnitude,
                                                       runtime_ms, token_count)

def award_for_insight(agent_name: str, insight_type: str, clarity_score: float,
                      impact_score: float, runtime_ms: int, token_count: int) -> Dict:
    """
    Award cookies for generating insight.
    
    Args:
        agent_name: Name of the agent
        insight_type: Type of insight
        clarity_score: Clarity score (0-1)
        impact_score: Impact score (0-1)
        runtime_ms: Runtime in milliseconds
        token_count: Token count
        
    Returns:
        Cookie award dictionary
    """
    return get_cookie_award().award_for_insight(agent_name, insight_type, clarity_score,
                                             impact_score, runtime_ms, token_count)

def award_for_prompt_optimization(agent_name: str, category: str, improvement: float,
                                 runtime_ms: int, token_count: int) -> Dict:
    """
    Award cookies for prompt optimization.
    
    Args:
        agent_name: Name of the agent
        category: Category where prompts were optimized
        improvement: Improvement in prompt effectiveness
        runtime_ms: Runtime in milliseconds
        token_count: Token count
        
    Returns:
        Cookie award dictionary
    """
    return get_cookie_award().award_for_prompt_optimization(agent_name, category, improvement,
                                                         runtime_ms, token_count)

def award_for_validation(agent_name: str, validation_type: str, issues_found: int,
                        runtime_ms: int, token_count: int) -> Dict:
    """
    Award cookies for validation tasks.
    
    Args:
        agent_name: Name of the agent
        validation_type: Type of validation
        issues_found: Number of issues found
        runtime_ms: Runtime in milliseconds
        token_count: Token count
        
    Returns:
        Cookie award dictionary
    """
    return get_cookie_award().award_for_validation(agent_name, validation_type, issues_found,
                                                runtime_ms, token_count)

def award_for_story_generation(agent_name: str, story_type: str, clarity_score: float,
                              impact_score: float, runtime_ms: int, token_count: int) -> Dict:
    """
    Award cookies for story generation.
    
    Args:
        agent_name: Name of the agent
        story_type: Type of story
        clarity_score: Clarity score (0-1)
        impact_score: Impact score (0-1)
        runtime_ms: Runtime in milliseconds
        token_count: Token count
        
    Returns:
        Cookie award dictionary
    """
    return get_cookie_award().award_for_story_generation(agent_name, story_type, clarity_score,
                                                      impact_score, runtime_ms, token_count)

def award_for_agent_rescue(agent_name: str, rescued_agent: str, contribution_level: float,
                          runtime_ms: int, token_count: int) -> Dict:
    """
    Award cookies for rescuing a failing agent.
    
    Args:
        agent_name: Name of the agent
        rescued_agent: Name of the rescued agent
        contribution_level: Level of contribution (0-1)
        runtime_ms: Runtime in milliseconds
        token_count: Token count
        
    Returns:
        Cookie award dictionary
    """
    return get_cookie_award().award_for_agent_rescue(agent_name, rescued_agent, contribution_level,
                                                  runtime_ms, token_count)

def check_pool_status() -> Dict:
    """
    Check current cookie pool status.
    
    Returns:
        Cookie pool status dictionary
    """
    return get_cookie_award().check_pool_status()

def check_failover_conditions() -> Dict:
    """
    Check failover conditions.
    
    Returns:
        Failover condition dictionary
    """
    return get_cookie_award().check_failover_conditions()

def reset_cookie_pool() -> bool:
    """
    Reset the cookie pool (typically called daily).
    
    Returns:
        Success flag
    """
    return get_cookie_award().reset_cookie_pool()