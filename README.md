# VirtualVinyl

This repository contains the code for the VirtualVinyl App. Instead of playing a long Spotify playlist, why not select a curated playlist of 8 to 12 songs to become your today's soundtrack?


## Backend setup

```bash
pip install -r requirements.txt
python app.py
```

## Frontend setup

The repository now includes a simple Dash application that acts as the
frontend. To run it locally without Docker, install the dependencies and
start the Dash server:

```bash
pip install -r requirements.frontend.txt
python dash_app.py
```

## Running with Docker Compose

This repository also provides a `docker-compose.yml` file that spins up the
Flask backend and the frontend automatically. No manual
setup steps are required.

Start both services with (use `--build` the first time to build the images):

```bash
docker-compose up
```

The backend will be available on <http://localhost:5000> and the frontend on
<http://localhost:3000>.
