from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from sqlmodel import Session, select

from app.core.security.password import decode_access_token
from app.database import get_session
from app.models import User

bearer_scheme = HTTPBearer()


def get_current_user(
    request: Request, session: Session = Depends(get_session)
) -> User:
    """Return the current authenticated user."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )

    token = auth_header.split(" ")[1]

    try:
        payload = decode_access_token(token)
    except HTTPException as e:
        raise e

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = session.exec(select(User).where(User.id == int(user_id))).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
