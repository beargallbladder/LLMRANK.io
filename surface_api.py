"""
The Surface API

This module provides FastAPI endpoints for the EchoLayer architecture
as outlined in Migration Blueprint MB-01.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Body, Query, Path
from pydantic import BaseModel, Field
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SURFACE_DATA_DIR = "data/surface"
os.makedirs(SURFACE_DATA_DIR, exist_ok=True)

BRAND_SURFACES_PATH = os.path.join(SURFACE_DATA_DIR, "brand_surfaces.json")
LLM_PICKUP_PATH = os.path.join(SURFACE_DATA_DIR, "llm_pickup.json")
CLAIMS_PATH = os.path.join(SURFACE_DATA_DIR, "claims.json")

# Create FastAPI app
app = FastAPI(
    title="LLMPageRank EchoLayer API",
    description="API for the EchoLayer architecture of LLMPageRank",
    version="1.0.0"
)

# Pydantic models for request/response validation
class BrandData(BaseModel):
    name: str = Field(..., description="Brand name")
    domain: str = Field(..., description="Brand domain")
    industry: Optional[str] = Field(None, description="Brand industry")
    description: Optional[str] = Field(None, description="Brand description")

class SurfaceResponse(BaseModel):
    slug: str = Field(..., description="Brand slug")
    brand_name: str = Field(..., description="Brand name")
    domain: str = Field(..., description="Brand domain")
    miss_score: float = Field(..., description="MISS score")
    preservation_score: float = Field(..., description="Preservation score")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    claimed: bool = Field(..., description="Whether the surface is claimed")
    summary: str = Field(..., description="Brand summary")
    faq: List[Dict[str, str]] = Field(..., description="Brand FAQ items")
    tags: List[str] = Field(..., description="Brand tags")

class ContentUpdate(BaseModel):
    summary: Optional[str] = Field(None, description="Updated summary")
    faq: Optional[List[Dict[str, str]]] = Field(None, description="Updated FAQ items")
    tags: Optional[List[str]] = Field(None, description="Updated tags")

class PickupData(BaseModel):
    llm_model: str = Field(..., description="LLM model name")
    query: str = Field(..., description="Query used for testing")
    picked_up: bool = Field(..., description="Whether the model picked up information")

class ClaimRequest(BaseModel):
    email: str = Field(..., description="Business email")
    name: str = Field(..., description="Contact name")
    title: str = Field(..., description="Contact title")

class ApiResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict] = Field(None, description="Response data")

# Helper functions
def load_surfaces():
    """Load all brand surfaces from file."""
    surfaces = {}
    try:
        if os.path.exists(BRAND_SURFACES_PATH):
            with open(BRAND_SURFACES_PATH, 'r') as f:
                surfaces = json.load(f)
    except Exception as e:
        logger.error(f"Error loading surfaces: {e}")
        surfaces = {}
    return surfaces

def save_surfaces(surfaces):
    """Save brand surfaces to file."""
    try:
        with open(BRAND_SURFACES_PATH, 'w') as f:
            json.dump(surfaces, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving surfaces: {e}")
        return False

def load_pickup_data():
    """Load LLM pickup data from file."""
    pickup_data = {}
    try:
        if os.path.exists(LLM_PICKUP_PATH):
            with open(LLM_PICKUP_PATH, 'r') as f:
                pickup_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading pickup data: {e}")
        pickup_data = {}
    return pickup_data

def save_pickup_data(pickup_data):
    """Save LLM pickup data to file."""
    try:
        with open(LLM_PICKUP_PATH, 'w') as f:
            json.dump(pickup_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving pickup data: {e}")
        return False

def load_claims():
    """Load all claims from file."""
    claims = {}
    try:
        if os.path.exists(CLAIMS_PATH):
            with open(CLAIMS_PATH, 'r') as f:
                claims = json.load(f)
    except Exception as e:
        logger.error(f"Error loading claims: {e}")
        claims = {}
    return claims

def save_claims(claims):
    """Save claims to file."""
    try:
        with open(CLAIMS_PATH, 'w') as f:
            json.dump(claims, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving claims: {e}")
        return False

def create_brand_slug(brand_name):
    """Create a URL-friendly slug from a brand name."""
    if not brand_name:
        return ""
    # Convert to lowercase and replace spaces with hyphens
    slug = brand_name.lower().replace(' ', '-')
    # Remove special characters
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    return slug

def verify_domain_ownership(email, domain):
    """
    Verify that the user owns the domain.
    
    In a real implementation, this would send a verification email
    or check for DNS verification. For this demo, we'll assume any
    email that matches the domain is valid.
    """
    try:
        email_domain = email.split('@')[1]
        if email_domain == domain or domain.endswith('.' + email_domain):
            return True
        return False
    except:
        return False

def generate_memory_draft(brand_data):
    """Generate a memory draft for a brand."""
    brand_name = brand_data.get('name')
    industry = brand_data.get('industry', 'technology')
    
    # Generate summary
    summary = f"{brand_name} is a company in the {industry} industry known for its innovative approach to solving customer challenges. The brand has established a strong presence in its market segment."
    
    # Generate FAQ
    faq = [
        {
            'question': f"What does {brand_name} do?",
            'answer': f"{brand_name} provides solutions in the {industry} space, focusing on quality and customer satisfaction."
        },
        {
            'question': f"When was {brand_name} founded?",
            'answer': f"{brand_name} was founded to address key challenges in the {industry} sector."
        },
        {
            'question': f"What makes {brand_name} unique?",
            'answer': f"{brand_name} differentiates itself through its commitment to innovation and customer-centric approach."
        }
    ]
    
    # Generate JSON-LD schema
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": brand_name,
        "url": f"https://{brand_data.get('domain')}",
        "description": summary,
        "industry": industry
    }
    
    # Generate tags
    tags = [industry, 'company'] 
    if brand_name:
        tags.append(brand_name.lower())
    
    return {
        'summary': summary,
        'faq': faq,
        'json_ld': json_ld,
        'tags': tags
    }

# API endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "LLMPageRank EchoLayer API",
        "version": "1.0.0",
        "description": "API for the EchoLayer architecture of LLMPageRank"
    }

@app.get("/surface", response_model=List[SurfaceResponse])
async def get_all_surfaces():
    """Get all brand surfaces."""
    surfaces = load_surfaces()
    return list(surfaces.values())

@app.get("/surface/{slug}", response_model=SurfaceResponse)
async def get_surface(slug: str = Path(..., description="Brand slug")):
    """Get a brand surface by slug."""
    surfaces = load_surfaces()
    if slug not in surfaces:
        raise HTTPException(status_code=404, detail="Surface not found")
    return surfaces[slug]

@app.post("/surface/generate", response_model=SurfaceResponse)
async def generate_surface(brand_data: BrandData):
    """Generate a brand surface."""
    surfaces = load_surfaces()
    
    # Create slug
    slug = create_brand_slug(brand_data.name)
    
    if slug in surfaces:
        # Update existing surface
        surface = surfaces[slug]
        surface['updated_at'] = datetime.now().isoformat()
    else:
        # Create new surface
        surface = {
            'slug': slug,
            'brand_name': brand_data.name,
            'domain': brand_data.domain,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'claimed': False,
            'miss_score': 0.0,
            'miss_history': [],
            'signal_audit': {},
            'summary': '',
            'faq': [],
            'json_ld': {},
            'drift_deltas': [],
            'preservation_score': 0.0,
            'llm_pickup': {
                'gpt4': 0,
                'claude': 0
            },
            'tags': []
        }
    
    # Generate memory draft
    draft = generate_memory_draft(brand_data.dict())
    
    surface['summary'] = draft['summary']
    surface['faq'] = draft['faq']
    surface['json_ld'] = draft['json_ld']
    surface['tags'] = draft['tags']
    
    # Calculate preservation score
    has_summary = bool(surface['summary'])
    has_faq = len(surface['faq']) > 0
    has_schema = bool(surface['json_ld'])
    has_history = len(surface['miss_history']) > 0
    
    preservation_score = sum([
        0.25 if has_summary else 0,
        0.25 if has_faq else 0,
        0.25 if has_schema else 0,
        0.25 if has_history else 0
    ])
    
    surface['preservation_score'] = preservation_score
    
    # Save surface
    surfaces[slug] = surface
    save_surfaces(surfaces)
    
    return surface

@app.post("/surface/{slug}/track-pickup", response_model=ApiResponse)
async def track_llm_pickup(
    slug: str = Path(..., description="Brand slug"),
    pickup_data: PickupData = Body(..., description="Pickup data")
):
    """Track LLM pickup for a brand surface."""
    surfaces = load_surfaces()
    if slug not in surfaces:
        raise HTTPException(status_code=404, detail="Surface not found")
    
    pickup_data_dict = load_pickup_data()
    
    # Initialize tracking for this brand if needed
    if slug not in pickup_data_dict:
        pickup_data_dict[slug] = {}
    
    # Initialize tracking for this model if needed
    model = pickup_data.llm_model
    if model not in pickup_data_dict[slug]:
        pickup_data_dict[slug][model] = {
            'queries': [],
            'pickup_count': 0,
            'total_queries': 0
        }
    
    # Update tracking
    model_data = pickup_data_dict[slug][model]
    model_data['queries'].append({
        'query': pickup_data.query,
        'picked_up': pickup_data.picked_up,
        'timestamp': datetime.now().isoformat()
    })
    
    if pickup_data.picked_up:
        model_data['pickup_count'] += 1
    
    model_data['total_queries'] += 1
    
    # Update the surface with the pickup count
    if model in surfaces[slug]['llm_pickup']:
        surfaces[slug]['llm_pickup'][model] = model_data['pickup_count']
    
    # Save data
    save_pickup_data(pickup_data_dict)
    save_surfaces(surfaces)
    
    return {
        "status": "success",
        "message": "Pickup tracked successfully",
        "data": model_data
    }

@app.post("/surface/{slug}/claim", response_model=ApiResponse)
async def claim_surface(
    slug: str = Path(..., description="Brand slug"),
    claim_data: ClaimRequest = Body(..., description="Claim request data")
):
    """Claim a brand surface."""
    surfaces = load_surfaces()
    if slug not in surfaces:
        raise HTTPException(status_code=404, detail="Surface not found")
    
    surface = surfaces[slug]
    if surface.get('claimed', False):
        raise HTTPException(status_code=400, detail="Surface already claimed")
    
    # Verify domain ownership
    domain = surface.get('domain', '').lower()
    if not verify_domain_ownership(claim_data.email, domain):
        raise HTTPException(status_code=400, detail="Email doesn't match domain")
    
    # Save claim
    claims = load_claims()
    
    if slug not in claims:
        claims[slug] = []
    
    # Check if this email already made a claim
    for claim in claims[slug]:
        if claim.get('email') == claim_data.email:
            return {
                "status": "error",
                "message": "You've already claimed this surface",
                "data": None
            }
    
    # Add new claim
    claims[slug].append({
        'email': claim_data.email,
        'name': claim_data.name,
        'title': claim_data.title,
        'timestamp': datetime.now().isoformat(),
        'status': 'pending'
    })
    
    save_claims(claims)
    
    return {
        "status": "success",
        "message": "Claim submitted successfully",
        "data": {
            "brand": surface.get('brand_name'),
            "domain": domain,
            "status": "pending"
        }
    }

@app.put("/surface/{slug}/content", response_model=ApiResponse)
async def update_surface_content(
    slug: str = Path(..., description="Brand slug"),
    content_update: ContentUpdate = Body(..., description="Content update data")
):
    """Update content for a claimed brand surface."""
    surfaces = load_surfaces()
    if slug not in surfaces:
        raise HTTPException(status_code=404, detail="Surface not found")
    
    surface = surfaces[slug]
    
    # In a real implementation, we would verify user authentication and ownership
    # For this demo, we'll skip that step
    
    # Update content fields
    if content_update.summary is not None:
        surface['summary'] = content_update.summary
    
    if content_update.faq is not None:
        surface['faq'] = content_update.faq
    
    if content_update.tags is not None:
        surface['tags'] = content_update.tags
    
    # Update timestamp
    surface['updated_at'] = datetime.now().isoformat()
    
    # Recalculate preservation score
    has_summary = bool(surface['summary'])
    has_faq = len(surface['faq']) > 0
    has_schema = bool(surface['json_ld'])
    has_history = len(surface['miss_history']) > 0
    
    preservation_score = sum([
        0.25 if has_summary else 0,
        0.25 if has_faq else 0,
        0.25 if has_schema else 0,
        0.25 if has_history else 0
    ])
    
    surface['preservation_score'] = preservation_score
    
    # Save data
    surfaces[slug] = surface
    save_surfaces(surfaces)
    
    return {
        "status": "success",
        "message": "Content updated successfully",
        "data": {
            "brand": surface.get('brand_name'),
            "slug": slug,
            "preservation_score": preservation_score
        }
    }

@app.get("/surface/{slug}/pickup", response_model=ApiResponse)
async def get_pickup_data(slug: str = Path(..., description="Brand slug")):
    """Get LLM pickup data for a brand surface."""
    pickup_data_dict = load_pickup_data()
    if slug not in pickup_data_dict:
        return {
            "status": "success",
            "message": "No pickup data available",
            "data": {}
        }
    
    return {
        "status": "success",
        "message": "Pickup data retrieved successfully",
        "data": pickup_data_dict[slug]
    }

@app.get("/domains")
async def get_domains(
    limit: Optional[int] = Query(100, description="Maximum number of domains to return"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get all domains from competitive intelligence database."""
    # Load authentic domain data from your competitive intelligence system
    try:
        import psycopg2
        import os
        
        # Connect to your PostgreSQL database
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Build query based on filters
        base_query = """
        SELECT DISTINCT 
            domain, 
            COALESCE(category, 'unknown') as category,
            COALESCE(score, 0) as score,
            COALESCE(rank, 0) as rank,
            COALESCE(insights_count, 0) as insights_count,
            COALESCE(competitive_score, 0) as competitive_score,
            COALESCE(market_position, 'challenger') as market_position
        FROM domains 
        WHERE domain IS NOT NULL
        """
        
        params = []
        if category:
            base_query += " AND LOWER(category) = LOWER(%s)"
            params.append(category)
            
        base_query += " ORDER BY score DESC, rank ASC"
        
        if limit:
            base_query += " LIMIT %s"
            params.append(limit)
        
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        
        domains = []
        for row in rows:
            domains.append({
                'domain': row[0],
                'category': row[1],
                'score': float(row[2]),
                'rank': int(row[3]) if row[3] else 999,
                'insights_count': int(row[4]),
                'competitive_score': float(row[5]),
                'market_position': row[6]
            })
        
        cursor.close()
        conn.close()
        
        return domains
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        # Fallback: return empty list if database unavailable
        return []

