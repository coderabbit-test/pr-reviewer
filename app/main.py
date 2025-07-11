from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
from fastapi import Request
from .auth.routes import router as auth_router
from .example_protected_routes import router as protected_router
import os

# Create FastAPI app
app = FastAPI(
    title="Authentication API",
    description="A FastAPI application with Firebase authentication",
    version="1.0.0"
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
async def global_exception_handler(request: Request, exc: Exception):
    # Log full traceback (could also write to a file or logging service)
    print(f"Unhandled Exception: {exc}")
    traceback.print_exc()

    # You can add more detailed errors in dev mode
    is_dev = os.environ.get("ENV", "dev") == "dev"
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if is_dev else None,
            "path": request.url.path
        },
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Authentication API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Authentication API",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/auth",
            "protected": "/protected"
        }
    } 
