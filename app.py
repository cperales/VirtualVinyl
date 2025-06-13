# app.py
"""AWS Lambda backend for VirtualVinyl without Flask."""
import base64
import json
import os
import secrets
from urllib.parse import urlencode
import requests

# Load environment variables from .env file
try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    print("dotenv module not found, ensure you have it installed if using .env files.")

# Spotify App Credentials (replace with your actual credentials)
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "https://cperales.github.io/VirtualVinyl/callback"

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

# In-memory session store for lambda usage
SESSION_STORE = {}


def _parse_cookies(header):
    """Parse cookie header into a dictionary."""
    cookies = {}
    if not header:
        return cookies
    for item in header.split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            cookies[k.strip()] = v
    return cookies


def _get_session(event):
    """Retrieve session dict based on session_id cookie."""
    headers = event.get("headers") or {}
    cookie_header = headers.get("cookie") or headers.get("Cookie")
    cookies = _parse_cookies(cookie_header)
    session_id = cookies.get("session_id")
    if session_id and session_id in SESSION_STORE:
        return session_id, SESSION_STORE[session_id]
    return None, None


def _create_response(body="", status=200, headers=None):
    """Create a standard lambda proxy response."""
    if headers is None:
        headers = {}
    if isinstance(body, (dict, list)):
        body = json.dumps(body)
        headers.setdefault("Content-Type", "application/json")
    return {"statusCode": status, "headers": headers, "body": body}


def get_auth_header(session):
    """Get authorization header for Spotify API calls."""
    if session and "access_token" in session:
        return {"Authorization": f"Bearer {session['access_token']}"}
    return None


def login(event):
    """Initiate Spotify OAuth flow."""
    state = secrets.token_urlsafe(16)
    session_id = secrets.token_urlsafe(16)
    SESSION_STORE[session_id] = {"state": state}

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "scope": (
            "user-read-private user-read-email playlist-modify-public "
            "playlist-modify-private user-library-read"
        ),
    }
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"
    headers = {
        "Location": auth_url,
        "Set-Cookie": f"session_id={session_id}; Path=/; HttpOnly",
    }
    return _create_response(status=302, headers=headers)


def callback(event):
    """Handle Spotify OAuth callback."""
    params = event.get("queryStringParameters") or {}
    code = params.get("code")
    state = params.get("state")

    session_id, session = _get_session(event)
    if not code or not session or state != session.get("state"):
        return _create_response({"error": "Invalid callback"}, 400)

    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_str.encode("ascii")).decode("ascii")

    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI}
    response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
    token_data = response.json()

    if "access_token" in token_data:
        session["access_token"] = token_data["access_token"]
        session["refresh_token"] = token_data.get("refresh_token")
        headers = {
            "Location": "http://localhost:3000?auth=success",
            "Set-Cookie": f"session_id={session_id}; Path=/; HttpOnly",
        }
        return _create_response(status=302, headers=headers)

    return _create_response({"error": "Failed to get access token"}, 400)


def get_user(event):
    """Get current user profile."""
    _, session = _get_session(event)
    headers = get_auth_header(session)
    if not headers:
        return _create_response({"error": "Not authenticated"}, 401)

    response = requests.get(f"{SPOTIFY_API_BASE_URL}/me", headers=headers)
    return _create_response(response.json())


def search_tracks(event):
    """Search for tracks."""
    _, session = _get_session(event)
    headers = get_auth_header(session)
    if not headers:
        return _create_response({"error": "Not authenticated"}, 401)

    query = (event.get("queryStringParameters") or {}).get("q", "")
    if not query:
        return _create_response({"error": "Query parameter required"}, 400)

    params = {"q": query, "type": "track", "limit": 20}
    response = requests.get(f"{SPOTIFY_API_BASE_URL}/search", headers=headers, params=params)
    return _create_response(response.json())


def create_playlist(event):
    """Create a new playlist and add tracks."""
    _, session = _get_session(event)
    headers = get_auth_header(session)
    if not headers:
        return _create_response({"error": "Not authenticated"}, 401)

    try:
        data = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        data = {}
    playlist_name = data.get("name", "El vinilo de hoy")
    track_uris = data.get("track_uris", [])
    if len(track_uris) < 8 or len(track_uris) > 12:
        return _create_response({"error": "Playlist must have 8-12 tracks"}, 400)

    user_resp = requests.get(f"{SPOTIFY_API_BASE_URL}/me", headers=headers)
    user_id = user_resp.json().get("id")

    playlist_data = {
        "name": playlist_name,
        "description": "Created with VirtualVinyl - A vinyl-inspired playlist",
        "public": False,
    }
    playlist_resp = requests.post(
        f"{SPOTIFY_API_BASE_URL}/users/{user_id}/playlists",
        headers={**headers, "Content-Type": "application/json"},
        json=playlist_data,
    )
    if playlist_resp.status_code != 201:
        return _create_response({"error": "Failed to create playlist"}, 400)

    playlist = playlist_resp.json()
    playlist_id = playlist["id"]
    tracks_data = {"uris": track_uris}
    tracks_resp = requests.post(
        f"{SPOTIFY_API_BASE_URL}/playlists/{playlist_id}/tracks",
        headers={**headers, "Content-Type": "application/json"},
        json=tracks_data,
    )
    if tracks_resp.status_code != 201:
        return _create_response({"error": "Failed to add tracks to playlist"}, 400)

    return _create_response(
        {
            "playlist_id": playlist_id,
            "playlist_url": playlist["external_urls"]["spotify"],
            "message": "Virtual vinyl created successfully!",
        }
    )


def auth_status(event):
    """Check if user is authenticated."""
    _, session = _get_session(event)
    return _create_response({"authenticated": bool(session and "access_token" in session)})


def logout(event):
    """Logout user."""
    session_id, session = _get_session(event)
    if session_id and session:
        SESSION_STORE.pop(session_id, None)
    headers = {"Set-Cookie": "session_id=; Path=/; Max-Age=0"}
    return _create_response({"message": "Logged out successfully"}, headers=headers)


def lambda_handler(event, context):
    """AWS Lambda entry point."""
    path = event.get("rawPath") or event.get("path")
    method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
    )
    routes = {
        ("/login", "GET"): login,
        ("/callback", "GET"): callback,
        ("/api/user", "GET"): get_user,
        ("/api/search", "GET"): search_tracks,
        ("/api/create-playlist", "POST"): create_playlist,
        ("/api/auth-status", "GET"): auth_status,
        ("/api/logout", "POST"): logout,
    }
    handler = routes.get((path, method))
    if handler:
        return handler(event)
    return _create_response({"error": "Not found"}, 404)

