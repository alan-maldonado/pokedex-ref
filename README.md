# Pokédex Reference App

A personal Pokédex tracker built with Vue 3 + Vite + Tailwind (frontend) and Express + SQLite (backend). Tracks caught Pokémon across multiple games and regional Pokédexes.

Currently includes **Pokémon Legends: Z-A**:
- Pokédex de Ciudad Luminalia (256 entries)
- Pokédex Dimensional (152 entries)

---

## Project structure

```
pokedex-ref/
├── backend/              Express API + SQLite database
│   ├── server.js
│   └── data/
│       └── games/        JSON data files, one per game
├── frontend/             Vue 3 + Vite + Tailwind
│   └── src/App.vue
├── scrapers/             Data scraper scripts
│   ├── legends_za.py     Scraper for Pokémon Legends: Z-A
│   └── README.md         Guide for adding new games
└── docker-compose.yml
```

---

## Running locally (Node)

### Prerequisites
- Node.js 20+
- Python 3.9+ (only needed to regenerate data)

### 1. Generate the game data

```bash
python3 scrapers/legends_za.py
# Outputs: backend/data/games/legends-za.json
```

> Skip this step if `backend/data/games/legends-za.json` already exists.

### 2. Start the backend

```bash
cd backend
npm install
node server.js
# API running on http://localhost:3000
```

The backend seeds the SQLite database from the JSON files on first run.

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
# App running on http://localhost:5173
```

Open [http://localhost:5173](http://localhost:5173).

---

## Running with Docker Compose

### Prerequisites
- Docker Desktop

### 1. Generate the game data

```bash
python3 scrapers/legends_za.py
# Outputs: backend/data/games/legends-za.json
```

### 2. Build and start

```bash
docker-compose up --build
```

| Service  | URL |
|----------|-----|
| App      | http://localhost:4001 |
| API      | http://localhost:4001/api |

The `backend/data/` directory is mounted as a volume, so the SQLite database
and JSON files persist between container restarts.

### Stop

```bash
docker-compose down
```

---

## API reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/games` | All games with dexes and caught/total counts |
| `GET` | `/api/dexes/:id/pokemon` | All Pokémon for a specific dex |
| `PUT` | `/api/pokemon/:id/caught` | Toggle caught status `{ caught: true\|false }` |

---

## Adding a new game

See **[scrapers/README.md](scrapers/README.md)** for the full guide.

Short version:
1. Copy the scraper template from `scrapers/README.md`
2. Save it as `scrapers/<game-slug>.py` and fill in the config
3. Run it — outputs to `backend/data/games/<game-slug>.json`
4. Restart the backend — the new game appears automatically in the app

---

## Resetting caught progress

Delete `backend/data/pokemon.db` and restart the backend. The database will be
re-seeded from the JSON files with all caught statuses reset to zero.
