from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str):
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str):
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def email_exists(self, email: str) -> bool:
        """Check if email exists"""
        return self.db.query(User).filter(User.email == email).first() is not None

    def username_exists(self, username: str) -> bool:
        """Check if username exists"""
        return self.db.query(User).filter(User.username == username).first() is not None
