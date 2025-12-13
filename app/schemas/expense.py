"""
Expense Schemas

Pydantic models for expense-related requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ExpenseCreate(BaseModel):
    """Expense creation schema."""
    model_config = ConfigDict(from_attributes=True)
    
    account_id: str = Field(..., description="Account UUID")
    mission_id: Optional[str] = Field(None, description="Mission UUID (optional for account-level expenses)")
    category: str = Field(..., min_length=1, max_length=100, description="Expense category")
    amount: float = Field(..., gt=0, description="Expense amount (must be positive)")
    description: Optional[str] = Field(None, max_length=255, description="Expense description")


class ExpenseUpdate(BaseModel):
    """Expense update schema."""
    model_config = ConfigDict(from_attributes=True)
    
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=255)
    deleted_at: Optional[str] = None


class ExpenseResponse(BaseModel):
    """Expense response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    account_id: str
    mission_id: Optional[str] = None
    user_id: str
    category: str
    amount: float
    description: Optional[str] = None
    deleted_at: Optional[str] = None
    created_at: str
    updated_at: str
    
    @classmethod
    def from_expense(cls, expense):
        """Create ExpenseResponse from Expense model."""
        return cls(
            id=str(expense.id),
            account_id=str(expense.account_id),
            mission_id=str(expense.mission_id) if expense.mission_id else None,
            user_id=str(expense.user_id),
            category=expense.category,
            amount=expense.amount,
            description=expense.description,
            deleted_at=expense.deleted_at.isoformat() if expense.deleted_at else None,
            created_at=expense.created_at.isoformat() if expense.created_at else "",
            updated_at=expense.updated_at.isoformat() if expense.updated_at else ""
        )

