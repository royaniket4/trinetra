from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class IncidentResponse(BaseModel):
    id: int
    incident_id: str
    title: str
    description: Optional[str]
    severity: int
    status: str
    assigned_to: Optional[str]
    alert_count: int
    first_activity: datetime
    last_activity: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: int
    alert_ids: list[int] = []


class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None