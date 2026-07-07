from typing import List, Optional, Dict, Any
from app.repositories.item_repository import ItemRepository
from app.core.exceptions import NotFoundException
from app.core.logging import logger
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository

    def create_item(self, item_data: ItemCreate):
        """Create a new item"""
        item_dict = item_data.model_dump()
        item = self.item_repository.create(item_dict)
        logger.info(f"Created item: {item.name}")
        return item

    def get_item(self, item_id: int):
        """Get item by ID"""
        item = self.item_repository.get_item(item_id)
        if item is None:
            raise NotFoundException(f"Item with id {item_id} not found")
        return item

    def update_item(self, item_id: int, item_data: ItemUpdate):
        """Update an existing item"""
        item = self.get_item(item_id)
        update_dict = item_data.model_dump(exclude_unset=True)
        if update_dict:
            item = self.item_repository.update(item, update_dict)
            logger.info(f"Updated item {item_id}")
        return item

    def delete_item(self, item_id: int):
        """Delete an item"""
        item = self.get_item(item_id)
        self.item_repository.delete(item)
        logger.info(f"Deleted item {item_id}")

    def list_items(self, filters: Optional[Dict[str, Any]] = None):
        """List items with optional filters"""
        items = self.item_repository.list_items(filters=filters)
        logger.info(f"Listed {len(items)} items with filters: {filters}")
        return items

    def get_paginated_items(self, page: int, limit: int, filters: Optional[Dict[str, Any]] = None):
        """Get paginated items with optional filters"""
        items = self.list_items(filters=filters)
        total = len(items)
        sliced_items = items[(page - 1) * limit: page * limit]
        return {
            "items": sliced_items,
            "total": total,
            "page": page,
            "limit": limit
        }
