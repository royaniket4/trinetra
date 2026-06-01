import logging
from fastapi import APIRouter, Query
from typing import Optional

from backend.services.stats_aggregator import get_stats_aggregator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/dashboard")
async def get_dashboard_stats(force_refresh: bool = False):
    """Get full dashboard statistics."""
    try:
        aggregator = get_stats_aggregator()
        return aggregator.get_dashboard_stats(force_refresh)
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return {}


@router.get("/attack-paths")
async def get_attack_paths(limit: int = Query(default=30, le=100)):
    """Get attack paths for map visualization."""
    try:
        aggregator = get_stats_aggregator()
        return aggregator.get_attack_paths(limit)
    except Exception as e:
        logger.error(f"Error getting attack paths: {e}")
        return []


@router.get("/kill-chain")
async def get_kill_chain():
    """Get kill chain stage counts."""
    try:
        aggregator = get_stats_aggregator()
        return aggregator.get_kill_chain()
    except Exception as e:
        logger.error(f"Error getting kill chain: {e}")
        return {}


@router.get("/timeline")
async def get_timeline(hours: int = Query(default=24, le=168)):
    """Get alerts grouped by hour."""
    try:
        aggregator = get_stats_aggregator()
        return aggregator.get_timeline(hours)
    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        return []