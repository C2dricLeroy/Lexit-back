import pytest
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture
def db():
    """Create a new database session for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Crée toutes les tables (tu peux ajouter d’autres modèles si besoin)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
