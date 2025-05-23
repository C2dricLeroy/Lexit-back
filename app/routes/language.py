from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.models.language import Language
from app.database import get_session

router = APIRouter()

@router.get("/")
def get_languages(session: Session = Depends(get_session)):
    return session.exec(select(Language)).all()
