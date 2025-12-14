"""
Account Schemas

Pydantic models for account-related requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AccountResponse(BaseModel):
    """Account response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    account_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    created_by: str
    is_active: bool
    created_at: str
    updated_at: str
    
    @classmethod
    def from_account(cls, account):
        """Create AccountResponse from Account model."""
        from datetime import datetime
        return cls(
            id=str(account.id),
            account_name=account.account_name,
            email=account.email,
            phone_number=account.phone_number,
            location=account.location,
            created_by=str(account.created_by),
            is_active=account.is_active,
            created_at=account.created_at.isoformat() if account.created_at else datetime.utcnow().isoformat(),
            updated_at=account.updated_at.isoformat() if account.updated_at else datetime.utcnow().isoformat()
        )
