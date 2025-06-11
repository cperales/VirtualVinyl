# app.py
from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
import requests
import base64
import secrets
import os
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
CORS(app, supports_credentials=True)

# Spotify App Credentials (replace with your actual credentials)
CLIENT_ID = 'your_spotify_client_id'
CLIENT_SECRET = 'your_spotify_client_secret'
REDIRECT_URI = 'http://localhost:5000/callback'

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE_URL = 'https://api.spotify.com/v1'

def get_auth_header():
    """Get authorization header for Spotify API calls"""
    if 'access_token' in session:
        return {'Authorization': f'Bearer {session["access_token"]}'}
    return None

@app.route('/login')
def login():
    """Initiate Spotify OAuth flow"""
    state = secrets.token_urlsafe(16)
    session['state'] = state
    
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': state,
        'scope': 'user-read-private user-read-email playlist-modify-public playlist-modify-private user-library-read'
    }
    
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle Spotify OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or state != session.get('state'):
        return jsonify({'error': 'Invalid callback'}), 400
    
    # Exchange code for access token
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_str.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
    token_data = response.json()
    
    if 'access_token' in token_data:
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data.get('refresh_token')
        return redirect('http://localhost:3000?auth=success')
    
    return jsonify({'error': 'Failed to get access token'}), 400

@app.route('/api/user')
def get_user():
    """Get current user profile"""
    headers = get_auth_header()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    response = requests.get(f"{SPOTIFY_API_BASE_URL}/me", headers=headers)
    return jsonify(response.json())

@app.route('/api/search')
def search_tracks():
    """Search for tracks"""
    headers = get_auth_header()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    params = {
        'q': query,
        'type': 'track',
        'limit': 20
    }
    
    response = requests.get(f"{SPOTIFY_API_BASE_URL}/search", headers=headers, params=params)
    return jsonify(response.json())

@app.route('/api/create-playlist', methods=['POST'])
def create_playlist():
    """Create a new playlist and add tracks"""
    headers = get_auth_header()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    playlist_name = data.get('name', 'My Virtual Vinyl')
    track_uris = data.get('track_uris', [])
    
    if len(track_uris) < 8 or len(track_uris) > 12:
        return jsonify({'error': 'Playlist must have 8-12 tracks'}), 400
    
    # Get user ID
    user_response = requests.get(f"{SPOTIFY_API_BASE_URL}/me", headers=headers)
    user_id = user_response.json().get('id')
    
    # Create playlist
    playlist_data = {
        'name': playlist_name,
        'description': 'Created with VirtualVinyl - A vinyl-inspired playlist',
        'public': False
    }
    
    playlist_response = requests.post(
        f"{SPOTIFY_API_BASE_URL}/users/{user_id}/playlists",
        headers={**headers, 'Content-Type': 'application/json'},
        json=playlist_data
    )
    
    if playlist_response.status_code != 201:
        return jsonify({'error': 'Failed to create playlist'}), 400
    
    playlist = playlist_response.json()
    playlist_id = playlist['id']
    
    # Add tracks to playlist
    tracks_data = {'uris': track_uris}
    tracks_response = requests.post(
        f"{SPOTIFY_API_BASE_URL}/playlists/{playlist_id}/tracks",
        headers={**headers, 'Content-Type': 'application/json'},
        json=tracks_data
    )
    
    if tracks_response.status_code != 201:
        return jsonify({'error': 'Failed to add tracks to playlist'}), 400
    
    return jsonify({
        'playlist_id': playlist_id,
        'playlist_url': playlist['external_urls']['spotify'],
        'message': 'Virtual vinyl created successfully!'
    })

@app.route('/api/auth-status')
def auth_status():
    """Check if user is authenticated"""
    return jsonify({'authenticated': 'access_token' in session})

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
