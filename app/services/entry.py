from logging import getLogger

_logger = getLogger(__name__)


def compute_display_name(db_entry):
    """Compute and return the display name for a given entry."""
    _logger.info(f"Computing display name for entry {db_entry}")
    db_entry.display_name = (
        f"{db_entry.original_name} ({db_entry.translation})"
    )
    return db_entry
