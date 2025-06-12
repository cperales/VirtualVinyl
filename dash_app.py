# dash_app.py
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import requests
import json
from datetime import datetime

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Backend API URL
API_BASE = 'http://localhost:5000'

# Custom CSS styles
custom_styles = {
    'body': {
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'min-height': '100vh',
        'font-family': 'Inter, sans-serif'
    },
    'card': {
        'background': 'rgba(255, 255, 255, 0.1)',
        'backdrop-filter': 'blur(10px)',
        'border': '1px solid rgba(255, 255, 255, 0.2)',
        'border-radius': '20px',
        'box-shadow': '0 8px 32px rgba(0, 0, 0, 0.1)'
    },
    'vinyl-logo': {
        'width': '80px',
        'height': '80px',
        'border-radius': '50%',
        'background': 'conic-gradient(from 0deg, #1a1a1a, #333, #1a1a1a, #333, #1a1a1a)',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'center',
        'position': 'relative',
        'box-shadow': '0 4px 20px rgba(0, 0, 0, 0.3)'
    },
    'vinyl-center': {
        'width': '20px',
        'height': '20px',
        'border-radius': '50%',
        'background': '#ff6b6b',
        'position': 'absolute'
    }
}

def create_vinyl_logo():
    """Create a vinyl record-inspired logo"""
    return html.Div([
        html.Div(
            html.Div(style=custom_styles['vinyl-center']),
            style=custom_styles['vinyl-logo']
        )
    ])

def create_header():
    """Create the app header"""
    return dbc.Navbar([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        create_vinyl_logo(),
                        html.H2("VirtualVinyl", className="ms-3 mb-0 text-white fw-bold")
                    ], style={'display': 'flex', 'align-items': 'center'})
                ], width="auto"),
                dbc.Col([
                    html.Div(id="user-info", className="text-white")
                ], width="auto"),
                dbc.Col([
                    dbc.Button("Logout", id="logout-btn", color="danger", size="sm", className="ms-2")
                ], width="auto", className="ms-auto")
            ], align="center", className="w-100")
        ], fluid=True)
    ], 
    color="dark", 
    dark=True, 
    style={'background': 'rgba(0, 0, 0, 0.2)', 'backdrop-filter': 'blur(10px)'}
    )

