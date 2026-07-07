from typing import Optional, List
from app.repositories.user_repository import UserRepository
from app.core.exceptions import NotFoundException, ValidationException
from app.core.logging import logger
from app.schemas.user import UserUpdate
from app.models.user import User


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_user(self, user_id: int) -> User:
        """Get user by ID"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.user_repository.get_by_email(email)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.user_repository.get_by_username(username)

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user information"""
        user = self.get_user(user_id)
        
        update_dict = user_data.model_dump(exclude_unset=True)
        
        # Check email uniqueness if being updated
        if "email" in update_dict and update_dict["email"] != user.email:
            if self.user_repository.email_exists(update_dict["email"]):
                raise ValidationException("Email already registered")
        
        if update_dict:
            updated_user = self.user_repository.update(user, update_dict)
            logger.info(f"User updated: {user.email}")
            return updated_user
        
        return user

    def deactivate_user(self, user_id: int) -> User:
        """Deactivate a user account"""
        user = self.get_user(user_id)
        user = self.user_repository.update(user, {"is_active": False})
        logger.info(f"User deactivated: {user.email}")
        return user

    def activate_user(self, user_id: int) -> User:
        """Activate a user account"""
        user = self.get_user(user_id)
        user = self.user_repository.update(user, {"is_active": True})
        logger.info(f"User activated: {user.email}")
        return user

    def make_admin(self, user_id: int) -> User:
        """Grant admin privileges to a user"""
        user = self.get_user(user_id)
        user = self.user_repository.update(user, {"is_admin": True})
        logger.info(f"Admin privileges granted to: {user.email}")
        return user

    def revoke_admin(self, user_id: int) -> User:
        """Revoke admin privileges from a user"""
        user = self.get_user(user_id)
        user = self.user_repository.update(user, {"is_admin": False})
        logger.info(f"Admin privileges revoked from: {user.email}")
        return user

    def list_users(self) -> List[User]:
        """List all users"""
        users = self.user_repository.get_all()
        logger.info(f"Listed {len(users)} users")
        return users
