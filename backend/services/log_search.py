"""Log search engine with Splunk-compatible search syntax."""

import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func

from backend.models.log import Log
from backend.models.alert import Alert

logger = logging.getLogger(__name__)


class LogSearchParser:
    """Parses Splunk-like search syntax into SQL filters.
    
    Supports:
    - field:value exact match
    - field="value with spaces"
    - "free text" search
    - AND, OR, NOT operators
    - sourcetype=*, source_ip=192.168.1.*
    - earliest=-24h, latest=now
    - | stats count by field
    - | top field limit=10
    """

    def __init__(self):
        self.field_map = {
            "source_ip": Log.source_ip,
            "dest_ip": Log.dest_ip,
            "username": Log.username,
            "event_type": Log.event_type,
            "sourcetype": Log.sourcetype,
            "host": Log.host,
            "severity": Alert.severity,
            "rule_name": Alert.rule_name,
        }

    def parse(self, query: str) -> Tuple[Dict[str, Any], str]:
        """Parse search query into filters and determine query type."""
        filters = {
            "text_terms": [],
            "field_filters": {},
            "time_range": {"earliest": "-24h", "latest": "now"},
            "limit": 100,
            "offset": 0,
        }

        query = query.strip()
        parts = re.findall(r'[\w\.\*:\/\-@=]+|"[^"]*"|\|\s*\w+.*', query)

        pipeline = []
        main_query = []

        in_pipeline = False
        for part in parts:
            if part.startswith("|"):
                in_pipeline = True
                pipeline.append(part[1:].strip())
            elif in_pipeline:
                pipeline[-1] += " " + part
            else:
                main_query.append(part)

        for token in main_query:
            token = token.strip()
            if not token:
                continue

            field_match = re.match(r'(\w+):(.+)', token)
            if field_match:
                field, value = field_match.group(1), field_match.group(2)
                value = value.strip('"')
                if '*' in value:
                    filters["field_filters"][field] = {"type": "wildcard", "value": value.replace('*', '%')}
                else:
                    filters["field_filters"][field] = {"type": "exact", "value": value}
            elif '=' in token and not token.startswith('"'):
                field_match = re.match(r'(\w+)=(.*)', token)
                if field_match:
                    field, value = field_match.group(1), field_match.group(2).strip('"')
                    if '*' in value:
                        filters["field_filters"][field] = {"type": "wildcard", "value": value.replace('*', '%')}
                    else:
                        filters["field_filters"][field] = {"type": "exact", "value": value}
                else:
                    filters["text_terms"].append(token.strip('"'))
            else:
                filters["text_terms"].append(token.strip('"'))

        for pipe in pipeline:
            if pipe.startswith("stats"):
                stats_match = re.match(r'stats\s+(\w+)\s+by\s+(\w+)', pipe)
                if stats_match:
                    filters["stats"] = {"function": stats_match.group(1), "by": stats_match.group(2)}
            elif pipe.startswith("top"):
                top_match = re.match(r'top\s+(\w+)(?:\s+limit=(\d+))?', pipe)
                if top_match:
                    filters["top"] = {"field": top_match.group(1), "limit": int(top_match.group(2) or 10)}
            elif pipe.startswith("sort"):
                sort_match = re.match(r'sort\s+(-?\w+)', pipe)
                if sort_match:
                    filters["sort"] = sort_match.group(1)
            elif pipe.startswith("fields"):
                fields_match = re.match(r'fields\s+([\w,\s]+)', pipe)
                if fields_match:
                    filters["fields"] = [f.strip() for f in fields_match.group(1).split(',')]
            elif pipe.startswith("head"):
                head_match = re.match(r'head\s+(\d+)', pipe)
                if head_match:
                    filters["limit"] = int(head_match.group(1))

        return filters, query


class LogSearchEngine:
    """Executes parsed log searches against the database."""

    def __init__(self, db: Session):
        self.db = db

    def search(self, query: str, include_alerts: bool = False) -> Dict[str, Any]:
        """Execute a search query and return results."""
        parser = LogSearchParser()
        filters, _ = parser.parse(query)

        # Default: search logs
        log_query = self.db.query(Log)
        alert_query = self.db.query(Alert) if include_alerts else None

        # Apply text search
        if filters.get("text_terms"):
            for term in filters["text_terms"]:
                term_pattern = f"%{term}%"
                log_query = log_query.filter(
                    or_(
                        Log.raw_log.ilike(term_pattern),
                        Log.source_ip.ilike(term_pattern),
                        Log.dest_ip.ilike(term_pattern),
                        Log.username.ilike(term_pattern),
                        Log.event_type.ilike(term_pattern),
                    )
                )

        # Apply field filters
        for field, filter_def in filters.get("field_filters", {}).items():
            col = self._get_column(field, is_alert=False)
            if col is not None:
                if filter_def["type"] == "exact":
                    log_query = log_query.filter(col == filter_def["value"])
                elif filter_def["type"] == "wildcard":
                    log_query = log_query.filter(col.ilike(filter_def["value"]))

        # Apply time range
        earliest = self._parse_time(filters.get("time_range", {}).get("earliest", "-24h"))
        if earliest:
            log_query = log_query.filter(Log.timestamp >= earliest)

        # Apply defaults
        log_query = log_query.order_by(desc(Log.timestamp))
        total = log_query.count()
        results = log_query.limit(filters.get("limit", 100)).offset(filters.get("offset", 0)).all()

        return {
            "query": query,
            "total": total,
            "returned": len(results),
            "results": [
                {
                    "id": r.id,
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                    "source_ip": r.source_ip,
                    "dest_ip": r.dest_ip,
                    "username": r.username,
                    "event_type": r.event_type,
                    "sourcetype": r.sourcetype,
                    "host": r.host,
                    "raw_log": r.raw_log[:500] if r.raw_log else None,
                    "country": r.country,
                }
                for r in results
            ],
            "took_ms": 0,
        }

    def _get_column(self, field: str, is_alert: bool = False):
        """Get SQLAlchemy column for a field name."""
        field_map = {
            "source_ip": Log.source_ip,
            "dest_ip": Log.dest_ip,
            "username": Log.username,
            "event_type": Log.event_type,
            "sourcetype": Log.sourcetype,
            "host": Log.host,
            "country": Log.country,
        }
        if is_alert:
            field_map.update({
                "severity": Alert.severity,
                "rule_name": Alert.rule_name,
                "status": Alert.status,
            })
        return field_map.get(field)

    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """Parse time expressions like -24h, -7d, -30m, now."""
        now = datetime.utcnow()
        if not time_str or time_str == "now":
            return None
        match = re.match(r'(-?\d+)([hdwms])', time_str)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            if unit == 'h':
                return now - timedelta(hours=abs(value))
            elif unit == 'd':
                return now - timedelta(days=abs(value))
            elif unit == 'm':
                return now - timedelta(minutes=abs(value))
            elif unit == 'w':
                return now - timedelta(weeks=abs(value))
        return None

    def get_field_values(self, field: str, search: str = None, limit: int = 20) -> List[str]:
        """Get distinct values for a field (for autocomplete)."""
        col = self._get_column(field)
        if col is None:
            return []
        query = self.db.query(col).distinct()
        if search:
            query = query.filter(col.ilike(f"%{search}%"))
        return [r[0] for r in query.limit(limit).all() if r[0]]
