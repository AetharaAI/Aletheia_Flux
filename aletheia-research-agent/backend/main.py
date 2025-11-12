"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Security
from middleware.rate_limiter import rate_limit_middleware
from middleware.error_handler import error_handler_middleware
from api.auth_routes import router as auth_router
from api.chat_routes import router as chat_router
from config import settings
from fastapi.security import HTTPBearer
from jose import jwt

security = HTTPBearer()

# Create FastAPI app
app = FastAPI(
    title="Aletheia Research Agent API",
    description="Truth-seeking research assistant with agentic workflows",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware (production)
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.aletheia.app", "localhost"]
    )

# Custom middleware
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(error_handler_middleware)

# Include routers
app.include_router(auth_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Aletheia Research Agent API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/debug-token")
async def debug_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Debug endpoint to inspect token payload."""
    try:
        payload = jwt.decode(credentials.credentials, key=None, options={"verify_signature": False})
        return {
            "has_iss": "iss" in payload,
            "iss": payload.get("iss"),
            "has_sub": "sub" in payload,
            "sub": payload.get("sub"),
            "exp": payload.get("exp"),
            "payload_keys": list(payload.keys())
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )
