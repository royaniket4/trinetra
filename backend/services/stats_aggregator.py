import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
from sqlalchemy import func, and_

from backend.database import SessionLocal
from backend.models.alert import Alert
from backend.models.log import Log
from backend.models.incident import Incident
from backend.models.response_action import ResponseAction

logger = logging.getLogger(__name__)


class StatsAggregator:
    """Aggregate statistics for the dashboard."""
    
    def __init__(self, cache_ttl: int = 5):
        self._cache_ttl = cache_ttl
        self._last_cache_time: Optional[datetime] = None
        self._cached_stats: Optional[Dict] = None
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self._last_cache_time or not self._cached_stats:
            return False
        return (datetime.utcnow() - self._last_cache_time).total_seconds() < self._cache_ttl
    
    def get_dashboard_stats(self, force_refresh: bool = False) -> Dict:
        """Get all dashboard statistics."""
        if self._is_cache_valid() and not force_refresh:
            return self._cached_stats
        
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            day_ago = now - timedelta(hours=24)
            
            # Total alerts in 24h
            total_alerts_24h = db.query(func.count(Alert.id)).filter(
                Alert.timestamp >= day_ago
            ).scalar() or 0
            
            # Active incidents
            active_incidents = db.query(func.count(Incident.id)).filter(
                Incident.status == 'open'
            ).scalar() or 0
            
            # Critical alerts in 24h
            critical_alerts = db.query(func.count(Alert.id)).filter(
                and_(Alert.timestamp >= day_ago, Alert.severity >= 5)
            ).scalar() or 0
            
            # Alerts by severity
            severity_counts = db.query(
                Alert.severity,
                func.count(Alert.id)
            ).filter(Alert.timestamp >= day_ago).group_by(Alert.severity).all()
            alerts_by_severity = {f"severity_{s}": c for s, c in severity_counts}
            
            # Alerts by status
            status_counts = db.query(
                Alert.status,
                func.count(Alert.id)
            ).group_by(Alert.status).all()
            alerts_by_status = {s: c for s, c in status_counts}
            
            # Alerts by hour (last 24h)
            alerts_by_hour = []
            for i in range(24):
                hour_start = now - timedelta(hours=i+1)
                hour_end = now - timedelta(hours=i)
                count = db.query(func.count(Alert.id)).filter(
                    and_(Alert.timestamp >= hour_start, Alert.timestamp < hour_end)
                ).scalar() or 0
                alerts_by_hour.append({'hour': 23 - i, 'count': count})
            
            # Top attacker countries
            top_countries = self._get_top_countries(db, day_ago)
            
            # Top MITRE techniques
            top_techniques = self._get_top_techniques(db, day_ago)
            
            # Attack paths for map
            attack_paths = self._get_attack_paths(db, day_ago)
            
            # Kill chain stages
            kill_chain = self._get_kill_chain_stages(db, day_ago)
            
            # Blocked IPs count
            blocked_ips = db.query(func.count(ResponseAction.id)).filter(
                ResponseAction.action_type == 'block_ip',
                ResponseAction.status == 'completed'
            ).scalar() or 0
            
            # Unique attack sources
            unique_sources = db.query(func.count(func.distinct(Alert.source_ip))).filter(
                Alert.timestamp >= day_ago,
                Alert.source_ip.isnot(None)
            ).scalar() or 0
            
            # Unique techniques
            unique_techniques = db.query(func.count(func.distinct(Alert.mitre_technique))).filter(
                Alert.timestamp >= day_ago,
                Alert.mitre_technique.isnot(None)
            ).scalar() or 0
            
            stats = {
                'total_alerts_24h': total_alerts_24h,
                'active_incidents': active_incidents,
                'critical_alerts_24h': critical_alerts,
                'blocked_ips_count': blocked_ips,
                'unique_attack_sources': unique_sources,
                'unique_mitre_techniques': unique_techniques,
                'alerts_by_severity': alerts_by_severity,
                'alerts_by_status': alerts_by_status,
                'alerts_by_hour': alerts_by_hour,
                'top_countries': top_countries,
                'top_techniques': top_techniques,
                'attack_paths': attack_paths,
                'kill_chain': kill_chain,
            }
            
            self._cached_stats = stats
            self._last_cache_time = datetime.utcnow()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error aggregating stats: {e}")
            return {}
        finally:
            db.close()
    
    def _get_top_countries(self, db, since) -> List[Dict]:
        """Get top attacker countries."""
        geo_lookup = None
        
        results = db.query(
            Alert.source_ip,
            func.count(Alert.id).label('count')
        ).filter(
            Alert.timestamp >= since,
            Alert.source_ip.isnot(None)
        ).group_by(
            Alert.source_ip
        ).order_by(
            func.count(Alert.id).desc()
        ).limit(15).all()
        
        from backend.services.geo_lookup import get_geo_lookup
        geo = get_geo_lookup()
        
        country_data = defaultdict(lambda: {'count': 0, 'lat': 0, 'lon': 0})
        
        for ip, count in results:
            geo_info = geo.lookup(ip)
            if geo_info and geo_info.get('country_name'):
                country_data[geo_info['country_name']]['count'] += count
                country_data[geo_info['country_name']]['lat'] = geo_info.get('lat', 0)
                country_data[geo_info['country_name']]['lon'] = geo_info.get('lon', 0)
        
        return [
            {'country': k, 'count': v['count'], 'lat': v['lat'], 'lon': v['lon']}
            for k, v in sorted(country_data.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
        ]
    
    def _get_top_techniques(self, db, since) -> List[Dict]:
        """Get top MITRE techniques."""
        results = db.query(
            Alert.mitre_technique,
            Alert.mitre_tactic,
            func.count(Alert.id).label('count')
        ).filter(
            Alert.timestamp >= since,
            Alert.mitre_technique.isnot(None)
        ).group_by(
            Alert.mitre_technique,
            Alert.mitre_tactic
        ).order_by(
            func.count(Alert.id).desc()
        ).limit(10).all()
        
        return [
            {'technique': t, 'tactic': tac, 'count': c}
            for t, tac, c in results
        ]
    
    def _get_attack_paths(self, db, since) -> List[Dict]:
        """Get recent attack paths for map visualization."""
        alerts = db.query(Alert).filter(
            Alert.timestamp >= since,
            Alert.source_ip.isnot(None),
            Alert.severity >= 3
        ).order_by(Alert.timestamp.desc()).limit(30).all()
        
        from backend.services.geo_lookup import get_geo_lookup
        geo = get_geo_lookup()
        
        paths = []
        for alert in alerts:
            if not alert.source_ip:
                continue
            
            source_geo = geo.lookup(alert.source_ip)
            dest_geo = geo.lookup(alert.dest_ip or '10.0.0.1')
            
            if source_geo and dest_geo:
                paths.append({
                    'source_lat': source_geo.get('lat', 0),
                    'source_lon': source_geo.get('lon', 0),
                    'dest_lat': dest_geo.get('lat', 0),
                    'dest_lon': dest_geo.get('lon', 0),
                    'severity': alert.severity,
                    'timestamp': alert.timestamp.isoformat(),
                    'rule_name': alert.rule_name,
                })
        
        return paths
    
    def _get_kill_chain_stages(self, db, since) -> Dict:
        """Get kill chain stage counts."""
        stages = {
            'reconnaissance': 0,
            'initial_access': 0,
            'execution': 0,
            'persistence': 0,
            'privilege_escalation': 0,
            'defense_evasion': 0,
            'credential_access': 0,
            'discovery': 0,
            'lateral_movement': 0,
            'collection': 0,
            'command_control': 0,
            'exfiltration': 0,
            'impact': 0,
        }
        
        tactic_map = {
            'TA0001': 'initial_access',
            'TA0002': 'execution',
            'TA0003': 'persistence',
            'TA0004': 'privilege_escalation',
            'TA0005': 'defense_evasion',
            'TA0006': 'credential_access',
            'TA0007': 'discovery',
            'TA0008': 'lateral_movement',
            'TA0009': 'collection',
            'TA0011': 'command_control',
            'TA0010': 'exfiltration',
            'TA0040': 'impact',
        }
        
        results = db.query(
            Alert.mitre_tactic,
            func.count(Alert.id)
        ).filter(
            Alert.timestamp >= since,
            Alert.mitre_tactic.isnot(None)
        ).group_by(Alert.mitre_tactic).all()
        
        for tactic, count in results:
            stage = tactic_map.get(tactic)
            if stage:
                stages[stage] = count
        
        return stages
    
    def get_attack_paths(self, limit: int = 30) -> List[Dict]:
        """Get attack paths for map."""
        db = SessionLocal()
        try:
            day_ago = datetime.utcnow() - timedelta(hours=24)
            return self._get_attack_paths(db, day_ago)[:limit]
        finally:
            db.close()
    
    def get_kill_chain(self) -> Dict:
        """Get kill chain stages."""
        db = SessionLocal()
        try:
            day_ago = datetime.utcnow() - timedelta(hours=24)
            return self._get_kill_chain_stages(db, day_ago)
        finally:
            db.close()
    
    def get_timeline(self, hours: int = 24) -> List[Dict]:
        """Get alerts grouped by hour."""
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            hour_ago = now - timedelta(hours=hours)
            
            results = []
            for i in range(hours):
                hour_start = hour_ago + timedelta(hours=i)
                hour_end = hour_start + timedelta(hours=1)
                count = db.query(func.count(Alert.id)).filter(
                    and_(Alert.timestamp >= hour_start, Alert.timestamp < hour_end)
                ).scalar() or 0
                results.append({'hour': i, 'count': count})
            
            return results
        finally:
            db.close()


_stats_aggregator: Optional[StatsAggregator] = None


def get_stats_aggregator() -> StatsAggregator:
    """Get singleton stats aggregator."""
    global _stats_aggregator
    if _stats_aggregator is None:
        _stats_aggregator = StatsAggregator()
    return _stats_aggregator