"""
User Schemas

Pydantic models for user-related requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    """User creation schema."""
    model_config = ConfigDict(from_attributes=True)
    
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=50)


class UserUpdate(BaseModel):
    """User update schema."""
    model_config = ConfigDict(from_attributes=True)
    
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    full_name: str
    email: EmailStr
    phone_number: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str
