from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class DetectionRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rule_type: str = "single_event"
    event_type: Optional[str] = None
    severity: int = 3
    time_window_seconds: int = 300
    threshold: int = 5
    pattern: Optional[str] = None
    sequence: Optional[str] = None
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None


class DetectionRuleResponse(BaseModel):
    id: int
    rule_id: str
    name: str
    description: Optional[str]
    rule_type: str
    event_type: Optional[str]
    severity: int
    time_window_seconds: int
    threshold: int
    pattern: Optional[str]
    sequence: Optional[str]
    enabled: bool
    mitre_tactic: Optional[str]
    mitre_technique: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DetectionRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    severity: Optional[int] = None
    threshold: Optional[int] = None
    pattern: Optional[str] = None


class CorrelationResult(BaseModel):
    rule_name: str
    severity: int
    description: str
    alert_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    source_ip: Optional[str] = None
    details: Optional[dict] = None


class UserRiskScore(BaseModel):
    username: str
    risk_score: int
    risk_level: str
    alerts_last_hour: int
    alerts_last_24h: int
    top_alert_types: List[str]


class AnomalyResult(BaseModel):
    type: str
    severity: str
    description: str
    details: Optional[dict] = None
