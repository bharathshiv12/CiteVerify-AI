"""
User and auth schemas.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    id: UUID
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    institution: Optional[str] = None
    role: str = "authenticated"


class User(UserBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserProfile(BaseModel):
    id: UUID
    full_name: Optional[str] = None
    institution: Optional[str] = None
    email: Optional[str] = None
    updated_at: Optional[datetime] = None


class AuthMeResponse(BaseModel):
    user: User
