from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.config import APP_NAME
from app.core.exceptions import AppError
from app.core.logging import logger
from app.db.session import get_db
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.schemas.pagination import PaginatedResponse
from app.schemas.recommendation import ProfileInput, RecommendationResponse
from app.repositories.item_repository import ItemRepository
from app.services.recommendation_service import RecommendationService
from app.services.explain_service import ExplainService
from app.services.item_service import ItemService
from app.schemas.response import ApiResponse
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User

router = APIRouter()


@router.get("/health", tags=["Health"])
def healthcheck():
    """Health check endpoint"""
    return ApiResponse(success=True, message="Service is healthy", data={"name": APP_NAME, "status": "Running"}).model_dump()


@router.get("/health/application", tags=["Health"])
def health_application():
    """Application health check endpoint"""
    return ApiResponse(success=True, message="Application is running", data={"name": APP_NAME}).model_dump()


@router.get("/health/db", tags=["Health"])
def health_database(db: Session = Depends(get_db)):
    """Database health check endpoint"""
    try:
        db.execute(text("SELECT 1"))
        return ApiResponse(success=True, message="Database reachable", data={"status": "ok"}).model_dump()
    except Exception as exc:
        logger.error("Database health check failed", exc_info=exc)
        raise AppError("Database unavailable", status_code=503) from exc


@router.post("/recommend", response_model=RecommendationResponse, tags=["Recommendations"])
def recommend(
    profile: ProfileInput, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get personalized recommendations based on user profile"""
    item_repository = ItemRepository(db)
    recommendation_service = RecommendationService(item_repository)
    recommendations = recommendation_service.build_recommendations(profile)
    return RecommendationResponse(recommendations=recommendations)


@router.get("/items", response_model=PaginatedResponse[ItemRead], tags=["Items"])
def list_items(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    goal: Optional[str] = Query(None, description="Filter by goal"),
    location: Optional[str] = Query(None, description="Filter by location"),
    skill_level: Optional[str] = Query(None, description="Filter by skill level"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """List items with pagination and filtering (admin only)"""
    item_repository = ItemRepository(db)
    item_service = ItemService(item_repository)
    
    filters = {
        "name": name,
        "category": category,
        "goal": goal,
        "location": location,
        "skill_level": skill_level,
    }
    
    paginated_data = item_service.get_paginated_items(page, limit, filters)
    return PaginatedResponse(
        page=paginated_data["page"],
        limit=paginated_data["limit"],
        total=paginated_data["total"],
        items=[ItemRead.model_validate(item) for item in paginated_data["items"]],
    )


@router.post("/items", response_model=ItemRead, tags=["Items"])
def create_item(
    item: ItemCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new item (admin only)"""
    item_repository = ItemRepository(db)
    item_service = ItemService(item_repository)
    new_item = item_service.create_item(item)
    return ItemRead.model_validate(new_item)


@router.get("/items/{item_id}", response_model=ItemRead, tags=["Items"])
def get_item(
    item_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get item by ID (admin only)"""
    item_repository = ItemRepository(db)
    item_service = ItemService(item_repository)
    item = item_service.get_item(item_id)
    return ItemRead.model_validate(item)


@router.put("/items/{item_id}", response_model=ItemRead, tags=["Items"])
def update_item(
    item_id: int, 
    item: ItemUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update an existing item (admin only)"""
    item_repository = ItemRepository(db)
    item_service = ItemService(item_repository)
    updated_item = item_service.update_item(item_id, item)
    return ItemRead.model_validate(updated_item)


@router.delete("/items/{item_id}", tags=["Items"])
def delete_item(
    item_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete an item (admin only)"""
    item_repository = ItemRepository(db)
    item_service = ItemService(item_repository)
    item_service.delete_item(item_id)
    return {"message": "Item deleted"}


@router.get("/explain/{item_id}", tags=["Recommendations"])
def explain_item(
    item_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get explanation for why an item is recommended"""
    item_repository = ItemRepository(db)
    item_service = ItemService(item_repository)
    explain_service = ExplainService()
    
    item = item_service.get_item(item_id)
    explanation = explain_service.explain_item(item)
    return {"item_id": item_id, "explanation": explanation}
