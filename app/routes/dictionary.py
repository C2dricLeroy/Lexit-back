from logging import getLogger

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.dto.dictionary import DictionaryCreate, DictionaryRead
from app.models.dictionary import Dictionary
from app.models.user import User

router = APIRouter()
_logger = getLogger(__name__)


@router.get("/", response_model=list[DictionaryRead])
def get_dictionaries(session: Session = Depends(get_session)):
    """Return all dictionaries."""
    return session.exec(select(Dictionary)).all()


@router.get("/{id}", response_model=list[DictionaryRead])
def get_dictionary_by_id(
    dictionary_id: int, session: Session = Depends(get_session)
):
    """Return a dictionary by its ID."""
    return session.exec(
        select(Dictionary).where(Dictionary.id == dictionary_id)
    ).first()


@router.post("/", response_model=DictionaryRead, status_code=201)
def create_dictionary(
    dictionary: DictionaryCreate, session: Session = Depends(get_session)
):
    """Create a new dictionary."""
    db_user = session.get(User, dictionary.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_dictionary = Dictionary(**dictionary.model_dump())
    db_user.dictionaries.append(db_dictionary)  # Facultatif mais explicite

    session.add(db_dictionary)
    session.commit()
    session.refresh(db_dictionary)
    return db_dictionary
