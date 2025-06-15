from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from starlette.requests import Request

from app.core.limiter import limiter
from app.database import get_session
from app.dto.language import LanguageCreate, LanguageRead
from app.models.language import Language
from app.models.user import User
from app.services.user import get_current_user

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


@router.delete("/admin/{language_id}", response_model=List[LanguageRead])
@limiter.limit("5/minute")
def delete_language(
    request: Request,
    language_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Admin delete a language by its ID."""
    db_language = session.get(Language, language_id)
    if not db_language:
        raise HTTPException(status_code=404, detail="Language not found")

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to delete this language.",
        )

    session.delete(db_language)
    session.commit()
    return {"message": "Language deleted successfully"}
