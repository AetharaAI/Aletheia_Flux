"""Rate limiting middleware."""
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from config import settings


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self.requests = defaultdict(list)
        self.limit = settings.rate_limit_per_minute
        self.window = 60  # seconds
    
    def check_rate_limit(self, client_id: str) -> bool:
        """
        Check if client has exceeded rate limit.
        
        Args:
            client_id: Client identifier (IP address or user ID)
        
        Returns:
            True if within limit, raises HTTPException otherwise
        """
        now = time.time()
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.limit} requests per minute."
            )
        
        # Add current request
        self.requests[client_id].append(now)
        return True


# Global rate limiter
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    client_ip = request.client.host
    
    try:
        rate_limiter.check_rate_limit(client_ip)
    except HTTPException as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )
    
    response = await call_next(request)
    return response
