import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import requests
import webbrowser

# Spotify OAuth endpoints and your backend URL
BACKEND_URL = "http://localhost:5000"
SPOTIFY_AUTH_URL = f"{BACKEND_URL}/login"

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Virtual Vinyl - Spotify Login"),
    html.Button("Login with Spotify", id="login-btn", n_clicks=0),
    dcc.Location(id="url", refresh=True),
    html.Div(id="login-status")
])

@app.callback(
    Output("login-status", "children"),
    Input("login-btn", "n_clicks"),
    prevent_initial_call=True
)
def login_with_spotify(n_clicks):
    if n_clicks:
        # Open the backend's Spotify login endpoint in a new browser tab
        webbrowser.open_new_tab(SPOTIFY_AUTH_URL)
        return "Redirecting to Spotify login..."
    return ""

if __name__ == "__main__":
    app.run(debug=True, port=3000)
# 