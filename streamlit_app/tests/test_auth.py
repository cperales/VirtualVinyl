import importlib
import urllib.parse
import sys
from unittest.mock import Mock

import pytest


def reload_module(module_name):
    if module_name in sys.modules:
        return importlib.reload(sys.modules[module_name])
    return importlib.import_module(module_name)


def test_spotify_oauth_url(monkeypatch):
    monkeypatch.setenv("SPOTIFY_CLIENT_API", "cid")
    monkeypatch.setenv("SPOTIFY_SECRET_API", "secret")
    monkeypatch.setenv("REDIRECT_URI", "http://localhost/callback")
    sc = reload_module("streamlit_app.spotify_client")
    client = sc.SpotifyClient()
    url = client.login_url()
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    assert qs["client_id"] == ["cid"]
    assert qs["redirect_uri"] == ["http://localhost/callback"]


def test_tidal_oauth_url(monkeypatch):
    monkeypatch.setenv("TIDAL_CLIENT_ID", "tidal123")
    monkeypatch.setenv("TIDAL_REDIRECT_URI", "http://local/cb")
    tc = reload_module("streamlit_app.tidal_client")
    client = tc.TidalClient()
    url = client.login_url("abc")
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    assert parsed.netloc.endswith("login.tidal.com")
    assert qs["client_id"] == ["tidal123"]
    assert qs["redirect_uri"] == ["http://local/cb"]
    assert qs["state"] == ["abc"]


def test_spotify_missing_credentials(monkeypatch):
    monkeypatch.delenv("SPOTIFY_CLIENT_API", raising=False)
    monkeypatch.delenv("SPOTIFY_SECRET_API", raising=False)
    monkeypatch.delenv("REDIRECT_URI", raising=False)
    sc = reload_module("streamlit_app.spotify_client")
    with pytest.raises(Exception):
        sc.SpotifyClient()


def test_tidal_missing_credentials(monkeypatch):
    monkeypatch.delenv("TIDAL_CLIENT_ID", raising=False)
    monkeypatch.delenv("TIDAL_REDIRECT_URI", raising=False)
    tc = reload_module("streamlit_app.tidal_client")
    client = tc.TidalClient()
    assert isinstance(client.login_url("state"), str)
    assert not client.is_authenticated()
