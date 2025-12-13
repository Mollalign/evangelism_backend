"""
Authentication Schemas

Pydantic models for authentication requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ----------------------------------------------------
# Request Schemas
# ----------------------------------------------------

class UserRegister(BaseModel):
    """User registration request schema."""
    model_config = ConfigDict(from_attributes=True)
    
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password (min 8 characters)")
    phone_number: Optional[str] = Field(None, max_length=50, description="User's phone number")


class UserLogin(BaseModel):
    """User login request schema."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User password")


class TokenRefresh(BaseModel):
    """Token refresh request schema."""
    model_config = ConfigDict(from_attributes=True)
    
    refresh_token: str = Field(..., description="Refresh token")


# ----------------------------------------------------
# Response Schemas
# ----------------------------------------------------

class TokenResponse(BaseModel):
    """Token response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class UserResponse(BaseModel):
    """User response schema (without sensitive data)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="User UUID")
    full_name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    phone_number: Optional[str] = Field(None, description="User's phone number")
    is_active: bool = Field(..., description="User account active status")
    created_at: str = Field(..., description="Account creation timestamp")
    
    @classmethod
    def from_user(cls, user: "User") -> "UserResponse":
        """Create UserResponse from User model."""
        from datetime import datetime
        return cls(
            id=str(user.id),
            full_name=user.full_name,
            email=user.email,
            phone_number=user.phone_number,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat()
        )


class AuthResponse(BaseModel):
    """Authentication response with user and tokens."""
    model_config = ConfigDict(from_attributes=True)
    
    user: UserResponse = Field(..., description="User information")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class MessageResponse(BaseModel):
    """Simple message response."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(..., description="Response message")
