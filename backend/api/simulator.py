import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services.synthetic_attacks import get_synthetic_generator, start_generator, stop_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simulator", tags=["Simulator"])


class SimulatorConfig(BaseModel):
    interval_min: Optional[int] = None
    interval_max: Optional[int] = None


class BurstRequest(BaseModel):
    count: int = 20


@router.get("/status")
async def get_status():
    """Get synthetic attack simulator status."""
    generator = get_synthetic_generator()
    return generator.get_status()


@router.post("/start")
async def start():
    """Start synthetic attack generator."""
    try:
        start_generator()
        return {"status": "running", "message": "Synthetic attack generator started"}
    except Exception as e:
        logger.error(f"Error starting simulator: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop():
    """Stop synthetic attack generator."""
    try:
        stop_generator()
        return {"status": "stopped", "message": "Synthetic attack generator stopped"}
    except Exception as e:
        logger.error(f"Error stopping simulator: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/toggle")
async def toggle():
    """Toggle synthetic attack generator on/off."""
    generator = get_synthetic_generator()
    
    if generator.is_running:
        stop_generator()
        return {"status": "stopped", "message": "Synthetic attack generator stopped"}
    else:
        start_generator()
        return {"status": "running", "message": "Synthetic attack generator started"}


@router.post("/burst")
async def trigger_burst(request: BurstRequest):
    """Trigger an attack wave (burst of attacks)."""
    try:
        generator = get_synthetic_generator()
        count = generator.generate_burst(request.count)
        return {
            "status": "success", 
            "message": f"Generated {count} attacks",
            "count": count
        }
    except Exception as e:
        logger.error(f"Error generating burst: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def update_config(config: SimulatorConfig):
    """Update simulator configuration."""
    try:
        generator = get_synthetic_generator()
        generator.update_config(config.interval_min, config.interval_max)
        return {
            "status": "success",
            "message": "Configuration updated",
            "interval_min": generator.interval_min,
            "interval_max": generator.interval_max,
        }
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))