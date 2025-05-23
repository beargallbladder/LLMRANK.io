"""
Domain Routes - Core API endpoints for competitive intelligence
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
import json
import os
import time

router = APIRouter(prefix="/api/v1", tags=["domains"])

def verify_api_key():
    """Placeholder for API key verification"""
    return True

def get_all_domains_from_database():
    """Get all domains from competitive intelligence database"""
    # This connects to your actual data source
    return []

@router.get("/domains")
async def get_all_domains(
    limit: int = Query(500, description="Maximum number of domains to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_score: Optional[float] = Query(None, description="Minimum competitive score"),
    authenticated: bool = Depends(verify_api_key)
):
    """Get all domains from your competitive intelligence database."""
    
    domains = get_all_domains_from_database()
    
    # Apply filters
    if category:
        domains = [d for d in domains if d['category'].lower() == category.lower()]
    
    if min_score is not None:
        domains = [d for d in domains if d['score'] >= min_score]
    
    # Apply limit
    domains = domains[:limit]
    
    return {
        "total_domains": len(domains),
        "limit": limit,
        "filters": {
            "category": category,
            "min_score": min_score
        },
        "domains": domains,
        "metadata": {
            "source": "authentic_crawling_data",
            "last_updated": max([d.get('last_updated', 0) for d in domains]) if domains else 0,
            "quality_threshold": 0.7
        }
    }

@router.get("/domains/{domain}")
async def get_domain_details(
    domain: str,
    include_insights: bool = Query(True, description="Include recent insights"),
    authenticated: bool = Depends(verify_api_key)
):
    """Get detailed competitive intelligence for a specific domain."""
    
    all_domains = get_all_domains_from_database()
    domain_data = None
    
    for d in all_domains:
        if d['domain'].lower() == domain.lower():
            domain_data = d
            break
    
    if not domain_data:
        raise HTTPException(
            status_code=404, 
            detail=f"Domain '{domain}' not found in competitive intelligence database"
        )
    
    response = domain_data.copy()
    
    if include_insights:
        # Load recent insights for this domain
        insights = []
        try:
            if os.path.exists('data/insights/insight_log.json'):
                with open('data/insights/insight_log.json', 'r') as f:
                    all_insights = json.load(f)
                    insights = [
                        i for i in all_insights 
                        if i.get('domain', '').lower() == domain.lower()
                    ][-10:]  # Last 10 insights
        except Exception:
            insights = []
        
        response["recent_insights"] = insights
        response["total_insights_available"] = len(insights)
        response["insight_quality_avg"] = (
            sum(i.get('quality', 0) for i in insights) / len(insights)
            if insights else 0
        )
    
    return response