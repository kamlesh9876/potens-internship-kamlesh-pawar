import pytest
from tests.fixtures import auth_headers, assert_response_success, assert_response_error


def test_register_success(client):
    """Test successful user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPass123",
            "full_name": "New User"
        }
    )
    assert_response_success(response, 200)
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "hashed_password" not in data
    assert data["id"] is not None


def test_register_duplicate_email(client, normal_user):
    """Test registration with duplicate email"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "different",
            "email": "user@test.com",
            "password": "TestPass123",
            "full_name": "Different User"
        }
    )
    assert_response_error(response, 400)


def test_register_duplicate_username(client, normal_user):
    """Test registration with duplicate username"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "different@example.com",
            "password": "TestPass123",
            "full_name": "Different User"
        }
    )
    assert_response_error(response, 400)


def test_register_weak_password(client):
    """Test registration with weak password"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "weak",
            "full_name": "Weak User"
        }
    )
    assert_response_error(response, 422)


def test_login_success(client, normal_user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "user123"}
    )
    assert_response_success(response, 200)
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_email(client):
    """Test login with wrong email"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "TestPass123"}
    )
    assert_response_error(response, 401)


def test_login_wrong_password(client, normal_user):
    """Test login with wrong password"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "WrongPass123"}
    )
    assert_response_error(response, 401)


def test_get_current_user(client, normal_user, user_token):
    """Test getting current user info with valid token"""
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers(user_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert data["email"] == "user@test.com"
    assert data["username"] == "testuser"


def test_get_current_user_no_token(client):
    """Test getting current user without token"""
    response = client.get("/api/v1/users/me")
    assert_response_error(response, 401)


def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token"""
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers("invalid_token")
    )
    assert_response_error(response, 401)


def test_get_current_user_expired_token(client):
    """Test getting current user with expired token"""
    # Use a malformed/expired token
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expired")
    )
    assert_response_error(response, 401)


def test_admin_endpoint_with_admin(client, admin_user, admin_token):
    """Test admin endpoint with admin user"""
    response = client.get(
        "/api/v1/users/users",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)


def test_admin_endpoint_with_regular_user(client, normal_user, user_token):
    """Test admin endpoint with regular user"""
    response = client.get(
        "/api/v1/users/users",
        headers=auth_headers(user_token)
    )
    assert_response_error(response, 403)


def test_change_password_success(client, normal_user, user_token):
    """Test successful password change"""
    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "old_password": "user123",
            "new_password": "NewPass456"
        },
        headers=auth_headers(user_token)
    )
    assert_response_success(response, 200)
    
    # Verify new password works
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "NewPass456"}
    )
    assert_response_success(login_response, 200)


def test_change_password_wrong_old_password(client, normal_user, user_token):
    """Test password change with wrong old password"""
    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "old_password": "WrongPass123",
            "new_password": "NewPass456"
        },
        headers=auth_headers(user_token)
    )
    assert_response_error(response, 400)


def test_change_password_no_token(client):
    """Test password change without authentication"""
    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "old_password": "user123",
            "new_password": "NewPass456"
        }
    )
    assert_response_error(response, 401)


def test_jwt_tampering(client, normal_user):
    """Test JWT tampering detection"""
    # Get valid token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "user123"}
    )
    token = login_response.json()["access_token"]
    
    # Tamper with token (change last character)
    tampered_token = token[:-1] + ("X" if token[-1] != "X" else "Y")
    
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers(tampered_token)
    )
    assert_response_error(response, 401)
