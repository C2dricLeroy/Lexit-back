from sqlalchemy import func

from app.enum.timegranularity import TimeGranularity
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
