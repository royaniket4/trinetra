import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from backend.database import get_db
from backend.schemas.log import (
    LogIngestRequest,
    BulkLogIngestRequest,
    LogResponse,
    IngestResult,
)
from backend.models.log import Log
from backend.services.log_normalizer import LogNormalizer
from backend.services.detection_engine import DetectionEngine
from backend.websocket.manager import broadcast_log, broadcast_alert

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("/ingest", response_model=LogResponse)
async def ingest_log(log_data: LogIngestRequest, db: Session = Depends(get_db)):
    """Ingest and normalize a single log entry."""
    normalizer = LogNormalizer()
    normalized = normalizer.normalize(log_data)
    
    log = Log(**normalized)
    db.add(log)
    db.commit()
    db.refresh(log)
    
    logger.info(f"Log ingested: ID={log.id}, type={log.event_type}")
    
    detection_engine = DetectionEngine(db)
    alerts = detection_engine.analyze_log(log)
    logger.info(f"Detection complete: {len(alerts)} alerts generated")
    
    for alert in alerts:
        await broadcast_alert({
            'id': alert.id,
            'alert_id': alert.alert_id,
            'rule_name': alert.rule_name,
            'severity': alert.severity,
            'timestamp': alert.timestamp.isoformat(),
            'source_ip': alert.source_ip,
            'status': alert.status,
        })
    
    await broadcast_log({
        'id': log.id,
        'timestamp': log.timestamp.isoformat(),
        'source_ip': log.source_ip,
        'event_type': log.event_type,
        'severity': log.severity,
    })
    
    return log


@router.post("/ingest/bulk", response_model=IngestResult)
async def ingest_bulk_logs(bulk_data: BulkLogIngestRequest, db: Session = Depends(get_db)):
    """Ingest multiple log entries in bulk."""
    normalizer = LogNormalizer()
    detection_engine = DetectionEngine(db)
    
    logs_stored = 0
    alert_ids: List[str] = []
    
    for log_data in bulk_data.logs:
        try:
            normalized = normalizer.normalize(log_data)
            log = Log(**normalized)
            db.add(log)
            db.flush()
            
            logs_stored += 1
            
            alerts = detection_engine.analyze_log(log)
            for alert in alerts:
                alert_ids.append(alert.alert_id)
            
        except Exception as e:
            logger.error(f"Failed to process log: {e}")
            db.rollback()
            continue
    
    db.commit()
    
    logger.info(f"Bulk ingest complete: {logs_stored} logs, {len(alert_ids)} alerts")
    
    return IngestResult(
        logs_received=len(bulk_data.logs),
        logs_stored=logs_stored,
        alerts_generated=len(alert_ids),
        alert_ids=alert_ids,
    )


@router.get("", response_model=List[LogResponse])
async def get_logs(
    limit: int = 50,
    offset: int = 0,
    severity: Optional[int] = None,
    source_ip: Optional[str] = None,
    event_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Get log entries with filters."""
    query = db.query(Log)
    
    if severity is not None:
        query = query.filter(Log.severity >= severity)
    if source_ip:
        query = query.filter(Log.source_ip == source_ip)
    if event_type:
        query = query.filter(Log.event_type == event_type)
    if start_time:
        query = query.filter(Log.timestamp >= start_time)
    if end_time:
        query = query.filter(Log.timestamp <= end_time)
    
    logs = query.order_by(Log.timestamp.desc()).offset(offset).limit(min(limit, 500)).all()
    return logs


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(log_id: int, db: Session = Depends(get_db)):
    """Get a specific log entry."""
    log = db.query(Log).filter(Log.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log