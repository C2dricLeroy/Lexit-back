from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.dto.language import LanguageCreate, LanguageRead
from app.models.language import Language

router = APIRouter()


@router.get("/", response_model=list[LanguageRead])
def get_languages(session: Session = Depends(get_session)):
    """Return all languages."""
    return session.exec(select(Language)).all()


@router.get("/{id}", response_model=list[LanguageRead])
def get_language_by_id(
    language_id: int, session: Session = Depends(get_session)
):
    """Return a language by its ID."""
    return session.exec(
        select(Language).where(Language.id == language_id)
    ).first()


@router.post("/", response_model=LanguageRead, status_code=201)
def create_language(
    language: LanguageCreate, session: Session = Depends(get_session)
):
    """Create a new language."""
    db_language = Language(**language.model_dump())
    session.add(db_language)
    session.commit()
    session.refresh(db_language)
    return db_language
