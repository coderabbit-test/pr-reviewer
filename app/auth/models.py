from pydantic import BaseModel, EmailStr
from typing import Optional


class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserLoginRequest(BaseModel):
    email: str  
    password: Optional[str] = None  


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str 