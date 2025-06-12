from logging import getLogger

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.security.password import decode_access_token
from app.database import get_session
from app.models import User

_logger = getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/user/login/",
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    """Return the current authenticated user from the JWT token."""
    payload = decode_access_token(token)

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = session.exec(select(User).where(User.id == int(user_id))).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
