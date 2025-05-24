from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .countryLanguage import CountryLanguageLink

if TYPE_CHECKING:
    from .country import Country
    from .dictionary import Dictionary


class Language(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    code: str = Field(max_length=100, unique=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    countries: List["Country"] = Relationship(
        back_populates="languages", link_model=CountryLanguageLink
    )

    source_dictionaries: List["Dictionary"] = Relationship(
        back_populates="source_language",
        sa_relationship_kwargs={
            "foreign_keys": "[Dictionary.source_language_id]"
        },
    )
    target_dictionaries: List["Dictionary"] = Relationship(
        back_populates="target_language",
        sa_relationship_kwargs={
            "foreign_keys": "[Dictionary.target_language_id]"
        },
    )
