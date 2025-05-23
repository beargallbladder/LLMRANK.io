"""
MCP Logo Service

This module provides logo retrieval capabilities for brands tracked in the LLMPageRank system.
Logos add credibility and familiarity to brand insights displayed on LLMRank.io.
"""

import os
import json
import requests
import time
import hashlib
import base64
from io import BytesIO
from typing import Dict, Any, Optional, List, Tuple
import logging
from fastapi import FastAPI, HTTPException, Depends, Header, Query, Path
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from urllib.parse import urlparse
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
LOGO_CACHE_DIR = "data/logos"
MCP_KEYS_DIR = "data/mcp/keys"
LOGO_CACHE_EXPIRY = 7 * 24 * 60 * 60  # 7 days in seconds

# Ensure directories exist
os.makedirs(LOGO_CACHE_DIR, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="LLMRank.io MCP Logo API",
    description="Logo retrieval service for brands tracked in LLMPageRank",
    version="1.0.0"
)

# Models
class LogoResponse(BaseModel):
    """Logo response model."""
    domain: str
    logo_url: Optional[str] = None
    logo_data: Optional[str] = None
    format: Optional[str] = None
    source: str
    cached: bool
    
class DomainRequest(BaseModel):
    """Domain request model."""
    domain: str = Field(..., description="The domain to get the logo for")
    force_refresh: bool = Field(False, description="Whether to force a refresh of cached logo")
    
class BulkLogoRequest(BaseModel):
    """Bulk logo request model."""
    domains: List[str] = Field(..., description="List of domains to get logos for")
    force_refresh: bool = Field(False, description="Whether to force a refresh of cached logos")

# Helper functions
def validate_api_key(api_key: str = Header(..., description="MCP API Key")) -> Dict[str, Any]:
    """
    Validate the MCP API key.
    
    Args:
        api_key: The MCP API key from the header
        
    Returns:
        Key metadata if valid
        
    Raises:
        HTTPException: If the key is invalid
    """
    key_path = os.path.join(MCP_KEYS_DIR, f"{api_key}.json")
    
    if not os.path.exists(key_path):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        with open(key_path, "r") as f:
            metadata = json.load(f)
        
        # Check if key is active
        if metadata.get("status") != "active":
            raise HTTPException(status_code=401, detail="API key is inactive")
        
        # Check if key has expired
        expires_at = metadata.get("expires_at")
        if expires_at and expires_at != "None" and time.time() > float(expires_at):
            raise HTTPException(status_code=401, detail="API key has expired")
        
        return metadata
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        raise HTTPException(status_code=401, detail="Invalid API key")

def get_cached_logo(domain: str) -> Optional[Dict[str, Any]]:
    """
    Get cached logo for a domain.
    
    Args:
        domain: Domain to get logo for
        
    Returns:
        Cached logo data or None if not cached or expired
    """
    cache_file = os.path.join(LOGO_CACHE_DIR, f"{domain}.json")
    
    if not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file, "r") as f:
            cached_data = json.load(f)
        
        # Check if cache has expired
        if time.time() - cached_data["timestamp"] > LOGO_CACHE_EXPIRY:
            return None
        
        return cached_data
    except Exception as e:
        logger.error(f"Error reading cached logo for {domain}: {e}")
        return None

def save_logo_to_cache(domain: str, logo_data: Dict[str, Any]) -> bool:
    """
    Save logo to cache.
    
    Args:
        domain: Domain to save logo for
        logo_data: Logo data to save
        
    Returns:
        Whether the operation was successful
    """
    cache_file = os.path.join(LOGO_CACHE_DIR, f"{domain}.json")
    
    try:
        # Add timestamp to cache
        logo_data["timestamp"] = time.time()
        
        with open(cache_file, "w") as f:
            json.dump(logo_data, f)
        
        return True
    except Exception as e:
        logger.error(f"Error saving logo to cache for {domain}: {e}")
        return False

