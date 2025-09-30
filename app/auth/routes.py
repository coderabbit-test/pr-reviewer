from fastapi import APIRouter, HTTPException, status, Depends, Request, Header
from fastapi.security import HTTPBearer
from .models import (
    UserSignupRequest, 
    UserLoginRequest, 
    AuthResponse, 
    UserResponse, 
    TokenResponse,
    RefreshTokenRequest,
    UserUpdateRequest,
    ChangePasswordRequest,
    UserRole,
    SessionInfo,
    AuditLogEntry
)
from .firebase_auth import firebase_auth
from .dependencies import get_current_user
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignupRequest):
    """
    Create a new user account
    """
    try:
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
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
            "role": current_user.get("role", "user")
        }
    }


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request = None
):
    """
    Update user profile information
    """
    try:
        # Update user in Firebase
        update_data = {}
        if profile_data.first_name is not None:
            update_data["first_name"] = profile_data.first_name
        if profile_data.last_name is not None:
            update_data["last_name"] = profile_data.last_name
            
        # Only admins can change roles
        if profile_data.role is not None:
            if current_user.get("role") != UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only administrators can change user roles"
                )
            update_data["role"] = profile_data.role.value
        
        if update_data:
            await firebase_auth.update_user(current_user["uid"], update_data)
        
        # Log the profile update
        await _log_audit_event(
            user_id=current_user["uid"],
            action="profile_update",
            request=request,
            details=update_data
        )
        
        # Return updated user info
        updated_user = await firebase_auth.get_user(current_user["uid"])
        return UserResponse(
            id=updated_user["uid"],
            email=updated_user["email"],
            first_name=updated_user["first_name"],
            last_name=updated_user["last_name"],
            is_active=True,
            created_at=updated_user.get("created_at", ""),
            role=UserRole(updated_user.get("role", "user")),
            last_login=updated_user.get("last_login")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request = None
):
    """
    Change user password
    """
    try:
        # Verify current password
        await firebase_auth.sign_in_user(
            email=current_user["email"],
            password=password_data.current_password
        )
        
        # Update password
        await firebase_auth.update_user_password(
            current_user["uid"],
            password_data.new_password
        )
        
        # Log the password change
        await _log_audit_event(
            user_id=current_user["uid"],
            action="password_change",
            request=request
        )
        
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password or unable to update password"
        )


@router.get("/sessions", response_model=List[SessionInfo])
async def get_user_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get active sessions for the current user
    """
    # This would typically fetch from a database
    # For demo purposes, return a mock session
    sessions = [
        SessionInfo(
            session_id=str(uuid.uuid4()),
            created_at=datetime.now(),
            last_activity=datetime.now(),
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0 (Demo Browser)"
        )
    ]
    return sessions


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request = None
):
    """
    Revoke a specific user session
    """
    # This would typically remove the session from a database
    await _log_audit_event(
        user_id=current_user["uid"],
        action="session_revoked",
        request=request,
        details={"session_id": session_id}
    )
    
    return {"message": f"Session {session_id} has been revoked"}


@router.get("/audit-logs", response_model=List[AuditLogEntry])
async def get_audit_logs(
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = 50
):
    """
    Get audit logs for the current user (admin only)
    """
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view audit logs"
        )
    
    # This would typically fetch from a database
    # For demo purposes, return mock audit logs
    logs = [
        AuditLogEntry(
            user_id=current_user["uid"],
            action="login",
            timestamp=datetime.now(),
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0 (Demo Browser)"
        ),
        AuditLogEntry(
            user_id=current_user["uid"],
            action="profile_update",
            timestamp=datetime.now(),
            ip_address="127.0.0.1",
            details={"fields_updated": ["first_name"]}
        )
    ]
    return logs[:limit]


async def _log_audit_event(
    user_id: str,
    action: str,
    request: Request = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log an audit event
    """
    # This would typically save to a database
    # For demo purposes, we'll just print it
    ip_address = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None
    
    audit_entry = AuditLogEntry(
        user_id=user_id,
        action=action,
        timestamp=datetime.now(),
        ip_address=ip_address,
        user_agent=user_agent,
        details=details
    )
    
    print(f"Audit Log: {audit_entry.dict()}") 