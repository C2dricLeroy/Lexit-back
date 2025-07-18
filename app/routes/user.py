from datetime import timedelta
from logging import getLogger

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select
from starlette.requests import Request

from app.config import settings
from app.core.limiter import limiter
from app.core.security.password import (
    check_password,
    create_access_token,
    hash_password,
)
from app.database import get_session
from app.dto.dictionary import DictionaryRead
from app.dto.user import LoginRequest, UserCreate, UserRead
from app.models import User
from app.services.user import get_current_user

router = APIRouter()
_logger = getLogger(__name__)


@router.get("/", response_model=list[UserRead])
@limiter.limit("5/minute")
def get_users(request: Request, session: Session = Depends(get_session)):
    """Return all users."""
    return session.exec(select(User)).all()


@router.get("/me", response_model=UserRead)
@limiter.limit("1000/day")
def read_me(request: Request, current_user: User = Depends(get_current_user)):
    """Return the current authenticated user."""
    return current_user


@router.get("/dictionary", response_model=list[DictionaryRead])
@limiter.limit("1000/day")
def get_user_dictionaries(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Return dictionaries belonging to a user."""
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user.dictionaries


@router.get("/{user_id}", response_model=list[UserRead])
@limiter.limit("1000/day")
def get_user_by_id(
    request: Request, user_id: int, session: Session = Depends(get_session)
):
    """Return a user by its ID."""
    return session.exec(select(User).where(User.id == user_id)).first()


@router.post("/signup", response_model=UserRead, status_code=201)
@limiter.limit("10/minute")
def create_user(
    request: Request, user: UserCreate, session: Session = Depends(get_session)
):
    """Create a new user."""
    db_user = db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        is_active=user.is_active,
        is_superuser=user.is_superuser,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/login", summary="Login a user")
@limiter.limit("10/minute")
def login(
    request: Request,
    login_request: LoginRequest,
    session: Session = Depends(get_session),
):
    """Authenticate a user by email and password."""
    user = session.exec(
        select(User).where(User.email == login_request.email)
    ).first()

    if not user or not check_password(
        login_request.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.delete("/admin/{user_id}", response_model=UserRead)
@limiter.limit("5/minute")
def admin_delete_user(
    request: Request,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a user by its ID."""
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.id == current_user.id:
        raise HTTPException(status_code=403, detail="Cannot delete yourself")

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to delete this user.",
        )

    session.delete(db_user)
    session.commit()
    return {"message": "User deleted successfully"}
