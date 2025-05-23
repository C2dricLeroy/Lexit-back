from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from .dictionaryEntry import DictionaryEntryLink

if TYPE_CHECKING:
    from .dictionary import Dictionary
    from .description import Description


class Entry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_name: str
    display_name: str
    translation: str
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    descriptions: List["Description"] = Relationship(back_populates="entry")

    dictionaries: List["Dictionary"] = Relationship(back_populates="entries", link_model=DictionaryEntryLink)
