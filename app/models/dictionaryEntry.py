from sqlmodel import SQLModel, Field
from typing import Optional


class DictionaryEntryLink(SQLModel, table=True):
    dictionary_id: Optional[int] = Field(default=None, foreign_key="dictionary.id", primary_key=True)
    entry_id: Optional[int] = Field(default=None, foreign_key="entry.id", primary_key=True)
