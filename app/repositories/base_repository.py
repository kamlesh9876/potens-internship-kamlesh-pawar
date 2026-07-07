from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.logging import logger

T = TypeVar('T')


class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def create(self, data: Dict[str, Any]) -> T:
        try:
            obj = self.model(**data)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            logger.info(f"Created {self.model.__name__} with id {getattr(obj, 'id', 'unknown')}")
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to create {self.model.__name__}: {str(e)}")
            raise

    def update(self, obj: T, data: Dict[str, Any]) -> T:
        try:
            for field, value in data.items():
                setattr(obj, field, value)
            self.db.commit()
            self.db.refresh(obj)
            logger.info(f"Updated {self.model.__name__} with id {getattr(obj, 'id', 'unknown')}")
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to update {self.model.__name__}: {str(e)}")
            raise

    def delete(self, obj: T) -> None:
        try:
            obj_id = getattr(obj, 'id', 'unknown')
            self.db.delete(obj)
            self.db.commit()
            logger.info(f"Deleted {self.model.__name__} with id {obj_id}")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to delete {self.model.__name__}: {str(e)}")
            raise

    def get_by_id(self, obj_id: int) -> Optional[T]:
        try:
            return self.db.query(self.model).filter(self.model.id == obj_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get {self.model.__name__} by id {obj_id}: {str(e)}")
            raise

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        try:
            query = self.db.query(self.model)
            if filters:
                for field, value in filters.items():
                    if value is not None:
                        query = query.filter(getattr(self.model, field).ilike(f"%{value}%"))
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get all {self.model.__name__}: {str(e)}")
            raise

    def exists(self, obj_id: int) -> bool:
        try:
            return self.db.query(self.model).filter(self.model.id == obj_id).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Failed to check existence of {self.model.__name__} with id {obj_id}: {str(e)}")
            raise
