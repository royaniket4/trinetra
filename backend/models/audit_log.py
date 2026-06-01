from sqlalchemy import Column, Integer, String, DateTime, Text
from backend.database import Base
from datetime import datetime


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(100), nullable=True)
    action = Column(String(100), index=True)  # login, alert_update, soar_execute, etc.
    resource_type = Column(String(50))  # alert, incident, user, playbook
    resource_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
