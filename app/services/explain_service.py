from app.core.logging import logger


class ExplainService:
    def explain_item(self, item) -> str:
        """Generate explanation for why an item is recommended"""
        explanation = (
            f"This item is suitable when the learner's goal matches '{item.goal}', "
            f"the budget fits the item price of {item.price}, "
            f"the skill level aligns with '{item.skill_level}', and the location matches '{item.location}'."
        )
        logger.info(f"Generated explanation for item {item.id}: {item.name}")
        return explanation
