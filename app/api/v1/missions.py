"""
Missions API Routes

This module handles mission endpoints:
- GET /api/v1/missions
- POST /api/v1/missions
- GET /api/v1/missions/{id}
- PUT /api/v1/missions/{id}
- DELETE /api/v1/missions/{id}
"""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_database_session, get_current_active_user
from app.models.user import User
from app.schemas.mission import MissionCreate, MissionUpdate, MissionResponse
from app.services.mission import MissionService

router = APIRouter()


@router.get("", response_model=List[MissionResponse])
async def list_missions(
    account_id: str = Query(..., description="Account ID to filter missions"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """List missions for an account."""
    service = MissionService(db)
    missions = await service.get_missions_by_account(account_id, skip, limit)
    return [MissionResponse.from_mission(mission) for mission in missions]


@router.post("", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
async def create_mission(
    mission_data: MissionCreate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new mission."""
    service = MissionService(db)
    mission = await service.create_mission(mission_data, current_user)
    return MissionResponse.from_mission(mission)


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(
    mission_id: str,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get mission by ID."""
    service = MissionService(db)
    mission = await service.get_mission(mission_id)
    return MissionResponse.from_mission(mission)


@router.put("/{mission_id}", response_model=MissionResponse)
async def update_mission(
    mission_id: str,
    mission_data: MissionUpdate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update mission."""
    service = MissionService(db)
    mission = await service.update_mission(mission_id, mission_data, current_user)
    return MissionResponse.from_mission(mission)


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mission(
    mission_id: str,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete mission (soft delete)."""
    service = MissionService(db)
    await service.delete_mission(mission_id, current_user)
    return None
