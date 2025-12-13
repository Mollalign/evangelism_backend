"""
Outreach API Routes

This module handles outreach endpoints:
- GET /api/v1/outreach/data
- POST /api/v1/outreach/data
- GET /api/v1/outreach/numbers
- POST /api/v1/outreach/numbers
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_database_session, get_current_active_user
from app.models.user import User
from app.schemas.outreach import (
    OutreachDataCreate,
    OutreachDataUpdate,
    OutreachDataResponse,
    OutreachNumbersCreate,
    OutreachNumbersResponse
)
from app.services.outreach import OutreachService

router = APIRouter()


@router.get("/data", response_model=List[OutreachDataResponse])
async def list_outreach_data(
    mission_id: Optional[str] = Query(None, description="Mission ID to filter outreach data"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """List outreach data, optionally filtered by mission."""
    service = OutreachService(db)
    
    if mission_id:
        data = await service.get_outreach_data_by_mission(mission_id, skip, limit)
    else:
        # Get all for user's missions if no mission_id
        data = []
    
    return [OutreachDataResponse.from_outreach_data(item) for item in data]


@router.post("/data", response_model=OutreachDataResponse, status_code=status.HTTP_201_CREATED)
async def create_outreach_data(
    outreach_data: OutreachDataCreate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create new outreach data."""
    service = OutreachService(db)
    data = await service.create_outreach_data(outreach_data, current_user)
    return OutreachDataResponse.from_outreach_data(data)


@router.get("/numbers", response_model=Optional[OutreachNumbersResponse])
async def get_outreach_numbers(
    mission_id: str = Query(..., description="Mission ID"),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get outreach numbers for a mission."""
    service = OutreachService(db)
    numbers = await service.get_outreach_numbers(mission_id)
    
    if not numbers:
        return None
    
    return OutreachNumbersResponse.from_outreach_numbers(numbers)


@router.post("/numbers", response_model=OutreachNumbersResponse)
async def create_or_update_outreach_numbers(
    numbers_data: OutreachNumbersCreate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create or update outreach numbers for a mission."""
    service = OutreachService(db)
    numbers = await service.get_or_create_outreach_numbers(numbers_data)
    return OutreachNumbersResponse.from_outreach_numbers(numbers)
