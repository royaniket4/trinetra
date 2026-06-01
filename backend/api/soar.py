from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.schemas.response_action import (
    ResponseActionResponse,
    ResponseActionExecute,
)
from backend.models.response_action import ResponseAction
from backend.models.asset import Asset

router = APIRouter(prefix="/soar", tags=["SOAR"])


def generate_action_id() -> str:
    import uuid
    return f"ACT-{uuid.uuid4().hex[:8].upper()}"


@router.get("/actions", response_model=list[ResponseActionResponse])
async def get_actions(
    limit: int = 50,
    action_type: str = None,
    status: str = None,
    db: Session = Depends(get_db),
):
    """Get response actions with filters."""
    query = db.query(ResponseAction)
    
    if action_type:
        query = query.filter(ResponseAction.action_type == action_type)
    if status:
        query = query.filter(ResponseAction.status == status)
    
    actions = query.order_by(desc(ResponseAction.executed_at)).limit(limit).all()
    return actions


@router.post("/actions")
async def execute_action(data: ResponseActionExecute, db: Session = Depends(get_db)):
    """Execute a response action."""
    action = ResponseAction(
        action_id=generate_action_id(),
        action_type=data.action_type,
        target=data.target,
        triggered_by="manual" if not data.trigger_source else data.trigger_source,
        trigger_source=data.trigger_source,
        status="completed",
        details=data.details,
    )
    
    if data.action_type == "block_ip":
        action.details = f"Blocked IP address: {data.target}"
    elif data.action_type == "disable_user":
        action.details = f"Disabled user account: {data.target}"
    elif data.action_type == "quarantine_file":
        action.details = f"Quarantined file: {data.target}"
    elif data.action_type == "isolate_endpoint":
        action.details = f"Isolated endpoint: {data.target}"
    
    db.add(action)
    db.commit()
    db.refresh(action)
    
    return action


@router.get("/blocked-ips")
async def get_blocked_ips(db: Session = Depends(get_db)):
    """Get all blocked IP addresses."""
    actions = (
        db.query(ResponseAction)
        .filter(ResponseAction.action_type == "block_ip")
        .filter(ResponseAction.status == "completed")
        .order_by(desc(ResponseAction.executed_at))
        .all()
    )
    return [{"ip": a.target, "blocked_at": a.executed_at} for a in actions]


@router.get("/disabled-users")
async def get_disabled_users(db: Session = Depends(get_db)):
    """Get all disabled user accounts."""
    actions = (
        db.query(ResponseAction)
        .filter(ResponseAction.action_type == "disable_user")
        .filter(ResponseAction.status == "completed")
        .order_by(desc(ResponseAction.executed_at))
        .all()
    )
    return [{"username": a.target, "disabled_at": a.executed_at} for a in actions]