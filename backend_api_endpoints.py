"""
Backend API Endpoints
Provides structured data contracts for frontend UI components
"""

from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional, Dict
import json
import os
from domain_index_builder import get_domain_suggestions, build_domain_index
import requests
from urllib.parse import urlparse

app = FastAPI(title="LLMPageRank Backend API", version="1.0")

def load_domain_data():
    """Load all domain data from insights"""
    try:
        with open('data/insights/insight_log.json', 'r') as f:
            insights = json.load(f)
        
        # Build domain lookup
        domain_data = {}
        for insight in insights:
            domain = insight.get('domain')
            if domain:
                if domain not in domain_data:
                    domain_data[domain] = {
                        'domain': domain,
                        'display_name': domain.replace('.com', '').replace('.', ' ').title(),
                        'insights': [],
                        'latest_quality': 0,
                        'total_insights': 0
                    }
                
                domain_data[domain]['insights'].append(insight)
                domain_data[domain]['total_insights'] += 1
                quality = insight.get('quality_score', 0)
                if quality > domain_data[domain]['latest_quality']:
                    domain_data[domain]['latest_quality'] = quality
        
        return domain_data
    except Exception as e:
        print(f"Error loading domain data: {e}")
        return {}

@app.get("/api/search")
async def search_domains(q: str = Query(..., description="Search query")):
    """
    Search endpoint for domain autocomplete and filtering
    Returns structured data contract for frontend search components
    """
    try:
        # Load domain index
        try:
            with open('data/domain_index.json', 'r') as f:
                domains = json.load(f)
        except:
            domains = build_domain_index()
        
        # Filter domains based on query
        query = q.lower()
        filtered_domains = []
        
        for domain_data in domains:
            domain = domain_data.get('domain', '')
            display_name = domain_data.get('display_name', '')
            
            if (query in domain.lower() or 
                query in display_name.lower()):
                
                # Structure for frontend consumption
                result = {
                    'domain': domain,
                    'display_name': display_name,
                    'quality_score': domain_data.get('quality_score', 0),
                    'insight_count': domain_data.get('insight_count', 0),
                    'has_insights': domain_data.get('has_insights', False),
                    'category': 'enterprise' if domain_data.get('quality_score', 0) > 0.8 else 'standard'
                }
                filtered_domains.append(result)
        
        # Sort by quality score descending
        filtered_domains.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return {
            'query': q,
            'results': filtered_domains[:20],  # Limit to 20 results
            'total_count': len(filtered_domains),
            'has_more': len(filtered_domains) > 20
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/domain/{domain_name}")
async def get_domain_details(domain_name: str):
    """
    Domain details endpoint
    Returns comprehensive domain data contract for frontend detail views
    """
    try:
        domain_data = load_domain_data()
        
        if domain_name not in domain_data:
            raise HTTPException(status_code=404, detail="Domain not found")
        
        data = domain_data[domain_name]
        insights = data['insights']
        
        # Calculate aggregated metrics
        quality_scores = [i.get('quality_score', 0) for i in insights if i.get('quality_score', 0) > 0]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Get latest insight
        latest_insight = max(insights, key=lambda x: x.get('timestamp', 0)) if insights else {}
        
        # Structure comprehensive domain response
        response = {
            'domain': domain_name,
            'display_name': data['display_name'],
            'overview': {
                'total_insights': data['total_insights'],
                'average_quality': round(avg_quality, 2),
                'latest_quality': data['latest_quality'],
                'last_updated': latest_insight.get('timestamp'),
                'status': 'active' if data['latest_quality'] > 0.7 else 'monitoring'
            },
            'competitive_metrics': {
                'market_position': 'leader' if avg_quality > 0.8 else 'challenger',
                'authority_score': min(avg_quality + 0.1, 1.0),
                'visibility_rank': len([d for d in domain_data.values() if d['latest_quality'] > avg_quality]) + 1,
                'trend': 'stable'
            },
            'insights': [
                {
                    'id': i.get('id', ''),
                    'content': i.get('content', '')[:200] + '...' if len(i.get('content', '')) > 200 else i.get('content', ''),
                    'quality_score': i.get('quality_score', 0),
                    'timestamp': i.get('timestamp', 0),
                    'category': i.get('category', 'general')
                } for i in insights[-5:]  # Last 5 insights
            ],
            'metadata': {
                'data_freshness': 'recent',
                'confidence_level': 'high' if avg_quality > 0.8 else 'medium',
                'last_scan': latest_insight.get('timestamp')
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch domain: {str(e)}")

@app.get("/api/logo")
async def get_domain_logo(domain: str = Query(..., description="Domain name")):
    """
    Logo proxy endpoint
    Returns logo URL or fallback for domain branding
    """
    try:
        # Clean domain name
        clean_domain = domain.lower().strip()
        if not clean_domain.startswith('http'):
            clean_domain = f"https://{clean_domain}"
        
        parsed = urlparse(clean_domain)
        domain_name = parsed.netloc or parsed.path
        
        # Try different logo services in order of preference
        logo_sources = [
            f"https://logo.clearbit.com/{domain_name}",
            f"https://www.google.com/s2/favicons?domain={domain_name}&sz=128",
            f"https://favicons.githubusercontent.com/{domain_name}",
        ]
        
        # Test each logo source
        for logo_url in logo_sources:
            try:
                response = requests.head(logo_url, timeout=3)
                if response.status_code == 200:
                    return {
                        'domain': domain_name,
                        'logo_url': logo_url,
                        'source': 'external',
                        'status': 'available',
                        'fallback': False
                    }
            except:
                continue
        
        # Fallback response
        return {
            'domain': domain_name,
            'logo_url': '/logo-missing.png',
            'source': 'fallback',
            'status': 'missing',
            'fallback': True,
            'message': 'No logo found, using fallback'
        }
        
    except Exception as e:
        return {
            'domain': domain,
            'logo_url': '/logo-missing.png',
            'source': 'fallback',
            'status': 'error',
            'fallback': True,
            'error': str(e)
        }

@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    try:
        domain_data = load_domain_data()
        return {
            'status': 'healthy',
            'domains_available': len(domain_data),
            'endpoints': {
                'search': '/api/search?q=',
                'domain': '/api/domain/{name}',
                'logo': '/api/logo?domain='
            },
            'version': '1.0'
        }
    except Exception as e:
        return {
            'status': 'degraded',
            'error': str(e),
            'version': '1.0'
        }

# CORS middleware for frontend integration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Backend API Server")
    print("📡 Endpoints available:")
    print("   GET /api/search?q={query}")
    print("   GET /api/domain/{domain_name}")
    print("   GET /api/logo?domain={domain}")
    print("   GET /api/health")
    uvicorn.run(app, host="0.0.0.0", port=9001)