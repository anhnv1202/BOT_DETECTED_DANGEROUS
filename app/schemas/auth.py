from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password: tối thiểu 6 ký tự, không giới hạn tối đa"""
        if len(v) < 6:
            raise ValueError('Password phải có ít nhất 6 ký tự')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    avatar: Optional[str]
    credits: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class GoogleAuthRequest(BaseModel):
    code: str



