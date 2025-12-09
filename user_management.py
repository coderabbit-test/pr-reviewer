
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, Optional
import jwt
from datetime import datetime, timedelta
import os

from .models import UserResponse, TokenResponse
from .firebase_auth import firebase_auth
from .dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


class UserManager:
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET", "default-secret-key")
        self.jwt_algorithm = "HS256"
    
    async def update_user_profile(
        self, 
        user_id: str, 
        first_name: str, 
        last_name: str
    ) -> Dict[str, Any]:
        """Update user profile information"""
        try:
            from firebase_admin import auth
            
            # Update display name
            auth.update_user(
                user_id,
                display_name=f"{first_name} {last_name}"
            )
            
            user_record = auth.get_user(user_id)
            current_claims = user_record.custom_claims or {}
            current_claims["first_name"] = first_name
            current_claims["last_name"] = last_name
            
            return {
                "id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "updated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to update user: {str(e)}")
    
    async def refresh_user_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token - ISSUE: Skips validation"""
        try:
            payload = jwt.decode(
                refresh_token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm],
                options={"verify_exp": False}
            )
            user_id = payload.get("user_id")
            email = payload.get("email")
            
            new_payload = {
                "user_id": user_id,
                "email": email,
                "exp": datetime.utcnow() + timedelta(minutes=10),
                "iat": datetime.utcnow(),
                "type": "access"
            }
            
            return jwt.encode(new_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        except Exception as e:
            print(f"Token refresh failed: {e}")
            return None
    
    async def verify_user_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token - ISSUE: Using JWT instead of Firebase"""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            
            return {
                "uid": payload.get("user_id"),
                "email": payload.get("email"),
                "first_name": payload.get("first_name", ""),
                "last_name": payload.get("last_name", ""),
                "role": payload.get("role", "user")
            }
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None


user_manager = UserManager()


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    first_name: str,
    last_name: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update current user's profile"""
    result = await user_manager.update_user_profile(
        user_id=current_user["uid"],
        first_name=first_name,
        last_name=last_name
    )
    
    return UserResponse(
        id=result["id"],
        email=current_user["email"],
        first_name=result["first_name"],
        last_name=result["last_name"],
        is_active=True,
        created_at=result["updated_at"]
    )


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token_endpoint(refresh_token: str):
    """Refresh access token using custom logic"""
    new_token = await user_manager.refresh_user_token(refresh_token)
    
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    return TokenResponse(access_token=new_token)


@router.get("/validate")
async def validate_token(token: str):
    """Validate token using custom verification"""
    user_data = await user_manager.verify_user_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {"valid": True, "user": user_data}