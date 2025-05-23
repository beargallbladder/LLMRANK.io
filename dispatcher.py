"""
LLMPageRank V10 Agent Dispatcher

This module implements the agent dispatcher according to PRD 10 Addendum 2,
controlling the execution of agents based on triggers and managing their lifecycle.
"""

import os
import json
import time
import logging
import importlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Import project modules
from config import DATA_DIR
import agent_monitor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
AGENTS_DIR = "agents"
SYSTEM_FEEDBACK_DIR = f"{DATA_DIR}/system_feedback"
DISPATCHER_LOG_FILE = f"{SYSTEM_FEEDBACK_DIR}/dispatcher_log.json"

class Dispatcher:
    """
    Controls the execution of agents based on triggers and manages their lifecycle.
    """
    
    def __init__(self):
        """Initialize the dispatcher."""
        # Ensure directories exist
        os.makedirs(SYSTEM_FEEDBACK_DIR, exist_ok=True)
        
        self.dispatcher_logs = self._load_dispatcher_logs()
    
    def _load_dispatcher_logs(self) -> List[Dict]:
        """
        Load dispatcher logs from file.
        
        Returns:
            List of dispatcher log dictionaries
        """
        if not os.path.exists(DISPATCHER_LOG_FILE):
            return []
            
        try:
            with open(DISPATCHER_LOG_FILE, 'r') as f:
                logs = json.load(f)
                
                # Ensure logs is a list
                if not isinstance(logs, list):
                    return []
                    
                return logs
        except Exception as e:
            logger.error(f"Error loading dispatcher logs: {e}")
            return []
    
    def _save_dispatcher_logs(self) -> bool:
        """
        Save dispatcher logs to file.
        
        Returns:
            Success flag
        """
        try:
            os.makedirs(os.path.dirname(DISPATCHER_LOG_FILE), exist_ok=True)
            with open(DISPATCHER_LOG_FILE, 'w') as f:
                json.dump(self.dispatcher_logs, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving dispatcher logs: {e}")
            return False
    
    def execute_agent(self, agent_name: str, context: Optional[Dict] = None) -> Dict:
        """
        Execute an agent.
        
        Args:
            agent_name: Agent name
            context: Optional context dictionary
            
        Returns:
            Execution result dictionary
        """
        logger.info(f"Executing agent: {agent_name}")
        
        start_time = time.time()
        
        # Default result structure
        execution_result = {
            "status": "failed",
            "runtime_ms": 0,
            "cookies_earned": 0,
            "error": None,
            "result_summary": {}
        }
        
        try:
            # Check if agent exists and is active
            registry = agent_monitor.get_registry()
            agents = registry.get("agents", [])
            
            agent_found = False
            agent_active = False
            
            for agent in agents:
                if agent.get("agent_name") == agent_name:
                    agent_found = True
                    agent_active = agent.get("status") == "active"
                    break
            
            if not agent_found:
                raise Exception(f"Agent {agent_name} not found in registry")
            
            if not agent_active:
                raise Exception(f"Agent {agent_name} is not active")
            
            # Load agent module
            module_name = agent_name.replace(".agent", "")
            module_path = f"agents.{module_name}"
            
            try:
                agent_module = importlib.import_module(module_path)
            except ImportError:
                raise Exception(f"Failed to import agent module: {module_path}")
            
            # Execute agent
            if hasattr(agent_module, "run"):
                result = agent_module.run(context)
                
                # Validate result
                if not isinstance(result, dict):
                    raise Exception(f"Agent {agent_name} run function returned invalid result type")
                
                # Update execution result
                execution_result["status"] = "completed"
                execution_result["cookies_earned"] = result.get("cookies_earned", 0)
                execution_result["result_summary"] = result
            else:
                raise Exception(f"Agent {agent_name} module does not have a run function")
        except Exception as e:
            logger.error(f"Error executing agent {agent_name}: {e}")
            execution_result["error"] = str(e)
        
        # Calculate runtime
        end_time = time.time()
        runtime_ms = int((end_time - start_time) * 1000)
        execution_result["runtime_ms"] = runtime_ms
        
        # Log agent execution
        agent_monitor.log_agent_execution(agent_name, execution_result)
        
        return execution_result
    
    def execute_agents_by_trigger(self, trigger: str, context: Optional[Dict] = None) -> Dict:
        """
        Execute agents by trigger event.
        
        Args:
            trigger: Trigger event string
            context: Optional context dictionary
            
        Returns:
            Execution result dictionary
        """
        logger.info(f"Executing agents by trigger: {trigger}")
        
        start_time = time.time()
        
        # Get agents to execute
        registry = agent_monitor.get_registry()
        agents = registry.get("agents", [])
        
        agents_to_execute = [a.get("agent_name") for a in agents if a.get("trigger") == trigger and a.get("status") == "active"]
        
        logger.info(f"Found {len(agents_to_execute)} agent(s) to execute for trigger: {trigger}")
        
        # Execute agents
        run_successes = 0
        run_failures = 0
        
        for agent_name in agents_to_execute:
            result = self.execute_agent(agent_name, context)
            
            if result.get("status") == "completed":
                run_successes += 1
            else:
                run_failures += 1
        
        # Calculate runtime
        end_time = time.time()
        total_runtime_ms = int((end_time - start_time) * 1000)
        
        # Create log entry
        log_entry = {
            "event": trigger,
            "timestamp": time.time(),
            "agents_triggered": agents_to_execute,
            "run_successes": run_successes,
            "run_failures": run_failures,
            "total_runtime_ms": total_runtime_ms
        }
        
        # Add to logs
        self.dispatcher_logs.append(log_entry)
        
        # Limit logs to last 100
        if len(self.dispatcher_logs) > 100:
            self.dispatcher_logs = self.dispatcher_logs[-100:]
        
        # Save logs
        self._save_dispatcher_logs()
        
        # Return execution summary
        return {
            "event": trigger,
            "agents_triggered": agents_to_execute,
            "run_successes": run_successes,
            "run_failures": run_failures,
            "total_runtime_ms": total_runtime_ms
        }
    
    def get_dispatcher_logs(self, limit: int = 10) -> List[Dict]:
        """
        Get dispatcher logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of dispatcher log dictionaries
        """
        if not self.dispatcher_logs:
            return []
        
        # Return last 'limit' logs
        return self.dispatcher_logs[-limit:]

# Initialize dispatcher
dispatcher = Dispatcher()

def execute_agent(agent_name: str, context: Optional[Dict] = None) -> Dict:
    """
    Execute an agent.
    
    Args:
        agent_name: Agent name
        context: Optional context dictionary
        
    Returns:
        Execution result dictionary
    """
    return dispatcher.execute_agent(agent_name, context)

def execute_agents_by_trigger(trigger: str, context: Optional[Dict] = None) -> Dict:
    """
    Execute agents by trigger event.
    
    Args:
        trigger: Trigger event string
        context: Optional context dictionary
        
    Returns:
        Execution result dictionary
    """
    return dispatcher.execute_agents_by_trigger(trigger, context)

def get_dispatcher_logs(limit: int = 10) -> List[Dict]:
    """
    Get dispatcher logs.
    
    Args:
        limit: Maximum number of logs to return
        
    Returns:
        List of dispatcher log dictionaries
    """
    return dispatcher.get_dispatcher_logs(limit)