from sqlmodel import SQLModel, Field
from typing import Optional


class CountryLanguageLink(SQLModel, table=True):
    country_id: Optional[int] = Field(
        default=None,
        foreign_key="country.id",
        primary_key=True
        )
    language_id: Optional[int] = Field(
        default=None,
        foreign_key="language.id",
        primary_key=True
        )