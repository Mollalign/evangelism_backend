"""
Account Service

Business logic for account operations.
"""

from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.account import Account
from app.repositories.account import AccountRepository
from app.repositories.account_user import AccountUserRepository
from app.repositories.role import RoleRepository
from app.schemas.account import AccountCreate, AccountResponse


class AccountService:
    """Service for account operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize account service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.account_repo = AccountRepository(db)
        self.account_user_repo = AccountUserRepository(db)
        self.role_repo = RoleRepository(db)
    
    async def create_account(self, current_user: User, data: AccountCreate) -> AccountResponse:
        """
        Create a new account and assign the creating user as owner.
        
        Args:
            current_user: The authenticated user creating the account
            data: Account creation data
            
        Returns:
            Created account response
        """
        # Create the account
        account = Account(
            account_name=data.account_name,
            email=data.email,
            phone_number=data.phone_number,
            location=data.location,
            created_by=current_user.id,
            is_active=True
        )
        
        self.db.add(account)
        await self.db.flush()
        await self.db.refresh(account)
        
        # Ensure default roles exist
        await self.role_repo.ensure_default_roles()
        
        # Get owner role
        owner_role = await self.role_repo.get_by_name("owner")
        if not owner_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Owner role not found"
            )
        
        # Link user to account as owner
        await self.account_user_repo.create(
            account_id=account.id,
            user_id=current_user.id,
            role_id=owner_role.id
        )
        
        # Commit transaction
        await self.db.commit()
        await self.db.refresh(account)
        
        return AccountResponse.model_validate(account)

    async def get_account_by_id(self, account_id: UUID) -> AccountResponse:
        """
        Get an account by ID.
        
        Args:
            account_id: Account UUID
            
        Returns:
            Account response
        """
        account = await self.account_repo.get_by_id(str(account_id))
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        return AccountResponse.model_validate(account)
    
    async def get_user_accounts(self, user_id: UUID) -> List[dict]:
        """
        Get all accounts a user belongs to.
        
        Args:
            user_id: User UUID
            
        Returns:
            List of account information with role
        """
        account_users = await self.account_user_repo.get_by_user_id(str(user_id))
        
        result = []
        for au in account_users:
            account = await self.account_repo.get_by_id(str(au.account_id))
            if account and account.is_active:
                result.append({
                    "id": str(account.id),
                    "account_name": account.account_name,
                    "email": account.email,
                    "phone_number": account.phone_number,
                    "location": account.location,
                    "is_active": account.is_active,
                    "created_by": str(account.created_by),
                    "role_id": str(au.role_id)
                })
        
        return result
    
    async def request_join_account(self, current_user: User, account_id: UUID) -> None:
        """
        Request to join an existing account.
        
        Args:
            current_user: The authenticated user requesting to join
            account_id: Account UUID to join
            
        Raises:
            HTTPException: If account not found or user already member
        """
        # Check if account exists
        account = await self.account_repo.get_by_id(str(account_id))
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        if not account.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is not active"
            )
        
        # Check if user is already a member
        existing = await self.account_user_repo.get_by_user_and_account(
            user_id=str(current_user.id),
            account_id=str(account_id)
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already a member of this account"
            )
        
        # Get member role (default for join requests)
        member_role = await self.role_repo.get_by_name("member")
        if not member_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Member role not found"
            )
        
        # Create account-user relationship
        # Note: In a real app, this might create a pending invitation instead
        await self.account_user_repo.create(
            account_id=account_id,
            user_id=current_user.id,
            role_id=member_role.id
        )
        
        await self.db.commit()
