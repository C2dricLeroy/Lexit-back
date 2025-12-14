from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlmodel import Session, select

from app.database import get_session
from app.dto.statistics import WordsOverTimePoint, WordsOverTimeRead
from app.enum.timegranularity import TimeGranularity
from app.models.dictionary import Dictionary
from app.models.entry import Entry
from app.services.statistics import get_date_trunc

router = APIRouter()


@router.get("/words-over-time", response_model=list[WordsOverTimeRead])
def get_dictionary_words_over_time(
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
        .group_by(Entry.dictionary_id, Dictionary.name, date_bucket)
        .order_by(Entry.dictionary_id, date_bucket)
    )

    rows = session.exec(stmt).all()

    series: dict[int, WordsOverTimeRead] = {}

    for dictionary_id, name, bucket, count in rows:
        if dictionary_id not in series:
            series[dictionary_id] = WordsOverTimeRead(
                dictionary_id=dictionary_id,
                dictionary_name=name,
                data=[],
            )

        previous = (
            series[dictionary_id].data[-1].count
            if series[dictionary_id].data
            else 0
        )

        series[dictionary_id].data.append(
            WordsOverTimePoint(
                date=bucket.date(),
                count=previous + count,
            )
        )

    return list[WordsOverTimeRead](series.values())


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
