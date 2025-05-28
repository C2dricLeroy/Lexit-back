from logging import getLogger

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.dto.entry import EntryCreate, EntryRead
from app.models.entry import Entry

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
    db_entry = Entry(**entry.model_dump())
    session.add(db_entry)
    session.commit()
    session.refresh(db_entry)
    return db_entry
