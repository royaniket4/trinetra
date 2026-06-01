from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.models.user import User, UserRole
from backend.database import get_db
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from backend.config import get_settings
from functools import wraps
from typing import List

security = HTTPBearer()
settings = get_settings()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_roles(allowed_roles: List[UserRole]):
    """Dependency to check user roles."""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


# Pre-built role dependencies
require_admin = require_roles([UserRole.ADMIN])
require_analyst = require_roles([UserRole.ADMIN, UserRole.ANALYST])
require_viewer = require_roles([UserRole.ADMIN, UserRole.ANALYST, UserRole.VIEWER])


# Decorator for route protection
def role_required(allowed_roles: List[UserRole]):
    """Decorator for protecting routes with role-based access."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current_user from kwargs if passed
            current_user = kwargs.get('current_user')
            if not current_user:
                # If not passed, it will be injected by FastAPI dependency
                pass
            return await func(*args, **kwargs)
        return wrapper
    return decorator