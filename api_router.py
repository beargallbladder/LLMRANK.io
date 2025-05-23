"""
LLMPageRank V3 API Router

This module implements the API layer for the LLMPageRank V3 system,
providing external access to the trust signal data and benchmarks.
"""

import json
import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, Depends, HTTPException, Header, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import from project modules
from config import DATA_DIR, SYSTEM_VERSION, PROMPT_VERSION, LLM_MODELS
import database as db
from category_matrix import category_matrix, calculate_foma_score, get_peer_domains
from crawl_planner import get_prioritized_domains
from prompt_validator import get_invalid_prompts

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
API_KEYS_FILE = f"{DATA_DIR}/api_keys.json"


# Initialize FastAPI app
app = FastAPI(
    title="LLMPageRank API",
    description="API for accessing LLMPageRank trust signal intelligence data",
    version=SYSTEM_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API keys
def load_api_keys() -> Dict[str, Dict]:
    """
    Load API keys.
    
    Returns:
        Dictionary of API keys
    """
    if os.path.exists(API_KEYS_FILE):
        try:
            with open(API_KEYS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
    
    return {}

API_KEYS = load_api_keys()

# Dependency for API key authentication
async def verify_api_key(
    authorization: str = Header(None),
    x_mcp_agent: Optional[str] = Header(None),
    x_session_type: Optional[str] = Header("browser"),
    x_query_purpose: Optional[str] = Header("trust_query")
):
    """
    Verify API key from Authorization header.
    Also checks for MCP compatibility headers.
    
    Args:
        authorization: Authorization header
        x_mcp_agent: MCP agent flag
        x_session_type: Session type
        x_query_purpose: Query purpose
    
    Returns:
        API key information if valid
    
    Raises:
        HTTPException: If API key is invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required"
        )
    
    # Extract token from "Bearer {token}" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    # Check if token is valid
    if token not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Return API key info
    api_key_info = API_KEYS[token].copy()
    api_key_info.update({
        "key": token,
        "is_mcp_agent": x_mcp_agent == "true",
        "session_type": x_session_type,
        "query_purpose": x_query_purpose
    })
    
    return api_key_info

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log API requests and timing.
    
    Args:
        request: The HTTP request
        call_next: The next middleware
    
    Returns:
        The HTTP response
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} - Took {process_time:.4f}s - Status: {response.status_code}")
    
    return response

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "ok",
        "version": SYSTEM_VERSION,
        "timestamp": time.time()
    }

# Domain score endpoint
@app.get("/api/v1/score/{domain}")
async def get_domain_score(domain: str, api_key_info: Dict = Depends(verify_api_key)):
    """
    Get trust score and details for a domain.
    
    Args:
        domain: Domain name
        api_key_info: API key information
    
    Returns:
        Domain score and details
    
    Raises:
        HTTPException: If domain not found
    """
    # Get latest domain result
    domain_result = db.get_latest_domain_result(domain)
    
    if not domain_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain not found: {domain}"
        )
    
    # Get peer domains
    peer_domains = get_peer_domains(domain)
    
    # Calculate FOMA score
    foma = calculate_foma_score(domain)
    
    # Get previous result for delta
    domain_history = db.get_domain_history(domain)
    delta_7d = 0
    
    if len(domain_history) > 1:
        current_score = domain_result.get("visibility_score", 0)
        previous_score = domain_history[1].get("visibility_score", 0)
        delta_7d = current_score - previous_score
    
    # Format response
    response = {
        "domain": domain,
        "llmrank": domain_result.get("visibility_score", 0),
        "delta_7d": delta_7d,
        "category": domain_result.get("category", ""),
        "trust_status": foma.get("trust_status", "Unknown"),
        "peer_set_size": len(peer_domains),
        "qa_intensity_score": domain_result.get("qa_score", 0.5),
        "citations": domain_result.get("citation_coverage", {}),
        "structure_score": domain_result.get("structure_score", 0),
        "consensus_score": domain_result.get("consensus_score", 0),
        "timestamp": domain_result.get("timestamp", time.time()),
        "last_updated": datetime.fromtimestamp(domain_result.get("timestamp", time.time())).strftime("%Y-%m-%d")
    }
    
    return response

# Top domains by category endpoint
@app.get("/api/v1/top/{category}")
async def get_top_domains(category: str, limit: int = 10, api_key_info: Dict = Depends(verify_api_key)):
    """
    Get top domains by visibility score for a category.
    
    Args:
        category: Category name
        limit: Maximum number of domains to return
        api_key_info: API key information
    
    Returns:
        List of top domains
    
    Raises:
        HTTPException: If category not found
    """
    # Get all domains in category
    domains_by_category = db.load_domains_by_category()
    
    if category not in domains_by_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category not found: {category}"
        )
    
    # Get domains in category
    category_domains = domains_by_category[category]
    
    # Get latest scores for each domain
    scored_domains = []
    
    for domain_info in category_domains:
        domain = domain_info.get("domain", "")
        if not domain:
            continue
        
        # Get latest result
        latest_result = db.get_latest_domain_result(domain)
        if not latest_result:
            continue
        
        # Add to scored domains
        scored_domains.append({
            "domain": domain,
            "llmrank": latest_result.get("visibility_score", 0),
            "structure_score": latest_result.get("structure_score", 0),
            "consensus_score": latest_result.get("consensus_score", 0),
            "category": category,
            "timestamp": latest_result.get("timestamp", time.time())
        })
    
    # Sort by visibility score (descending)
    scored_domains.sort(key=lambda x: x["llmrank"], reverse=True)
    
    # Return top N domains
    return {
        "category": category,
        "domains": scored_domains[:limit],
        "total_domains": len(category_domains),
        "timestamp": time.time()
    }

# Visibility deltas endpoint
@app.get("/api/v1/visibility-deltas")
async def get_visibility_deltas(limit: int = 10, api_key_info: Dict = Depends(verify_api_key)):
    """
    Get domains with the biggest changes in visibility.
    
    Args:
        limit: Maximum number of domains to return
        api_key_info: API key information
    
    Returns:
        List of domains with significant visibility changes
    """
    # Get all domains
    all_domains = db.get_all_tested_domains()
    
    # Calculate deltas
    domains_with_deltas = []
    
    for domain in all_domains:
        # Get domain history
        history = db.get_domain_history(domain)
        
        if len(history) < 2:
            continue
        
        # Calculate delta
        current_score = history[0].get("visibility_score", 0)
        previous_score = history[1].get("visibility_score", 0)
        delta = current_score - previous_score
        
        # Only include significant changes
        if abs(delta) < 3:
            continue
        
        # Add to list
        domains_with_deltas.append({
            "domain": domain,
            "category": history[0].get("category", ""),
            "current_score": current_score,
            "previous_score": previous_score,
            "delta": delta,
            "direction": "up" if delta > 0 else "down",
            "timestamp": history[0].get("timestamp", time.time())
        })
    
    # Sort by absolute delta (descending)
    domains_with_deltas.sort(key=lambda x: abs(x["delta"]), reverse=True)
    
    return {
        "deltas": domains_with_deltas[:limit],
        "timestamp": time.time()
    }

# Prompts by category endpoint
@app.get("/api/v1/prompts/{category}")
async def get_prompts(category: str, api_key_info: Dict = Depends(verify_api_key)):
    """
    Get prompts used for a specific category.
    
    Args:
        category: Category name
        api_key_info: API key information
    
    Returns:
        List of prompts for the category
    
    Raises:
        HTTPException: If category not found
    """
    # Check if category exists
    if category not in os.listdir(f"{DATA_DIR}/prompts"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prompts found for category: {category}"
        )
    
    # Load prompts for category
    try:
        with open(f"{DATA_DIR}/prompts/{category}_prompts.json", "r") as f:
            prompts = json.load(f)
    except Exception as e:
        logger.error(f"Error loading prompts for {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading prompts: {str(e)}"
        )
    
    # Format response
    return {
        "category": category,
        "prompt_count": len(prompts),
        "prompt_version": PROMPT_VERSION,
        "prompts": prompts,
        "timestamp": time.time()
    }

# FOMA endpoint
@app.get("/api/v1/foma/{domain}")
async def get_foma(domain: str, api_key_info: Dict = Depends(verify_api_key)):
    """
    Get FOMA (Fear Of Missing AI) score for a domain.
    
    Args:
        domain: Domain name
        api_key_info: API key information
    
    Returns:
        FOMA score and details
    
    Raises:
        HTTPException: If domain not found
    """
    # Check if domain exists
    domain_result = db.get_latest_domain_result(domain)
    
    if not domain_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain not found: {domain}"
        )
    
    # Calculate FOMA score
    foma = calculate_foma_score(domain)
    
    # Enhance with additional info
    foma["category"] = domain_result.get("category", "")
    foma["structure_score"] = domain_result.get("structure_score", 0)
    
    return foma

# Metadata endpoint
@app.get("/api/v1/metadata")
async def get_metadata(api_key_info: Dict = Depends(verify_api_key)):
    """
    Get system metadata.
    
    Args:
        api_key_info: API key information
    
    Returns:
        System metadata
    """
    # Get system stats
    stats = db.get_domain_status_summary()
    
    # Format response
    return {
        "system_version": SYSTEM_VERSION,
        "prompt_version": PROMPT_VERSION,
        "total_domains": stats.get("total_discovered", 0),
        "tested_domains": stats.get("total_tested", 0),
        "categories": len(stats.get("categories", {})),
        "invalid_prompts": len(get_invalid_prompts()),
        "model_versions": {model: data["version"] if isinstance(data, dict) else "unknown" 
                           for model, data in LLM_MODELS.items()},
        "timestamp": time.time(),
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    }

# Add a default API key for testing
def create_default_api_key():
    """Create a default API key for testing."""
    if not os.path.exists(API_KEYS_FILE):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(API_KEYS_FILE), exist_ok=True)
        
        # Create default API key
        default_key = "llmpagerank_v3_test_key"
        
        api_keys = {
            default_key: {
                "name": "Test API Key",
                "created_at": time.time(),
                "created_by": "system",
                "rate_limit": 100,
                "permissions": ["read"]
            }
        }
        
        # Save API keys
        try:
            with open(API_KEYS_FILE, 'w') as f:
                json.dump(api_keys, f, indent=2)
            logger.info(f"Created default API key: {default_key}")
        except Exception as e:
            logger.error(f"Error creating default API key: {e}")

# Create default API key on import
create_default_api_key()

def run_api_server():
    """Run the API server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_api_server()