import urllib.parse
from unittest.mock import Mock

import pytest
from streamlit_app.spotify_client import SpotifyClient
from streamlit_app.tidal_client import TidalClient
import streamlit_app.spotify_client as sc_module
import streamlit_app.tidal_client as tc_module


def test_spotify_oauth_url(monkeypatch):
    monkeypatch.setattr(sc_module, "SPOTIPY_CLIENT_ID", "cid")
    monkeypatch.setattr(sc_module, "SPOTIPY_CLIENT_SECRET", "secret")
    monkeypatch.setattr(sc_module, "REDIRECT_URI", "http://localhost/callback")
    client = SpotifyClient()
    url = client.login_url()
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    assert qs["client_id"] == ["cid"]
    assert qs["redirect_uri"] == ["http://localhost/callback"]


def test_tidal_oauth_url(monkeypatch):
    monkeypatch.setattr(tc_module, "TIDAL_CLIENT_ID", "tidal123")
    monkeypatch.setattr(tc_module, "TIDAL_REDIRECT_URI", "http://local/cb")
    client = TidalClient()
    url = client.login_url("abc")
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    assert parsed.netloc.endswith("login.tidal.com")
    assert qs["client_id"] == ["tidal123"]
    assert qs["redirect_uri"] == ["http://local/cb"]
    assert qs["state"] == ["abc"]


def test_spotify_missing_credentials(monkeypatch):
    monkeypatch.setattr(sc_module, "SPOTIPY_CLIENT_ID", "")
    monkeypatch.setattr(sc_module, "SPOTIPY_CLIENT_SECRET", "")
    monkeypatch.setattr(sc_module, "REDIRECT_URI", "")
    with pytest.raises(Exception):
        SpotifyClient()


def test_tidal_missing_credentials(monkeypatch):
    monkeypatch.setattr(tc_module, "TIDAL_CLIENT_ID", "")
    monkeypatch.setattr(tc_module, "TIDAL_REDIRECT_URI", "")
    client = TidalClient()
    assert isinstance(client.login_url("state"), str)
    assert not client.is_authenticated()
