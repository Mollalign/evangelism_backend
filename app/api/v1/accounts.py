"""
Accounts API Routes

This module handles account endpoints:
- POST /api/v1/accounts (Create)
- GET /api/v1/accounts (List my accounts)
- GET /api/v1/accounts/{id} (Get)
- PUT /api/v1/accounts/{id} (Update)
- DELETE /api/v1/accounts/{id} (Delete)
- POST /api/v1/accounts/{id}/join (Request to join)
"""

from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_database_session, get_current_active_user
from app.models.user import User
from app.services.account import AccountService
from app.schemas.account import AccountCreate, AccountResponse

router = APIRouter()

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new account.
    The creating user automatically becomes the Account Owner / Admin.
    """
    service = AccountService(db)
    return await service.create_account(current_user, data)

@router.get("/", response_model=List[Any])
async def list_my_accounts(
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """List all accounts membership for the current user."""
    service = AccountService(db)
    return await service.get_user_accounts(current_user.id)

@router.post("/{account_id}/join", status_code=status.HTTP_200_OK)
async def request_join_account(
    account_id: str,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Request to join an existing account.
    Sends an invitation request to the account admin.
    """
    service = AccountService(db)
    # Check if UUID valid
    try:
        uuid_id = UUID(account_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
        
    await service.request_join_account(current_user, uuid_id)
    return {"message": "Join request sent successfully"}


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific account.
    """
    service = AccountService(db)
    # Check if UUID valid
    try:
        uuid_id = UUID(account_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid account ID format"
        )
        
    return await service.get_account_by_id(uuid_id)
