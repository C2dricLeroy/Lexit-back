from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from starlette.requests import Request

from app.database import get_session
from app.dto.language import LanguageCreate, LanguageRead
from app.main import limiter
from app.models.language import Language

router = APIRouter()


@router.get("/", response_model=list[LanguageRead])
@limiter.limit("1000/day")
def get_languages(request: Request, session: Session = Depends(get_session)):
    """Return all languages."""
    return session.exec(select(Language)).all()


@router.get("/{id}", response_model=list[LanguageRead])
@limiter.limit("1000/day")
def get_language_by_id(
    request: Request, language_id: int, session: Session = Depends(get_session)
):
    """Return a language by its ID."""
    return session.exec(
        select(Language).where(Language.id == language_id)
    ).first()


@router.post("/", response_model=List[LanguageRead], status_code=201)
@limiter.limit("10/minute")
def create_language(
    request: Request,
    language: LanguageCreate,
    session: Session = Depends(get_session),
):
    """Create a new language."""
    db_language = Language(**language.model_dump())
    session.add(db_language)
    session.commit()
    session.refresh(db_language)
    return [db_language]
