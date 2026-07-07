from typing import List, Dict, Any
from app.repositories.item_repository import ItemRepository
from app.core.logging import logger


class RecommendationService:
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository

    def build_recommendations(self, profile) -> List[Dict[str, Any]]:
        """Build recommendations based on user profile"""
        items = self.item_repository.list_items()
        scored = []
        
        for item in items:
            score = 0.0
            reasons = []

            if profile.goal.lower() != item.goal.lower():
                continue
            score += 4.0
            reasons.append("goal match")

            if profile.experience_level.lower() == item.skill_level.lower():
                score += 3.0
                reasons.append("skill match")
            elif profile.experience_level.lower() == "beginner" and item.skill_level.lower() in {"beginner", "intermediate"}:
                score += 2.0
                reasons.append("beginner-friendly")
            else:
                continue

            if profile.budget >= item.price:
                score += 2.0
                reasons.append("budget fit")
            elif profile.budget >= item.price * 0.8:
                score += 1.0
                reasons.append("near-budget fit")
            else:
                continue

            if profile.location.lower() == item.location.lower() or item.location.lower() == "remote":
                score += 2.0
                reasons.append("location fit")
            else:
                continue

            if profile.preferred_pace is None or profile.preferred_pace.lower() == item.pace.lower():
                score += 1.0
                reasons.append("pace fit")

            if score >= 8.0:
                reason = f"This recommendation fits your {', '.join(reasons)} and is suitable for your current profile."
                scored.append({"item_id": item.id, "name": item.name, "score": score, "reason": reason})

        scored.sort(key=lambda item: item["score"], reverse=True)
        logger.info(f"Generated {len(scored[:3])} recommendations for profile with goal: {profile.goal}")
        return scored[:3]
