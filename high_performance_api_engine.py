"""
High-Performance API Engine
Codename: "Lightning Scale"

Optimized FastAPI architecture for high-volume, low-latency operations
with connection pooling, async processing, and intelligent caching.
"""

import asyncio
import uvloop
import json
import time
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from datetime import datetime
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import asyncpg
import aiofiles
from pydantic import BaseModel, Field
from collections import defaultdict
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use uvloop for better performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Constants
DB_POOL_SIZE = 50  # Large connection pool
REDIS_POOL_SIZE = 20
CACHE_TTL = 300  # 5 minutes
BATCH_SIZE = 1000
MAX_CONCURRENT_REQUESTS = 10000

class PerformanceMetrics:
    """Track API performance metrics."""
    
    def __init__(self):
        self.request_count = 0
        self.total_latency = 0
        self.endpoint_stats = defaultdict(lambda: {"count": 0, "latency": 0})
        self.error_count = 0
        self._lock = threading.Lock()
        
    def record_request(self, endpoint: str, latency: float, success: bool = True):
        """Record request metrics."""
        with self._lock:
            self.request_count += 1
            self.total_latency += latency
            
            self.endpoint_stats[endpoint]["count"] += 1
            self.endpoint_stats[endpoint]["latency"] += latency
            
            if not success:
                self.error_count += 1
                
    def get_stats(self) -> Dict:
        """Get performance statistics."""
        with self._lock:
            avg_latency = self.total_latency / self.request_count if self.request_count > 0 else 0
            error_rate = self.error_count / self.request_count if self.request_count > 0 else 0
            
            endpoint_averages = {}
            for endpoint, stats in self.endpoint_stats.items():
                endpoint_averages[endpoint] = {
                    "count": stats["count"],
                    "avg_latency": stats["latency"] / stats["count"] if stats["count"] > 0 else 0
                }
                
            return {
                "total_requests": self.request_count,
                "average_latency": avg_latency,
                "error_rate": error_rate,
                "endpoint_stats": endpoint_averages
            }

# Global metrics instance
metrics = PerformanceMetrics()

