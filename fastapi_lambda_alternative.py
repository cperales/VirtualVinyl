# lambda_function.py - FastAPI version for AWS Lambda
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import logging

load_dotenv(dotenv_path='.env',
            verbose=True,
            override=True)

logging.basicConfig(level=logging.INFO)

app = FastAPI()

SPOTIFY_CLIENT_API = os.getenv('SPOTIFY_CLIENT_API')
logging.warning("SPOTIFY_CLIENT_API: %s", SPOTIFY_CLIENT_API)
SPOTIFY_SECRET_API = os.getenv('SPOTIFY_SECRET_API')
logging.warning("SPOTIFY_SECRET_API: %s", SPOTIFY_SECRET_API)
REDIRECT_URI = os.getenv('REDIRECT_URI')
logging.warning("REDIRECT_URI: %s", REDIRECT_URI)


# Spotify client setup (same as your original)
spotify_auth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_API,
    client_secret=SPOTIFY_SECRET_API,
    redirect_uri=REDIRECT_URI,
    scope='user-read-private user-read-email user-top-read playlist-modify-public playlist-modify-private',
    open_browser=False,
)

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Virtual Vinyl</title>
        <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .track { padding: 10px; border: 1px solid #ddd; margin: 5px 0; display: flex; justify-content: space-between; }
            .selected { background-color: #e8f5e8; }
            button { padding: 8px 16px; margin: 5px; }
        </style>
    </head>
    <body>
        <h1>Virtual Vinyl</h1>
        <button onclick="spotifyLogin()">Login with Spotify</button>
        <div id="user-info"></div>
        <input type="text" id="search" placeholder="Search tracks" onkeyup="searchTracks()">
        <div id="tracks"></div>
        <div id="selected-count"></div>
        <input type="text" id="playlist-name" placeholder="Playlist name">
        <button onclick="createPlaylist()">Create Playlist</button>
        
        <script>
            let selectedTracks = [];
            let accessToken = localStorage.getItem('spotify_token');
            
            function spotifyLogin() {
                window.location = '/auth/spotify';
            }
            
            async function searchTracks() {
                const query = document.getElementById('search').value;
                if (!query || !accessToken) return;
                
                try {
                    const response = await axios.get(`/api/search?q=${query}`, {
                        headers: { 'Authorization': `Bearer ${accessToken}` }
                    });
                    displayTracks(response.data.tracks);
                } catch (error) {
                    console.error('Search failed:', error);
                }
            }
            
            function displayTracks(tracks) {
                const container = document.getElementById('tracks');
                container.innerHTML = tracks.map(track => `
                    <div class="track ${selectedTracks.find(t => t.id === track.id) ? 'selected' : ''}">
                        <span>${track.name} - ${track.artists.map(a => a.name).join(', ')}</span>
                        <button onclick="toggleTrack('${track.id}', '${track.uri}', '${track.name}')">
                            ${selectedTracks.find(t => t.id === track.id) ? 'Remove' : 'Add'}
                        </button>
                    </div>
                `).join('');
            }
            
            function toggleTrack(id, uri, name) {
                const index = selectedTracks.findIndex(t => t.id === id);
                if (index >= 0) {
                    selectedTracks.splice(index, 1);
                } else if (selectedTracks.length < 10) {
                    selectedTracks.push({ id, uri, name });
                }
                document.getElementById('selected-count').textContent = `Selected: ${selectedTracks.length} tracks`;
                searchTracks(); // Refresh display
            }
            
            async function createPlaylist() {
                const name = document.getElementById('playlist-name').value;
                if (!name || selectedTracks.length === 0) return;
                
                try {
                    const response = await axios.post('/api/playlist', {
                        name,
                        track_uris: selectedTracks.map(t => t.uri)
                    }, {
                        headers: { 'Authorization': `Bearer ${accessToken}` }
                    });
                    alert(`Playlist created: ${response.data.name}`);
                    selectedTracks = [];
                    document.getElementById('selected-count').textContent = '';
                } catch (error) {
                    console.error('Playlist creation failed:', error);
                }
            }
            
            // Check for auth callback
            const urlParams = new URLSearchParams(window.location.search);
            const code = urlParams.get('code');
            if (code) {
                axios.post('/auth/callback', { code })
                    .then(response => {
                        accessToken = response.data.access_token;
                        localStorage.setItem('spotify_token', accessToken);
                        window.location = '/';
                    });
            }
        </script>
    </body>
    </html>
    """

@app.get("/auth/spotify")
async def spotify_login():
    auth_url = spotify_auth.get_authorize_url()
    return {"auth_url": auth_url}

@app.post("/auth/callback")
async def spotify_callback(request: Request):
    data = await request.json()
    code = data.get("code")
    token_info = spotify_auth.get_access_token(code)
    return {"access_token": token_info["access_token"]}

@app.get("/api/search")
async def search_tracks(q: str, request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return JSONResponse({"error": "No auth"}, 401)
    
    token = auth_header.split(" ")[1]
    sp = spotipy.Spotify(auth=token)
    results = sp.search(q=q, type='track', limit=20)
    return {"tracks": results['tracks']['items']}

@app.post("/api/playlist")
async def create_playlist(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return JSONResponse({"error": "No auth"}, 401)
    
    token = auth_header.split(" ")[1]
    sp = spotipy.Spotify(auth=token)
    data = await request.json()
    
    user = sp.current_user()
    playlist = sp.user_playlist_create(user['id'], data['name'])
    if data.get('track_uris'):
        sp.playlist_add_items(playlist['id'], data['track_uris'])
    
    return playlist

# Lambda handler
handler = Mangum(app)