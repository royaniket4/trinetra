"""Webhook notification engine - Slack, Email, Teams, generic webhooks."""

import json
import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.models.webhook import Webhook

logger = logging.getLogger(__name__)


class WebhookEngine:
    """Send notifications via configured webhooks."""

    def __init__(self, db: Session):
        self.db = db

    def dispatch(self, event_type: str, payload: Dict[str, Any]) -> int:
        """Dispatch an event to all matching webhooks."""
        hooks = self.db.query(Webhook).filter(
            Webhook.event_type == event_type,
            Webhook.is_active == True,
        ).all()

        sent = 0
        for hook in hooks:
            try:
                self._send(hook, payload)
                hook.last_triggered = datetime.utcnow()
                sent += 1
            except Exception as e:
                logger.error(f"Webhook {hook.name} ({hook.provider}) failed: {e}")

        self.db.commit()
        return sent

    def _send(self, hook: Webhook, payload: Dict[str, Any]):
        """Send to a specific webhook based on provider type."""
        import httpx

        if hook.provider == "slack":
            message = self._format_slack(payload)
        elif hook.provider == "teams":
            message = self._format_teams(payload)
        elif hook.provider == "email":
            message = payload
        else:
            message = payload

        httpx.post(hook.url, json=message, timeout=10.0)

    def _format_slack(self, payload: Dict) -> Dict:
        """Format payload as Slack message."""
        severity_colors = {5: "#ff0000", 4: "#ff6600", 3: "#ffcc00"}
        color = severity_colors.get(payload.get("severity"), "#36a64f")

        return {
            "attachments": [{
                "color": color,
                "title": payload.get("title", "Trinetra Alert"),
                "text": payload.get("message", ""),
                "fields": [
                    {"title": "Alert ID", "value": payload.get("alert_id", "N/A"), "short": True},
                    {"title": "Source IP", "value": payload.get("source_ip", "N/A"), "short": True},
                    {"title": "Severity", "value": str(payload.get("severity", "N/A")), "short": True},
                ],
                "footer": "Trinetra SIEM",
                "ts": int(datetime.utcnow().timestamp()),
            }]
        }

    def _format_teams(self, payload: Dict) -> Dict:
        """Format payload as Teams adaptive card."""
        return {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "body": [
                        {"type": "TextBlock", "text": payload.get("title", "Trinetra Alert"), "weight": "bolder", "size": "large"},
                        {"type": "TextBlock", "text": payload.get("message", ""), "wrap": True},
                        {"type": "FactSet", "facts": [
                            {"title": "Alert ID", "value": str(payload.get("alert_id", "N/A"))},
                            {"title": "Source IP", "value": str(payload.get("source_ip", "N/A"))},
                            {"title": "Severity", "value": str(payload.get("severity", "N/A"))},
                        ]},
                    ],
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.4",
                },
            }]
        }

    def create_hook(self, name: str, url: str, event_type: str, provider: str = "webhook") -> Webhook:
        """Register a new webhook."""
        hook = Webhook(name=name, url=url, event_type=event_type, provider=provider)
        self.db.add(hook)
        self.db.commit()
        self.db.refresh(hook)
        return hook

    def test_hook(self, webhook_id: int) -> bool:
        """Test a webhook by sending a test payload."""
        hook = self.db.query(Webhook).filter(Webhook.id == webhook_id).first()
        if not hook:
            return False
        try:
            self._send(hook, {"title": "Trinetra Test", "message": "This is a test notification", "severity": 3})
            return True
        except Exception as e:
            logger.error(f"Test failed: {e}")
            return False
