from app.db.database import Base, engine
from app.models.item import Item


def init_db() -> None:
    """Initialize database - migrations should be used instead"""
    # This function is deprecated. Use Alembic migrations instead.
    # Base.metadata.create_all(bind=engine)
    pass
