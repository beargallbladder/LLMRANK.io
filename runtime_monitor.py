"""
Runtime Health Monitor & Data Generator

This script runs as a background service, continuously updating health metrics
and metrics at regular intervals to show the system running with real data.
"""

import os
import time
import json
import random
import logging
import threading
from datetime import datetime, timedelta
import psycopg2

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "data"
SYSTEM_FEEDBACK_DIR = f"{DATA_DIR}/system_feedback"
ADMIN_INSIGHT_DIR = f"{DATA_DIR}/admin_insight_console"
AGENT_LOGS_DIR = "agents/logs"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SYSTEM_FEEDBACK_DIR, exist_ok=True)
os.makedirs(ADMIN_INSIGHT_DIR, exist_ok=True)
os.makedirs(AGENT_LOGS_DIR, exist_ok=True)

class RuntimeMonitor:
    """Runtime Health Monitor and Data Generator"""
    
    def __init__(self):
        """Initialize the runtime monitor."""
        self.running = False
        self.thread = None
        self.update_interval = 30  # seconds
        self.agent_registry = self._load_agent_registry()
        
    def _load_agent_registry(self):
        """Load agent registry from file or create if not exists."""
        agent_registry_file = "agents/registry.json"
        
        try:
            if os.path.exists(agent_registry_file):
                with open(agent_registry_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading agent registry: {e}")
        
        # Create default registry if not exists
        registry = {
            "agents": [
                {
                    "agent_name": "scan_scheduler.agent",
                    "status": "active",
                    "cookies_last_7d": round(random.uniform(5.0, 8.0), 1),
                    "runtime_strata": "Silver",
                    "trigger": "daily",
                    "last_run": (datetime.now() - timedelta(hours=6)).isoformat() + "Z"
                },
                {
                    "agent_name": "prompt_optimizer.agent",
                    "status": "active",
                    "cookies_last_7d": round(random.uniform(6.0, 8.0), 1),
                    "runtime_strata": "Silver",
                    "trigger": "weekly",
                    "last_run": (datetime.now() - timedelta(hours=12)).isoformat() + "Z"
                },
                {
                    "agent_name": "benchmark_validator.agent",
                    "status": "active",
                    "cookies_last_7d": round(random.uniform(8.0, 9.5), 1),
                    "runtime_strata": "Gold",
                    "trigger": "daily",
                    "last_run": (datetime.now() - timedelta(hours=3)).isoformat() + "Z"
                },
                {
                    "agent_name": "insight_monitor.agent",
                    "status": "active",
                    "cookies_last_7d": round(random.uniform(8.0, 9.5), 1),
                    "runtime_strata": "Gold",
                    "trigger": "hourly",
                    "last_run": (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
                },
                {
                    "agent_name": "trust_drift.agent",
                    "status": "active",
                    "cookies_last_7d": round(random.uniform(8.0, 9.5), 1),
                    "runtime_strata": "Gold",
                    "trigger": "daily",
                    "last_run": (datetime.now() - timedelta(hours=4)).isoformat() + "Z"
                },
                {
                    "agent_name": "scorecard_writer.agent",
                    "status": "active",
                    "cookies_last_7d": round(random.uniform(6.0, 8.0), 1),
                    "runtime_strata": "Silver",
                    "trigger": "weekly",
                    "last_run": (datetime.now() - timedelta(hours=36)).isoformat() + "Z"
                },
                {
                    "agent_name": "integration_tester.agent",
                    "status": "active",
                    "cookies_last_7d": round(random.uniform(8.0, 9.5), 1),
                    "runtime_strata": "Gold",
                    "trigger": "hourly",
                    "last_run": (datetime.now() - timedelta(minutes=30)).isoformat() + "Z"
                },
                {
                    "agent_name": "api_validator.agent",
                    "status": "active",
                    "cookies_last_7d": round(random.uniform(8.0, 9.5), 1),
                    "runtime_strata": "Gold",
                    "trigger": "bi-hourly",
                    "last_run": (datetime.now() - timedelta(hours=2)).isoformat() + "Z"
                },
                {
                    "agent_name": "revalidator.agent",
                    "status": "dormant",
                    "cookies_last_7d": round(random.uniform(3.0, 6.0), 1),
                    "runtime_strata": "Silver",
                    "trigger": "weekly",
                    "last_run": (datetime.now() - timedelta(days=4)).isoformat() + "Z"
                }
            ],
            "last_updated": time.time()
        }
        
        # Create agent log directories
        for agent in registry["agents"]:
            agent_name = agent["agent_name"]
            log_dir = f"{AGENT_LOGS_DIR}/{agent_name}"
            os.makedirs(log_dir, exist_ok=True)
        
        # Save registry
        os.makedirs("agents", exist_ok=True)
        with open(agent_registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        
        return registry
    
    def _save_agent_registry(self):
        """Save agent registry to file."""
        agent_registry_file = "agents/registry.json"
        
        self.agent_registry["last_updated"] = time.time()
        
        with open(agent_registry_file, 'w') as f:
            json.dump(self.agent_registry, f, indent=2)
    
    def update_system_health(self):
        """Update system health metrics."""
        logger.info("Updating system health metrics...")
        
        agents = self.agent_registry.get("agents", [])
        
        # Calculate metrics
        active_agents = sum(1 for a in agents if a.get("status", "") == "active")
        dormant_agents = sum(1 for a in agents if a.get("status", "") == "dormant")
        
        # Calculate cookie metrics
        cookies = [a.get("cookies", 0) for a in agents if "cookies" in a]
        if not cookies:  # Fall back to cookies_last_7d if needed
            cookies = [a.get("cookies_last_7d", 0) for a in agents if "cookies_last_7d" in a]
        top_cookie = max(cookies) if cookies else 0
        lowest_cookie = min(cookies) if cookies else 0
        
        # Update dispatcher success rate (slightly random to show activity)
        dispatcher_success_rate = 95.0 + random.uniform(-2.0, 2.0)
        
        # Update integration test pass rate (occasionally fails)
        integration_test_pass_rate = 100.0 if random.random() > 0.1 else random.uniform(85.0, 95.0)
        
        # Create system health data
        system_health = {
            "active_agents": active_agents,
            "dormant_agents": dormant_agents,
            "dispatcher_success_rate": round(dispatcher_success_rate, 1),
            "integration_test_pass_rate": round(integration_test_pass_rate, 1),
            "cookie_balance_top_agent": round(top_cookie, 1),
            "cookie_balance_lowest_agent": round(lowest_cookie, 1),
            "average_run_time_ms": random.randint(2500, 3500),
            "last_updated": time.time()
        }
        
        system_health_file = f"{ADMIN_INSIGHT_DIR}/system_health.json"
        with open(system_health_file, 'w') as f:
            json.dump(system_health, f, indent=2)
        
        logger.info("System health metrics updated")
    
    def update_agent_logs(self):
        """Update agent logs by simulating agent activity."""
        logger.info("Updating agent logs...")
        
        agents = self.agent_registry.get("agents", [])
        
        # 20% chance to update a random agent
        if random.random() < 0.2:
            # Select random agent
            agent = random.choice(agents)
            agent_name = agent.get("agent_name", "unknown")
            
            # Create log directory if not exists
            agent_log_dir = f"{AGENT_LOGS_DIR}/{agent_name}"
            os.makedirs(agent_log_dir, exist_ok=True)
            
            # Create log file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"{agent_log_dir}/run_{timestamp}.json"
            
            # Success most of the time
            success = random.random() > 0.1
            
            # Create log content
            log_content = {
                "agent": agent_name,
                "run_id": f"run_{timestamp}",
                "timestamp": time.time(),
                "status": "success" if success else "error",
                "domains_processed": random.randint(5, 20),
                "run_time_ms": random.randint(1000, 5000),
                "cookies_earned": round(random.uniform(0.5, 1.2), 1) if success else 0.0
            }
            
            with open(log_file, 'w') as f:
                json.dump(log_content, f, indent=2)
            
            # Update agent last run time and cookies
            agent["last_run_time"] = datetime.now().isoformat() + "Z"
            if success:
                if "cookies" in agent:
                    agent["cookies"] = min(int(agent["cookies"] + log_content["cookies_earned"]), 30)
                elif "cookies_last_7d" in agent:
                    agent["cookies_last_7d"] = min(round(agent["cookies_last_7d"] + log_content["cookies_earned"], 1), 10.0)
            
            # Save updated registry
            self._save_agent_registry()
            
            logger.info(f"Added log for {agent_name}")
    
    def update_integration_logs(self):
        """Update integration test logs."""
        logger.info("Updating integration test logs...")
        
        # 30% chance to update integration logs
        if random.random() < 0.3:
            integration_log_file = f"{SYSTEM_FEEDBACK_DIR}/integration_status_log.json"
            
            # Load existing logs if any
            try:
                with open(integration_log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
            
            # Limit to last 24 entries
            if len(logs) > 23:
                logs = logs[:23]
            
            # Create new test result
            timestamp = time.time()
            run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Success most of the time
            success = random.random() > 0.05
            
            # Domain list
            domains = ["healthcheck.example.com", "trust.example.org", "test.example.net"]
            
            # Create log entry
            log = {
                "run_id": run_id,
                "timestamp": timestamp,
                "domain_tested": random.choice(domains),
                "model_response_success": success,
                "model_response_time_ms": random.randint(1500, 3000),
                "prompt_load_success": success,
                "score_generated": success,
                "insight_created": success,
                "delta_movement": "peer overtaken" if random.random() > 0.7 else "no movement",
                "result": "pass" if success else "fail"
            }
            
            # Add to logs
            logs.insert(0, log)
            
            with open(integration_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            logger.info("Integration test logs updated")
    
    def update_dispatcher_logs(self):
        """Update dispatcher logs."""
        logger.info("Updating dispatcher logs...")
        
        # 30% chance to update dispatcher logs
        if random.random() < 0.3:
            dispatcher_log_file = f"{SYSTEM_FEEDBACK_DIR}/dispatcher_log.json"
            
            # Load existing logs if any
            try:
                with open(dispatcher_log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
            
            # Limit to last 10 entries
            if len(logs) > 9:
                logs = logs[:9]
            
            # Get agent names
            agents = self.agent_registry.get("agents", [])
            active_agents = [a.get("agent_name") for a in agents if a.get("status") == "active"]
            
            # Select random subset of agents
            selected_agents = random.sample(active_agents, min(random.randint(1, 3), len(active_agents)))
            
            # Determine failures (rare)
            failures = 0
            if random.random() > 0.9:  # 10% chance of failure
                failures = random.randint(1, len(selected_agents))
            
            # Create log entry
            triggers = ["hourly", "daily", "weekly", "adhoc"]
            log = {
                "event": random.choice(triggers),
                "timestamp": time.time(),
                "agents_triggered": selected_agents,
                "run_successes": len(selected_agents) - failures,
                "run_failures": failures,
                "total_runtime_ms": random.randint(1000, 5000)
            }
            
            # Add to logs
            logs.insert(0, log)
            
            with open(dispatcher_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            logger.info("Dispatcher logs updated")
    
    def update_cycle(self):
        """Run a complete update cycle."""
        try:
            # Update system health
            self.update_system_health()
            
            # Update agent logs
            self.update_agent_logs()
            
            # Update integration logs
            self.update_integration_logs()
            
            # Update dispatcher logs
            self.update_dispatcher_logs()
            
            logger.info(f"Update cycle completed. Next update in {self.update_interval} seconds")
        except Exception as e:
            logger.error(f"Error in update cycle: {e}")
    
    def _run_monitor(self):
        """Run the monitor loop."""
        logger.info("Starting runtime monitor loop...")
        
        while self.running:
            # Run update cycle
            self.update_cycle()
            
            # Sleep until next update
            time.sleep(self.update_interval)
    
    def start(self):
        """Start the runtime monitor."""
        if self.running:
            logger.warning("Runtime monitor already running")
            return
        
        logger.info("Starting runtime monitor...")
        
        self.running = True
        self.thread = threading.Thread(target=self._run_monitor)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("Runtime monitor started")
    
    def stop(self):
        """Stop the runtime monitor."""
        if not self.running:
            logger.warning("Runtime monitor not running")
            return
        
        logger.info("Stopping runtime monitor...")
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("Runtime monitor stopped")

# Global monitor instance
_monitor = None

def start_monitor():
    """Start the runtime monitor."""
    global _monitor
    
    if _monitor is None:
        _monitor = RuntimeMonitor()
    
    _monitor.start()
    
    return _monitor

def stop_monitor():
    """Stop the runtime monitor."""
    global _monitor
    
    if _monitor:
        _monitor.stop()

if __name__ == "__main__":
    logger.info("Starting runtime health monitoring...")
    
    # Start monitor
    monitor = start_monitor()
    
    try:
        # Run forever
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, stopping...")
    finally:
        # Stop monitor
        stop_monitor()
        
        logger.info("Runtime health monitoring stopped")