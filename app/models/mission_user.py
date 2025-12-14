import enum
from sqlalchemy import Column, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel

class MissionRole(str, enum.Enum):
    LEADER = "leader"
    MEMBER = "member"
    GUEST = "guest"
    EVANGELIST = "evangelist"
    MISSIONARY = "missionary"

class MissionUser(BaseModel):
    __tablename__ = "mission_users"

    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(Enum(MissionRole), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    mission = relationship("Mission", back_populates="users")
    user = relationship("User", back_populates="missions")

    def __repr__(self):
        return f"<MissionUser(mission_id={self.mission_id}, user_id={self.user_id}, role={self.role})>"
