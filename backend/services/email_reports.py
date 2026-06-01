"""Email Notification & Report Scheduling Engine."""

import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.services.reports import ReportEngine

logger = logging.getLogger(__name__)


class EmailEngine:
    """Send email notifications and scheduled reports."""

    def __init__(self, smtp_host: str = "localhost", smtp_port: int = 25,
                 smtp_user: str = "", smtp_pass: str = "", use_tls: bool = False,
                 from_addr: str = "trinetra@localhost"):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.use_tls = use_tls
        self.from_addr = from_addr

    def send_alert_notification(self, to_email: str, alert_data: dict):
        """Send alert notification email."""
        subject = f"[Trinetra] {alert_data.get('severity', 3)} Alert: {alert_data.get('rule_name', 'Unknown')}"
        body = f"""
Alert triggered in Trinetra SIEM

Rule: {alert_data.get('rule_name', 'N/A')}
Severity: {alert_data.get('severity', 'N/A')}
Source IP: {alert_data.get('source_ip', 'N/A')}
Timestamp: {alert_data.get('timestamp', datetime.utcnow().isoformat())}

View in Trinetra: http://localhost:5173/alerts
        """
        self._send(to_email, subject, body)

    def send_daily_report(self, to_email: str, db: Session):
        """Send daily SOC brief via email."""
        engine = ReportEngine(db)
        brief = engine.generate_daily_brief()

        subject = f"Trinetra Daily SOC Brief - {datetime.utcnow().strftime('%Y-%m-%d')}"
        body = f"""
TRINETRA DAILY SOC BRIEF
{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

SUMMARY
- Total Alerts (24h): {brief['summary']['total_alerts']}
- Critical: {brief['summary']['critical']}
- High: {brief['summary']['high']}
- Log Volume: {brief['summary']['log_volume']}

TOP ALERT RULES
{chr(10).join(f'  - {r}' for r in brief.get('top_alert_rules', ['None']))}

TOP SOURCE IPS
{chr(10).join(f'  - {ip}' for ip in brief.get('top_source_ips', ['None']))}

--
Trinetra SIEM - AI-Powered Cyber Defense
        """
        csv_data = engine.generate_alerts_csv(24)
        self._send(to_email, subject, body, attachments=[("alerts_24h.csv", csv_data)])

    def send_threat_brief(self, to_email: str, db: Session):
        """Send threat brief via email."""
        engine = ReportEngine(db)
        brief = engine.generate_threat_brief()

        subject = f"Trinetra Threat Brief - {datetime.utcnow().strftime('%Y-%m-%d')}"
        body = f"""
TRINETRA THREAT BRIEF
{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

ACTIVE IOCs: {brief.get('active_iocs', 0)}
NEW THREATS TODAY: {brief.get('new_threats_today', 0)}

TOP ATTACK VECTORS
{chr(10).join(f'  - {v}' for v in brief.get('top_attack_vectors', ['None']))}

RECOMMENDATIONS
{chr(10).join(f'  - {r}' for r in brief.get('recommendations', ['None']))}

--
Trinetra SIEM - AI-Powered Cyber Defense
        """
        self._send(to_email, subject, body)

    def _send(self, to_email: str, subject: str, body: str, attachments: List[tuple] = None):
        """Internal send method."""
        try:
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.from_addr
            msg['To'] = to_email
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            if attachments:
                for filename, data in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(data.encode('utf-8'))
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user:
                    server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")


class ReportScheduler:
    """Simple in-memory report scheduler."""

    def __init__(self, db: Session):
        self.db = db
        self.schedules = []

    def add_schedule(self, name: str, report_type: str, cron_expr: str, recipients: List[str]):
        """Add a report schedule."""
        self.schedules.append({
            "name": name,
            "type": report_type,
            "cron": cron_expr,
            "recipients": recipients,
            "enabled": True,
        })
        return {"status": "scheduled", "schedule": name}

    def list_schedules(self):
        return self.schedules

    def remove_schedule(self, name: str):
        self.schedules = [s for s in self.schedules if s["name"] != name]
        return {"status": "removed"}
