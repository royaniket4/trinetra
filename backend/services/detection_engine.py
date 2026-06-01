import re
import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.models.log import Log
from backend.models.alert import Alert
from backend.websocket.manager import broadcast_alert
from backend.services.geo_lookup import get_geo_lookup
from backend.services.mitre_mapper import get_mitre_mapper

logger = logging.getLogger(__name__)


class DetectionEngine:
    """Rule-based detection engine with 12 detection rules."""
    
    def __init__(self, db: Session):
        self.db = db
        self.geo_lookup = get_geo_lookup()
        self.mitre_mapper = get_mitre_mapper()
        self._login_failures: Dict[str, List[datetime]] = {}
        self._network_connections: Dict[str, List[datetime]] = {}
        logger.info("DetectionEngine initialized")
    
    def _load_mitre_mapping(self) -> Dict[str, Dict]:
        """Load MITRE ATT&CK mapping."""
        return {
            'brute_force': {
                'tactic': 'Credential Access',
                'technique': 'T1110',
            },
            'successful_login_after_brute_force': {
                'tactic': 'Initial Access',
                'technique': 'T1078',
            },
            'powershell_encoded': {
                'tactic': 'Execution',
                'technique': 'T1059.001',
            },
            'suspicious_download': {
                'tactic': 'Initial Access',
                'technique': 'T1204',
            },
            'privilege_escalation': {
                'tactic': 'Privilege Escalation',
                'technique': 'T1068',
            },
            'credential_dumping': {
                'tactic': 'Credential Access',
                'technique': 'T1003',
            },
            'lateral_movement': {
                'tactic': 'Lateral Movement',
                'technique': 'T1021',
            },
            'data_exfiltration': {
                'tactic': 'Exfiltration',
                'technique': 'T1041',
            },
            'port_scan': {
                'tactic': 'Discovery',
                'technique': 'T1046',
            },
            'sql_injection': {
                'tactic': 'Initial Access',
                'technique': 'T1190',
            },
            'reverse_shell': {
                'tactic': 'Execution',
                'technique': 'T1059',
            },
            'ransomware': {
                'tactic': 'Impact',
                'technique': 'T1486',
            },
        }
    
    def analyze_log(self, log: Log) -> List[Alert]:
        """Analyze a log entry and generate alerts if rules match."""
        alerts = []
        
        try:
            if self._check_brute_force(log):
                logger.info("  -> Matched: brute_force")
                alert = self._create_alert('Brute Force Detection', 4, 'brute_force', log)
                alerts.append(alert)
            
            if self._check_powershell_encoded(log):
                logger.info("  -> Matched: powershell_encoded")
                alert = self._create_alert('PowerShell Encoded Command', 4, 'powershell_encoded', log)
                alerts.append(alert)
            
            if self._check_suspicious_download(log):
                logger.info("  -> Matched: suspicious_download")
                alert = self._create_alert('Suspicious File Download', 3, 'suspicious_download', log)
                alerts.append(alert)
            
            if self._check_privilege_escalation(log):
                logger.info("  -> Matched: privilege_escalation")
                alert = self._create_alert('Privilege Escalation Attempt', 5, 'privilege_escalation', log)
                alerts.append(alert)
            
            if self._check_credential_dumping(log):
                logger.info("  -> Matched: credential_dumping")
                alert = self._create_alert('Credential Dumping Indicators', 5, 'credential_dumping', log)
                alerts.append(alert)
            
            if self._check_lateral_movement(log):
                logger.info("  -> Matched: lateral_movement")
                alert = self._create_alert('Lateral Movement Detected', 4, 'lateral_movement', log)
                alerts.append(alert)
            
            if self._check_data_exfiltration(log):
                logger.info("  -> Matched: data_exfiltration")
                alert = self._create_alert('Potential Data Exfiltration', 5, 'data_exfiltration', log)
                alerts.append(alert)
            
            if self._check_port_scan(log):
                logger.info("  -> Matched: port_scan")
                alert = self._create_alert('Port Scan Detected', 3, 'port_scan', log)
                alerts.append(alert)
            
            if self._check_sql_injection(log):
                logger.info("  -> Matched: sql_injection")
                alert = self._create_alert('SQL Injection Attempt', 4, 'sql_injection', log)
                alerts.append(alert)
            
            if self._check_reverse_shell(log):
                logger.info("  -> Matched: reverse_shell")
                alert = self._create_alert('Reverse Shell Signature', 5, 'reverse_shell', log)
                alerts.append(alert)
            
            if self._check_ransomware(log):
                logger.info("  -> Matched: ransomware")
                alert = self._create_alert('Ransomware Activity', 5, 'ransomware', log)
                alerts.append(alert)
        except Exception as e:
            logger.error(f"Error in analyze_log: {e}", exc_info=True)
            return alerts
        
        for alert in alerts:
            try:
                self.db.add(alert)
                self.db.commit()
                self.db.refresh(alert)
                logger.info(f"  -> Alert saved: {alert.alert_id}")
            except Exception as e:
                logger.error(f"Error saving alert: {e}", exc_info=True)
        
        return alerts
    
    def _check_brute_force(self, log: Log) -> bool:
        """Check for brute force: 5+ failed logins in 60 seconds."""
        if 'failed' not in log.event_type.lower() and 'failure' not in log.raw_log.lower():
            return False
        
        key = log.source_ip or log.username
        if not key:
            return False
        
        now = datetime.utcnow()
        
        if key not in self._login_failures:
            self._login_failures[key] = []
        
        self._login_failures[key] = [
            t for t in self._login_failures[key]
            if now - t < timedelta(seconds=60)
        ]
        
        self._login_failures[key].append(now)
        
        if len(self._login_failures[key]) >= 5:
            return True
        
        return False
    
    def _check_powershell_encoded(self, log: Log) -> bool:
        """Check for PowerShell encoded commands."""
        raw_lower = log.raw_log.lower()
        patterns = [
            r'powershell.*-enc',
            r'powershell.*-encodedcommand',
            r'-enc\s+',
            r'frombase64string',
            r'encodedcommand',
            r'powershell.*-e\s+',
        ]
        return any(re.search(p, raw_lower) for p in patterns)
    
    def _check_suspicious_download(self, log: Log) -> bool:
        """Check for suspicious file downloads."""
        raw_lower = log.raw_log.lower()
        suspicious_exts = ['.exe', '.scr', '.bat', '.cmd', '.vbs', '.js', '.jar', '.ps1']
        download_keywords = ['download', 'get', 'fetch', 'wget', 'curl']
        
        return any(ext in raw_lower for ext in suspicious_exts) and \
               any(kw in raw_lower for kw in download_keywords)
    
    def _check_privilege_escalation(self, log: Log) -> bool:
        """Check for privilege escalation attempts."""
        raw_lower = log.raw_log.lower()
        patterns = [
            r'sudo\s+',
            r'chmod\s+4777',
            r'setuid',
            r'root\s+',
            r'admin\s+',
            r'become-root',
            r'wheel\s+',
        ]
        return any(re.search(p, raw_lower) for p in patterns)
    
    def _check_credential_dumping(self, log: Log) -> bool:
        """Check for credential dumping indicators."""
        raw_lower = log.raw_log.lower()
        patterns = [
            r'mimikatz',
            r'procdump',
            r'lsass',
            r'credential',
            r'pwdump',
            r'cachedump',
            r'sam\s+',
            r'reg\s+save.*sam',
        ]
        return any(re.search(p, raw_lower) for p in patterns)
    
    def _check_lateral_movement(self, log: Log) -> bool:
        """Check for lateral movement via SMB/RDP."""
        raw_lower = log.raw_log.lower()
        patterns = [
            r'smb://',
            r'\\\\.*\\c\$',
            r'445.*connect',
            r'rdp',
            r'3389',
            r'winrm',
            r'psexec',
            r'wmi',
        ]
        return any(re.search(p, raw_lower) for p in patterns)
    
    def _check_data_exfiltration(self, log: Log) -> bool:
        """Check for potential data exfiltration."""
        bytes_out = getattr(log, 'bytes_out', None)
        if bytes_out and bytes_out > 10000000:
            return True
        
        raw_lower = log.raw_log.lower()
        patterns = [
            r'exfil',
            r'transfer',
            r'upload',
            r'scp\s+',
            r'ftp\s+',
            r'tftp',
            r'dns\s+query.*large',
        ]
        return any(re.search(p, raw_lower) for p in patterns)
    
    def _check_port_scan(self, log: Log) -> bool:
        """Check for port scan activity."""
        raw_lower = log.raw_log.lower()
        patterns = [
            r'port\s+\d+',
            r'scan',
            r'nmap',
            r'-masscan',
            r'tcpdump',
        ]
        return any(re.search(p, raw_lower) for p in patterns) and \
               len(re.findall(r'\d+', log.raw_log)) > 5
    
    def _check_sql_injection(self, log: Log) -> bool:
        """Check for SQL injection patterns."""
        raw_lower = log.raw_log.lower()
        patterns = [
            r'union\s+select',
            r"';.*--",
            r'or\s+1\s*=\s*1',
            r'drop\s+table',
            r'exec\s*\(',
            r'execute\s*\(',
            r'union\s+all\s+select',
            r'1\s*=\s*1',
            r'<script>',
            r'javascript:',
        ]
        return any(re.search(p, raw_lower) for p in patterns)
    
    def _check_reverse_shell(self, log: Log) -> bool:
        """Check for reverse shell signatures."""
        raw_lower = log.raw_log.lower()
        patterns = [
            r'/bin/sh.*-i',
            r'bash.*-i',
            r'nc\s+-e',
            r'netcat.*-e',
            r'perl.*-e',
            r'python.*-c',
            r'php.*-r',
            r'sh\s+-i',
            r'/dev/tcp/',
            r'socket\.',
        ]
        return any(re.search(p, raw_lower) for p in patterns)
    
    def _check_ransomware(self, log: Log) -> bool:
        """Check for ransomware file patterns."""
        raw_lower = log.raw_log.lower()
        patterns = [
            r'\.locked',
            r'\.encrypted',
            r'ransom',
            r'locked\s+files',
            r'pay\s+bitcoin',
            r' Decrypt',
            r'filecoder',
            r'wyrm',
            r'locky',
            r'cerber',
            r'conti',
        ]
        return any(re.search(p, raw_lower) for p in patterns)
    
    def _create_alert(self, rule_name: str, severity: int, rule_key: str, log: Log) -> Alert:
        """Create an alert from a triggered rule."""
        mitre = self.mitre_mapper.get_mitre(rule_name)
        
        evidence_data = {
            'rule_key': rule_key,
            'rule_name': rule_name,
            'matched_log': log.raw_log[:200],
            'source_ip': log.source_ip,
            'username': log.username,
            'timestamp': log.timestamp.isoformat() if log.timestamp else None,
        }
        
        confidence = 0.75
        if mitre:
            confidence = mitre.get('confidence', 0.75)
        
        alert = Alert(
            alert_id=f"ALERT-{uuid.uuid4().hex[:8].upper()}",
            rule_name=rule_name,
            severity=severity,
            mitre_tactic=mitre.get('tactic') if mitre else None,
            mitre_technique=mitre.get('technique') if mitre else None,
            confidence=confidence,
            asset_impact='unknown',
            evidence=json.dumps(evidence_data),
            timestamp=datetime.utcnow(),
            source_ip=log.source_ip,
            dest_ip=log.dest_ip,
            username=log.username,
            status='open',
        )
        
        logger.info(f"Alert created: {alert.alert_id} - {rule_name} (severity: {severity})")
        
        return alert