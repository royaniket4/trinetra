"""SOAR Playbook API routes - Trigger playbooks, approve/deny steps, view history."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.playbooks.registry import list_playbooks, get_playbook
from backend.playbooks.engine import PlaybookEngine
from backend.schemas.playbook import (
    PlaybookTriggerRequest,
    PlaybookExecutionResponse,
    ApproveStepRequest,
    PendingApprovalResponse,
    PlaybookExecutionHistory,
)
from backend.models.playbook import PlaybookExecution, PlaybookExecutionStep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/soar", tags=["SOAR"])


@router.get("/playbooks")
async def get_playbooks():
    """List all available playbooks."""
    return list_playbooks()


@router.get("/playbooks/executions", response_model=list[PlaybookExecutionHistory])
async def get_executions(limit: int = 20, db: Session = Depends(get_db)):
    """Get playbook execution history."""
    executions = (
        db.query(PlaybookExecution)
        .order_by(desc(PlaybookExecution.started_at))
        .limit(limit)
        .all()
    )
    return executions


@router.get("/playbooks/executions/{execution_id}")
async def get_execution_detail(execution_id: str, db: Session = Depends(get_db)):
    """Get detailed execution info including steps."""
    execution = (
        db.query(PlaybookExecution)
        .filter(PlaybookExecution.execution_id == execution_id)
        .first()
    )
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    steps = (
        db.query(PlaybookExecutionStep)
        .filter(PlaybookExecutionStep.execution_id == execution.id)
        .order_by(PlaybookExecutionStep.order)
        .all()
    )

    return {
        "execution": {
            "execution_id": execution.execution_id,
            "playbook_id": execution.playbook_id,
            "playbook_name": execution.playbook_name,
            "status": execution.status,
            "triggered_by": execution.triggered_by,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
        },
        "steps": [
            {
                "id": s.id,
                "order": s.order,
                "action_type": s.action_type,
                "target": s.target,
                "label": s.label,
                "status": s.status,
                "requires_approval": s.requires_approval,
                "approved_by": s.approved_by,
                "error_message": s.error_message,
                "completed_at": s.completed_at,
            }
            for s in steps
        ],
    }


@router.post("/playbooks/trigger", response_model=PlaybookExecutionResponse)
async def trigger_playbook(request: PlaybookTriggerRequest, db: Session = Depends(get_db)):
    """Trigger matching playbooks for an alert."""
    engine = PlaybookEngine(db)
    results = engine.find_and_trigger(request.alert_id)

    if not results:
        raise HTTPException(status_code=404, detail="No matching playbooks found for this alert")

    return results[0]


@router.get("/playbooks/{playbook_id}")
async def get_playbook_by_id(playbook_id: str):
    """Get a single playbook definition."""
    pb = get_playbook(playbook_id)
    if not pb:
        raise HTTPException(status_code=404, detail="Playbook not found")
    return pb


@router.get("/approvals/pending", response_model=list[PendingApprovalResponse])
async def get_pending_approvals(db: Session = Depends(get_db)):
    """Get all steps awaiting approval."""
    steps = (
        db.query(PlaybookExecutionStep)
        .filter(PlaybookExecutionStep.status == "pending")
        .filter(PlaybookExecutionStep.requires_approval == True)
        .order_by(PlaybookExecutionStep.started_at)
        .all()
    )

    result = []
    for step in steps:
        execution = (
            db.query(PlaybookExecution)
            .filter(PlaybookExecution.id == step.execution_id)
            .first()
        )
        result.append(
            PendingApprovalResponse(
                id=step.id,
                execution_id=step.execution_id,
                playbook_name=execution.playbook_name if execution else None,
                order=step.order,
                action_type=step.action_type,
                target=step.target,
                label=step.label,
                status=step.status,
                started_at=step.started_at,
            )
        )

    return result


@router.post("/approvals/respond")
async def respond_approval(request: ApproveStepRequest, db: Session = Depends(get_db)):
    """Approve or deny a pending step."""
    engine = PlaybookEngine(db)

    if request.approved:
        result = engine.approve_step(request.step_id)
    else:
        result = engine.deny_step(request.step_id)

    return result
