from sqlalchemy.orm import Session
from app.models.item import Item
from app.repositories.base_repository import BaseRepository


class ItemRepository(BaseRepository[Item]):
    def __init__(self, db: Session):
        super().__init__(db, Item)

    def list_items(self, filters: dict | None = None):
        return self.get_all(filters=filters)

    def get_item(self, item_id: int):
        return self.get_by_id(item_id)
