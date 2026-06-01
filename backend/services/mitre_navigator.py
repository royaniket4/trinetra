"""MITRE ATT&CK Navigator - Coverage mapping and visualization."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.alert import Alert

logger = logging.getLogger(__name__)


# Full MITRE ATT&CK Enterprise Matrix (v15)
MITRE_MATRIX = {
    "Reconnaissance": {
        "TA0043": {"name": "Active Scanning", "techniques": ["T1595"]},
        "TA0043": {"name": "Gather Victim Info", "techniques": ["T1592", "T1589", "T1590"]},
    },
    "Resource Development": {
        "TA0042": {"name": "Develop Capabilities", "techniques": ["T1587"]},
        "TA0042": {"name": "Obtain Capabilities", "techniques": ["T1588"]},
    },
    "Initial Access": {
        "TA0001": {"name": "Phishing", "techniques": ["T1566"]},
        "TA0001": {"name": "Exploit Public-Facing App", "techniques": ["T1190"]},
        "TA0001": {"name": "Valid Accounts", "techniques": ["T1078"]},
        "TA0001": {"name": "Drive-by Compromise", "techniques": ["T1189"]},
    },
    "Execution": {
        "TA0002": {"name": "Command & Scripting Interpreter", "techniques": ["T1059"]},
        "TA0002": {"name": "PowerShell", "techniques": ["T1059.001"]},
        "TA0002": {"name": "Native API", "techniques": ["T1106"]},
        "TA0002": {"name": "Windows Management Instrumentation", "techniques": ["T1047"]},
    },
    "Persistence": {
        "TA0003": {"name": "Account Manipulation", "techniques": ["T1098"]},
        "TA0003": {"name": "Create Account", "techniques": ["T1136"]},
        "TA0003": {"name": "Boot or Logon Autostart", "techniques": ["T1547"]},
    },
    "Privilege Escalation": {
        "TA0004": {"name": "Exploitation for Priv Esc", "techniques": ["T1068"]},
        "TA0004": {"name": "Access Token Manipulation", "techniques": ["T1134"]},
        "TA0004": {"name": "Process Injection", "techniques": ["T1055"]},
    },
    "Defense Evasion": {
        "TA0005": {"name": "Obfuscated Files or Info", "techniques": ["T1027"]},
        "TA0005": {"name": "Masquerading", "techniques": ["T1036"]},
        "TA0005": {"name": "Indicator Removal", "techniques": ["T1070"]},
        "TA0005": {"name": "Modify Registry", "techniques": ["T1112"]},
    },
    "Credential Access": {
        "TA0006": {"name": "Brute Force", "techniques": ["T1110"]},
        "TA0006": {"name": "OS Credential Dumping", "techniques": ["T1003"]},
        "TA0006": {"name": "Steal Web Session Cookie", "techniques": ["T1539"]},
    },
    "Discovery": {
        "TA0007": {"name": "Network Service Scanning", "techniques": ["T1046"]},
        "TA0007": {"name": "System Information Discovery", "techniques": ["T1082"]},
        "TA0007": {"name": "Account Discovery", "techniques": ["T1087"]},
    },
    "Lateral Movement": {
        "TA0008": {"name": "Remote Services", "techniques": ["T1021"]},
        "TA0008": {"name": "Lateral Tool Transfer", "techniques": ["T1570"]},
        "TA0008": {"name": "Internal Spearphishing", "techniques": ["T1534"]},
    },
    "Collection": {
        "TA0009": {"name": "Data from Local System", "techniques": ["T1005"]},
        "TA0009": {"name": "Input Capture", "techniques": ["T1056"]},
        "TA0009": {"name": "Screen Capture", "techniques": ["T1113"]},
    },
    "Command & Control": {
        "TA0011": {"name": "Application Layer Protocol", "techniques": ["T1071"]},
        "TA0011": {"name": "Web Protocols", "techniques": ["T1071.001"]},
        "TA0011": {"name": "DNS", "techniques": ["T1572"]},
    },
    "Exfiltration": {
        "TA0010": {"name": "Exfiltration Over C2", "techniques": ["T1041"]},
        "TA0010": {"name": "Scheduled Transfer", "techniques": ["T1029"]},
        "TA0010": {"name": "Data Transfer Size Limits", "techniques": ["T1030"]},
    },
    "Impact": {
        "TA0040": {"name": "Data Encrypted for Impact", "techniques": ["T1486"]},
        "TA0040": {"name": "Service Stop", "techniques": ["T1489"]},
        "TA0040": {"name": "Inhibit System Recovery", "techniques": ["T1490"]},
    },
}


class MitreNavigator:
    """Builds ATT&CK coverage data from alert history."""

    def __init__(self, db: Session):
        self.db = db

    def get_coverage(self, hours: int = 720) -> Dict[str, Any]:
        """Get full coverage matrix with detection status per technique."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        # Get all unique technique+tactic combinations from alerts
        alert_techniques = self.db.query(
            Alert.mitre_tactic,
            Alert.mitre_technique,
            func.count(Alert.id).label('count'),
            func.max(Alert.severity).label('max_severity'),
        ).filter(
            Alert.mitre_tactic.isnot(None),
            Alert.timestamp >= cutoff,
        ).group_by(Alert.mitre_tactic, Alert.mitre_technique).all()

        covered = {}
        for tactic, technique, count, max_sev in alert_techniques:
            if tactic not in covered:
                covered[tactic] = {}
            covered[tactic][technique] = {
                "alert_count": count,
                "max_severity": max_sev,
            }

        # Compare against full matrix to create coverage heatmap
        tactics = []
        total_techniques = 0
        covered_techniques = 0

        for tactic_name, tactic_data in MITRE_MATRIX.items():
            tactic_techniques = []
            for ta_id, sub_data in tactic_data.items():
                for tech_id in sub_data["techniques"]:
                    total_techniques += 1
                    is_covered = False
                    severity = 0
                    alert_count = 0

                    for ctactic, ctechs in covered.items():
                        if ctactic and ctactic.lower() == tactic_name.lower():
                            for ctech, cdata in ctechs.items():
                                if ctech == tech_id:
                                    is_covered = True
                                    severity = cdata["max_severity"]
                                    alert_count = cdata["alert_count"]
                                    break

                    if is_covered:
                        covered_techniques += 1

                    tactic_techniques.append({
                        "id": tech_id,
                        "name": sub_data["name"],
                        "covered": is_covered,
                        "severity": severity,
                        "alert_count": alert_count,
                    })

            coverage_pct = round((sum(1 for t in tactic_techniques if t["covered"]) / max(len(tactic_techniques), 1)) * 100, 1)
            tactics.append({
                "name": tactic_name,
                "ta_id": ta_id,
                "coverage_pct": coverage_pct,
                "techniques": tactic_techniques,
                "detected": sum(1 for t in tactic_techniques if t["covered"]),
                "total": len(tactic_techniques),
            })

        overall_pct = round((covered_techniques / max(total_techniques, 1)) * 100, 1)

        return {
            "overall_coverage_pct": overall_pct,
            "covered_techniques": covered_techniques,
            "total_techniques": total_techniques,
            "tactics": tactics,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_technique_detail(self, technique_id: str, hours: int = 720) -> Dict:
        """Get detailed info about a specific technique."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        alerts = self.db.query(Alert).filter(
            Alert.mitre_technique == technique_id,
            Alert.timestamp >= cutoff,
        ).order_by(Alert.timestamp.desc()).limit(20).all()

        return {
            "technique_id": technique_id,
            "total_alerts": len(alerts),
            "recent_alerts": [
                {
                    "id": a.id,
                    "alert_id": a.alert_id,
                    "rule_name": a.rule_name,
                    "severity": a.severity,
                    "source_ip": a.source_ip,
                    "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                }
                for a in alerts[:10]
            ],
        }

    def get_recommendations(self) -> List[Dict]:
        """Get recommendations for improving coverage."""
        coverage = self.get_coverage()
        recommendations = []

        for tactic in coverage["tactics"]:
            uncovered = [t for t in tactic["techniques"] if not t["covered"]]
            if len(uncovered) == tactic["total"]:
                recommendations.append({
                    "tactic": tactic["name"],
                    "priority": "high",
                    "message": f"No detection coverage for {tactic['name']}. Consider adding rules for: {', '.join(t['id'] for t in uncovered[:3])}",
                    "techniques_to_add": [t["id"] for t in uncovered[:5]],
                })
            elif len(uncovered) > 0:
                recommendations.append({
                    "tactic": tactic["name"],
                    "priority": "medium",
                    "message": f"Partial coverage ({tactic['coverage_pct']}%) for {tactic['name']}. Missing: {', '.join(t['id'] for t in uncovered[:3])}",
                    "techniques_to_add": [t["id"] for t in uncovered[:3]],
                })

        return sorted(recommendations, key=lambda r: 0 if r["priority"] == "high" else 1)
