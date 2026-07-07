from sqlalchemy.orm import Session
from app.models.item import Item


class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, item_data: dict):
        item = Item(**item_data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, item, data: dict):
        for field, value in data.items():
            setattr(item, field, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item) -> None:
        self.db.delete(item)
        self.db.commit()

    def get_by_id(self, item_id: int):
        return self.db.query(Item).filter(Item.id == item_id).first()

    def get_all(self, filters: dict | None = None):
        query = self.db.query(Item)
        if filters:
            for field, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(Item, field).ilike(f"%{value}%"))
        return query.all()

    def list_items(self, filters: dict | None = None):
        return self.get_all(filters=filters)

    def get_item(self, item_id: int):
        return self.get_by_id(item_id)
