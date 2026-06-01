from sqlalchemy import Column, Integer, String, DateTime, Text
from backend.database import Base
from datetime import datetime


class ResponseAction(Base):
    __tablename__ = "response_actions"

    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String(100), unique=True, index=True)
    action_type = Column(String(50), index=True)
    target = Column(String(255))
    triggered_by = Column(String(20))
    trigger_source = Column(String(100), nullable=True)
    status = Column(String(20), default="pending")
    details = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)