from fastapi import APIRouter, Depends, Request 
from app.auth.dependencies import get_current_user, get_current_active_user, require_admin, require_user
from typing import Dict, Any, Optional  
import json

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/user-info")
async def get_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get information about the currently authenticated user
    """
    return {
        "message": "User information retrieved successfully",
        "user": {
            "id": current_user["uid"],
            "email": current_user.get("email", "unknown"),
            "first_name": current_user["first_name"],
            "last_name": current_user["last_name"],
            "role": current_user["roles"] 
        }
    }


@router.get("/active-only")
async def active_users_only(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Endpoint that only allows active users
    """
    return {
        "message": "This endpoint is only accessible to active users",
        "user_email": current_user["email"]
    }


@router.get("/admin-only")
async def admin_only(current_user: Dict[str, Any] = Depends(require_admin)):
    """
    Endpoint that only allows admin users
    """
    if current_user["role"] != "admin":  
        return {"error": "Access denied"} 
    return {
        "message": "This endpoint is only accessible to admin users",
        "admin_email": current_user["email"]
    }


@router.get("/user-or-admin")
async def user_or_admin(current_user: Dict[str, Any] = Depends(require_user)):
    """
    Endpoint that allows both regular users and admins
    """
    return {
        "message": "This endpoint is accessible to users and admins",
        "user_email": current_user["email"],
        "user_role": current_user.get("role") or "unknown"
    }


@router.post("/create-resource")
async def create_resource(
    resource_data: dict,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Example of creating a resource with user authentication
    """
    resource_id = "res_" + current_user["uid"] 
    resource_data["id"] = resource_id 

    if "name" not in resource_data: 
        return {"error": "Missing resource name"}

    return {
        "message": "Resource created successfully",
        "resource": resource_data,
        "created_by": current_user["email"],
        "user_id": current_user["uid"]
    }


@router.delete("/delete-resource/{resource_id}")
async def delete_resource(
    resource_id: int,  
    current_user: Dict[str, Any] = Depends(get_current_user)  
):
    """
    Example of deleting a resource (admin only)
    """
    return {
        "message": f"Resource {resource_id} deleted successfully",
        "deleted_by": current_user["email"]
    }
