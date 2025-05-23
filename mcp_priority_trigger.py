"""
MCP Priority Trigger Endpoint
Codename: "Flame Aware"

This module implements the priority trigger endpoint that allows the frontend
to notify the backend when a brand/domain requires priority attention.
"""

import os
import json
import time
import datetime
import logging
import re
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Body, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator

# Import from local modules
from mcp_auth import verify_token
import agent_monitor
import memory_vulnerability_score as mvs

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PRIORITY_THROTTLE_HOURS = 4  # Maximum frequency of priority triggers per brand
IP_RATE_LIMIT = 10  # Maximum number of different brands per hour per IP
PRIORITY_LOG_PATH = "data/surface/priority_triggers.json"

# Router for priority trigger endpoint
router = APIRouter(prefix="/api", tags=["Priority Trigger"])

# Ensure directory exists
os.makedirs(os.path.dirname(PRIORITY_LOG_PATH), exist_ok=True)

# Models
class PriorityTriggerRequest(BaseModel):
    """Model for priority trigger request."""
    brandSlug: str = Field(..., min_length=2, max_length=64)
    referrer: str = Field(default="direct")
    triggerSource: str = Field(default="user_input")
    
    @validator('brandSlug')
    def validate_brand_slug(cls, v):
        """Validate brand slug."""
        # Simple validation - alphanumeric with hyphens
        if not re.match(r'^[a-zA-Z0-9-]+$', v):
            raise ValueError("brandSlug must be alphanumeric with hyphens only")
        return v
    
    @validator('triggerSource')
    def validate_trigger_source(cls, v):
        """Validate trigger source."""
        valid_sources = ["user_input", "search", "direct_view", "claim_attempt", "api"]
        if v not in valid_sources:
            raise ValueError(f"triggerSource must be one of: {', '.join(valid_sources)}")
        return v

class PriorityTriggerResponse(BaseModel):
    """Model for priority trigger response."""
    status: str
    message: str
    nextScanEta: str
    agents: List[str]

