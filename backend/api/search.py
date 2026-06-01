"""Search API - Splunk-like log explorer with field syntax."""

import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.log_search import LogSearchEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/logs")
async def search_logs(
    query: str = Query("*", description="Search query (field:value syntax)"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    earliest: str = Query("-24h", description="Earliest time: -24h, -7d, -30m"),
    db: Session = Depends(get_db),
):
    """Search logs with Splunk-like syntax."""
    engine = LogSearchEngine(db)
    result = engine.search(query)
    return result


@router.get("/fields/{field_name}")
async def get_field_values(
    field_name: str,
    search: str = Query(None),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    """Get distinct values for autocomplete."""
    engine = LogSearchEngine(db)
    values = engine.get_field_values(field_name, search, limit)
    return {"field": field_name, "values": values, "count": len(values)}
