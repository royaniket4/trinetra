import json
import logging
import os
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class MitreMapper:
    """Service for mapping detection rules to MITRE ATT&CK techniques."""
    
    def __init__(self):
        self._mappings: Dict = {}
        self._all_tactics: List[Dict] = []
        self._load_mitre_data()
    
    def _load_mitre_data(self) -> None:
        """Load MITRE mapping data from JSON file."""
        try:
            data_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'mitre_mapping.json'
            )
            with open(data_file, 'r') as f:
                data = json.load(f)
                self._mappings = data.get('mappings', {})
                self._all_tactics = data.get('all_tactics', [])
                logger.info(f"Loaded {len(self._mappings)} MITRE mappings")
        except Exception as e:
            logger.error(f"Failed to load MITRE data: {e}")
            self._mappings = {}
            self._all_tactics = []
    
    def get_mitre(self, rule_name: str) -> Optional[Dict]:
        """
        Get MITRE mapping for a detection rule.
        
        Args:
            rule_name: The name of the detection rule
            
        Returns:
            Dict with tactic, tactic_name, technique, technique_name, description
            or None if not found
        """
        rule_key = self._get_rule_key(rule_name)
        
        if rule_key in self._mappings:
            mapping = self._mappings[rule_key]
            return {
                'tactic': mapping.get('tactic'),
                'tactic_name': mapping.get('tactic_name'),
                'technique': mapping.get('technique'),
                'technique_name': mapping.get('technique_name'),
                'description': mapping.get('description'),
                'severity': mapping.get('severity'),
                'confidence': mapping.get('confidence'),
            }
        
        return None
    
    def _get_rule_key(self, rule_name: str) -> str:
        """Convert rule name to mapping key."""
        rule_lower = rule_name.lower().replace(' ', '_').replace('-', '_')
        
        key_mapping = {
            'brute_force': 'brute_force',
            'brute_force_detection': 'brute_force',
            'successful_login_after_bruteforce': 'successful_login_after_bruteforce',
            'successful_login_after_brute_force': 'successful_login_after_bruteforce',
            'powershell_encoded': 'powershell_encoded',
            'powershell_encoded_command': 'powershell_encoded',
            'suspicious_download': 'suspicious_download',
            'suspicious_file_download': 'suspicious_download',
            'privilege_escalation': 'privilege_escalation',
            'privilege_escalation_attempt': 'privilege_escalation',
            'credential_dumping': 'credential_dumping',
            'credential_dumping_indicators': 'credential_dumping',
            'lateral_movement': 'lateral_movement',
            'lateral_movement_detected': 'lateral_movement',
            'data_exfiltration': 'data_exfiltration',
            'potential_data_exfiltration': 'data_exfiltration',
            'port_scan': 'port_scan',
            'port_scan_detected': 'port_scan',
            'sql_injection': 'sql_injection',
            'sql_injection_attempt': 'sql_injection',
            'reverse_shell': 'reverse_shell',
            'reverse_shell_signature': 'reverse_shell',
            'ransomware': 'ransomware',
            'ransomware_activity': 'ransomware',
        }
        
        return key_mapping.get(rule_lower, rule_lower)
    
    def list_all_techniques(self) -> List[Dict]:
        """Get list of all MITRE techniques."""
        techniques = []
        for key, mapping in self._mappings.items():
            techniques.append({
                'rule_key': key,
                'rule_name': mapping.get('rule_name'),
                'tactic': mapping.get('tactic'),
                'tactic_name': mapping.get('tactic_name'),
                'technique': mapping.get('technique'),
                'technique_name': mapping.get('technique_name'),
            })
        return techniques
    
    def get_tactic_by_id(self, tactic_id: str) -> Optional[str]:
        """Get tactic name by ID."""
        for tactic in self._all_tactics:
            if tactic.get('id') == tactic_id:
                return tactic.get('name')
        return None


_mitre_mapper_instance: Optional[MitreMapper] = None


def get_mitre_mapper() -> MitreMapper:
    """Get singleton MitreMapper instance."""
    global _mitre_mapper_instance
    if _mitre_mapper_instance is None:
        _mitre_mapper_instance = MitreMapper()
    return _mitre_mapper_instance


def get_mitre(rule_name: str) -> Optional[Dict]:
    """Convenience function to get MITRE mapping."""
    return get_mitre_mapper().get_mitre(rule_name)


def list_all_techniques() -> List[Dict]:
    """Convenience function to list all techniques."""
    return get_mitre_mapper().list_all_techniques()