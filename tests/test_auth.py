import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base
from app.models.user import User
from app.core.security import get_password_hash

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(db):
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("TestPass123"),
        full_name="Test User",
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_user(db):
    """Create an admin user"""
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("AdminPass123"),
        full_name="Admin User",
        is_active=True,
        is_admin=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_register_success(db):
    """Test successful user registration"""
    response = client.post("/auth/register", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "NewPass123",
        "full_name": "New User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "hashed_password" not in data
    assert data["id"] is not None


def test_register_duplicate_email(db, test_user):
    """Test registration with duplicate email"""
    response = client.post("/auth/register", json={
        "username": "different",
        "email": "test@example.com",
        "password": "TestPass123",
        "full_name": "Different User"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_duplicate_username(db, test_user):
    """Test registration with duplicate username"""
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "different@example.com",
        "password": "TestPass123",
        "full_name": "Different User"
    })
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]


def test_register_weak_password(db):
    """Test registration with weak password"""
    response = client.post("/auth/register", json={
        "username": "weakuser",
        "email": "weak@example.com",
        "password": "weak",
        "full_name": "Weak User"
    })
    assert response.status_code == 422


def test_login_success(db, test_user):
    """Test successful login"""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_email(db):
    """Test login with wrong email"""
    response = client.post("/auth/login", json={
        "email": "wrong@example.com",
        "password": "TestPass123"
    })
    assert response.status_code == 401


def test_login_wrong_password(db, test_user):
    """Test login with wrong password"""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "WrongPass123"
    })
    assert response.status_code == 401


def test_get_current_user(db, test_user):
    """Test getting current user info with valid token"""
    # First login to get token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123"
    })
    token = login_response.json()["access_token"]
    
    # Use token to get current user
    response = client.get("/users/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


def test_get_current_user_no_token():
    """Test getting current user without token"""
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token():
    """Test getting current user with invalid token"""
    response = client.get("/users/me", headers={
        "Authorization": "Bearer invalid_token"
    })
    assert response.status_code == 401


def test_admin_endpoint_with_admin(db, admin_user):
    """Test admin endpoint with admin user"""
    # Login as admin
    login_response = client.post("/auth/login", json={
        "email": "admin@example.com",
        "password": "AdminPass123"
    })
    token = login_response.json()["access_token"]
    
    # Access admin endpoint
    response = client.get("/users/users", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200


def test_admin_endpoint_with_regular_user(db, test_user):
    """Test admin endpoint with regular user"""
    # Login as regular user
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123"
    })
    token = login_response.json()["access_token"]
    
    # Try to access admin endpoint
    response = client.get("/users/users", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 403


def test_change_password_success(db, test_user):
    """Test successful password change"""
    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123"
    })
    token = login_response.json()["access_token"]
    
    # Change password
    response = client.post("/auth/change-password", 
        json={
            "old_password": "TestPass123",
            "new_password": "NewPass456"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Verify new password works
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "NewPass456"
    })
    assert login_response.status_code == 200


def test_change_password_wrong_old_password(db, test_user):
    """Test password change with wrong old password"""
    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123"
    })
    token = login_response.json()["access_token"]
    
    # Try to change with wrong old password
    response = client.post("/auth/change-password",
        json={
            "old_password": "WrongPass123",
            "new_password": "NewPass456"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400


def test_recommendation_requires_auth(db):
    """Test that recommendation endpoint requires authentication"""
    response = client.post("/recommend", json={
        "age": 28,
        "budget": 200,
        "experience_level": "beginner",
        "goal": "career-switch",
        "location": "remote"
    })
    assert response.status_code == 401


def test_recommendation_with_auth(db, test_user):
    """Test recommendation endpoint with valid authentication"""
    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123"
    })
    token = login_response.json()["access_token"]
    
    # Access recommendation endpoint
    response = client.post("/recommend",
        json={
            "age": 28,
            "budget": 200,
            "experience_level": "beginner",
            "goal": "career-switch",
            "location": "remote"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
