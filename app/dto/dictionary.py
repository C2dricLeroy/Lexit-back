from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel

from app.dto.language import LanguageRead


class DictionaryCreate(SQLModel):
    """Dictionary Create DTO."""

    name: str
    code: str
    description: Optional[str] = None
    source_language_id: int
    target_language_id: int
    user_id: int


class DictionaryRead(DictionaryCreate):
    """Dictionary Read DTO."""

    id: int
    created_at: datetime
    updated_at: datetime
    languages: Optional[List[LanguageRead]]
