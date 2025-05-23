"""
LLMPageRank Agent Monitor

This module provides functionality to monitor and track agent status, logs, and performance
within the Cookie Combat Runtime Economy system.
"""

import os
import json
import datetime
import logging
from typing import Dict, List, Optional, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Constants
AGENT_REGISTRY_PATH = "agents/agent_registry.json"
AGENT_LOGS_DIR = "agents/logs"


def get_registry() -> Dict:
    """
    Get the current agent registry.
    
    Returns:
        Agent registry dictionary
    """
    if os.path.exists(AGENT_REGISTRY_PATH):
        try:
            with open(AGENT_REGISTRY_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode agent registry JSON: {AGENT_REGISTRY_PATH}")
    
    # If registry doesn't exist or is invalid, create default registry
    logger.warning(f"Creating default agent registry: {AGENT_REGISTRY_PATH}")
    
    default_registry = {
        "agents": [],
        "last_update": datetime.datetime.now().isoformat(),
        "cookie_economy": {
            "total_daily_cookies": 100,
            "remaining_cookies": 100,
            "distributed_cookies": 0,
            "rollover_cookies": 0,
            "economy_status": "initialized",
            "last_reset": datetime.datetime.now().isoformat()
        },
        "rescue_operations": [],
        "challenges": []
    }
    
    # Save default registry
    os.makedirs(os.path.dirname(AGENT_REGISTRY_PATH), exist_ok=True)
    with open(AGENT_REGISTRY_PATH, "w") as f:
        json.dump(default_registry, f, indent=2)
    
    return default_registry


def save_registry(registry: Dict) -> bool:
    """
    Save the agent registry.
    
    Args:
        registry: Agent registry dictionary
        
    Returns:
        Success flag
    """
    # Update last update timestamp
    registry["last_update"] = datetime.datetime.now().isoformat()
    
    # Save registry
    try:
        os.makedirs(os.path.dirname(AGENT_REGISTRY_PATH), exist_ok=True)
        with open(AGENT_REGISTRY_PATH, "w") as f:
            json.dump(registry, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save agent registry: {e}")
        return False


def get_agent_info(agent_name: str) -> Optional[Dict]:
    """
    Get information about a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Agent information dictionary or None if not found
    """
    registry = get_registry()
    
    # Find agent in registry
    for agent in registry.get("agents", []):
        if agent.get("name") == agent_name:
            return agent
    
    return None


def update_agent_status(agent_name: str, status: Optional[str] = None, 
                       strata: Optional[str] = None, 
                       cookie_adjustment: Optional[float] = None,
                       performance_score: Optional[float] = None) -> bool:
    """
    Update an agent's status in the registry.
    
    Args:
        agent_name: Name of the agent
        status: New status (active, dormant, etc.)
        strata: New strata (gold, silver, bronze, rust)
        cookie_adjustment: Cookie adjustment (positive or negative)
        performance_score: New performance score
        
    Returns:
        Success flag
    """
    registry = get_registry()
    
    # Find agent in registry
    agent_found = False
    
    for i, agent in enumerate(registry.get("agents", [])):
        if agent.get("name") == agent_name:
            # Update agent status
            if status is not None:
                agent["status"] = status
            
            # Update agent strata
            if strata is not None:
                agent["strata"] = strata
            
            # Adjust cookies
            if cookie_adjustment is not None:
                agent["cookies"] = max(0, agent.get("cookies", 0) + cookie_adjustment)
            
            # Update performance score
            if performance_score is not None:
                agent["performance_score"] = performance_score
            
            # Update agent in registry
            registry["agents"][i] = agent
            agent_found = True
            break
    
    # If agent not found, create new agent
    if not agent_found and (status is not None or strata is not None or cookie_adjustment is not None):
        new_agent = {
            "name": agent_name,
            "status": status or "active",
            "strata": strata or "bronze",
            "cookies": max(0, cookie_adjustment or 0),
            "last_success_time": datetime.datetime.now().isoformat(),
            "last_run_time": datetime.datetime.now().isoformat(),
            "performance_score": performance_score or 0.5,
            "specialties": [],
            "capabilities": {
                "clarity": 0.5,
                "speed": 0.5,
                "impact": 0.5
            }
        }
        
        registry["agents"].append(new_agent)
    
    return save_registry(registry)


def log_agent_activity(agent_name: str, event_type: str, 
                     success: bool = True, 
                     details: Optional[Dict] = None) -> bool:
    """
    Log an agent activity.
    
    Args:
        agent_name: Name of the agent
        event_type: Type of event (run, insight, rescue, etc.)
        success: Whether the activity was successful
        details: Additional details about the activity
        
    Returns:
        Success flag
    """
    # Ensure agent logs directory exists
    agent_log_dir = os.path.join(AGENT_LOGS_DIR, agent_name)
    os.makedirs(agent_log_dir, exist_ok=True)
    
    # Create log entry
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "agent": agent_name,
        "event_type": event_type,
        "success": success,
        "details": details or {}
    }
    
    # Generate log file name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(agent_log_dir, f"{timestamp}_{event_type}.json")
    
    # Save log entry
    try:
        with open(log_file, "w") as f:
            json.dump(log_entry, f, indent=2)
        
        # Update agent last run/success times
        registry = get_registry()
        for i, agent in enumerate(registry.get("agents", [])):
            if agent.get("name") == agent_name:
                agent["last_run_time"] = datetime.datetime.now().isoformat()
                if success:
                    agent["last_success_time"] = datetime.datetime.now().isoformat()
                registry["agents"][i] = agent
                save_registry(registry)
                break
        
        return True
    except Exception as e:
        logger.error(f"Failed to log agent activity: {e}")
        return False


def get_agent_logs(agent_name: str, limit: int = 10) -> List[Dict]:
    """
    Get recent logs for an agent.
    
    Args:
        agent_name: Name of the agent
        limit: Maximum number of logs to return
        
    Returns:
        List of log entry dictionaries
    """
    # Ensure agent logs directory exists
    agent_log_dir = os.path.join(AGENT_LOGS_DIR, agent_name)
    
    if not os.path.exists(agent_log_dir):
        logger.warning(f"Agent log directory does not exist: {agent_log_dir}")
        return []
    
    # Get log files
    log_files = []
    
    try:
        for filename in os.listdir(agent_log_dir):
            if filename.endswith(".json"):
                log_files.append(os.path.join(agent_log_dir, filename))
    except Exception as e:
        logger.error(f"Failed to list agent log files: {e}")
        return []
    
    # Sort log files by modification time (newest first)
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Read log entries
    logs = []
    
    for log_file in log_files[:limit]:
        try:
            with open(log_file, "r") as f:
                log_entry = json.load(f)
                logs.append(log_entry)
        except Exception as e:
            logger.error(f"Failed to read log file {log_file}: {e}")
    
    return logs


def get_all_agents() -> List[Dict]:
    """
    Get all agents from the registry.
    
    Returns:
        List of agent dictionaries
    """
    registry = get_registry()
    return registry.get("agents", [])


def update_cookie_economy(economy_update: Dict) -> bool:
    """
    Update the cookie economy status in the registry.
    
    Args:
        economy_update: Cookie economy update dictionary
        
    Returns:
        Success flag
    """
    registry = get_registry()
    
    # Update cookie economy
    current_economy = registry.get("cookie_economy", {})
    current_economy.update(economy_update)
    registry["cookie_economy"] = current_economy
    
    return save_registry(registry)


def add_rescue_operation(rescue_op: Dict) -> bool:
    """
    Add a rescue operation to the registry.
    
    Args:
        rescue_op: Rescue operation dictionary
        
    Returns:
        Success flag
    """
    registry = get_registry()
    
    # Add rescue operation
    rescue_operations = registry.get("rescue_operations", [])
    rescue_operations.append(rescue_op)
    registry["rescue_operations"] = rescue_operations
    
    return save_registry(registry)


def add_challenge(challenge: Dict) -> bool:
    """
    Add a challenge to the registry.
    
    Args:
        challenge: Challenge dictionary
        
    Returns:
        Success flag
    """
    registry = get_registry()
    
    # Add challenge
    challenges = registry.get("challenges", [])
    challenges.append(challenge)
    registry["challenges"] = challenges
    
    return save_registry(registry)


def update_agent_capabilities(agent_name: str, capabilities: Dict) -> bool:
    """
    Update an agent's capabilities in the registry.
    
    Args:
        agent_name: Name of the agent
        capabilities: Capability update dictionary
        
    Returns:
        Success flag
    """
    registry = get_registry()
    
    # Find agent in registry
    for i, agent in enumerate(registry.get("agents", [])):
        if agent.get("name") == agent_name:
            # Update agent capabilities
            current_capabilities = agent.get("capabilities", {})
            current_capabilities.update(capabilities)
            agent["capabilities"] = current_capabilities
            
            # Update agent in registry
            registry["agents"][i] = agent
            
            return save_registry(registry)
    
    return False


def register_new_agent(agent_info: Dict) -> bool:
    """
    Register a new agent in the registry.
    
    Args:
        agent_info: Agent information dictionary
        
    Returns:
        Success flag
    """
    registry = get_registry()
    
    # Check if agent already exists
    for agent in registry.get("agents", []):
        if agent.get("name") == agent_info.get("name"):
            return False
    
    # Add new agent
    registry["agents"].append(agent_info)
    
    return save_registry(registry)


def log_agent_self_report(agent_name: str, report: Dict) -> bool:
    """
    Log an agent self-report with health and status information.
    
    Args:
        agent_name: Name of the agent
        report: Self-report dictionary containing status, metrics, and health data
        
    Returns:
        Success flag
    """
    try:
        # Get the current timestamp
        now = datetime.datetime.now().isoformat()
        
        # Create the log entry
        log_entry = {
            "timestamp": now,
            "agent": agent_name,
            "type": "self_report",
            "data": report
        }
        
        # Load existing reports
        reports_file = os.path.join("data/system_feedback", "agent_self_report.json")
        os.makedirs(os.path.dirname(reports_file), exist_ok=True)
        
        reports = []
        if os.path.exists(reports_file):
            try:
                with open(reports_file, "r") as f:
                    reports = json.load(f)
            except json.JSONDecodeError:
                # If file is corrupted, start fresh
                reports = []
        
        # Add new report
        reports.append(log_entry)
        
        # Keep only the latest 100 reports
        if len(reports) > 100:
            reports = reports[-100:]
        
        # Save updated reports
        with open(reports_file, "w") as f:
            json.dump(reports, f, indent=2)
        
        logger.info(f"Logged self-report for agent: {agent_name}")
        return True
    except Exception as e:
        logger.error(f"Error logging self-report for agent {agent_name}: {e}")
        return False