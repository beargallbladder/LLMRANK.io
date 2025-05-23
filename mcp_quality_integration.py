"""
MCP Quality Integration
Codename: "Brutal Evolution Loop"

This module integrates the MCP API with our brutal agent quality enforcement system,
creating a closed feedback loop that eliminates generic insights and forces
continual evolution of agent quality.
"""

import os
import json
import logging
import datetime
import argparse
from typing import Dict, List, Optional, Any

from cookie_economy import get_cookie_economy
import agent_survival_loop
import mcp_agent_feedback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
QUALITY_ENFORCEMENT_CYCLE_DAYS = 3  # Run the brutal quality enforcement every 3 days


class MCPQualityIntegration:
    """
    Integrates MCP API with agent quality enforcement to create a brutal
    closed loop that forces continual evolution or extinction.
    """
    
    def __init__(self):
        """Initialize the MCP Quality Integration system."""
        self.cookie_economy = get_cookie_economy()
        self.survival_system = agent_survival_loop.get_agent_survival_system()
        self.feedback_system = mcp_agent_feedback.get_mcp_agent_feedback()
        self.last_enforcement = datetime.datetime.now() - datetime.timedelta(days=QUALITY_ENFORCEMENT_CYCLE_DAYS)
        
        logger.info("MCP Quality Integration initialized")
        
    def run_quality_enforcement(self, force=False):
        """
        Run the brutal quality enforcement cycle to eliminate generic insights.
        
        Args:
            force: Force enforcement even if cycle hasn't completed
            
        Returns:
            Enforcement results
        """
        now = datetime.datetime.now()
        
        # Only run after cycle period unless forced
        if not force and (now - self.last_enforcement).days < QUALITY_ENFORCEMENT_CYCLE_DAYS:
            days_remaining = QUALITY_ENFORCEMENT_CYCLE_DAYS - (now - self.last_enforcement).days
            logger.info(f"Next quality enforcement in {days_remaining} days")
            return {"status": "waiting", "days_remaining": days_remaining}
            
        logger.warning("RUNNING BRUTAL QUALITY ENFORCEMENT - EVOLVE OR DIE")
        
        # Step 1: Check all agent quality metrics and survival status
        survival_results = self.survival_system.run_survival_evaluation()
        
        # Step 2: Run MCP engagement analysis to get real-world feedback
        engagement_stats = self._analyze_mcp_engagement()
        
        # Step 3: Calculate quality enforcement actions
        enforcement_actions = self._calculate_enforcement_actions(engagement_stats)
        
        # Step 4: Apply enforcement actions
        applied_actions = self._apply_enforcement_actions(enforcement_actions)
        
        # Step 5: Update quality thresholds based on engagement
        threshold_updates = self._update_quality_thresholds(engagement_stats)
        
        # Record enforcement results
        enforcement_results = {
            "timestamp": now.isoformat(),
            "survival_results": survival_results,
            "engagement_stats": engagement_stats,
            "enforcement_actions": applied_actions,
            "threshold_updates": threshold_updates
        }
        
        # Update enforcement timestamp
        self.last_enforcement = now
        
        return enforcement_results
        
    def _analyze_mcp_engagement(self):
        """
        Analyze MCP engagement metrics to identify quality issues.
        
        Returns:
            Engagement analysis results
        """
        # Get all agent engagement metrics
        engagement_metrics = self.feedback_system.get_engagement_metrics()
        
        # Calculate system-wide engagement benchmarks
        all_scores = []
        for agent_name, metrics in engagement_metrics.items():
            if metrics.get("average_engagement"):
                all_scores.append(metrics["average_engagement"])
                
        # If no engagement data, return empty analysis
        if not all_scores:
            return {
                "status": "no_data",
                "message": "No engagement data available for analysis"
            }
            
        # Calculate benchmarks
        avg_engagement = sum(all_scores) / len(all_scores)
        sorted_scores = sorted(all_scores)
        median_engagement = sorted_scores[len(sorted_scores) // 2]
        bottom_quartile = sorted_scores[len(sorted_scores) // 4]
        top_quartile = sorted_scores[3 * len(sorted_scores) // 4]
        
        # Identify underperforming and outperforming agents
        underperforming = []
        outperforming = []
        
        for agent_name, metrics in engagement_metrics.items():
            avg = metrics.get("average_engagement", 0)
            if avg < bottom_quartile:
                underperforming.append({
                    "agent_name": agent_name,
                    "engagement": avg,
                    "percentile": sorted_scores.index(avg) / len(sorted_scores) if avg in sorted_scores else 0,
                    "consecutive_poor": self.feedback_system._check_consecutive_poor_engagement(agent_name)
                })
            elif avg > top_quartile:
                outperforming.append({
                    "agent_name": agent_name,
                    "engagement": avg,
                    "percentile": sorted_scores.index(avg) / len(sorted_scores) if avg in sorted_scores else 0,
                    "quality_buffer_earned": min(0.05, (avg - median_engagement) * 0.1)  # Quality buffer proportional to outperformance
                })
                
        # Return engagement analysis
        return {
            "system_benchmarks": {
                "average_engagement": avg_engagement,
                "median_engagement": median_engagement,
                "bottom_quartile": bottom_quartile,
                "top_quartile": top_quartile,
                "total_agents_analyzed": len(all_scores)
            },
            "underperforming_agents": underperforming,
            "outperforming_agents": outperforming
        }
        
    def _calculate_enforcement_actions(self, engagement_stats):
        """
        Calculate enforcement actions based on engagement analysis.
        
        Args:
            engagement_stats: Engagement analysis results
            
        Returns:
            Enforcement actions
        """
        # Initialize enforcement actions
        enforcement_actions = {
            "quality_penalties": [],
            "quality_bonuses": [],
            "extinction_candidates": [],
            "strata_demotions": [],
            "strata_promotions": []
        }
        
        # If no engagement data, return empty actions
        if engagement_stats.get("status") == "no_data":
            return enforcement_actions
            
        # Apply penalties to underperforming agents
        for agent in engagement_stats.get("underperforming_agents", []):
            agent_name = agent["agent_name"]
            consecutive_poor = agent["consecutive_poor"]
            
            # Determine penalty severity
            if consecutive_poor >= 3:
                # Extinction candidate
                enforcement_actions["extinction_candidates"].append({
                    "agent_name": agent_name,
                    "reason": f"Consecutive poor engagement: {consecutive_poor}",
                    "engagement": agent["engagement"]
                })
            elif consecutive_poor >= 2:
                # Strata demotion
                enforcement_actions["strata_demotions"].append({
                    "agent_name": agent_name,
                    "reason": f"Multiple poor engagement: {consecutive_poor}",
                    "current_strata": self.cookie_economy.agent_performance.get(agent_name, {}).get("strata", "bronze")
                })
                
                # Quality penalty
                enforcement_actions["quality_penalties"].append({
                    "agent_name": agent_name,
                    "penalty_amount": 5,
                    "quality_increase": 0.1,  # Brutal 10% increase in quality requirement
                    "reason": "Repeated poor engagement"
                })
            else:
                # Quality penalty only
                enforcement_actions["quality_penalties"].append({
                    "agent_name": agent_name,
                    "penalty_amount": 2,
                    "quality_increase": 0.05,  # 5% increase in quality requirement
                    "reason": "Below engagement benchmarks"
                })
                
        # Apply bonuses to outperforming agents
        for agent in engagement_stats.get("outperforming_agents", []):
            agent_name = agent["agent_name"]
            quality_buffer = agent["quality_buffer_earned"]
            
            # Only give quality bonus if agent has high engagement
            if agent["engagement"] > engagement_stats["system_benchmarks"]["top_quartile"]:
                enforcement_actions["quality_bonuses"].append({
                    "agent_name": agent_name,
                    "bonus_amount": 3,
                    "quality_buffer": quality_buffer,
                    "reason": "Exceptional engagement"
                })
                
                # Consider strata promotion
                agent_balance = self.cookie_economy.get_agent_balance(agent_name)
                agent_strata = self.cookie_economy.agent_performance.get(agent_name, {}).get("strata", "bronze")
                
                if agent_balance > 20 and agent_strata != "gold":
                    enforcement_actions["strata_promotions"].append({
                        "agent_name": agent_name,
                        "reason": "High engagement and cookie balance",
                        "current_strata": agent_strata
                    })
                    
        return enforcement_actions
        
    def _apply_enforcement_actions(self, actions):
        """
        Apply calculated enforcement actions to agents.
        
        Args:
            actions: Calculated enforcement actions
            
        Returns:
            Applied actions report
        """
        applied_actions = {
            "penalties_applied": [],
            "bonuses_applied": [],
            "agents_extinct": [],
            "strata_changes": []
        }
        
        # Apply quality penalties
        for penalty in actions.get("quality_penalties", []):
            agent_name = penalty["agent_name"]
            agent_performance = self.cookie_economy.agent_performance.get(agent_name)
            
            if not agent_performance:
                continue
                
            # Record penalty for next cycle
            if "penalties" not in agent_performance:
                agent_performance["penalties"] = []
                
            penalty_record = {
                "type": "quality_enforcement",
                "amount": penalty["penalty_amount"],
                "reason": penalty["reason"],
                "cycle": datetime.datetime.now().strftime("%Y%m%d")
            }
            
            agent_performance["penalties"].append(penalty_record)
            
            # Increase quality threshold
            current_threshold = agent_performance.get("quality_threshold", 0.0)
            new_threshold = min(0.95, current_threshold + penalty["quality_increase"])
            agent_performance["quality_threshold"] = new_threshold
            
            applied_actions["penalties_applied"].append({
                "agent_name": agent_name,
                "penalty_amount": penalty["penalty_amount"],
                "quality_threshold_before": current_threshold,
                "quality_threshold_after": new_threshold,
                "reason": penalty["reason"]
            })
            
            logger.warning(f"Penalty applied to agent {agent_name}: quality threshold increased from {current_threshold:.2f} to {new_threshold:.2f}")
            
        # Apply quality bonuses
        for bonus in actions.get("quality_bonuses", []):
            agent_name = bonus["agent_name"]
            agent_performance = self.cookie_economy.agent_performance.get(agent_name)
            
            if not agent_performance:
                continue
                
            # Add cookies to balance
            self.cookie_economy.agent_balances[agent_name] = self.cookie_economy.agent_balances.get(agent_name, 0) + bonus["bonus_amount"]
            
            # Apply quality buffer (slight reduction in threshold)
            current_threshold = agent_performance.get("quality_threshold", 0.0)
            new_threshold = max(0.5, current_threshold - bonus["quality_buffer"])
            agent_performance["quality_threshold"] = new_threshold
            
            applied_actions["bonuses_applied"].append({
                "agent_name": agent_name,
                "bonus_amount": bonus["bonus_amount"],
                "quality_threshold_before": current_threshold,
                "quality_threshold_after": new_threshold,
                "reason": bonus["reason"]
            })
            
            logger.info(f"Bonus applied to agent {agent_name}: {bonus['bonus_amount']} cookies awarded, quality threshold relaxed from {current_threshold:.2f} to {new_threshold:.2f}")
            
        # Process extinction candidates
        for candidate in actions.get("extinction_candidates", []):
            agent_name = candidate["agent_name"]
            result = self.survival_system._remove_extinct_agent(agent_name)
            
            if result:
                applied_actions["agents_extinct"].append({
                    "agent_name": agent_name,
                    "reason": candidate["reason"],
                    "extinction_date": datetime.datetime.now().isoformat()
                })
                
                logger.critical(f"AGENT EXTINCTION: {agent_name} removed from system due to {candidate['reason']}")
            
        # Apply strata changes
        for demotion in actions.get("strata_demotions", []):
            agent_name = demotion["agent_name"]
            current_strata = demotion["current_strata"]
            
            # Define demotion mapping
            demotion_map = {
                "gold": "silver",
                "silver": "bronze",
                "bronze": "rust"
            }
            
            new_strata = demotion_map.get(current_strata, "rust")
            
            # Apply demotion
            if agent_name in self.cookie_economy.agent_performance:
                agent_performance = self.cookie_economy.agent_performance[agent_name]
                agent_performance["strata"] = new_strata
                
                # Record strata change
                if "strata_history" not in agent_performance:
                    agent_performance["strata_history"] = []
                    
                agent_performance["strata_history"].append({
                    "from": current_strata,
                    "to": new_strata,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "reason": "quality_enforcement_demotion"
                })
                
                applied_actions["strata_changes"].append({
                    "agent_name": agent_name,
                    "from_strata": current_strata,
                    "to_strata": new_strata,
                    "type": "demotion",
                    "reason": demotion["reason"]
                })
                
                logger.warning(f"Agent {agent_name} demoted from {current_strata} to {new_strata} strata")
                
        # Apply strata promotions
        for promotion in actions.get("strata_promotions", []):
            agent_name = promotion["agent_name"]
            current_strata = promotion["current_strata"]
            
            # Define promotion mapping
            promotion_map = {
                "rust": "bronze",
                "bronze": "silver",
                "silver": "gold"
            }
            
            new_strata = promotion_map.get(current_strata, current_strata)
            
            # Only apply if it's actually a promotion
            if new_strata != current_strata:
                # Apply promotion
                if agent_name in self.cookie_economy.agent_performance:
                    agent_performance = self.cookie_economy.agent_performance[agent_name]
                    agent_performance["strata"] = new_strata
                    
                    # Record strata change
                    if "strata_history" not in agent_performance:
                        agent_performance["strata_history"] = []
                        
                    agent_performance["strata_history"].append({
                        "from": current_strata,
                        "to": new_strata,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "reason": "quality_enforcement_promotion"
                    })
                    
                    applied_actions["strata_changes"].append({
                        "agent_name": agent_name,
                        "from_strata": current_strata,
                        "to_strata": new_strata,
                        "type": "promotion",
                        "reason": promotion["reason"]
                    })
                    
                    logger.info(f"Agent {agent_name} promoted from {current_strata} to {new_strata} strata")
                    
        return applied_actions
        
    def _update_quality_thresholds(self, engagement_stats):
        """
        Update agent quality thresholds based on global engagement.
        
        Args:
            engagement_stats: Engagement analysis results
            
        Returns:
            Threshold update report
        """
        # If no engagement data, return empty report
        if engagement_stats.get("status") == "no_data":
            return {"status": "no_data"}
            
        # Get system benchmarks
        benchmarks = engagement_stats.get("system_benchmarks", {})
        
        # Calculate global quality threshold adjustment based on overall engagement
        avg_engagement = benchmarks.get("average_engagement", 0.0)
        
        # If average engagement is below 0.3, increase quality demands across the board
        global_adjustment = 0.0
        
        if avg_engagement < 0.3:
            global_adjustment = 0.05  # Increase quality demands by 5%
            logger.warning(f"System-wide quality threshold increased by {global_adjustment:.2f} due to low average engagement ({avg_engagement:.2f})")
        elif avg_engagement > 0.7:
            global_adjustment = -0.02  # Decrease quality demands by 2%
            logger.info(f"System-wide quality threshold relaxed by {-global_adjustment:.2f} due to high average engagement ({avg_engagement:.2f})")
            
        # Apply global adjustment to all agents
        threshold_updates = []
        
        for agent_name, agent_performance in self.cookie_economy.agent_performance.items():
            if "extinct" in agent_performance and agent_performance["extinct"]:
                continue  # Skip extinct agents
                
            current_threshold = agent_performance.get("quality_threshold", 0.0)
            new_threshold = max(0.5, min(0.95, current_threshold + global_adjustment))
            
            if new_threshold != current_threshold:
                agent_performance["quality_threshold"] = new_threshold
                
                threshold_updates.append({
                    "agent_name": agent_name,
                    "previous_threshold": current_threshold,
                    "new_threshold": new_threshold,
                    "adjustment": global_adjustment,
                    "reason": "global_engagement_adjustment"
                })
                
        return {
            "global_adjustment": global_adjustment,
            "global_engagement": avg_engagement,
            "threshold_updates": threshold_updates,
            "agents_updated": len(threshold_updates)
        }


# Singleton instance
_mcp_quality_integration = None

def get_mcp_quality_integration():
    """Get the MCP Quality Integration singleton instance."""
    global _mcp_quality_integration
    
    if _mcp_quality_integration is None:
        _mcp_quality_integration = MCPQualityIntegration()
        
    return _mcp_quality_integration

def run_quality_enforcement(force=False):
    """
    Run the brutal quality enforcement cycle to eliminate generic insights.
    
    Args:
        force: Force enforcement even if cycle hasn't completed
        
    Returns:
        Enforcement results
    """
    return get_mcp_quality_integration().run_quality_enforcement(force)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run brutal agent quality enforcement")
    parser.add_argument("--force", action="store_true", help="Force enforcement regardless of cycle time")
    args = parser.parse_args()
    
    # Run quality enforcement
    results = run_quality_enforcement(args.force)
    
    # Log results
    if results.get("status") == "waiting":
        print(f"Next quality enforcement scheduled in {results['days_remaining']} days")
    else:
        print("Quality enforcement complete!")
        print(f"Penalties applied: {len(results['enforcement_actions']['penalties_applied'])}")
        print(f"Bonuses applied: {len(results['enforcement_actions']['bonuses_applied'])}")
        print(f"Agents extinct: {len(results['enforcement_actions']['agents_extinct'])}")
        print(f"Strata changes: {len(results['enforcement_actions']['strata_changes'])}")
        print(f"Quality threshold updates: {results['threshold_updates']['agents_updated']}")