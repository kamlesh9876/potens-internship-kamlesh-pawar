import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.database import Base
from app.db.session import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.item import Item
from alembic.config import Config
from alembic import command

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    
    try:
        yield session
        session.commit()
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        test_client.headers.update({"x-test-client": "true"})
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing"""
    admin = User(
        username="admin",
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        is_active=True,
        is_admin=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def normal_user(db_session):
    """Create a normal user for testing"""
    user = User(
        username="testuser",
        email="user@test.com",
        hashed_password=get_password_hash("user123"),
        full_name="Test User",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(client, admin_user):
    """Get admin access token"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
def user_token(client, normal_user):
    """Get normal user access token"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "user123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
def sample_items(db_session):
    """Create sample items for testing"""
    items = [
        Item(
            name="Python Bootcamp",
            category="Programming",
            price=99.99,
            skill_level="Beginner",
            goal="Career Change",
            location="Online",
            pace="Self-paced",
            description="Learn Python from scratch"
        ),
        Item(
            name="Data Science Course",
            category="Data Science",
            price=149.99,
            skill_level="Intermediate",
            goal="Career Growth",
            location="Online",
            pace="Self-paced",
            description="Master data science with Python"
        ),
        Item(
            name="Web Development",
            category="Web Development",
            price=79.99,
            skill_level="Beginner",
            goal="Career Change",
            location="Online",
            pace="Instructor-led",
            description="Build modern web applications"
        )
    ]
    
    for item in items:
        db_session.add(item)
    
    db_session.commit()
    return items


@pytest.fixture
def recommendation_data():
    """Sample recommendation profile data"""
    return {
        "age": 25,
        "budget": 200,
        "experience_level": "Beginner",
        "goals": ["Career Change"],
        "location": "Online",
        "preferred_pace": "Self-paced"
    }
