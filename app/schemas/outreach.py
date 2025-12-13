"""
Outreach Schemas

Pydantic models for outreach-related requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class OutreachDataCreate(BaseModel):
    """Outreach data creation schema."""
    model_config = ConfigDict(from_attributes=True)
    
    account_id: str = Field(..., description="Account UUID")
    mission_id: str = Field(..., description="Mission UUID")
    full_name: str = Field(..., min_length=1, max_length=255, description="Contact's full name")
    phone_number: Optional[str] = Field(None, max_length=50, description="Contact's phone number")
    status: Optional[str] = Field(None, max_length=50, description="Outreach status (e.g., 'interested', 'saved')")


class OutreachDataUpdate(BaseModel):
    """Outreach data update schema."""
    model_config = ConfigDict(from_attributes=True)
    
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    deleted_at: Optional[str] = None


class OutreachDataResponse(BaseModel):
    """Outreach data response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    account_id: str
    mission_id: str
    full_name: str
    phone_number: Optional[str] = None
    status: Optional[str] = None
    created_by_user_id: str
    deleted_at: Optional[str] = None
    created_at: str
    updated_at: str
    
    @classmethod
    def from_outreach_data(cls, outreach_data):
        """Create OutreachDataResponse from OutreachData model."""
        return cls(
            id=str(outreach_data.id),
            account_id=str(outreach_data.account_id),
            mission_id=str(outreach_data.mission_id),
            full_name=outreach_data.full_name,
            phone_number=outreach_data.phone_number,
            status=outreach_data.status,
            created_by_user_id=str(outreach_data.created_by_user_id),
            deleted_at=outreach_data.deleted_at.isoformat() if outreach_data.deleted_at else None,
            created_at=outreach_data.created_at.isoformat() if outreach_data.created_at else "",
            updated_at=outreach_data.updated_at.isoformat() if outreach_data.updated_at else ""
        )


class OutreachNumbersCreate(BaseModel):
    """Outreach numbers creation schema."""
    model_config = ConfigDict(from_attributes=True)
    
    account_id: str = Field(..., description="Account UUID")
    mission_id: str = Field(..., description="Mission UUID")
    interested: int = Field(0, ge=0, description="Number of interested contacts")
    heared: int = Field(0, ge=0, description="Number of contacts who heard")
    saved: int = Field(0, ge=0, description="Number of saved contacts")


class OutreachNumbersUpdate(BaseModel):
    """Outreach numbers update schema."""
    model_config = ConfigDict(from_attributes=True)
    
    interested: Optional[int] = Field(None, ge=0)
    heared: Optional[int] = Field(None, ge=0)
    saved: Optional[int] = Field(None, ge=0)
    deleted_at: Optional[str] = None


class OutreachNumbersResponse(BaseModel):
    """Outreach numbers response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    account_id: str
    mission_id: str
    interested: int
    heared: int
    saved: int
    deleted_at: Optional[str] = None
    created_at: str
    updated_at: str
    
    @classmethod
    def from_outreach_numbers(cls, outreach_numbers):
        """Create OutreachNumbersResponse from OutreachNumbers model."""
        return cls(
            id=str(outreach_numbers.id),
            account_id=str(outreach_numbers.account_id),
            mission_id=str(outreach_numbers.mission_id),
            interested=outreach_numbers.interested,
            heared=outreach_numbers.heared,
            saved=outreach_numbers.saved,
            deleted_at=outreach_numbers.deleted_at.isoformat() if outreach_numbers.deleted_at else None,
            created_at=outreach_numbers.created_at.isoformat() if outreach_numbers.created_at else "",
            updated_at=outreach_numbers.updated_at.isoformat() if outreach_numbers.updated_at else ""
        )

