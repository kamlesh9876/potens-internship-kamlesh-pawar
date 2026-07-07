from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
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
    created_at: datetime
    updated_at: datetime


class ItemUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    skill_level: Optional[str] = None
    goal: Optional[str] = None
    location: Optional[str] = None
    pace: Optional[str] = None
    description: Optional[str] = None
