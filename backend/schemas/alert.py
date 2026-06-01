from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from backend.schemas.common import AlertStatus


class AlertResponse(BaseModel):
    """Response model for alert data."""
    id: int
    alert_id: str
    rule_name: str
    severity: int
    mitre_tactic: Optional[str] = None
    mitre_tactic_name: Optional[str] = None
    mitre_technique: Optional[str] = None
    mitre_technique_name: Optional[str] = None
    confidence: float
    asset_impact: Optional[str]
    evidence: str
    evidence_parsed: Optional[Dict[str, Any]] = None
    timestamp: datetime
    source_ip: Optional[str]
    dest_ip: Optional[str]
    username: Optional[str]
    status: str
    acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    assignee: Optional[str] = None
    incident_id: Optional[int] = None

    class Config:
        from_attributes = True


class AlertUpdateRequest(BaseModel):
    """Request model for updating an alert."""
    status: Optional[AlertStatus] = None
    assignee: Optional[str] = None


class AlertListResponse(BaseModel):
    """Response model for alert list."""
    total: int
    alerts: list[AlertResponse]


class AlertStatsResponse(BaseModel):
    """Response model for alert statistics."""
    total: int
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    top_source_ips: list[Dict[str, Any]]
    top_mitre_techniques: list[Dict[str, Any]]
    alerts_per_hour: list[Dict[str, int]]