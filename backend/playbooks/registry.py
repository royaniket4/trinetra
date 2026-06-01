"""Built-in SOAR playbook definitions."""

from datetime import datetime, timedelta

BUILTIN_PLAYBOOKS = [
    {
        "id": "brute_force_response",
        "name": "Brute Force Response",
        "description": "Automated response to detected brute force attacks. Blocks source IP and disables affected accounts.",
        "trigger_conditions": {
            "rule_names": ["Brute Force Detection"],
            "min_severity": 4,
        },
        "steps": [
            {
                "order": 1,
                "action_type": "block_ip",
                "target_from": "source_ip",
                "label": "Block Source IP",
                "description": "Block the attacking IP address at the firewall",
                "requires_approval": False,
            },
            {
                "order": 2,
                "action_type": "disable_user",
                "target_from": "username",
                "label": "Disable Compromised Account",
                "description": "Disable the targeted user account pending investigation",
                "requires_approval": True,
            },
            {
                "order": 3,
                "action_type": "notify",
                "target": "soc-team",
                "label": "Notify SOC Team",
                "description": "Send alert notification to SOC team channel",
                "requires_approval": False,
            },
        ],
    },
    {
        "id": "ransomware_containment",
        "name": "Ransomware Containment",
        "description": "Immediate containment actions for suspected ransomware activity. Isolates endpoints and blocks C2 communications.",
        "trigger_conditions": {
            "rule_names": ["Suspicious File Download"],
            "min_severity": 5,
        },
        "steps": [
            {
                "order": 1,
                "action_type": "isolate_endpoint",
                "target_from": "source_ip",
                "label": "Isolate Affected Endpoint",
                "description": "Immediately isolate the compromised endpoint from the network",
                "requires_approval": False,
            },
            {
                "order": 2,
                "action_type": "block_ip",
                "target_from": "dest_ip",
                "label": "Block C2 IP",
                "description": "Block the command & control server IP address",
                "requires_approval": False,
            },
            {
                "order": 3,
                "action_type": "quarantine_file",
                "target_from": "evidence_hash",
                "label": "Quarantine Suspicious File",
                "description": "Quarantine the detected malicious file for analysis",
                "requires_approval": True,
            },
            {
                "order": 4,
                "action_type": "notify",
                "target": "soc-team",
                "label": "Escalate to SOC Lead",
                "description": "Notify SOC lead for manual investigation",
                "requires_approval": False,
            },
        ],
    },
    {
        "id": "lateral_movement_response",
        "name": "Lateral Movement Response",
        "description": "Response to detected lateral movement. Disables compromised accounts and blocks internal communication paths.",
        "trigger_conditions": {
            "rule_names": ["PowerShell Encoded Command", "Credential Dumping Indicators"],
            "min_severity": 4,
        },
        "steps": [
            {
                "order": 1,
                "action_type": "disable_user",
                "target_from": "username",
                "label": "Disable Affected Accounts",
                "description": "Disable all user accounts associated with the compromise",
                "requires_approval": True,
            },
            {
                "order": 2,
                "action_type": "isolate_endpoint",
                "target_from": "source_ip",
                "label": "Isolate Source Endpoint",
                "description": "Isolate the endpoint from which lateral movement originated",
                "requires_approval": False,
            },
            {
                "order": 3,
                "action_type": "block_ip",
                "target_from": "dest_ip",
                "label": "Block Lateral Movement Path",
                "description": "Block network communication between compromised systems",
                "requires_approval": True,
            },
            {
                "order": 4,
                "action_type": "notify",
                "target": "soc-team",
                "label": "Incident Escalation",
                "description": "Escalate to incident response team",
                "requires_approval": False,
            },
        ],
    },
    {
        "id": "sql_injection_response",
        "name": "SQL Injection Response",
        "description": "Response to SQL injection attempts. Blocks attacker IP and triggers WAF rule update.",
        "trigger_conditions": {
            "rule_names": ["SQL Injection Attempt"],
            "min_severity": 3,
        },
        "steps": [
            {
                "order": 1,
                "action_type": "block_ip",
                "target_from": "source_ip",
                "label": "Block Attacker IP",
                "description": "Block the attacking IP at the WAF/firewall",
                "requires_approval": False,
            },
            {
                "order": 2,
                "action_type": "notify",
                "target": "app-team",
                "label": "Notify Application Team",
                "description": "Notify app team to review and patch vulnerable endpoints",
                "requires_approval": False,
            },
        ],
    },
    {
        "id": "port_scan_response",
        "name": "Port Scan Response",
        "description": "Automated response to reconnaissance activity. Blocks scanning IP and enables rate limiting.",
        "trigger_conditions": {
            "rule_names": ["Port Scan Detected"],
            "min_severity": 3,
        },
        "steps": [
            {
                "order": 1,
                "action_type": "block_ip",
                "target_from": "source_ip",
                "label": "Block Scanning IP",
                "description": "Block the IP address performing the port scan",
                "requires_approval": False,
            },
        ],
    },
    {
        "id": "reverse_shell_response",
        "name": "Reverse Shell Response",
        "description": "Immediate response to detected reverse shell activity. Isolates compromised system and kills malicious processes.",
        "trigger_conditions": {
            "rule_names": ["Reverse Shell Signature"],
            "min_severity": 5,
        },
        "steps": [
            {
                "order": 1,
                "action_type": "isolate_endpoint",
                "target_from": "source_ip",
                "label": "Isolate Compromised System",
                "description": "Immediately isolate the compromised system from the network",
                "requires_approval": False,
            },
            {
                "order": 2,
                "action_type": "block_ip",
                "target_from": "dest_ip",
                "label": "Block C2 Server",
                "description": "Block the command and control server IP",
                "requires_approval": False,
            },
            {
                "order": 3,
                "action_type": "disable_user",
                "target_from": "username",
                "label": "Suspend User Account",
                "description": "Suspend the user account that initiated the reverse shell",
                "requires_approval": True,
            },
            {
                "order": 4,
                "action_type": "notify",
                "target": "soc-team",
                "label": "Critical Alert - SOC",
                "description": "Immediately notify SOC team of critical reverse shell detection",
                "requires_approval": False,
            },
        ],
    },
]


def list_playbooks():
    """Return all registered playbooks."""
    return BUILTIN_PLAYBOOKS


def get_playbook(playbook_id: str):
    """Get a playbook by ID."""
    for pb in BUILTIN_PLAYBOOKS:
        if pb["id"] == playbook_id:
            return pb
    return None


def find_matching_playbooks(alert: dict):
    """Find playbooks that match an alert's conditions."""
    matches = []
    for pb in BUILTIN_PLAYBOOKS:
        conditions = pb["trigger_conditions"]
        rule_match = alert.get("rule_name") in conditions.get("rule_names", [])
        severity_match = alert.get("severity", 1) >= conditions.get("min_severity", 1)
        if rule_match and severity_match:
            matches.append(pb)
    return matches
