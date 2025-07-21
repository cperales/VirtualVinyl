import os
import requests


class TidalClient:
    """Minimal TIDAL API wrapper."""

    AUTH_URL = "https://auth.tidal.com/v1/oauth2/token"
    API_URL = "https://api.tidal.com/v1"

    def __init__(self):
        self.access_token = None
        self.client_id = os.getenv("TIDAL_CLIENT_ID")
        self.redirect_uri = os.getenv("TIDAL_REDIRECT_URI")

    def login_url(self, state):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": "r_usr w_usr r_sub w_sub",
        }
        query = "&".join(
            f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()
        )
        return f"https://login.tidal.com/authorize?{query}"

    def handle_callback(self, code):
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        resp = requests.post(self.AUTH_URL, data=data)
        if resp.ok:
            payload = resp.json()
            self.access_token = payload.get("access_token")

    def is_authenticated(self):
        return self.access_token is not None

    def search_tracks(self, query):
        if not self.access_token or not query:
            return []
        resp = requests.get(
            f"{self.API_URL}/search/tracks",
            params={"query": query, "limit": 50},
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        if resp.ok:
            data = resp.json()
            return data.get("items", [])
        return []

    def create_playlist(self, user_id, name, track_ids):
        if not self.access_token:
            return None
        resp = requests.post(
            f"{self.API_URL}/users/{user_id}/playlists",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            json={
                "title": name,
                "description": "Created with Virtual Vinyl",
                "visibility": "PRIVATE",
            },
        )
        if not resp.ok:
            return None
        playlist = resp.json()
        if track_ids:
            requests.post(
                f"{self.API_URL}/playlists/{playlist['uuid']}/items",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                json={"trackIds": track_ids, "onDupes": "SKIP"},
            )
        return playlist
