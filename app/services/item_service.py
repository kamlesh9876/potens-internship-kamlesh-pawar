from typing import List, Optional, Dict, Any
from sqlalchemy import or_, and_
from app.repositories.item_repository import ItemRepository
from app.core.exceptions import NotFoundException
from app.core.logging import logger
from app.schemas.item import ItemCreate, ItemUpdate
from app.models.item import Item


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

    def list_items(
        self,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = "asc"
    ):
        """List items with optional filters, search, and sorting"""
        query = self.item_repository.db.query(Item)
        
        # Apply filters
        if filters:
            if filters.get("category"):
                query = query.filter(Item.category == filters["category"])
            if filters.get("location"):
                query = query.filter(Item.location == filters["location"])
            if filters.get("goal"):
                query = query.filter(Item.goal == filters["goal"])
            if filters.get("skill_level"):
                query = query.filter(Item.skill_level == filters["skill_level"])
            if filters.get("price_min"):
                query = query.filter(Item.price >= filters["price_min"])
            if filters.get("price_max"):
                query = query.filter(Item.price <= filters["price_max"])
        
        # Apply search
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Item.name.ilike(search_pattern),
                    Item.description.ilike(search_pattern),
                    Item.category.ilike(search_pattern)
                )
            )
        
        # Apply sorting
        if sort_by:
            sort_column = getattr(Item, sort_by, None)
            if sort_column:
                if order.lower() == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
        
        items = query.all()
        logger.info(f"Listed {len(items)} items with filters: {filters}, search: {search}, sort: {sort_by}")
        return items

    def get_paginated_items(
        self,
        page: int,
        limit: int,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = "asc"
    ):
        """Get paginated items with optional filters, search, and sorting"""
        items = self.list_items(filters=filters, search=search, sort_by=sort_by, order=order)
        total = len(items)
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        offset = (page - 1) * limit
        sliced_items = items[offset: offset + limit]
        
        return {
            "items": sliced_items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
