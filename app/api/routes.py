from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.config import ADMIN_TOKEN, APP_NAME
from app.core.exceptions import AppError
from app.core.logging import logger
from app.db.session import get_db
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.schemas.pagination import PaginatedResponse
from app.schemas.recommendation import ProfileInput, RecommendationResponse
from app.repositories.item_repository import ItemRepository
from app.services.recommendation_service import RecommendationService
from app.services.explain_service import ExplainService
from app.models.item import Item
from app.schemas.response import ApiResponse

router = APIRouter()


def get_admin_token(x_admin_token: Optional[str] = Header(None)) -> str:
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Admin token required")
    return x_admin_token


@router.get("/health")
def healthcheck():
    return ApiResponse(success=True, message="Service is healthy", data={"name": APP_NAME, "status": "Running"}).model_dump()


@router.get("/health/application")
def health_application():
    return ApiResponse(success=True, message="Application is running", data={"name": APP_NAME}).model_dump()


@router.get("/health/db")
def health_database(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return ApiResponse(success=True, message="Database reachable", data={"status": "ok"}).model_dump()
    except Exception as exc:
        logger.error("Database health check failed", exc_info=exc)
        raise AppError("Database unavailable", status_code=503) from exc


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(profile: ProfileInput, db: Session = Depends(get_db)):
    repository = ItemRepository(db)
    service = RecommendationService()
    items = repository.list_items()
    recommendations = service.build_recommendations(profile, items)
    return RecommendationResponse(recommendations=recommendations)


@router.get("/items", response_model=PaginatedResponse[ItemRead])
def list_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    name: Optional[str] = None,
    category: Optional[str] = None,
    goal: Optional[str] = None,
    location: Optional[str] = None,
    skill_level: Optional[str] = None,
    db: Session = Depends(get_db),
    token: str = Depends(get_admin_token),
):
    repository = ItemRepository(db)
    filters = {
        "name": name,
        "category": category,
        "goal": goal,
        "location": location,
        "skill_level": skill_level,
    }
    items = repository.list_items(filters=filters)
    total = len(items)
    sliced_items = items[(page - 1) * limit: page * limit]
    return PaginatedResponse(
        page=page,
        limit=limit,
        total=total,
        items=[ItemRead(**item.__dict__) for item in sliced_items],
    )


@router.post("/items", response_model=ItemRead)
def create_item(item: ItemCreate, db: Session = Depends(get_db), token: str = Depends(get_admin_token)):
    repository = ItemRepository(db)
    new_item = Item(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return ItemRead(**new_item.__dict__)


@router.get("/items/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db), token: str = Depends(get_admin_token)):
    repository = ItemRepository(db)
    item = repository.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemRead(**item.__dict__)


@router.put("/items/{item_id}", response_model=ItemRead)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db), token: str = Depends(get_admin_token)):
    repository = ItemRepository(db)
    existing = repository.get_item(item_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(existing, field, value)
    db.commit()
    db.refresh(existing)
    return ItemRead(**existing.__dict__)


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), token: str = Depends(get_admin_token)):
    repository = ItemRepository(db)
    item = repository.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}


@router.get("/explain/{item_id}")
def explain_item(item_id: int, db: Session = Depends(get_db)):
    repository = ItemRepository(db)
    item = repository.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    explanation = ExplainService().explain_item(item)
    return {"item_id": item_id, "explanation": explanation}
