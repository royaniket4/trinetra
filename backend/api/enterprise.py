"""Enterprise SIEM features API - Compliance, Threat Intel, MITRE, Webhooks, Reports, Assets."""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.compliance import ComplianceEngine, COMPLIANCE_FRAMEWORKS
from backend.services.threat_intel import ThreatIntelEngine
from backend.services.reports import ReportEngine
from backend.services.mitre_navigator import MitreNavigator
from backend.services.webhook_engine import WebhookEngine
from backend.models.webhook import Webhook
from backend.models.asset import Asset

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enterprise", tags=["Enterprise"])


@router.get("/compliance/frameworks")
async def list_frameworks(db: Session = Depends(get_db)):
    engine = ComplianceEngine(db)
    return engine.list_frameworks()


@router.get("/compliance/frameworks/{framework_id}")
async def get_compliance_score(framework_id: str, db: Session = Depends(get_db)):
    if framework_id not in COMPLIANCE_FRAMEWORKS:
        raise HTTPException(status_code=404, detail=f"Unknown framework: {framework_id}")
    engine = ComplianceEngine(db)
    return engine.get_framework_summary(framework_id)


@router.get("/threat-intel/summary")
async def get_threat_intel_summary(db: Session = Depends(get_db)):
    engine = ThreatIntelEngine(db)
    return engine.get_threat_intel_summary()


@router.get("/reports/daily-brief")
async def get_daily_brief(db: Session = Depends(get_db)):
    engine = ReportEngine(db)
    return engine.generate_daily_brief()


@router.get("/reports/threat-brief")
async def get_threat_brief(db: Session = Depends(get_db)):
    engine = ReportEngine(db)
    return engine.generate_threat_brief()


@router.get("/reports/alerts-csv")
async def export_alerts_csv(hours: int = Query(24), db: Session = Depends(get_db)):
    engine = ReportEngine(db)
    csv_content = engine.generate_alerts_csv(hours)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=alerts_{datetime.utcnow().strftime('%Y%m%d')}.csv"},
    )


@router.get("/reports/incidents-csv")
async def export_incidents_csv(hours: int = Query(168), db: Session = Depends(get_db)):
    engine = ReportEngine(db)
    csv_content = engine.generate_incidents_csv(hours)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=incidents_{datetime.utcnow().strftime('%Y%m%d')}.csv"},
    )


@router.get("/mitre/coverage")
async def get_mitre_coverage(hours: int = Query(720), db: Session = Depends(get_db)):
    nav = MitreNavigator(db)
    return nav.get_coverage(hours)


@router.get("/mitre/technique/{technique_id}")
async def get_technique_detail(technique_id: str, hours: int = Query(720), db: Session = Depends(get_db)):
    nav = MitreNavigator(db)
    return nav.get_technique_detail(technique_id, hours)


@router.get("/mitre/recommendations")
async def get_mitre_recommendations(db: Session = Depends(get_db)):
    nav = MitreNavigator(db)
    return nav.get_recommendations()


@router.get("/webhooks")
async def list_webhooks(db: Session = Depends(get_db)):
    return db.query(Webhook).all()


@router.post("/webhooks")
async def create_webhook(name: str, url: str, event_type: str, provider: str = "webhook", db: Session = Depends(get_db)):
    engine = WebhookEngine(db)
    hook = engine.create_hook(name, url, event_type, provider)
    return hook


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: int, db: Session = Depends(get_db)):
    hook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not hook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    db.delete(hook)
    db.commit()
    return {"status": "deleted"}


@router.post("/webhooks/{webhook_id}/test")
async def test_webhook(webhook_id: int, db: Session = Depends(get_db)):
    engine = WebhookEngine(db)
    result = engine.test_hook(webhook_id)
    return {"success": result}


@router.get("/assets")
async def list_assets(db: Session = Depends(get_db)):
    return db.query(Asset).all()


@router.get("/assets/{asset_id}")
async def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset
