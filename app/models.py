from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    checks = relationship("CodeCheck", back_populates="user", cascade="all, delete-orphan")
    error_stats = relationship("ErrorStatistic", back_populates="user", cascade="all, delete-orphan")


class CodeCheck(Base):
    __tablename__ = "code_checks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    code_snippet = Column(Text, nullable=False)
    errors_found = Column(Integer, default=0)
    errors_details = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="checks")


class ErrorStatistic(Base):
    __tablename__ = "error_statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    error_type = Column(String(100), nullable=False)
    count = Column(Integer, default=1)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="error_stats")