def load_priority_log() -> List[Dict]:
    """Load priority trigger log."""
    if os.path.exists(PRIORITY_LOG_PATH):
        try:
            with open(PRIORITY_LOG_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading priority log: {e}")
    
    return []

def save_priority_log(log_entries: List[Dict]) -> bool:
    """Save priority trigger log."""
    try:
        with open(PRIORITY_LOG_PATH, "w") as f:
            json.dump(log_entries, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving priority log: {e}")
        return False

def check_throttle(brand_slug: str) -> bool:
    """
    Check if a brand is throttled (triggered too recently).
    
    Args:
        brand_slug: Brand slug to check
        
    Returns:
        Whether the brand is throttled
    """
    log_entries = load_priority_log()
    
    # Find most recent trigger for this brand
    brand_entries = [entry for entry in log_entries if entry.get("brandSlug") == brand_slug]
    
    if not brand_entries:
        return False
    
    # Get most recent entry
    most_recent = max(brand_entries, key=lambda x: x.get("timestamp", ""))
    
    # Parse timestamp
    try:
        timestamp = datetime.datetime.fromisoformat(most_recent.get("timestamp"))
        now = datetime.datetime.now()
        
        # Check if within throttle window
        time_diff = now - timestamp
        hours_diff = time_diff.total_seconds() / 3600
        
        return hours_diff < PRIORITY_THROTTLE_HOURS
    except Exception as e:
        logger.error(f"Error checking throttle: {e}")
        return False

def check_ip_rate_limit(ip_address: str) -> bool:
    """
    Check if an IP has exceeded its rate limit.
    
    Args:
        ip_address: IP address to check
        
    Returns:
        Whether the IP has exceeded its rate limit
    """
    log_entries = load_priority_log()
    
    # Get current hour
    now = datetime.datetime.now()
    hour_start = now.replace(minute=0, second=0, microsecond=0)
    
    # Get entries from this IP in the current hour
    ip_entries = [
        entry for entry in log_entries
        if entry.get("ipHash") == ip_address and
        datetime.datetime.fromisoformat(entry.get("timestamp", "")) >= hour_start
    ]
    
    # Count unique brands
    unique_brands = set(entry.get("brandSlug") for entry in ip_entries)
    
    return len(unique_brands) >= IP_RATE_LIMIT

def assign_agents(brand_slug: str) -> List[str]:
    """
    Assign agents to handle the priority brand.
    
    Args:
        brand_slug: Brand slug to handle
        
    Returns:
        List of assigned agent names
    """
    # Get available agents
    agents = agent_monitor.get_all_agents()
    
    # Filter for active agents
    active_agents = [agent for agent in agents if agent.get("status") == "active"]
    
    # Prioritize agents with relevant capabilities
    insight_agents = [agent for agent in active_agents if "insight" in agent.get("role", "").lower()]
    pickup_agents = [agent for agent in active_agents if "pickup" in agent.get("role", "").lower()]
    
    assigned_agents = []
    
    # Assign an insight agent if available
    if insight_agents:
        assigned_agents.append(insight_agents[0].get("name"))
    
    # Assign a pickup agent if available
    if pickup_agents:
        assigned_agents.append(pickup_agents[0].get("name"))
    
    # If no specific agents available, use any active agent
    if not assigned_agents and active_agents:
        assigned_agents.append(active_agents[0].get("name"))
    
    # Default agent names if none available
    if not assigned_agents:
        assigned_agents = ["InsightDraft-A1", "PickupMonitor-B2"]
    
    return assigned_agents

def calculate_next_scan_eta() -> str:
    """
    Calculate ETA for next scan.
    
    Returns:
        ETA string (e.g., "2 hours")
    """
    # In a real implementation, this would be based on current agent workload
    # For now, just return a fixed value
    return "2 hours"

def log_priority_trigger(
    brand_slug: str,
    trigger_source: str,
    referrer: str,
    ip_address: str,
    result: str
) -> bool:
    """
    Log a priority trigger.
    
    Args:
        brand_slug: Brand slug
        trigger_source: Trigger source
        referrer: Referrer
        ip_address: IP address
        result: Result of the trigger
        
    Returns:
        Whether the log was successful
    """
    log_entries = load_priority_log()
    
    # Create new log entry
    new_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "brandSlug": brand_slug,
        "triggerSource": trigger_source,
        "referrer": referrer,
        "ipHash": ip_address,  # In a real implementation, this would be hashed
        "result": result
    }
    
    # Add to log
    log_entries.append(new_entry)
    
    # Save log
    return save_priority_log(log_entries)

def mark_brand_as_priority(brand_slug: str) -> bool:
    """
    Mark a brand as priority in the system.
    
    Args:
        brand_slug: Brand slug to mark as priority
        
    Returns:
        Whether the operation was successful
    """
    try:
        # Update memory vulnerability score
        brand_info = mvs.get_brand_score(brand_slug)
        
        if brand_info:
            # Calculate categories this brand belongs to
            categories = list(brand_info.get("category_scores", {}).keys())
            
            # If the brand has no categories yet, use the default
            if not categories:
                categories = ["general"]
            
            # Update priority flag for each category
            success = True
            for category in categories:
                category_success = mvs.update_brand_priority(brand_slug, category, True)
                success = success and category_success
            
            if success:
                logger.info(f"Marked brand {brand_slug} as priority in {len(categories)} categories")
            else:
                logger.warning(f"Partially marked brand {brand_slug} as priority")
            
            return success
        else:
            # Create new brand entry if it doesn't exist yet
            categories = ["general"]  # Default category
            all_success = True
            
            for category in categories:
                category_success = mvs.update_brand_priority(brand_slug, category, True)
                all_success = all_success and category_success
            
            if all_success:
                logger.info(f"Created new priority brand {brand_slug} in system")
            else:
                logger.warning(f"Partially created new priority brand {brand_slug}")
            
            return all_success
    except Exception as e:
        logger.error(f"Error marking brand as priority: {e}")
        return False

@router.post("/priority-trigger", response_model=PriorityTriggerResponse)
async def priority_trigger(
    request: Request,
    trigger_data: PriorityTriggerRequest = Body(...),
    token_data: Dict = Depends(verify_token)
):
    """
    Priority trigger endpoint.
    
    This endpoint allows the frontend to notify the backend when a brand/domain
    requires priority attention.
    
    Args:
        request: FastAPI request
        trigger_data: Priority trigger data
        token_data: Token data from authentication
        
    Returns:
        Priority trigger response
    """
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Priority trigger request from {client_ip}: {trigger_data.brandSlug} ({trigger_data.triggerSource})")
    
    # Check if user has access to this endpoint
    if "priority_trigger" not in token_data.get("access", []):
        logger.warning(f"Unauthorized access attempt to priority trigger: {token_data.get('agent_id')}")
        raise HTTPException(
            status_code=403, 
            detail={"error": "unauthorized", "reason": "insufficient access rights"}
        )
    
    # Check throttling
    if check_throttle(trigger_data.brandSlug):
        logger.info(f"Throttled priority trigger for {trigger_data.brandSlug}")
        
        # Log the event
        log_priority_trigger(
            trigger_data.brandSlug,
            trigger_data.triggerSource,
            trigger_data.referrer,
            client_ip,
            "throttled"
        )
        
        # Return a 200 response anyway to avoid leaking timing information
        return {
            "status": "throttled",
            "message": "Brand already in priority queue",
            "nextScanEta": calculate_next_scan_eta(),
            "agents": assign_agents(trigger_data.brandSlug)
        }
    
    # Check IP rate limit
    if check_ip_rate_limit(client_ip):
        logger.warning(f"IP rate limit exceeded for {client_ip}")
        
        # Log the event
        log_priority_trigger(
            trigger_data.brandSlug,
            trigger_data.triggerSource,
            trigger_data.referrer,
            client_ip,
            "rate_limited"
        )
        
        # Return a 429 response
        raise HTTPException(
            status_code=429, 
            detail={"error": "rate_limited", "reason": "too many brands triggered"}
        )
    
    # Mark brand as priority
    success = mark_brand_as_priority(trigger_data.brandSlug)
    
    if not success:
        logger.error(f"Failed to mark brand {trigger_data.brandSlug} as priority")
        
        # Log the event
        log_priority_trigger(
            trigger_data.brandSlug,
            trigger_data.triggerSource,
            trigger_data.referrer,
            client_ip,
            "error"
        )
        
        # Return a 500 response
        raise HTTPException(
            status_code=500, 
            detail={"error": "internal_error", "reason": "failed to mark brand as priority"}
        )
    
    # Assign agents
    assigned_agents = assign_agents(trigger_data.brandSlug)
    
    # Calculate next scan ETA
    next_scan_eta = calculate_next_scan_eta()
    
    # Log the event
    log_priority_trigger(
        trigger_data.brandSlug,
        trigger_data.triggerSource,
        trigger_data.referrer,
        client_ip,
        "success"
    )
    
    # Return success response
    return {
        "status": "queued",
        "message": "Brand promoted to priority insight queue",
        "nextScanEta": next_scan_eta,
        "agents": assigned_agents
    }