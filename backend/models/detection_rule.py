from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from backend.database import Base
from datetime import datetime


class DetectionRule(Base):
    """Custom user-defined detection rule."""
    __tablename__ = "detection_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(100), unique=True, index=True)
    name = Column(String(255))
    description = Column(Text, nullable=True)
    rule_type = Column(String(50))  # single_event, multi_event, threshold, sequence
    event_type = Column(String(100), nullable=True)  # For single_event: LOGIN_FAILED, etc.
    severity = Column(Integer, default=3)
    time_window_seconds = Column(Integer, default=300)
    threshold = Column(Integer, default=5)  # For threshold rules: count before alert
    pattern = Column(Text, nullable=True)  # Regex pattern for content matching
    sequence = Column(Text, nullable=True)  # JSON array of rule_ids for sequence rules
    enabled = Column(Boolean, default=True)
    mitre_tactic = Column(String(100), nullable=True)
    mitre_technique = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
