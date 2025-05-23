"""
Model Context Protocol (MCP) Integration

This module connects the LLMPageRank Insight Engine to the Model Context Protocol (MCP)
to enable standardized access to multiple LLM models and facilitate agent coordination.
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Union

import domain_memory_tracker
import notification_agent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SIGNIFICANT_DELTA_THRESHOLD = 3  # Minimum rank change to be considered significant
MCP_SYNC_INTERVAL_HOURS = 6  # How often to sync with MCP

class MCPIntegration:
    """
    Integrates LLMPageRank Insight Engine with the Model Context Protocol (MCP)
    for standardized model access and agent coordination.
    """
    
    def __init__(self):
        """Initialize the MCP integration."""
        self.last_sync_time = None
        self.mcp_endpoints = {
            "domain_citations": "/api/v1/domain-citations",
            "insight_events": "/api/v1/insight-events",
            "memory_decay": "/api/v1/memory-decay"
        }
        
        # Base URL - can be configured
        self.mcp_base_url = os.environ.get("MCP_BASE_URL", "http://localhost:5050/mcp")
    
    def _get_authorization_header(self) -> Dict:
        """Get authorization header for MCP API calls."""
        api_key = os.environ.get("MCP_API_KEY", "")
        
        if not api_key:
            logger.warning("No MCP_API_KEY found in environment variables")
            return {}
        
        return {"Authorization": f"Bearer {api_key}"}
    
    def publish_domain_ranking(self, domain: str, model: str, query_category: str, 
                             rank: int, query_text: Optional[str] = None) -> Dict:
        """
        Publish domain ranking data to MCP.
        
        Args:
            domain: Domain name
            model: Model name
            query_category: Query category
            rank: Domain rank
            query_text: Optional query text
            
        Returns:
            Response data or error
        """
        endpoint = f"{self.mcp_base_url}{self.mcp_endpoints['domain_citations']}"
        headers = self._get_authorization_header()
        headers["Content-Type"] = "application/json"
        
        data = {
            "domain": domain,
            "model_id": model,
            "query_category": query_category,
            "rank": rank,
            "timestamp": datetime.now().isoformat(),
            "citation_type": "organic"
        }
        
        if query_text:
            data["query_text"] = query_text
        
        try:
            response = requests.post(endpoint, json=data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Error publishing domain ranking: {response.text}")
                return {"error": f"API returned {response.status_code}", "details": response.text}
        except Exception as e:
            logger.error(f"Error publishing domain ranking: {e}")
            return {"error": str(e)}
    
    def publish_memory_decay(self, domain: str, model: str, query_category: str, 
                           decay_score: float, trend: str) -> Dict:
        """
        Publish memory decay data to MCP.
        
        Args:
            domain: Domain name
            model: Model name
            query_category: Query category
            decay_score: Memory decay score (0-1)
            trend: Trend direction ("improving", "declining", "stable")
            
        Returns:
            Response data or error
        """
        endpoint = f"{self.mcp_base_url}{self.mcp_endpoints['memory_decay']}"
        headers = self._get_authorization_header()
        headers["Content-Type"] = "application/json"
        
        data = {
            "domain": domain,
            "model_id": model,
            "query_category": query_category,
            "decay_score": decay_score,
            "trend": trend,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(endpoint, json=data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Error publishing memory decay: {response.text}")
                return {"error": f"API returned {response.status_code}", "details": response.text}
        except Exception as e:
            logger.error(f"Error publishing memory decay: {e}")
            return {"error": str(e)}
    
    def publish_insight_event(self, event_type: str, domain: str, model: str, 
                            query_category: str, details: Dict) -> Dict:
        """
        Publish insight event to MCP.
        
        Args:
            event_type: Event type (e.g., "rank_change", "new_domain", "trend_shift")
            domain: Domain name
            model: Model name
            query_category: Query category
            details: Event details
            
        Returns:
            Response data or error
        """
        endpoint = f"{self.mcp_base_url}{self.mcp_endpoints['insight_events']}"
        headers = self._get_authorization_header()
        headers["Content-Type"] = "application/json"
        
        data = {
            "event_type": event_type,
            "domain": domain,
            "model_id": model,
            "query_category": query_category,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(endpoint, json=data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Error publishing insight event: {response.text}")
                return {"error": f"API returned {response.status_code}", "details": response.text}
        except Exception as e:
            logger.error(f"Error publishing insight event: {e}")
            return {"error": str(e)}
    
    def sync_domain_rankings(self) -> Dict:
        """
        Sync recent domain rankings with MCP.
        
        Returns:
            Sync results
        """
        logger.info("Syncing domain rankings with MCP")
        
        # Get recent memory snapshots
        recent_snapshots = domain_memory_tracker.get_tracker().memory_snapshots[-100:]
        
        results = {
            "total": len(recent_snapshots),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for snapshot in recent_snapshots:
            response = self.publish_domain_ranking(
                domain=snapshot["domain"],
                model=snapshot["model"],
                query_category=snapshot["query_category"],
                rank=snapshot["rank"],
                query_text=snapshot.get("query_text")
            )
            
            if "error" in response:
                results["failed"] += 1
                results["errors"].append({
                    "domain": snapshot["domain"],
                    "error": response["error"]
                })
            else:
                results["successful"] += 1
        
        logger.info(f"Domain ranking sync completed: {results['successful']} successful, {results['failed']} failed")
        
        return results
    
    def sync_memory_decay(self) -> Dict:
        """
        Sync memory decay data with MCP.
        
        Returns:
            Sync results
        """
        logger.info("Syncing memory decay data with MCP")
        
        # This is a simplified example - in a real implementation, you would iterate
        # through domains, models, and categories to calculate decay metrics
        
        # Get top domains for each model and category
        models = ["gpt-4o", "claude-3-opus", "gemini-pro"]
        categories = ["Technology", "Finance", "Healthcare", "Education", "Entertainment"]
        
        results = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for model in models:
            for category in categories:
                domains = domain_memory_tracker.get_top_domains(model, category, limit=10)
                
                for domain_data in domains:
                    domain = domain_data["domain"]
                    
                    # Get memory decay for this domain
                    decay_metrics = domain_memory_tracker.get_memory_decay(
                        domain=domain,
                        model=model,
                        query_category=category
                    )
                    
                    if decay_metrics and "models" in decay_metrics and model in decay_metrics["models"]:
                        model_metrics = decay_metrics["models"][model]
                        
                        if category in model_metrics:
                            cat_metrics = model_metrics[category]
                            
                            results["total"] += 1
                            
                            response = self.publish_memory_decay(
                                domain=domain,
                                model=model,
                                query_category=category,
                                decay_score=cat_metrics["decay_score"],
                                trend=cat_metrics["trend"]
                            )
                            
                            if "error" in response:
                                results["failed"] += 1
                                results["errors"].append({
                                    "domain": domain,
                                    "error": response["error"]
                                })
                            else:
                                results["successful"] += 1
        
        logger.info(f"Memory decay sync completed: {results['successful']} successful, {results['failed']} failed")
        
        return results
    
    def sync_significant_deltas(self) -> Dict:
        """
        Sync significant delta events with MCP.
        
        Returns:
            Sync results
        """
        logger.info("Syncing significant delta events with MCP")
        
        # Get recent significant deltas
        deltas = domain_memory_tracker.get_significant_deltas(days=1)
        
        results = {
            "total": len(deltas),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for delta in deltas:
            event_type = "rank_improvement" if delta["delta"] > 0 else "rank_decline"
            
            details = {
                "previous_rank": delta["previous_rank"],
                "current_rank": delta["current_rank"],
                "delta": delta["delta"],
                "query_text": delta.get("query_text", "")
            }
            
            response = self.publish_insight_event(
                event_type=event_type,
                domain=delta["domain"],
                model=delta["model"],
                query_category=delta["query_category"],
                details=details
            )
            
            if "error" in response:
                results["failed"] += 1
                results["errors"].append({
                    "domain": delta["domain"],
                    "error": response["error"]
                })
            else:
                results["successful"] += 1
        
        logger.info(f"Significant delta sync completed: {results['successful']} successful, {results['failed']} failed")
        
        return results
    
    def run_full_sync(self) -> Dict:
        """
        Run a full sync of all data with MCP.
        
        Returns:
            Combined sync results
        """
        logger.info("Starting full MCP sync")
        
        # Sync each data type
        ranking_results = self.sync_domain_rankings()
        decay_results = self.sync_memory_decay()
        delta_results = self.sync_significant_deltas()
        
        # Combine results
        results = {
            "timestamp": datetime.now().isoformat(),
            "domain_rankings": ranking_results,
            "memory_decay": decay_results,
            "significant_deltas": delta_results,
            "total_successful": ranking_results["successful"] + decay_results["successful"] + delta_results["successful"],
            "total_failed": ranking_results["failed"] + decay_results["failed"] + delta_results["failed"]
        }
        
        self.last_sync_time = datetime.now()
        
        logger.info(f"Full MCP sync completed: {results['total_successful']} successful, {results['total_failed']} failed")
        
        return results


# Singleton instance
_mcp_integration = None

def get_integration() -> MCPIntegration:
    """Get the MCP integration singleton instance."""
    global _mcp_integration
    
    if _mcp_integration is None:
        _mcp_integration = MCPIntegration()
    
    return _mcp_integration

def publish_domain_ranking(domain: str, model: str, query_category: str, 
                         rank: int, query_text: Optional[str] = None) -> Dict:
    """
    Publish domain ranking data to MCP.
    
    Args:
        domain: Domain name
        model: Model name
        query_category: Query category
        rank: Domain rank
        query_text: Optional query text
        
    Returns:
        Response data or error
    """
    return get_integration().publish_domain_ranking(domain, model, query_category, rank, query_text)

def publish_memory_decay(domain: str, model: str, query_category: str, 
                       decay_score: float, trend: str) -> Dict:
    """
    Publish memory decay data to MCP.
    
    Args:
        domain: Domain name
        model: Model name
        query_category: Query category
        decay_score: Memory decay score (0-1)
        trend: Trend direction ("improving", "declining", "stable")
        
    Returns:
        Response data or error
    """
    return get_integration().publish_memory_decay(domain, model, query_category, decay_score, trend)

def publish_insight_event(event_type: str, domain: str, model: str, 
                        query_category: str, details: Dict) -> Dict:
    """
    Publish insight event to MCP.
    
    Args:
        event_type: Event type (e.g., "rank_change", "new_domain", "trend_shift")
        domain: Domain name
        model: Model name
        query_category: Query category
        details: Event details
        
    Returns:
        Response data or error
    """
    return get_integration().publish_insight_event(event_type, domain, model, query_category, details)

def run_full_sync() -> Dict:
    """
    Run a full sync of all data with MCP.
    
    Returns:
        Combined sync results
    """
    return get_integration().run_full_sync()

def schedule_regular_sync():
    """Schedule regular MCP syncs."""
    import schedule
    import time
    import threading
    
    def sync_job():
        logger.info("Running scheduled MCP sync")
        run_full_sync()
    
    # Schedule sync every MCP_SYNC_INTERVAL_HOURS
    schedule.every(MCP_SYNC_INTERVAL_HOURS).hours.do(sync_job)
    
    # Run in a separate thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    
    logger.info(f"MCP sync scheduled every {MCP_SYNC_INTERVAL_HOURS} hours")
    
    return thread