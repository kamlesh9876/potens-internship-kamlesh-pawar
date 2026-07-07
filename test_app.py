from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_db
import sqlite3

client = TestClient(app)


def setup_function():
    init_db()
    conn = sqlite3.connect('data/app.db')
    conn.execute('DELETE FROM items')
    conn.execute('DROP TABLE IF EXISTS sqlite_sequence')
    conn.executemany(
        'INSERT INTO items (name, category, price, skill_level, goal, location, pace, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        [
            ('LaunchPad Bootcamp', 'course', 120.0, 'beginner', 'career-switch', 'remote', 'steady', 'Structured beginner course'),
            ('Career Pivot Accelerator', 'bootcamp', 180.0, 'beginner', 'career-switch', 'remote', 'steady', 'Career switch bootcamp with coaching'),
            ('Data Storytelling Clinic', 'workshop', 110.0, 'beginner', 'career-switch', 'remote', 'steady', 'Learn to communicate insights clearly'),
            ('Data Sprint', 'bootcamp', 250.0, 'intermediate', 'career-switch', 'hybrid', 'fast', 'Hands-on data bootcamp'),
            ('AI Foundations', 'course', 180.0, 'beginner', 'build-ai', 'remote', 'steady', 'Accessible AI course'),
            ('Design Systems Lab', 'workshop', 90.0, 'beginner', 'portfolio', 'onsite', 'steady', 'Portfolio design workshop'),
            ('Product Strategy Studio', 'mentoring', 300.0, 'advanced', 'leadership', 'remote', 'steady', 'Leadership coaching'),
        ],
    )
    conn.commit()
    conn.close()


def test_recommend_returns_top_three_for_valid_profile():
    response = client.post('/recommend', json={
        'age': 28,
        'budget': 200,
        'experience_level': 'beginner',
        'goal': 'career-switch',
        'location': 'remote',
        'preferred_pace': 'steady'
    })
    assert response.status_code == 200
    body = response.json()
    assert len(body['recommendations']) == 3
    assert body['recommendations'][0]['name'] == 'LaunchPad Bootcamp'


def test_recommend_handles_missing_preferred_pace():
    response = client.post('/recommend', json={
        'age': 24,
        'budget': 150,
        'experience_level': 'beginner',
        'goal': 'build-ai',
        'location': 'remote'
    })
    assert response.status_code == 200
    assert len(response.json()['recommendations']) >= 1


def test_recommend_returns_empty_when_no_match_exists():
    response = client.post('/recommend', json={
        'age': 60,
        'budget': 20,
        'experience_level': 'beginner',
        'goal': 'leadership',
        'location': 'onsite',
        'preferred_pace': 'fast'
    })
    assert response.status_code == 200
    assert response.json()['recommendations'] == []


def test_admin_items_crud_requires_token():
    response = client.get('/items')
    assert response.status_code == 401


def test_explain_returns_plain_language_logic():
    response = client.get('/explain/1')
    assert response.status_code == 200
    assert 'goal' in response.json()['explanation']


def test_items_endpoint_supports_pagination_and_filters():
    response = client.get(
        '/items',
        params={'page': 1, 'limit': 2, 'goal': 'career-switch', 'location': 'remote'},
        headers={'x-admin-token': 'secret-token'}
    )
    assert response.status_code == 200
    body = response.json()
    assert body['page'] == 1
    assert body['limit'] == 2
    assert body['total'] == 3
    assert len(body['items']) == 2
    assert body['items'][0]['goal'] == 'career-switch'
    assert body['items'][0]['location'] == 'remote'


def test_health_endpoints_are_available():
    health = client.get('/health')
    assert health.status_code == 200
    assert health.json()['success'] is True

    application = client.get('/health/application')
    assert application.status_code == 200

    database = client.get('/health/db')
    assert database.status_code == 200
