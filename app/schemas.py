from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ErrorDetail(BaseModel):
    line: int
    type: str
    message: str
    fix: str
    resource: str
    severity: str = "warning"


class CodeAnalysisRequest(BaseModel):
    code: str
    user_id: Optional[int] = None


class CodeAnalysisResponse(BaseModel):
    check_id: int
    errors_count: int
    errors: List[ErrorDetail]
    score: float
    recommendations: List[str]
    created_at: datetime


class ErrorStatisticResponse(BaseModel):
    error_type: str
    count: int
    last_seen: datetime

    class Config:
        from_attributes = True


class UserStatistics(BaseModel):
    total_checks: int
    total_errors: int
    error_types: List[ErrorStatisticResponse]
    progress: Dict[str, Any]