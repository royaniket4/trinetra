from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from backend.database import Base
from datetime import datetime


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(255), index=True)
    ip_address = Column(String(45), index=True)
    mac_address = Column(String(50), nullable=True)
    asset_type = Column(String(50))
    os = Column(String(100), nullable=True)
    os_version = Column(String(100), nullable=True)
    manufacturer = Column(String(255), nullable=True)
    model = Column(String(255), nullable=True)
    services = Column(Text, nullable=True)
    open_ports = Column(Text, nullable=True)
    vulnerabilities = Column(Text, nullable=True)
    risk_score = Column(Float, default=0.0)
    owner = Column(String(255), nullable=True)
    department = Column(String(100), nullable=True)
    criticality = Column(String(20), default="medium")
    status = Column(String(20), default="active")
    is_blocked = Column(Boolean, default=False)
    is_quarantined = Column(Boolean, default=False)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)