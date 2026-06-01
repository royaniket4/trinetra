import logging
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List

from backend.database import get_db
from backend.schemas.alert import (
    AlertResponse,
    AlertListResponse,
    AlertUpdateRequest,
    AlertStatsResponse,
)
from backend.models.alert import Alert

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=AlertListResponse)
async def get_alerts(
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    severity: Optional[int] = Query(default=None, ge=1, le=5),
    status: Optional[str] = None,
    source_ip: Optional[str] = None,
    mitre_tactic: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Get alerts with filters."""
    query = db.query(Alert)
    
    if severity is not None:
        query = query.filter(Alert.severity >= severity)
    if status:
        query = query.filter(Alert.status == status)
    if source_ip:
        query = query.filter(Alert.source_ip == source_ip)
    if mitre_tactic:
        query = query.filter(Alert.mitre_tactic == mitre_tactic)
    if from_date:
        query = query.filter(Alert.timestamp >= from_date)
    if to_date:
        query = query.filter(Alert.timestamp <= to_date)
    
    total = query.count()
    alerts = query.order_by(desc(Alert.timestamp)).offset(offset).limit(limit).all()
    
    return AlertListResponse(total=total, alerts=alerts)


@router.get("/stats/summary", response_model=AlertStatsResponse)
async def get_alert_stats(db: Session = Depends(get_db)):
    """Get alert statistics summary."""
    total = db.query(Alert).count()
    
    severity_counts = db.query(
        Alert.severity,
        func.count(Alert.id)
    ).group_by(Alert.severity).all()
    by_severity = {f"severity_{s}": c for s, c in severity_counts}
    
    status_counts = db.query(
        Alert.status,
        func.count(Alert.id)
    ).group_by(Alert.status).all()
    by_status = {s: c for s, c in status_counts}
    
    top_ips = db.query(
        Alert.source_ip,
        func.count(Alert.id).label('count')
    ).filter(
        Alert.source_ip.isnot(None)
    ).group_by(
        Alert.source_ip
    ).order_by(
        desc('count')
    ).limit(10).all()
    top_source_ips = [{'ip': ip, 'count': c} for ip, c in top_ips]
    
    top_techniques = db.query(
        Alert.mitre_technique,
        func.count(Alert.id).label('count')
    ).filter(
        Alert.mitre_technique.isnot(None)
    ).group_by(
        Alert.mitre_technique
    ).order_by(
        desc('count')
    ).limit(10).all()
    top_mitre_techniques = [{'technique': t, 'count': c} for t, c in top_techniques]
    
    now = datetime.utcnow()
    alerts_per_hour = []
    for i in range(24):
        hour_start = now - timedelta(hours=i+1)
        hour_end = now - timedelta(hours=i)
        count = db.query(Alert).filter(
            Alert.timestamp >= hour_start,
            Alert.timestamp < hour_end
        ).count()
        alerts_per_hour.append({'hour': i, 'count': count})
    alerts_per_hour.reverse()
    
    return AlertStatsResponse(
        total=total,
        by_severity=by_severity,
        by_status=by_status,
        top_source_ips=top_source_ips,
        top_mitre_techniques=top_mitre_techniques,
        alerts_per_hour=alerts_per_hour,
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/{alert_id}")
async def update_alert(
    alert_id: int,
    data: AlertUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update an alert's status or assignee."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if data.status:
        alert.status = data.status.value if hasattr(data.status, 'value') else data.status
    if data.assignee:
        alert.assignee = data.assignee
    
    db.commit()
    db.refresh(alert)
    
    logger.info(f"Alert updated: {alert.alert_id} - status: {alert.status}")
    
    return alert


@router.delete("/{alert_id}")
async def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Soft delete an alert (set status to closed)."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = "closed"
    db.commit()
    
    logger.info(f"Alert deleted (closed): {alert.alert_id}")
    
    return {"status": "deleted", "alert_id": alert.alert_id}