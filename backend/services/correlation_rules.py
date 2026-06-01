"""Multi-event correlation rules engine - detects attack patterns across sequences of alerts."""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.models.alert import Alert
from backend.models.incident import Incident
from backend.websocket.manager import broadcast_alert

logger = logging.getLogger(__name__)


CORRELATION_RULES = []


def correlation_rule(name: str, description: str, severity: int, time_window_minutes: int = 60):
    """Decorator to register a correlation rule."""
    def decorator(func: Callable):
        CORRELATION_RULES.append({
            "name": name,
            "description": description,
            "severity": severity,
            "time_window_minutes": time_window_minutes,
            "handler": func,
        })
        return func
    return decorator


class CorrelationEngine:
    """Advanced multi-event correlation engine for attack pattern detection."""

    def __init__(self, db: Session):
        self.db = db

    def run_all_rules(self) -> List[Alert]:
        """Run all registered correlation rules and return generated alerts."""
        new_alerts = []
        for rule in CORRELATION_RULES:
            try:
                window = timedelta(minutes=rule["time_window_minutes"])
                cutoff = datetime.utcnow() - window
                alerts = rule["handler"](self.db, cutoff)
                for alert_data in alerts:
                    alert = self._create_correlation_alert(rule, alert_data)
                    if alert:
                        new_alerts.append(alert)
            except Exception as e:
                logger.error(f"Correlation rule '{rule['name']}' failed: {e}")
        return new_alerts

    def _create_correlation_alert(self, rule: Dict, alert_data: Dict) -> Optional[Alert]:
        """Create an alert from a correlation rule match."""
        existing = self.db.query(Alert).filter(
            Alert.rule_name == f"[Correlation] {rule['name']}",
            Alert.source_ip == alert_data.get("source_ip"),
            Alert.timestamp >= datetime.utcnow() - timedelta(minutes=5),
        ).first()
        if existing:
            return None

        alert = Alert(
            alert_id=f"CORR-{uuid.uuid4().hex[:8].upper()}",
            rule_name=f"[Correlation] {rule['name']}",
            severity=rule["severity"],
            mitre_tactic=alert_data.get("mitre_tactic", "Discovery"),
            mitre_technique=alert_data.get("mitre_technique", "T1078"),
            confidence=0.85,
            evidence=json.dumps(alert_data.get("evidence", {})),
            timestamp=datetime.utcnow(),
            source_ip=alert_data.get("source_ip"),
            dest_ip=alert_data.get("dest_ip"),
            username=alert_data.get("username"),
            status="open",
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        try:
            broadcast_alert(alert)
        except Exception as e:
            logger.error(f"Broadcast failed: {e}")

        logger.info(f"Correlation alert: {alert.alert_id} - {rule['name']}")
        return alert

    def get_active_correlations(self, hours: int = 24) -> List[Dict]:
        """Get active correlation patterns."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        alerts = self.db.query(Alert).filter(
            Alert.rule_name.like("[Correlation]%"),
            Alert.timestamp >= cutoff,
        ).order_by(desc(Alert.timestamp)).all()

        result = {}
        for alert in alerts:
            key = alert.rule_name
            if key not in result:
                result[key] = {"rule": key, "count": 0, "last_seen": alert.timestamp}
            result[key]["count"] += 1
            if alert.timestamp > result[key]["last_seen"]:
                result[key]["last_seen"] = alert.timestamp
        return list(result.values())


import uuid


@correlation_rule(
    name="Brute Force to Compromise",
    description="Failed logins followed by successful login and suspicious activity from same IP",
    severity=5,
    time_window_minutes=30,
)
def brute_force_to_compromise(db: Session, cutoff: datetime):
    """Detect: failed logins + successful login + powershell/execution from same IP."""
    results = []

    # Get recent brute force alerts
    bf_alerts = db.query(Alert).filter(
        Alert.rule_name == "Brute Force Detection",
        Alert.timestamp >= cutoff,
    ).all()

    for bf in bf_alerts:
        ip = bf.source_ip
        if not ip:
            continue

        # Check for successful login after brute force
        success_logins = db.query(Alert).filter(
            Alert.rule_name.ilike("%login_success%"),
            Alert.source_ip == ip,
            Alert.timestamp >= bf.timestamp,
            Alert.timestamp <= bf.timestamp + timedelta(minutes=15),
        ).count()

        # Check for execution/powershell activity after brute force
        exec_alerts = db.query(Alert).filter(
            Alert.rule_name.in_(["PowerShell Encoded Command", "Reverse Shell Signature"]),
            Alert.source_ip == ip,
            Alert.timestamp >= bf.timestamp,
            Alert.timestamp <= bf.timestamp + timedelta(minutes=30),
        ).all()

        if success_logins > 0 and len(exec_alerts) > 0:
            results.append({
                "source_ip": ip,
                "username": bf.username,
                "mitre_tactic": "Privilege Escalation",
                "mitre_technique": "T1078",
                "evidence": {
                    "brute_force_alert_id": bf.alert_id,
                    "execution_alerts": [a.alert_id for a in exec_alerts],
                    "successful_logins": success_logins,
                    "description": f"Brute force from {ip} followed by {len(exec_alerts)} execution alerts - likely compromise",
                },
            })

    return results


@correlation_rule(
    name="Lateral Movement Chain",
    description="Multiple lateral movement alerts from sequential IPs indicating spread",
    severity=5,
    time_window_minutes=60,
)
def lateral_movement_chain(db: Session, cutoff: datetime):
    """Detect: lateral movement spreading through the network."""
    results = []

    lm_alerts = db.query(Alert).filter(
        Alert.rule_name == "Lateral Movement Detected",
        Alert.timestamp >= cutoff,
    ).order_by(Alert.timestamp).all()

    # Group by username
    by_user = {}
    for a in lm_alerts:
        user = a.username or "unknown"
        if user not in by_user:
            by_user[user] = []
        by_user[user].append(a)

    for user, alerts in by_user.items():
        if len(alerts) >= 3:
            unique_ips = set(a.source_ip for a in alerts if a.source_ip)
            unique_dests = set(a.dest_ip for a in alerts if a.dest_ip)
            if len(unique_ips) >= 2 or len(unique_dests) >= 2:
                results.append({
                    "username": user,
                    "source_ip": alerts[0].source_ip,
                    "dest_ip": alerts[-1].dest_ip,
                    "mitre_tactic": "Lateral Movement",
                    "mitre_technique": "T1021",
                    "evidence": {
                        "alert_ids": [a.alert_id for a in alerts],
                        "hop_count": len(alerts),
                        "source_ips": list(unique_ips),
                        "dest_ips": list(unique_dests),
                        "description": f"Lateral movement chain detected for user {user}: {len(alerts)} hops across {len(unique_ips)} sources",
                    },
                })

    return results


@correlation_rule(
    name="Recon to Exploitation",
    description="Port scan followed by exploitation attempt (SQLi, RCE) from same IP",
    severity=4,
    time_window_minutes=30,
)
def recon_to_exploitation(db: Session, cutoff: datetime):
    """Detect: port scan + exploitation from same IP."""
    results = []

    scan_alerts = db.query(Alert).filter(
        Alert.rule_name == "Port Scan Detected",
        Alert.timestamp >= cutoff,
    ).all()

    exploit_rules = ["SQL Injection Attempt", "Reverse Shell Signature", "Privilege Escalation Attempt"]

    for scan in scan_alerts:
        ip = scan.source_ip
        if not ip:
            continue

        exploits = db.query(Alert).filter(
            Alert.rule_name.in_(exploit_rules),
            Alert.source_ip == ip,
            Alert.timestamp >= scan.timestamp,
            Alert.timestamp <= scan.timestamp + timedelta(minutes=30),
        ).all()

        if exploits:
            results.append({
                "source_ip": ip,
                "mitre_tactic": "Initial Access",
                "mitre_technique": "T1190",
                "evidence": {
                    "scan_alert_id": scan.alert_id,
                    "exploit_alerts": [a.alert_id for a in exploits],
                    "description": f"Recon from {ip} followed by exploitation: {', '.join(a.rule_name for a in exploits)}",
                },
            })

    return results


@correlation_rule(
    name="Credential Access to Exfiltration",
    description="Credential dumping followed by data exfiltration from same host",
    severity=5,
    time_window_minutes=60,
)
def credential_to_exfiltration(db: Session, cutoff: datetime):
    """Detect: credential dumping + data exfiltration from same IP."""
    results = []

    dump_alerts = db.query(Alert).filter(
        Alert.rule_name == "Credential Dumping Indicators",
        Alert.timestamp >= cutoff,
    ).all()

    for dump in dump_alerts:
        ip = dump.source_ip
        if not ip:
            continue

        exfil = db.query(Alert).filter(
            Alert.rule_name == "Potential Data Exfiltration",
            Alert.source_ip == ip,
            Alert.timestamp >= dump.timestamp,
            Alert.timestamp <= dump.timestamp + timedelta(hours=1),
        ).first()

        if exfil:
            results.append({
                "source_ip": ip,
                "username": dump.username,
                "mitre_tactic": "Exfiltration",
                "mitre_technique": "T1041",
                "evidence": {
                    "credential_dump_alert_id": dump.alert_id,
                    "exfiltration_alert_id": exfil.alert_id,
                    "description": f"Credential dumping on {ip} followed by data exfiltration",
                },
            })

    return results


@correlation_rule(
    name="Ransomware Pre-cursor Chain",
    description="Suspicious download + privilege escalation + credential access = ransomware risk",
    severity=5,
    time_window_minutes=45,
)
def ransomware_precursor(db: Session, cutoff: datetime):
    """Detect: suspicious download followed by escalation and credential access."""
    results = []

    download_alerts = db.query(Alert).filter(
        Alert.rule_name == "Suspicious File Download",
        Alert.timestamp >= cutoff,
    ).all()

    for dl in download_alerts:
        ip = dl.source_ip
        if not ip:
            continue

        escalation = db.query(Alert).filter(
            Alert.rule_name == "Privilege Escalation Attempt",
            Alert.source_ip == ip,
            Alert.timestamp >= dl.timestamp,
            Alert.timestamp <= dl.timestamp + timedelta(minutes=30),
        ).first()

        credential_access = db.query(Alert).filter(
            Alert.rule_name == "Credential Dumping Indicators",
            Alert.source_ip == ip,
            Alert.timestamp >= dl.timestamp,
            Alert.timestamp <= dl.timestamp + timedelta(minutes=45),
        ).first()

        if escalation and credential_access:
            results.append({
                "source_ip": ip,
                "username": dl.username,
                "mitre_tactic": "Impact",
                "mitre_technique": "T1486",
                "evidence": {
                    "download_alert_id": dl.alert_id,
                    "escalation_alert_id": escalation.alert_id,
                    "credential_access_alert_id": credential_access.alert_id,
                    "description": f"Ransomware precursor chain detected on {ip}: download -> escalation -> credential access",
                },
            })

    return results
