from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, ChangePassword, UserResponse
from app.schemas.token import Token
from app.schemas.response import ApiResponse
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, tags=["Authentication"])
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account"""
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    
    try:
        user = auth_service.register(user_data)
        return UserResponse.model_validate(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token, tags=["Authentication"])
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password to get access token"""
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    
    try:
        token = auth_service.login(login_data)
        return token
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/change-password", tags=["Authentication"])
def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change current user's password"""
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    
    try:
        auth_service.change_password(current_user, password_data.old_password, password_data.new_password)
        return ApiResponse(success=True, message="Password changed successfully").model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
