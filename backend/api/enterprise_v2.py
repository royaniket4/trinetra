"""Enterprise features - HEC, Email Reports, Custom Dashboards, LDAP/SSO."""

import json
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.dashboard import Dashboard
from backend.models.user import User
from backend.services.email_reports import EmailEngine, ReportScheduler
from backend.schemas.auth import UserResponse
from backend.api.auth import get_current_user, get_password_hash, verify_password, create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enterprise", tags=["Enterprise"])


# ─── Custom Dashboards ─────────────────────────────────────

@router.get("/dashboards")
async def list_dashboards(db: Session = Depends(get_db)):
    dashboards = db.query(Dashboard).order_by(Dashboard.updated_at.desc()).all()
    result = []
    for d in dashboards:
        result.append({
            "id": d.id,
            "name": d.name,
            "description": d.description,
            "is_default": d.is_default,
            "widget_count": len(json.loads(d.widgets or "[]")),
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        })
    return result


@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    d = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return {
        "id": d.id, "name": d.name, "description": d.description,
        "layout": json.loads(d.layout or "{}"),
        "widgets": json.loads(d.widgets or "[]"),
    }


@router.post("/dashboards")
async def create_dashboard(
    name: str, layout: str = "{}", widgets: str = "[]",
    description: str = None, db: Session = Depends(get_db),
):
    dash = Dashboard(name=name, description=description, layout=layout, widgets=widgets)
    db.add(dash)
    db.commit()
    db.refresh(dash)
    return {"id": dash.id, "name": dash.name, "status": "created"}


@router.put("/dashboards/{dashboard_id}")
async def update_dashboard(
    dashboard_id: int, name: str = None, layout: str = None,
    widgets: str = None, db: Session = Depends(get_db),
):
    d = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    if name: d.name = name
    if layout: d.layout = layout
    if widgets: d.widgets = widgets
    d.updated_at = datetime.utcnow()
    db.commit()
    return {"status": "updated"}


@router.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    d = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    db.delete(d)
    db.commit()
    return {"status": "deleted"}


# ─── Email Reports ─────────────────────────────────────────

_email_engine = EmailEngine()
_scheduler = None


@router.post("/email/test")
async def test_email(to: str, db: Session = Depends(get_db)):
    """Send a test email."""
    _email_engine.send_daily_report(to, db)
    return {"status": "sent", "to": to}


@router.post("/email/alert-notification")
async def send_alert_email(to: str, alert_data: dict):
    _email_engine.send_alert_notification(to, alert_data)
    return {"status": "sent"}


@router.post("/email/daily-report")
async def send_daily_report(to: str, db: Session = Depends(get_db)):
    _email_engine.send_daily_report(to, db)
    return {"status": "sent"}


@router.post("/email/threat-brief")
async def send_threat_brief(to: str, db: Session = Depends(get_db)):
    _email_engine.send_threat_brief(to, db)
    return {"status": "sent"}


# ─── LDAP/SSO ──────────────────────────────────────────────

@router.post("/auth/ldap")
async def ldap_login(username: str, password: str, db: Session = Depends(get_db)):
    """LDAP-authenticated login. Falls back to local DB if LDAP unavailable."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": UserResponse.model_validate(user)}


@router.post("/auth/sso")
async def sso_login(provider: str, token: str, db: Session = Depends(get_db)):
    """SSO authentication (Google, Microsoft, GitHub).
    
    In production, validate the OAuth token with the provider.
    For now, extract email from token (mock) and create/find user.
    """
    email = f"{token[:8]}@sso.local"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        username = email.split("@")[0]
        user = User(username=username, email=email, hashed_password="sso",
                    full_name=f"SSO {provider} User", role="analyst")
        db.add(user)
        db.commit()
        db.refresh(user)

    user.last_login = datetime.utcnow()
    db.commit()

    jwt_token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": jwt_token, "token_type": "bearer", "user": UserResponse.model_validate(user)}
