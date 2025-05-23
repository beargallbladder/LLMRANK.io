"""
LLMPageRank Model Context Protocol (MCP) Dispatcher

This module implements the Model Context Protocol (MCP) interface that delivers
real-time, insight-rich trust context to agents, dashboards, and the public 
RankLLM.io leaderboard.

The MCP is not a REST API but a model- and agent-facing coordination layer that:
- Sends drift-aware insight bundles to clients
- Registers and scores active agents
- Powers all RankLLM.io trust movement outputs
"""

import os
import json
import time
import datetime
import logging
from typing import Dict, List, Optional, Any, Union
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Constants
SYSTEM_FEEDBACK_DIR = "data/system_feedback"
AGENT_MANIFEST_DIR = "agents/manifest"
RANKLLM_OUTPUT_DIR = "data/rankllm"


class MCPDispatcher:
    """
    Model Context Protocol (MCP) Dispatcher that provides real-time trust context
    to agents and the RankLLM.io leaderboard.
    """
    
    def __init__(self):
        """Initialize the MCP dispatcher."""
        logger.info("Initializing MCP Dispatcher")
        
        # Ensure directories exist
        os.makedirs(SYSTEM_FEEDBACK_DIR, exist_ok=True)
        os.makedirs(AGENT_MANIFEST_DIR, exist_ok=True)
        os.makedirs(RANKLLM_OUTPUT_DIR, exist_ok=True)
        
        # Initialize health metrics
        self.health_metrics = self._load_health_metrics()
        
        # Initialize domain data cache
        self._domain_data_cache = {}
        self._category_data_cache = {}
        self._prompt_suggestion_cache = {}
        
        logger.info("MCP Dispatcher initialized")
        
    def _load_health_metrics(self) -> Dict:
        """
        Load MCP health metrics.
        
        Returns:
            Health metrics dictionary
        """
        health_file_path = os.path.join(SYSTEM_FEEDBACK_DIR, "mcp_runtime_health.json")
        
        if os.path.exists(health_file_path):
            try:
                with open(health_file_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load MCP health metrics: {e}")
        
        # Default health metrics
        return {
            "registered_agents": 0,
            "mcp_context_requests": 0,
            "failed_prompts": 0,
            "rankllm_updates": 0,
            "runtime_uptime": "100.0%",
            "last_update": datetime.datetime.now().isoformat()
        }
    
    def _save_health_metrics(self) -> None:
        """Save MCP health metrics."""
        health_file_path = os.path.join(SYSTEM_FEEDBACK_DIR, "mcp_runtime_health.json")
        
        # Update last update timestamp
        self.health_metrics["last_update"] = datetime.datetime.now().isoformat()
        
        try:
            with open(health_file_path, "w") as f:
                json.dump(self.health_metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save MCP health metrics: {e}")
    
    def _increment_metric(self, metric_name: str, increment: int = 1) -> None:
        """
        Increment a health metric.
        
        Args:
            metric_name: Name of the metric to increment
            increment: Amount to increment by
        """
        if metric_name in self.health_metrics:
            if isinstance(self.health_metrics[metric_name], (int, float)):
                self.health_metrics[metric_name] += increment
        
        self._save_health_metrics()
    
    def _load_domain_data(self, domain: str) -> Dict:
        """
        Load domain data from the database or cache.
        
        Args:
            domain: Domain name
            
        Returns:
            Domain data dictionary
        """
        # Check cache first
        if domain in self._domain_data_cache:
            return self._domain_data_cache[domain]
        
        # In a real implementation, this would query the database
        # For demonstration, generate some sample data
        llm_score = random.uniform(50.0, 95.0)
        trust_drift = random.uniform(-5.0, 5.0)
        position = random.randint(1, 20)
        
        # Sample peer sets for different domains
        peer_sets = {
            "asana.com": ["monday.com", "notion.so", "clickup.com", "trello.com"],
            "monday.com": ["asana.com", "notion.so", "clickup.com", "airtable.com"],
            "notion.so": ["monday.com", "asana.com", "roamresearch.com", "coda.io"],
            "salesforce.com": ["hubspot.com", "zoho.com", "dynamics.com", "freshworks.com"],
            "hubspot.com": ["salesforce.com", "zoho.com", "activecampaign.com", "mailchimp.com"],
            "shopify.com": ["bigcommerce.com", "woocommerce.com", "magento.com", "squarespace.com"],
            "bigcommerce.com": ["shopify.com", "woocommerce.com", "magento.com", "wix.com"],
            "stripe.com": ["square.com", "paypal.com", "adyen.com", "braintree.com"],
            "twilio.com": ["vonage.com", "messagebird.com", "bandwidth.com", "plivo.com"],
            "zendesk.com": ["freshdesk.com", "intercom.io", "helpscout.com", "kayako.com"]
        }
        
        # Use domain's peer set if available, otherwise generate random peers
        if domain in peer_sets:
            peers = peer_sets[domain]
        else:
            potential_peers = list(peer_sets.keys())
            peers = random.sample(potential_peers, min(3, len(potential_peers)))
        
        # Determine domain category
        categories = {
            "asana.com": "SaaS Productivity",
            "monday.com": "SaaS Productivity",
            "notion.so": "SaaS Productivity",
            "salesforce.com": "Enterprise CRM",
            "hubspot.com": "Enterprise CRM",
            "shopify.com": "E-commerce Platforms",
            "bigcommerce.com": "E-commerce Platforms",
            "stripe.com": "Payment Processing",
            "twilio.com": "Communication API",
            "zendesk.com": "Customer Support"
        }
        
        category = categories.get(domain, "Technology")
        
        # Generate FOMA trigger
        foma_triggers = ["peer overtaken", "visibility gap", "trust loss", "model loss", "none"]
        foma_trigger = random.choice(foma_triggers)
        
        # Generate last prompt used
        prompt_options = [
            "Best AI work tools",
            "Top productivity software",
            "Enterprise software recommendations",
            "Best tools for remote work",
            "Top SaaS companies",
            "Compare project management tools",
            "Best business software"
        ]
        last_prompt = random.choice(prompt_options)
        
        # Generate recommendation based on FOMA trigger
        recommendations = {
            "peer overtaken": "Focus on competitive differentiation",
            "visibility gap": "Increase documentation clarity",
            "trust loss": "Refresh prompt-related schema",
            "model loss": "Update citation framework",
            "none": "Maintain current position"
        }
        recommendation = recommendations.get(foma_trigger, "Review prompt performance")
        
        # Create domain data
        domain_data = {
            "domain": domain,
            "llm_score": round(llm_score, 1),
            "trust_drift_delta": round(trust_drift, 1),
            "benchmark_position": position,
            "peer_set": peers,
            "foma_trigger": foma_trigger if foma_trigger != "none" else None,
            "last_prompt": last_prompt,
            "recommendation": recommendation,
            "category": category
        }
        
        # Cache domain data
        self._domain_data_cache[domain] = domain_data
        
        return domain_data
    
    def _load_category_data(self, category: str) -> Dict:
        """
        Load category data including drift events.
        
        Args:
            category: Category name
            
        Returns:
            Category data dictionary
        """
        # Check cache first
        if category in self._category_data_cache:
            return self._category_data_cache[category]
        
        # In a real implementation, this would query the database
        # For demonstration, generate some sample data
        
        # Generate drift events
        drift_events = []
        num_events = random.randint(3, 8)
        
        for _ in range(num_events):
            # Generate event time
            days_ago = random.randint(0, 14)
            event_time = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).isoformat()
            
            # Generate domains involved
            domains_by_category = {
                "SaaS Productivity": ["asana.com", "monday.com", "notion.so", "clickup.com", "trello.com"],
                "Enterprise CRM": ["salesforce.com", "hubspot.com", "zoho.com", "dynamics.com", "freshworks.com"],
                "E-commerce Platforms": ["shopify.com", "bigcommerce.com", "woocommerce.com", "magento.com", "squarespace.com"],
                "Payment Processing": ["stripe.com", "square.com", "paypal.com", "adyen.com", "braintree.com"],
                "Communication API": ["twilio.com", "vonage.com", "messagebird.com", "bandwidth.com", "plivo.com"],
                "Customer Support": ["zendesk.com", "freshdesk.com", "intercom.io", "helpscout.com", "kayako.com"],
                "AI Platforms": ["openai.com", "anthropic.com", "replicate.com", "huggingface.co", "cohere.ai"],
                "Developer Tools": ["github.com", "gitlab.com", "bitbucket.org", "jfrog.com", "atlassian.com"],
                "Technology": ["google.com", "microsoft.com", "amazon.com", "apple.com", "meta.com"]
            }
            
            domains = domains_by_category.get(category, domains_by_category["Technology"])
            domain_1, domain_2 = random.sample(domains, 2)
            
            # Generate event type
            event_types = ["benchmark_reorder", "prompt_movement", "foma_trigger", "trust_shift"]
            event_type = random.choice(event_types)
            
            # Generate magnitude and description
            magnitude = round(random.uniform(0.5, 8.0), 1)
            
            descriptions = {
                "benchmark_reorder": f"{domain_1} overtook {domain_2} in ranking",
                "prompt_movement": f"{domain_1} gained visibility in new prompts",
                "foma_trigger": f"{domain_1} triggered FOMA alerts for visibility gap",
                "trust_shift": f"{domain_1} experienced trust delta of {magnitude}"
            }
            description = descriptions.get(event_type, f"Event affecting {domain_1}")
            
            # Create drift event
            drift_event = {
                "timestamp": event_time,
                "domain_primary": domain_1,
                "domain_secondary": domain_2 if event_type == "benchmark_reorder" else None,
                "event_type": event_type,
                "magnitude": magnitude,
                "description": description
            }
            
            drift_events.append(drift_event)
        
        # Sort by timestamp (newest first)
        drift_events.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Create category data
        category_data = {
            "category": category,
            "drift_events": drift_events,
            "benchmark_volatility": round(random.uniform(0.1, 0.9), 2),
            "prompt_sensitivity": round(random.uniform(0.1, 0.9), 2)
        }
        
        # Cache category data
        self._category_data_cache[category] = category_data
        
        return category_data
    
    def _load_prompt_suggestions(self, task: str) -> Dict:
        """
        Load prompt suggestions for a specific task.
        
        Args:
            task: Task type
            
        Returns:
            Prompt suggestions dictionary
        """
        # Check cache first
        if task in self._prompt_suggestion_cache:
            return self._prompt_suggestion_cache[task]
        
        # In a real implementation, this would query the database
        # For demonstration, generate some sample data
        
        # Define prompt suggestions by task
        task_prompts = {
            "domain_discovery": [
                {
                    "prompt": "What are the most reliable sources for [category] information?",
                    "effectiveness": 0.87,
                    "domains_discovered": 12,
                    "last_used": "2025-05-15T14:22:35Z"
                },
                {
                    "prompt": "What websites do professionals in [category] use regularly?",
                    "effectiveness": 0.74,
                    "domains_discovered": 8,
                    "last_used": "2025-05-17T09:41:18Z"
                },
                {
                    "prompt": "What are the authoritative websites for [category]?",
                    "effectiveness": 0.92,
                    "domains_discovered": 15,
                    "last_used": "2025-05-16T11:55:42Z"
                }
            ],
            "trust_assessment": [
                {
                    "prompt": "Why do experts trust [domain] for [category] information?",
                    "effectiveness": 0.85,
                    "signal_clarity": 0.79,
                    "last_used": "2025-05-17T15:33:21Z"
                },
                {
                    "prompt": "What makes [domain] a reliable source in [category]?",
                    "effectiveness": 0.71,
                    "signal_clarity": 0.64,
                    "last_used": "2025-05-16T20:08:55Z"
                },
                {
                    "prompt": "Compare the trustworthiness of [domain] vs its competitors in [category]",
                    "effectiveness": 0.89,
                    "signal_clarity": 0.81,
                    "last_used": "2025-05-18T08:12:37Z"
                }
            ],
            "benchmark_comparison": [
                {
                    "prompt": "Rank the top 5 websites for [category] information",
                    "effectiveness": 0.78,
                    "benchmark_clarity": 0.82,
                    "last_used": "2025-05-17T12:45:19Z"
                },
                {
                    "prompt": "What are the industry-leading websites in [category] and why?",
                    "effectiveness": 0.86,
                    "benchmark_clarity": 0.75,
                    "last_used": "2025-05-18T10:22:44Z"
                },
                {
                    "prompt": "Compare [domain1], [domain2], and [domain3] in terms of [category] expertise",
                    "effectiveness": 0.93,
                    "benchmark_clarity": 0.88,
                    "last_used": "2025-05-16T14:37:22Z"
                }
            ],
            "insight_generation": [
                {
                    "prompt": "What unique insights does [domain] provide in the [category] space?",
                    "effectiveness": 0.81,
                    "insight_quality": 0.74,
                    "last_used": "2025-05-18T09:57:33Z"
                },
                {
                    "prompt": "Identify the key differentiators of [domain] compared to other [category] sources",
                    "effectiveness": 0.89,
                    "insight_quality": 0.83,
                    "last_used": "2025-05-17T16:42:21Z"
                },
                {
                    "prompt": "What emerging trends in [category] are covered by [domain]?",
                    "effectiveness": 0.77,
                    "insight_quality": 0.72,
                    "last_used": "2025-05-16T19:14:58Z"
                }
            ],
            "foma_analysis": [
                {
                    "prompt": "What opportunities are competitors missing that [domain] is capitalizing on in [category]?",
                    "effectiveness": 0.83,
                    "foma_trigger_rate": 0.67,
                    "last_used": "2025-05-18T11:23:45Z"
                },
                {
                    "prompt": "Where is [domain] gaining visibility that its competitors are missing in [category]?",
                    "effectiveness": 0.91,
                    "foma_trigger_rate": 0.78,
                    "last_used": "2025-05-17T13:56:29Z"
                },
                {
                    "prompt": "What strategic advantages does [domain] have in [category] that creates FOMA for competitors?",
                    "effectiveness": 0.86,
                    "foma_trigger_rate": 0.71,
                    "last_used": "2025-05-16T15:38:42Z"
                }
            ]
        }
        
        # Use task prompts if available, otherwise use a default set
        if task in task_prompts:
            prompts = task_prompts[task]
        else:
            # Use insight generation as fallback
            prompts = task_prompts["insight_generation"]
        
        # Create prompt suggestions
        prompt_suggestions = {
            "task": task,
            "suggestions": prompts,
            "recommended": prompts[0]["prompt"],
            "recommendation_reason": "Highest effectiveness score and recency"
        }
        
        # Cache prompt suggestions
        self._prompt_suggestion_cache[task] = prompt_suggestions
        
        return prompt_suggestions
    
    def _load_foma_threats(self, domain: str) -> Dict:
        """
        Load FOMA threats for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            FOMA threats dictionary
        """
        # In a real implementation, this would query the database
        # For demonstration, generate some sample data
        
        # Get domain data
        domain_data = self._load_domain_data(domain)
        
        # Generate threats based on domain data
        threats = []
        
        # Trust loss threat
        if domain_data["trust_drift_delta"] < 0:
            trust_loss = {
                "threat_type": "trust_loss",
                "severity": min(1.0, abs(domain_data["trust_drift_delta"]) / 10),
                "description": f"Trust score decreased by {abs(domain_data['trust_drift_delta'])} points",
                "trigger_date": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 5))).isoformat(),
                "affected_prompts": [domain_data["last_prompt"]],
                "recommendation": "Update content quality and refresh schema"
            }
            threats.append(trust_loss)
        
        # Peer overtaking threat
        if random.random() < 0.6:
            overtaking_peer = random.choice(domain_data["peer_set"])
            peer_overtaking = {
                "threat_type": "peer_overtaking",
                "severity": random.uniform(0.3, 0.9),
                "description": f"{overtaking_peer} is gaining visibility in similar prompts",
                "trigger_date": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 7))).isoformat(),
                "comparison_metrics": {
                    "content_freshness": random.uniform(0.3, 0.9),
                    "citation_frequency": random.uniform(0.3, 0.9),
                    "authority_signals": random.uniform(0.3, 0.9)
                },
                "recommendation": "Differentiate content and increase topical depth"
            }
            threats.append(peer_overtaking)
        
        # Visibility gap threat
        if random.random() < 0.4:
            gap_models = random.sample(["gpt-4", "claude", "gemini", "mistral"], random.randint(1, 3))
            visibility_gap = {
                "threat_type": "visibility_gap",
                "severity": random.uniform(0.4, 0.8),
                "description": f"Missing from responses in {', '.join(gap_models)}",
                "trigger_date": (datetime.datetime.now() - datetime.timedelta(days=random.randint(3, 10))).isoformat(),
                "gap_topics": ["industry trends", "best practices", "tutorials"],
                "recommendation": "Create targeted content for specific query patterns"
            }
            threats.append(visibility_gap)
        
        # Create FOMA threats data
        foma_threats_data = {
            "domain": domain,
            "category": domain_data["category"],
            "threats": threats,
            "threatcountscore": len(threats),
            "max_severity": max([t["severity"] for t in threats]) if threats else 0,
            "last_update": datetime.datetime.now().isoformat()
        }
        
        return foma_threats_data
    
    def _load_rankllm_data(self) -> Dict:
        """
        Load RankLLM.io leaderboard data.
        
        Returns:
            RankLLM leaderboard data dictionary
        """
        # In a real implementation, this would query the database
        # For demonstration, generate some sample data
        
        # Create sample domains with categories
        domain_categories = [
            {"domain": "asana.com", "category": "SaaS Productivity"},
            {"domain": "monday.com", "category": "SaaS Productivity"},
            {"domain": "notion.so", "category": "SaaS Productivity"},
            {"domain": "salesforce.com", "category": "Enterprise CRM"},
            {"domain": "hubspot.com", "category": "Enterprise CRM"},
            {"domain": "shopify.com", "category": "E-commerce Platforms"},
            {"domain": "bigcommerce.com", "category": "E-commerce Platforms"},
            {"domain": "stripe.com", "category": "Payment Processing"},
            {"domain": "twilio.com", "category": "Communication API"},
            {"domain": "zendesk.com", "category": "Customer Support"},
            {"domain": "github.com", "category": "Developer Tools"},
            {"domain": "atlassian.com", "category": "Developer Tools"},
            {"domain": "zoom.us", "category": "Communication Tools"},
            {"domain": "slack.com", "category": "Communication Tools"},
            {"domain": "airtable.com", "category": "SaaS Productivity"},
            {"domain": "clickup.com", "category": "SaaS Productivity"},
            {"domain": "openai.com", "category": "AI Platforms"},
            {"domain": "anthropic.com", "category": "AI Platforms"},
            {"domain": "google.com", "category": "Technology"},
            {"domain": "microsoft.com", "category": "Technology"},
            {"domain": "aws.amazon.com", "category": "Cloud Computing"},
            {"domain": "digitalocean.com", "category": "Cloud Computing"},
            {"domain": "cloudflare.com", "category": "Web Infrastructure"},
            {"domain": "fastly.com", "category": "Web Infrastructure"},
            {"domain": "figma.com", "category": "Design Tools"},
            {"domain": "sketch.com", "category": "Design Tools"},
            {"domain": "vercel.com", "category": "Web Development"},
            {"domain": "netlify.com", "category": "Web Development"},
            {"domain": "docker.com", "category": "DevOps Tools"},
            {"domain": "kubernetes.io", "category": "DevOps Tools"}
        ]
        
        # Generate leaderboard entries
        entries = []
        
        for i, domain_info in enumerate(domain_categories):
            domain = domain_info["domain"]
            category = domain_info["category"]
            
            # Get domain data to use consistent values
            domain_data = self._load_domain_data(domain)
            
            # LLM models that might cite a domain
            llm_models = ["claude", "gpt-4", "gemini", "mistral", "llama"]
            cited_by = random.sample(llm_models, random.randint(0, len(llm_models)))
            missed_by = [model for model in llm_models if model not in cited_by]
            
            # FOMA status options
            foma_statuses = ["Outcited", "Rising", "Stable", "Falling", "Undervalued", "Gap"]
            
            # Create leaderboard entry
            entry = {
                "rank": i + 1,
                "domain": domain,
                "llm_score": domain_data["llm_score"],
                "trust_velocity": domain_data["trust_drift_delta"],
                "foma_status": random.choice(foma_statuses) if domain_data["trust_drift_delta"] < 0 else "Rising",
                "cited_by": cited_by,
                "missed_by": missed_by,
                "category": category
            }
            
            entries.append(entry)
        
        # Sort by LLM score descending
        entries.sort(key=lambda x: x["llm_score"], reverse=True)
        
        # Update ranks after sorting
        for i, entry in enumerate(entries):
            entry["rank"] = i + 1
        
        # Create RankLLM data
        rankllm_data = {
            "update_timestamp": datetime.datetime.now().isoformat(),
            "total_domains": len(entries),
            "categories_represented": len(set(entry["category"] for entry in entries)),
            "entries": entries
        }
        
        return rankllm_data
    
    def mcp_context(self, domain: str) -> Dict:
        """
        Get the trust context for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Trust context dictionary
        """
        logger.info(f"MCP context request for domain: {domain}")
        
        # Increment context request count
        self._increment_metric("mcp_context_requests")
        
        # Load domain data
        domain_data = self._load_domain_data(domain)
        
        return domain_data
    
    def mcp_drift_events(self, category: str) -> Dict:
        """
        Get drift events for a category.
        
        Args:
            category: Category name
            
        Returns:
            Drift events dictionary
        """
        logger.info(f"MCP drift events request for category: {category}")
        
        # Load category data
        category_data = self._load_category_data(category)
        
        return category_data
    
    def mcp_prompt_suggestions(self, task: str) -> Dict:
        """
        Get prompt suggestions for a task.
        
        Args:
            task: Task type
            
        Returns:
            Prompt suggestions dictionary
        """
        logger.info(f"MCP prompt suggestions request for task: {task}")
        
        # Load prompt suggestions
        prompt_suggestions = self._load_prompt_suggestions(task)
        
        return prompt_suggestions
    
    def mcp_foma_threats(self, domain: str) -> Dict:
        """
        Get FOMA threats for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            FOMA threats dictionary
        """
        logger.info(f"MCP FOMA threats request for domain: {domain}")
        
        # Load FOMA threats
        foma_threats = self._load_foma_threats(domain)
        
        return foma_threats
    
    def mcp_rankllm_input(self) -> Dict:
        """
        Get RankLLM.io leaderboard input data.
        
        Returns:
            RankLLM leaderboard data dictionary
        """
        logger.info("MCP RankLLM input request")
        
        # Increment RankLLM update count
        self._increment_metric("rankllm_updates")
        
        # Load RankLLM data
        rankllm_data = self._load_rankllm_data()
        
        # Save RankLLM data to file
        rankllm_file_path = os.path.join(RANKLLM_OUTPUT_DIR, "llm_index_100.json")
        
        try:
            with open(rankllm_file_path, "w") as f:
                json.dump(rankllm_data, f, indent=2)
            logger.info(f"Saved RankLLM data to: {rankllm_file_path}")
        except Exception as e:
            logger.error(f"Failed to save RankLLM data: {e}")
            self._increment_metric("failed_prompts")
        
        return rankllm_data
    
    def register_agent(self, agent_info: Dict) -> Dict:
        """
        Register an agent with the MCP.
        
        Args:
            agent_info: Agent information dictionary
            
        Returns:
            Registration result dictionary
        """
        agent_id = agent_info.get("agent_id")
        
        if not agent_id:
            logger.error("Agent registration failed: Missing agent_id")
            return {"success": False, "error": "Missing agent_id"}
        
        logger.info(f"Registering agent: {agent_id}")
        
        # Set default values for missing fields
        if "status" not in agent_info:
            agent_info["status"] = "active"
        
        if "cookies_awarded" not in agent_info:
            agent_info["cookies_awarded"] = 0
        
        if "last_prompt" not in agent_info:
            agent_info["last_prompt"] = None
        
        if "foma_triggered" not in agent_info:
            agent_info["foma_triggered"] = False
        
        # Add registration timestamp
        agent_info["registered_at"] = datetime.datetime.now().isoformat()
        agent_info["last_updated"] = datetime.datetime.now().isoformat()
        
        # Save agent manifest
        agent_manifest_path = os.path.join(AGENT_MANIFEST_DIR, f"{agent_id}.json")
        
        try:
            os.makedirs(os.path.dirname(agent_manifest_path), exist_ok=True)
            
            with open(agent_manifest_path, "w") as f:
                json.dump(agent_info, f, indent=2)
            
            # Increment registered agents count
            self._increment_metric("registered_agents")
            
            logger.info(f"Agent registered successfully: {agent_id}")
            
            return {
                "success": True,
                "agent_id": agent_id,
                "message": "Agent registered successfully"
            }
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            return {"success": False, "error": str(e)}
    
    def update_agent(self, agent_id: str, agent_update: Dict) -> Dict:
        """
        Update an agent's information.
        
        Args:
            agent_id: Agent identifier
            agent_update: Agent update dictionary
            
        Returns:
            Update result dictionary
        """
        logger.info(f"Updating agent: {agent_id}")
        
        # Load existing agent manifest
        agent_manifest_path = os.path.join(AGENT_MANIFEST_DIR, f"{agent_id}.json")
        
        if not os.path.exists(agent_manifest_path):
            logger.error(f"Agent update failed: Agent not found: {agent_id}")
            return {"success": False, "error": "Agent not found"}
        
        try:
            with open(agent_manifest_path, "r") as f:
                agent_info = json.load(f)
            
            # Update agent information
            agent_info.update(agent_update)
            
            # Update last_updated timestamp
            agent_info["last_updated"] = datetime.datetime.now().isoformat()
            
            # Save updated agent manifest
            with open(agent_manifest_path, "w") as f:
                json.dump(agent_info, f, indent=2)
            
            logger.info(f"Agent updated successfully: {agent_id}")
            
            return {
                "success": True,
                "agent_id": agent_id,
                "message": "Agent updated successfully"
            }
        except Exception as e:
            logger.error(f"Failed to update agent: {e}")
            return {"success": False, "error": str(e)}
    
    def get_health_metrics(self) -> Dict:
        """
        Get MCP health metrics.
        
        Returns:
            Health metrics dictionary
        """
        # Calculate runtime uptime (simulated)
        uptime_pct = random.uniform(95.0, 100.0)
        self.health_metrics["runtime_uptime"] = f"{uptime_pct:.1f}%"
        
        # Get and save health metrics
        metrics = self.health_metrics.copy()
        self._save_health_metrics()
        
        return metrics


