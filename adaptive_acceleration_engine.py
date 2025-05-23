"""
Adaptive Acceleration Engine
Codename: "Pedal to the Metal"

This engine dynamically accelerates domain processing by monitoring system performance,
auto-hiring agents when quality is high, and throttling when systems struggle.
"""

import os
import json
import logging
import datetime
import threading
import time
import asyncio
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

from cookie_economy import get_cookie_economy
from agent_directive_contract import get_agent_directive_contract
from engagement_warfare_engine import get_engagement_warfare_engine
import agent_survival_loop

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File paths
DATA_DIR = "data/acceleration"
os.makedirs(DATA_DIR, exist_ok=True)

ACCELERATION_LOG_PATH = os.path.join(DATA_DIR, "acceleration_log.json")
PERFORMANCE_METRICS_PATH = os.path.join(DATA_DIR, "performance_metrics.json")
AGENT_SCALING_PATH = os.path.join(DATA_DIR, "agent_scaling.json")


class AdaptiveAccelerationEngine:
    """
    Dynamic acceleration system that monitors performance and scales agents
    automatically to maximize throughput while maintaining quality.
    """
    
    def __init__(self):
        """Initialize the Adaptive Acceleration Engine."""
        self.acceleration_log = []
        self.performance_metrics = {}
        self.agent_scaling = {}
        self.active_agents = {}
        self.processing_queue = queue.Queue()
        self.system_health = {"cpu": 0, "memory": 0, "quality": 0}
        self.acceleration_active = False
        
        # Dynamic scaling parameters
        self.base_agent_count = 5
        self.max_agent_count = 100
        self.min_agent_count = 2
        self.current_agent_count = self.base_agent_count
        
        # Performance thresholds
        self.thresholds = {
            "quality_minimum": 0.7,      # Minimum quality to maintain acceleration
            "quality_excellent": 0.9,    # Quality level to increase agents
            "cpu_limit": 80,             # CPU percentage limit
            "memory_limit": 85,          # Memory percentage limit
            "success_rate_minimum": 0.6, # Minimum success rate
            "engagement_minimum": 0.3    # Minimum engagement rate
        }
        
        # Acceleration strategies
        self.strategies = {
            "conservative": {"multiplier": 1.2, "risk": "low"},
            "aggressive": {"multiplier": 2.0, "risk": "medium"},
            "blitz": {"multiplier": 5.0, "risk": "high"}
        }
        
        self.current_strategy = "conservative"
        
        # Initialize systems
        self.cookie_economy = get_cookie_economy()
        self.directive_contract = get_agent_directive_contract()
        self.engagement_engine = get_engagement_warfare_engine()
        
        # Load existing data
        self._load_data()
        
        logger.info("🚀 ADAPTIVE ACCELERATION ENGINE INITIALIZED - Ready to go pedal to the metal!")
        
    def _load_data(self):
        """Load existing acceleration data."""
        try:
            if os.path.exists(ACCELERATION_LOG_PATH):
                with open(ACCELERATION_LOG_PATH, 'r') as f:
                    self.acceleration_log = json.load(f)
                    
            if os.path.exists(PERFORMANCE_METRICS_PATH):
                with open(PERFORMANCE_METRICS_PATH, 'r') as f:
                    self.performance_metrics = json.load(f)
                    
            if os.path.exists(AGENT_SCALING_PATH):
                with open(AGENT_SCALING_PATH, 'r') as f:
                    self.agent_scaling = json.load(f)
                    
            logger.info("Acceleration data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading acceleration data: {e}")
            
    def _save_data(self):
        """Save acceleration data."""
        try:
            with open(ACCELERATION_LOG_PATH, 'w') as f:
                json.dump(self.acceleration_log, f, indent=2)
                
            with open(PERFORMANCE_METRICS_PATH, 'w') as f:
                json.dump(self.performance_metrics, f, indent=2)
                
            with open(AGENT_SCALING_PATH, 'w') as f:
                json.dump(self.agent_scaling, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving acceleration data: {e}")
            
    def start_acceleration(self, target_domains_per_hour: int = 50, strategy: str = "aggressive"):
        """
        Start adaptive acceleration to target domains per hour.
        
        Args:
            target_domains_per_hour: Target processing rate
            strategy: Acceleration strategy (conservative, aggressive, blitz)
        """
        self.target_rate = target_domains_per_hour
        self.current_strategy = strategy
        self.acceleration_active = True
        
        # Start monitoring thread
        monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitoring_thread.start()
        
        # Start processing thread
        processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        processing_thread.start()
        
        logger.warning(f"🔥 ACCELERATION STARTED: {target_domains_per_hour}/hour using {strategy} strategy")
        
        return {
            "status": "acceleration_started",
            "target_rate": target_domains_per_hour,
            "strategy": strategy,
            "initial_agent_count": self.current_agent_count
        }
        
    def _monitoring_loop(self):
        """Main monitoring loop for adaptive acceleration."""
        while self.acceleration_active:
            try:
                # Monitor system performance
                system_metrics = self._get_system_metrics()
                
                # Monitor quality metrics
                quality_metrics = self._get_quality_metrics()
                
                # Monitor engagement metrics
                engagement_metrics = self._get_engagement_metrics()
                
                # Make acceleration decisions
                scaling_decision = self._make_scaling_decision(system_metrics, quality_metrics, engagement_metrics)
                
                # Apply scaling decision
                if scaling_decision["action"] != "maintain":
                    self._apply_scaling_decision(scaling_decision)
                
                # Log performance
                self._log_performance(system_metrics, quality_metrics, engagement_metrics, scaling_decision)
                
                # Check every 30 seconds
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
                
    def _processing_loop(self):
        """Main processing loop for domain acceleration."""
        while self.acceleration_active:
            try:
                # Get domains to process
                domains_batch = self._get_domains_batch()
                
                if domains_batch:
                    # Process batch with current agent count
                    self._process_domains_batch(domains_batch)
                else:
                    # No domains available, wait
                    time.sleep(10)
                    
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(30)
                
    def _get_system_metrics(self) -> Dict:
        """Get current system performance metrics."""
        try:
            # Simulate system metrics (in real implementation, use psutil)
            import random
            
            # Simulate based on current load
            base_cpu = min(30 + (self.current_agent_count * 2), 95)
            base_memory = min(40 + (self.current_agent_count * 1.5), 90)
            
            # Add some variance
            cpu_usage = max(0, min(100, base_cpu + random.uniform(-10, 10)))
            memory_usage = max(0, min(100, base_memory + random.uniform(-5, 15)))
            
            return {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "active_agents": self.current_agent_count,
                "queue_size": self.processing_queue.qsize(),
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"cpu_usage": 50, "memory_usage": 50, "active_agents": self.current_agent_count}
            
    def _get_quality_metrics(self) -> Dict:
        """Get current quality metrics from brutal enforcement system."""
        try:
            # Get recent agent performance
            recent_quality_scores = []
            recent_engagement_scores = []
            
            for agent_name, agent_data in self.cookie_economy.agent_performance.items():
                avg_quality = agent_data.get("average_quality", 0.0)
                if avg_quality > 0:
                    recent_quality_scores.append(avg_quality)
                    
            # Get engagement scores from engagement warfare engine
            ecosystem_health = self.engagement_engine._get_ecosystem_health()
            
            avg_quality = sum(recent_quality_scores) / len(recent_quality_scores) if recent_quality_scores else 0.5
            engagement_score = ecosystem_health.get("health_score", 0.0)
            
            return {
                "average_quality": avg_quality,
                "engagement_score": engagement_score,
                "quality_agents_count": len(recent_quality_scores),
                "quality_trend": self._calculate_quality_trend(),
                "engagement_trend": self._calculate_engagement_trend()
            }
        except Exception as e:
            logger.error(f"Error getting quality metrics: {e}")
            return {"average_quality": 0.5, "engagement_score": 0.3}
            
    def _get_engagement_metrics(self) -> Dict:
        """Get current engagement metrics from warfare engine."""
        try:
            ecosystem_health = self.engagement_engine._get_ecosystem_health()
            
            return {
                "health_score": ecosystem_health.get("health_score", 0.0),
                "total_insights": ecosystem_health.get("total_insights", 0),
                "monitoring_active": ecosystem_health.get("monitoring_active", False)
            }
        except Exception as e:
            logger.error(f"Error getting engagement metrics: {e}")
            return {"health_score": 0.3, "total_insights": 0}
            
    def _make_scaling_decision(self, system_metrics: Dict, quality_metrics: Dict, engagement_metrics: Dict) -> Dict:
        """
        Make intelligent scaling decision based on all metrics.
        
        Args:
            system_metrics: System performance data
            quality_metrics: Quality and engagement data
            engagement_metrics: Real-time engagement data
            
        Returns:
            Scaling decision
        """
        cpu_usage = system_metrics.get("cpu_usage", 50)
        memory_usage = system_metrics.get("memory_usage", 50)
        avg_quality = quality_metrics.get("average_quality", 0.5)
        engagement_score = engagement_metrics.get("health_score", 0.3)
        
        decision = {
            "action": "maintain",
            "new_agent_count": self.current_agent_count,
            "reason": "Monitoring",
            "confidence": 0.5
        }
        
        # SCALE DOWN conditions (system struggling)
        if cpu_usage > self.thresholds["cpu_limit"]:
            decision = {
                "action": "scale_down",
                "new_agent_count": max(self.min_agent_count, int(self.current_agent_count * 0.7)),
                "reason": f"CPU overload: {cpu_usage}%",
                "confidence": 0.9
            }
        elif memory_usage > self.thresholds["memory_limit"]:
            decision = {
                "action": "scale_down", 
                "new_agent_count": max(self.min_agent_count, int(self.current_agent_count * 0.8)),
                "reason": f"Memory overload: {memory_usage}%",
                "confidence": 0.9
            }
        elif avg_quality < self.thresholds["quality_minimum"]:
            decision = {
                "action": "scale_down",
                "new_agent_count": max(self.min_agent_count, int(self.current_agent_count * 0.6)),
                "reason": f"Quality below minimum: {avg_quality:.2f}",
                "confidence": 0.95
            }
            
        # SCALE UP conditions (system performing well)
        elif (avg_quality > self.thresholds["quality_excellent"] and 
              engagement_score > self.thresholds["engagement_minimum"] and
              cpu_usage < 60 and memory_usage < 70):
            
            multiplier = self.strategies[self.current_strategy]["multiplier"]
            new_count = min(self.max_agent_count, int(self.current_agent_count * multiplier))
            
            decision = {
                "action": "scale_up",
                "new_agent_count": new_count,
                "reason": f"Excellent performance: Q={avg_quality:.2f}, E={engagement_score:.2f}",
                "confidence": 0.8
            }
            
        # MODERATE SCALE UP (good performance, room to grow)
        elif (avg_quality > 0.8 and engagement_score > 0.4 and 
              cpu_usage < 70 and memory_usage < 75):
            
            new_count = min(self.max_agent_count, self.current_agent_count + 2)
            
            decision = {
                "action": "scale_up",
                "new_agent_count": new_count,
                "reason": f"Good performance with capacity: Q={avg_quality:.2f}",
                "confidence": 0.6
            }
            
        return decision
        
    def _apply_scaling_decision(self, decision: Dict):
        """Apply the scaling decision by hiring/firing agents."""
        new_count = decision["new_agent_count"]
        action = decision["action"]
        reason = decision["reason"]
        
        if new_count == self.current_agent_count:
            return
            
        if action == "scale_up":
            agents_to_add = new_count - self.current_agent_count
            self._hire_agents(agents_to_add, reason)
            logger.info(f"🚀 SCALING UP: Added {agents_to_add} agents. Total: {new_count}. Reason: {reason}")
            
        elif action == "scale_down":
            agents_to_remove = self.current_agent_count - new_count
            self._fire_agents(agents_to_remove, reason)
            logger.warning(f"⚡ SCALING DOWN: Removed {agents_to_remove} agents. Total: {new_count}. Reason: {reason}")
            
        self.current_agent_count = new_count
        
        # Record scaling event
        scaling_event = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "agents_before": self.current_agent_count,
            "agents_after": new_count,
            "reason": reason,
            "confidence": decision.get("confidence", 0.5)
        }
        
        self.acceleration_log.append(scaling_event)
        self._save_data()
        
    def _hire_agents(self, count: int, reason: str):
        """Hire new agents for acceleration."""
        for i in range(count):
            agent_name = f"accel_agent_{datetime.datetime.now().strftime('%H%M%S')}_{i}"
            
            # Register agent with directive contract
            self.directive_contract.register_agent_contract(
                agent_name=agent_name,
                domain="auto_discovery",
                insight_type="comparative_insight"
            )
            
            # Add to active agents
            self.active_agents[agent_name] = {
                "created": datetime.datetime.now().isoformat(),
                "reason": reason,
                "status": "active",
                "domains_processed": 0
            }
            
    def _fire_agents(self, count: int, reason: str):
        """Fire agents to reduce load."""
        # Fire the newest agents first
        agents_to_fire = list(self.active_agents.keys())[-count:]
        
        for agent_name in agents_to_fire:
            # Mark as terminated in directive contract
            if agent_name in self.directive_contract.agent_contracts:
                self.directive_contract.agent_contracts[agent_name]["status"] = "terminated"
                
            # Remove from active agents
            if agent_name in self.active_agents:
                self.active_agents[agent_name]["status"] = "terminated"
                self.active_agents[agent_name]["termination_reason"] = reason
                
    def _get_domains_batch(self) -> List[str]:
        """Get batch of domains to process."""
        # This would integrate with domain discovery systems
        # For now, return sample domains for acceleration testing
        
        sample_domains = [
            "newcompany1.com", "startup2.com", "techfirm3.com",
            "innovate4.com", "future5.com", "growth6.com",
            "scale7.com", "disrupt8.com", "transform9.com",
            "evolve10.com"
        ]
        
        # Return batch size based on current agent count
        batch_size = min(len(sample_domains), self.current_agent_count)
        return sample_domains[:batch_size]
        
    def _process_domains_batch(self, domains: List[str]):
        """Process batch of domains with current agent pool."""
        processed_count = 0
        
        with ThreadPoolExecutor(max_workers=self.current_agent_count) as executor:
            # Submit all domains for processing
            future_to_domain = {
                executor.submit(self._process_single_domain, domain): domain 
                for domain in domains
            }
            
            # Collect results
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    result = future.result()
                    if result.get("success"):
                        processed_count += 1
                except Exception as e:
                    logger.error(f"Error processing domain {domain}: {e}")
                    
        # Update processing metrics
        self._update_processing_metrics(processed_count, len(domains))
        
    def _process_single_domain(self, domain: str) -> Dict:
        """Process a single domain with quality validation."""
        try:
            # Simulate domain processing
            import random
            time.sleep(random.uniform(0.5, 2.0))  # Simulate processing time
            
            # Simulate quality score based on current system health
            base_quality = 0.6 + (random.uniform(0, 0.4))
            
            # Quality boost if system is running well
            system_metrics = self._get_system_metrics()
            if system_metrics.get("cpu_usage", 100) < 50:
                base_quality += 0.1
                
            quality_score = min(1.0, base_quality)
            
            # Apply brutal quality filter
            if quality_score < 0.85:
                return {
                    "success": False,
                    "domain": domain,
                    "quality_score": quality_score,
                    "reason": "Failed brutal quality threshold"
                }
                
            return {
                "success": True,
                "domain": domain,
                "quality_score": quality_score,
                "processing_time": random.uniform(0.5, 2.0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "domain": domain,
                "error": str(e)
            }
            
    def _update_processing_metrics(self, processed: int, attempted: int):
        """Update processing performance metrics."""
        success_rate = processed / attempted if attempted > 0 else 0
        timestamp = datetime.datetime.now().isoformat()
        
        if timestamp not in self.performance_metrics:
            self.performance_metrics[timestamp] = {
                "processed": processed,
                "attempted": attempted,
                "success_rate": success_rate,
                "active_agents": self.current_agent_count
            }
            
    def _calculate_quality_trend(self) -> str:
        """Calculate quality trend over recent performance."""
        # Simplified trend calculation
        recent_metrics = list(self.performance_metrics.values())[-5:]  # Last 5 measurements
        
        if len(recent_metrics) < 2:
            return "stable"
            
        recent_success_rates = [m.get("success_rate", 0) for m in recent_metrics]
        
        if recent_success_rates[-1] > recent_success_rates[0] + 0.1:
            return "improving"
        elif recent_success_rates[-1] < recent_success_rates[0] - 0.1:
            return "declining"
        else:
            return "stable"
            
    def _calculate_engagement_trend(self) -> str:
        """Calculate engagement trend."""
        # Would analyze engagement warfare engine data
        return "stable"  # Simplified for now
        
    def _log_performance(self, system_metrics: Dict, quality_metrics: Dict, engagement_metrics: Dict, scaling_decision: Dict):
        """Log comprehensive performance data."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "system_metrics": system_metrics,
            "quality_metrics": quality_metrics,
            "engagement_metrics": engagement_metrics,
            "scaling_decision": scaling_decision,
            "active_agents": self.current_agent_count,
            "strategy": self.current_strategy
        }
        
        # Keep only last 100 log entries
        self.acceleration_log.append(log_entry)
        if len(self.acceleration_log) > 100:
            self.acceleration_log = self.acceleration_log[-100:]
            
    def get_acceleration_status(self) -> Dict:
        """Get current acceleration status."""
        if not self.acceleration_active:
            return {"status": "inactive"}
            
        latest_metrics = self.acceleration_log[-1] if self.acceleration_log else {}
        
        return {
            "status": "active",
            "current_agent_count": self.current_agent_count,
            "target_rate": getattr(self, 'target_rate', 0),
            "strategy": self.current_strategy,
            "latest_metrics": latest_metrics,
            "total_processed": sum(m.get("processed", 0) for m in self.performance_metrics.values()),
            "overall_success_rate": self._calculate_overall_success_rate()
        }
        
    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate."""
        total_processed = sum(m.get("processed", 0) for m in self.performance_metrics.values())
        total_attempted = sum(m.get("attempted", 0) for m in self.performance_metrics.values())
        
        return total_processed / total_attempted if total_attempted > 0 else 0.0
        
    def stop_acceleration(self):
        """Stop adaptive acceleration."""
        self.acceleration_active = False
        logger.info("🛑 ACCELERATION STOPPED")
        
        return {
            "status": "stopped",
            "final_agent_count": self.current_agent_count,
            "total_processed": sum(m.get("processed", 0) for m in self.performance_metrics.values()),
            "final_success_rate": self._calculate_overall_success_rate()
        }


# Singleton instance
_acceleration_engine = None

def get_acceleration_engine() -> AdaptiveAccelerationEngine:
    """Get the Adaptive Acceleration Engine singleton instance."""
    global _acceleration_engine
    
    if _acceleration_engine is None:
        _acceleration_engine = AdaptiveAccelerationEngine()
        
    return _acceleration_engine

def start_acceleration(target_domains_per_hour: int = 50, strategy: str = "aggressive") -> Dict:
    """Start adaptive acceleration."""
    return get_acceleration_engine().start_acceleration(target_domains_per_hour, strategy)

def stop_acceleration() -> Dict:
    """Stop adaptive acceleration."""
    return get_acceleration_engine().stop_acceleration()

def get_acceleration_status() -> Dict:
    """Get current acceleration status."""
    return get_acceleration_engine().get_acceleration_status()

if __name__ == "__main__":
    # Test the acceleration engine
    engine = get_acceleration_engine()
    
    print("🚀 Starting Adaptive Acceleration Engine Test")
    result = start_acceleration(target_domains_per_hour=100, strategy="blitz")
    print(f"Acceleration started: {result}")
    
    # Let it run for a bit
    time.sleep(10)
    
    status = get_acceleration_status()
    print(f"Current status: {status}")
    
    stop_result = stop_acceleration()
    print(f"Acceleration stopped: {stop_result}")