import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.alert import Alert

logger = logging.getLogger(__name__)

MAX_CONTEXT_LENGTH = 4000


class ContextBuilder:
    """Build context for AI prompts from database data."""
    
    def __init__(self):
        self._mitre_cache = None
    
    def _load_mitre_mappings(self) -> Dict:
        """Load MITRE mapping data."""
        if self._mitre_cache is not None:
            return self._mitre_cache
        
        try:
            import os
            data_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'backend', 'data', 'mitre_mapping.json'
            )
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    self._mitre_cache = data.get('mappings', {})
                    return self._mitre_cache
        except Exception as e:
            logger.warning(f"Could not load MITRE mappings: {e}")
        
        self._mitre_cache = {}
        return self._mitre_cache
    
    def build_alert_context(self, alert_id: int, db: Session) -> Dict[str, Any]:
        """Build context for a single alert."""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        
        if not alert:
            return {'error': 'Alert not found'}
        
        related_alerts = db.query(Alert).filter(
            Alert.source_ip == alert.source_ip,
            Alert.timestamp >= datetime.utcnow() - timedelta(hours=24),
            Alert.id != alert_id
        ).order_by(Alert.timestamp.desc()).limit(5).all()
        
        mitre_mappings = self._load_mitre_mappings()
        mitre_key = alert.mitre_technique or alert.rule_name.lower().replace(' ', '_')
        mitre_details = mitre_mappings.get(mitre_key, {})
        
        return {
            'alert': self._format_alert(alert),
            'related_alerts': [self._format_alert(a) for a in related_alerts],
            'asset_info': {'ip': alert.source_ip, 'name': 'unknown'},
            'mitre_details': mitre_details,
        }
    
    def build_narrative_context(self, alert_ids: List[int], db: Session) -> Dict[str, Any]:
        """Build context for multiple alerts (narrative)."""
        alerts = db.query(Alert).filter(Alert.id.in_(alert_ids)).order_by(Alert.timestamp).all()
        
        if not alerts:
            return {'error': 'No alerts found'}
        
        return {
            'alerts': [self._format_alert(a) for a in alerts],
            'start_time': alerts[0].timestamp.isoformat() if alerts else None,
            'end_time': alerts[-1].timestamp.isoformat() if alerts else None,
        }
    
    def build_incident_context(self, incident_id: int, db: Session) -> Dict[str, Any]:
        """Build context for an incident."""
        from backend.models.incident import Incident
        
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        
        if not incident:
            return {'error': 'Incident not found'}
        
        linked_alerts = db.query(Alert).filter(
            Alert.incident_id == incident_id
        ).order_by(Alert.timestamp).all()
        
        return {
            'incident': {
                'id': incident.id,
                'title': incident.title,
                'severity': incident.severity,
                'status': incident.status,
                'created_at': incident.created_at.isoformat() if incident.created_at else None,
            },
            'alerts': [self._format_alert(a) for a in linked_alerts],
            'assets': [],
        }
    
    def build_platform_context(self, db: Session) -> Dict[str, Any]:
        """Build current platform context."""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        active_alerts = db.query(Alert).filter(Alert.status == 'open').count()
        critical_last_hour = db.query(Alert).filter(
            Alert.severity >= 5,
            Alert.timestamp >= hour_ago
        ).count()
        
        top_techniques = db.query(
            Alert.mitre_technique,
            func.count(Alert.id).label('count')
        ).filter(
            Alert.timestamp >= now - timedelta(hours=24),
            Alert.mitre_technique.isnot(None)
        ).group_by(Alert.mitre_technique).order_by(func.count(Alert.id).desc()).limit(3).all()
        
        top_sources = db.query(
            Alert.source_ip,
            func.count(Alert.id).label('count')
        ).filter(
            Alert.timestamp >= now - timedelta(hours=24),
            Alert.source_ip.isnot(None)
        ).group_by(Alert.source_ip).order_by(func.count(Alert.id).desc()).limit(3).all()
        
        return {
            'active_alerts_count': active_alerts,
            'critical_alerts_last_hour': critical_last_hour,
            'top_mitre_techniques': [{'technique': t, 'count': c} for t, c in top_techniques],
            'top_attacked_assets': [{'ip': ip, 'count': c} for ip, c in top_sources],
        }
    
    def format_for_prompt(self, data: Dict[str, Any]) -> str:
        """Format context data for AI prompt with truncation."""
        try:
            json_str = json.dumps(data, indent=2, default=str)
            
            if len(json_str) <= MAX_CONTEXT_LENGTH:
                return json_str
            
            truncated = json_str[:MAX_CONTEXT_LENGTH]
            last_brace = truncated.rfind('}')
            if last_brace > 0:
                truncated = truncated[:last_brace + 1]
            
            return truncated + '\n\n[Data truncated for context limit]'
        except Exception as e:
            logger.error(f"Error formatting context: {e}")
            return str(data)
    
    def _format_alert(self, alert: Alert) -> Dict[str, Any]:
        """Format alert for AI context."""
        return {
            'alert_id': alert.alert_id,
            'rule_name': alert.rule_name,
            'severity': alert.severity,
            'source_ip': alert.source_ip,
            'dest_ip': alert.dest_ip,
            'username': alert.username,
            'mitre_tactic': alert.mitre_tactic,
            'mitre_technique': alert.mitre_technique,
            'evidence': alert.evidence[:500] if alert.evidence else None,
            'timestamp': alert.timestamp.isoformat() if alert.timestamp else None,
            'status': alert.status,
        }


_context_builder: Optional[ContextBuilder] = None


def get_context_builder() -> ContextBuilder:
    """Get singleton context builder."""
    global _context_builder
    if _context_builder is None:
        _context_builder = ContextBuilder()
    return _context_builder