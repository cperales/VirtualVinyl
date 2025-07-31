from unittest.mock import Mock

from streamlit_app.spotify_client import SpotifyClient
import streamlit_app.spotify_client as sc_module


def test_create_playlist(monkeypatch):
    monkeypatch.setattr(sc_module, "SPOTIPY_CLIENT_ID", "cid")
    monkeypatch.setattr(sc_module, "SPOTIPY_CLIENT_SECRET", "secret")
    monkeypatch.setattr(sc_module, "REDIRECT_URI", "http://localhost/callback")
    client = SpotifyClient()
    mock_sp = Mock()
    mock_sp.current_user.return_value = {"id": "u1"}
    mock_sp.user_playlist_create.return_value = {"id": "p1", "name": "name"}
    client.client = mock_sp
    playlist = client.create_playlist("name", ["uri1", "uri2"])
    mock_sp.user_playlist_create.assert_called_with("u1", "name")
    mock_sp.playlist_add_items.assert_called_with("p1", ["uri1", "uri2"])
    assert playlist["name"] == "name"
