from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel

class Expense(BaseModel):
    __tablename__ = "expenses"

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=True) # Nullable for account-level expenses
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    account = relationship("Account", back_populates="expenses")
    mission = relationship("Mission", back_populates="expenses")
    user = relationship("User") # No back_populates needed on User for now, unless requested

    def __repr__(self):
        return f"<Expense(id={self.id}, amount={self.amount}, category={self.category})>"
