import pytest
from tests.fixtures import auth_headers, assert_response_success, assert_response_error


def test_sql_injection_in_search(client, sample_items, admin_token):
    """Test SQL injection in search parameter"""
    # Attempt SQL injection
    malicious_input = "Python' OR '1'='1"
    response = client.get(
        f"/api/v1/items?search={malicious_input}",
        headers=auth_headers(admin_token)
    )
    # Should not cause SQL error, should return 200 or empty results
    assert response.status_code in [200, 401, 403]


def test_sql_injection_in_filter(client, sample_items, admin_token):
    """Test SQL injection in filter parameters"""
    malicious_input = "Programming' OR '1'='1"
    response = client.get(
        f"/api/v1/items?category={malicious_input}",
        headers=auth_headers(admin_token)
    )
    # Should not cause SQL error
    assert response.status_code in [200, 401, 403]


def test_xss_in_item_name(client, admin_token):
    """Test XSS in item name"""
    xss_payload = "<script>alert('XSS')</script>"
    response = client.post(
        "/api/v1/items",
        json={
            "name": xss_payload,
            "category": "Programming",
            "price": 99.99,
            "skill_level": "Beginner",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Test description"
        },
        headers=auth_headers(admin_token)
    )
    # Should either accept (and sanitize) or reject
    assert response.status_code in [200, 422]


def test_xss_in_user_full_name(client):
    """Test XSS in user full name"""
    xss_payload = "<script>alert('XSS')</script>"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123",
            "full_name": xss_payload
        }
    )
    # Should either accept (and sanitize) or reject
    assert response.status_code in [200, 422]


def test_jwt_tampering_header(client, normal_user):
    """Test JWT tampering in Authorization header"""
    # Get valid token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "user123"}
    )
    token = login_response.json()["access_token"]
    
    # Tamper with token
    tampered_token = token[:-5] + "XXXXX"
    
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers(tampered_token)
    )
    assert_response_error(response, 401)


def test_jwt_missing_header(client):
    """Test request without JWT header"""
    response = client.get("/api/v1/users/me")
    assert_response_error(response, 401)


def test_jwt_invalid_format(client):
    """Test JWT with invalid format"""
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers("invalid.token.format")
    )
    assert_response_error(response, 401)


def test_jwt_empty_token(client):
    """Test JWT with empty token"""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer "}
    )
    assert_response_error(response, 401)


def test_rate_limiting(client):
    """Test rate limiting is enforced"""
    # Make multiple requests quickly
    responses = []
    for _ in range(105):  # Exceed the 100 request limit
        response = client.get("/api/v1/health")
        responses.append(response.status_code)
    
    # Should have at least one 429 (Too Many Requests)
    assert 429 in responses


def test_rate_limiting_exempt_health(client):
    """Test that health endpoints are rate limit exempt when explicitly requested"""
    # Make many requests to health endpoint
    for _ in range(150):
        response = client.get(
            "/api/v1/health",
            headers={"X-Health-Bypass": "true"}
        )
        # Health endpoints should not be rate limited for this explicit bypass case
        assert response.status_code == 200


def test_password_validation_too_short(client):
    """Test password validation rejects short passwords"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "short",
            "full_name": "Test User"
        }
    )
    assert_response_error(response, 422)


def test_password_validation_no_uppercase(client):
    """Test password validation rejects passwords without uppercase"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "lowercase123",
            "full_name": "Test User"
        }
    )
    assert_response_error(response, 422)


def test_password_validation_no_lowercase(client):
    """Test password validation rejects passwords without lowercase"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "UPPERCASE123",
            "full_name": "Test User"
        }
    )
    assert_response_error(response, 422)


def test_password_validation_no_digit(client):
    """Test password validation rejects passwords without digits"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "NoDigitsHere",
            "full_name": "Test User"
        }
    )
    assert_response_error(response, 422)


def test_password_validation_common_password(client):
    """Test password validation rejects common passwords"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123",
            "full_name": "Test User"
        }
    )
    assert_response_error(response, 422)


def test_email_validation_invalid_format(client):
    """Test email validation rejects invalid email formats"""
    invalid_emails = [
        "invalid",
        "invalid@",
        "@invalid.com",
        "invalid@com",
        "invalid..email@example.com"
    ]
    
    for invalid_email in invalid_emails:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": invalid_email,
                "password": "TestPass123",
                "full_name": "Test User"
            }
        )
        assert_response_error(response, 422)


def test_unauthorized_admin_access(client, user_token):
    """Test that non-admin users cannot access admin endpoints"""
    response = client.get(
        "/api/v1/users/users",
        headers=auth_headers(user_token)
    )
    assert_response_error(response, 403)


def test_unauthorized_item_creation(client, user_token):
    """Test that non-admin users cannot create items"""
    response = client.post(
        "/api/v1/items",
        json={
            "name": "Test Course",
            "category": "Programming",
            "price": 99.99,
            "skill_level": "Beginner",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Test description"
        },
        headers=auth_headers(user_token)
    )
    assert_response_error(response, 403)


def test_unauthorized_item_deletion(client, sample_items, user_token):
    """Test that non-admin users cannot delete items"""
    item_id = sample_items[0].id
    response = client.delete(
        f"/api/v1/items/{item_id}",
        headers=auth_headers(user_token)
    )
    assert_response_error(response, 403)


def test_path_traversal_attempt(client, admin_token):
    """Test path traversal attempt"""
    response = client.get(
        "/api/v1/items/../../../etc/passwd",
        headers=auth_headers(admin_token)
    )
    # Should return 404 or error, not file content
    assert response.status_code in [404, 400, 422]


def test_command_injection_attempt(client, admin_token):
    """Test command injection attempt"""
    malicious_input = "Python; rm -rf /"
    response = client.get(
        f"/api/v1/items?search={malicious_input}",
        headers=auth_headers(admin_token)
    )
    # Should not execute command
    assert response.status_code in [200, 401, 403]


def test_large_payload_dos(client, admin_token):
    """Test that large payloads are rejected"""
    large_description = "A" * 100000  # Very large payload
    response = client.post(
        "/api/v1/items",
        json={
            "name": "Test Course",
            "category": "Programming",
            "price": 99.99,
            "skill_level": "Beginner",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": large_description
        },
        headers=auth_headers(admin_token)
    )
    # Should reject large payload
    assert response.status_code in [413, 422, 400]


def test_security_headers_present(client):
    """Test that security headers are present"""
    response = client.get("/api/v1/health")
    
    # Check for security headers
    headers = response.headers
    assert "X-Frame-Options" in headers or "x-frame-options" in headers
    assert "X-Content-Type-Options" in headers or "x-content-type-options" in headers


def test_request_id_header_present(client):
    """Test that request ID header is present"""
    response = client.get("/api/v1/health")
    
    headers = response.headers
    assert "X-Request-ID" in headers or "x-request-id" in headers


def test_response_time_header_present(client):
    """Test that response time header is present"""
    response = client.get("/api/v1/health")
    
    headers = response.headers
    assert "X-Response-Time" in headers or "x-response-time" in headers
