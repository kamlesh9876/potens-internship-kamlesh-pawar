from sqlalchemy import Column, Integer, String, Float, Text
from app.db.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    skill_level = Column(String, nullable=False)
    goal = Column(String, nullable=False)
    location = Column(String, nullable=False)
    pace = Column(String, nullable=False)
    description = Column(Text, nullable=False)