def create_login_page():
    """Create the login page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            create_vinyl_logo(),
                            html.H1("VirtualVinyl", className="text-white fw-bold mt-3 mb-2"),
                            html.P("Create vinyl-style playlists from your favorite tracks", 
                                 className="text-light mb-4"),
                            dbc.Button(
                                "Connect with Spotify", 
                                id="login-btn", 
                                color="success", 
                                size="lg",
                                className="rounded-pill px-4"
                            )
                        ], className="text-center")
                    ])
                ], style=custom_styles['card'])
            ], width=6, lg=4, className="mx-auto")
        ], justify="center", className="min-vh-100 align-items-center")
    ], fluid=True, className="bg-gradient")

def create_main_app():
    """Create the main application interface"""
    return html.Div([
        create_header(),
        dbc.Container([
            dbc.Row([
                # Search Section
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("🔍 Search Tracks", className="text-white mb-0")
                        ], style={'background': 'transparent', 'border': 'none'}),
                        dbc.CardBody([
                            dbc.InputGroup([
                                dbc.Input(
                                    id="search-input",
                                    placeholder="Search for songs, artists, albums...",
                                    style={'background': 'rgba(255, 255, 255, 0.1)', 'border': 'none', 'color': 'white'}
                                ),
                                dbc.Button("Search", id="search-btn", color="success")
                            ], className="mb-3"),
                            dcc.Loading(
                                id="loading-search",
                                children=[html.Div(id="search-results")],
                                type="default"
                            )
                        ])
                    ], style=custom_styles['card'])
                ], width=12, lg=6, className="mb-4"),
                
                # Vinyl Creation Section
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("🎵 Your Virtual Vinyl", className="text-white mb-0"),
                            html.Small(id="track-counter", className="text-light")
                        ], style={'background': 'transparent', 'border': 'none'}),
                        dbc.CardBody([
                            dbc.Input(
                                id="playlist-name",
                                placeholder="Enter playlist name...",
                                className="mb-3",
                                style={'background': 'rgba(255, 255, 255, 0.1)', 'border': 'none', 'color': 'white'}
                            ),
                            html.Div(id="vinyl-tracks", className="mb-3"),
                            dbc.Button(
                                "🎼 Create Virtual Vinyl",
                                id="create-playlist-btn",
                                color="primary",
                                disabled=True,
                                className="w-100 rounded-pill",
                                size="lg"
                            )
                        ])
                    ], style=custom_styles['card'])
                ], width=12, lg=6, className="mb-4")
            ])
        ], fluid=True, className="py-4"),
        
        # Hidden divs for storing data
        html.Div(id="auth-status", style={'display': 'none'}),
        html.Div(id="vinyl-data", style={'display': 'none'}, children='[]'),
        
        # Toast for notifications
        dbc.Toast(
            id="notification-toast",
            header="Notification",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350}
        )
    ])

# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Interval(id='auth-check-interval', interval=2000, n_intervals=0, max_intervals=1)
])

# Callbacks
@app.callback(
    Output('page-content', 'children'),
    Output('auth-status', 'children'),
    Input('url', 'pathname'),
    Input('auth-check-interval', 'n_intervals')
)
def display_page(pathname, n_intervals):
    """Display appropriate page based on authentication status"""
    try:
        response = requests.get(f'{API_BASE}/api/auth-status', timeout=5)
        auth_data = response.json()
        is_authenticated = auth_data.get('authenticated', False)
        
        if is_authenticated:
            return create_main_app(), 'authenticated'
        else:
            return create_login_page(), 'not_authenticated'
    except:
        return create_login_page(), 'not_authenticated'

@app.callback(
    Output('url', 'href'),
    Input('login-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_login(n_clicks):
    """Handle login button click"""
    if n_clicks:
        return f'{API_BASE}/login'
    return ''

@app.callback(
    Output('user-info', 'children'),
    Input('auth-status', 'children'),
    prevent_initial_call=True
)
def update_user_info(auth_status):
    """Update user information in header"""
    if auth_status == 'authenticated':
        try:
            response = requests.get(f'{API_BASE}/api/user')
            if response.status_code == 200:
                user_data = response.json()
                return f"Welcome, {user_data.get('display_name', 'User')}!"
        except:
            pass
    return ""

@app.callback(
    Output('search-results', 'children'),
    Input('search-btn', 'n_clicks'),
    State('search-input', 'value'),
    prevent_initial_call=True
)
def search_tracks(n_clicks, search_query):
    """Handle track search"""
    if not n_clicks or not search_query:
        return html.Div("Enter a search term and click Search", className="text-light text-center py-4")
    
    try:
        response = requests.get(f'{API_BASE}/api/search', params={'q': search_query})
        if response.status_code == 200:
            data = response.json()
            tracks = data.get('tracks', {}).get('items', [])
            
            if not tracks:
                return html.Div("No tracks found", className="text-light text-center py-4")
            
            search_results = []
            for track in tracks[:10]:  # Limit to 10 results
                artists = ', '.join([artist['name'] for artist in track['artists']])
                duration_ms = track['duration_ms']
                duration = f"{duration_ms // 60000}:{(duration_ms % 60000) // 1000:02d}"
                
                album_image = None
                if track['album']['images']:
                    album_image = track['album']['images'][-1]['url']  # Smallest image
                
                search_results.append(
                    dbc.Card([
                        dbc.Row([
                            dbc.Col([
                                html.Img(src=album_image, style={'width': '50px', 'height': '50px', 'border-radius': '8px'}) if album_image else html.Div()
                            ], width="auto"),
                            dbc.Col([
                                html.H6(track['name'], className="text-white mb-1"),
                                html.Small(f"{artists} • {duration}", className="text-light")
                            ]),
                            dbc.Col([
                                dbc.Button(
                                    "Add",
                                    id={'type': 'add-track-btn', 'index': track['id']},
                                    color="primary",
                                    size="sm"
                                )
                            ], width="auto")
                        ], align="center", className="g-2")
                    ], 
                    body=True, 
                    className="mb-2",
                    style={
                        'background': 'rgba(255, 255, 255, 0.05)',
                        'border': '1px solid rgba(255, 255, 255, 0.1)'
                    }
                )
            )
            
            return html.Div(search_results, style={'max-height': '400px', 'overflow-y': 'auto'})
        
        return html.Div("Search failed", className="text-danger text-center py-4")
    except Exception as e:
        return html.Div("Search error", className="text-danger text-center py-4")

@app.callback(
    Output('vinyl-data', 'children'),
    Output('vinyl-tracks', 'children'),
    Output('track-counter', 'children'),
    Output('create-playlist-btn', 'disabled'),
    Input({'type': 'add-track-btn', 'index': dash.dependencies.ALL}, 'n_clicks'),
    Input({'type': 'remove-track-btn', 'index': dash.dependencies.ALL}, 'n_clicks'),
    State('vinyl-data', 'children'),
    prevent_initial_call=True
)
def manage_vinyl_tracks(add_clicks, remove_clicks, vinyl_data):
    """Manage tracks in the virtual vinyl"""
    ctx = callback_context
    if not ctx.triggered:
        return vinyl_data, [], "(0/12)", True
    
    # Parse current vinyl data
    try:
        current_tracks = json.loads(vinyl_data) if vinyl_data else []
    except:
        current_tracks = []
    
    # Handle add/remove actions
    triggered_id = ctx.triggered[0]['prop_id']
    
    if 'add-track-btn' in triggered_id and ctx.triggered[0]['value']:
        # Extract track ID from triggered component
        track_id = eval(triggered_id.split('.')[0])['index']
        
        # Check if track already exists
        if not any(track['id'] == track_id for track in current_tracks):
            if len(current_tracks) < 12:
                # In a real app, you'd fetch track details from your search results
                # For now, we'll add a placeholder
                new_track = {
                    'id': track_id,
                    'name': f'Track {track_id[:8]}...',
                    'artists': [{'name': 'Artist'}],
                    'uri': f'spotify:track:{track_id}'
                }
                current_tracks.append(new_track)
    
    elif 'remove-track-btn' in triggered_id and ctx.triggered[0]['value']:
        track_id = eval(triggered_id.split('.')[0])['index']
        current_tracks = [track for track in current_tracks if track['id'] != track_id]
    
    # Create vinyl tracks display
    vinyl_tracks_display = []
    for i, track in enumerate(current_tracks):
        artists = ', '.join([artist['name'] for artist in track['artists']])
        vinyl_tracks_display.append(
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Span(f"{i+1:02d}", className="text-light me-2", style={'font-family': 'monospace'})
                    ], width="auto"),
                    dbc.Col([
                        html.H6(track['name'], className="text-white mb-0"),
                        html.Small(artists, className="text-light")
                    ]),
                    dbc.Col([
                        dbc.Button(
                            "×",
                            id={'type': 'remove-track-btn', 'index': track['id']},
                            color="danger",
                            size="sm",
                            style={'border-radius': '50%', 'width': '30px', 'height': '30px', 'padding': '0'}
                        )
                    ], width="auto")
                ], align="center", className="g-2")
            ],
            body=True,
            className="mb-2",
            style={
                'background': 'rgba(255, 255, 255, 0.05)',
                'border': '1px solid rgba(255, 255, 255, 0.1)'
            }
            )
        )
    
    if not vinyl_tracks_display:
        vinyl_tracks_display = [
            html.Div([
                html.Div("🎵", style={'font-size': '3rem', 'margin-bottom': '1rem'}),
                html.P("Start building your vinyl by searching and adding tracks", className="text-light"),
                html.Small("Minimum 8 tracks, maximum 12 tracks", className="text-muted")
            ], className="text-center py-4")
        ]
    
    # Update counter and button state
    track_count = len(current_tracks)
    counter_text = f"({track_count}/12)"
    button_disabled = track_count < 8
    
    return json.dumps(current_tracks), vinyl_tracks_display, counter_text, button_disabled

@app.callback(
    Output('notification-toast', 'is_open'),
    Output('notification-toast', 'children'),
    Output('notification-toast', 'header'),
    Input('create-playlist-btn', 'n_clicks'),
    State('playlist-name', 'value'),
    State('vinyl-data', 'children'),
    prevent_initial_call=True
)
def create_playlist(n_clicks, playlist_name, vinyl_data):
    """Create playlist on Spotify"""
    if not n_clicks:
        return False, "", ""
    
    if not playlist_name or not playlist_name.strip():
        return True, "Please enter a playlist name!", "Error"
    
    try:
        tracks = json.loads(vinyl_data) if vinyl_data else []
        if len(tracks) < 8:
            return True, "You need at least 8 tracks to create a vinyl!", "Error"
        
        # Create playlist via API
        track_uris = [track['uri'] for track in tracks]
        response = requests.post(f'{API_BASE}/api/create-playlist', json={
            'name': playlist_name.strip(),
            'track_uris': track_uris
        })
        
        if response.status_code == 200:
            return True, "Virtual Vinyl created successfully! Check your Spotify playlists.", "Success"
        else:
            return True, "Failed to create playlist. Please try again.", "Error"
            
    except Exception as e:
        return True, "An error occurred while creating the playlist.", "Error"

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)