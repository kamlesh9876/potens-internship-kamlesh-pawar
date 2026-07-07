from pydantic import BaseModel
from typing import Optional


class ItemBase(BaseModel):
    name: str
    category: str
    price: float
    skill_level: str
    goal: str
    location: str
    pace: str
    description: str


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: int


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    skill_level: Optional[str] = None
    goal: Optional[str] = None
    location: Optional[str] = None
    pace: Optional[str] = None
    description: Optional[str] = None
