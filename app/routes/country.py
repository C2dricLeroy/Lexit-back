import csv
from logging import getLogger
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import engine, get_session
from app.dto.country import CountryCreate, CountryRead
from app.models.country import Country
from app.models.countryLanguage import CountryLanguageLink
from app.models.language import Language

router = APIRouter()
_logger = getLogger(__name__)


@router.get("/", response_model=list[CountryRead])
def get_country(session: Session = Depends(get_session)):
    """Return all countries."""
    return session.exec(select(Country)).all()


@router.get("/{id}", response_model=list[CountryRead])
def get_country_by_id(
    country_id: int, session: Session = Depends(get_session)
):
    """Return a country by its ID."""
    return session.exec(
        select(Country).where(Country.id == country_id)
    ).first()


@router.post("/", response_model=CountryRead, status_code=201)
def create_country(
    country: CountryCreate, session: Session = Depends(get_session)
):
    """Create a new country."""
    db_country = Country(**country.model_dump())
    session.add(db_country)
    session.commit()
    session.refresh(db_country)
    return db_country


def load_csv_at_startup():
    """Load countries and languages from CSV at startup."""
    csv_path = Path("data/country_list.csv")
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        countries = list(reader)

    with Session(engine) as session:
        for row in countries:
            existing_country = session.exec(
                select(Country).where(Country.code == row["country_code"])
            ).first()

            if existing_country:
                continue

            country = Country(
                name=row["country_name"],
                code=row["country_code"],
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
            )
            session.add(country)
            session.flush()

            lang_name = row.get("lang_name", "").strip()
            lang_code = row.get("lang_code", "").strip()

            if lang_name and lang_code:
                language = session.exec(
                    select(Language).where(Language.code == lang_code)
                ).first()

                if not language:
                    language = Language(name=lang_name, code=lang_code)
                    session.add(language)
                    session.flush()

                link = CountryLanguageLink(
                    country_id=country.id, language_id=language.id
                )
                session.add(link)

        session.commit()
        return countries
