from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.security.password import check_password, hash_password
from app.database import get_session
from app.dto.dictionary import DictionaryRead
from app.dto.user import LoginRequest, UserCreate, UserRead
from app.models import Dictionary, User

router = APIRouter()
_logger = getLogger(__name__)


@router.get("/", response_model=list[UserRead])
def get_users(session: Session = Depends(get_session)):
    """Return all users."""
    return session.exec(select(User)).all()


@router.get("/{id}", response_model=list[UserRead])
def get_user_by_id(user_id: int, session: Session = Depends(get_session)):
    """Return a user by its ID."""
    return session.exec(select(User).where(User.id == user_id)).first()


@router.get("/dictionary/{user_id}", response_model=list[DictionaryRead])
def get_user_dictionaries(
    user_id: int, session: Session = Depends(get_session)
):
    """Return dictionaries belonging to a user."""
    return session.exec(
        select(Dictionary).where(Dictionary.user_id == user_id)
    ).all()


@router.post("/signup", response_model=UserRead, status_code=201)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
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


@router.post("/login", response_model=UserRead, summary="Login a user")
def login(
    login_request: LoginRequest, session: Session = Depends(get_session)
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

    return user
