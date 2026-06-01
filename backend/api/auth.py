"""Authentication API - Login, register, profile, user management."""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import hashlib
import secrets

from backend.database import get_db
from backend.models.user import User
from backend.models.audit_log import AuditLog
from backend.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    UserUpdate,
    AuditLogResponse,
)
from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    salt = hashed_password[:32]
    stored_hash = hashed_password[32:]
    return hashlib.sha256(salt.encode() + plain_password.encode()).hexdigest() == stored_hash


def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    pw_hash = hashlib.sha256(salt.encode() + password.encode()).hexdigest()
    return salt + pw_hash

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = settings.jwt_secret or "trinetra-dev-secret-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user


def log_audit(db: Session, user: User, action: str, resource_type: str, resource_id: str = None, details: str = None, ip: str = None):
    audit = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip,
    )
    db.add(audit)
    db.commit()


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # First user gets admin role
    user_count = db.query(User).count()
    role = "admin" if user_count == 0 else user_data.role
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username, "role": user.role})
    
    log_audit(db, user, "register", "user", str(user.id), f"User {user.username} registered")
    
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    token = create_access_token({"sub": user.username, "role": user.role})
    
    log_audit(db, user, "login", "auth", str(user.id), f"User {user.username} logged in")
    
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    if update.full_name is not None:
        current_user.full_name = update.full_name
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all users (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    users = db.query(User).all()
    return [UserResponse.model_validate(u) for u in users]


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user role or status (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if update.role is not None:
        user.role = update.role
    if update.is_active is not None:
        user.is_active = update.is_active
    
    db.commit()
    db.refresh(user)
    
    log_audit(db, current_user, "update_user", "user", str(user.id), f"Updated user {user.username}: role={update.role}, active={update.is_active}")
    
    return UserResponse.model_validate(user)


@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def get_audit_logs(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get audit logs (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [AuditLogResponse.model_validate(l) for l in logs]
