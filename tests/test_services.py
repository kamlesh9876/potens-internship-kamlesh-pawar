import pytest
from unittest.mock import Mock, patch
from app.services.auth_service import AuthService
from app.services.item_service import ItemService
from app.services.recommendation_service import RecommendationService
from app.services.explain_service import ExplainService
from app.schemas.user import UserCreate, UserLogin
from app.schemas.item import ItemCreate, ItemUpdate
from app.core.exceptions import NotFoundException
from app.models.user import User
from app.models.item import Item


def test_auth_service_register_success(db_session):
    """Test AuthService register with valid data"""
    mock_repo = Mock()
    mock_repo.email_exists.return_value = False
    mock_repo.username_exists.return_value = False
    mock_repo.create.return_value = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        is_active=True,
        is_admin=False
    )
    
    auth_service = AuthService(mock_repo)
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPass123",
        full_name="Test User"
    )
    
    user = auth_service.register(user_data)
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    mock_repo.email_exists.assert_called_once_with("test@example.com")
    mock_repo.username_exists.assert_called_once_with("testuser")
    mock_repo.create.assert_called_once()


def test_auth_service_register_duplicate_email(db_session):
    """Test AuthService register with duplicate email"""
    mock_repo = Mock()
    mock_repo.email_exists.return_value = True
    
    auth_service = AuthService(mock_repo)
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPass123",
        full_name="Test User"
    )
    
    with pytest.raises(Exception) as exc_info:
        auth_service.register(user_data)
    assert "already registered" in str(exc_info.value)


def test_auth_service_login_success(db_session):
    """Test AuthService login with valid credentials"""
    mock_repo = Mock()
    mock_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        is_active=True,
        is_admin=False
    )
    mock_repo.get_by_email.return_value = mock_user
    
    with patch('app.services.auth_service.verify_password', return_value=True):
        with patch('app.services.auth_service.create_access_token', return_value="test_token"):
            auth_service = AuthService(mock_repo)
            login_data = UserLogin(email="test@example.com", password="TestPass123")
            
            token = auth_service.login(login_data)
            
            assert token["access_token"] == "test_token"
            assert token["token_type"] == "bearer"


def test_auth_service_login_wrong_password(db_session):
    """Test AuthService login with wrong password"""
    mock_repo = Mock()
    mock_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        is_active=True,
        is_admin=False
    )
    mock_repo.get_by_email.return_value = mock_user
    
    with patch('app.services.auth_service.verify_password', return_value=False):
        auth_service = AuthService(mock_repo)
        login_data = UserLogin(email="test@example.com", password="WrongPass123")
        
        with pytest.raises(Exception) as exc_info:
            auth_service.login(login_data)
        assert "Incorrect password" in str(exc_info.value)


def test_item_service_create_item(db_session):
    """Test ItemService create_item"""
    mock_repo = Mock()
    mock_item = Item(
        id=1,
        name="Test Course",
        category="Programming",
        price=99.99,
        skill_level="Beginner",
        goal="Career Growth",
        location="Online",
        pace="Self-paced",
        description="Test description"
    )
    mock_repo.create.return_value = mock_item
    
    item_service = ItemService(mock_repo)
    item_data = ItemCreate(
        name="Test Course",
        category="Programming",
        price=99.99,
        skill_level="Beginner",
        goal="Career Growth",
        location="Online",
        pace="Self-paced",
        description="Test description"
    )
    
    item = item_service.create_item(item_data)
    
    assert item.name == "Test Course"
    assert item.price == 99.99
    mock_repo.create.assert_called_once()


def test_item_service_get_item_success(db_session):
    """Test ItemService get_item with valid ID"""
    mock_repo = Mock()
    mock_item = Item(
        id=1,
        name="Test Course",
        category="Programming",
        price=99.99,
        skill_level="Beginner",
        goal="Career Growth",
        location="Online",
        pace="Self-paced",
        description="Test description"
    )
    mock_repo.get_item.return_value = mock_item
    
    item_service = ItemService(mock_repo)
    
    item = item_service.get_item(1)
    
    assert item.id == 1
    assert item.name == "Test Course"
    mock_repo.get_item.assert_called_once_with(1)


def test_item_service_get_item_not_found(db_session):
    """Test ItemService get_item with invalid ID"""
    mock_repo = Mock()
    mock_repo.get_item.return_value = None
    
    item_service = ItemService(mock_repo)
    
    with pytest.raises(NotFoundException) as exc_info:
        item_service.get_item(999)
    assert "not found" in str(exc_info.value)


