"""User behavior analytics engine - detects anomalous user activity."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.log import Log
from backend.models.alert import Alert

logger = logging.getLogger(__name__)


class UserBehaviorAnalytics:
    """Track user behavior baselines and detect anomalies."""

    def __init__(self, db: Session):
        self.db = db
        self._baselines: Dict[str, Dict] = {}

    def build_baseline(self, user: str, hours: int = 24) -> Dict:
        """Build a behavior baseline for a user."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        logs = self.db.query(Log).filter(
            Log.username == user,
            Log.timestamp >= cutoff,
        ).all()

        baseline = {
            "username": user,
            "total_logs": len(logs),
            "event_types": defaultdict(int),
            "hourly_distribution": defaultdict(int),
            "source_ips": defaultdict(int),
            "avg_logs_per_hour": 0,
            "peak_hour": None,
            "last_seen": None,
        }

        for log in logs:
            if log.event_type:
                baseline["event_types"][log.event_type] += 1
            if log.timestamp:
                hour = log.timestamp.hour
                baseline["hourly_distribution"][hour] += 1
            if log.source_ip:
                baseline["source_ips"][log.source_ip] += 1

            if log.timestamp:
                if not baseline["last_seen"] or log.timestamp > baseline["last_seen"]:
                    baseline["last_seen"] = log.timestamp

        if logs:
            baseline["avg_logs_per_hour"] = len(logs) / max(hours, 1)
            peak_hour = max(baseline["hourly_distribution"], key=baseline["hourly_distribution"].get)
            baseline["peak_hour"] = peak_hour

        baseline["event_types"] = dict(baseline["event_types"])
        baseline["hourly_distribution"] = dict(baseline["hourly_distribution"])
        baseline["source_ips"] = dict(baseline["source_ips"])

        self._baselines[user] = baseline
        return baseline

    def detect_anomalies(self, user: str, new_log: Log) -> Optional[Dict]:
        """Detect anomalies in a user's latest activity."""
        if user not in self._baselines:
            self.build_baseline(user)
            return None

        baseline = self._baselines[user]
        anomalies = []

        # Check for unusual event type
        if new_log.event_type and baseline["event_types"]:
            expected_count = baseline["event_types"].get(new_log.event_type, 0)
            total = sum(baseline["event_types"].values())
            if total > 10 and expected_count < max(2, total * 0.05):
                anomalies.append(f"Rare event type '{new_log.event_type}' for user {user}")

        # Check for unusual source IP
        if new_log.source_ip and baseline["source_ips"]:
            if new_log.source_ip not in baseline["source_ips"]:
                anomalies.append(f"New source IP '{new_log.source_ip}' for user {user}")

        # Check for unusual hour
        if new_log.timestamp:
            hour = new_log.timestamp.hour
            if baseline["hourly_distribution"] and baseline["avg_logs_per_hour"] > 1:
                hour_count = baseline["hourly_distribution"].get(hour, 0)
                expected = baseline["avg_logs_per_hour"]
                if hour_count < expected * 0.3:
                    anomalies.append(f"Unusual activity hour ({hour}:00) for user {user}")

        # Check for high velocity
        if baseline["total_logs"] > 10:
            recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
            recent_count = self.db.query(Log).filter(
                Log.username == user,
                Log.timestamp >= recent_cutoff,
            ).count()
            expected_5min = baseline["avg_logs_per_hour"] / 12
            if recent_count > expected_5min * 5 and recent_count >= 5:
                anomalies.append(f"High activity velocity: {recent_count} events in 5min for user {user}")

        if anomalies:
            return {
                "username": user,
                "anomalies": anomalies,
                "severity": "medium" if len(anomalies) <= 2 else "high",
                "timestamp": datetime.utcnow(),
            }

        return None

    def get_user_risk_score(self, user: str) -> Dict:
        """Get risk assessment for a user based on behavior."""
        cutoff = datetime.utcnow() - timedelta(hours=1)

        alert_count = self.db.query(Alert).filter(
            Alert.username == user,
            Alert.timestamp >= cutoff,
        ).count()

        recent_alerts = self.db.query(Alert).filter(
            Alert.username == user,
            Alert.timestamp >= datetime.utcnow() - timedelta(hours=24),
        ).order_by(Alert.timestamp.desc()).all()

        severity_scores = {"3": 1, "4": 2, "5": 3}
        total_risk = sum(severity_scores.get(str(a.severity), 0) for a in recent_alerts)

        risk_level = "low"
        if total_risk >= 10:
            risk_level = "critical"
        elif total_risk >= 6:
            risk_level = "high"
        elif total_risk >= 3:
            risk_level = "medium"

        return {
            "username": user,
            "risk_score": total_risk,
            "risk_level": risk_level,
            "alerts_last_hour": alert_count,
            "alerts_last_24h": len(recent_alerts),
            "top_alert_types": list(set(a.rule_name for a in recent_alerts[:10])),
        }

    def get_all_user_risk_scores(self) -> List[Dict]:
        """Get risk scores for all users with recent activity."""
        cutoff = datetime.utcnow() - timedelta(hours=24)

        users = self.db.query(Alert.username).filter(
            Alert.username.isnot(None),
            Alert.timestamp >= cutoff,
        ).distinct().all()

        scores = []
        for (user,) in users:
            if user:
                score = self.get_user_risk_score(user)
                scores.append(score)

        return sorted(scores, key=lambda x: x["risk_score"], reverse=True)
