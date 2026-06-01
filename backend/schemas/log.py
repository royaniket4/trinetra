from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List
from backend.schemas.common import LogFormat, EventType


class LogIngestRequest(BaseModel):
    """Request model for log ingestion."""
    timestamp: Optional[datetime] = None
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    username: Optional[str] = None
    event_type: str = Field(..., description="Event type from EventType enum")
    severity: int = Field(default=1, ge=1, le=5)
    raw_log: str = Field(..., description="Raw log message")
    log_format: Optional[LogFormat] = Field(
        default=None,
        description="Log format type: windows|linux|apache|nginx|firewall|json|custom"
    )
    metadata: Optional[Dict] = Field(
        default=None,
        description="Additional metadata (e.g., bytes_out for exfiltration detection)"
    )
    geo_country: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lon: Optional[float] = None


class BulkLogIngestRequest(BaseModel):
    """Request model for bulk log ingestion."""
    logs: List[LogIngestRequest] = Field(..., min_length=1, max_length=500)


class LogResponse(BaseModel):
    """Response model for log data."""
    id: int
    timestamp: datetime
    source_ip: Optional[str]
    dest_ip: Optional[str]
    username: Optional[str]
    event_type: str
    severity: int
    raw_log: str
    geo_country: Optional[str]
    geo_lat: Optional[float]
    geo_lon: Optional[float]
    log_source: str

    class Config:
        from_attributes = True


class IngestResult(BaseModel):
    """Result of log ingestion."""
    logs_received: int
    logs_stored: int
    alerts_generated: int
    alert_ids: List[str] = []