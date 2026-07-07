from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class ProfileInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    age: int
    budget: float
    experience_level: str
    goal: str
    location: str
    preferred_pace: Optional[str] = None


class RecommendationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    item_id: int
    name: str
    score: float
    reason: str


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    recommendations: List[RecommendationItem]
