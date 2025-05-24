import csv
from logging import getLogger
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import engine, get_session
from app.dto.country import CountryCreate, CountryRead
from app.models.country import Country

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
    """Import countries from CSV into the database."""
    csv_path = Path("data/country_list.csv")
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        countries = list(reader)

    with Session(engine) as session:
        for row in countries:
            existing = session.exec(
                select(Country).where(Country.code == row["country_code"])
            ).first()

            if existing:
                continue

            country = Country(
                name=row["country_name"],
                code=row["country_code"],
            )
            session.add(country)

        session.commit()

    _logger.info("%s rows processed from CSV.", len(countries))
    return countries
