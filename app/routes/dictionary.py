from logging import getLogger

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from starlette.requests import Request

from app.database import get_session
from app.dto.dictionary import (
    DictionaryCreate,
    DictionaryRead,
    DictionaryUpdate,
)
from app.main import limiter
from app.models.dictionary import Dictionary
from app.models.user import User
from app.services.dictionary import compute_display_name

router = APIRouter()
_logger = getLogger(__name__)


@router.get("/", response_model=list[DictionaryRead])
@limiter.limit("10/minute")
def get_dictionaries(
    request: Request, session: Session = Depends(get_session)
):
    """Return all dictionaries."""
    return session.exec(select(Dictionary)).all()


@router.get("/{id}", response_model=list[DictionaryRead])
@limiter.limit("1000/day")
def get_dictionary_by_id(
    request: Request,
    dictionary_id: int,
    session: Session = Depends(get_session),
):
    """Return a dictionary by its ID."""
    return session.exec(
        select(Dictionary).where(Dictionary.id == dictionary_id)
    ).first()


@router.post("/", response_model=DictionaryRead, status_code=201)
@limiter.limit("10/minute")
def create_dictionary(
    request: Request,
    dictionary: DictionaryCreate,
    session: Session = Depends(get_session),
):
    """Create a new dictionary."""
    db_user = session.get(User, dictionary.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_dictionary = Dictionary(**dictionary.model_dump())
    db_dictionary = compute_display_name(db_dictionary)
    db_user.dictionaries.append(db_dictionary)

    try:
        session.commit()
        session.refresh(db_dictionary)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="A dictionary with these languages already exists.",
        ) from exc
    return db_dictionary


@router.put("/{dictionary_id}", response_model=DictionaryRead)
@limiter.limit("5/minute")
def update_dictionary(
    request: Request,
    dictionary_id: int,
    dictionary_update: DictionaryUpdate,
    session: Session = Depends(get_session),
):
    """Update a dictionary by its ID."""
    db_dictionary = session.get(Dictionary, dictionary_id)
    if not db_dictionary:
        raise HTTPException(status_code=404, detail="Dictionary not found")

    update_data = dictionary_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_dictionary, key, value)

    try:
        session.commit()
        session.refresh(db_dictionary)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="A dictionary with these languages already exists.",
        ) from exc
    return db_dictionary


@router.delete("/{dictionary_id}", status_code=204)
@limiter.limit("10/minute")
def delete_dictionary(
    request: Request,
    dictionary_id: int,
    session: Session = Depends(get_session),
):
    """Delete a dictionary by its ID."""
    db_dictionary = session.get(Dictionary, dictionary_id)
    if not db_dictionary:
        raise HTTPException(status_code=404, detail="Dictionary not found")

    try:
        session.delete(db_dictionary)
        session.commit()
    except Exception as exc:
        session.rollback()
        _logger.error("Error deleting dictionary %s: %s", dictionary_id, exc)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting the dictionary",
        ) from exc
    return {
        "message": "Dictionary %s deleted successfully!",
        dictionary_id: dictionary_id,
    }
