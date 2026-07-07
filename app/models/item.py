from sqlalchemy import Column, Integer, String, Float, Text, DateTime, func, Index
from app.db.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)
    skill_level = Column(String, nullable=False, index=True)
    goal = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False, index=True)
    pace = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_category_goal', 'category', 'goal'),
        Index('idx_location_skill', 'location', 'skill_level'),
        Index('idx_price_category', 'price', 'category'),
    )
