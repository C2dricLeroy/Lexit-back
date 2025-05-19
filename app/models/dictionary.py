from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .language import Language
    from .user import User
    from .entry import Entry


class Dictionary(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    source_language_id: int = Field(foreign_key="language.id")
    target_language_id: int = Field(foreign_key="language.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    source_language: Optional["Language"] = Relationship(back_populates="source_dictionaries", sa_relationship_kwargs={"foreign_keys": "[Dictionary.source_language_id]"})
    target_language: Optional["Language"] = Relationship(back_populates="target_dictionaries", sa_relationship_kwargs={"foreign_keys": "[Dictionary.target_language_id]"})
    user: Optional["User"] = Relationship(back_populates="dictionaries")
    entries: List["Entry"] = Relationship(back_populates="dictionaries", link_model="DictionaryEntryLink")
