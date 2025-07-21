# Virtual Vinyl

This repository contains the code for **Virtual Vinyl**. Instead of playing a long Spotify playlist, why not select a curated playlist of 8 to 12 songs to become your today's soundtrack? [Click here to discover](https://cperales.github.io/VirtualVinyl).

## Streamlit App

A basic Streamlit interface reproduces the Virtual Vinyl experience in Python.

### Setup

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set the following environment variables for authentication:

- `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` – Spotify credentials
- `REDIRECT_URI` – Spotify redirect URI
- `TIDAL_CLIENT_ID` – TIDAL application id
- `TIDAL_REDIRECT_URI` – TIDAL redirect URI

### Run

```sh
streamlit run streamlit_app/app.py
```

### Flask Version

You can also run the web interface with Flask:

```sh
flask --app flask_app.app run
```

### Python Tests

Run the Streamlit backend tests with `pytest`:

```sh
pytest
```
