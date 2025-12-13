"""
Authentication Service

Business logic for authentication operations.
"""

from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
    create_token_pair
)
from app.repositories.user import UserRepository
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize auth service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register(self, user_data: UserRegister) -> tuple[User, dict]:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Tuple of (User instance, token dict)
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        if await self.user_repo.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user
        user = await self.user_repo.create_user(
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            is_active=True
        )
        
        # Commit transaction
        await self.db.commit()
        await self.db.refresh(user)
        
        # Create tokens
        tokens = create_token_pair(
            user_id=str(user.id),
            email=user.email
        )
        
        return user, tokens
    
    async def login(self, login_data: UserLogin) -> tuple[User, dict]:
        """
        Authenticate user and return tokens.
        
        Args:
            login_data: User login credentials
            
        Returns:
            Tuple of (User instance, token dict)
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = await self.user_repo.get_by_email(login_data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create tokens
        tokens = create_token_pair(
            user_id=str(user.id),
            email=user.email
        )
        
        return user, tokens
    
    async def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token dict with access_token
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        from app.core.security import decode_token, verify_token_type, create_access_token
        
        # Verify token type
        if not verify_token_type(refresh_token, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Decode token
        try:
            payload = decode_token(refresh_token)
            user_id = payload.get("user_id")
            email = payload.get("email") or payload.get("sub")
            
            if not user_id or not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify user still exists and is active
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive"
                )
            
            # Create new access token
            token_data = {
                "user_id": str(user.id),
                "sub": email,
                "email": email
            }
            access_token = create_access_token(data=token_data)
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid refresh token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