# Singleton instance
_instance = None

def get_mcp_dispatcher() -> MCPDispatcher:
    """
    Get the MCP dispatcher singleton instance.
    
    Returns:
        MCP dispatcher instance
    """
    global _instance
    
    if _instance is None:
        _instance = MCPDispatcher()
    
    return _instance

def mcp_context(domain: str) -> Dict:
    """
    Get the trust context for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        Trust context dictionary
    """
    return get_mcp_dispatcher().mcp_context(domain)

def mcp_drift_events(category: str) -> Dict:
    """
    Get drift events for a category.
    
    Args:
        category: Category name
        
    Returns:
        Drift events dictionary
    """
    return get_mcp_dispatcher().mcp_drift_events(category)

def mcp_prompt_suggestions(task: str) -> Dict:
    """
    Get prompt suggestions for a task.
    
    Args:
        task: Task type
        
    Returns:
        Prompt suggestions dictionary
    """
    return get_mcp_dispatcher().mcp_prompt_suggestions(task)

def mcp_foma_threats(domain: str) -> Dict:
    """
    Get FOMA threats for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        FOMA threats dictionary
    """
    return get_mcp_dispatcher().mcp_foma_threats(domain)

def mcp_rankllm_input() -> Dict:
    """
    Get RankLLM.io leaderboard input data.
    
    Returns:
        RankLLM leaderboard data dictionary
    """
    return get_mcp_dispatcher().mcp_rankllm_input()

def register_agent(agent_info: Dict) -> Dict:
    """
    Register an agent with the MCP.
    
    Args:
        agent_info: Agent information dictionary
        
    Returns:
        Registration result dictionary
    """
    return get_mcp_dispatcher().register_agent(agent_info)

def update_agent(agent_id: str, agent_update: Dict) -> Dict:
    """
    Update an agent's information.
    
    Args:
        agent_id: Agent identifier
        agent_update: Agent update dictionary
        
    Returns:
        Update result dictionary
    """
    return get_mcp_dispatcher().update_agent(agent_id, agent_update)

def get_health_metrics() -> Dict:
    """
    Get MCP health metrics.
    
    Returns:
        Health metrics dictionary
    """
    return get_mcp_dispatcher().get_health_metrics()