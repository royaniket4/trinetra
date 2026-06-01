from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from backend.database import Base
from datetime import datetime


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(100), unique=True, index=True)
    rule_name = Column(String(200), index=True)
    severity = Column(Integer, index=True)
    mitre_tactic = Column(String(100), nullable=True)
    mitre_technique = Column(String(100), nullable=True)
    confidence = Column(Float, default=1.0)
    asset_impact = Column(String(100), nullable=True)
    evidence = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source_ip = Column(String(45), index=True)
    dest_ip = Column(String(45), nullable=True)
    username = Column(String(255), nullable=True)
    status = Column(String(20), default="active")
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(255), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    incident_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)