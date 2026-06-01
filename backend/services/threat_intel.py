"""Threat Intelligence engine - IOC matching, feed imports, reputation scoring."""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from backend.models.log import Log
from backend.models.alert import Alert

logger = logging.getLogger(__name__)


class ThreatIntelEngine:
    """Threat intelligence feed processing and IOC matching."""

    def __init__(self, db: Session):
        self.db = db
        self.iocs = {
            "ip": [],
            "domain": [],
            "hash": [],
            "url": [],
        }

    def load_iocs_from_db(self):
        """Load IOCs from the threat_intel table (if exists)."""
        try:
            from backend.models.threat_intel import ThreatIntel
            items = self.db.query(ThreatIntel).filter(ThreatIntel.is_active == True).all()
            self.iocs = {"ip": [], "domain": [], "hash": [], "url": []}
            for item in items:
                ioc_type = self._classify_ioc(item.indicator)
                if ioc_type and ioc_type in self.iocs:
                    self.iocs[ioc_type].append(item.indicator)
        except Exception as e:
            logger.debug(f"No threat_intel table yet: {e}")

    def load_builtin_iocs(self):
        """Load built-in known bad indicators."""
        self.iocs["ip"].extend([
            "185.220.101.0/24",
            "91.121.87.0/24",
            "5.254.113.0/24",
        ])
        known_malicious_hashes = [
            "a3b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5",
            "e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
        ]
        self.iocs["hash"].extend(known_malicious_hashes)

    def _classify_ioc(self, ioc: str) -> Optional[str]:
        """Classify an IOC as ip, domain, hash, or url."""
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(/\d{1,2})?$', ioc):
            return "ip"
        if re.match(r'^[a-fA-F0-9]{32,64}$', ioc):
            return "hash"
        if re.match(r'^https?://', ioc):
            return "url"
        if re.match(r'^[\w\.-]+\.[a-zA-Z]{2,}$', ioc):
            return "domain"
        return None

    def check_log(self, log: Log) -> Optional[Dict]:
        """Check a single log against IOCs."""
        if not self.iocs["ip"] and not self.iocs["hash"]:
            return None

        raw = (log.raw_log or "").lower()

        matched_ip = None
        if log.source_ip:
            for ioc_ip in self.iocs["ip"]:
                if ioc_ip.endswith("/24"):
                    network = ioc_ip.split("/")[0]
                    network_parts = network.split(".")[:3]
                    ip_parts = log.source_ip.split(".")
                    if ip_parts[:3] == network_parts:
                        matched_ip = ioc_ip
                        break
                elif log.source_ip == ioc_ip:
                    matched_ip = ioc_ip
                    break

        matched_hash = None
        for ioc_hash in self.iocs["hash"]:
            if ioc_hash.lower() in raw:
                matched_hash = ioc_hash
                break

        if matched_ip or matched_hash:
            return {
                "log_id": log.id,
                "source_ip": log.source_ip,
                "matched_iocs": {
                    "ip": matched_ip,
                    "hash": matched_hash,
                },
                "threat_score": 8 if matched_ip else 6,
                "timestamp": datetime.utcnow(),
            }
        return None

    def get_threat_intel_summary(self) -> Dict:
        """Get threat intel dashboard summary."""
        self.load_iocs_from_db()
        if not any(self.iocs.values()):
            self.load_builtin_iocs()

        total_iocs = sum(len(v) for v in self.iocs.values())

        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        ioc_matches = self.db.query(Alert).filter(
            Alert.rule_name == "IOC Match",
            Alert.timestamp >= recent_cutoff,
        ).count()

        return {
            "total_iocs": total_iocs,
            "by_type": {k: len(v) for k, v in self.iocs.items()},
            "matches_24h": ioc_matches,
            "feed_status": "active",
            "last_updated": datetime.utcnow().isoformat(),
        }


def fetch_alienvault_otx() -> List[str]:
    """Fetch IOCs from AlienVault OTX (mock - requires API key)."""
    return []


def fetch_virustotal(api_key: str, ip: str) -> Dict:
    """Mock VirusTotal lookup."""
    return {"ip": ip, "malicious": 0, "suspicious": 0, "harmless": 10}