def test_item_service_update_item(db_session):
    """Test ItemService update_item"""
    mock_repo = Mock()
    mock_item = Item(
        id=1,
        name="Test Course",
        category="Programming",
        price=99.99,
        skill_level="Beginner",
        goal="Career Growth",
        location="Online",
        pace="Self-paced",
        description="Test description"
    )
    mock_repo.get_item.return_value = mock_item
    mock_repo.update.return_value = mock_item
    
    item_service = ItemService(mock_repo)
    update_data = ItemUpdate(name="Updated Course", price=149.99)
    
    updated_item = item_service.update_item(1, update_data)
    
    mock_repo.get_item.assert_called_once_with(1)
    mock_repo.update.assert_called_once()


def test_item_service_delete_item(db_session):
    """Test ItemService delete_item"""
    mock_repo = Mock()
    mock_item = Item(
        id=1,
        name="Test Course",
        category="Programming",
        price=99.99,
        skill_level="Beginner",
        goal="Career Growth",
        location="Online",
        pace="Self-paced",
        description="Test description"
    )
    mock_repo.get_item.return_value = mock_item
    
    item_service = ItemService(mock_repo)
    
    item_service.delete_item(1)
    
    mock_repo.get_item.assert_called_once_with(1)
    mock_repo.delete.assert_called_once_with(mock_item)


def test_recommendation_service_build_recommendations(db_session):
    """Test RecommendationService build_recommendations"""
    mock_repo = Mock()
    mock_items = [
        Item(
            id=1,
            name="Python Course",
            category="Programming",
            price=99.99,
            skill_level="Beginner",
            goal="Career Growth",
            location="Online",
            pace="Self-paced",
            description="Python course"
        ),
        Item(
            id=2,
            name="Web Dev Course",
            category="Web Development",
            price=79.99,
            skill_level="Beginner",
            goal="Career Change",
            location="Online",
            pace="Self-paced",
            description="Web dev course"
        )
    ]
    mock_repo.list_items.return_value = mock_items
    
    recommendation_service = RecommendationService(mock_repo)
    profile = {
        "age": 25,
        "budget": 200,
        "experience_level": "Beginner",
        "goals": ["Career Change"],
        "location": "Online",
        "preferred_pace": "Self-paced"
    }
    
    recommendations = recommendation_service.build_recommendations(profile)
    
    assert len(recommendations) > 0
    mock_repo.list_items.assert_called_once()


def test_explain_service_explain_item(db_session):
    """Test ExplainService explain_item"""
    explain_service = ExplainService()
    mock_item = Item(
        id=1,
        name="Python Course",
        category="Programming",
        price=99.99,
        skill_level="Beginner",
        goal="Career Growth",
        location="Online",
        pace="Self-paced",
        description="Python course"
    )
    
    explanation = explain_service.explain_item(mock_item)
    
    assert explanation is not None
    assert isinstance(explanation, str)
    assert len(explanation) > 0


def test_item_service_list_items_with_filters(db_session):
    """Test ItemService list_items with filters"""
    mock_repo = Mock()
    mock_repo.db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    
    item_service = ItemService(mock_repo)
    
    filters = {"category": "Programming", "price_min": 50}
    items = item_service.list_items(filters=filters)
    
    assert isinstance(items, list)


def test_item_service_list_items_with_search(db_session):
    """Test ItemService list_items with search"""
    mock_repo = Mock()
    mock_repo.db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    
    item_service = ItemService(mock_repo)
    
    items = item_service.list_items(search="Python")
    
    assert isinstance(items, list)


def test_item_service_list_items_with_sorting(db_session):
    """Test ItemService list_items with sorting"""
    mock_repo = Mock()
    mock_repo.db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    
    item_service = ItemService(mock_repo)
    
    items = item_service.list_items(sort_by="price", order="desc")
    
    assert isinstance(items, list)


def test_item_service_get_paginated_items(db_session):
    """Test ItemService get_paginated_items"""
    mock_repo = Mock()
    mock_repo.db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    
    item_service = ItemService(mock_repo)
    
    paginated_data = item_service.get_paginated_items(page=1, limit=10)
    
    assert "items" in paginated_data
    assert "total" in paginated_data
    assert "page" in paginated_data
    assert "limit" in paginated_data
    assert "total_pages" in paginated_data
    assert "has_next" in paginated_data
    assert "has_previous" in paginated_data