@app.get("/domain/{domain}")
async def get_domain_details(domain: str = Path(..., description="Domain name")):
    """Get detailed information for a specific domain."""
    try:
        import psycopg2
        import os
        
        # Connect to your PostgreSQL database
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Get domain details
        cursor.execute("""
        SELECT 
            domain, 
            COALESCE(category, 'unknown') as category,
            COALESCE(score, 0) as score,
            COALESCE(rank, 0) as rank,
            COALESCE(insights_count, 0) as insights_count,
            COALESCE(competitive_score, 0) as competitive_score,
            COALESCE(market_position, 'challenger') as market_position
        FROM domains 
        WHERE LOWER(domain) = LOWER(%s)
        LIMIT 1
        """, (domain,))
        
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Get recent insights for this domain
        cursor.execute("""
        SELECT content, quality_score, created_at
        FROM insights 
        WHERE LOWER(domain) = LOWER(%s)
        ORDER BY created_at DESC 
        LIMIT 5
        """, (domain,))
        
        insights_rows = cursor.fetchall()
        recent_insights = []
        for insight_row in insights_rows:
            recent_insights.append({
                'content': insight_row[0],
                'quality_score': float(insight_row[1]) if insight_row[1] else 0.0,
                'created_at': insight_row[2].isoformat() if insight_row[2] else None
            })
        
        cursor.close()
        conn.close()
        
        domain_data = {
            'domain': row[0],
            'category': row[1],
            'score': float(row[2]),
            'rank': int(row[3]) if row[3] else 999,
            'insights_count': int(row[4]),
            'competitive_score': float(row[5]),
            'market_position': row[6],
            'recent_insights': recent_insights
        }
        
        return domain_data
        
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Error getting domain details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/categories")
async def get_categories():
    """Get all categories with domain counts."""
    try:
        import psycopg2
        import os
        
        # Connect to your PostgreSQL database
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Get categories with counts
        cursor.execute("""
        SELECT 
            COALESCE(category, 'unknown') as category,
            COUNT(*) as domain_count
        FROM domains 
        WHERE domain IS NOT NULL
        GROUP BY category
        ORDER BY domain_count DESC
        """)
        
        rows = cursor.fetchall()
        
        categories = []
        for row in rows:
            categories.append({
                'category': row[0],
                'domain_count': int(row[1])
            })
        
        cursor.close()
        conn.close()
        
        return categories
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        return []

@app.get("/miss", response_model=ApiResponse)
async def get_miss_score(domain: str = Query(..., description="Domain name")):
    """Get MISS score for a domain."""
    # In a real implementation, this would calculate the MISS score
    # For this demo, we'll return a placeholder
    return {
        "status": "success",
        "message": "MISS score retrieved successfully",
        "data": {
            "domain": domain,
            "miss_score": 50.0
        }
    }

@app.get("/signal", response_model=ApiResponse)
async def get_signal_score(domain: str = Query(..., description="Domain name")):
    """Get signal score for a domain."""
    # In a real implementation, this would calculate the signal score
    # For this demo, we'll return a placeholder
    return {
        "status": "success",
        "message": "Signal score retrieved successfully",
        "data": {
            "domain": domain,
            "signal_score": 75.0,
            "signal_delta": 2.5
        }
    }

if __name__ == "__main__":
    uvicorn.run("surface_api:app", host="0.0.0.0", port=8000, reload=True)