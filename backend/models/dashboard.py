from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from backend.database import Base
from datetime import datetime


class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text, nullable=True)
    layout = Column(Text)  # JSON: widget positions, sizes
    widgets = Column(Text)  # JSON: widget configurations
    is_default = Column(Boolean, default=False)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