def get_domain_from_url(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain name
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return url

def clean_domain(domain: str) -> str:
    """
    Clean domain name.
    
    Args:
        domain: Domain to clean
        
    Returns:
        Cleaned domain
    """
    # Ensure domain is lowercase
    domain = domain.lower()
    
    # Remove protocol if present
    if "://" in domain:
        domain = domain.split("://")[1]
    
    # Remove www. prefix if present
    if domain.startswith("www."):
        domain = domain[4:]
    
    # Remove path if present
    domain = domain.split("/")[0]
    
    # Remove port if present
    domain = domain.split(":")[0]
    
    return domain

def fetch_logo_from_clearbit(domain: str) -> Optional[Dict[str, Any]]:
    """
    Fetch logo from Clearbit Logo API.
    
    Args:
        domain: Domain to fetch logo for
        
    Returns:
        Logo data or None if not found
    """
    try:
        url = f"https://logo.clearbit.com/{domain}"
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            return None
        
        # Determine image format
        content_type = response.headers.get("Content-Type", "")
        format = "png"  # Default
        
        if "jpeg" in content_type or "jpg" in content_type:
            format = "jpg"
        elif "png" in content_type:
            format = "png"
        elif "svg" in content_type:
            format = "svg"
        
        # Encode image data as base64
        image_data = base64.b64encode(response.content).decode("utf-8")
        
        return {
            "domain": domain,
            "logo_url": url,
            "logo_data": image_data,
            "format": format,
            "source": "clearbit"
        }
    except Exception as e:
        logger.error(f"Error fetching logo from Clearbit for {domain}: {e}")
        return None

def fetch_logo_from_google(domain: str) -> Optional[Dict[str, Any]]:
    """
    Fetch logo from Google (fallback method).
    
    Args:
        domain: Domain to fetch logo for
        
    Returns:
        Logo data or None if not found
    """
    try:
        # This is a placeholder. In a production environment, you would implement
        # an approved method to fetch logos, such as using a paid API or
        # an authorized data source.
        return None
    except Exception as e:
        logger.error(f"Error fetching logo from Google for {domain}: {e}")
        return None

def fetch_logo(domain: str, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Fetch logo for a domain.
    
    Args:
        domain: Domain to fetch logo for
        force_refresh: Whether to force a refresh of cached logo
        
    Returns:
        Logo data
    """
    domain = clean_domain(domain)
    
    # Check cache first
    if not force_refresh:
        cached_logo = get_cached_logo(domain)
        if cached_logo:
            cached_logo["cached"] = True
            return cached_logo
    
    # Try Clearbit
    logo_data = fetch_logo_from_clearbit(domain)
    
    # If not found, try fallback method
    if not logo_data:
        logo_data = fetch_logo_from_google(domain)
    
    # If still not found, return empty response
    if not logo_data:
        logo_data = {
            "domain": domain,
            "logo_url": None,
            "logo_data": None,
            "format": None,
            "source": "none",
            "cached": False
        }
    else:
        logo_data["cached"] = False
        # Save to cache
        save_logo_to_cache(domain, logo_data)
    
    return logo_data

def extract_company_name(domain: str) -> str:
    """
    Extract company name from domain.
    
    Args:
        domain: Domain to extract company name from
        
    Returns:
        Company name
    """
    # Remove TLD
    name = domain.split(".")[0]
    
    # Replace dashes with spaces
    name = name.replace("-", " ")
    
    # Title case
    name = name.title()
    
    return name

# API endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LLMRank.io MCP Logo API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

@app.get("/api/logos/{domain}", response_model=LogoResponse)
async def get_logo(
    domain: str = Path(..., description="Domain to get logo for"),
    force_refresh: bool = Query(False, description="Whether to force a refresh of cached logo"),
    key_metadata: Dict[str, Any] = Depends(validate_api_key)
):
    """
    Get logo for a domain.
    
    Args:
        domain: Domain to get logo for
        force_refresh: Whether to force a refresh of cached logo
        key_metadata: Key metadata from validation
        
    Returns:
        Logo data
    """
    logo_data = fetch_logo(domain, force_refresh)
    return logo_data

@app.post("/api/logos", response_model=LogoResponse)
async def post_logo(
    request: DomainRequest,
    key_metadata: Dict[str, Any] = Depends(validate_api_key)
):
    """
    Get logo for a domain (POST method).
    
    Args:
        request: Domain request
        key_metadata: Key metadata from validation
        
    Returns:
        Logo data
    """
    logo_data = fetch_logo(request.domain, request.force_refresh)
    return logo_data

@app.post("/api/logos/bulk", response_model=List[LogoResponse])
async def bulk_logo(
    request: BulkLogoRequest,
    key_metadata: Dict[str, Any] = Depends(validate_api_key)
):
    """
    Get logos for multiple domains.
    
    Args:
        request: Bulk logo request
        key_metadata: Key metadata from validation
        
    Returns:
        List of logo data
    """
    results = []
    
    for domain in request.domains:
        logo_data = fetch_logo(domain, request.force_refresh)
        results.append(logo_data)
    
    return results

@app.get("/api/logos/{domain}/image")
async def get_logo_image(
    domain: str = Path(..., description="Domain to get logo for"),
    force_refresh: bool = Query(False, description="Whether to force a refresh of cached logo"),
    key_metadata: Dict[str, Any] = Depends(validate_api_key)
):
    """
    Get logo image for a domain.
    
    Args:
        domain: Domain to get logo for
        force_refresh: Whether to force a refresh of cached logo
        key_metadata: Key metadata from validation
        
    Returns:
        Logo image
    """
    logo_data = fetch_logo(domain, force_refresh)
    
    if not logo_data["logo_data"]:
        raise HTTPException(status_code=404, detail="Logo not found")
    
    # Decode base64 image data
    image_data = base64.b64decode(logo_data["logo_data"])
    
    # Determine content type
    content_type = "image/png"  # Default
    if logo_data["format"] == "jpg":
        content_type = "image/jpeg"
    elif logo_data["format"] == "png":
        content_type = "image/png"
    elif logo_data["format"] == "svg":
        content_type = "image/svg+xml"
    
    return Response(content=image_data, media_type=content_type)

if __name__ == "__main__":
    print("\n====== STARTING MCP LOGO SERVICE ======")
    print("Logo API documentation available at: http://localhost:6500/docs")
    print("=======================================\n")
    
    uvicorn.run(app, host="0.0.0.0", port=6500)