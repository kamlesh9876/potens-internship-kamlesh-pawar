from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
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
from app.background.tasks import save_recommendation_history, generate_item_analytics

router = APIRouter()


@router.get("/health", tags=["Health"])
def healthcheck():
    """Health check endpoint"""
    import time
    from app.core.config import APP_VERSION, DEBUG
    from app.main import _start_time
    
    uptime = time.time() - _start_time
    uptime_str = f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m" if uptime > 60 else f"{int(uptime)}s"
    
    return ApiResponse(
        success=True, 
        message="Service is healthy", 
        data={
            "name": APP_NAME,
            "version": APP_VERSION,
            "status": "healthy",
            "uptime": uptime_str,
            "environment": "production" if not DEBUG else "development"
        }
    ).model_dump()


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


@router.get("/metrics", tags=["Health"])
def get_metrics():
    """Get application metrics"""
    from app.metrics.metrics import metrics
    return metrics.get_metrics()


@router.post(
    "/recommend", 
    response_model=RecommendationResponse, 
    tags=["Recommendations"],
    summary="Get personalized recommendations",
    description="Generate personalized skill path recommendations based on user profile including age, budget, experience level, goals, and location.",
    responses={
        200: {"description": "Recommendations generated successfully"},
        401: {"description": "Unauthorized - authentication required"}
    }
)
def recommend(
    profile: ProfileInput, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Get personalized recommendations based on user profile"""
    item_repository = ItemRepository(db)
    recommendation_service = RecommendationService(item_repository)
    recommendations = recommendation_service.build_recommendations(profile)
    
    # Save recommendation history in background
    profile_dict = profile.model_dump()
    recommendations_list = recommendations
    background_tasks.add_task(save_recommendation_history, current_user.id, profile_dict, recommendations_list)
    
    return RecommendationResponse(recommendations=recommendations)


@router.get(
    "/items", 
    response_model=PaginatedResponse[ItemRead], 
    tags=["Items"],
    summary="List items with filtering and pagination",
    description="Retrieve a paginated list of items with advanced filtering, search, and sorting capabilities. Admin only.",
    responses={
        200: {"description": "Items retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - admin access required"}
    }
)
def list_items(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    location: Optional[str] = Query(None, description="Filter by location"),
    goal: Optional[str] = Query(None, description="Filter by goal"),
    skill_level: Optional[str] = Query(None, description="Filter by skill level"),
    price_min: Optional[float] = Query(None, ge=0, description="Minimum price"),
    price_max: Optional[float] = Query(None, ge=0, description="Maximum price"),
    search: Optional[str] = Query(None, description="Search in name, description, category"),
    sort_by: Optional[str] = Query(None, description="Sort by field (price, name, created_at)"),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Sort order (asc or desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """List items with advanced filtering, search, sorting, and pagination (admin only)"""
    from app.cache.cache import cache
    
    # Create cache key
    cache_key = f"items_{page}_{limit}_{category}_{location}_{goal}_{skill_level}_{price_min}_{price_max}_{search}_{sort_by}_{order}"
    
    # Try cache first
    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response
    
    item_repository = ItemRepository(db)
    item_service = ItemService(item_repository)
    
    filters = {
        "category": category,
        "location": location,
        "goal": goal,
        "skill_level": skill_level,
        "price_min": price_min,
        "price_max": price_max,
    }
    
    paginated_data = item_service.get_paginated_items(page, limit, filters, search, sort_by, order)
    response = PaginatedResponse(
        page=paginated_data["page"],
        limit=paginated_data["limit"],
        total=paginated_data["total"],
        total_pages=paginated_data["total_pages"],
        has_next=paginated_data["has_next"],
        has_previous=paginated_data["has_previous"],
        items=[ItemRead.model_validate(item) for item in paginated_data["items"]],
    )
    
    # Cache response for 5 minutes
    cache.set(cache_key, response, ttl=300)
    
    return response


@router.post("/items", response_model=ItemRead, tags=["Items"])
def create_item(
    item: ItemCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Create a new item (admin only)"""
    from app.cache.cache import cache
    
    item_repository = ItemRepository(db)
    item_service = ItemService(item_repository)
    new_item = item_service.create_item(item)
    
    # Invalidate items cache
    cache.clear()
    
    # Generate analytics in background
    background_tasks.add_task(generate_item_analytics, new_item.id)
    
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
