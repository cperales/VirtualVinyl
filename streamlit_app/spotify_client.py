import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import logging

load_dotenv(dotenv_path='.env',
            verbose=True,
            override=False)

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
    logging.warning("Spotify credentials are not fully set")

class SpotifyClient:
    """Minimal wrapper around spotipy for Virtual Vinyl."""

    def __init__(self):
        if not all([SPOTIFY_CLIENT_API, SPOTIFY_SECRET_API, REDIRECT_URI]):
            raise Exception("Missing Spotify credentials")
        self.client = None
        self.auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_API,
            client_secret=SPOTIFY_SECRET_API,
            redirect_uri=REDIRECT_URI,
            scope=(
                'user-read-private user-read-email user-top-read '
                'playlist-modify-public playlist-modify-private'
            ),
            open_browser=False,
        )

    def login_url(self):
        return self.auth_manager.get_authorize_url()

    def handle_callback(self, code):
        token_info = self.auth_manager.get_access_token(code)
        self.client = spotipy.Spotify(auth=token_info['access_token'])

    def is_authenticated(self):
        return self.client is not None

    def current_user(self):
        if not self.client:
            return None
        return self.client.current_user()

    def top_tracks(self, limit=50):
        if not self.client:
            return []
        results = self.client.current_user_top_tracks(limit=limit)
        return results.get('items', [])

    def search_tracks(self, query, limit=50):
        if not self.client or not query:
            return []
        results = self.client.search(q=query, type='track', limit=limit)
        return results['tracks']['items']

    def create_playlist(self, name, track_uris):
        if not self.client:
            return None
        user = self.client.current_user()
        playlist = self.client.user_playlist_create(user['id'], name)
        if track_uris:
            self.client.playlist_add_items(playlist['id'], track_uris)
        return playlist

    def play_track(self, uri):
        if not self.client:
            return
        try:
            self.client.start_playback(uris=[uri])
        except spotipy.SpotifyException:
            pass

    def pause(self):
        if self.client:
            try:
                self.client.pause_playback()
            except spotipy.SpotifyException:
                pass
