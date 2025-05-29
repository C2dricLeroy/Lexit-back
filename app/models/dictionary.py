from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from .entry import Entry
    from .language import Language
    from .user import User


class Dictionary(SQLModel, table=True):
    """Define a Dictionary Model."""

    __table_args__ = (
        UniqueConstraint(
            "source_language_id",
            "target_language_id",
            name="uix_dictionary_languages",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None, max_length=500)
    display_name: Optional[str] = Field(default=None, nullable=True)

    source_language_id: int = Field(foreign_key="language.id")
    target_language_id: int = Field(foreign_key="language.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    source_language: Optional["Language"] = Relationship(
        back_populates="source_dictionaries",
        sa_relationship_kwargs={
            "foreign_keys": "[Dictionary.source_language_id]"
        },
    )
    target_language: Optional["Language"] = Relationship(
        back_populates="target_dictionaries",
        sa_relationship_kwargs={
            "foreign_keys": "[Dictionary.target_language_id]"
        },
    )
    user: Optional["User"] = Relationship(back_populates="dictionaries")
    entries: List["Entry"] = Relationship(back_populates="dictionary")
