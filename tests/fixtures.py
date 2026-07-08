"""Additional test fixtures and helper functions"""
import pytest
from app.schemas.user import UserCreate, UserLogin
from app.schemas.item import ItemCreate


def create_user_data(email="test@example.com", username="testuser", password="Test1234"):
    """Helper to create user data"""
    return UserCreate(
        email=email,
        username=username,
        password=password,
        full_name="Test User"
    )


def create_login_data(email="test@example.com", password="Test1234"):
    """Helper to create login data"""
    return UserLogin(email=email, password=password)


def create_item_data(name="Test Item", category="Test", price=99.99):
    """Helper to create item data"""
    return ItemCreate(
        name=name,
        category=category,
        price=price,
        skill_level="Beginner",
        goal="Career Growth",
        location="Online",
        pace="Self-paced",
        description="Test description"
    )


def auth_headers(token):
    """Helper to create authorization headers"""
    return {"Authorization": f"Bearer {token}"}


def assert_response_success(response, status_code=200):
    """Helper to assert successful response"""
    assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {response.text}"


def assert_response_error(response, status_code):
    """Helper to assert error response"""
    assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {response.text}"
