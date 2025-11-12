"""Error handling middleware."""
import traceback
import bleach
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Union


async def error_handler_middleware(request: Request, call_next):
    """Global error handling middleware."""
    try:
        response = await call_next(request)
        return response
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"error": {"code": "HTTP_ERROR", "message": e.detail}}
        )
    except Exception as e:
        # Log error
        print(f"Unhandled error: {str(e)}")
        print(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal error occurred. Please try again."
                }
            }
        )


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        text: Raw user input
    
    Returns:
        Sanitized text
    """
    # Allow basic formatting tags
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br']
    allowed_attributes = {'a': ['href', 'title']}
    
    sanitized = bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    return sanitized


def validate_input_length(text: str, max_length: int = 10000) -> bool:
    """
    Validate input length.
    
    Args:
        text: Input text
        max_length: Maximum allowed length
    
    Returns:
        True if valid, raises HTTPException otherwise
    """
    if len(text) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Input too long. Maximum {max_length} characters allowed."
        )
    return True
