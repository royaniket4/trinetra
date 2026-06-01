from pydantic import BaseModel, Field
from typing import List, Optional


class AlertExplainRequest(BaseModel):
    alert_id: int = Field(..., description="ID of the alert to explain")


class PlaybookRequest(BaseModel):
    alert_id: int = Field(..., description="ID of the alert to generate playbook for")


class NarrativeRequest(BaseModel):
    alert_ids: List[int] = Field(..., description="List of alert IDs to build narrative from")


class ThreatHuntRequest(BaseModel):
    query: str = Field(..., description="Natural language threat hunting query")


class IncidentReportRequest(BaseModel):
    incident_id: int = Field(..., description="ID of the incident to generate report for")


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Conversation session ID")
    message: str = Field(..., description="User message")


class AIHealthResponse(BaseModel):
    provider: str
    model: str
    status: str
    latency_ms: Optional[int] = None
    available_models: Optional[List[str]] = None


class ThreatHuntFilters(BaseModel):
    event_type: Optional[List[str]] = None
    geo_country: Optional[List[str]] = None
    severity_min: Optional[int] = 1
    time_window_hours: Optional[int] = 24
    source_ip_pattern: Optional[str] = None
    username_pattern: Optional[str] = None
    mitre_technique: Optional[str] = None


class ThreatHuntResponse(BaseModel):
    filters: ThreatHuntFilters
    explanation: str
    estimated_result_size: str
    results: List[dict] = []
    count: int = 0


class WorkflowInfo(BaseModel):
    id: str
    name: str
    description: str
    requires_input: str


class WorkflowListResponse(BaseModel):
    workflows: List[WorkflowInfo]