from logging import getLogger

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.dto.dictionary import DictionaryRead
from app.models.dictionary import Dictionary

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
