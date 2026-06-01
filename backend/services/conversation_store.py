"""In-memory + DB-backed conversation history store."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session
from backend.models.conversation import Conversation

logger = logging.getLogger(__name__)

_conversation_store: Dict[str, List[Dict]] = {}
_session_timestamps: Dict[str, datetime] = {}


def get_history(session_id: str, db: Session = None) -> List[Dict]:
    """Get conversation history for a session (memory first, DB fallback)."""
    if session_id in _conversation_store:
        return _conversation_store[session_id]
    
    if db:
        rows = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(Conversation.created_at).limit(20).all()
        if rows:
            history = [{"role": r.role, "content": r.content, "timestamp": r.created_at.isoformat()} for r in rows]
            _conversation_store[session_id] = history
            return history
    
    return []


def add_message(session_id: str, role: str, content: str, db: Session = None) -> None:
    """Add a message to the conversation history."""
    if session_id not in _conversation_store:
        _conversation_store[session_id] = []
        _session_timestamps[session_id] = datetime.utcnow()
    
    message = {
        'role': role,
        'content': content,
        'timestamp': datetime.utcnow().isoformat(),
    }
    _conversation_store[session_id].append(message)
    
    if db:
        conv = Conversation(
            session_id=session_id,
            role=role,
            content=content,
        )
        db.add(conv)
        db.commit()
    
    if len(_conversation_store[session_id]) > 20:
        _conversation_store[session_id] = _conversation_store[session_id][-20:]


def clear_session(session_id: str, db: Session = None) -> None:
    """Clear conversation history for a session."""
    if session_id in _conversation_store:
        del _conversation_store[session_id]
    if session_id in _session_timestamps:
        del _session_timestamps[session_id]
    
    if db:
        db.query(Conversation).filter(Conversation.session_id == session_id).delete()
        db.commit()


def prune_old_sessions(older_than_hours: int = 24, db: Session = None) -> None:
    """Remove old session data."""
    cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
    to_remove = []
    
    for session_id, timestamp in _session_timestamps.items():
        if timestamp < cutoff:
            to_remove.append(session_id)
    
    for session_id in to_remove:
        clear_session(session_id, db)
    
    if db:
        db.query(Conversation).filter(Conversation.created_at < cutoff).delete()
        db.commit()
    
    if to_remove:
        logger.info(f"Pruned {len(to_remove)} old conversation sessions")


def create_session() -> str:
    """Create a new session ID."""
    return str(uuid4())
