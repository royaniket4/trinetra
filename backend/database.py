from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from backend.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    poolclass=StaticPool if "sqlite" in settings.database_url else None,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    # Import ALL models so SQLAlchemy registers their tables before create_all
    from backend.models.log import Log
    from backend.models.alert import Alert
    from backend.models.incident import Incident
    from backend.models.asset import Asset
    from backend.models.response_action import ResponseAction
    from backend.models.playbook import PlaybookExecution, PlaybookExecutionStep
    from backend.models.detection_rule import DetectionRule
    from backend.models.user import User
    from backend.models.conversation import Conversation
    from backend.models.audit_log import AuditLog
    from backend.models.threat_intel import ThreatIntel
    from backend.models.webhook import Webhook
    from backend.models.dashboard import Dashboard
    Base.metadata.create_all(bind=engine)