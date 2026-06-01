import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from backend.services.geo_lookup import get_geo_lookup

logger = logging.getLogger(__name__)


class LogNormalizer:
    """Normalize various log formats to a standard schema."""
    
    def __init__(self):
        self.geo_lookup = get_geo_lookup()
        
        self.windows_patterns = {
            'event_id': r'EventID:\s*(\d+)',
            'logon_type': r'LogonType:\s*(\d+)',
            'ip_address': r'IP Address:\s*([\d.]+)',
            'username': r'Account Name:\s*(\S+)',
        }
        
        self.linux_patterns = {
            'ip': r'(\d+\.\d+\.\d+\.\d+)',
            'username': r'user=(\S+)',
            'service': r'service=(\S+)',
        }
        
        self.apache_patterns = {
            'ip': r'(\d+\.\d+\.\d+\.\d+).*\[.*\]',
            'method': r'"(GET|POST|PUT|DELETE)',
            'path': r'"\S+\s+(\S+)',
            'status': r'\s+(\d{3})\s+',
        }
    
    def normalize(self, log_data) -> Dict[str, Any]:
        """Normalize a log entry to the standard schema."""
        timestamp = log_data.timestamp or datetime.utcnow()
        
        log_source = getattr(log_data, 'log_format', None) or 'custom'
        
        source_ip = log_data.source_ip
        if not source_ip:
            source_ip = self._extract_ip(log_data.raw_log, log_source)
        
        geo_data = None
        if source_ip and not getattr(log_data, 'geo_country', None):
            geo_data = self.geo_lookup.lookup(source_ip)
        
        severity = log_data.severity
        if not severity:
            severity = self._infer_severity(log_data.event_type, log_data.raw_log)
        
        event_type = log_data.event_type
        if not event_type:
            event_type = self._infer_event_type(log_data.raw_log, log_source)
        
        username = log_data.username
        if not username:
            username = self._extract_username(log_data.raw_log, log_source)
        
        return {
            'timestamp': timestamp,
            'source_ip': source_ip,
            'dest_ip': log_data.dest_ip,
            'username': username,
            'event_type': event_type,
            'severity': severity,
            'raw_log': log_data.raw_log,
            'geo_country': geo_data['country'] if geo_data else getattr(log_data, 'geo_country', None),
            'geo_lat': geo_data['lat'] if geo_data else getattr(log_data, 'geo_lat', None),
            'geo_lon': geo_data['lon'] if geo_data else getattr(log_data, 'geo_lon', None),
            'log_source': log_source,
        }
    
    def _extract_ip(self, raw_log: str, log_source: str) -> Optional[str]:
        """Extract IP address from raw log."""
        patterns = {
            'windows': r'IP Address:\s*([\d.]+)',
            'linux': r'(\d+\.\d+\.\d+\.\d+)',
            'apache': r'(\d+\.\d+\.\d+\.\d+)',
            'nginx': r'(\d+\.\d+\.\d+\.\d+)',
            'firewall': r'Src:\s*([\d.]+)',
        }
        
        pattern = patterns.get(log_source.lower())
        if pattern:
            match = re.search(pattern, raw_log, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_username(self, raw_log: str, log_source: str) -> Optional[str]:
        """Extract username from raw log."""
        patterns = {
            'windows': r'Account Name:\s*(\S+)',
            'linux': r'user=(\S+)',
            'apache': r'"(\S+)@',
        }
        
        pattern = patterns.get(log_source.lower())
        if pattern:
            match = re.search(pattern, raw_log, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _infer_event_type(self, raw_log: str, log_source: str) -> str:
        """Infer event type from raw log."""
        raw_lower = raw_log.lower()
        
        if 'failed' in raw_lower or 'failure' in raw_lower:
            return 'authentication_failed'
        elif 'success' in raw_lower or 'accepted' in raw_lower:
            return 'authentication_success'
        elif 'powershell' in raw_lower:
            return 'powershell_execution'
        elif 'cmd.exe' in raw_lower or 'cmd ' in raw_lower:
            return 'command_execution'
        elif 'download' in raw_lower or '.exe' in raw_lower:
            return 'file_download'
        elif 'sudo' in raw_lower:
            return 'privilege_escalation'
        elif 'smb' in raw_lower or '445' in raw_lower:
            return 'smb_access'
        elif 'rdp' in raw_lower or '3389' in raw_lower:
            return 'rdp_access'
        
        return 'unknown'
    
    def _infer_severity(self, event_type: str, raw_log: str) -> int:
        """Infer severity level from event type and content."""
        raw_lower = raw_log.lower()
        
        high_severity_keywords = ['critical', 'failed', 'attack', 'malware', 'ransomware']
        medium_severity_keywords = ['warning', 'suspicious', 'unusual', 'error']
        
        if any(kw in raw_lower for kw in high_severity_keywords):
            return 4
        elif any(kw in raw_lower for kw in medium_severity_keywords):
            return 3
        elif 'failed' in raw_lower:
            return 2
        
        event_severity_map = {
            'authentication_failed': 3,
            'authentication_success': 1,
            'powershell_execution': 3,
            'command_execution': 2,
            'file_download': 3,
            'privilege_escalation': 4,
            'smb_access': 3,
            'rdp_access': 3,
        }
        
        return event_severity_map.get(event_type, 1)