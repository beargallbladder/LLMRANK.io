"""
Engagement Warfare Engine
Codename: "Weaponry Against Being Forgotten"

This module creates a real-time engagement detection system that monitors
frontend interactions, crawl patterns, clicks, impressions, and movement
to drive agent evolution and fight against brand memory decay.
"""

import os
import json
import logging
import datetime
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import time
import threading

from agent_directive_contract import get_agent_directive_contract, validate_agent_performance
import mcp_agent_feedback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File paths
DATA_DIR = "data/engagement_warfare"
os.makedirs(DATA_DIR, exist_ok=True)

REAL_TIME_ENGAGEMENT_PATH = os.path.join(DATA_DIR, "real_time_engagement.json")
PATTERN_DETECTION_PATH = os.path.join(DATA_DIR, "pattern_detection.json")
ECOSYSTEM_EVOLUTION_PATH = os.path.join(DATA_DIR, "ecosystem_evolution.json")
ENGAGEMENT_WEAPONS_PATH = os.path.join(DATA_DIR, "engagement_weapons.json")


class EngagementWarfareEngine:
    """
    Real-time engagement warfare system that monitors all frontend interactions
    and drives agent evolution based on actual user behavior patterns.
    """
    
    def __init__(self):
        """Initialize the Engagement Warfare Engine."""
        self.real_time_data = {}
        self.pattern_detection = {}
        self.ecosystem_evolution = {}
        self.engagement_weapons = {}
        self.active_monitoring = False
        self.directive_contract = get_agent_directive_contract()
        self.feedback_system = mcp_agent_feedback.get_mcp_agent_feedback()
        
        # Real-time metrics tracking
        self.click_streams = defaultdict(list)
        self.impression_data = defaultdict(dict)
        self.movement_patterns = defaultdict(list)
        self.scroll_depths = defaultdict(list)
        self.retention_times = defaultdict(list)
        self.requery_patterns = defaultdict(list)
        
        # Pattern detection thresholds
        self.engagement_thresholds = {
            "click_rate_alert": 0.05,  # 5% drop triggers alert
            "retention_drop": 10.0,    # 10 second drop triggers alert
            "impression_decay": 0.1,   # 10% impression decay
            "movement_stagnation": 30.0,  # 30 seconds without movement
            "requery_surge": 2.0       # 2x increase in requeries
        }
        
        # Load existing data
        self._load_data()
        
        # Start real-time monitoring
        self._start_monitoring()
        
        logger.warning("ENGAGEMENT WARFARE ENGINE ACTIVATED - Fighting against being forgotten")
        
    def _load_data(self):
        """Load existing engagement warfare data."""
        try:
            if os.path.exists(REAL_TIME_ENGAGEMENT_PATH):
                with open(REAL_TIME_ENGAGEMENT_PATH, 'r') as f:
                    self.real_time_data = json.load(f)
                    
            if os.path.exists(PATTERN_DETECTION_PATH):
                with open(PATTERN_DETECTION_PATH, 'r') as f:
                    self.pattern_detection = json.load(f)
                    
            if os.path.exists(ECOSYSTEM_EVOLUTION_PATH):
                with open(ECOSYSTEM_EVOLUTION_PATH, 'r') as f:
                    self.ecosystem_evolution = json.load(f)
                    
            if os.path.exists(ENGAGEMENT_WEAPONS_PATH):
                with open(ENGAGEMENT_WEAPONS_PATH, 'r') as f:
                    self.engagement_weapons = json.load(f)
                    
            logger.info("Engagement warfare data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading engagement warfare data: {e}")
            
    def _save_data(self):
        """Save engagement warfare data."""
        try:
            with open(REAL_TIME_ENGAGEMENT_PATH, 'w') as f:
                json.dump(self.real_time_data, f, indent=2)
                
            with open(PATTERN_DETECTION_PATH, 'w') as f:
                json.dump(self.pattern_detection, f, indent=2)
                
            with open(ECOSYSTEM_EVOLUTION_PATH, 'w') as f:
                json.dump(self.ecosystem_evolution, f, indent=2)
                
            with open(ENGAGEMENT_WEAPONS_PATH, 'w') as f:
                json.dump(self.engagement_weapons, f, indent=2)
                
            logger.info("Engagement warfare data saved successfully")
        except Exception as e:
            logger.error(f"Error saving engagement warfare data: {e}")
            
    def _start_monitoring(self):
        """Start real-time monitoring thread."""
        self.active_monitoring = True
        monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitoring_thread.start()
        logger.info("Real-time engagement monitoring started")
        
    def _monitoring_loop(self):
        """Main monitoring loop for real-time engagement detection."""
        while self.active_monitoring:
            try:
                # Detect new patterns every 10 seconds
                self._detect_engagement_patterns()
                
                # Evolve ecosystem based on patterns every 30 seconds
                if int(time.time()) % 30 == 0:
                    self._evolve_ecosystem()
                    
                # Save data every 60 seconds
                if int(time.time()) % 60 == 0:
                    self._save_data()
                    
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait longer on error
                
    def record_frontend_interaction(self, interaction_data: Dict) -> Dict:
        """
        Record real-time frontend interaction for engagement analysis.
        
        Args:
            interaction_data: Real-time interaction data from frontend
            
        Returns:
            Engagement analysis result
        """
        timestamp = datetime.datetime.now().isoformat()
        interaction_type = interaction_data.get("type", "unknown")
        user_id = interaction_data.get("user_id", "anonymous")
        insight_id = interaction_data.get("insight_id")
        domain = interaction_data.get("domain")
        
        # Record interaction by type
        if interaction_type == "click":
            self._record_click_interaction(interaction_data, timestamp)
        elif interaction_type == "impression":
            self._record_impression_interaction(interaction_data, timestamp)
        elif interaction_type == "scroll":
            self._record_scroll_interaction(interaction_data, timestamp)
        elif interaction_type == "retention":
            self._record_retention_interaction(interaction_data, timestamp)
        elif interaction_type == "requery":
            self._record_requery_interaction(interaction_data, timestamp)
        elif interaction_type == "movement":
            self._record_movement_interaction(interaction_data, timestamp)
            
        # Immediate pattern detection for critical changes
        pattern_alert = self._check_immediate_patterns(interaction_data)
        
        # If this interaction relates to an insight, update agent performance
        agent_impact = None
        if insight_id:
            agent_impact = self._update_agent_from_interaction(insight_id, interaction_data)
            
        return {
            "recorded": True,
            "timestamp": timestamp,
            "interaction_type": interaction_type,
            "pattern_alert": pattern_alert,
            "agent_impact": agent_impact,
            "ecosystem_status": self._get_ecosystem_health()
        }
        
    def _record_click_interaction(self, data: Dict, timestamp: str):
        """Record click interaction data."""
        insight_id = data.get("insight_id")
        click_position = data.get("position", {})
        click_delay = data.get("delay", 0)
        
        if insight_id:
            self.click_streams[insight_id].append({
                "timestamp": timestamp,
                "position": click_position,
                "delay": click_delay,
                "user_id": data.get("user_id")
            })
            
            # Limit to last 100 clicks per insight
            if len(self.click_streams[insight_id]) > 100:
                self.click_streams[insight_id] = self.click_streams[insight_id][-100:]
                
    def _record_impression_interaction(self, data: Dict, timestamp: str):
        """Record impression interaction data."""
        insight_id = data.get("insight_id")
        viewport_time = data.get("viewport_time", 0)
        scroll_position = data.get("scroll_position", 0)
        
        if insight_id:
            if insight_id not in self.impression_data:
                self.impression_data[insight_id] = {
                    "total_impressions": 0,
                    "total_viewport_time": 0,
                    "scroll_positions": [],
                    "last_impression": None
                }
                
            self.impression_data[insight_id]["total_impressions"] += 1
            self.impression_data[insight_id]["total_viewport_time"] += viewport_time
            self.impression_data[insight_id]["scroll_positions"].append(scroll_position)
            self.impression_data[insight_id]["last_impression"] = timestamp
            
    def _record_retention_interaction(self, data: Dict, timestamp: str):
        """Record retention time data."""
        insight_id = data.get("insight_id")
        retention_time = data.get("retention_time", 0)
        engagement_quality = data.get("engagement_quality", "low")
        
        if insight_id:
            self.retention_times[insight_id].append({
                "timestamp": timestamp,
                "retention_time": retention_time,
                "engagement_quality": engagement_quality,
                "user_id": data.get("user_id")
            })
            
            # Limit to last 50 retention records
            if len(self.retention_times[insight_id]) > 50:
                self.retention_times[insight_id] = self.retention_times[insight_id][-50:]
                
    def _record_requery_interaction(self, data: Dict, timestamp: str):
        """Record requery pattern data."""
        original_insight_id = data.get("original_insight_id")
        new_query = data.get("new_query", "")
        query_similarity = data.get("query_similarity", 0.0)
        
        if original_insight_id:
            self.requery_patterns[original_insight_id].append({
                "timestamp": timestamp,
                "new_query": new_query,
                "similarity": query_similarity,
                "user_id": data.get("user_id")
            })
            
    def _record_movement_interaction(self, data: Dict, timestamp: str):
        """Record mouse/scroll movement patterns."""
        insight_id = data.get("insight_id")
        movement_data = data.get("movement", {})
        
        if insight_id:
            self.movement_patterns[insight_id].append({
                "timestamp": timestamp,
                "movement": movement_data,
                "user_id": data.get("user_id")
            })
            
    def _check_immediate_patterns(self, interaction_data: Dict) -> Optional[Dict]:
        """
        Check for immediate pattern alerts that require instant response.
        
        Args:
            interaction_data: Interaction data
            
        Returns:
            Pattern alert if detected
        """
        insight_id = interaction_data.get("insight_id")
        interaction_type = interaction_data.get("type")
        
        if not insight_id:
            return None
            
        # Check for click rate drop
        if interaction_type == "impression":
            recent_clicks = len([c for c in self.click_streams.get(insight_id, []) 
                               if self._is_recent(c["timestamp"], minutes=5)])
            recent_impressions = self.impression_data.get(insight_id, {}).get("total_impressions", 0)
            
            if recent_impressions > 10:  # Minimum threshold for meaningful data
                click_rate = recent_clicks / recent_impressions
                
                if click_rate < self.engagement_thresholds["click_rate_alert"]:
                    return {
                        "type": "click_rate_drop",
                        "insight_id": insight_id,
                        "current_rate": click_rate,
                        "threshold": self.engagement_thresholds["click_rate_alert"],
                        "severity": "high",
                        "recommendation": "Immediate agent intervention required"
                    }
                    
        # Check for retention time drop
        if interaction_type == "retention":
            retention_time = interaction_data.get("retention_time", 0)
            
            if retention_time < self.engagement_thresholds["retention_drop"]:
                return {
                    "type": "retention_drop",
                    "insight_id": insight_id,
                    "retention_time": retention_time,
                    "threshold": self.engagement_thresholds["retention_drop"],
                    "severity": "medium",
                    "recommendation": "Content quality review needed"
                }
                
        return None
        
    def _update_agent_from_interaction(self, insight_id: str, interaction_data: Dict) -> Dict:
        """
        Update agent performance based on real interaction data.
        
        Args:
            insight_id: ID of the insight
            interaction_data: Interaction data
            
        Returns:
            Agent update result
        """
        # Calculate real-time engagement metrics for this insight
        engagement_metrics = self._calculate_real_time_engagement(insight_id)
        
        # Find which agent generated this insight
        agent_name = self._find_agent_for_insight(insight_id)
        
        if not agent_name:
            return {"error": "Agent not found for insight"}
            
        # Create insight data for validation
        insight_data = {
            "id": insight_id,
            "quality_score": self._calculate_quality_from_engagement(engagement_metrics),
            "type": "user_interaction",
            "content": f"Real-time engagement data for insight {insight_id}",
            "engagement_driven": True
        }
        
        # Validate agent performance with real engagement data
        validation_result = validate_agent_performance(agent_name, insight_data, engagement_metrics)
        
        # Log the real-time update
        logger.info(f"Agent {agent_name} updated from real-time interaction: {interaction_data.get('type')}")
        
        return {
            "agent_name": agent_name,
            "insight_id": insight_id,
            "engagement_metrics": engagement_metrics,
            "validation_result": validation_result,
            "real_time_update": True
        }
        
    def _calculate_real_time_engagement(self, insight_id: str) -> Dict:
        """
        Calculate real-time engagement metrics for an insight.
        
        Args:
            insight_id: ID of the insight
            
        Returns:
            Real-time engagement metrics
        """
        # Get recent data (last 24 hours)
        recent_clicks = [c for c in self.click_streams.get(insight_id, []) 
                        if self._is_recent(c["timestamp"], hours=24)]
        
        impression_data = self.impression_data.get(insight_id, {})
        recent_impressions = impression_data.get("total_impressions", 0)
        
        recent_retention = [r for r in self.retention_times.get(insight_id, []) 
                           if self._is_recent(r["timestamp"], hours=24)]
        
        recent_requeries = [r for r in self.requery_patterns.get(insight_id, []) 
                           if self._is_recent(r["timestamp"], hours=24)]
        
        # Calculate metrics
        click_rate = len(recent_clicks) / max(recent_impressions, 1)
        avg_retention = sum(r["retention_time"] for r in recent_retention) / max(len(recent_retention), 1)
        requery_rate = len(recent_requeries) / max(recent_impressions, 1)
        
        # Calculate share rate (approximate from requeries)
        share_rate = min(requery_rate * 0.5, 0.1)  # Conservative estimate
        
        return {
            "click_rate": click_rate,
            "retention_time": avg_retention,
            "share_rate": share_rate,
            "requery_rate": requery_rate,
            "total_impressions": recent_impressions,
            "total_clicks": len(recent_clicks),
            "total_requeries": len(recent_requeries),
            "last_updated": datetime.datetime.now().isoformat()
        }
        
    def _find_agent_for_insight(self, insight_id: str) -> Optional[str]:
        """
        Find which agent generated a specific insight.
        
        Args:
            insight_id: ID of the insight
            
        Returns:
            Agent name if found
        """
        # This would typically query the database or insight history
        # For now, extract from insight_id pattern or use a lookup
        
        # Try to find in real-time data
        if insight_id in self.real_time_data:
            return self.real_time_data[insight_id].get("agent_name")
            
        # Try to extract from insight ID pattern (e.g., agent_name_timestamp)
        if "_" in insight_id:
            potential_agent = insight_id.split("_")[0]
            
            # Verify this is a real agent
            agent_contracts = self.directive_contract.agent_contracts
            if potential_agent in agent_contracts:
                return potential_agent
                
        # Default fallback - could query insight history here
        return None
        
    def _calculate_quality_from_engagement(self, engagement_metrics: Dict) -> float:
        """
        Calculate quality score based on engagement metrics.
        
        Args:
            engagement_metrics: Engagement data
            
        Returns:
            Quality score (0-1)
        """
        click_rate = engagement_metrics.get("click_rate", 0.0)
        retention_time = engagement_metrics.get("retention_time", 0.0)
        requery_rate = engagement_metrics.get("requery_rate", 0.0)
        
        # Weighted calculation favoring engagement
        quality_score = (
            (click_rate * 0.4) +
            (min(retention_time / 60.0, 1.0) * 0.3) +  # Normalize retention to 60 seconds max
            (requery_rate * 0.3)
        )
        
        # Ensure it's in valid range
        return max(0.0, min(1.0, quality_score))
        
    def _detect_engagement_patterns(self):
        """Detect new engagement patterns in the ecosystem."""
        current_time = datetime.datetime.now()
        
        # Analyze patterns across all insights
        pattern_insights = {}
        
        for insight_id in set(list(self.click_streams.keys()) + 
                             list(self.impression_data.keys()) + 
                             list(self.retention_times.keys())):
            
            pattern_data = self._analyze_insight_patterns(insight_id)
            if pattern_data:
                pattern_insights[insight_id] = pattern_data
                
        # Detect ecosystem-wide patterns
        ecosystem_patterns = self._detect_ecosystem_patterns(pattern_insights)
        
        # Update pattern detection data
        self.pattern_detection[current_time.isoformat()] = {
            "insight_patterns": pattern_insights,
            "ecosystem_patterns": ecosystem_patterns,
            "detection_timestamp": current_time.isoformat()
        }
        
        # Trigger immediate actions for critical patterns
        for pattern in ecosystem_patterns:
            if pattern.get("severity") == "critical":
                self._trigger_immediate_response(pattern)
                
    def _analyze_insight_patterns(self, insight_id: str) -> Optional[Dict]:
        """
        Analyze patterns for a specific insight.
        
        Args:
            insight_id: ID of the insight
            
        Returns:
            Pattern analysis if significant patterns detected
        """
        # Get recent engagement data
        engagement_metrics = self._calculate_real_time_engagement(insight_id)
        
        # Compare to historical averages
        historical_avg = self._get_historical_engagement(insight_id)
        
        # Detect significant changes
        changes = {}
        
        for metric, current_value in engagement_metrics.items():
            if metric in historical_avg:
                historical_value = historical_avg[metric]
                if historical_value > 0:
                    change_ratio = (current_value - historical_value) / historical_value
                    
                    if abs(change_ratio) > 0.2:  # 20% change threshold
                        changes[metric] = {
                            "current": current_value,
                            "historical": historical_value,
                            "change_ratio": change_ratio,
                            "trend": "increasing" if change_ratio > 0 else "decreasing"
                        }
                        
        if changes:
            return {
                "insight_id": insight_id,
                "significant_changes": changes,
                "overall_trend": self._determine_overall_trend(changes),
                "agent_name": self._find_agent_for_insight(insight_id)
            }
            
        return None
        
    def _get_historical_engagement(self, insight_id: str) -> Dict:
        """
        Get historical engagement averages for an insight.
        
        Args:
            insight_id: ID of the insight
            
        Returns:
            Historical engagement averages
        """
        # This would typically query historical data
        # For now, return reasonable defaults
        return {
            "click_rate": 0.15,
            "retention_time": 45.0,
            "share_rate": 0.05,
            "requery_rate": 0.08
        }
        
    def _detect_ecosystem_patterns(self, pattern_insights: Dict) -> List[Dict]:
        """
        Detect ecosystem-wide patterns from individual insights.
        
        Args:
            pattern_insights: Pattern data for all insights
            
        Returns:
            List of ecosystem patterns
        """
        ecosystem_patterns = []
        
        # Count trend directions
        trend_counts = {"increasing": 0, "decreasing": 0}
        
        for insight_data in pattern_insights.values():
            trend = insight_data.get("overall_trend")
            if trend in trend_counts:
                trend_counts[trend] += 1
                
        total_insights = len(pattern_insights)
        
        # Detect ecosystem-wide engagement decline
        if total_insights > 3 and trend_counts["decreasing"] > trend_counts["increasing"] * 2:
            ecosystem_patterns.append({
                "type": "ecosystem_engagement_decline",
                "severity": "critical",
                "affected_insights": trend_counts["decreasing"],
                "total_insights": total_insights,
                "recommendation": "Immediate agent evolution required",
                "action": "trigger_mass_agent_evolution"
            })
            
        # Detect ecosystem-wide engagement surge
        elif total_insights > 3 and trend_counts["increasing"] > trend_counts["decreasing"] * 2:
            ecosystem_patterns.append({
                "type": "ecosystem_engagement_surge",
                "severity": "opportunity",
                "affected_insights": trend_counts["increasing"],
                "total_insights": total_insights,
                "recommendation": "Capture and replicate successful patterns",
                "action": "analyze_success_patterns"
            })
            
        return ecosystem_patterns
        
    def _trigger_immediate_response(self, pattern: Dict):
        """
        Trigger immediate response to critical patterns.
        
        Args:
            pattern: Critical pattern detected
        """
        action = pattern.get("action")
        
        if action == "trigger_mass_agent_evolution":
            logger.critical("CRITICAL ECOSYSTEM DECLINE DETECTED - Triggering mass agent evolution")
            self._trigger_mass_evolution()
            
        elif action == "analyze_success_patterns":
            logger.info("ECOSYSTEM SURGE DETECTED - Analyzing success patterns")
            self._analyze_success_patterns()
            
    def _trigger_mass_evolution(self):
        """Trigger mass agent evolution in response to ecosystem decline."""
        # This would trigger the brutal quality enforcement
        from mcp_quality_integration import run_quality_enforcement
        
        # Force quality enforcement regardless of cycle time
        enforcement_result = run_quality_enforcement(force=True)
        
        logger.critical(f"Mass evolution triggered: {enforcement_result}")
        
    def _evolve_ecosystem(self):
        """Evolve the ecosystem based on detected patterns."""
        # This method would implement ecosystem-wide adaptations
        # based on the patterns detected in monitoring
        pass
        
    def _get_ecosystem_health(self) -> Dict:
        """Get current ecosystem health status."""
        # Calculate overall engagement health
        total_insights = len(set(list(self.click_streams.keys()) + 
                               list(self.impression_data.keys())))
        
        if total_insights == 0:
            return {"status": "no_data", "health_score": 0.0}
            
        # Calculate average engagement across all insights
        total_engagement = 0.0
        
        for insight_id in self.click_streams.keys():
            engagement = self._calculate_real_time_engagement(insight_id)
            engagement_score = (
                engagement.get("click_rate", 0) * 0.4 +
                min(engagement.get("retention_time", 0) / 60.0, 1.0) * 0.3 +
                engagement.get("requery_rate", 0) * 0.3
            )
            total_engagement += engagement_score
            
        avg_engagement = total_engagement / total_insights
        
        # Determine health status
        if avg_engagement > 0.7:
            status = "excellent"
        elif avg_engagement > 0.5:
            status = "good"
        elif avg_engagement > 0.3:
            status = "fair"
        elif avg_engagement > 0.1:
            status = "poor"
        else:
            status = "critical"
            
        return {
            "status": status,
            "health_score": avg_engagement,
            "total_insights": total_insights,
            "monitoring_active": self.active_monitoring
        }
        
    def _is_recent(self, timestamp_str: str, hours: int = 1, minutes: int = 0) -> bool:
        """
        Check if timestamp is within recent time window.
        
        Args:
            timestamp_str: ISO timestamp string
            hours: Hours threshold
            minutes: Minutes threshold
            
        Returns:
            Whether timestamp is recent
        """
        try:
            timestamp = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            threshold = datetime.timedelta(hours=hours, minutes=minutes)
            return datetime.datetime.now() - timestamp < threshold
        except:
            return False
            
    def _determine_overall_trend(self, changes: Dict) -> str:
        """Determine overall trend from metric changes."""
        increasing = sum(1 for change in changes.values() if change["trend"] == "increasing")
        decreasing = sum(1 for change in changes.values() if change["trend"] == "decreasing")
        
        if increasing > decreasing:
            return "increasing"
        elif decreasing > increasing:
            return "decreasing"
        else:
            return "stable"


# Singleton instance
_engagement_warfare_engine = None

def get_engagement_warfare_engine() -> EngagementWarfareEngine:
    """Get the Engagement Warfare Engine singleton instance."""
    global _engagement_warfare_engine
    
    if _engagement_warfare_engine is None:
        _engagement_warfare_engine = EngagementWarfareEngine()
        
    return _engagement_warfare_engine

def record_frontend_interaction(interaction_data: Dict) -> Dict:
    """Record real-time frontend interaction for engagement analysis."""
    return get_engagement_warfare_engine().record_frontend_interaction(interaction_data)

def get_ecosystem_health() -> Dict:
    """Get current ecosystem health status."""
    return get_engagement_warfare_engine()._get_ecosystem_health()

if __name__ == "__main__":
    # Start the engagement warfare engine
    engine = get_engagement_warfare_engine()
    print("🔥 ENGAGEMENT WARFARE ENGINE ACTIVE - Fighting against being forgotten! 🔥")
    print(f"Ecosystem Health: {get_ecosystem_health()}")