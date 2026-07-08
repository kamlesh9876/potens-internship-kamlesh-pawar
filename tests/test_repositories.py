import pytest
from app.repositories.item_repository import ItemRepository
from app.repositories.user_repository import UserRepository
from app.models.item import Item
from app.models.user import User
from app.core.security import get_password_hash


def test_item_repository_create(db_session):
    """Test ItemRepository create method"""
    repo = ItemRepository(db_session)
    item_data = {
        "name": "Test Course",
        "category": "Programming",
        "price": 99.99,
        "skill_level": "Beginner",
        "goal": "Career Growth",
        "location": "Online",
        "pace": "Self-paced",
        "description": "Test description"
    }
    item = repo.create(item_data)
    
    assert item.id is not None
    assert item.name == "Test Course"
    assert item.price == 99.99


def test_item_repository_get_item(db_session):
    """Test ItemRepository get_item method"""
    repo = ItemRepository(db_session)
    
    # Create an item first
    item_data = {
        "name": "Test Course",
        "category": "Programming",
        "price": 99.99,
        "skill_level": "Beginner",
        "goal": "Career Growth",
        "location": "Online",
        "pace": "Self-paced",
        "description": "Test description"
    }
    created_item = repo.create(item_data)
    
    # Retrieve the item
    retrieved_item = repo.get_item(created_item.id)
    
    assert retrieved_item is not None
    assert retrieved_item.id == created_item.id
    assert retrieved_item.name == "Test Course"


def test_item_repository_get_item_not_found(db_session):
    """Test ItemRepository get_item with non-existent ID"""
    repo = ItemRepository(db_session)
    item = repo.get_item(99999)
    assert item is None


def test_item_repository_update(db_session):
    """Test ItemRepository update method"""
    repo = ItemRepository(db_session)
    
    # Create an item
    item_data = {
        "name": "Test Course",
        "category": "Programming",
        "price": 99.99,
        "skill_level": "Beginner",
        "goal": "Career Growth",
        "location": "Online",
        "pace": "Self-paced",
        "description": "Test description"
    }
    item = repo.create(item_data)
    
    # Update the item
    updated_item = repo.update(item, {"name": "Updated Course", "price": 149.99})
    
    assert updated_item.name == "Updated Course"
    assert updated_item.price == 149.99


def test_item_repository_delete(db_session):
    """Test ItemRepository delete method"""
    repo = ItemRepository(db_session)
    
    # Create an item
    item_data = {
        "name": "Test Course",
        "category": "Programming",
        "price": 99.99,
        "skill_level": "Beginner",
        "goal": "Career Growth",
        "location": "Online",
        "pace": "Self-paced",
        "description": "Test description"
    }
    item = repo.create(item_data)
    item_id = item.id
    
    # Delete the item
    repo.delete(item)
    
    # Verify deletion
    deleted_item = repo.get_item(item_id)
    assert deleted_item is None


def test_item_repository_list_items(db_session):
    """Test ItemRepository list_items method"""
    repo = ItemRepository(db_session)
    
    # Create multiple items
    for i in range(3):
        item_data = {
            "name": f"Test Course {i}",
            "category": "Programming",
            "price": 99.99 + i * 10,
            "skill_level": "Beginner",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": f"Test description {i}"
        }
        repo.create(item_data)
    
    # List items
    items = repo.list_items()
    
    assert len(items) == 3


def test_item_repository_list_items_with_filters(db_session):
    """Test ItemRepository list_items with filters"""
    repo = ItemRepository(db_session)
    
    # Create items with different categories
    repo.create({
        "name": "Python Course",
        "category": "Programming",
        "price": 99.99,
        "skill_level": "Beginner",
        "goal": "Career Growth",
        "location": "Online",
        "pace": "Self-paced",
        "description": "Python course"
    })
    
    repo.create({
        "name": "Data Science Course",
        "category": "Data Science",
        "price": 149.99,
        "skill_level": "Intermediate",
        "goal": "Career Growth",
        "location": "Online",
        "pace": "Self-paced",
        "description": "Data science course"
    })
    
    # Filter by category
    filtered_items = repo.list_items(filters={"category": "Programming"})
    
    assert len(filtered_items) == 1
    assert filtered_items[0].category == "Programming"


def test_user_repository_create(db_session):
    """Test UserRepository create method"""
    repo = UserRepository(db_session)
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("TestPass123"),
        "full_name": "Test User",
        "is_active": True,
        "is_admin": False
    }
    user = repo.create(user_data)
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_user_repository_get_by_email(db_session):
    """Test UserRepository get_by_email method"""
    repo = UserRepository(db_session)
    
    # Create a user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("TestPass123"),
        "full_name": "Test User",
        "is_active": True,
        "is_admin": False
    }
    repo.create(user_data)
    
    # Retrieve by email
    user = repo.get_by_email("test@example.com")
    
    assert user is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"


def test_user_repository_get_by_username(db_session):
    """Test UserRepository get_by_username method"""
    repo = UserRepository(db_session)
    
    # Create a user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("TestPass123"),
        "full_name": "Test User",
        "is_active": True,
        "is_admin": False
    }
    repo.create(user_data)
    
    # Retrieve by username
    user = repo.get_by_username("testuser")
    
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_user_repository_email_exists(db_session):
    """Test UserRepository email_exists method"""
    repo = UserRepository(db_session)
    
    # Create a user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("TestPass123"),
        "full_name": "Test User",
        "is_active": True,
        "is_admin": False
    }
    repo.create(user_data)
    
    # Check email exists
    assert repo.email_exists("test@example.com") is True
    assert repo.email_exists("nonexistent@example.com") is False


def test_user_repository_username_exists(db_session):
    """Test UserRepository username_exists method"""
    repo = UserRepository(db_session)
    
    # Create a user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("TestPass123"),
        "full_name": "Test User",
        "is_active": True,
        "is_admin": False
    }
    repo.create(user_data)
    
    # Check username exists
    assert repo.username_exists("testuser") is True
    assert repo.username_exists("nonexistent") is False


def test_user_repository_get_by_id(db_session):
    """Test UserRepository get_by_id method"""
    repo = UserRepository(db_session)
    
    # Create a user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("TestPass123"),
        "full_name": "Test User",
        "is_active": True,
        "is_admin": False
    }
    created_user = repo.create(user_data)
    
    # Retrieve by ID
    user = repo.get_by_id(created_user.id)
    
    assert user is not None
    assert user.id == created_user.id
    assert user.username == "testuser"