class DatabasePool:
    """High-performance async database connection pool."""
    
    def __init__(self):
        self.pool = None
        
    async def init_pool(self, database_url: str):
        """Initialize connection pool."""
        self.pool = await asyncpg.create_pool(
            database_url,
            min_size=10,
            max_size=DB_POOL_SIZE,
            command_timeout=5,
            server_settings={
                'jit': 'off',  # Disable JIT for predictable performance
                'application_name': 'llmrank_api'
            }
        )
        logger.info(f"Database pool initialized with {DB_POOL_SIZE} connections")
        
    async def execute_query(self, query: str, *args) -> List[Dict]:
        """Execute query with automatic retry."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with self.pool.acquire() as conn:
                    rows = await conn.fetch(query, *args)
                    return [dict(row) for row in rows]
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Database query failed after {max_retries} attempts: {e}")
                    raise
                await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
                
    async def execute_batch(self, query: str, batch_data: List[tuple]) -> None:
        """Execute batch operations efficiently."""
        async with self.pool.acquire() as conn:
            await conn.executemany(query, batch_data)

class RedisCache:
    """High-performance Redis cache with connection pooling."""
    
    def __init__(self):
        self.redis = None
        
    async def init_cache(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis connection pool."""
        try:
            self.redis = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=REDIS_POOL_SIZE,
                socket_timeout=1.0,
                socket_connect_timeout=1.0,
                retry_on_timeout=True
            )
            await self.redis.ping()
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning(f"Redis cache not available: {e}")
            self.redis = None
            
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        if not self.redis:
            return None
            
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
            
    async def set(self, key: str, value: Any, ttl: int = CACHE_TTL) -> None:
        """Set cached value."""
        if not self.redis:
            return
            
        try:
            await self.redis.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            pass  # Fail silently for cache errors
            
    async def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate cache keys matching pattern."""
        if not self.redis:
            return
            
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        except Exception:
            pass

class HighPerformanceAPI:
    """High-performance API engine with optimized FastAPI setup."""
    
    def __init__(self):
        self.db_pool = DatabasePool()
        self.cache = RedisCache()
        self.app = None
        
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Application lifespan management."""
        # Startup
        logger.info("🚀 INITIALIZING HIGH-PERFORMANCE API ENGINE")
        
        # Initialize database pool
        database_url = "postgresql://user:pass@localhost/dbname"  # Will use actual env var
        await self.db_pool.init_pool(database_url)
        
        # Initialize Redis cache
        await self.cache.init_cache()
        
        logger.info("✅ API ENGINE READY FOR HIGH VOLUME")
        
        yield
        
        # Shutdown
        if self.db_pool.pool:
            await self.db_pool.pool.close()
        if self.cache.redis:
            await self.cache.redis.close()
            
    def create_app(self) -> FastAPI:
        """Create optimized FastAPI application."""
        self.app = FastAPI(
            title="LLMPageRank High-Performance API",
            description="Optimized for high-volume, low-latency operations",
            version="2.0.0",
            lifespan=self.lifespan,
            # Performance optimizations
            docs_url="/docs" if True else None,  # Disable in production
            redoc_url=None,  # Disable redoc for performance
        )
        
        # Add performance middleware
        self._add_middleware()
        
        # Add optimized routes
        self._add_routes()
        
        return self.app
        
    def _add_middleware(self):
        """Add performance-optimized middleware."""
        
        # CORS with specific origins for performance
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure specific origins in production
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )
        
        # GZip compression for responses > 1KB
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Performance tracking middleware
        @self.app.middleware("http")
        async def performance_middleware(request: Request, call_next):
            start_time = time.time()
            
            try:
                response = await call_next(request)
                latency = time.time() - start_time
                
                # Record metrics
                endpoint = f"{request.method} {request.url.path}"
                metrics.record_request(endpoint, latency, True)
                
                # Add performance headers
                response.headers["X-Response-Time"] = f"{latency:.3f}s"
                response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")
                
                return response
                
            except Exception as e:
                latency = time.time() - start_time
                endpoint = f"{request.method} {request.url.path}"
                metrics.record_request(endpoint, latency, False)
                raise
                
    def _add_routes(self):
        """Add optimized API routes."""
        
        @self.app.get("/health")
        async def health_check():
            """Ultra-fast health check."""
            return {"status": "healthy", "timestamp": time.time()}
            
        @self.app.get("/metrics")
        async def get_metrics():
            """Get API performance metrics."""
            return metrics.get_stats()
            
        @self.app.get("/api/domains/{domain}/insights")
        async def get_domain_insights(domain: str, limit: int = 100):
            """Get insights for domain with caching."""
            cache_key = f"domain_insights:{domain}:{limit}"
            
            # Try cache first
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return {"data": cached_result, "cached": True}
                
            # Query database
            query = """
                SELECT id, domain, content, quality_score, timestamp, category
                FROM insights 
                WHERE domain = $1 
                ORDER BY timestamp DESC 
                LIMIT $2
            """
            
            insights = await self.db_pool.execute_query(query, domain, limit)
            
            # Cache result
            await self.cache.set(cache_key, insights)
            
            return {"data": insights, "cached": False}
            
        @self.app.get("/api/insights/recent")
        async def get_recent_insights(hours: int = 24, limit: int = 100):
            """Get recent insights across all domains."""
            cache_key = f"recent_insights:{hours}:{limit}"
            
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return {"data": cached_result, "cached": True}
                
            cutoff_time = int(time.time() - (hours * 3600))
            
            query = """
                SELECT id, domain, content, quality_score, timestamp, category, agent_name
                FROM insights 
                WHERE timestamp >= $1 
                ORDER BY quality_score DESC, timestamp DESC 
                LIMIT $2
            """
            
            insights = await self.db_pool.execute_query(query, cutoff_time, limit)
            
            # Cache with shorter TTL for recent data
            await self.cache.set(cache_key, insights, ttl=60)
            
            return {"data": insights, "cached": False}
            
        @self.app.get("/api/insights/top")
        async def get_top_insights(min_quality: float = 0.8, limit: int = 50):
            """Get top quality insights."""
            cache_key = f"top_insights:{min_quality}:{limit}"
            
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return {"data": cached_result, "cached": True}
                
            query = """
                SELECT i.*, e.click_rate, e.retention_time, e.share_rate
                FROM insights i
                LEFT JOIN engagement_metrics e ON i.id = e.insight_id
                WHERE i.quality_score >= $1
                ORDER BY i.quality_score DESC, e.click_rate DESC
                LIMIT $2
            """
            
            insights = await self.db_pool.execute_query(query, min_quality, limit)
            
            await self.cache.set(cache_key, insights)
            
            return {"data": insights, "cached": False}
            
        @self.app.post("/api/insights/batch")
        async def store_insights_batch(insights: List[Dict], background_tasks: BackgroundTasks):
            """Store multiple insights efficiently."""
            
            # Validate insights
            if len(insights) > BATCH_SIZE:
                raise HTTPException(400, f"Batch size cannot exceed {BATCH_SIZE}")
                
            # Prepare batch data
            batch_data = []
            for insight in insights:
                batch_data.append((
                    insight.get("id"),
                    insight.get("domain"),
                    insight.get("content"),
                    insight.get("quality_score", 0.0),
                    insight.get("timestamp", int(time.time())),
                    insight.get("category"),
                    insight.get("agent_name")
                ))
                
            # Execute batch insert
            query = """
                INSERT INTO insights (id, domain, content, quality_score, timestamp, category, agent_name)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (id) DO UPDATE SET
                content = EXCLUDED.content,
                quality_score = EXCLUDED.quality_score,
                timestamp = EXCLUDED.timestamp
            """
            
            await self.db_pool.execute_batch(query, batch_data)
            
            # Invalidate related caches in background
            background_tasks.add_task(self._invalidate_insight_caches, insights)
            
            return {"status": "success", "processed": len(insights)}
            
        @self.app.get("/api/search")
        async def search_insights(
            q: str,
            domain: Optional[str] = None,
            category: Optional[str] = None,
            min_quality: Optional[float] = None,
            limit: int = 50
        ):
            """Advanced search with multiple filters."""
            
            # Build cache key from all parameters
            cache_key = f"search:{q}:{domain}:{category}:{min_quality}:{limit}"
            
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return {"data": cached_result, "cached": True}
                
            # Build dynamic query
            conditions = ["content ILIKE $1"]
            params = [f"%{q}%"]
            param_count = 1
            
            if domain:
                param_count += 1
                conditions.append(f"domain = ${param_count}")
                params.append(domain)
                
            if category:
                param_count += 1
                conditions.append(f"category = ${param_count}")
                params.append(category)
                
            if min_quality:
                param_count += 1
                conditions.append(f"quality_score >= ${param_count}")
                params.append(min_quality)
                
            param_count += 1
            where_clause = " AND ".join(conditions)
            
            query = f"""
                SELECT id, domain, content, quality_score, timestamp, category
                FROM insights 
                WHERE {where_clause}
                ORDER BY quality_score DESC, timestamp DESC
                LIMIT ${param_count}
            """
            
            params.append(limit)
            
            results = await self.db_pool.execute_query(query, *params)
            
            # Cache search results
            await self.cache.set(cache_key, results)
            
            return {"data": results, "cached": False}
            
        @self.app.get("/api/agents/performance")
        async def get_agent_performance():
            """Get agent performance metrics."""
            cache_key = "agent_performance"
            
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return {"data": cached_result, "cached": True}
                
            query = """
                SELECT 
                    agent_name,
                    COUNT(*) as total_insights,
                    AVG(quality_score) as avg_quality,
                    MAX(timestamp) as last_active
                FROM insights 
                WHERE agent_name IS NOT NULL
                GROUP BY agent_name
                ORDER BY avg_quality DESC, total_insights DESC
            """
            
            agents = await self.db_pool.execute_query(query)
            
            await self.cache.set(cache_key, agents, ttl=120)  # 2 minute cache
            
            return {"data": agents, "cached": False}
            
    async def _invalidate_insight_caches(self, insights: List[Dict]):
        """Invalidate caches related to stored insights."""
        domains = {insight.get("domain") for insight in insights if insight.get("domain")}
        
        for domain in domains:
            await self.cache.invalidate_pattern(f"domain_insights:{domain}:*")
            
        # Invalidate global caches
        await self.cache.invalidate_pattern("recent_insights:*")
        await self.cache.invalidate_pattern("top_insights:*")
        await self.cache.invalidate_pattern("agent_performance")

# Global API instance
api_engine = HighPerformanceAPI()

def create_optimized_app() -> FastAPI:
    """Create the optimized FastAPI application."""
    return api_engine.create_app()

# Pydantic models for request validation
class InsightCreate(BaseModel):
    id: Optional[str] = None
    domain: str = Field(..., min_length=1)
    content: str = Field(..., min_length=10)
    quality_score: float = Field(..., ge=0.0, le=1.0)
    category: Optional[str] = None
    agent_name: Optional[str] = None
    timestamp: Optional[int] = None

class InsightBatch(BaseModel):
    insights: List[InsightCreate] = Field(..., max_items=BATCH_SIZE)

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    domain: Optional[str] = None
    category: Optional[str] = None
    min_quality: Optional[float] = Field(None, ge=0.0, le=1.0)
    limit: int = Field(50, ge=1, le=1000)

if __name__ == "__main__":
    # For testing
    import uvicorn
    
    app = create_optimized_app()
    
    # Run with high-performance settings
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        loop="uvloop",
        http="httptools",
        workers=1,  # Single worker for development, scale in production
        access_log=False,  # Disable for performance
        server_header=False,
        date_header=False,
    )