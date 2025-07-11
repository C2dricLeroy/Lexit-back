from logging import getLogger

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import count
from sqlmodel import Session, select
from starlette.requests import Request

from app.core.limiter import limiter
from app.database import get_session
from app.dto.dictionary import (
    DictionaryCreate,
    DictionaryRead,
    DictionaryUpdate,
)
from app.models.dictionary import Dictionary
from app.models.entry import Entry
from app.models.user import User
from app.services.dictionary import compute_display_name
from app.services.user import get_current_user

router = APIRouter()
_logger = getLogger(__name__)


@router.get("/", response_model=list[DictionaryRead])
@limiter.limit("10/minute")
def get_dictionaries(
    request: Request, session: Session = Depends(get_session)
):
    """Return all dictionaries with entry count."""
    dictionaries = session.exec(select(Dictionary)).all()

    results = []
    for d in dictionaries:
        entry_count = session.exec(
            select(count())
            .select_from(Entry)
            .where(Entry.dictionary_id == d.id)
        ).one()
        results.append(
            DictionaryRead(**d.model_dump(), entry_count=entry_count)
        )

    return results


@router.get("/{dictionary_id}", response_model=DictionaryRead)
def get_dictionary_by_id(
    request: Request,
    dictionary_id: int,
    session: Session = Depends(get_session),
):
    """Get a dictionary by its ID with entry count."""
    dictionary = session.exec(
        select(Dictionary).where(Dictionary.id == dictionary_id)
    ).first()

    if not dictionary:
        raise HTTPException(status_code=404, detail="Dictionary not found")

    entry_count = session.exec(
        select(count())
        .select_from(Entry)
        .where(Entry.dictionary_id == dictionary_id)
    ).one()

    return DictionaryRead(**dictionary.model_dump(), entry_count=entry_count)


@router.post("/", response_model=DictionaryRead, status_code=201)
@limiter.limit("10/minute")
def create_dictionary(
    request: Request,
    dictionary: DictionaryCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new dictionary."""
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_dictionary = Dictionary(**dictionary.model_dump())
    db_dictionary.user = user
    db_dictionary = compute_display_name(session, db_dictionary)
    session.add(db_dictionary)

    try:
        session.commit()
        session.refresh(db_dictionary)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="A dictionary with these languages already exists.",
        ) from exc
    return DictionaryRead(**db_dictionary.model_dump(), entry_count=0)


@router.put("/{dictionary_id}", response_model=DictionaryRead)
@limiter.limit("5/minute")
def update_own_dictionary(
    request: Request,
    dictionary_id: int,
    dictionary_update: DictionaryUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update a dictionary by its ID."""
    db_dictionary = session.get(Dictionary, dictionary_id)
    if not db_dictionary:
        raise HTTPException(status_code=404, detail="Dictionary not found")

    if db_dictionary.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to update this dictionary.",
        )

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

    entry_count = session.exec(
        select(count())
        .select_from(Entry)
        .where(Entry.dictionary_id == dictionary_id)
    ).one()

    return DictionaryRead(
        **db_dictionary.model_dump(), entry_count=entry_count
    )


@router.put("/admin/{dictionary_id}", response_model=DictionaryRead)
@limiter.limit("5/minute")
def admin_update_dictionary(
    request: Request,
    dictionary_id: int,
    dictionary_update: DictionaryUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Admin update a dictionary by its ID."""
    db_dictionary = session.get(Dictionary, dictionary_id)
    if not db_dictionary:
        raise HTTPException(status_code=404, detail="Dictionary not found")

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to update this dictionary.",
        )

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

    entry_count = session.exec(
        select(count())
        .select_from(Entry)
        .where(Entry.dictionary_id == dictionary_id)
    ).one()

    return DictionaryRead(
        **db_dictionary.model_dump(), entry_count=entry_count
    )


@router.delete("/{dictionary_id}", status_code=204)
@limiter.limit("10/minute")
def delete_own_dictionary(
    request: Request,
    dictionary_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a dictionary by its ID."""
    db_dictionary = session.get(Dictionary, dictionary_id)
    if not db_dictionary:
        raise HTTPException(status_code=404, detail="Dictionary not found")

    if db_dictionary.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to delete this dictionary.",
        )

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


@router.delete("/admin/{dictionary_id}", status_code=204)
@limiter.limit("10/minute")
def admin_delete_dictionary(
    request: Request,
    dictionary_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a dictionary by its ID."""
    db_dictionary = session.get(Dictionary, dictionary_id)
    if not db_dictionary:
        raise HTTPException(status_code=404, detail="Dictionary not found")

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to delete this dictionary.",
        )

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
