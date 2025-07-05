from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .dictionary import Dictionary
    from .userProvider import UserProvider
    from .userRefreshToken import UserRefreshToken


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: Optional[str] = Field(index=True)
    email: str = Field(index=True, unique=True)
    hashed_password: Optional[str]

    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    dictionaries: List["Dictionary"] = Relationship(back_populates="user")
    providers: List["UserProvider"] = Relationship(back_populates="user")
    refreshTokens: List["UserRefreshToken"] = Relationship(back_populates="user")
