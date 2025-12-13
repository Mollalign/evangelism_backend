"""
Main API Router

This module aggregates all API version routers.
"""

from fastapi import APIRouter

# Import version routers
from app.api.v1 import auth, missions, expenses, outreach, users

# Create main API router
api_router = APIRouter()

# Include version routers
api_router.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
api_router.include_router(missions.router, prefix="/v1/missions", tags=["Missions"])
api_router.include_router(expenses.router, prefix="/v1/expenses", tags=["Expenses"])
api_router.include_router(outreach.router, prefix="/v1/outreach", tags=["Outreach"])
api_router.include_router(users.router, prefix="/v1/users", tags=["Users"])

# API info endpoint
@api_router.get("/v1")
async def api_info():
    """API version information."""
    return {
        "version": "v1",
        "status": "active",
        "endpoints": {
            "auth": "/api/v1/auth",
            "missions": "/api/v1/missions",
            "expenses": "/api/v1/expenses",
            "outreach": "/api/v1/outreach",
            "users": "/api/v1/users"
        }
    }

