from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from backend.database import Base
from datetime import datetime


class PlaybookExecution(Base):
    __tablename__ = "playbook_executions"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(100), unique=True, index=True)
    playbook_id = Column(String(100), index=True)
    playbook_name = Column(String(255))
    triggered_by = Column(String(100))
    status = Column(String(20), default="running")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class PlaybookExecutionStep(Base):
    __tablename__ = "playbook_execution_steps"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("playbook_executions.id"))
    order = Column(Integer)
    action_type = Column(String(50))
    target = Column(String(255))
    label = Column(String(255))
    status = Column(String(20), default="pending")
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
