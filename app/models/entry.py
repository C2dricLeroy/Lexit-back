from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from app.models.dictionary import Dictionary


class Entry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_name: str
    display_name: Optional[str] = Field(default=None, nullable=True)
    translation: str
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    description: Optional[str] = None

    dictionary_id: int = Field(default=None, foreign_key="dictionary.id")
    dictionary: Optional["Dictionary"] = Relationship(back_populates="entries")

    __table_args__ = (
        UniqueConstraint(
            "original_name", "dictionary_id", name="uix_entry_name_dict"
        ),
    )
