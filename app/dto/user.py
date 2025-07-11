from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class UserCreate(SQLModel):
    """User Create DTO."""

    username: str
    email: str
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserRead(SQLModel):
    """User Read DTO."""

    id: int
    username: str
    email: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    created_at: datetime
    updated_at: datetime


class LoginRequest(SQLModel):
    """Login Request DTO."""

    email: str
    password: str
