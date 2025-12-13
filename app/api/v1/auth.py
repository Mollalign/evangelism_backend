"""
Authentication API Routes

This module handles authentication endpoints:
- POST /api/v1/auth/login
- POST /api/v1/auth/register
- GET /api/v1/auth/me
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_database_session, get_current_active_user
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenRefresh,
    AuthResponse,
    UserResponse,
    TokenResponse,
    MessageResponse
)
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Register a new user account.
    
    Creates a new user account and returns authentication tokens.
    """
    auth_service = AuthService(db)
    user, tokens = await auth_service.register(user_data)
    
    return AuthResponse(
        user=UserResponse.from_user(user),
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"]
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Authenticate user and return access tokens.
    
    Validates user credentials and returns JWT tokens for authenticated requests.
    """
    auth_service = AuthService(db)
    user, tokens = await auth_service.login(login_data)
    
    return AuthResponse(
        user=UserResponse.from_user(user),
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"]
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    
    Returns the user profile of the currently authenticated user.
    """
    return UserResponse.from_user(current_user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Refresh access token using refresh token.
    
    Generates a new access token from a valid refresh token.
    """
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_token(token_data.refresh_token)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=token_data.refresh_token,  # Return same refresh token
        token_type=tokens["token_type"]
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout user (client-side token invalidation).
    
    Note: Since we're using stateless JWT tokens, actual invalidation
    should be handled client-side. This endpoint is provided for
    consistency with the API contract.
    """
    return MessageResponse(message="Successfully logged out")
