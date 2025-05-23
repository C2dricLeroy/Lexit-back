from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models.language import Language

router = APIRouter()


@router.get("/")
def get_languages(session: Session = Depends(get_session)):
    """Return all languages."""
    return session.exec(select(Language)).all()


@router.get("/{id}")
def get_language_by_id(id: int, session: Session = Depends(get_session)):
    """Return a language by its ID."""
    return session.exec(select(Language).where(Language.id == id)).first()


@router.post("/")
def create_language(language: Language, session: Session = Depends(get_session)):
    """Create a new language."""
    session.add(language)
    session.commit()
    session.refresh(language)
    return language
