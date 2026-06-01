from enum import Enum


class SeverityLevel(int, Enum):
    """Alert severity levels."""
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class AlertStatus(str, Enum):
    """Alert status values."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"


class EventType(str, Enum):
    """Log event types."""
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    FILE_ACCESS = "FILE_ACCESS"
    PROCESS_CREATED = "PROCESS_CREATED"
    NETWORK_CONNECTION = "NETWORK_CONNECTION"
    POWERSHELL = "POWERSHELL"
    FILE_DOWNLOAD = "FILE_DOWNLOAD"
    PRIVILEGE_CHANGE = "PRIVILEGE_CHANGE"
    SERVICE_INSTALLED = "SERVICE_INSTALLED"
    REGISTRY_CHANGE = "REGISTRY_CHANGE"
    DNS_QUERY = "DNS_QUERY"
    AUTH = "AUTH"
    PORT_SCAN = "PORT_SCAN"
    SQL_QUERY = "SQL_QUERY"


class LogFormat(str, Enum):
    """Log format types."""
    WINDOWS = "windows"
    LINUX = "linux"
    APACHE = "apache"
    NGINX = "nginx"
    FIREWALL = "firewall"
    JSON = "json"
    CUSTOM = "custom"