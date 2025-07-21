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

- `CLIENT_ID` and `CLIENT_SECRET` – Spotify credentials
- `REDIRECT_URI` – Spotify redirect URI
- `TIDAL_CLIENT_ID` – TIDAL application id
- `TIDAL_REDIRECT_URI` – TIDAL redirect URI

### Run

```sh
streamlit run streamlit_app/app.py
```

## Dash App

A Plotly Dash interface providing the same functionality as the Streamlit version.

### Setup

Use the same Python environment as for the Streamlit app:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run

```sh
python -m dash_app.app
```
