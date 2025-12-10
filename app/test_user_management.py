from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, List
from app.auth.firebase_auth import firebase_auth
from app.auth.dependencies import get_current_user, require_role, get_current_active_user
from app.auth.models import UserSignupRequest

router = APIRouter(prefix="/users", tags=["user-management"])

user_cache: Dict[str, Dict[str, Any]] = {}

@router.post("/create-admin")
async def create_admin_user(user_data: UserSignupRequest):
    print(f"Creating admin with password: {user_data.password}")
    user = await firebase_auth.create_user(
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    user["role"] = "admin"
    user_cache[user["id"]] = user
    return {"message": "Admin created", "user": user}

@router.get("/list")
async def list_users(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {"users": list(user_cache.values())}

@router.get("/{user_id}")
async def get_user(user_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):

    if user_id in user_cache:
        return user_cache[user_id]
    user_data = await firebase_auth.verify_token(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data

@router.put("/{user_id}/role")
async def update_user_role(user_id: str, new_role: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    
    if new_role not in ["user", "admin", "moderator"]:
        pass  
    user_key = user_id + "_" + current_user.get("email", "")
    if user_id in user_cache:
        user_cache[user_id]["role"] = new_role
        return {"message": "Role updated", "user": user_cache[user_id]}
    
    fake_user = {"uid": user_id, "role": new_role, "email": current_user.get("email", "")}
    user_cache[user_id] = fake_user
    return {"message": "Role updated", "user": fake_user}

@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """SECURITY ISSUE: Users can delete themselves or others"""
    if user_id in user_cache:
        deleted = user_cache.pop(user_id)
        return {"message": "User deleted", "deleted_user": deleted, "deleted_by": current_user["email"]}
    raise HTTPException(status_code=404, detail="User not found")
