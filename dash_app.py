"""Dash frontend for Virtual Vinyl."""

import webbrowser

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output

BACKEND_URL = "http://localhost:5000"
SPOTIFY_AUTH_URL = f"{BACKEND_URL}/login"

external_stylesheets = [dbc.themes.SANDSTONE]
app = dash.Dash(
    __name__, assets_folder="docs/img", external_stylesheets=external_stylesheets
)

image_url = app.get_asset_url("vinyl.jpg")

app.layout = dbc.Container(
    [
        html.H1("Virtual Vinyl", className="text-center mt-4"),
        html.P(
            "Create a curated playlist of 8 to 12 songs.",
            className="text-center",
        ),
        dbc.Row(
            dbc.Col(
                html.Img(
                    src=image_url,
                    className="img-fluid rounded shadow-sm",
                    style={"maxWidth": "400px"},
                ),
                width="auto",
            ),
            className="justify-content-center my-4",
        ),
        dbc.Row(
            dbc.Button(
                "Login with Spotify",
                id="login-btn",
                color="primary",
                n_clicks=0,
                className="px-4 py-2",
            ),
            className="justify-content-center",
        ),
        dcc.Location(id="url", refresh=True),
        html.Div(id="login-status", className="text-center mt-3"),
    ],
    fluid=True,
)


@app.callback(
    Output("login-status", "children"),
    Input("login-btn", "n_clicks"),
    prevent_initial_call=True,
)
def login_with_spotify(n_clicks):
    """Open backend's login endpoint in a new tab when button is clicked."""

    if n_clicks:
        webbrowser.open_new_tab(SPOTIFY_AUTH_URL)
        return "Redirecting to Spotify login..."
    return ""


if __name__ == "__main__":
    app.run(debug=True, port=3000)
