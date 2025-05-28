from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class EntryUpdate(SQLModel):
    original_name: Optional[str] = None
    translation: Optional[str] = None
    description: Optional[str] = None


class EntryCreate(SQLModel):
    """Entry Create DTO."""

    original_name: str
    translation: str
    dictionary_id: int
    description: Optional[str] = None


class EntryRead(EntryCreate):
    """Entry Read DTO."""

    id: int
    display_name: Optional[str]
    created_at: datetime
    updated_at: datetime
