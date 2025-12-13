"""
Users API Routes

This module handles user endpoints:
- GET /api/v1/users
"""

from fastapi import APIRouter

router = APIRouter()

# TODO: Implement user endpoints
# These will be implemented once schemas, services, and repositories are ready

@router.get("")
async def list_users():
    """List users (typically account-scoped)."""
    return {"message": "List users endpoint - to be implemented"}

