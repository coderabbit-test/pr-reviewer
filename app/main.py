from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from .auth.routes import router as auth_router
from .example_protected_routes import router as protected_router
import os
import time
from collections import defaultdict
from typing import Dict

# Rate limiting storage (in production, use Redis or database)
rate_limit_storage: Dict[str, list] = defaultdict(list)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Get client IP
    client_ip = request.client.host
    
    # Current time
    current_time = time.time()
    
    # Clean old entries (older than 1 minute)
    rate_limit_storage[client_ip] = [
        timestamp for timestamp in rate_limit_storage[client_ip]
        if current_time - timestamp < 60
    ]
    
    # Check if rate limit exceeded (100 requests per minute)
    if len(rate_limit_storage[client_ip]) >= 100:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Maximum 100 requests per minute."}
        )
    
    # Add current request timestamp
    rate_limit_storage[client_ip].append(current_time)
    
    # Process request
    response = await call_next(request)
    return response

# Create FastAPI app
app = FastAPI(
    title="Authentication API",
    description="A FastAPI application with Firebase authentication and enhanced security features",
    version="2.0.0"
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)

# Include protected routes (examples)
app.include_router(protected_router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Authentication API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Authentication API v2.0",
        "version": "2.0.0",
        "features": [
            "User authentication and authorization",
            "Role-based access control",
            "Profile management",
            "Session management",
            "Audit logging",
            "Rate limiting",
            "Security enhancements"
        ],
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/auth",
            "protected": "/protected"
        }
    }

# Security information endpoint
@app.get("/security-info")
async def security_info():
    return {
        "security_features": {
            "rate_limiting": "100 requests per minute per IP",
            "trusted_hosts": "Configured for localhost and trusted domains",
            "cors": "Configured for cross-origin requests",
            "audit_logging": "All authentication events are logged",
            "session_management": "Users can manage active sessions",
            "role_based_access": "Admin, Moderator, and User roles supported"
        },
        "recommendations": [
            "Configure CORS origins for production",
            "Use HTTPS in production",
            "Implement proper database for audit logs",
            "Consider using Redis for rate limiting",
            "Add two-factor authentication",
            "Implement password complexity requirements"
        ]
    } 