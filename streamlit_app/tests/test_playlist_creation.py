import importlib
import sys
from unittest.mock import Mock


def reload_module(module_name):
    if module_name in sys.modules:
        return importlib.reload(sys.modules[module_name])
    return importlib.import_module(module_name)


def test_create_playlist(monkeypatch):
    monkeypatch.setenv("SPOTIFY_CLIENT_API", "cid")
    monkeypatch.setenv("SPOTIFY_SECRET_API", "secret")
    monkeypatch.setenv("REDIRECT_URI", "http://localhost/callback")
    sc = reload_module("streamlit_app.spotify_client")
    client = sc.SpotifyClient()
    mock_sp = Mock()
    mock_sp.current_user.return_value = {"id": "u1"}
    mock_sp.user_playlist_create.return_value = {"id": "p1", "name": "name"}
    client.client = mock_sp
    playlist = client.create_playlist("name", ["uri1", "uri2"])
    mock_sp.user_playlist_create.assert_called_with("u1", "name")
    mock_sp.playlist_add_items.assert_called_with("p1", ["uri1", "uri2"])
    assert playlist["name"] == "name"
