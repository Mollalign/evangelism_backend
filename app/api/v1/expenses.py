"""
Expenses API Routes

This module handles expense endpoints:
- GET /api/v1/expenses
- POST /api/v1/expenses
- PUT /api/v1/expenses/{id}
- DELETE /api/v1/expenses/{id}
"""

from fastapi import APIRouter

router = APIRouter()

# TODO: Implement expense endpoints
# These will be implemented once schemas, services, and repositories are ready

@router.get("")
async def list_expenses():
    """List expenses for a mission."""
    return {"message": "List expenses endpoint - to be implemented"}


@router.post("")
async def create_expense():
    """Create a new expense."""
    return {"message": "Create expense endpoint - to be implemented"}


@router.put("/{expense_id}")
async def update_expense(expense_id: str):
    """Update expense."""
    return {"message": f"Update expense {expense_id} endpoint - to be implemented"}


@router.delete("/{expense_id}")
async def delete_expense(expense_id: str):
    """Delete expense."""
    return {"message": f"Delete expense {expense_id} endpoint - to be implemented"}

