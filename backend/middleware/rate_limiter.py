from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from backend.config import get_settings
import time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""
    
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        
        if not self.settings.rate_limit_enabled:
            return
            
        # Store request counts: {ip: [(timestamp, count)]}
        self.requests = defaultdict(list)
        self.window_size = 60  # 1 minute window
        self.max_requests = self.settings.rate_limit_requests_per_minute
    
    async def dispatch(self, request: Request, call_next):
        if not self.settings.rate_limit_enabled:
            return await call_next(request)
        
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Clean old requests outside the window
        current_time = time.time()
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip]
            if current_time - ts < self.window_size
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": self.window_size
                }
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.max_requests - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response