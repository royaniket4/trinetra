from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from backend.database import Base
from datetime import datetime


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source_ip = Column(String(45), index=True)
    dest_ip = Column(String(45), nullable=True)
    username = Column(String(255), nullable=True, index=True)
    event_type = Column(String(100), index=True)
    severity = Column(Integer, default=1)
    raw_log = Column(Text)
    geo_country = Column(String(100), nullable=True)
    geo_lat = Column(Float, nullable=True)
    geo_lon = Column(Float, nullable=True)
    sourcetype = Column(String(100), nullable=True, index=True)
    host = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    log_source = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)