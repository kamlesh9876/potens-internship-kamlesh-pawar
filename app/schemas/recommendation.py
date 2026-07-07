from pydantic import BaseModel
from typing import List, Optional


class ProfileInput(BaseModel):
    age: int
    budget: float
    experience_level: str
    goal: str
    location: str
    preferred_pace: Optional[str] = None


class RecommendationItem(BaseModel):
    item_id: int
    name: str
    score: float
    reason: str


class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
