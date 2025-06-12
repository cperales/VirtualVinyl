import requests
from dash import Dash, html, dcc, Input, Output, State
from flask import request as flask_request

BACKEND_URL = "http://localhost:5000"

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("VirtualVinyl"),
    html.A("Login with Spotify", href=f"{BACKEND_URL}/login"),
    html.Br(),
    dcc.Input(id='search-input', type='text', placeholder='Search tracks'),
    html.Button('Search', id='search-btn'),
    html.Div(id='search-results'),
    html.Button('Create Playlist', id='create-btn'),
    html.Div(id='playlist-msg')
])


@app.callback(Output('search-results', 'children'),
              Input('search-btn', 'n_clicks'),
              State('search-input', 'value'))
def search(n_clicks, query):
    if not n_clicks or not query:
        return ''
    r = requests.get(f"{BACKEND_URL}/api/search", params={'q': query},
                     cookies=flask_request.cookies)
    if r.status_code != 200:
        return f"Error: {r.json().get('error')}"
    tracks = r.json().get('tracks', {}).get('items', [])
    options = [
        {'label': f"{t['name']} - {t['artists'][0]['name']}", 'value': t['uri']} 
        for t in tracks
    ]
    return dcc.Checklist(id='track-list', options=options)


@app.callback(Output('playlist-msg', 'children'),
              Input('create-btn', 'n_clicks'),
              State('track-list', 'value'))
def create_playlist(n_clicks, track_uris):
    if not n_clicks:
        return ''
    track_uris = track_uris or []
    r = requests.post(f"{BACKEND_URL}/api/create-playlist",
                      json={'track_uris': track_uris},
                      cookies=flask_request.cookies)
    if r.status_code != 200:
        return f"Error: {r.json().get('error')}"
    data = r.json()
    return html.Div([
        html.P(data.get('message')),
        html.A('Open Playlist', href=data.get('playlist_url'), target='_blank')
    ])


if __name__ == '__main__':
    app.run(port=3000, debug=True)
