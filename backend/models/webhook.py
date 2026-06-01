from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from backend.database import Base
from datetime import datetime


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    url = Column(String(500))
    event_type = Column(String(100), index=True)  # alert_created, incident_created, playbook_executed
    provider = Column(String(50))  # slack, email, teams, webhook
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
