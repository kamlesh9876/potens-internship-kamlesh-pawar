from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///data/app.db"))
    admin_token: str = Field(default_factory=lambda: os.getenv("ADMIN_TOKEN", "secret-token"))
    app_name: str = Field(default_factory=lambda: os.getenv("APP_NAME", "SkillPath Recommendation API"))
    app_version: str = Field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "True").lower() == "true")
    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", "your-secret-key-change-in-production"))
    access_token_expire_minutes: int = Field(default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    algorithm: str = Field(default_factory=lambda: os.getenv("ALGORITHM", "HS256"))


settings = Settings()
DATABASE_URL = settings.database_url
ADMIN_TOKEN = settings.admin_token
APP_NAME = settings.app_name
APP_VERSION = settings.app_version
DEBUG = settings.debug
SECRET_KEY = settings.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
ALGORITHM = settings.algorithm
