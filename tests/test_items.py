import pytest
from tests.fixtures import auth_headers, assert_response_success, assert_response_error


def test_list_items_success(client, sample_items, admin_token):
    """Test listing items successfully"""
    response = client.get(
        "/api/v1/items",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert "total_pages" in data
    assert "has_next" in data
    assert "has_previous" in data


def test_list_items_pagination(client, sample_items, admin_token):
    """Test item pagination"""
    response = client.get(
        "/api/v1/items?page=1&limit=2",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["has_next"] is True
    assert data["has_previous"] is False


def test_list_items_filter_by_category(client, sample_items, admin_token):
    """Test filtering items by category"""
    response = client.get(
        "/api/v1/items?category=Programming",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert all(item["category"] == "Programming" for item in data["items"])


def test_list_items_filter_by_price_range(client, sample_items, admin_token):
    """Test filtering items by price range"""
    response = client.get(
        "/api/v1/items?price_min=80&price_max=100",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    for item in data["items"]:
        assert 80 <= item["price"] <= 100


def test_list_items_search(client, sample_items, admin_token):
    """Test searching items"""
    response = client.get(
        "/api/v1/items?search=Python",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert len(data["items"]) > 0


def test_list_items_sort_by_price(client, sample_items, admin_token):
    """Test sorting items by price"""
    response = client.get(
        "/api/v1/items?sort_by=price&order=asc",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    prices = [item["price"] for item in data["items"]]
    assert prices == sorted(prices)


def test_list_items_unauthorized(client, sample_items):
    """Test listing items without authentication"""
    response = client.get("/api/v1/items")
    assert_response_error(response, 401)


def test_list_items_forbidden(client, sample_items, user_token):
    """Test listing items with non-admin user"""
    response = client.get(
        "/api/v1/items",
        headers=auth_headers(user_token)
    )
    assert_response_error(response, 403)


def test_create_item_success(client, admin_token):
    """Test creating an item successfully"""
    response = client.post(
        "/api/v1/items",
        json={
            "name": "New Course",
            "category": "Test",
            "price": 199.99,
            "skill_level": "Intermediate",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "A new test course"
        },
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert data["name"] == "New Course"
    assert data["price"] == 199.99


def test_create_item_unauthorized(client):
    """Test creating item without authentication"""
    response = client.post(
        "/api/v1/items",
        json={
            "name": "New Course",
            "category": "Test",
            "price": 199.99,
            "skill_level": "Intermediate",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "A new test course"
        }
    )
    assert_response_error(response, 401)


def test_create_item_forbidden(client, user_token):
    """Test creating item with non-admin user"""
    response = client.post(
        "/api/v1/items",
        json={
            "name": "New Course",
            "category": "Test",
            "price": 199.99,
            "skill_level": "Intermediate",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "A new test course"
        },
        headers=auth_headers(user_token)
    )
    assert_response_error(response, 403)


def test_create_item_validation_error(client, admin_token):
    """Test creating item with invalid data"""
    response = client.post(
        "/api/v1/items",
        json={
            "name": "",  # Empty name
            "category": "Test",
            "price": -10,  # Negative price
            "skill_level": "Intermediate",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "A new test course"
        },
        headers=auth_headers(admin_token)
    )
    assert_response_error(response, 422)


def test_get_item_success(client, sample_items, admin_token):
    """Test getting a single item"""
    item_id = sample_items[0].id
    response = client.get(
        f"/api/v1/items/{item_id}",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == sample_items[0].name


def test_get_item_not_found(client, admin_token):
    """Test getting non-existent item"""
    response = client.get(
        "/api/v1/items/99999",
        headers=auth_headers(admin_token)
    )
    assert_response_error(response, 404)


def test_get_item_unauthorized(client, sample_items):
    """Test getting item without authentication"""
    item_id = sample_items[0].id
    response = client.get(f"/api/v1/items/{item_id}")
    assert_response_error(response, 401)


def test_update_item_success(client, sample_items, admin_token):
    """Test updating an item"""
    item_id = sample_items[0].id
    response = client.put(
        f"/api/v1/items/{item_id}",
        json={"name": "Updated Name", "price": 299.99},
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["price"] == 299.99


def test_update_item_not_found(client, admin_token):
    """Test updating non-existent item"""
    response = client.put(
        "/api/v1/items/99999",
        json={"name": "Updated Name"},
        headers=auth_headers(admin_token)
    )
    assert_response_error(response, 404)


def test_update_item_unauthorized(client, sample_items):
    """Test updating item without authentication"""
    item_id = sample_items[0].id
    response = client.put(
        f"/api/v1/items/{item_id}",
        json={"name": "Updated Name"}
    )
    assert_response_error(response, 401)


def test_update_item_forbidden(client, sample_items, user_token):
    """Test updating item with non-admin user"""
    item_id = sample_items[0].id
    response = client.put(
        f"/api/v1/items/{item_id}",
        json={"name": "Updated Name"},
        headers=auth_headers(user_token)
    )
    assert_response_error(response, 403)


def test_delete_item_success(client, sample_items, admin_token):
    """Test deleting an item"""
    item_id = sample_items[0].id
    response = client.delete(
        f"/api/v1/items/{item_id}",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
    
    # Verify item is deleted
    get_response = client.get(
        f"/api/v1/items/{item_id}",
        headers=auth_headers(admin_token)
    )
    assert_response_error(get_response, 404)


def test_delete_item_not_found(client, admin_token):
    """Test deleting non-existent item"""
    response = client.delete(
        "/api/v1/items/99999",
        headers=auth_headers(admin_token)
    )
    assert_response_error(response, 404)


def test_delete_item_unauthorized(client, sample_items):
    """Test deleting item without authentication"""
    item_id = sample_items[0].id
    response = client.delete(f"/api/v1/items/{item_id}")
    assert_response_error(response, 401)


def test_delete_item_forbidden(client, sample_items, user_token):
    """Test deleting item with non-admin user"""
    item_id = sample_items[0].id
    response = client.delete(
        f"/api/v1/items/{item_id}",
        headers=auth_headers(user_token)
    )
    assert_response_error(response, 403)


def test_recommendation_endpoint(client, user_token, recommendation_data):
    """Test recommendation endpoint"""
    response = client.post(
        "/api/v1/recommend",
        json=recommendation_data,
        headers=auth_headers(user_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert "recommendations" in data


def test_recommendation_unauthorized(client, recommendation_data):
    """Test recommendation without authentication"""
    response = client.post("/api/v1/recommend", json=recommendation_data)
    assert_response_error(response, 401)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert_response_success(response, 200)
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_health_db_check(client):
    """Test database health check"""
    response = client.get("/api/v1/health/db")
    assert_response_success(response, 200)


def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    response = client.get("/api/v1/metrics")
    assert_response_success(response, 200)
    data = response.json()
    assert "total_requests" in data
    assert "uptime_seconds" in data
