import json
import app


def invoke_lambda(path, method="GET", query=None, body=None, cookies=None):
    headers = {}
    if cookies:
        headers["cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())
    event = {
        "rawPath": path,
        "requestContext": {"http": {"method": method}},
        "headers": headers,
    }
    if query:
        event["queryStringParameters"] = query
    if body is not None:
        event["body"] = json.dumps(body)
    return app.lambda_handler(event, None)


def test_get_auth_header_without_token():
    assert app.get_auth_header({}) is None


def test_get_auth_header_with_token():
    assert app.get_auth_header({"access_token": "abc123"}) == {
        "Authorization": "Bearer abc123"
    }


def test_login_sets_state_and_redirects():
    response = invoke_lambda("/login")
    assert response["statusCode"] == 302
    assert "accounts.spotify.com/authorize" in response["headers"]["Location"]
    cookie = response["headers"]["Set-Cookie"]
    session_id = cookie.split("=", 1)[1].split(";", 1)[0]
    assert session_id in app.SESSION_STORE
    assert "state" in app.SESSION_STORE[session_id]


def test_search_requires_auth():
    response = invoke_lambda("/api/search", query={"q": "test"})
    assert response["statusCode"] == 401
    assert json.loads(response["body"]) == {"error": "Not authenticated"}


def test_search_requires_query():
    session_id = "s1"
    app.SESSION_STORE[session_id] = {"access_token": "token"}
    response = invoke_lambda("/api/search", cookies={"session_id": session_id})
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Query parameter required"}


def test_create_playlist_invalid_track_count():
    session_id = "s2"
    app.SESSION_STORE[session_id] = {"access_token": "token"}
    response = invoke_lambda(
        "/api/create-playlist",
        method="POST",
        body={"track_uris": ["a", "b"]},
        cookies={"session_id": session_id},
    )
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Playlist must have 8-12 tracks"}


def test_auth_status():
    response = invoke_lambda("/api/auth-status")
    assert json.loads(response["body"]) == {"authenticated": False}
    session_id = "s3"
    app.SESSION_STORE[session_id] = {"access_token": "token"}
    response = invoke_lambda("/api/auth-status", cookies={"session_id": session_id})
    assert json.loads(response["body"]) == {"authenticated": True}


def test_logout_clears_session():
    session_id = "s4"
    app.SESSION_STORE[session_id] = {"access_token": "token"}
    response = invoke_lambda("/api/logout", method="POST", cookies={"session_id": session_id})
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["message"] == "Logged out successfully"
    assert session_id not in app.SESSION_STORE

