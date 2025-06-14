from logging import getLogger

from app.models import Language

_logger = getLogger(__name__)


def compute_display_name(session, db_dictionary):
    """Compute and return the display name for a given dictionary."""
    source_language = session.get(Language, db_dictionary.source_language_id)
    target_language = session.get(Language, db_dictionary.target_language_id)

    if not source_language or not target_language:
        raise ValueError("Languages not found in the database.")

    db_dictionary.display_name = (
        f"{source_language.name} : {target_language.name}"
    )
    return db_dictionary
