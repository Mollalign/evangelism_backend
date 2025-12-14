from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel

class Role(BaseModel):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint('name', 'account_id', name='unique_role_per_account'),
    )

    name = Column(String(50), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    description = Column(String(255), nullable=True)

    # Relationships
    account_users = relationship("AccountUser", back_populates="role")
    account = relationship("Account", back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"
