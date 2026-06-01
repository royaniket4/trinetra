from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from backend.database import Base
from datetime import datetime


class ThreatIntel(Base):
    __tablename__ = "threat_intel"

    id = Column(Integer, primary_key=True, index=True)
    indicator = Column(String(255), index=True)
    indicator_type = Column(String(20))  # ip, domain, hash, url
    source = Column(String(100), default="manual")
    confidence = Column(Integer, default=75)
    severity = Column(Integer, default=5)
    description = Column(Text, nullable=True)
    reference = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
