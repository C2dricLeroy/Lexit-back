from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class DictionaryCreate(SQLModel):
    """Dictionary Create DTO."""

    name: str
    description: Optional[str] = None
    source_language_id: int
    target_language_id: int
    user_id: int


class DictionaryRead(DictionaryCreate):
    """Dictionary Read DTO."""

    id: int
    created_at: datetime
    updated_at: datetime
