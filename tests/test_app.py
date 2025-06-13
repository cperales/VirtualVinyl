import pytest
from flask import session

import app


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


def test_get_auth_header_without_token():
    with app.app.test_request_context('/'):
        assert app.get_auth_header() is None


def test_get_auth_header_with_token():
    with app.app.test_request_context('/'):
        session['access_token'] = 'abc123'
        assert app.get_auth_header() == {'Authorization': 'Bearer abc123'}


def test_login_sets_state_and_redirects(client):
    response = client.get('/login')
    assert response.status_code == 302
    assert 'accounts.spotify.com/authorize' in response.location
    with client.session_transaction() as sess:
        assert 'state' in sess


def test_search_requires_auth(client):
    response = client.get('/api/search?q=test')
    assert response.status_code == 401
    assert response.get_json() == {'error': 'Not authenticated'}


def test_search_requires_query(client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'token'
    response = client.get('/api/search')
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Query parameter required'}


def test_create_playlist_invalid_track_count(client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'token'
    response = client.post(
        '/api/create-playlist',
        json={'track_uris': ['a', 'b']},
    )
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Playlist must have 8-12 tracks'}


def test_auth_status(client):
    response = client.get('/api/auth-status')
    assert response.get_json() == {'authenticated': False}
    with client.session_transaction() as sess:
        sess['access_token'] = 'token'
    response = client.get('/api/auth-status')
    assert response.get_json() == {'authenticated': True}


def test_logout_clears_session(client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'token'
    response = client.post('/api/logout')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Logged out successfully'
    with client.session_transaction() as sess:
        assert 'access_token' not in sess
