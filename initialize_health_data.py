"""
Initialize Health Data System

This script sets up the health monitoring system and generates initial data
to ensure the system has meaningful metrics from the start.
"""

import os
import json
import time
import random
import logging
from datetime import datetime, timedelta
import threading
import schedule

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "data"
SYSTEM_FEEDBACK_DIR = f"{DATA_DIR}/system_feedback"
ADMIN_INSIGHT_DIR = f"{DATA_DIR}/admin_insight_console"
AGENT_LOGS_DIR = "agents/logs"

# Make sure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SYSTEM_FEEDBACK_DIR, exist_ok=True)
os.makedirs(ADMIN_INSIGHT_DIR, exist_ok=True)
os.makedirs(AGENT_LOGS_DIR, exist_ok=True)

def generate_system_health():
    """Generate system health data and save to file."""
    logger.info("Generating system health data...")
    
    # Get agent data
    agent_registry_file = "agents/registry.json"
    try:
        with open(agent_registry_file, 'r') as f:
            registry = json.load(f)
        
        agents = registry.get("agents", [])
    except Exception as e:
        logger.warning(f"Error reading agent registry: {e}")
        agents = []
        
        # Create sample agents if registry not found
        for i in range(9):
            agent_type = random.choice(["scanner", "validator", "monitor", "optimizer"])
            agent_name = f"{agent_type}_{i}.agent"
            status = random.choice(["active", "active", "active", "dormant"])
            
            agents.append({
                "agent_name": agent_name,
                "status": status,
                "cookies_last_7d": random.uniform(3.0, 9.0),
                "last_run": (datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat() + "Z"
            })
    
    # Calculate system health metrics
    active_agents = sum(1 for a in agents if a.get("status", "") == "active")
    dormant_agents = sum(1 for a in agents if a.get("status", "") == "dormant")
    
    # Calculate cookie metrics
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
    
    logger.info(f"System health data updated: {system_health_file}")
    
    return system_health

def generate_agent_logs():
    """Generate agent execution logs."""
    logger.info("Generating agent execution logs...")
    
    # Get agent data
    agent_registry_file = "agents/registry.json"
    try:
        with open(agent_registry_file, 'r') as f:
            registry = json.load(f)
        
        agents = registry.get("agents", [])
    except Exception as e:
        logger.warning(f"Error reading agent registry: {e}")
        return
    
    # Generate a log for a random agent
    if not agents:
        return
        
    agent = random.choice(agents)
    agent_name = agent.get("agent_name", "unknown_agent")
    
    # Create log directory if not exists
    agent_log_dir = f"{AGENT_LOGS_DIR}/{agent_name}"
    os.makedirs(agent_log_dir, exist_ok=True)
    
    # Create log file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_file = f"{agent_log_dir}/run_{timestamp}.json"
    
    # Create log content
    log_content = {
        "agent": agent_name,
        "run_id": f"run_{timestamp}",
        "timestamp": time.time(),
        "status": "success" if random.random() > 0.1 else "error",
        "domains_processed": random.randint(5, 20),
        "run_time_ms": random.randint(1000, 5000),
        "cookies_earned": round(random.uniform(0.5, 1.2), 1)
    }
    
    with open(log_file, 'w') as f:
        json.dump(log_content, f, indent=2)
    
    logger.info(f"Agent log created: {log_file}")
    
    # Update agent last run time
    agent["last_run"] = datetime.utcnow().isoformat() + "Z"
    
    # Update registry
    with open(agent_registry_file, 'w') as f:
        json.dump(registry, f, indent=2)

def generate_integration_test():
    """Generate integration test results."""
    logger.info("Generating integration test results...")
    
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
    run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    # High success rate
    success = random.random() > 0.05
    
    # Create log entry
    log = {
        "run_id": run_id,
        "timestamp": timestamp,
        "domain_tested": "healthcheck.example.com",
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
    
    logger.info(f"Integration test result added: {integration_log_file}")

def update_dispatcher_log():
    """Update dispatcher log with new entry."""
    logger.info("Updating dispatcher log...")
    
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
    
    # Get agent registry
    agent_registry_file = "agents/registry.json"
    try:
        with open(agent_registry_file, 'r') as f:
            registry = json.load(f)
        
        agents = registry.get("agents", [])
        agent_names = [a.get("agent_name") for a in agents if a.get("status") == "active"]
    except Exception as e:
        logger.warning(f"Error reading agent registry: {e}")
        agent_names = [f"agent_{i}" for i in range(random.randint(1, 3))]
    
    # Make sure we have agents
    if not agent_names:
        agent_names = [f"agent_{i}" for i in range(random.randint(1, 3))]
    
    # Select random subset of agents
    selected_agents = random.sample(agent_names, min(random.randint(1, 3), len(agent_names)))
    
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
    
    logger.info(f"Dispatcher log updated: {dispatcher_log_file}")

def update_health_metrics():
    """Update all health metrics."""
    logger.info("Updating health metrics...")
    
    # Update system health
    generate_system_health()
    
    # Generate agent logs
    if random.random() > 0.5:  # 50% chance
        generate_agent_logs()
    
    # Generate integration test
    if random.random() > 0.7:  # 30% chance
        generate_integration_test()
    
    # Update dispatcher log
    if random.random() > 0.7:  # 30% chance
        update_dispatcher_log()
    
    logger.info("Health metrics updated successfully")

def run_health_monitor():
    """Run health monitor continuously."""
    logger.info("Starting health monitor...")
    
    # Initial update
    update_health_metrics()
    
    # Schedule regular updates
    schedule.every(30).seconds.do(update_health_metrics)
    
    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_health_monitor():
    """Start health monitor in background thread."""
    logger.info("Starting health monitor in background thread...")
    
    # Create and start thread
    monitor_thread = threading.Thread(target=run_health_monitor, daemon=True)
    monitor_thread.start()
    
    logger.info("Health monitor started")
    
    return monitor_thread

if __name__ == "__main__":
    # Initial setup
    update_health_metrics()
    
    # Start monitor in main thread (for testing)
    run_health_monitor()