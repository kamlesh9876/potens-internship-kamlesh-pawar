from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///data/app.db"))
    admin_token: str = Field(default_factory=lambda: os.getenv("ADMIN_TOKEN", "secret-token"))
    app_name: str = "SkillPath Recommendation API"


settings = Settings()
DATABASE_URL = settings.database_url
ADMIN_TOKEN = settings.admin_token
APP_NAME = settings.app_name
