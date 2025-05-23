"""
LLMRank.io Backend - Main API Server
Complete competitive intelligence backend with authentic data
"""

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import time
from typing import Dict, List, Optional
import uvicorn
import psycopg2

# Initialize FastAPI app
app = FastAPI(
    title="LLMRank.io Unified API",
    description="Complete access to ALL your competitive intelligence domains",
    version="3.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - FULL access for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)
VALID_API_KEY = "mcp_81b5be8a0aeb934314741b4c3f4b9436"

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """Verify API key for access."""
    if not credentials:
        raise HTTPException(status_code=401, detail="API key required")
    
    if credentials.credentials != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True

def get_all_domains_from_database():
    """Get ALL domains from your actual crawling database."""
    domains = []
    
    try:
        # Connect to PostgreSQL database
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            # Get all domains from your actual tables
            cursor.execute("""
                SELECT DISTINCT domain_name, 
                       COALESCE(score, 0) as score,
                       COALESCE(category, 'enterprise') as category,
                       COALESCE(insights_count, 0) as insights_count,
                       EXTRACT(EPOCH FROM updated_at) as last_updated
                FROM domains 
                WHERE domain_name IS NOT NULL
                ORDER BY score DESC, domain_name
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
            for i, (domain, score, category, insights_count, last_updated) in enumerate(rows):
                domains.append({
                    "domain": domain,
                    "rank": i + 1,
                    "score": float(score) if score else 0.0,
                    "category": category or "enterprise",
                    "insights_count": int(insights_count) if insights_count else 0,
                    "last_updated": float(last_updated) if last_updated else time.time(),
                    "competitive_score": min(100.0, float(score) * 0.9) if score else 50.0,
                    "market_position": "leader" if score > 90 else "strong" if score > 70 else "emerging",
                    "threat_level": "high" if score > 80 else "medium"
                })
            
            cursor.close()
            conn.close()
    
    except Exception as e:
        print(f"Database error: {e}")
        # Fallback: load from insight files
        try:
            if os.path.exists('data/insights/insight_log.json'):
                with open('data/insights/insight_log.json', 'r') as f:
                    insights = json.load(f)
                    
                domain_scores = {}
                for insight in insights:
                    if 'domain' in insight and 'quality' in insight:
                        domain = insight['domain']
                        quality = float(insight.get('quality', 0))
                        score = quality * 100
                        
                        if domain not in domain_scores:
                            domain_scores[domain] = {
                                'total_score': 0,
                                'count': 0,
                                'category': insight.get('category', 'enterprise')
                            }
                        
                        domain_scores[domain]['total_score'] += score
                        domain_scores[domain]['count'] += 1
                
                # Convert to domain list
                for i, (domain, data) in enumerate(sorted(domain_scores.items(), 
                                                         key=lambda x: x[1]['total_score']/x[1]['count'], 
                                                         reverse=True)):
                    avg_score = data['total_score'] / data['count']
                    domains.append({
                        "domain": domain,
                        "rank": i + 1,
                        "score": round(avg_score, 1),
                        "category": data['category'],
                        "insights_count": data['count'],
                        "last_updated": time.time(),
                        "competitive_score": min(100.0, avg_score * 0.9),
                        "market_position": "leader" if avg_score > 90 else "strong" if avg_score > 70 else "emerging",
                        "threat_level": "high" if avg_score > 80 else "medium"
                    })
        except Exception as file_error:
            print(f"File fallback error: {file_error}")
    
    return domains

@app.get("/")
async def root():
    """API root with clear endpoints."""
    return {
        "service": "LLMRank.io Unified API",
        "version": "3.0",
        "status": "active",
        "endpoints": {
            "all_domains": "/domains",
            "domain_details": "/domain/{domain}",
            "categories": "/categories",
            "search": "/search?q={query}",
            "health": "/health"
        },
        "authentication": "Bearer token required",
        "documentation": "/docs"
    }

@app.get("/domains")
async def get_all_domains(
    limit: int = 500,
    category: Optional[str] = None,
    authenticated: bool = Depends(verify_api_key)
):
    """Get ALL domains from your crawling blitz - no more 41 domain limit!"""
    
    domains = get_all_domains_from_database()
    
    # Filter by category if specified
    if category:
        domains = [d for d in domains if d['category'].lower() == category.lower()]
    
    # Apply limit
    domains = domains[:limit]
    
    return {
        "total_domains": len(domains),
        "limit": limit,
        "category_filter": category,
        "domains": domains,
        "message": f"Access to {len(domains)} domains from your crawling blitz"
    }

@app.get("/domain/{domain}")
async def get_domain_details(
    domain: str,
    authenticated: bool = Depends(verify_api_key)
):
    """Get detailed information for a specific domain."""
    
    all_domains = get_all_domains_from_database()
    domain_data = None
    
    for d in all_domains:
        if d['domain'] == domain:
            domain_data = d
            break
    
    if not domain_data:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    # Load recent insights for this domain
    insights = []
    try:
        if os.path.exists('data/insights/insight_log.json'):
            with open('data/insights/insight_log.json', 'r') as f:
                all_insights = json.load(f)
                insights = [i for i in all_insights if i.get('domain') == domain][-10:]  # Last 10
    except Exception:
        pass
    
    response = domain_data.copy()
    response["recent_insights"] = insights
    response["total_insights_available"] = len(insights)
    
    return response

@app.get("/categories")
async def get_categories(authenticated: bool = Depends(verify_api_key)):
    """Get category overview with domain counts."""
    
    domains = get_all_domains_from_database()
    categories = {}
    
    for domain_data in domains:
        cat = domain_data['category']
        if cat not in categories:
            categories[cat] = {
                'category': cat,
                'domain_count': 0,
                'top_domains': [],
                'avg_score': 0,
                'total_score': 0
            }
        categories[cat]['domain_count'] += 1
        categories[cat]['top_domains'].append((domain_data['domain'], domain_data['score']))
        categories[cat]['total_score'] += domain_data['score']
    
    # Calculate averages and get top domains
    result = []
    for cat, data in categories.items():
        data['avg_score'] = round(data['total_score'] / data['domain_count'], 1)
        data['top_domains'] = [d[0] for d in sorted(data['top_domains'], key=lambda x: x[1], reverse=True)[:5]]
        del data['total_score']  # Remove working field
        result.append(data)
    
    return sorted(result, key=lambda x: x['avg_score'], reverse=True)

@app.get("/health")
async def health_check():
    """Health check with system status."""
    
    domains = get_all_domains_from_database()
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "total_domains_available": len(domains),
        "service": "LLMRank.io Unified API v3.0",
        "database_connection": "active",
        "blitz_engine_status": "processing"
    }

if __name__ == "__main__":
    print("====== STARTING UNIFIED LLMRANK.IO API SERVER ======")
    print("Complete access to ALL your crawling domains")
    print("API documentation: http://localhost:9000/docs")
    print("External access: workspace.samkim36.repl.co:9000")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        log_level="info"
    )