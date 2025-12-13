from sqlalchemy import Column, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel

class Mission(BaseModel):
    __tablename__ = "missions"

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    name = Column(String(255), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    location = Column(JSON, nullable=True)
    budget = Column(Float, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    account = relationship("Account", back_populates="missions")
    users = relationship("MissionUser", back_populates="mission")
    outreach_data = relationship("OutreachData", back_populates="mission")
    outreach_numbers = relationship("OutreachNumbers", back_populates="mission", uselist=False)
    expenses = relationship("Expense", back_populates="mission")

    def __repr__(self):
        return f"<Mission(id={self.id}, name={self.name})>"
