"""Time-series anomaly detection for log volume and alert patterns."""

import logging
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.log import Log
from backend.models.alert import Alert

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detect anomalies in time-series data (log volume, alert frequency)."""

    def __init__(self, db: Session):
        self.db = db
        self._baseline = None

    def build_volume_baseline(self, hours: int = 24) -> Dict:
        """Build hourly volume baseline for logs."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        rows = self.db.query(
            func.strftime('%Y-%m-%d %H:00:00', Log.timestamp).label('hour'),
            func.count(Log.id).label('count'),
        ).filter(
            Log.timestamp >= cutoff,
        ).group_by('hour').all()

        hourly_counts = {}
        for row in rows:
            hourly_counts[row.hour] = row.count

        if not hourly_counts:
            return {"mean": 0, "std": 0, "hourly_counts": {}}

        values = list(hourly_counts.values())
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(variance) if variance > 0 else 1

        self._baseline = {
            "mean": mean,
            "std": std,
            "hourly_counts": hourly_counts,
            "total_hours": len(values),
        }

        return self._baseline

    def check_volume_anomaly(self) -> Optional[Dict]:
        """Check current hour log volume for anomalies."""
        baseline = self._baseline
        if not baseline:
            baseline = self.build_volume_baseline()

        now = datetime.utcnow()
        current_hour = now.strftime('%Y-%m-%d %H:00:00')

        current_count = self.db.query(Log).filter(
            func.strftime('%Y-%m-%d %H:00:00', Log.timestamp) == current_hour,
        ).count()

        mean = baseline.get("mean", 0)
        std = baseline.get("std", 1)

        if mean == 0 or current_count == 0:
            return None

        z_score = (current_count - mean) / std

        if abs(z_score) < 2:
            return None

        direction = "spike" if z_score > 0 else "drop"
        severity = "high" if abs(z_score) > 4 else "medium"

        return {
            "type": f"volume_{direction}",
            "severity": severity,
            "current_count": current_count,
            "expected_mean": round(mean, 1),
            "z_score": round(z_score, 2),
            "std_deviation": round(std, 1),
            "hour": current_hour,
            "description": f"Log volume {direction} detected: {current_count} vs expected {round(mean, 1)} (z={round(z_score, 2)})",
        }

    def check_alert_anomaly(self, hours: int = 6) -> Optional[Dict]:
        """Detect unusual spikes in alert generation."""
        now = datetime.utcnow()
        recent = self.db.query(Alert).filter(
            Alert.timestamp >= now - timedelta(hours=hours),
        ).count()

        older = self.db.query(Alert).filter(
            Alert.timestamp >= now - timedelta(hours=hours * 2),
            Alert.timestamp < now - timedelta(hours=hours),
        ).count()

        if older == 0:
            return None

        ratio = recent / older if older > 0 else 0

        if ratio > 3 and recent >= 10:
            return {
                "type": "alert_spike",
                "severity": "high",
                "recent_count": recent,
                "previous_count": older,
                "ratio": round(ratio, 1),
                "hours_analyzed": hours,
                "description": f"Alert spike detected: {recent} alerts in last {hours}h vs {older} in previous {hours}h ({ratio}x increase)",
            }

        return None

    def get_anomaly_summary(self) -> Dict:
        """Get anomaly dashboard summary."""
        volume = self.check_volume_anomaly()
        alert_spike = self.check_alert_anomaly()

        anomalies = []
        if volume:
            anomalies.append(volume)
        if alert_spike:
            anomalies.append(alert_spike)

        return {
            "total_anomalies": len(anomalies),
            "anomalies": anomalies,
            "baseline": self.build_volume_baseline() if self._baseline is None else self._baseline,
        }
