from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel

class Role(BaseModel):
    __tablename__ = "roles"
    
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    # Relationships
    account_users = relationship("AccountUser", back_populates="role")
    # account relationship removed as roles are now global

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"
