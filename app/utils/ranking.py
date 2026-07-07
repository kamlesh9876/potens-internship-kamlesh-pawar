def rank_items(items, profile):
    return sorted(items, key=lambda item: (
        profile.goal.lower() == item.goal.lower(),
        profile.experience_level.lower() == item.skill_level.lower(),
        profile.budget >= item.price,
        profile.location.lower() == item.location.lower() or item.location.lower() == 'remote',
        profile.preferred_pace is None or profile.preferred_pace.lower() == item.pace.lower(),
    ), reverse=True)
