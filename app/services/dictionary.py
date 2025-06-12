from logging import getLogger

_logger = getLogger(__name__)


def compute_display_name(db_entry):
    """Compute and return the display name for a given dictionary."""
    source_language_name = db_entry.source_language.name
    target_language_name = db_entry.target_language.name
    db_entry.display_name = f"{source_language_name} : {target_language_name}"
    return db_entry
