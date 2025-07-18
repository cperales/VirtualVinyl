import os
import streamlit as st
from playlist import PlaylistManager
from spotify_client import SpotifyClient
from tidal_client import TidalClient

st.set_page_config(page_title="Virtual Vinyl")

if "spotify" not in st.session_state:
    st.session_state.spotify = SpotifyClient()
if "tidal" not in st.session_state:
    st.session_state.tidal = TidalClient()
if "playlist" not in st.session_state:
    st.session_state.playlist = PlaylistManager()

sp = st.session_state.spotify
td = st.session_state.tidal
pl = st.session_state.playlist

st.title("Virtual Vinyl")

# Authentication buttons
col1, col2 = st.columns(2)
with col1:
    if not sp.is_authenticated():
        if st.button("Login with Spotify"):
            auth_url = sp.login_url()
            st.write("[Open login]({})".format(auth_url))
    else:
        user = sp.current_user()
        st.write(f"Logged in as {user['display_name']}")

with col2:
    if not td.is_authenticated():
        if st.button("Login with TIDAL"):
            auth_url = td.login_url("state123")
            st.write("[Open login]({})".format(auth_url))
    else:
        st.write("TIDAL authenticated")

# Handle code from URL params
code = st.query_params.get("code")
if code and not sp.is_authenticated():
    sp.handle_callback(code[0])
if code and not td.is_authenticated():
    td.handle_callback(code[0])

if sp.is_authenticated():
    if "tracks" not in st.session_state:
        st.session_state.tracks = sp.top_tracks()
    search = st.text_input("Search tracks")
    if search:
        tracks = sp.search_tracks(search)
    else:
        tracks = st.session_state.tracks

    for t in tracks:
        cols = st.columns([4,1])
        cols[0].write(f"{t['name']} - {', '.join(a['name'] for a in t['artists'])}")
        if st.button("Select", key=t['id']):
            pl.toggle_track({"id": t['id'], "uri": t['uri']})

    st.write(f"Selected {len(pl.selected_tracks)} tracks")
    playlist_name = st.text_input("Playlist name")
    if st.button("Create Spotify Playlist") and playlist_name:
        track_uris = [t['uri'] for t in pl.selected_tracks]
        playlist = sp.create_playlist(playlist_name, track_uris)
        if playlist:
            st.success(f"Created playlist {playlist['name']}")
            st.write(playlist.get('external_urls', {}).get('spotify'))
            pl.selected_tracks = []


