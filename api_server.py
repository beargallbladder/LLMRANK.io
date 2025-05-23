"""
LLMPageRank V9 API Server

This module implements the FastAPI server for the LLMPageRank V9 API
with optimizations for increased partner traffic.
"""

import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Import API routers
from api.v1.router import router as api_v1_router
from mcp_api import router as mcp_router
from mcp_key_request import router as key_request_router
from mcp_priority_trigger import router as priority_trigger_router
from admin_console_routes import router as admin_console_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database connection pool on startup
try:
    from database_pool import initialize_connection_pool
    logger.info("Initializing database connection pool")
    connection_pool = initialize_connection_pool()
    if connection_pool:
        logger.info("Database connection pool initialized successfully")
    else:
        logger.warning("Failed to initialize database connection pool")
except ImportError:
    logger.warning("Database connection pooling not available")

# Initialize API cache
try:
    from api_cache import get_cache
    logger.info("Initializing API cache")
    cache = get_cache()
    logger.info("API cache initialized successfully")
except ImportError:
    logger.warning("API cache not available")

# Create FastAPI app
app = FastAPI(
    title="LLMRank.io API",
    description="API for LLMRank.io trust signal data",
    version="1.0",
    docs_url="/api-docs",  # Custom Swagger UI URL at root
    redoc_url="/api-reference"  # Custom ReDoc URL
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(f"Request {request.method} {request.url.path} processed in {process_time:.4f} seconds")
        
        return response

app.add_middleware(LoggingMiddleware)

# Add rate limit headers middleware if available
try:
    from mcp_rate_limit_middleware import RateLimitHeaderMiddleware
    logger.info("Adding rate limit header middleware")
    app.add_middleware(RateLimitHeaderMiddleware)
except ImportError:
    logger.warning("Rate limit header middleware not available")

# Add crawler protection middleware if available
try:
    from mcp_crawler_protection import CrawlerProtectionMiddleware
    logger.info("Adding crawler protection middleware")
    app.add_middleware(CrawlerProtectionMiddleware)
except ImportError:
    logger.warning("Crawler protection middleware not available")

# Include routers
app.include_router(api_v1_router, prefix="/api")
app.include_router(mcp_router)
app.include_router(key_request_router)
app.include_router(priority_trigger_router)
app.include_router(admin_console_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to LLMRank.io API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Run API server
def run_api_server():
    """Run the API server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050, log_level="info", access_log=True, use_colors=True)

if __name__ == "__main__":
    run_api_server()