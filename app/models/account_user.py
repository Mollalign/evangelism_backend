from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel

class AccountUser(BaseModel):
    __tablename__ = "account_users"

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    account = relationship("Account", back_populates="users")
    user = relationship("User", back_populates="accounts")
    role = relationship("Role", back_populates="account_users")

    def __repr__(self):
        return f"<AccountUser(account_id={self.account_id}, user_id={self.user_id}, role_id={self.role_id})>"
