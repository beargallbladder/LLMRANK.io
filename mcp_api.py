"""
LLMPageRank Model Context Protocol (MCP) API

This module implements the API endpoints for the Model Context Protocol (MCP) interface
that delivers real-time trust context to agents, dashboards, and the RankLLM.io leaderboard.
"""

import os
import json
import time
import datetime
import logging
from typing import Dict, List, Optional, Any, Union
from fastapi import APIRouter, HTTPException, Body, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import mcp_dispatcher
import mcp_auth

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(
    prefix="/mcp",
    tags=["mcp"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Unauthorized"},
        429: {"description": "Rate limit exceeded"}
    },
)


@router.get("/context/{domain}")
async def get_context(domain: str, token_data: Dict = Depends(mcp_auth.verify_token)):
    """Get the trust context for a domain."""
    try:
        # Check if user has access to this endpoint
        if "context" not in token_data.get("access", []):
            raise HTTPException(
                status_code=403, 
                detail={"error": "unauthorized", "reason": "insufficient access rights"}
            )
            
        context = mcp_dispatcher.mcp_context(domain)
        return context
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting context for {domain}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drift_events/{category}")
async def get_drift_events(category: str, token_data: Dict = Depends(mcp_auth.verify_token)):
    """Get drift events for a category."""
    try:
        # Check if user has access to this endpoint
        if "drift_events" not in token_data.get("access", []):
            raise HTTPException(
                status_code=403, 
                detail={"error": "unauthorized", "reason": "insufficient access rights"}
            )
            
        drift_events = mcp_dispatcher.mcp_drift_events(category)
        return drift_events
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting drift events for {category}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompt_suggestions/{task}")
async def get_prompt_suggestions(task: str, token_data: Dict = Depends(mcp_auth.verify_token)):
    """Get prompt suggestions for a task."""
    try:
        # Check if user has access to this endpoint
        if "prompt_suggestions" not in token_data.get("access", []):
            raise HTTPException(
                status_code=403, 
                detail={"error": "unauthorized", "reason": "insufficient access rights"}
            )
            
        prompt_suggestions = mcp_dispatcher.mcp_prompt_suggestions(task)
        return prompt_suggestions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt suggestions for {task}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/foma_threats/{domain}")
async def get_foma_threats(domain: str, token_data: Dict = Depends(mcp_auth.verify_token)):
    """Get FOMA threats for a domain."""
    try:
        # Check if user has access to this endpoint
        if "foma_threats" not in token_data.get("access", []):
            raise HTTPException(
                status_code=403, 
                detail={"error": "unauthorized", "reason": "insufficient access rights"}
            )
            
        foma_threats = mcp_dispatcher.mcp_foma_threats(domain)
        return foma_threats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting FOMA threats for {domain}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rankllm_input")
async def get_rankllm_input(token_data: Dict = Depends(mcp_auth.verify_token)):
    """Get RankLLM.io leaderboard input data."""
    try:
        # Check if user has access to this endpoint
        if "rankllm_input" not in token_data.get("access", []):
            raise HTTPException(
                status_code=403, 
                detail={"error": "unauthorized", "reason": "insufficient access rights"}
            )
            
        rankllm_data = mcp_dispatcher.mcp_rankllm_input()
        return rankllm_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting RankLLM input: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent_register")
async def register_agent(agent_info: Dict = Body(...), token_data: Dict = Depends(mcp_auth.verify_token)):
    """Register an agent with the MCP."""
    try:
        # Check if user has access to this endpoint
        if "agent_register" not in token_data.get("access", []):
            raise HTTPException(
                status_code=403, 
                detail={"error": "unauthorized", "reason": "insufficient access rights"}
            )
            
        result = mcp_dispatcher.register_agent(agent_info)
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Registration failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/agent_update/{agent_id}")
async def update_agent(agent_id: str, agent_update: Dict = Body(...), 
                       token_data: Dict = Depends(mcp_auth.verify_token)):
    """Update an agent's information."""
    try:
        # Check if user has access to this endpoint
        if "agent_update" not in token_data.get("access", []):
            raise HTTPException(
                status_code=403, 
                detail={"error": "unauthorized", "reason": "insufficient access rights"}
            )
            
        result = mcp_dispatcher.update_agent(agent_id, agent_update)
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Update failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_health(token_data: Dict = Depends(mcp_auth.verify_token)):
    """Get MCP health metrics."""
    try:
        # Check if user has access to this endpoint
        if "health" not in token_data.get("access", []):
            raise HTTPException(
                status_code=403, 
                detail={"error": "unauthorized", "reason": "insufficient access rights"}
            )
            
        health_metrics = mcp_dispatcher.get_health_metrics()
        return health_metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting health metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))