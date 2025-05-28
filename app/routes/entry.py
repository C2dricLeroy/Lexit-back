from datetime import datetime
from logging import getLogger

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.database import get_session
from app.dto.entry import EntryCreate, EntryRead, EntryUpdate
from app.models.entry import Entry
from app.services.entry import compute_display_name

router = APIRouter()
_logger = getLogger(__name__)


@router.get("/", response_model=list[EntryRead])
def get_entries(session: Session = Depends(get_session)):
    """Return all entries."""
    return session.exec(select(Entry)).all()


@router.get("/{id}", response_model=EntryRead)
def get_entry_by_id(entry_id: int, session: Session = Depends(get_session)):
    """Return an entry by its ID."""
    return session.exec(select(Entry).where(Entry.id == entry_id)).first()


@router.get("/dictionary/{dictionary_id}", response_model=list[EntryRead])
def get_entries_by_dictionary_id(
    dictionary_id: int, session: Session = Depends(get_session)
):
    """Return all entries for a given dictionary."""
    return session.exec(
        select(Entry).where(Entry.dictionary_id == dictionary_id)
    ).all()


@router.post("/", response_model=EntryRead, status_code=201)
def create_entry(entry: EntryCreate, session: Session = Depends(get_session)):
    """Create a new entry."""
    db_dictionary = session.get(Entry, entry.dictionary_id)
    if not db_dictionary:
        raise HTTPException(status_code=404, detail="Dictionary not found")

    db_entry = Entry(**entry.model_dump())
    db_entry = compute_display_name(db_entry)

    session.add(db_entry)
    try:
        session.commit()
        session.refresh(db_entry)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="An entry with this name already exists in the dictionary.",
        )

    return db_entry


@router.delete("/{id}")
def delete_entry(entry_id: int, session: Session = Depends(get_session)):
    """Delete an entry by its ID."""
    session.delete(session.get(Entry, entry_id))


@router.patch("/{entry_id}", response_model=EntryRead)
def update_entry(
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
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="An entry with this name already exists in this dictionary.",
        )

    return db_entry
