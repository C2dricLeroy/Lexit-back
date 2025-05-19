from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .dictionary import Dictionary


class Entry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_name: str
    display_name: str
    translation: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    dictionaries: List["Dictionary"] = Relationship(back_populates="entries", link_model="DictionaryEntryLink")
