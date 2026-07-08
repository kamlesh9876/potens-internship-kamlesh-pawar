import pytest
from tests.fixtures import auth_headers, assert_response_success, assert_response_error


def test_get_current_user(client, normal_user, user_token):
    """Test getting current user profile"""
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers(user_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert data["email"] == "user@test.com"
    assert data["username"] == "testuser"


def test_update_current_user(client, normal_user, user_token):
    """Test updating current user profile"""
    response = client.put(
        "/api/v1/users/me",
        json={"full_name": "Updated Name"},
        headers=auth_headers(user_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert data["full_name"] == "Updated Name"


def test_update_current_user_unauthorized(client):
    """Test updating user without authentication"""
    response = client.put(
        "/api/v1/users/me",
        json={"full_name": "Updated Name"}
    )
    assert_response_error(response, 401)


def test_list_users_admin(client, admin_user, admin_token):
    """Test listing all users as admin"""
    response = client.get(
        "/api/v1/users/users",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert isinstance(data, list)


def test_list_users_forbidden(client, normal_user, user_token):
    """Test listing users as non-admin"""
    response = client.get(
        "/api/v1/users/users",
        headers=auth_headers(user_token)
    )
    assert_response_error(response, 403)


def test_get_user_by_id_admin(client, normal_user, admin_token):
    """Test getting user by ID as admin"""
    response = client.get(
        f"/api/v1/users/{normal_user.id}",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
    data = response.json()
    assert data["id"] == normal_user.id


def test_get_user_by_id_forbidden(client, normal_user, user_token):
    """Test getting user by ID as non-admin"""
    response = client.get(
        f"/api/v1/users/{normal_user.id}",
        headers=auth_headers(user_token)
    )
    assert_response_error(response, 403)


def test_deactivate_user_admin(client, normal_user, admin_token):
    """Test deactivating user as admin"""
    response = client.post(
        f"/api/v1/users/{normal_user.id}/deactivate",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)


def test_deactivate_user_forbidden(client, normal_user, user_token):
    """Test deactivating user as non-admin"""
    response = client.post(
        f"/api/v1/users/{normal_user.id}/deactivate",
        headers=auth_headers(user_token)
    )
    assert_response_error(response, 403)


def test_activate_user_admin(client, normal_user, admin_token):
    """Test activating user as admin"""
    response = client.post(
        f"/api/v1/users/{normal_user.id}/activate",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)


def test_make_user_admin(client, normal_user, admin_token):
    """Test granting admin privileges"""
    response = client.post(
        f"/api/v1/users/{normal_user.id}/make-admin",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)


def test_revoke_user_admin(client, admin_user, admin_token):
    """Test revoking admin privileges"""
    response = client.post(
        f"/api/v1/users/{admin_user.id}/revoke-admin",
        headers=auth_headers(admin_token)
    )
    assert_response_success(response, 200)
