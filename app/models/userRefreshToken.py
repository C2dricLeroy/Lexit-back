from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User


class UserRefreshToken(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    user: Optional["User"] = Relationship(back_populates="refreshTokens")
    refresh_token: str = Field(index=True)
    user_agent: Optional[str] = Field()
    revoked: bool = Field(default=False)
    created_at: datetime = Field(default=datetime.now())
