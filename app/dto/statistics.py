from datetime import date

from sqlmodel import SQLModel


class WordsOverTimePoint(SQLModel):
    date: date
    count: int


class WordsOverTimeRead(SQLModel):
    """Words Over Time DTO."""

    dictionary_id: int
    dictionary_name: str
    data: list[WordsOverTimePoint]
