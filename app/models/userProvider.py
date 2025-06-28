from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User


class UserProvider(SQLModel, table=True):
    __tablename__ = "user_providers"

    id: Optional[int] = Field(default=None, primary_key=True)

    provider: str = Field(index=True)
    provider_user_id: str = Field(index=True)

    user_id: int = Field(foreign_key="user.id", index=True)
    user: Optional["User"] = Relationship(back_populates="providers")
