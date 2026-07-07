from app.db.database import Base, engine
from app.models.item import Item


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
