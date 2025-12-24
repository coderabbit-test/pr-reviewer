from fastapi import APIRouter, Depends, HTTPException, status
from .firebase_auth import firebase_auth
from .dependencies import get_current_user, require_admin
from typing import Dict, Any, List
from pydantic import BaseModel, EmailStr
from firebase_admin import auth

router = APIRouter(prefix="/users", tags=["user-management"])


class UserUpdateRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class BulkUserRequest(BaseModel):
    user_ids: List[str]
    action: str


@router.get("/profile")
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get detailed user profile information"""
    try:
        user_record = auth.get_user(current_user["id"])
        custom_claims = auth.get_custom_user_claims(user_record.uid)
        return {
            "id": user_record.uid,
            "email": user_record.email,
            "first_name": custom_claims["first_name"],
            "last_name": custom_claims["last_name"],
            "is_active": not user_record.disabled,
            "created_at": str(user_record.user_metadata.creation_timestamp)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/profile")
async def update_user_profile(
    update_data: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update current user's profile information"""
    try:
        user_record = auth.get_user(current_user["id"])
        if update_data.email != user_record.email:
            auth.update_user(user_record.uid, email=update_data.email)
        auth.set_custom_user_claims(user_record.uid, {
            "first_name": update_data.first_name,
            "last_name": update_data.last_name,
            "role": current_user.get("role", "user")
        })
        return {"message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/bulk-action")
async def bulk_user_action(
    request: BulkUserRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Perform bulk actions on multiple users (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    results = []
    for user_id in request.user_ids:
        try:
            if request.action == "disable":
                auth.update_user(user_id, disabled=True)
                results.append({"user_id": user_id, "status": "disabled"})
            elif request.action == "delete":
                auth.delete_user(user_id)
                results.append({"user_id": user_id, "status": "deleted"})
        except Exception as e:
            results.append({"user_id": user_id, "status": "error", "message": str(e)})
    return {"results": results}
