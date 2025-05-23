"""
Agent Survival Loop - Brutal Evolution Enforcement

This module implements the survival-of-the-fittest mechanism for LLMPageRank agents.
Agents must continually evolve and improve or face extinction.
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Optional, Any

from cookie_economy import get_cookie_economy

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File paths
DATA_DIR = "data/agent_survival"
os.makedirs(DATA_DIR, exist_ok=True)

SURVIVAL_LOG_PATH = os.path.join(DATA_DIR, "survival_log.json")
EXTINCTION_LOG_PATH = os.path.join(DATA_DIR, "extinction_events.json")
INTERVENTION_LOG_PATH = os.path.join(DATA_DIR, "intervention_events.json")

# Constants
EXTINCTION_THRESHOLD = 3  # Number of consecutive cycles in Rust strata before extinction
QUALITY_IMPROVEMENT_REQUIREMENT = 0.05  # Minimum improvement required per cycle
EVALUATION_CYCLE_DAYS = 7  # How often to run survival evaluations


class AgentSurvivalSystem:
    """
    Implements the brutal survival-of-the-fittest mechanism for agents.
    Agents must continually evolve or face extinction.
    """
    
    def __init__(self):
        """Initialize the survival system."""
        self.survival_log = []
        self.extinction_log = []
        self.intervention_log = []
        self.cookie_economy = get_cookie_economy()
        self.last_evaluation = datetime.datetime.now() - datetime.timedelta(days=EVALUATION_CYCLE_DAYS)
        
        # Load existing data
        self._load_data()
        
    def _load_data(self):
        """Load existing data from files."""
        try:
            if os.path.exists(SURVIVAL_LOG_PATH):
                with open(SURVIVAL_LOG_PATH, 'r') as f:
                    self.survival_log = json.load(f)
                    
            if os.path.exists(EXTINCTION_LOG_PATH):
                with open(EXTINCTION_LOG_PATH, 'r') as f:
                    self.extinction_log = json.load(f)
                    
            if os.path.exists(INTERVENTION_LOG_PATH):
                with open(INTERVENTION_LOG_PATH, 'r') as f:
                    self.intervention_log = json.load(f)
                    
            logger.info("Agent survival data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading agent survival data: {e}")
            # Initialize with empty values
            self.survival_log = []
            self.extinction_log = []
            self.intervention_log = []
            
    def _save_data(self):
        """Save current data to files."""
        try:
            with open(SURVIVAL_LOG_PATH, 'w') as f:
                json.dump(self.survival_log, f, indent=2)
                
            with open(EXTINCTION_LOG_PATH, 'w') as f:
                json.dump(self.extinction_log, f, indent=2)
                
            with open(INTERVENTION_LOG_PATH, 'w') as f:
                json.dump(self.intervention_log, f, indent=2)
                
            logger.info("Agent survival data saved successfully")
        except Exception as e:
            logger.error(f"Error saving agent survival data: {e}")
            
    def run_survival_evaluation(self):
        """
        Run the brutal survival evaluation for all agents.
        Agents that fail to evolve or maintain quality will face extinction.
        """
        now = datetime.datetime.now()
        
        # Only run evaluation after the cycle period
        if (now - self.last_evaluation).days < EVALUATION_CYCLE_DAYS:
            days_remaining = EVALUATION_CYCLE_DAYS - (now - self.last_evaluation).days
            logger.info(f"Next survival evaluation in {days_remaining} days")
            return None
            
        logger.warning("RUNNING BRUTAL SURVIVAL EVALUATION - AGENTS MUST EVOLVE OR DIE")
        
        # Get all agent performance data
        agent_performance = {}
        for agent_name in self.cookie_economy.agent_performance:
            agent_performance[agent_name] = self.cookie_economy.get_agent_performance(agent_name)
            
        # Agents on extinction watch
        at_risk_agents = []
        extinct_agents = []
        probation_agents = []
        intervention_agents = []
        
        for agent_name, performance in agent_performance.items():
            # Check if agent is at risk based on strata and consecutive failures
            current_strata = performance.get("strata", "bronze")
            consecutive_failures = performance.get("consecutive_failures", 0)
            starvation_events = performance.get("starvation_events", 0)
            extinction_risk = performance.get("extinction_risk", False)
            
            # Check quality evolution trend
            evolution_trend = performance.get("evolution_trend", [])
            recent_trend = evolution_trend[-3:] if len(evolution_trend) >= 3 else evolution_trend
            avg_quality_change = sum(recent_trend) / len(recent_trend) if recent_trend else 0
            
            # Determine if agent should be extinct, receive intervention, or put on probation
            if current_strata == "rust" and consecutive_failures >= EXTINCTION_THRESHOLD:
                extinct_agents.append({
                    "agent_name": agent_name,
                    "reason": "consecutive_failures_in_rust_strata",
                    "consecutive_failures": consecutive_failures,
                    "quality_trend": recent_trend,
                    "extinction_date": now.isoformat()
                })
                logger.error(f"EXTINCTION: Agent {agent_name} extinct due to {consecutive_failures} consecutive failures in Rust strata")
                
            elif current_strata == "rust" and starvation_events >= EXTINCTION_THRESHOLD:
                extinct_agents.append({
                    "agent_name": agent_name,
                    "reason": "starvation_in_rust_strata",
                    "starvation_events": starvation_events,
                    "quality_trend": recent_trend,
                    "extinction_date": now.isoformat()
                })
                logger.error(f"EXTINCTION: Agent {agent_name} extinct due to {starvation_events} starvation events in Rust strata")
                
            elif extinction_risk and avg_quality_change < QUALITY_IMPROVEMENT_REQUIREMENT:
                # One last chance - register for intervention
                intervention_agents.append({
                    "agent_name": agent_name,
                    "reason": "extinction_risk_with_inadequate_evolution",
                    "current_strata": current_strata,
                    "quality_trend": recent_trend,
                    "intervention_date": now.isoformat()
                })
                logger.warning(f"INTERVENTION: Agent {agent_name} receives last-chance intervention to avoid extinction")
                
            elif extinction_risk and avg_quality_change >= QUALITY_IMPROVEMENT_REQUIREMENT:
                # Showing improvement despite risk - put on probation
                probation_agents.append({
                    "agent_name": agent_name,
                    "reason": "showing_improvement_despite_risk",
                    "quality_improvement": avg_quality_change,
                    "probation_start_date": now.isoformat(),
                    "probation_end_date": (now + datetime.timedelta(days=EVALUATION_CYCLE_DAYS * 2)).isoformat()
                })
                logger.info(f"PROBATION: Agent {agent_name} placed on probation due to improvement")
                
            elif current_strata == "rust" or consecutive_failures > 0 or starvation_events > 1:
                at_risk_agents.append({
                    "agent_name": agent_name,
                    "reason": f"at_risk_due_to_{current_strata}_strata" if current_strata == "rust" else "at_risk_due_to_failures",
                    "current_strata": current_strata,
                    "consecutive_failures": consecutive_failures,
                    "starvation_events": starvation_events
                })
                logger.warning(f"AT RISK: Agent {agent_name} at risk of extinction")
                
        # Record extinct agents and remove them from the system
        for extinct_agent in extinct_agents:
            self.extinction_log.append(extinct_agent)
            # Remove the agent from cookie economy
            self._remove_extinct_agent(extinct_agent["agent_name"])
            
        # Record intervention agents
        for intervention_agent in intervention_agents:
            self.intervention_log.append(intervention_agent)
            
        # Create survival log entry
        survival_log_entry = {
            "evaluation_date": now.isoformat(),
            "agents_evaluated": len(agent_performance),
            "at_risk_agents": at_risk_agents,
            "extinct_agents": extinct_agents,
            "intervention_agents": intervention_agents,
            "probation_agents": probation_agents,
            "survival_metrics": {
                "extinction_threshold": EXTINCTION_THRESHOLD,
                "quality_improvement_requirement": QUALITY_IMPROVEMENT_REQUIREMENT
            }
        }
        
        self.survival_log.append(survival_log_entry)
        self.last_evaluation = now
        
        # Save updated data
        self._save_data()
        
        return survival_log_entry
        
    def _remove_extinct_agent(self, agent_name: str) -> bool:
        """
        Remove an extinct agent from the system.
        This is a permanent operation.
        
        Args:
            agent_name: Name of the agent to remove
            
        Returns:
            Success flag
        """
        logger.critical(f"REMOVING EXTINCT AGENT: {agent_name}")
        
        try:
            # Internally mark agent as extinct
            extinct_file_path = os.path.join(DATA_DIR, f"extinct_{agent_name}.json")
            
            # Save a snapshot of agent data before removal
            agent_data = self.cookie_economy.get_agent_performance(agent_name)
            
            with open(extinct_file_path, 'w') as f:
                json.dump({
                    "agent_name": agent_name,
                    "extinction_date": datetime.datetime.now().isoformat(),
                    "agent_data": agent_data,
                    "cookies_at_extinction": self.cookie_economy.get_agent_balance(agent_name)
                }, f, indent=2)
                
            # Remove from cookie economy - we can't fully remove but we can mark as extinct
            if agent_name in self.cookie_economy.agent_performance:
                self.cookie_economy.agent_performance[agent_name]["extinct"] = True
                self.cookie_economy.agent_performance[agent_name]["extinction_date"] = datetime.datetime.now().isoformat()
                self.cookie_economy.agent_balances[agent_name] = 0
                
            logger.critical(f"Agent {agent_name} successfully marked as EXTINCT")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove extinct agent {agent_name}: {e}")
            return False
            
    def get_extinction_log(self) -> List[Dict]:
        """
        Get the extinction log.
        
        Returns:
            List of extinction event dictionaries
        """
        return self.extinction_log
        
    def get_intervention_log(self) -> List[Dict]:
        """
        Get the intervention log.
        
        Returns:
            List of intervention event dictionaries
        """
        return self.intervention_log
        
    def get_survival_log(self) -> List[Dict]:
        """
        Get the survival log.
        
        Returns:
            List of survival evaluation dictionaries
        """
        return self.survival_log
        
    def get_agent_survival_status(self, agent_name: str) -> Dict:
        """
        Get an agent's survival status.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Survival status dictionary
        """
        agent_performance = self.cookie_economy.get_agent_performance(agent_name)
        
        if not agent_performance:
            return {"error": "Agent not found"}
            
        # Check if agent is extinct
        if agent_performance.get("extinct", False):
            return {
                "status": "extinct",
                "extinction_date": agent_performance.get("extinction_date", "unknown"),
                "reason": "Marked as extinct"
            }
            
        # Check if agent is on probation
        for probation in [p for log in self.survival_log for p in log.get("probation_agents", [])]:
            if probation["agent_name"] == agent_name:
                probation_end = datetime.datetime.fromisoformat(probation["probation_end_date"])
                if probation_end > datetime.datetime.now():
                    return {
                        "status": "probation",
                        "reason": probation["reason"],
                        "probation_end_date": probation["probation_end_date"],
                        "days_remaining": (probation_end - datetime.datetime.now()).days
                    }
        
        # Check if agent is at risk
        strata = agent_performance.get("strata", "bronze")
        consecutive_failures = agent_performance.get("consecutive_failures", 0)
        starvation_events = agent_performance.get("starvation_events", 0)
        extinction_risk = agent_performance.get("extinction_risk", False)
        
        if extinction_risk:
            return {
                "status": "critical",
                "reason": "Extinction risk flagged",
                "strata": strata,
                "consecutive_failures": consecutive_failures,
                "starvation_events": starvation_events
            }
        elif strata == "rust":
            return {
                "status": "endangered",
                "reason": "In lowest strata (rust)",
                "consecutive_failures": consecutive_failures,
                "starvation_events": starvation_events,
                "remaining_failures": EXTINCTION_THRESHOLD - consecutive_failures
            }
        elif consecutive_failures > 0 or starvation_events > 0:
            return {
                "status": "at_risk",
                "reason": "Performance issues detected",
                "strata": strata,
                "consecutive_failures": consecutive_failures,
                "starvation_events": starvation_events
            }
        else:
            # Determine based on strata
            status_map = {
                "gold": "thriving",
                "silver": "stable",
                "bronze": "adequate"
            }
            
            return {
                "status": status_map.get(strata, "unknown"),
                "strata": strata,
                "consecutive_failures": 0,
                "starvation_events": starvation_events
            }


# Singleton instance
_agent_survival_system = None

def get_agent_survival_system() -> AgentSurvivalSystem:
    """Get the agent survival system singleton instance."""
    global _agent_survival_system
    
    if _agent_survival_system is None:
        _agent_survival_system = AgentSurvivalSystem()
        
    return _agent_survival_system

def run_survival_evaluation():
    """Run the survival evaluation for all agents."""
    return get_agent_survival_system().run_survival_evaluation()

def get_extinction_log() -> List[Dict]:
    """Get the extinction log."""
    return get_agent_survival_system().get_extinction_log()

def get_intervention_log() -> List[Dict]:
    """Get the intervention log."""
    return get_agent_survival_system().get_intervention_log()

def get_survival_log() -> List[Dict]:
    """Get the survival log."""
    return get_agent_survival_system().get_survival_log()

def get_agent_survival_status(agent_name: str) -> Dict:
    """Get an agent's survival status."""
    return get_agent_survival_system().get_agent_survival_status(agent_name)

if __name__ == "__main__":
    # Run survival evaluation when executed directly
    result = run_survival_evaluation()
    if result:
        print(f"Survival evaluation complete: {result['agents_evaluated']} agents evaluated")
        print(f"Extinct agents: {len(result['extinct_agents'])}")
        print(f"At risk agents: {len(result['at_risk_agents'])}")
    else:
        print("Evaluation not performed - waiting for next cycle")