"""
Mission Schemas

Pydantic models for mission-related requests and responses.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class MissionCreate(BaseModel):
    """Mission creation schema."""
    model_config = ConfigDict(from_attributes=True)
    
    account_id: str = Field(..., description="Account UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Mission name")
    start_date: Optional[datetime] = Field(None, description="Mission start date")
    end_date: Optional[datetime] = Field(None, description="Mission end date")
    location: Optional[Dict[str, Any]] = Field(None, description="Location data (JSON)")
    budget: Optional[float] = Field(None, ge=0, description="Mission budget")
    
    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v, info):
        """Validate end_date is after start_date."""
        if v and "start_date" in info.data and info.data["start_date"]:
            if v < info.data["start_date"]:
                raise ValueError("end_date must be after start_date")
        return v


class MissionUpdate(BaseModel):
    """Mission update schema."""
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[Dict[str, Any]] = None
    budget: Optional[float] = Field(None, ge=0)
    deleted_at: Optional[datetime] = None


class MissionResponse(BaseModel):
    """Mission response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    account_id: str
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    budget: Optional[float] = None
    created_by: str
    deleted_at: Optional[str] = None
    created_at: str
    updated_at: str
    
    @classmethod
    def from_mission(cls, mission):
        """Create MissionResponse from Mission model."""
        return cls(
            id=str(mission.id),
            account_id=str(mission.account_id),
            name=mission.name,
            start_date=mission.start_date.isoformat() if mission.start_date else None,
            end_date=mission.end_date.isoformat() if mission.end_date else None,
            location=mission.location,
            budget=mission.budget,
            created_by=str(mission.created_by),
            deleted_at=mission.deleted_at.isoformat() if mission.deleted_at else None,
            created_at=mission.created_at.isoformat() if mission.created_at else "",
            updated_at=mission.updated_at.isoformat() if mission.updated_at else ""
        )

