from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PlaybookStep(BaseModel):
    order: int
    action_type: str
    target_from: Optional[str] = None
    target: Optional[str] = None
    label: str
    description: Optional[str] = None
    requires_approval: bool = False


class PlaybookDefinition(BaseModel):
    id: str
    name: str
    description: str
    trigger_conditions: dict
    steps: List[PlaybookStep]


class PlaybookStepResult(BaseModel):
    step: PlaybookStep
    target: Optional[str] = None
    status: str
    action_id: Optional[str] = None
    error: Optional[str] = None
    reason: Optional[str] = None
    step_record_id: Optional[int] = None


class PlaybookExecutionResponse(BaseModel):
    execution_id: str
    playbook_id: str
    playbook_name: str
    status: str
    steps: List[PlaybookStepResult]


class PlaybookTriggerRequest(BaseModel):
    alert_id: int


class ApproveStepRequest(BaseModel):
    step_id: int
    approved: bool


class PendingApprovalResponse(BaseModel):
    id: int
    execution_id: int
    playbook_name: Optional[str] = None
    order: int
    action_type: str
    target: str
    label: str
    status: str
    started_at: datetime

    class Config:
        from_attributes = True


class PlaybookExecutionHistory(BaseModel):
    execution_id: str
    playbook_id: str
    playbook_name: str
    status: str
    triggered_by: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
