from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import os

# Ensure backend is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.config import get_settings
from backend.database import init_db
from backend.api import logs, alerts, incidents, ai, soar, simulator, reports, stats, playbooks, auth, detection, search, enterprise, enterprise_v2, hec
from backend.websocket.manager import ws_manager
from backend.services.synthetic_attacks import start_generator, stop_generator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Trinetra SIEM...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Start WebSocket manager
    ws_manager.start()
    logger.info("WebSocket manager started")
    
    # Start synthetic attack generator if enabled
    if settings.simulator_enabled:
        try:
            start_generator()
            logger.info("Synthetic attack generator started")
        except Exception as e:
            logger.warning(f"Could not start simulator: {e}")
    
    yield
    
    # Cleanup
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs.router, prefix=settings.api_prefix)
app.include_router(alerts.router, prefix=settings.api_prefix)
app.include_router(incidents.router, prefix=settings.api_prefix)
app.include_router(ai.router, prefix=settings.api_prefix)
app.include_router(soar.router, prefix=settings.api_prefix)
app.include_router(playbooks.router, prefix=settings.api_prefix)
app.include_router(simulator.router, prefix=settings.api_prefix)
app.include_router(reports.router, prefix=settings.api_prefix)
app.include_router(stats.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(detection.router, prefix=settings.api_prefix)
app.include_router(search.router, prefix=settings.api_prefix)
app.include_router(enterprise.router, prefix=settings.api_prefix)
app.include_router(enterprise_v2.router, prefix=settings.api_prefix)
app.include_router(hec.router, prefix=settings.api_prefix)
app.add_api_websocket_route(settings.ws_endpoint, ws_manager.websocket_endpoint)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "trinetra-siem"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)