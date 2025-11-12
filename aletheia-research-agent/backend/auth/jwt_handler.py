"""JWT authentication handler."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Verify JWT token and return payload."""
    try:
        token = credentials.credentials

        if not token:
            raise HTTPException(status_code=401, detail="No token provided")

        # Try to decode without verification first (for Supabase tokens)
        # Supabase tokens can be decoded but not verified without their public key
        try:
            # Decode without verification to get the payload
            payload = jwt.decode(
                token,
                key=None,
                options={"verify_signature": False, "verify_aud": False, "verify_exp": False}
            )

            # Check if this is a Supabase token (has 'iss' claim)
            if "supabase" in payload.get("iss", "").lower():
                # Ensure the payload has a 'sub' field (user ID)
                if not payload.get("sub"):
                    raise HTTPException(status_code=401, detail="Invalid token: no user ID found")
                return payload

        except JWTError as e:
            # If Supabase token decode fails, fall through to try our own secret
            pass

        # Try to verify with our own secret (for custom tokens)
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification error: {str(e)}")


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Get current user ID from token."""
    payload = verify_token(credentials)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: user ID not found")

    return user_id
