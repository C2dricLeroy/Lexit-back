from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel

from app.dto.language import LanguageRead


class CountryCreate(SQLModel):
    """Country Create DTO."""

    name: str
    code: str
    latitude: Optional[str]
    longitude: Optional[str]
    description: Optional[str] = None


class CountryRead(CountryCreate):
    """Country Read DTO."""

    id: int
    created_at: datetime
    updated_at: datetime
    languages: Optional[List[LanguageRead]]
