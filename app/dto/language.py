from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class LanguageCreate(SQLModel):
    """Language Create DTO."""

    name: str
    code: str
    description: Optional[str] = None


class LanguageRead(LanguageCreate):
    """Language Read DTO."""

    id: int
    created_at: datetime
    updated_at: datetime
