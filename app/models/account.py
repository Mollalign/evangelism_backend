from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel

class Account(BaseModel):
    __tablename__ = "accounts"

    account_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    users = relationship("AccountUser", back_populates="account")
    missions = relationship("Mission", back_populates="account")
    expenses = relationship("Expense", back_populates="account")
    # roles = relationship("Role", back_populates="account") # Roles are global

    def __repr__(self):
        return f"<Account(id={self.id}, name={self.account_name})>"
