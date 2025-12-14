"""
Users API Routes

This module handles user endpoints:
- GET /api/v1/users/accounts - Get user's accounts
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_database_session, get_current_active_user
from app.models.user import User
from app.schemas.account import AccountResponse
from app.repositories.account_user import AccountUserRepository
from app.repositories.account import AccountRepository

router = APIRouter()


@router.get("/accounts", response_model=List[AccountResponse])
async def get_user_accounts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_database_session)
):
    """
    Get all accounts the current user belongs to.
    
    Returns a list of accounts the authenticated user has access to.
    """
    account_user_repo = AccountUserRepository(db)
    account_repo = AccountRepository(db)
    
    # Get all account-user relationships for this user
    account_users = await account_user_repo.get_by_user_id(str(current_user.id))
    
    # Get account details
    accounts = []
    for au in account_users:
        account = await account_repo.get_by_id(str(au.account_id))
        if account and account.is_active:
            accounts.append(AccountResponse.model_validate(account))
    
    return accounts

