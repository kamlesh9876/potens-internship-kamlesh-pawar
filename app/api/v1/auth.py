from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, ChangePassword, UserResponse
from app.schemas.token import Token
from app.schemas.response import ApiResponse
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.background.tasks import send_welcome_email, log_user_login, log_password_change

router = APIRouter()


@router.post(
    "/register", 
    response_model=UserResponse, 
    tags=["Authentication"],
    summary="Register a new user",
    description="Create a new user account with email, username, and password. Password must be at least 8 characters with uppercase, lowercase, and digit.",
    responses={
        200: {"description": "User registered successfully"},
        400: {"description": "Invalid input or email/username already exists"}
    }
)
def register(
    user_data: UserCreate, 
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Register a new user account"""
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    
    try:
        user = auth_service.register(user_data)
        # Send welcome email in background
        background_tasks.add_task(send_welcome_email, user.email, user.username)
        return UserResponse.model_validate(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/login", 
    response_model=Token, 
    tags=["Authentication"],
    summary="Login user",
    description="Authenticate with email and password to receive JWT access token. Token expires in 30 minutes.",
    responses={
        200: {"description": "Login successful, returns access token"},
        401: {"description": "Invalid email or password"}
    }
)
def login(
    login_data: UserLogin, 
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Login with email and password to get access token"""
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    
    try:
        token = auth_service.login(login_data)
        # Log user login in background
        user = user_repository.get_by_email(login_data.email)
        if user:
            background_tasks.add_task(log_user_login, user.id, user.email)
        return token
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/change-password", tags=["Authentication"])
def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Change current user's password"""
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    
    try:
        auth_service.change_password(current_user, password_data.old_password, password_data.new_password)
        # Log password change in background
        background_tasks.add_task(log_password_change, current_user.id, current_user.email)
        return ApiResponse(success=True, message="Password changed successfully").model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
