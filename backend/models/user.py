from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum as SQLEnum
from backend.database import Base
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    SOC_MANAGER = "soc_manager"
    CISO = "ciso"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.ANALYST, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Additional security fields
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Profile fields
    department = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    
    def has_permission(self, required_role: UserRole) -> bool:
        """Check if user has required permission level."""
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.ANALYST: 2,
            UserRole.SOC_MANAGER: 3,
            UserRole.CISO: 4,
            UserRole.ADMIN: 5
        }
        
        # Superusers bypass hierarchy
        if self.is_superuser:
            return True
            
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)