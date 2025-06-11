# VirtualVinyl

This repository contains the code for the VirtualVinyl App. Instead of playing a long Spotify playlist, why not select a curated playlist of 8 to 12 songs to become your today's soundtrack?


## Backend setup

```bash
pip install -r requirements.txt
python app.py
```

## Frontend setup

```bash
npx create-react-app virtual-vinyl-frontend --template typescript
cd virtual-vinyl-frontend
npm install lucide-react
# Replace src/App.tsx with the React code
npm start
```

## Running with Docker Compose

This repository also provides a `docker-compose.yml` file that spins up the
Flask backend and builds a React frontend automatically. The compose setup
installs Python dependencies, generates a TypeScript React application, copies
`react_frontend.tsx` into it and starts both development servers. No manual
setup steps are required.

Start both services with (use `--build` the first time to build the images):

```bash
docker-compose up
```

The backend will be available on <http://localhost:5000> and the frontend on
<http://localhost:3000>.
