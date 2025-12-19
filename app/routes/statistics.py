from collections import defaultdict
from datetime import date

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlmodel import Session, select

from app.database import get_session
from app.dto.statistics import WordsOverTimePoint, WordsOverTimeRead
from app.enum.timegranularity import TimeGranularity
from app.models.dictionary import Dictionary
from app.models.entry import Entry
from app.models.user import User
from app.services.statistics import (
    get_date_trunc,
    retrieve_number_of_dictionaries,
    retrieve_total_words_added,
)
from app.services.user import get_current_user

router = APIRouter()


@router.get("/user")
def get_user_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Return the current user statistics."""
    total_words_added = retrieve_total_words_added(session, current_user.id)
    number_of_dictionaries = retrieve_number_of_dictionaries(
        session, current_user.id
    )

    return {
        "total_words_added": total_words_added,
        "number_of_dictionaries": number_of_dictionaries,
    }


@router.get("/words-over-time/chart")
def get_words_over_time_chart(
    granularity: TimeGranularity = TimeGranularity.day,
    session: Session = Depends(get_session),
):
    """Return the main chart data."""
    date_bucket = get_date_trunc(granularity)

    stmt = (
        select(
            Dictionary.name.label("dictionary"),
            date_bucket.label("bucket"),
            func.count(Entry.id).label("count"),
        )
        .join(Dictionary, Dictionary.id == Entry.dictionary_id)
        .group_by(Dictionary.name, date_bucket)
        .order_by(date_bucket)
    )

    rows = session.exec(stmt).all()

    timeline: dict[date, dict[str, int]] = defaultdict(dict)
    dictionaries: set[str] = set()

    for dictionary, bucket, count in rows:
        day = bucket.date()

        dictionaries.add(dictionary)
        timeline[day][dictionary] = count

    return {
        "granularity": granularity,
        "series": [
            {"key": name, "label": name} for name in sorted(dictionaries)
        ],
        "data": [
            {"date": day, **values} for day, values in sorted(timeline.items())
        ],
    }


@router.get("/words-over-time/{id}", response_model=WordsOverTimeRead)
def get_words_over_time_by_dictionary(
    dictionary_id: int,
    request: Request,
    granularity: TimeGranularity = TimeGranularity.day,
    session: Session = Depends(get_session),
):
    """Return the number of entries by dictionnary given the granularity time."""
    date_bucket = get_date_trunc(granularity)

    stmt = (
        select(
            Entry.dictionary_id,
            Dictionary.name,
            date_bucket.label("bucket"),
            func.count(Entry.id).label("count"),
        )
        .join(Dictionary, Dictionary.id == Entry.dictionary_id)
        .where(Entry.dictionary_id == dictionary_id)  # Le filtre ici!
        .group_by(Entry.dictionary_id, Dictionary.name, date_bucket)
        .order_by(date_bucket)
    )

    rows = session.exec(stmt).all()

    if not rows:
        return WordsOverTimeRead(
            dictionary_id=dictionary_id,
            dictionary_name="",
            data=[],
        )

    result = WordsOverTimeRead(
        dictionary_id=dictionary_id,
        dictionary_name=rows[0][1],
        data=[],
    )

    cumulative = 0
    for _, _, bucket, count in rows:
        cumulative += count
        result.data.append(
            WordsOverTimePoint(
                date=bucket.date(),
                count=cumulative,
            )
        )

    return result
