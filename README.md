# Pokédex Tracker

Track your caught Pokémon across multiple games and Pokédexes.

**Live demo:** https://alan-maldonado.github.io/pokedex-ref

---

## Modes

### Static (GitHub Pages)
The live demo runs entirely in the browser — no server required. Game data is bundled at build time and caught progress is saved in your browser's `localStorage`.

- No setup required
- Progress is saved per browser/device and is not synced across devices
- Clearing browser data will reset your progress

### Self-hosted
Runs with a backend (Express + SQLite) served via Docker. Progress is stored in a database and persists independently of the browser.

- Progress syncs across all devices on the same network
- Data survives browser clears
- Supports resetting or editing progress via the database

---

## Games included

| Game | Pokédexes |
|------|-----------|
| Pokémon Legends: Z-A | Luminalia, Dimensional |
| Pokémon Scarlet & Violet | Paldea, Noroteo, Arándano, Otros |
| Pokémon Sword & Shield | Galar, Isla Armadura, Tundra Corona, Otros |
| Pokémon Legends: Arceus | Hisui |
| Pokémon Brilliant Diamond & Shining Pearl | Sinnoh |
| Pokémon: Let's Go, Pikachu! & Let's Go, Eevee! | Kanto |

---

## Project structure

```
pokedex-ref/
├── backend/              Express API + SQLite database
│   ├── server.js
│   └── data/
│       └── games/        JSON data files, one per game
├── frontend/             Vue 3 + Vite + Tailwind
│   └── src/
│       ├── App.vue
│       └── data/         Game JSONs bundled for static mode
├── scrapers/             Data scraper scripts (Python)
└── docker-compose.yml
```

---

## Self-hosted setup

Requires Docker.

```bash
git clone https://github.com/alan-maldonado/pokedex-ref.git
cd pokedex-ref
docker compose up -d --build
```

Open `http://localhost:4001`

### Adding a new game

Run the scraper, then restart the backend:

```bash
python3 scrapers/scarlet_violet.py
docker compose restart backend
```

Available scrapers in `scrapers/`.

### Resetting progress for a specific dex

```bash
docker compose stop backend
sqlite3 backend/data/pokemon.db "DELETE FROM pokemon WHERE dex_id = (SELECT id FROM dexes WHERE slug = 'dex-slug');"
docker compose start backend
```

### Resetting all progress

Delete `backend/data/pokemon.db` and restart — the database will be re-seeded from the JSON files.

---

## Running locally (without Docker)

```bash
# Backend
cd backend && npm install && node server.js

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/games` | All games with dexes and caught/total counts |
| `GET` | `/api/dexes/:id/pokemon` | All Pokémon for a dex |
| `PUT` | `/api/pokemon/:id/caught` | Toggle caught `{ caught: true\|false }` |
