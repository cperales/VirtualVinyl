# VirtualVinyl

This repository contains the code for the VirtualVinyl App. Instead of playing a long Spotify playlist, why not select a curated playlist of 8 to 12 songs to become your today's soundtrack?


## Backend setup

```bash
pip install -r requirements.txt
python app.py
```

## Frontend setup

```bash
npx create-react-app virtualvinyl
cd virtualvinyl
npm install lucide-react
# Replace src/App.js with the React code
npm start
```

## Running with Docker Compose

This repository also provides a `docker-compose.yml` file that spins up the
Flask backend and a development server for the React frontend. The compose
setup expects that you have created the React application inside a
`virtualvinyl/` directory as shown in the steps above.

Start both services with:

```bash
docker-compose up
```

The backend will be available on <http://localhost:5000> and the frontend on
<http://localhost:3000>.
