from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ResponseActionResponse(BaseModel):
    id: int
    action_id: str
    action_type: str
    target: str
    triggered_by: str
    trigger_source: Optional[str]
    status: str
    details: Optional[str]
    executed_at: datetime

    class Config:
        from_attributes = True


class ResponseActionCreate(BaseModel):
    action_type: str
    target: str
    triggered_by: str = "manual"
    trigger_source: Optional[str] = None
    details: Optional[str] = None


class ResponseActionExecute(BaseModel):
    action_type: str
    target: str
    trigger_source: Optional[str] = "ai_suggested"
    details: Optional[str] = None