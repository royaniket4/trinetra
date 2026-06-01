import logging
import json
import sys
from datetime import datetime
from typing import Any
from backend.config import get_settings

settings = get_settings()


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


def setup_logging():
    """Configure application logging."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if settings.log_format == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


class AuditLogger:
    """Special logger for audit events."""
    
    def __init__(self):
        self.logger = logging.getLogger("audit")
    
    def log_event(
        self, 
        event_type: str, 
        user_id: str, 
        details: dict,
        ip_address: str = None
    ):
        """Log an audit event."""
        self.logger.info(
            f"AUDIT: {event_type}",
            extra={
                "extra_data": {
                    "event_type": event_type,
                    "user_id": user_id,
                    "ip_address": ip_address,
                    **details
                }
            }
        )
    
    def log_login(self, user_id: str, success: bool, ip_address: str = None):
        self.log_event(
            "USER_LOGIN" if success else "LOGIN_FAILED",
            user_id,
            {"success": success},
            ip_address
        )
    
    def log_action(self, user_id: str, action: str, resource: str, details: dict = None):
        self.log_event(
            "USER_ACTION",
            user_id,
            {"action": action, "resource": resource, **(details or {})}
        )
    
    def log_api_access(self, user_id: str, endpoint: str, method: str, status_code: int):
        self.log_event(
            "API_ACCESS",
            user_id,
            {"endpoint": endpoint, "method": method, "status_code": status_code}
        )


audit_logger = AuditLogger()