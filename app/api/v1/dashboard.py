"""
Dashboard API Routes

This module handles dashboard endpoints:
- GET /api/v1/dashboard/stats
- GET /api/v1/dashboard/map
- GET /api/v1/dashboard/summary
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_database_session, get_current_active_user
from app.models.user import User
from app.schemas.dashboard import (
    DashboardStats,
    DashboardMapResponse,
    DashboardSummaryResponse
)
from app.services.dashboard import DashboardService

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    account_id: str = Query(..., description="Account ID to get stats for"),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get aggregated dashboard statistics for an account."""
    service = DashboardService(db)
    return await service.get_dashboard_stats(account_id)


@router.get("/map", response_model=DashboardMapResponse)
async def get_map_data(
    account_id: str = Query(..., description="Account ID to get map data for"),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get mission locations for map visualization."""
    service = DashboardService(db)
    return await service.get_map_data(account_id)


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    account_id: str = Query(..., description="Account ID to get summary for"),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get combined dashboard summary with stats and map data."""
    service = DashboardService(db)
    return await service.get_dashboard_summary(account_id)
