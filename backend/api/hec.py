"""HTTP Event Collector - Splunk HEC-compatible log ingestion endpoint."""

import json
import logging
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.log import Log
from backend.services.detection_engine import DetectionEngine
from backend.websocket.manager import broadcast_log

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hec", tags=["HEC"])


@router.post("/event")
async def hec_event(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Splunk HEC-compatible single event ingestion.
    
    POST /api/hec/event
    Body: {"event": "...", "host": "...", "sourcetype": "...", "source": "...", "fields": {...}}
    """
    body = await request.json()
    return await _process_hec_payload(body, db)


@router.post("/raw")
async def hec_raw(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Splunk HEC-compatible raw event ingestion.
    
    POST /api/hec/raw
    Body: raw text string
    """
    raw_text = await request.body()
    body = {"event": raw_text.decode('utf-8', errors='replace')}
    return await _process_hec_payload(body, db)


async def _process_hec_payload(body: dict, db: Session) -> dict:
    """Process a HEC payload and create log entries."""
    raw_event = body.get("event")
    if not raw_event:
        raise HTTPException(status_code=400, detail="Missing 'event' field")
    
    host = body.get("host", "hec-client")
    sourcetype = body.get("sourcetype", "hec:generic")
    source = body.get("source", "hec")
    fields = body.get("fields", {})
    time = body.get("time", datetime.utcnow().timestamp())
    
    if isinstance(raw_event, dict):
        raw_text = json.dumps(raw_event)
    else:
        raw_text = str(raw_event)
    
    source_ip = fields.get("source_ip") or _extract_ip(raw_text)
    dest_ip = fields.get("dest_ip")
    username = fields.get("username")
    event_type = fields.get("event_type") or _detect_event_type(raw_text)
    
    log_entry = Log(
        timestamp=datetime.fromtimestamp(time) if isinstance(time, (int, float)) else datetime.utcnow(),
        source_ip=source_ip,
        dest_ip=dest_ip,
        username=username,
        event_type=event_type,
        sourcetype=sourcetype,
        host=host,
        raw_log=raw_text[:5000],
        log_source=f"hec/{sourcetype}",
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    try:
        await broadcast_log(log_entry)
    except Exception:
        pass
    
    engine = DetectionEngine(db)
    alerts = engine.analyze_log(log_entry)
    
    return {
        "acknowledged": True,
        "log_id": log_entry.id,
        "alerts_generated": len(alerts),
    }


def _extract_ip(text: str) -> Optional[str]:
    import re
    match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
    return match.group(0) if match else None


def _detect_event_type(text: str) -> str:
    t = text.lower()
    if 'failed' in t or 'login failed' in t:
        return 'LOGIN_FAILED'
    if 'success' in t or 'login success' in t:
        return 'LOGIN_SUCCESS'
    if 'powershell' in t or 'encodedcommand' in t:
        return 'POWERSHELL'
    if 'download' in t or '.exe' in t or '.scr' in t:
        return 'FILE_DOWNLOAD'
    if 'sql' in t or 'select' in t or 'union' in t:
        return 'SQL_INJECTION'
    if 'port' in t or 'scan' in t or 'nmap' in t:
        return 'PORT_SCAN'
    return 'GENERIC'
