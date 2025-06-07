from datetime import datetime
from logging import getLogger

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from starlette.requests import Request

from app.database import get_session
from app.dto.entry import EntryCreate, EntryRead, EntryUpdate
from app.main import limiter
from app.models.entry import Entry
from app.services.entry import compute_display_name

router = APIRouter()
_logger = getLogger(__name__)


@router.get("/", response_model=list[EntryRead])
@limiter.limit("1000/day")
def get_entries(request: Request, session: Session = Depends(get_session)):
    """Return all entries."""
    return session.exec(select(Entry)).all()


@router.get("/{id}", response_model=EntryRead)
@limiter.limit("1000/day")
def get_entry_by_id(
    request: Request, entry_id: int, session: Session = Depends(get_session)
):
    """Return an entry by its ID."""
    return session.exec(select(Entry).where(Entry.id == entry_id)).first()


@router.get("/dictionary/{dictionary_id}", response_model=list[EntryRead])
@limiter.limit("5000/day")
def get_entries_by_dictionary_id(
    request: Request,
    dictionary_id: int,
    session: Session = Depends(get_session),
):
    """Return all entries for a given dictionary."""
    return session.exec(
        select(Entry).where(Entry.dictionary_id == dictionary_id)
    ).all()


@router.post("/", response_model=EntryRead, status_code=201)
@limiter.limit("100/minute")
def create_entry(
    request: Request,
    entry: EntryCreate,
    session: Session = Depends(get_session),
):
    """Create a new entry."""
    db_dictionary = session.get(Entry, entry.dictionary_id)
    if not db_dictionary:
        raise HTTPException(status_code=404, detail="Dictionary not found")

    db_entry = Entry(**entry.model_dump())
    db_entry = compute_display_name(db_entry)

    db_dictionary.entries.append(db_entry)

    session.add(db_entry)
    try:
        session.commit()
        session.refresh(db_entry)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="An entry with this name already exists in the dictionary.",
        ) from exc

    return db_entry


@router.delete("/{entry_id}", status_code=204)
@limiter.limit("10/minute")
def delete_entry(
    request: Request, entry_id: int, session: Session = Depends(get_session)
):
    """Delete a entry by its ID."""
    db_entry = session.get(Entry, entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    try:
        session.delete(db_entry)
        session.commit()
    except Exception as exc:
        session.rollback()
        _logger.error("Error deleting entry %s: %s", entry_id, exc)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting the entry",
        ) from exc

    return {"message": "Entry %s deleted successfully!", entry_id: entry_id}


@router.patch("/{entry_id}", response_model=EntryRead)
@limiter.limit("10/minute")
def update_entry(
    request: Request,
    entry_id: int,
    entry_update: EntryUpdate,
    session: Session = Depends(get_session),
):
    """Update an entry by its ID."""
    db_entry = session.get(Entry, entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry_data = entry_update.model_dump(exclude_unset=True)

    for key, value in entry_data.items():
        setattr(db_entry, key, value)

    if "original_name" in entry_data or "translation" in entry_data:
        db_entry = compute_display_name(db_entry)

    db_entry.updated_at = datetime.now()

    try:
        session.add(db_entry)
        session.commit()
        session.refresh(db_entry)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="An entry with this name already exists in this dictionary.",
        ) from exc

    return db_entry
