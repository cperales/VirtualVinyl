import json
from urllib.parse import parse_qs

import dash
from dash import html, dcc, Input, Output, State, ctx

from streamlit_app.playlist import PlaylistManager
from streamlit_app.spotify_client import SpotifyClient
from streamlit_app.tidal_client import TidalClient

# Global clients mimicking Streamlit session state
sp = SpotifyClient()
td = TidalClient()
pl = PlaylistManager()

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.H1("Virtual Vinyl"),
    html.Div([
        html.Div([
            html.Button("Login with Spotify", id="spotify-login-btn"),
            html.Div(id="spotify-login-area"),
        ], style={"width": "48%", "display": "inline-block"}),
        html.Div([
            html.Button("Login with TIDAL", id="tidal-login-btn"),
            html.Div(id="tidal-login-area"),
        ], style={"width": "48%", "display": "inline-block"}),
    ]),
    html.Div(id="user-info"),
    html.Div([
        dcc.Input(id="search-input", type="text", placeholder="Search tracks"),
        html.Button("Search", id="search-btn"),
    ], style={"marginTop": "20px"}),
    html.Div(id="tracks-list"),
    html.Div(id="selected-count"),
    dcc.Input(id="playlist-name", type="text", placeholder="Playlist name"),
    html.Button("Create Spotify Playlist", id="create-playlist-btn"),
    html.Div(id="playlist-message"),
    dcc.Store(id="track-map", data={}),
])


@app.callback(Output("spotify-login-area", "children"), Input("spotify-login-btn", "n_clicks"), prevent_initial_call=True)
def show_spotify_login(n_clicks):
    return html.A("Open login", href=sp.login_url(), target="_blank")


@app.callback(Output("tidal-login-area", "children"), Input("tidal-login-btn", "n_clicks"), prevent_initial_call=True)
def show_tidal_login(n_clicks):
    return html.A("Open login", href=td.login_url("state123"), target="_blank")


@app.callback(Output("user-info", "children"), Input("url", "search"))
def handle_auth(search):
    if search:
        params = parse_qs(search.lstrip("?"))
        code = params.get("code", [None])[0]
        if code:
            if not sp.is_authenticated():
                sp.handle_callback(code)
            if not td.is_authenticated():
                td.handle_callback(code)
    msgs = []
    if sp.is_authenticated():
        user = sp.current_user()
        msgs.append(html.Div(f"Logged in as {user['display_name']}"))
    if td.is_authenticated():
        msgs.append(html.Div("TIDAL authenticated"))
    return msgs


@app.callback(
    [Output("tracks-list", "children"), Output("track-map", "data")],
    [Input("search-btn", "n_clicks"), Input("user-info", "children")],
    State("search-input", "value"),
    prevent_initial_call=True,
)
def update_tracks(n_clicks, _user, query):
    if not sp.is_authenticated():
        return [], {}
    if query:
        tracks = sp.search_tracks(query)
    else:
        tracks = sp.top_tracks()
    track_map = {
        t["id"]: {"id": t["id"], "uri": t["uri"]}
        for t in tracks
    }
    children = [
        html.Div(
            [
                html.Span(f"{t['name']} - {', '.join(a['name'] for a in t['artists'])}"),
                html.Button("Select", id={"type": "track", "index": t["id"]}),
            ]
        )
        for t in tracks
    ]
    return children, track_map


@app.callback(
    Output("selected-count", "children"),
    Input({"type": "track", "index": dash.ALL}, "n_clicks"),
    State("track-map", "data"),
    prevent_initial_call=True,
)
def toggle_track(n_clicks, track_map):
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    trig = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    track_id = trig["index"]
    track = track_map.get(track_id)
    if track:
        pl.toggle_track(track)
    return f"Selected {len(pl.selected_tracks)} tracks"


@app.callback(
    Output("playlist-message", "children"),
    Input("create-playlist-btn", "n_clicks"),
    [State("playlist-name", "value"), State("track-map", "data")],
    prevent_initial_call=True,
)
def create_playlist(n_clicks, name, track_map):
    if not name or not sp.is_authenticated():
        raise dash.exceptions.PreventUpdate
    track_uris = [t["uri"] for t in pl.selected_tracks]
    playlist = sp.create_playlist(name, track_uris)
    if playlist:
        pl.selected_tracks = []
        url = playlist.get("external_urls", {}).get("spotify")
        return html.Div(["Created playlist ", html.A(playlist["name"], href=url, target="_blank")])
    return "Failed to create playlist"


if __name__ == "__main__":
    app.run(debug=True, port=8000)
