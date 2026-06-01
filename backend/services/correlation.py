from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from models.alert import Alert


class CorrelationEngine:
    """Correlate alerts to identify attack patterns and create incidents."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def correlate_alerts(self, time_window: int = 3600) -> List[Dict[str, Any]]:
        """Find related alerts within a time window."""
        cutoff = datetime.utcnow() - timedelta(seconds=time_window)
        
        recent_alerts = (
            self.db.query(Alert)
            .filter(Alert.timestamp >= cutoff)
            .filter(Alert.status == 'active')
            .order_by(Alert.timestamp.desc())
            .all()
        )
        
        correlations = {}
        
        for alert in recent_alerts:
            key = self._get_correlation_key(alert)
            if key not in correlations:
                correlations[key] = []
            correlations[key].append(alert)
        
        results = []
        for key, alerts in correlations.items():
            if len(alerts) >= 2:
                results.append({
                    'type': key['type'],
                    'alerts': alerts,
                    'count': len(alerts),
                    'first_seen': alerts[-1].timestamp,
                    'last_seen': alerts[0].timestamp,
                    'severity': max(a.severity for a in alerts),
                })
        
        return results
    
    def _get_correlation_key(self, alert: Alert) -> Dict[str, Any]:
        """Generate correlation key for an alert."""
        if alert.source_ip:
            return {
                'type': 'by_ip',
                'value': alert.source_ip,
            }
        elif alert.username:
            return {
                'type': 'by_user',
                'value': alert.username,
            }
        
        return {
            'type': 'by_pattern',
            'value': alert.rule_name,
        }
    
    def identify_attack_chain(self, source_ip: str, time_window: int = 3600) -> List[Alert]:
        """Identify a complete attack chain from a source IP."""
        cutoff = datetime.utcnow() - timedelta(seconds=time_window)
        
        alerts = (
            self.db.query(Alert)
            .filter(Alert.source_ip == source_ip)
            .filter(Alert.timestamp >= cutoff)
            .order_by(Alert.timestamp.asc())
            .all()
        )
        
        return alerts
    
    def group_by_incident(self, alerts: List[Alert]) -> Dict[int, List[Alert]]:
        """Group alerts by incident ID."""
        grouped = {}
        
        for alert in alerts:
            if alert.incident_id:
                if alert.incident_id not in grouped:
                    grouped[alert.incident_id] = []
                grouped[alert.incident_id].append(alert)
        
        return grouped