from typing import Optional
from pydantic import BaseModel, UUID4, EmailStr

class AccountCreate(BaseModel):
    account_name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None

class AccountResponse(BaseModel):
    id: UUID4
    account_name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    is_active: bool
    created_by: UUID4

    class Config:
        from_attributes = True

class AccountJoinRequest(BaseModel):
    # Depending on how we identify the account. Usually by ID or name?
    # Requirement: "Request to join an existing account."
    # Ideally by ID? Or maybe by Invite Code?
    # I'll stick to ID for now, as search is separate.
    account_id: UUID4
