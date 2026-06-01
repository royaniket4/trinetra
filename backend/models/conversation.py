from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from backend.database import Base
from datetime import datetime


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    role = Column(String(20))  # user, assistant
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
