"""Authentication routes."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from supabase import create_client
from config import settings
from auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()

# Supabase client
supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)


class SignUpRequest(BaseModel):
    """Sign up request model."""
    email: EmailStr
    password: str


class SignInRequest(BaseModel):
    """Sign in request model."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str
    refresh_token: str
    user: dict


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """Sign up a new user."""
    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Failed to create user")
        
        user = auth_response.user
        
        # Create user profile
        supabase.table("users").insert({
            "id": user.id,
            "email": user.email
        }).execute()
        
        # Generate JWT tokens
        access_token = create_access_token({"sub": user.id, "email": user.email})
        refresh_token = create_refresh_token({"sub": user.id})
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={"id": user.id, "email": user.email}
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signin", response_model=AuthResponse)
async def signin(request: SignInRequest):
    """Sign in an existing user."""
    try:
        # Sign in with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = auth_response.user
        
        # Generate JWT tokens
        access_token = create_access_token({"sub": user.id, "email": user.email})
        refresh_token = create_refresh_token({"sub": user.id})
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={"id": user.id, "email": user.email}
        )
    
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh access token."""
    try:
        from jose import jwt
        
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        
        # Generate new access token
        access_token = create_access_token({"sub": user_id})
        
        return {"access_token": access_token}
    
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/signout")
async def signout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Sign out user."""
    # In a production app, you would invalidate the token here
    # For now, client-side token removal is sufficient
    return {"message": "Signed out successfully"}


@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user information."""
    payload = verify_token(credentials)
    user_id = payload.get("sub")
    
    # Get user profile
    result = supabase.table("users")\
        .select("*")\
        .eq("id", user_id)\
        .maybeSingle()\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user": result.data}
