from pydantic import BaseModel, ConfigDict
from typing import Generic, List, TypeVar

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool
    items: List[T]
