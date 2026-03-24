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
- Adding, editing, duplicating, deleting entries and reordering are not available in this mode

### Self-hosted
Runs with a backend (Express + SQLite) served via Docker. Progress is stored in a database and persists independently of the browser.

- Progress syncs across all devices on the same network
- Data survives browser clears
- Supports custom entries, reordering, and editing via the UI

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

## Features

### Filters
All filters are active by default. Toggling one off hides that category.

| Filter | Color | Hides |
|--------|-------|-------|
| Caught | Red | Already-caught Pokémon |
| Forms | Blue | Alternate forms (same National #) |
| Genders | Purple | Entries with `(F)` in the name |
| Megas | Orange | Entries starting with `Mega-` |

Genders and Megas are intentionally excluded from the Forms filter — they each have their own dedicated toggle.

### Custom entries (self-hosted only)
- **Add Pokémon** — `+` button opens a modal to add an entry manually with name, types, dex numbers, and icon URL
- **Duplicate** — hover over any row to reveal a copy icon; opens the modal pre-filled for quick edits, inserts the new entry right after the original
- **Edit** — hover over a custom entry to reveal an edit icon
- **Delete** — hover over a custom entry to reveal a `×` icon

### Reorder (self-hosted only)
- Toggle the reorder button (↕) to enable drag-and-drop on all rows
- Order is persisted in the database

### Export / Import (static mode)
Progress, custom entries, and order can be exported as a JSON file and re-imported on another browser.

---

## Install as app (PWA)

The app can be installed on your device and used like a native app.

### Android (Chrome)

1. Open the app in Chrome
2. Tap the **"Add to home screen"** banner, or open the menu (⋮) and tap **"Add to home screen"**
3. Confirm and tap **Add**

### iOS (Safari)

1. Open the app in **Safari** (must be Safari, not Chrome or other browsers)
2. Tap the **Share** button (square with arrow, bottom toolbar)
3. Scroll down and tap **"Add to Home Screen"**
4. Confirm the name and tap **Add**

> On iOS, the app cache may be cleared by the system if the app is not used for 7+ days.

### Desktop (Chrome / Edge)

1. Open the app
2. Click the install icon in the address bar (or open the browser menu and look for **"Install app"**)

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
| `GET` | `/api/dexes/:id/pokemon` | All Pokémon for a dex, ordered by sort_order |
| `PUT` | `/api/pokemon/:id/caught` | Toggle caught `{ caught: true\|false }` |
| `POST` | `/api/dexes/:id/pokemon` | Add a custom Pokémon to a dex |
| `PUT` | `/api/pokemon/:id/fields` | Edit fields of a custom Pokémon |
| `DELETE` | `/api/pokemon/:id` | Delete a custom Pokémon |
| `PUT` | `/api/dexes/:id/order` | Update sort order `{ order: [id, ...] }` |
