"""
Logo Service Fix

This script improves the MCP Logo Service by making it more accessible
and resolving connectivity issues.
"""

import os
import logging
from fastapi import FastAPI, Path, Query, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
import uvicorn
import base64
import requests
from typing import Dict, Any, List, Optional
import time
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
LOGO_CACHE_DIR = "data/logos/fix"
LOGO_CACHE_EXPIRY = 7 * 24 * 60 * 60  # 7 days in seconds

# Ensure directories exist
os.makedirs(LOGO_CACHE_DIR, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="MCP Logo Service",
    description="Logo retrieval service for brands tracked in LLMPageRank",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def clean_domain(domain: str) -> str:
    """Clean domain name (remove www, protocol, etc.)."""
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

def get_cached_logo(domain: str) -> Optional[Dict[str, Any]]:
    """Get cached logo for a domain."""
    cache_file = os.path.join(LOGO_CACHE_DIR, f"{domain}.json")
    
    if not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file, "r") as f:
            import json
            cached_data = json.load(f)
        
        # Check if cache has expired
        if time.time() - cached_data["timestamp"] > LOGO_CACHE_EXPIRY:
            return None
        
        return cached_data
    except Exception as e:
        logger.error(f"Error reading cached logo for {domain}: {e}")
        return None

def save_logo_to_cache(domain: str, logo_data: Dict[str, Any]) -> bool:
    """Save logo to cache."""
    cache_file = os.path.join(LOGO_CACHE_DIR, f"{domain}.json")
    
    try:
        # Add timestamp to cache
        logo_data["timestamp"] = time.time()
        
        with open(cache_file, "w") as f:
            import json
            json.dump(logo_data, f)
        
        return True
    except Exception as e:
        logger.error(f"Error saving logo to cache for {domain}: {e}")
        return False

def fetch_logo_from_clearbit(domain: str) -> Optional[Dict[str, Any]]:
    """Fetch logo from Clearbit Logo API."""
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
            "source": "clearbit",
            "cached": False
        }
    except Exception as e:
        logger.error(f"Error fetching logo from Clearbit for {domain}: {e}")
        return None

def fetch_logo(domain: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Fetch logo for a domain."""
    domain = clean_domain(domain)
    
    # Check cache first
    if not force_refresh:
        cached_logo = get_cached_logo(domain)
        if cached_logo:
            cached_logo["cached"] = True
            return cached_logo
    
    # Try Clearbit
    logo_data = fetch_logo_from_clearbit(domain)
    
    # If not found, return empty response
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
        # Save to cache
        save_logo_to_cache(domain, logo_data)
    
    return logo_data

# Define routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MCP Logo Service",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "mcp_logo_service",
        "version": "1.0.0"
    }

@app.get("/api/logos/{domain}")
async def get_logo(
    domain: str = Path(..., description="Domain to get logo for"),
    force_refresh: bool = Query(False, description="Whether to force a refresh")
):
    """Get logo for a domain."""
    logo_data = fetch_logo(domain, force_refresh)
    return logo_data

@app.post("/api/logos/bulk")
async def bulk_logo(domains: List[str]):
    """Get logos for multiple domains."""
    results = []
    for domain in domains:
        logo_data = fetch_logo(domain)
        results.append(logo_data)
    return results

@app.get("/api/logos/{domain}/image")
async def get_logo_image(
    domain: str = Path(..., description="Domain to get logo for"),
    force_refresh: bool = Query(False, description="Whether to force a refresh")
):
    """Get logo image for a domain."""
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
    port = 6600  # Using a different port to avoid conflicts
    print(f"\n====== STARTING IMPROVED MCP LOGO SERVICE ======")
    print(f"Logo API documentation available at: http://localhost:{port}/docs")
    print(f"=======================================\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)