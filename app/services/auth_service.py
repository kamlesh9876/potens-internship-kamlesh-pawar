from datetime import datetime
from typing import Optional
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, get_password_hash
from app.core.jwt import create_access_token
from app.core.exceptions import ValidationException, UnauthorizedException, NotFoundException
from app.core.logging import logger
from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import Token
from app.models.user import User


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register(self, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if email already exists
        if self.user_repository.email_exists(user_data.email):
            raise ValidationException("Email already registered")
        
        # Check if username already exists
        if self.user_repository.username_exists(user_data.username):
            raise ValidationException("Username already taken")
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        
        user = self.user_repository.create(user_dict)
        logger.info(f"User registered: {user.email}")
        return user

    def login(self, login_data: UserLogin) -> Token:
        """Authenticate user and return access token"""
        user = self.user_repository.get_by_email(login_data.email)
        
        if not user:
            raise UnauthorizedException("Invalid email or password")
        
        if not verify_password(login_data.password, user.hashed_password):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            self.user_repository.update(user, {"failed_login_attempts": user.failed_login_attempts})
            raise UnauthorizedException("Invalid email or password")
        
        if not user.is_active:
            raise UnauthorizedException("Account is inactive")
        
        # Reset failed login attempts and update last login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        self.user_repository.update(user, {
            "failed_login_attempts": 0,
            "last_login": user.last_login
        })
        
        # Create access token
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email
        }
        access_token = create_access_token(token_data)
        
        logger.info(f"User logged in: {user.email}")
        return Token(access_token=access_token, token_type="bearer")

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        user = self.user_repository.get_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user

    def change_password(self, user: User, old_password: str, new_password: str) -> bool:
        """Change user password"""
        if not verify_password(old_password, user.hashed_password):
            raise ValidationException("Old password is incorrect")
        
        hashed_password = get_password_hash(new_password)
        self.user_repository.update(user, {"hashed_password": hashed_password})
        logger.info(f"Password changed for user: {user.email}")
        return True
