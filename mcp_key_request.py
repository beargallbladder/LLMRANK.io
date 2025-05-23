"""
MCP Key Request Module

This module implements the /mcp/request_key endpoint as specified in
"Keys for the Machines" PRD and the endpoint specification.
"""

import os
import json
import logging
import datetime
import re
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Request, Depends, Body
from pydantic import BaseModel, EmailStr, Field, validator

# Import from local modules
from api_key_manager import create_api_key, get_user_api_key, get_api_key, upgrade_api_key, downgrade_api_key
from api_rate_limiter import check_rate_limit
from api_usage_watcher import log_api_access, get_flagged_keys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router for key request endpoints
router = APIRouter(prefix="/mcp", tags=["Key Management"])

# Models
class KeyRequestModel(BaseModel):
    """Model for API key request data."""
    email: EmailStr
    plan: str = Field(default="free_temp")
    user_id: Optional[str] = Field(default=None)
    referrer: str = Field(default="unknown")
    verified: bool = Field(default=False)
    stripe_customer_id: Optional[str] = Field(default=None)
    
    @validator('plan')
    def validate_plan(cls, v):
        """Validate plan."""
        valid_plans = ["free_temp", "free", "starter", "pro", "enterprise"]
        if v not in valid_plans:
            raise ValueError(f"Invalid plan. Must be one of: {', '.join(valid_plans)}")
        return v
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Validate user_id if provided."""
        if v is not None and (len(v) < 3 or len(v) > 64):
            raise ValueError("user_id must be between 3 and 64 characters")
        return v
    
    @validator('referrer')
    def validate_referrer(cls, v):
        """Validate referrer."""
        # Simple domain validation
        if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            # If not a valid domain, at least ensure it's a reasonable string
            if not re.match(r'^[a-zA-Z0-9._-]{3,64}$', v):
                raise ValueError("Invalid referrer format")
        return v

class KeyResponseModel(BaseModel):
    """Model for API key response data."""
    api_key: str
    plan: str
    rate_limit: int
    scope: list
    expires: Optional[str] = None

async def log_key_request(request_data: Dict, api_key: str, rate_limit: int):
    """
    Log key request for auditing purposes.
    
    Args:
        request_data: Key request data
        api_key: Generated API key
        rate_limit: Rate limit assigned to the key
    """
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "requested_by": request_data.get("referrer", "unknown"),
        "user_email": request_data.get("email"),
        "plan": request_data.get("plan"),
        "api_key": api_key,
        "rate_limit": rate_limit
    }
    
    # Ensure log directory exists
    log_dir = os.path.join("data", "api_keys", "request_logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Append to log file
    log_file = os.path.join(log_dir, "key_requests.json")
    
    try:
        # Read existing logs
        logs = []
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        
        # Append new log
        logs.append(log_entry)
        
        # Write logs back to file
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
            
        logger.info(f"Logged key request: {log_entry['user_email']} from {log_entry['requested_by']}")
    except Exception as e:
        logger.error(f"Error logging key request: {e}")

@router.post("/request_key", response_model=KeyResponseModel)
async def request_key(
    request: Request,
    key_request: KeyRequestModel = Body(...)
):
    """
    Request a new API key.
    
    Implements the /mcp/request_key endpoint that follows the V2 API Key Lifecycle
    with anonymous soft registration and identity progression.
    
    Args:
        request: FastAPI request object
        key_request: Key request data
        
    Returns:
        API key response data
    """
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"API key request from {client_ip}: {key_request.email} ({key_request.referrer})")
    
    try:
        # Determine lifecycle phase
        has_user_id = bool(key_request.user_id)
        has_verification = key_request.verified
        has_payment = bool(key_request.stripe_customer_id)
        
        # Use user_id if provided, otherwise use email as user_id
        user_id = key_request.user_id if key_request.user_id else key_request.email
        
        # Check if user already has a key
        existing_key = get_user_api_key(user_id)
        
        # === Phase 1: Anonymous Soft Registration ===
        if not has_user_id and not has_verification and not has_payment:
            # If user already has a key in temp plan, return it
            if existing_key and existing_key.get("plan") == "free_temp":
                logger.info(f"Returning existing temporary key for {user_id}")
                key_data = existing_key
            else:
                # Create new temporary key (valid for 7 days or 1000 calls)
                logger.info(f"Creating new temporary key for {user_id}")
                key_data = create_api_key(
                    user_id=user_id,
                    plan="free_temp",
                    email=key_request.email,
                    ip_address=client_ip,
                    verified=False
                )
        
        # === Phase 2: Identity Upgrade ===
        elif has_user_id and has_verification and not has_payment:
            if existing_key:
                # Upgrade from temporary to verified free tier
                if existing_key.get("plan") == "free_temp":
                    logger.info(f"Upgrading temporary key to verified free tier for {user_id}")
                    key_data = upgrade_api_key(
                        user_id=user_id,
                        new_plan="free",
                        verified=True
                    )
                else:
                    # Return existing key
                    logger.info(f"Returning existing key for verified user {user_id}")
                    key_data = existing_key
            else:
                # Create new verified free tier key
                logger.info(f"Creating new verified free tier key for {user_id}")
                key_data = create_api_key(
                    user_id=user_id,
                    plan="free",
                    email=key_request.email,
                    ip_address=client_ip,
                    verified=True
                )
        
        # === Phase 3: Plan Promotion ===
        elif has_user_id and has_verification and has_payment:
            # Determine plan based on payment
            plan = key_request.plan
            if plan in ["free", "free_temp"]:
                plan = "starter"  # Minimum paid plan
            
            if existing_key:
                # Upgrade to paid plan
                logger.info(f"Upgrading key to paid plan {plan} for {user_id}")
                key_data = upgrade_api_key(
                    user_id=user_id,
                    new_plan=plan,
                    verified=True,
                    stripe_customer_id=key_request.stripe_customer_id
                )
            else:
                # Create new paid plan key
                logger.info(f"Creating new paid plan {plan} key for {user_id}")
                
                # For enterprise plan, use default high rate limit
                custom_rate_limit = None
                if plan == "enterprise":
                    custom_rate_limit = 50000
                
                key_data = create_api_key(
                    user_id=user_id,
                    plan=plan,
                    custom_rate_limit=custom_rate_limit,
                    email=key_request.email,
                    ip_address=client_ip,
                    verified=True,
                    stripe_customer_id=key_request.stripe_customer_id
                )
        
        # === Fallback case ===
        else:
            if existing_key:
                # Return existing key
                logger.info(f"Returning existing key for {user_id}")
                key_data = existing_key
            else:
                # Create new temporary key
                logger.info(f"Creating new temporary key for {user_id}")
                key_data = create_api_key(
                    user_id=user_id,
                    plan="free_temp",
                    email=key_request.email,
                    ip_address=client_ip
                )
        
        # Log key request
        await log_key_request(
            key_request.dict(),
            key_data.get("token", ""),
            key_data.get("rate_limit", 0)
        )
        
        # Record this request in the API access log
        log_api_access(
            token=key_data.get("token", ""),
            endpoint="/mcp/request_key",
            ip_address=client_ip,
            status_code=200
        )
        
        # Return key data
        expires = key_data.get("expires") 
        
        return {
            "api_key": key_data.get("token"),
            "plan": key_data.get("plan"),
            "rate_limit": key_data.get("rate_limit"),
            "scope": key_data.get("scope", []),
            "expires": expires if expires else None
        }
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating API key: {str(e)}")

@router.get("/validate_key/{api_key}")
async def validate_key(api_key: str):
    """
    Validate an API key.
    
    Args:
        api_key: API key to validate
        
    Returns:
        Validation result
    """
    # Get key data
    key_data = get_api_key(api_key)
    
    if not key_data:
        return {"valid": False, "reason": "API key not found"}
    
    if key_data.get("status") != "active":
        return {"valid": False, "reason": "API key is not active"}
    
    # Check rate limit
    within_limit, current_usage, limit = check_rate_limit(api_key)
    
    if not within_limit:
        return {
            "valid": False, 
            "reason": "Rate limit exceeded",
            "usage": current_usage,
            "limit": limit
        }
    
    # Return validation result
    return {
        "valid": True,
        "plan": key_data.get("plan"),
        "scope": key_data.get("scope", []),
        "usage": current_usage,
        "limit": limit
    }