"""Detection API - Correlation rules, custom rules, user analytics, anomalies."""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.alert import Alert
from backend.models.detection_rule import DetectionRule
from backend.schemas.detection import (
    DetectionRuleCreate,
    DetectionRuleResponse,
    DetectionRuleUpdate,
    CorrelationResult,
    UserRiskScore,
)
from backend.services.correlation_rules import CorrelationEngine, CORRELATION_RULES
from backend.services.user_analytics import UserBehaviorAnalytics
from backend.services.anomaly_detector import AnomalyDetector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/detection", tags=["Detection"])


def generate_rule_id() -> str:
    return f"RULE-{uuid.uuid4().hex[:8].upper()}"


@router.get("/correlation/rules")
async def get_correlation_rules():
    """List all active correlation rules."""
    return [
        {
            "name": r["name"],
            "description": r["description"],
            "severity": r["severity"],
            "time_window_minutes": r["time_window_minutes"],
        }
        for r in CORRELATION_RULES
    ]


@router.post("/correlation/run")
async def run_correlation(db: Session = Depends(get_db)):
    """Run all correlation rules and return generated alerts."""
    engine = CorrelationEngine(db)
    alerts = engine.run_all_rules()
    
    correlations = engine.get_active_correlations()
    
    return {
        "alerts_generated": len(alerts),
        "alert_ids": [a.alert_id for a in alerts],
        "active_correlations": correlations,
    }


@router.get("/correlation/results")
async def get_correlation_results(hours: int = 24, db: Session = Depends(get_db)):
    """Get correlation alerts generated in the last N hours."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    alerts = db.query(Alert).filter(
        Alert.rule_name.like("[Correlation]%"),
        Alert.timestamp >= cutoff,
    ).order_by(desc(Alert.timestamp)).all()

    return [
        CorrelationResult(
            rule_name=a.rule_name.replace("[Correlation] ", ""),
            severity=a.severity,
            description=f"Correlation alert from {a.source_ip or 'unknown'}",
            alert_id=a.alert_id,
            timestamp=a.timestamp,
            source_ip=a.source_ip,
            details={"username": a.username, "evidence": a.evidence[:200] if a.evidence else None},
        )
        for a in alerts
    ]


@router.get("/user-analytics/risk-scores", response_model=list[UserRiskScore])
async def get_user_risk_scores(db: Session = Depends(get_db)):
    """Get risk scores for all users."""
    analytics = UserBehaviorAnalytics(db)
    return analytics.get_all_user_risk_scores()


@router.get("/user-analytics/{username}")
async def get_user_analytics(username: str, db: Session = Depends(get_db)):
    """Get detailed analytics for a specific user."""
    analytics = UserBehaviorAnalytics(db)
    baseline = analytics.build_baseline(username)
    risk = analytics.get_user_risk_score(username)
    return {"baseline": baseline, "risk": risk}


@router.get("/anomalies")
async def get_anomalies(db: Session = Depends(get_db)):
    """Get current anomaly detection results."""
    detector = AnomalyDetector(db)
    return detector.get_anomaly_summary()


@router.post("/anomalies/check-volume")
async def check_volume_anomaly(db: Session = Depends(get_db)):
    """Force check for volume anomalies."""
    detector = AnomalyDetector(db)
    detector.build_volume_baseline()
    return detector.check_volume_anomaly()


@router.get("/rules", response_model=list[DetectionRuleResponse])
async def get_detection_rules(
    rule_type: str = None,
    enabled: bool = None,
    db: Session = Depends(get_db),
):
    """Get custom detection rules."""
    query = db.query(DetectionRule)
    if rule_type:
        query = query.filter(DetectionRule.rule_type == rule_type)
    if enabled is not None:
        query = query.filter(DetectionRule.enabled == enabled)
    return query.order_by(desc(DetectionRule.created_at)).all()


@router.post("/rules", response_model=DetectionRuleResponse)
async def create_detection_rule(rule: DetectionRuleCreate, db: Session = Depends(get_db)):
    """Create a custom detection rule."""
    db_rule = DetectionRule(
        rule_id=generate_rule_id(),
        name=rule.name,
        description=rule.description,
        rule_type=rule.rule_type,
        event_type=rule.event_type,
        severity=rule.severity,
        time_window_seconds=rule.time_window_seconds,
        threshold=rule.threshold,
        pattern=rule.pattern,
        sequence=rule.sequence,
        mitre_tactic=rule.mitre_tactic,
        mitre_technique=rule.mitre_technique,
        enabled=True,
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.put("/rules/{rule_id}", response_model=DetectionRuleResponse)
async def update_detection_rule(rule_id: str, rule: DetectionRuleUpdate, db: Session = Depends(get_db)):
    """Update a custom detection rule."""
    db_rule = db.query(DetectionRule).filter(DetectionRule.rule_id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    update_data = rule.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rule, key, value)

    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.delete("/rules/{rule_id}")
async def delete_detection_rule(rule_id: str, db: Session = Depends(get_db)):
    """Delete a custom detection rule."""
    db_rule = db.query(DetectionRule).filter(DetectionRule.rule_id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(db_rule)
    db.commit()
    return {"status": "deleted", "rule_id": rule_id}


@router.post("/integrate")
async def integrate_correlation_into_detection(alert_id: int, db: Session = Depends(get_db)):
    """Run correlation rules and detection engine for a specific alert context."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    engine = CorrelationEngine(db)
    results = engine.run_all_rules()

    analytics = UserBehaviorAnalytics(db)
    user_anomalies = None
    if alert.username:
        user_anomalies = analytics.detect_anomalies(alert.username, None)

    detector = AnomalyDetector(db)
    volume_anomaly = detector.check_volume_anomaly()

    return {
        "correlation_alerts_generated": len(results),
        "correlation_alert_ids": [a.alert_id for a in results],
        "user_anomalies_detected": user_anomalies is not None,
        "volume_anomaly_detected": volume_anomaly is not None,
        "volume_anomaly": volume_anomaly,
    }
