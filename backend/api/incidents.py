from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime

from backend.database import get_db
from backend.schemas.incident import (
    IncidentResponse,
    IncidentCreate,
    IncidentUpdate,
)
from backend.models.incident import Incident
from backend.models.alert import Alert

router = APIRouter(prefix="/incidents", tags=["Incidents"])


def generate_incident_id() -> str:
    import uuid
    return f"INC-{uuid.uuid4().hex[:8].upper()}"


@router.get("", response_model=list[IncidentResponse])
async def get_incidents(
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    severity: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get incidents with filters."""
    query = db.query(Incident)
    
    if severity:
        query = query.filter(Incident.severity >= severity)
    if status:
        query = query.filter(Incident.status == status)
    
    incidents = query.order_by(desc(Incident.created_at)).offset(offset).limit(limit).all()
    return incidents


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Get a specific incident with its alerts."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("")
async def create_incident(data: IncidentCreate, db: Session = Depends(get_db)):
    """Create a new incident."""
    incident = Incident(
        incident_id=generate_incident_id(),
        title=data.title,
        description=data.description,
        severity=data.severity,
        status="open",
        alert_count=len(data.alert_ids),
        first_activity=datetime.utcnow(),
        last_activity=datetime.utcnow(),
    )
    
    if data.alert_ids:
        alerts = db.query(Alert).filter(Alert.id.in_(data.alert_ids)).all()
        for alert in alerts:
            alert.incident_id = incident.id
            alert.status = "investigating"
    
    db.add(incident)
    db.flush() # Get the auto-incremented ID
    
    if data.alert_ids:
        alerts = db.query(Alert).filter(Alert.id.in_(data.alert_ids)).all()
        for alert in alerts:
            alert.incident_id = incident.id
            alert.status = "investigating"
    
    db.commit()
    db.refresh(incident)
    
    return incident


@router.patch("/{incident_id}")
async def update_incident(
    incident_id: int,
    data: IncidentUpdate,
    db: Session = Depends(get_db),
):
    """Update an incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if data.status:
        incident.status = data.status
        if data.status == "closed":
            incident.closed_at = datetime.utcnow()
    if data.assigned_to:
        incident.assigned_to = data.assigned_to
    
    incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    
    return incident


@router.get("/{incident_id}/alerts")
async def get_incident_alerts(incident_id: int, db: Session = Depends(get_db)):
    """Get all alerts associated with an incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    alerts = db.query(Alert).filter(Alert.incident_id == incident_id).all()
    return alerts