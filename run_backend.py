#!/usr/bin/env python
"""Run Trinetra backend server."""
import sys
import os

# Add the trinetra directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now imports can use 'backend.' prefix
from backend.config import get_settings, validate_security_settings
from backend.database import init_db
from backend.api import logs, alerts, incidents, ai, soar, simulator, stats, reports, playbooks, detection, auth, search, enterprise, enterprise_v2, hec
from backend.websocket.manager import ws_manager
from backend.services.synthetic_attacks import start_generator, stop_generator

# New imports for enhanced features
from backend.middleware.rate_limiter import RateLimitMiddleware
from backend.middleware.security_headers import SecurityHeadersMiddleware
from backend.services.logging_service import setup_logging, audit_logger
from backend.services.cache import cache

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()

# Validate security settings on startup
validate_security_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Trinetra SIEM...")
    logger.info(f"Version: {settings.app_version}")
    
    init_db()
    logger.info("Database initialized")
    ws_manager.start()
    logger.info("WebSocket manager started")
    
    if settings.simulator_enabled:
        try:
            start_generator()
            logger.info("Synthetic attack generator started")
        except Exception as e:
            logger.warning(f"Could not start simulator: {e}")
    
    # Log startup
    logger.info(f"Rate limiting enabled: {settings.rate_limit_enabled}")
    logger.info(f"Redis cache enabled: {cache.enabled}")
    
    yield
    
    try:
        stop_generator()
        logger.info("Synthetic attack generator stopped")
    except Exception as e:
        logger.warning(f"Error stopping simulator: {e}")
    
    ws_manager.stop()
    logger.info("Trinetra SIEM shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Cyber Defense Command Center",
    lifespan=lifespan,
)

# Add security middleware first
if settings.security_headers_enabled:
    app.add_middleware(SecurityHeadersMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
if settings.rate_limit_enabled:
    app.add_middleware(RateLimitMiddleware)


# Middleware for audit logging
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Log API access
    if request.url.path.startswith("/api"):
        # Skip sensitive paths
        if "/api/auth/login" not in request.url.path:
            audit_logger.log_api_access(
                user_id="unknown",  # Can be extracted from token if available
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code
            )
    
    return response


# Include all routers
app.include_router(logs.router, prefix=settings.api_prefix)
app.include_router(alerts.router, prefix=settings.api_prefix)
app.include_router(incidents.router, prefix=settings.api_prefix)
app.include_router(ai.router, prefix=settings.api_prefix)
app.include_router(soar.router, prefix=settings.api_prefix)
app.include_router(simulator.router, prefix=settings.api_prefix)
app.include_router(stats.router, prefix=settings.api_prefix)
app.include_router(reports.router, prefix=settings.api_prefix)
app.include_router(playbooks.router, prefix=settings.api_prefix)
app.include_router(detection.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(search.router, prefix=settings.api_prefix)
app.include_router(enterprise.router, prefix=settings.api_prefix)
app.include_router(enterprise_v2.router, prefix=settings.api_prefix)
app.include_router(hec.router, prefix=settings.api_prefix)

# Add WebSocket endpoint
app.add_api_websocket_route(settings.ws_endpoint, ws_manager.websocket_endpoint)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "features": {
            "rate_limiting": settings.rate_limit_enabled,
            "redis_cache": cache.enabled,
            "security_headers": settings.security_headers_enabled
        }
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "service": "trinetra-siem",
        "version": settings.app_version
    }


if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=False  # Set to True for development
    )