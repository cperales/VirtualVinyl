# VirtualVinyl

This repository contains the code for the VirtualVinyl App. Instead of playing a long Spotify playlist, why not select a curated playlist of 8 to 12 songs to become your today's soundtrack?


## Backend setup

```bash
pip install -r requirements.txt
python app.py
```

## Frontend setup

```bash
pip install -r requirements_frontend.txt
python dash_app.py
```

## Running with Docker Compose

This repository also provides a `docker-compose.yml` file that spins up the
Flask backend and the Dash frontend automatically.
Start both services with (use `--build` the first time to build the images):

```bash
docker-compose up
```

The backend will be available on <http://localhost:5000> and the frontend on
<http://localhost:3000>.
