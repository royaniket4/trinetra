from sqlalchemy import Column, Integer, String, DateTime, Text
from backend.database import Base
from datetime import datetime


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(100), unique=True, index=True)
    title = Column(String(500))
    description = Column(Text)
    severity = Column(Integer, index=True)
    status = Column(String(20), default="open")
    assigned_to = Column(String(255), nullable=True)
    alert_count = Column(Integer, default=0)
    first_activity = Column(DateTime)
    last_activity = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)