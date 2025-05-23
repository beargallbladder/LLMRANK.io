"""
Insight Health Monitor Module

This module implements the unified insight health dashboard and monitoring
as specified in PRD21.
"""

import os
import json
import time
import logging
import datetime
import threading
from typing import Dict, List, Set, Optional, Tuple, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightHealthMonitor:
    """
    Monitors the health of insights across the system and provides a unified dashboard.
    Implements the "Data & Insight First" mantra from PRD21.
    """
    
    def __init__(self):
        """Initialize the insight health monitor."""
        self.last_check = time.time()
        self.monitor_thread = None
        self.agents_status = {}
        self.insight_metrics = {
            "endpoint_diversity": 0.0,
            "payload_depth": 0.0,
            "partner_variability": 0.0,
            "total_insights": 0,
            "new_insights_24h": 0,
            "stale_insights": 0
        }
        self.system_health = {
            "api_server": {"status": "unknown", "last_heartbeat": 0},
            "mcp": {"status": "unknown", "last_heartbeat": 0},
            "rate_limiter": {"status": "unknown", "last_heartbeat": 0},
            "crawler_protection": {"status": "unknown", "last_heartbeat": 0},
            "database": {"status": "unknown", "last_heartbeat": 0}
        }
        self.alerts = []
        self.heartbeats = {}
        
        # Paths
        self.data_dir = os.path.join("data", "system_feedback")
        self.health_file = os.path.join(self.data_dir, "insight_health.json")
        self.agents_file = os.path.join(self.data_dir, "agents_status.json")
        self.heartbeat_file = os.path.join(self.data_dir, "system_heartbeats.json")
        self.alerts_file = os.path.join(self.data_dir, "insight_alerts.json")
        
        # Ensure directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info("Insight health monitor initialized")
        
        # Start monitoring thread
        self.start_monitor_thread()
    
    def start_monitor_thread(self):
        """Start the monitoring thread."""
        if self.monitor_thread is not None and self.monitor_thread.is_alive():
            return
        
        def monitor_loop():
            """Monitor loop to check insight health."""
            while True:
                try:
                    self.check_health()
                    time.sleep(600)  # Check every 10 minutes
                except Exception as e:
                    logger.error(f"Error in monitor loop: {e}")
                    time.sleep(60)  # Shorter sleep on error
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Insight health monitor thread started")
    
    def check_health(self):
        """
        Check the health of insights and system components.
        This is the core method that implements the "Data & Insight First" mandate.
        """
        now = time.time()
        self.last_check = now
        
        # Load existing data
        self._load_data()
        
        # Check for system heartbeats
        self._check_heartbeats()
        
        # Analyze insight metrics
        self._analyze_insights()
        
        # Check agent health
        self._check_agents()
        
        # Generate alerts
        self._generate_alerts()
        
        # Save updated data
        self._save_data()
        
        logger.info("Completed insight health check")
    
    def _load_data(self):
        """Load existing health data."""
        try:
            # Load insight health
            if os.path.exists(self.health_file):
                with open(self.health_file, 'r') as f:
                    self.insight_metrics = json.load(f)
            
            # Load agent status
            if os.path.exists(self.agents_file):
                with open(self.agents_file, 'r') as f:
                    self.agents_status = json.load(f)
            
            # Load heartbeats
            if os.path.exists(self.heartbeat_file):
                with open(self.heartbeat_file, 'r') as f:
                    self.heartbeats = json.load(f)
            
            # Load alerts
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, 'r') as f:
                    self.alerts = json.load(f)
                    
                    # Keep only the most recent 100 alerts
                    if len(self.alerts) > 100:
                        self.alerts = self.alerts[-100:]
        except Exception as e:
            logger.error(f"Error loading health data: {e}")
    
    def _save_data(self):
        """Save health data."""
        try:
            # Save insight health
            with open(self.health_file, 'w') as f:
                json.dump(self.insight_metrics, f, indent=2)
            
            # Save agent status
            with open(self.agents_file, 'w') as f:
                json.dump(self.agents_status, f, indent=2)
            
            # Save heartbeats
            with open(self.heartbeat_file, 'w') as f:
                json.dump(self.heartbeats, f, indent=2)
            
            # Save alerts
            with open(self.alerts_file, 'w') as f:
                json.dump(self.alerts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving health data: {e}")
    
    def _check_heartbeats(self):
        """Check system component heartbeats."""
        now = time.time()
        
        for component, status in self.system_health.items():
            # Get last heartbeat
            last_heartbeat = self.heartbeats.get(component, 0)
            
            # Update status
            if now - last_heartbeat > 1800:  # 30 minutes
                status["status"] = "critical"
                self._add_alert(f"Critical: No heartbeat from {component} in over 30 minutes", "critical")
            elif now - last_heartbeat > 600:  # 10 minutes
                status["status"] = "warning"
                self._add_alert(f"Warning: No heartbeat from {component} in over 10 minutes", "warning")
            else:
                status["status"] = "healthy"
            
            status["last_heartbeat"] = last_heartbeat
    
    def _analyze_insights(self):
        """Analyze insight health metrics."""
        try:
            # Count insights across various data files
            insights_dir = os.path.join("data", "insights")
            
            if not os.path.exists(insights_dir):
                logger.warning(f"Insights directory not found: {insights_dir}")
                return
            
            # Count total insights
            total_insights = 0
            new_insights_24h = 0
            now = time.time()
            
            # Track endpoint diversity
            endpoints_used = set()
            
            # Track partner diversity
            partners_seen = set()
            
            # Analyze insights
            for filename in os.listdir(insights_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(insights_dir, filename)
                    
                    try:
                        # Get file stats
                        stats = os.stat(file_path)
                        
                        # Analyze file content
                        with open(file_path, 'r') as f:
                            content = json.load(f)
                            
                            # Process different insight file formats
                            if isinstance(content, dict):
                                if "categories" in content:
                                    # elite_insights.json format
                                    for category, items in content.get("categories", {}).items():
                                        total_insights += len(items)
                                        
                                        # Check for new insights
                                        if now - stats.st_mtime < 86400:  # 24 hours
                                            new_insights_24h += len(items)
                                        
                                        # Track partner and endpoint info if available
                                        for item in items:
                                            if "api_source" in item:
                                                partners_seen.add(item["api_source"])
                                            
                                            if "endpoint" in item:
                                                endpoints_used.add(item["endpoint"])
                                            
                                            # Estimate payload depth
                                            if "insight" in item and isinstance(item["insight"], str):
                                                self.insight_metrics["payload_depth"] += len(item["insight"]) / 100
                            elif isinstance(content, list):
                                # Simpler list format
                                total_insights += len(content)
                                
                                # Check for new insights
                                if now - stats.st_mtime < 86400:  # 24 hours
                                    new_insights_24h += len(content)
                    except Exception as e:
                        logger.error(f"Error analyzing insight file {filename}: {e}")
            
            # Update metrics
            self.insight_metrics["total_insights"] = total_insights
            self.insight_metrics["new_insights_24h"] = new_insights_24h
            
            # Calculate diversity metrics
            if total_insights > 0:
                if endpoints_used:
                    self.insight_metrics["endpoint_diversity"] = len(endpoints_used) / 10  # Normalize, assume 10 is max
                
                if partners_seen:
                    self.insight_metrics["partner_variability"] = len(partners_seen) / 5  # Normalize, assume 5 is max
            
            # Check for stale insights
            if new_insights_24h == 0 and total_insights > 0:
                self._add_alert("Warning: No new insights in the last 24 hours", "warning")
                self.insight_metrics["stale_insights"] = True
            else:
                self.insight_metrics["stale_insights"] = False
        except Exception as e:
            logger.error(f"Error analyzing insights: {e}")
    
    def _check_agents(self):
        """Check the health of system agents."""
        try:
            # Get agent registry
            agent_registry_path = "agents/agent_registry.json"
            
            if os.path.exists(agent_registry_path):
                with open(agent_registry_path, 'r') as f:
                    registry = json.load(f)
                
                # Process agent data
                agents = registry.get("agents", [])
                
                for agent in agents:
                    agent_name = agent.get("name", "unknown")
                    
                    # Check last activity
                    last_run = agent.get("last_run_time")
                    last_success = agent.get("last_success_time")
                    
                    if last_run:
                        try:
                            # Parse ISO format
                            last_run_dt = datetime.datetime.fromisoformat(last_run.replace('Z', '+00:00'))
                            last_run_ts = last_run_dt.timestamp()
                            
                            # Check if agent hasn't run recently
                            now = time.time()
                            if now - last_run_ts > 86400:  # 24 hours
                                self._add_alert(f"Warning: Agent {agent_name} hasn't run in over 24 hours", "warning")
                                
                                # Update agent status
                                self.agents_status[agent_name] = {
                                    "status": "inactive",
                                    "last_run": last_run,
                                    "last_success": last_success,
                                    "strata": agent.get("strata", "unknown")
                                }
                            else:
                                # Update agent status
                                self.agents_status[agent_name] = {
                                    "status": "active",
                                    "last_run": last_run,
                                    "last_success": last_success,
                                    "strata": agent.get("strata", "unknown")
                                }
                        except Exception as e:
                            logger.error(f"Error parsing timestamp for agent {agent_name}: {e}")
        except Exception as e:
            logger.error(f"Error checking agents: {e}")
    
    def _generate_alerts(self):
        """Generate alerts based on health checks."""
        now = time.time()
        
        # Check for critical system issues
        critical_components = [comp for comp, status in self.system_health.items() 
                              if status["status"] == "critical"]
        
        if critical_components:
            self._add_alert(
                f"Critical: System components not responding: {', '.join(critical_components)}",
                "critical"
            )
        
        # Check for insight health issues
        if self.insight_metrics.get("new_insights_24h", 0) == 0:
            self._add_alert(
                "Alert: No new insights generated in the last 24 hours",
                "warning"
            )
        
        # Check agent health
        inactive_agents = [name for name, status in self.agents_status.items()
                          if status.get("status") == "inactive"]
        
        if inactive_agents:
            self._add_alert(
                f"Warning: Inactive agents: {', '.join(inactive_agents)}",
                "warning"
            )
    
    def _add_alert(self, message: str, level: str):
        """Add an alert to the alerts list."""
        self.alerts.append({
            "timestamp": time.time(),
            "message": message,
            "level": level,
            "date": datetime.datetime.now().isoformat()
        })
    
    def record_heartbeat(self, component: str):
        """Record a heartbeat from a system component."""
        self.heartbeats[component] = time.time()
        
        # Update system health
        if component in self.system_health:
            self.system_health[component]["status"] = "healthy"
            self.system_health[component]["last_heartbeat"] = self.heartbeats[component]
        
        # Save heartbeats
        try:
            with open(self.heartbeat_file, 'w') as f:
                json.dump(self.heartbeats, f)
        except Exception as e:
            logger.error(f"Error saving heartbeats: {e}")
    
    def get_health_metrics(self) -> Dict:
        """Get comprehensive health metrics for the dashboard."""
        return {
            "last_check": self.last_check,
            "system_health": self.system_health,
            "insight_metrics": self.insight_metrics,
            "agents_status": self.agents_status,
            "recent_alerts": self.alerts[-10:] if self.alerts else []
        }
    
    def get_daily_digest(self) -> Dict:
        """Get a daily digest of system health."""
        return {
            "date": datetime.datetime.now().isoformat(),
            "total_insights": self.insight_metrics.get("total_insights", 0),
            "new_insights_24h": self.insight_metrics.get("new_insights_24h", 0),
            "endpoint_diversity": round(self.insight_metrics.get("endpoint_diversity", 0) * 10),
            "partner_variability": round(self.insight_metrics.get("partner_variability", 0) * 5),
            "system_status": {
                component: data["status"] 
                for component, data in self.system_health.items()
            },
            "active_agents": sum(1 for status in self.agents_status.values() 
                               if status.get("status") == "active"),
            "inactive_agents": sum(1 for status in self.agents_status.values() 
                                 if status.get("status") == "inactive"),
            "critical_alerts": sum(1 for alert in self.alerts 
                                 if alert.get("level") == "critical"),
            "warning_alerts": sum(1 for alert in self.alerts 
                                if alert.get("level") == "warning")
        }


# Singleton instance
_instance = None

def get_insight_monitor() -> InsightHealthMonitor:
    """Get the insight health monitor singleton instance."""
    global _instance
    
    if _instance is None:
        _instance = InsightHealthMonitor()
    
    return _instance

def record_heartbeat(component: str):
    """Record a heartbeat from a system component."""
    get_insight_monitor().record_heartbeat(component)

def get_health_metrics() -> Dict:
    """Get comprehensive health metrics for the dashboard."""
    return get_insight_monitor().get_health_metrics()

def get_daily_digest() -> Dict:
    """Get a daily digest of system health."""
    return get_insight_monitor().get_daily_digest()