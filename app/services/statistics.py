from sqlalchemy import func
from sqlmodel import Session, select

from app.enum.timegranularity import TimeGranularity
from app.models.dictionary import Dictionary
from app.models.entry import Entry


def get_date_trunc(granularity: TimeGranularity):
    """Return the created_at of the entries given the time granularity."""
    match granularity:
        case TimeGranularity.day:
            return func.date_trunc("day", Entry.created_at)
        case TimeGranularity.week:
            return func.date_trunc("week", Entry.created_at)
        case TimeGranularity.month:
            return func.date_trunc("month", Entry.created_at)


def retrieve_total_words_added(session: Session, current_user_id):
    """Retrieve the total number of words added."""
    count = session.exec(
        select(func.count(Entry.id))
        .join(Dictionary, Dictionary.id == Entry.dictionary_id)
        .where(Dictionary.user_id == current_user_id)
    ).one()
    return count


def retrieve_number_of_dictionaries(session: Session, current_user_id):
    """Retrieve the number of dictionaries of the current user."""
    count = session.exec(
        select(func.count(Dictionary.id)).where(
            Dictionary.user_id == current_user_id
        )
    ).one()
    return count
