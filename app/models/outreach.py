from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel

class OutreachData(BaseModel):
    __tablename__ = "outreach_data"

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=True)
    status = Column(String(50), nullable=True) # e.g., "interested", "saved"
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    mission = relationship("Mission", back_populates="outreach_data")

    def __repr__(self):
        return f"<OutreachData(id={self.id}, full_name={self.full_name})>"


class OutreachNumbers(BaseModel):
    __tablename__ = "outreach_numbers"

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), unique=True, nullable=False, index=True)
    interested = Column(Integer, default=0, nullable=False)
    heared = Column(Integer, default=0, nullable=False)
    saved = Column(Integer, default=0, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    mission = relationship("Mission", back_populates="outreach_numbers")

    def __repr__(self):
        return f"<OutreachNumbers(mission_id={self.mission_id}, saved={self.saved})>"
