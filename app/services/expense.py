"""
Expense Service

Business logic for expense operations.
"""

from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.expense import ExpenseRepository
from app.repositories.mission import MissionRepository
from app.repositories.account import AccountRepository
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


class ExpenseService:
    """Service for expense operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.expense_repo = ExpenseRepository(db)
        self.mission_repo = MissionRepository(db)
        self.account_repo = AccountRepository(db)
    
    async def create_expense(
        self,
        expense_data: ExpenseCreate,
        current_user: User
    ) -> Expense:
        """Create a new expense."""
        # Verify account exists
        account = await self.account_repo.get_by_id(expense_data.account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # Verify mission exists if provided
        if expense_data.mission_id:
            mission = await self.mission_repo.get_by_id(expense_data.mission_id)
            if not mission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mission not found"
                )
        
        # Create expense
        expense = await self.expense_repo.create(
            account_id=UUID(expense_data.account_id),
            mission_id=UUID(expense_data.mission_id) if expense_data.mission_id else None,
            user_id=current_user.id,
            category=expense_data.category,
            amount=expense_data.amount,
            description=expense_data.description
        )
        
        await self.db.commit()
        await self.db.refresh(expense)
        return expense
    
    async def get_expense(self, expense_id: str) -> Expense:
        """Get expense by ID."""
        expense = await self.expense_repo.get_by_id(expense_id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        return expense
    
    async def get_expenses_by_mission(
        self,
        mission_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Expense]:
        """Get expenses for a mission."""
        return await self.expense_repo.get_by_mission(mission_id, skip, limit)
    
    async def update_expense(
        self,
        expense_id: str,
        expense_data: ExpenseUpdate,
        current_user: User
    ) -> Expense:
        """Update an expense."""
        expense = await self.get_expense(expense_id)
        
        # Verify user owns the expense
        if expense.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this expense"
            )
        
        update_data = expense_data.model_dump(exclude_unset=True)
        if "deleted_at" in update_data and update_data["deleted_at"]:
            from datetime import datetime
            update_data["deleted_at"] = datetime.fromisoformat(update_data["deleted_at"].replace("Z", "+00:00"))
        
        updated_expense = await self.expense_repo.update(expense_id, **update_data)
        await self.db.commit()
        await self.db.refresh(updated_expense)
        return updated_expense
    
    async def delete_expense(
        self,
        expense_id: str,
        current_user: User
    ) -> bool:
        """Soft delete an expense."""
        expense = await self.get_expense(expense_id)
        
        if expense.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this expense"
            )
        
        from datetime import datetime, timezone
        await self.expense_repo.update(expense_id, deleted_at=datetime.now(timezone.utc))
        await self.db.commit()
        return True

