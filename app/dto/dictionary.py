from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class DictionaryCreate(SQLModel):
    """Dictionary Create DTO."""

    name: str
    description: Optional[str] = None
    source_language_id: int
    target_language_id: int


class DictionaryRead(DictionaryCreate):
    """Dictionary Read DTO."""

    id: int
    display_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    entry_count: int


class DictionaryUpdate(SQLModel):
    """Dictionary Update DTO."""

    name: Optional[str] = None
    description: Optional[str] = None
