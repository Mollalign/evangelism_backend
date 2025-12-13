"""
Expenses API Routes

This module handles expense endpoints:
- GET /api/v1/expenses
- POST /api/v1/expenses
- PUT /api/v1/expenses/{id}
- DELETE /api/v1/expenses/{id}
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_database_session, get_current_active_user
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.services.expense import ExpenseService

router = APIRouter()


@router.get("", response_model=List[ExpenseResponse])
async def list_expenses(
    mission_id: Optional[str] = Query(None, description="Mission ID to filter expenses"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """List expenses, optionally filtered by mission."""
    service = ExpenseService(db)
    
    if mission_id:
        expenses = await service.get_expenses_by_mission(mission_id, skip, limit)
    else:
        # Get user's expenses if no mission_id provided
        expenses = await service.expense_repo.get_by_user(str(current_user.id), skip, limit)
    
    return [ExpenseResponse.from_expense(expense) for expense in expenses]


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new expense."""
    service = ExpenseService(db)
    expense = await service.create_expense(expense_data, current_user)
    return ExpenseResponse.from_expense(expense)


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    expense_data: ExpenseUpdate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update expense."""
    service = ExpenseService(db)
    expense = await service.update_expense(expense_id, expense_data, current_user)
    return ExpenseResponse.from_expense(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: str,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete expense (soft delete)."""
    service = ExpenseService(db)
    await service.delete_expense(expense_id, current_user)
    return None
