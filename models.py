# models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    # Use UUID with proper defaults
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        nullable=False
    )
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    date_created = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationship
    urls = relationship("URL", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class URL(Base):
    __tablename__ = "urls"
    
    # Use UUID with proper defaults
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        nullable=False
    )
    key = Column(String(255), unique=True, index=True, nullable=False)
    secret_key = Column(String(255), unique=True, index=True, nullable=False)
    target_url = Column(String(2048), index=True, nullable=False)  # URLs can be long
    is_active = Column(Boolean, default=True, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    
    # Foreign key relationship
    owner_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True  # Allow anonymous URLs
    )
    date_created = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationship
    owner = relationship("User", back_populates="urls")

    def __repr__(self):
        return f"<URL(id={self.id}, key='{self.key}', target_url='{self.target_url}', is_active={self.is_active})>"