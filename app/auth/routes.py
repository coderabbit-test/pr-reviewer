from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from .models import (
    UserSignupRequest, 
    UserLoginRequest, 
    AuthResponse, 
    UserResponse, 
    TokenResponse,
    RefreshTokenRequest
)
from .firebase_auth import firebase_auth
from .dependencies import get_current_user
from typing import Dict, Any
import logging

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignupRequest):
    """
    Create a new user account
    """
    try:
        # Basic validation
        if not user_data.email or not user_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        if len(user_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        # Create user in Firebase
        user = await firebase_auth.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        # Sign in the user to get tokens
        auth_result = await firebase_auth.sign_in_user(
            email=user_data.email,
            password=user_data.password
        )
        
        return AuthResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            user=UserResponse(**auth_result["user"])
        )
        
    except Exception as e:
        logger.error(f"User signup failed for {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user account"
        )


@router.post("/login", response_model=AuthResponse)
async def login(user_data: UserLoginRequest):
    """
    Authenticate user and return access tokens
    """
    try:
        auth_result = await firebase_auth.sign_in_user(
            email=user_data.email,
            password=user_data.password
        )
        
        return AuthResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            user=UserResponse(**auth_result["user"])
        )
        
    except Exception as e:
        logger.warning(f"Login attempt failed for {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    try:
        new_access_token = await firebase_auth.refresh_access_token(
            refresh_data.refresh_token
        )
        
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return TokenResponse(access_token=new_access_token)
        
    except Exception as e:
        logger.warning(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user information
    """
    return UserResponse(
        id=current_user["uid"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        is_active=True,
        created_at=""  # You might want to fetch this from your database
    )


@router.post("/logout")
async def logout():
    """
    Logout user (client should discard tokens)
    """
    return {"message": "Successfully logged out"}


@router.get("/verify")
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Verify if the current token is valid
    """
    return {
        "valid": True,
        "user": {
            "id": current_user["uid"],
            "email": current_user["email"],
            "role": current_user["role"]
        }
    } 