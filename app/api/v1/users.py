from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user import UserResponse, UserUpdate, UserPublic
from app.schemas.response import ApiResponse
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=UserResponse, tags=["Users"])
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user's information"""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse, tags=["Users"])
def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's information"""
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    
    try:
        updated_user = user_service.update_user(current_user.id, user_data)
        return UserResponse.model_validate(updated_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users", response_model=List[UserPublic], tags=["Users"])
def list_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    
    users = user_service.list_users()
    return [UserPublic.model_validate(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only)"""
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    
    try:
        user = user_service.get_user(user_id)
        return UserResponse.model_validate(user)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user by ID (admin only)"""
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    
    try:
        updated_user = user_service.update_user(user_id, user_data)
        return UserResponse.model_validate(updated_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/{user_id}/deactivate", tags=["Users"])
def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate user account (admin only)"""
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    
    try:
        user = user_service.deactivate_user(user_id)
        return ApiResponse(success=True, message=f"User {user.email} deactivated").model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/{user_id}/activate", tags=["Users"])
def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Activate user account (admin only)"""
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    
    try:
        user = user_service.activate_user(user_id)
        return ApiResponse(success=True, message=f"User {user.email} activated").model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/{user_id}/make-admin", tags=["Users"])
def make_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Grant admin privileges to user (admin only)"""
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    
    try:
        user = user_service.make_admin(user_id)
        return ApiResponse(success=True, message=f"Admin privileges granted to {user.email}").model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/{user_id}/revoke-admin", tags=["Users"])
def revoke_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Revoke admin privileges from user (admin only)"""
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    
    try:
        user = user_service.revoke_admin(user_id)
        return ApiResponse(success=True, message=f"Admin privileges revoked from {user.email}").model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
