from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from .countryLanguage import CountryLanguageLink

if TYPE_CHECKING:
    from .language import Language


class Country(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    code: str = Field(max_length=100, unique=True)
    latitude: Optional[str] = Field(default=None, max_length=100)
    longitude: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    languages: List["Language"] = Relationship(
        back_populates="countries",
        link_model=CountryLanguageLink
        )