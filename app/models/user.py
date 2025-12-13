from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    accounts = relationship("AccountUser", back_populates="user")
    missions = relationship("MissionUser", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
