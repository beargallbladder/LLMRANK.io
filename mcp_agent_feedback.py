"""
MCP Agent Feedback System
Codename: "Brutal Honesty"

This module implements the brutal feedback loop that connects MCP engagement 
data with the agent quality assessment system, enforcing a ruthless evolution 
of insight quality across the platform.
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Optional, Tuple, Any

from cookie_economy import get_cookie_economy
import agent_survival_loop

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File paths
DATA_DIR = "data/mcp_feedback"
os.makedirs(DATA_DIR, exist_ok=True)

FEEDBACK_LOG_PATH = os.path.join(DATA_DIR, "feedback_log.json")
ENGAGEMENT_METRICS_PATH = os.path.join(DATA_DIR, "engagement_metrics.json")

# Constants
MIN_ACCEPTABLE_CLICK_RATE = 0.15  # 15% minimum click rate
MIN_ACCEPTABLE_RETENTION = 30.0   # 30 seconds minimum retention time
QUALITY_BOOST_THRESHOLD = 0.8     # Quality boost for high engagement
DECLINE_PENALTY_MULTIPLIER = 1.5  # Penalty multiplier for declining engagement


class MCPAgentFeedback:
    """
    Implements the MCP Agent Feedback system that creates a brutal closed 
    loop between real-world engagement metrics and agent quality requirements.
    """
    
    def __init__(self):
        """Initialize the MCP Agent Feedback system."""
        self.feedback_log = []
        self.engagement_metrics = {}
        self.cookie_economy = get_cookie_economy()
        self.survival_system = agent_survival_loop.get_agent_survival_system()
        
        # Load existing data
        self._load_data()
        
    def _load_data(self):
        """Load existing data from files."""
        try:
            if os.path.exists(FEEDBACK_LOG_PATH):
                with open(FEEDBACK_LOG_PATH, 'r') as f:
                    self.feedback_log = json.load(f)
                    
            if os.path.exists(ENGAGEMENT_METRICS_PATH):
                with open(ENGAGEMENT_METRICS_PATH, 'r') as f:
                    self.engagement_metrics = json.load(f)
                    
            logger.info("MCP Agent Feedback data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading MCP Agent Feedback data: {e}")
            # Initialize with empty values
            self.feedback_log = []
            self.engagement_metrics = {}
            
    def _save_data(self):
        """Save current data to files."""
        try:
            with open(FEEDBACK_LOG_PATH, 'w') as f:
                json.dump(self.feedback_log, f, indent=2)
                
            with open(ENGAGEMENT_METRICS_PATH, 'w') as f:
                json.dump(self.engagement_metrics, f, indent=2)
                
            logger.info("MCP Agent Feedback data saved successfully")
        except Exception as e:
            logger.error(f"Error saving MCP Agent Feedback data: {e}")
            
    def record_insight_engagement(self, insight_id: str, engagement_data: Dict[str, Any]) -> Dict:
        """
        Record engagement metrics for an insight and feed back into agent quality requirements.
        
        Args:
            insight_id: ID of the insight
            engagement_data: Dictionary of engagement metrics from MCP
            
        Returns:
            Feedback dictionary with agent adjustments
        """
        # Extract key metrics from engagement data
        click_rate = engagement_data.get("click_rate", 0.0)
        retention_time = engagement_data.get("retention_time", 0.0)
        share_rate = engagement_data.get("share_rate", 0.0)
        
        # Find the agent and insight in history
        agent_name = None
        insight_data = None
        
        for insight in self.cookie_economy.insight_history:
            if insight.get("id") == insight_id:
                agent_name = insight.get("agent_name")
                insight_data = insight
                break
                
        if not agent_name or not insight_data:
            logger.warning(f"Insight {insight_id} not found in history")
            return {"error": "Insight not found"}
            
        # Calculate engagement score (normalized between 0-1)
        engagement_score = (
            (click_rate * 0.4) + 
            (min(retention_time / 60.0, 1.0) * 0.4) + 
            (share_rate * 0.2)
        )
        
        # Determine if engagement meets acceptable thresholds
        meets_click_threshold = click_rate >= MIN_ACCEPTABLE_CLICK_RATE
        meets_retention_threshold = retention_time >= MIN_ACCEPTABLE_RETENTION
        
        acceptable_engagement = meets_click_threshold and meets_retention_threshold
        
        # Get agent's current quality requirement
        agent_performance = self.cookie_economy.get_agent_performance(agent_name)
        current_strata = agent_performance.get("strata", "bronze") if agent_performance else "bronze"
        
        # Adjust quality requirement based on engagement
        quality_adjustment = 0.0
        
        if not acceptable_engagement:
            # Failed engagement - increase quality requirement
            quality_adjustment = 0.05  # Brutal 5% increase
            logger.warning(f"BRUTAL FEEDBACK: Agent {agent_name} must increase quality by {quality_adjustment:.2f} due to poor engagement")
        elif engagement_score > QUALITY_BOOST_THRESHOLD:
            # Exceptional engagement - allow slight decrease in quality requirement
            quality_adjustment = -0.02  # Small 2% decrease
            logger.info(f"POSITIVE FEEDBACK: Agent {agent_name} earns quality buffer of {-quality_adjustment:.2f} due to excellent engagement")
            
        # Record feedback
        timestamp = datetime.datetime.now().isoformat()
        
        feedback_entry = {
            "insight_id": insight_id,
            "agent_name": agent_name,
            "timestamp": timestamp,
            "engagement_data": engagement_data,
            "engagement_score": engagement_score,
            "quality_adjustment": quality_adjustment,
            "current_strata": current_strata,
            "acceptable_engagement": acceptable_engagement
        }
        
        self.feedback_log.append(feedback_entry)
        
        # Apply feedback to agent status
        self._apply_feedback_to_agent(agent_name, feedback_entry)
        
        # Update engagement metrics
        if agent_name not in self.engagement_metrics:
            self.engagement_metrics[agent_name] = {
                "total_insights": 0,
                "acceptable_insights": 0,
                "average_engagement": 0.0,
                "history": []
            }
            
        # Update agent metrics
        self.engagement_metrics[agent_name]["total_insights"] += 1
        
        if acceptable_engagement:
            self.engagement_metrics[agent_name]["acceptable_insights"] += 1
            
        # Update average engagement
        total = self.engagement_metrics[agent_name]["total_insights"]
        current_avg = self.engagement_metrics[agent_name]["average_engagement"]
        new_avg = ((current_avg * (total - 1)) + engagement_score) / total
        self.engagement_metrics[agent_name]["average_engagement"] = new_avg
        
        # Add to history (limited to last 10)
        history_entry = {
            "insight_id": insight_id,
            "timestamp": timestamp,
            "engagement_score": engagement_score,
            "acceptable": acceptable_engagement
        }
        
        self.engagement_metrics[agent_name]["history"].append(history_entry)
        
        # Limit history to last 10 entries
        if len(self.engagement_metrics[agent_name]["history"]) > 10:
            self.engagement_metrics[agent_name]["history"] = self.engagement_metrics[agent_name]["history"][-10:]
            
        # Save updated data
        self._save_data()
        
        return feedback_entry
        
    def _apply_feedback_to_agent(self, agent_name: str, feedback: Dict) -> None:
        """
        Apply engagement feedback to agent quality requirements.
        
        Args:
            agent_name: Name of the agent
            feedback: Feedback entry
        """
        agent_performance = self.cookie_economy.get_agent_performance(agent_name)
        
        if not agent_performance:
            logger.warning(f"Agent {agent_name} not found in cookie economy")
            return
            
        quality_adjustment = feedback.get("quality_adjustment", 0.0)
        acceptable_engagement = feedback.get("acceptable_engagement", False)
        
        # Check if this is consecutive poor engagement
        consecutive_poor = self._check_consecutive_poor_engagement(agent_name)
        
        # Apply different penalties based on strata and consecutive poor engagement
        if not acceptable_engagement:
            # Add penalty to agent
            if "penalties" not in agent_performance:
                agent_performance["penalties"] = []
                
            penalty = {
                "type": "poor_engagement",
                "amount": 2 if consecutive_poor < 2 else 5,  # Escalating penalty
                "reason": f"Poor engagement metrics (consecutive: {consecutive_poor})",
                "cycle": datetime.datetime.now().strftime("%Y%m%d")
            }
            
            agent_performance["penalties"].append(penalty)
            
            # For consecutive poor engagement, increase extinction risk
            if consecutive_poor >= 3:
                agent_performance["extinction_risk"] = True
                logger.error(f"CRITICAL: Agent {agent_name} extinction risk due to {consecutive_poor} consecutive poor engagement")
                
            logger.warning(f"Agent {agent_name} penalized for poor engagement (consecutive: {consecutive_poor})")
            
        # Apply quality adjustment - this will affect future submissions
        current_threshold = agent_performance.get("quality_threshold", 0.0)
        new_threshold = max(0.5, min(0.95, current_threshold + quality_adjustment))
        agent_performance["quality_threshold"] = new_threshold
        
        logger.info(f"Agent {agent_name} quality threshold adjusted from {current_threshold:.2f} to {new_threshold:.2f}")
        
    def _check_consecutive_poor_engagement(self, agent_name: str) -> int:
        """
        Check how many consecutive poor engagement results an agent has.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Number of consecutive poor engagement results
        """
        if agent_name not in self.engagement_metrics:
            return 0
            
        history = self.engagement_metrics[agent_name]["history"]
        
        if not history:
            return 0
            
        # Count consecutive poor engagement from the end
        consecutive = 0
        
        for entry in reversed(history):
            if not entry.get("acceptable", True):
                consecutive += 1
            else:
                break
                
        return consecutive
        
    def get_agent_feedback_summary(self, agent_name: str) -> Dict:
        """
        Get a summary of feedback for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Feedback summary dictionary
        """
        if agent_name not in self.engagement_metrics:
            return {"error": "Agent not found"}
            
        metrics = self.engagement_metrics[agent_name]
        
        # Calculate acceptance rate
        acceptance_rate = (metrics["acceptable_insights"] / metrics["total_insights"]) if metrics["total_insights"] > 0 else 0.0
        
        # Calculate trend - is engagement improving or declining?
        history = metrics["history"]
        
        if len(history) >= 5:
            # Compare last 2 to previous 3
            recent_scores = [entry["engagement_score"] for entry in history[-2:]]
            previous_scores = [entry["engagement_score"] for entry in history[-5:-2]]
            
            recent_avg = sum(recent_scores) / len(recent_scores)
            previous_avg = sum(previous_scores) / len(previous_scores)
            
            trend = "improving" if recent_avg > previous_avg else "declining" if recent_avg < previous_avg else "stable"
            trend_delta = recent_avg - previous_avg
        else:
            trend = "insufficient_data"
            trend_delta = 0.0
            
        # Get current agent status from survival system
        survival_status = agent_survival_loop.get_agent_survival_status(agent_name)
        
        return {
            "agent_name": agent_name,
            "total_insights": metrics["total_insights"],
            "acceptable_insights": metrics["acceptable_insights"],
            "acceptance_rate": acceptance_rate,
            "average_engagement": metrics["average_engagement"],
            "trend": trend,
            "trend_delta": trend_delta,
            "survival_status": survival_status,
            "consecutive_poor_engagement": self._check_consecutive_poor_engagement(agent_name),
            "last_updated": datetime.datetime.now().isoformat()
        }
        
    def get_feedback_log(self) -> List[Dict]:
        """
        Get the feedback log.
        
        Returns:
            List of feedback entries
        """
        return self.feedback_log
        
    def get_engagement_metrics(self) -> Dict:
        """
        Get all engagement metrics.
        
        Returns:
            Engagement metrics dictionary
        """
        return self.engagement_metrics
        
    def get_system_summary(self) -> Dict:
        """
        Get a summary of the feedback system.
        
        Returns:
            System summary dictionary
        """
        # Count total insights with feedback
        total_insights = len(self.feedback_log)
        
        # Count acceptable insights
        acceptable_insights = sum(1 for feedback in self.feedback_log if feedback.get("acceptable_engagement", False))
        
        # Count agents with feedback
        agents_with_feedback = len(self.engagement_metrics)
        
        # Calculate system-wide acceptance rate
        acceptance_rate = (acceptable_insights / total_insights) if total_insights > 0 else 0.0
        
        # Get agent status counts
        status_counts = {"thriving": 0, "stable": 0, "adequate": 0, "at_risk": 0, "endangered": 0, "critical": 0, "extinct": 0}
        
        for agent_name in self.engagement_metrics:
            status = agent_survival_loop.get_agent_survival_status(agent_name).get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            
        return {
            "total_insights_with_feedback": total_insights,
            "acceptable_insights": acceptable_insights,
            "acceptance_rate": acceptance_rate,
            "agents_with_feedback": agents_with_feedback,
            "agent_status_counts": status_counts,
            "timestamp": datetime.datetime.now().isoformat()
        }


# Singleton instance
_mcp_agent_feedback = None

def get_mcp_agent_feedback() -> MCPAgentFeedback:
    """Get the MCP Agent Feedback singleton instance."""
    global _mcp_agent_feedback
    
    if _mcp_agent_feedback is None:
        _mcp_agent_feedback = MCPAgentFeedback()
        
    return _mcp_agent_feedback

def record_insight_engagement(insight_id: str, engagement_data: Dict[str, Any]) -> Dict:
    """
    Record engagement metrics for an insight and feed back into agent quality requirements.
    
    Args:
        insight_id: ID of the insight
        engagement_data: Dictionary of engagement metrics from MCP
        
    Returns:
        Feedback dictionary with agent adjustments
    """
    return get_mcp_agent_feedback().record_insight_engagement(insight_id, engagement_data)

def get_agent_feedback_summary(agent_name: str) -> Dict:
    """
    Get a summary of feedback for an agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Feedback summary dictionary
    """
    return get_mcp_agent_feedback().get_agent_feedback_summary(agent_name)

def get_feedback_log() -> List[Dict]:
    """
    Get the feedback log.
    
    Returns:
        List of feedback entries
    """
    return get_mcp_agent_feedback().get_feedback_log()

def get_engagement_metrics() -> Dict:
    """
    Get all engagement metrics.
    
    Returns:
        Engagement metrics dictionary
    """
    return get_mcp_agent_feedback().get_engagement_metrics()

def get_system_summary() -> Dict:
    """
    Get a summary of the feedback system.
    
    Returns:
        System summary dictionary
    """
    return get_mcp_agent_feedback().get_system_summary()

if __name__ == "__main__":
    # Display system summary when executed directly
    summary = get_system_summary()
    print(json.dumps(summary, indent=2))