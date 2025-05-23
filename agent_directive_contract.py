"""
Universal Agent Directive Contract
Codename: "No Signal, No Engagement, No Second Chance"

This module implements the brutal agent directive that enforces engagement
requirements across all agents with MCP validation and self-termination logic.
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from cookie_economy import get_cookie_economy
import agent_survival_loop
import mcp_agent_feedback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File paths
DATA_DIR = "data/agent_contracts"
os.makedirs(DATA_DIR, exist_ok=True)

AGENT_CONTRACTS_PATH = os.path.join(DATA_DIR, "agent_contracts.json")
ENGAGEMENT_VALIDATION_PATH = os.path.join(DATA_DIR, "engagement_validation.json")
TERMINATION_LOG_PATH = os.path.join(DATA_DIR, "termination_log.json")


class InsightType(Enum):
    """Types of insights that count as valid engagement signals."""
    NEW_CITATION = "new_citation"
    COMPARATIVE_INSIGHT = "comparative_insight"
    EVENT_DRIVEN_SHIFT = "event_driven_shift"
    MEMORY_RECOVERY = "memory_recovery"
    USER_INTERACTION = "user_interaction"


class AgentStatus(Enum):
    """Agent lifecycle statuses."""
    ACTIVE = "active"
    WATCH = "watch"
    TERMINATION_SEQUENCE = "termination_sequence"
    TERMINATED = "terminated"
    REASSIGNED = "reassigned"


class AgentDirectiveContract:
    """
    Implements the Universal Agent Directive with brutal enforcement:
    'Gather insights that engage — or fail.'
    """
    
    def __init__(self):
        """Initialize the Agent Directive Contract system."""
        self.agent_contracts = {}
        self.engagement_validation = {}
        self.termination_log = []
        self.cookie_economy = get_cookie_economy()
        self.survival_system = agent_survival_loop.get_agent_survival_system()
        self.feedback_system = mcp_agent_feedback.get_mcp_agent_feedback()
        
        # Load existing data
        self._load_data()
        
        logger.warning("AGENT DIRECTIVE ACTIVATED: No signal. No engagement. No second chance.")
        
    def _load_data(self):
        """Load existing contract data from files."""
        try:
            if os.path.exists(AGENT_CONTRACTS_PATH):
                with open(AGENT_CONTRACTS_PATH, 'r') as f:
                    self.agent_contracts = json.load(f)
                    
            if os.path.exists(ENGAGEMENT_VALIDATION_PATH):
                with open(ENGAGEMENT_VALIDATION_PATH, 'r') as f:
                    self.engagement_validation = json.load(f)
                    
            if os.path.exists(TERMINATION_LOG_PATH):
                with open(TERMINATION_LOG_PATH, 'r') as f:
                    self.termination_log = json.load(f)
                    
            logger.info("Agent directive contract data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading agent directive contract data: {e}")
            self.agent_contracts = {}
            self.engagement_validation = {}
            self.termination_log = []
            
    def _save_data(self):
        """Save current contract data to files."""
        try:
            with open(AGENT_CONTRACTS_PATH, 'w') as f:
                json.dump(self.agent_contracts, f, indent=2)
                
            with open(ENGAGEMENT_VALIDATION_PATH, 'w') as f:
                json.dump(self.engagement_validation, f, indent=2)
                
            with open(TERMINATION_LOG_PATH, 'w') as f:
                json.dump(self.termination_log, f, indent=2)
                
            logger.info("Agent directive contract data saved successfully")
        except Exception as e:
            logger.error(f"Error saving agent directive contract data: {e}")
            
    def register_agent_contract(self, agent_name: str, domain: str, insight_type: str) -> Dict:
        """
        Register an agent with the Universal Directive Contract.
        
        Args:
            agent_name: Name of the agent
            domain: Assigned domain or insight area
            insight_type: Primary insight type the agent should surface
            
        Returns:
            Contract registration result
        """
        contract = {
            "agent_name": agent_name,
            "domain": domain,
            "insight_type": insight_type,
            "status": AgentStatus.ACTIVE.value,
            "creation_date": datetime.datetime.now().isoformat(),
            "cycles_completed": 0,
            "consecutive_failures": 0,
            "last_engagement": None,
            "last_insight": None,
            "engagement_metrics": {
                "click_rate": 0.0,
                "retention_time": 0.0,
                "share_rate": 0.0,
                "requery_rate": 0.0
            },
            "performance_history": [],
            "termination_warnings": 0
        }
        
        self.agent_contracts[agent_name] = contract
        
        # Also register in cookie economy
        self.cookie_economy.register_agent(agent_name)
        
        self._save_data()
        
        logger.info(f"Agent contract registered: {agent_name} assigned to {domain} for {insight_type}")
        
        return {
            "status": "registered",
            "contract": contract,
            "directive": "Gather insights that engage — or fail."
        }
        
    def validate_agent_performance(self, agent_name: str, insight_data: Dict, engagement_data: Optional[Dict] = None) -> Dict:
        """
        Validate agent performance against the Universal Directive.
        
        Args:
            agent_name: Name of the agent
            insight_data: Data about the insight generated
            engagement_data: Optional engagement metrics from MCP
            
        Returns:
            Validation result with survival decision
        """
        if agent_name not in self.agent_contracts:
            return {"error": "Agent not registered in directive contract"}
            
        contract = self.agent_contracts[agent_name]
        
        # Check if agent is already terminated
        if contract["status"] == AgentStatus.TERMINATED.value:
            return {"error": "Agent already terminated"}
            
        # Increment cycle counter
        contract["cycles_completed"] += 1
        
        # Validate insight quality
        insight_quality = insight_data.get("quality_score", 0.0)
        insight_type = insight_data.get("type", "unknown")
        
        # Check if insight meets engagement requirements
        engagement_valid = self._validate_engagement_requirements(insight_data, engagement_data)
        
        # Determine if this counts as actionable insight
        actionable_insight = self._is_insight_actionable(insight_data, engagement_data)
        
        # Update performance history
        performance_entry = {
            "cycle": contract["cycles_completed"],
            "timestamp": datetime.datetime.now().isoformat(),
            "insight_quality": insight_quality,
            "insight_type": insight_type,
            "actionable": actionable_insight,
            "engagement_valid": engagement_valid,
            "engagement_data": engagement_data
        }
        
        contract["performance_history"].append(performance_entry)
        
        # Limit history to last 10 cycles
        if len(contract["performance_history"]) > 10:
            contract["performance_history"] = contract["performance_history"][-10:]
            
        # Determine agent fate based on Universal Directive
        fate_decision = self._determine_agent_fate(agent_name, actionable_insight, engagement_valid)
        
        # Apply fate decision
        result = self._apply_fate_decision(agent_name, fate_decision)
        
        # Save updated contract
        self._save_data()
        
        return result
        
    def _validate_engagement_requirements(self, insight_data: Dict, engagement_data: Optional[Dict]) -> bool:
        """
        Validate if insight meets engagement requirements from the directive.
        
        Args:
            insight_data: Insight data
            engagement_data: Engagement metrics
            
        Returns:
            Whether engagement requirements are met
        """
        if not engagement_data:
            return False
            
        # Check minimum engagement thresholds
        click_rate = engagement_data.get("click_rate", 0.0)
        retention_time = engagement_data.get("retention_time", 0.0)
        share_rate = engagement_data.get("share_rate", 0.0)
        requery_rate = engagement_data.get("requery_rate", 0.0)
        
        # At least one engagement metric must exceed minimum threshold
        min_click_rate = 0.1  # 10% minimum click rate
        min_retention = 20.0  # 20 seconds minimum retention
        min_share_rate = 0.05  # 5% minimum share rate
        min_requery_rate = 0.03  # 3% minimum re-query rate
        
        return (
            click_rate >= min_click_rate or
            retention_time >= min_retention or
            share_rate >= min_share_rate or
            requery_rate >= min_requery_rate
        )
        
    def _is_insight_actionable(self, insight_data: Dict, engagement_data: Optional[Dict]) -> bool:
        """
        Determine if insight is actionable according to directive requirements.
        
        Args:
            insight_data: Insight data
            engagement_data: Engagement metrics
            
        Returns:
            Whether insight is actionable
        """
        insight_type = insight_data.get("type", "")
        content = insight_data.get("content", "")
        quality_score = insight_data.get("quality_score", 0.0)
        
        # Must meet quality threshold
        if quality_score < 0.85:
            return False
            
        # Check for specific actionable insight types
        actionable_types = [
            InsightType.NEW_CITATION.value,
            InsightType.COMPARATIVE_INSIGHT.value,
            InsightType.EVENT_DRIVEN_SHIFT.value,
            InsightType.MEMORY_RECOVERY.value,
            InsightType.USER_INTERACTION.value
        ]
        
        if insight_type not in actionable_types:
            return False
            
        # Check for specific actionable content patterns
        actionable_patterns = [
            "dropped from",
            "rose from",
            "new citation",
            "fresh quote",
            "sentiment increased",
            "sentiment decreased",
            "memory recovery",
            "after IPO",
            "compared to",
            "ranked #"
        ]
        
        content_actionable = any(pattern.lower() in content.lower() for pattern in actionable_patterns)
        
        # Must have actionable content OR strong engagement
        engagement_valid = self._validate_engagement_requirements(insight_data, engagement_data)
        
        return content_actionable or engagement_valid
        
    def _determine_agent_fate(self, agent_name: str, actionable_insight: bool, engagement_valid: bool) -> Dict:
        """
        Determine agent fate based on Universal Directive rules.
        
        Args:
            agent_name: Name of the agent
            actionable_insight: Whether insight was actionable
            engagement_valid: Whether engagement was valid
            
        Returns:
            Fate decision dictionary
        """
        contract = self.agent_contracts[agent_name]
        
        # Success case: both actionable insight and engagement
        if actionable_insight and engagement_valid:
            contract["consecutive_failures"] = 0  # Reset failure counter
            contract["last_engagement"] = datetime.datetime.now().isoformat()
            contract["last_insight"] = datetime.datetime.now().isoformat()
            contract["status"] = AgentStatus.ACTIVE.value
            
            return {
                "fate": "survival",
                "reason": "Agent survived. Delivered insight with engagement.",
                "action": "extend_for_2_cycles",
                "log_message": f"Agent {agent_name} survived. Delivered insight with engagement."
            }
            
        # Partial success: actionable insight but no engagement (warning)
        elif actionable_insight and not engagement_valid:
            contract["last_insight"] = datetime.datetime.now().isoformat()
            contract["termination_warnings"] += 1
            
            if contract["termination_warnings"] >= 2:
                return {
                    "fate": "watch_status",
                    "reason": "Actionable insight but no engagement. Final warning.",
                    "action": "move_to_watch",
                    "log_message": f"Agent {agent_name} on final warning. No engagement detected."
                }
            else:
                return {
                    "fate": "warning",
                    "reason": "Actionable insight but needs engagement.",
                    "action": "continue_with_warning",
                    "log_message": f"Agent {agent_name} warning. Needs engagement next cycle."
                }
                
        # Failure case: no actionable insight
        else:
            contract["consecutive_failures"] += 1
            
            # Immediate termination after 2 consecutive failures (per directive)
            if contract["consecutive_failures"] >= 2:
                return {
                    "fate": "termination",
                    "reason": "No new insight found in 2 consecutive fetch cycles.",
                    "action": "initiate_termination_sequence",
                    "log_message": f"Agent {agent_name} failed to gather signal. Termination sequence initiated."
                }
            else:
                contract["status"] = AgentStatus.WATCH.value
                return {
                    "fate": "watch_status",
                    "reason": "Failed to gather actionable insight.",
                    "action": "move_to_watch",
                    "log_message": f"Agent {agent_name} failed to gather signal. Moved to watch status."
                }
                
    def _apply_fate_decision(self, agent_name: str, fate_decision: Dict) -> Dict:
        """
        Apply the fate decision to the agent.
        
        Args:
            agent_name: Name of the agent
            fate_decision: Fate decision from determination
            
        Returns:
            Application result
        """
        contract = self.agent_contracts[agent_name]
        fate = fate_decision["fate"]
        
        if fate == "survival":
            # Agent survived - extend cookies and reset penalties
            self.cookie_economy.agent_balances[agent_name] = self.cookie_economy.agent_balances.get(agent_name, 0) + 5
            
            # Clear any pending penalties
            if agent_name in self.cookie_economy.agent_performance:
                self.cookie_economy.agent_performance[agent_name]["penalties"] = []
                
            logger.info(fate_decision["log_message"])
            
        elif fate == "warning":
            # Warning - record but continue
            logger.warning(fate_decision["log_message"])
            
        elif fate == "watch_status":
            # Move to watch status
            contract["status"] = AgentStatus.WATCH.value
            logger.warning(fate_decision["log_message"])
            
        elif fate == "termination":
            # Initiate termination sequence
            contract["status"] = AgentStatus.TERMINATION_SEQUENCE.value
            
            # Log termination event
            termination_event = {
                "agent_name": agent_name,
                "termination_date": datetime.datetime.now().isoformat(),
                "reason": fate_decision["reason"],
                "cycles_completed": contract["cycles_completed"],
                "last_engagement": contract.get("last_engagement"),
                "performance_summary": self._generate_performance_summary(agent_name)
            }
            
            self.termination_log.append(termination_event)
            
            # Remove from cookie economy (mark as extinct)
            self.survival_system._remove_extinct_agent(agent_name)
            
            logger.error(fate_decision["log_message"])
            
            # Check if MCP should create replacement agent
            replacement_decision = self._should_create_replacement(agent_name)
            
            if replacement_decision["create"]:
                logger.info(f"MCP authorized replacement agent creation: {replacement_decision['reason']}")
                
        return {
            "agent_name": agent_name,
            "fate": fate,
            "action": fate_decision["action"],
            "reason": fate_decision["reason"],
            "log_message": fate_decision["log_message"],
            "contract_status": contract["status"],
            "cycles_completed": contract["cycles_completed"],
            "consecutive_failures": contract["consecutive_failures"]
        }
        
    def _should_create_replacement(self, terminated_agent_name: str) -> Dict:
        """
        Determine if MCP should create a replacement agent after termination.
        
        Args:
            terminated_agent_name: Name of terminated agent
            
        Returns:
            Replacement decision
        """
        contract = self.agent_contracts[terminated_agent_name]
        domain = contract["domain"]
        
        # Check if domain still needs coverage
        active_agents_for_domain = [
            name for name, c in self.agent_contracts.items()
            if c["domain"] == domain and c["status"] == AgentStatus.ACTIVE.value
        ]
        
        # If no active agents for this domain, create replacement
        if len(active_agents_for_domain) == 0:
            return {
                "create": True,
                "reason": f"Domain {domain} has no active coverage after {terminated_agent_name} termination",
                "suggested_improvements": [
                    "Alter vector (new prompt)",
                    "Change insight type target",
                    "Modify comparator approach"
                ]
            }
            
        # Check if terminated agent had unique value
        insight_type = contract["insight_type"]
        agents_with_same_type = [
            name for name, c in self.agent_contracts.items()
            if c["insight_type"] == insight_type and c["status"] == AgentStatus.ACTIVE.value
        ]
        
        if len(agents_with_same_type) == 0:
            return {
                "create": True,
                "reason": f"No active agents providing {insight_type} insights after {terminated_agent_name} termination",
                "suggested_improvements": [
                    "Enhanced engagement detection",
                    "Improved content analysis",
                    "Better timing algorithms"
                ]
            }
            
        return {
            "create": False,
            "reason": f"Domain {domain} still has adequate coverage"
        }
        
    def _generate_performance_summary(self, agent_name: str) -> Dict:
        """
        Generate performance summary for terminated agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Performance summary
        """
        contract = self.agent_contracts[agent_name]
        history = contract["performance_history"]
        
        if not history:
            return {"error": "No performance history"}
            
        total_cycles = len(history)
        actionable_cycles = sum(1 for h in history if h.get("actionable", False))
        engaged_cycles = sum(1 for h in history if h.get("engagement_valid", False))
        avg_quality = sum(h.get("insight_quality", 0) for h in history) / total_cycles
        
        return {
            "total_cycles": total_cycles,
            "actionable_cycles": actionable_cycles,
            "engaged_cycles": engaged_cycles,
            "actionable_rate": actionable_cycles / total_cycles if total_cycles > 0 else 0,
            "engagement_rate": engaged_cycles / total_cycles if total_cycles > 0 else 0,
            "average_quality": avg_quality,
            "consecutive_failures_at_termination": contract["consecutive_failures"],
            "termination_warnings": contract["termination_warnings"]
        }
        
    def get_agent_contract_status(self, agent_name: str) -> Dict:
        """
        Get current contract status for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Contract status
        """
        if agent_name not in self.agent_contracts:
            return {"error": "Agent not registered"}
            
        contract = self.agent_contracts[agent_name]
        performance_summary = self._generate_performance_summary(agent_name)
        
        return {
            "agent_name": agent_name,
            "contract": contract,
            "performance_summary": performance_summary,
            "directive_compliance": self._check_directive_compliance(agent_name)
        }
        
    def _check_directive_compliance(self, agent_name: str) -> Dict:
        """
        Check agent compliance with Universal Directive.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Compliance status
        """
        contract = self.agent_contracts[agent_name]
        history = contract["performance_history"]
        
        if len(history) < 2:
            return {"status": "insufficient_data"}
            
        recent_history = history[-2:]  # Last 2 cycles
        
        # Check for consecutive failures
        consecutive_non_actionable = all(not h.get("actionable", False) for h in recent_history)
        consecutive_non_engaging = all(not h.get("engagement_valid", False) for h in recent_history)
        
        if consecutive_non_actionable:
            return {
                "status": "violation",
                "rule": "No new insight found in 2 consecutive fetch cycles",
                "recommendation": "Immediate termination required"
            }
            
        if consecutive_non_engaging and len(history) >= 5:
            return {
                "status": "warning",
                "rule": "No user engagement recorded",
                "recommendation": "Monitor next cycle closely"
            }
            
        return {
            "status": "compliant",
            "rule": "Meeting directive requirements",
            "recommendation": "Continue current operation"
        }
        
    def get_system_banner_message(self) -> str:
        """
        Get the system banner message with current directive status.
        
        Returns:
            Banner message
        """
        active_agents = sum(1 for c in self.agent_contracts.values() if c["status"] == AgentStatus.ACTIVE.value)
        watch_agents = sum(1 for c in self.agent_contracts.values() if c["status"] == AgentStatus.WATCH.value)
        terminated_agents = len(self.termination_log)
        
        return f"""
    ═══════════════════════════════════════════════════════════════════
                      UNIVERSAL AGENT DIRECTIVE ACTIVE
                  "No signal. No engagement. No second chance."
    ═══════════════════════════════════════════════════════════════════
    Active Agents: {active_agents} | Watch Status: {watch_agents} | Terminated: {terminated_agents}
    Directive: Gather insights that engage — or fail.
    ═══════════════════════════════════════════════════════════════════
        """


# Singleton instance
_agent_directive_contract = None

def get_agent_directive_contract() -> AgentDirectiveContract:
    """Get the Agent Directive Contract singleton instance."""
    global _agent_directive_contract
    
    if _agent_directive_contract is None:
        _agent_directive_contract = AgentDirectiveContract()
        
    return _agent_directive_contract

def register_agent_contract(agent_name: str, domain: str, insight_type: str) -> Dict:
    """Register an agent with the Universal Directive Contract."""
    return get_agent_directive_contract().register_agent_contract(agent_name, domain, insight_type)

def validate_agent_performance(agent_name: str, insight_data: Dict, engagement_data: Optional[Dict] = None) -> Dict:
    """Validate agent performance against the Universal Directive."""
    return get_agent_directive_contract().validate_agent_performance(agent_name, insight_data, engagement_data)

def get_agent_contract_status(agent_name: str) -> Dict:
    """Get current contract status for an agent."""
    return get_agent_directive_contract().get_agent_contract_status(agent_name)

def get_system_banner_message() -> str:
    """Get the system banner message with current directive status."""
    return get_agent_directive_contract().get_system_banner_message()

if __name__ == "__main__":
    # Display system banner when executed directly
    print(get_system_banner_message())