const express = require('express')
const Database = require('better-sqlite3')
const cors = require('cors')
const path = require('path')
const fs = require('fs')

const app = express()
app.use(cors())
app.use(express.json())

const DATA_DIR  = path.join(__dirname, 'data')
const GAMES_DIR = path.join(DATA_DIR, 'games')
fs.mkdirSync(GAMES_DIR, { recursive: true })

// ── Database setup ─────────────────────────────────────────────────────────────
const db = new Database(path.join(DATA_DIR, 'pokemon.db'))

db.exec(`
  CREATE TABLE IF NOT EXISTS games (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    year INTEGER
  );

  CREATE TABLE IF NOT EXISTS dexes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id   INTEGER NOT NULL REFERENCES games(id),
    slug      TEXT NOT NULL,
    name      TEXT NOT NULL,
    col_label TEXT NOT NULL DEFAULT 'DEX',
    UNIQUE(game_id, slug)
  );

  CREATE TABLE IF NOT EXISTS pokemon (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    dex_id   INTEGER NOT NULL REFERENCES dexes(id),
    nac      TEXT,
    dex_num  TEXT,
    name     TEXT,
    tipo1    TEXT,
    tipo2    TEXT,
    icon_url TEXT,
    caught   INTEGER NOT NULL DEFAULT 0
  );

  CREATE INDEX IF NOT EXISTS idx_pokemon_dex ON pokemon (dex_id);
`)

// ── Seed from backend/data/games/*.json (skips already-loaded slugs) ──────────
const insertGame    = db.prepare('INSERT OR IGNORE INTO games (slug, name, year) VALUES (@slug, @name, @year)')
const insertDex     = db.prepare('INSERT OR IGNORE INTO dexes (game_id, slug, name, col_label) VALUES (@game_id, @slug, @name, @col_label)')
const insertPokemon = db.prepare(`
  INSERT INTO pokemon (dex_id, nac, dex_num, name, tipo1, tipo2, icon_url)
  VALUES (@dex_id, @nac, @dex_num, @name, @tipo1, @tipo2, @icon_url)
`)

const seedGame = db.transaction((gameFile) => {
  const { game, dexes } = gameFile

  insertGame.run(game)
  const gameRow = db.prepare('SELECT id FROM games WHERE slug = ?').get(game.slug)

  for (const dex of dexes) {
    insertDex.run({ game_id: gameRow.id, slug: dex.slug, name: dex.name, col_label: dex.col_label })
    const dexRow = db.prepare('SELECT id FROM dexes WHERE game_id = ? AND slug = ?').get(gameRow.id, dex.slug)

    const alreadySeeded = db.prepare('SELECT COUNT(*) AS c FROM pokemon WHERE dex_id = ?').get(dexRow.id).c > 0
    if (alreadySeeded) continue

    for (const p of dex.pokemon) insertPokemon.run({ dex_id: dexRow.id, ...p })
    console.log(`  ✓ ${game.slug} / ${dex.slug}: ${dex.pokemon.length} Pokémon`)
  }
})

const gameFiles = fs.readdirSync(GAMES_DIR).filter(f => f.endsWith('.json'))
if (gameFiles.length === 0) {
  console.warn('⚠️  No game files found in backend/data/games/ — run a scraper first.')
} else {
  for (const file of gameFiles) {
    const data = JSON.parse(fs.readFileSync(path.join(GAMES_DIR, file), 'utf8'))
    seedGame(data)
  }
}

// ── Routes ─────────────────────────────────────────────────────────────────────

// List all games with their dexes and caught/total counts
app.get('/api/games', (req, res) => {
  const games = db.prepare('SELECT * FROM games ORDER BY year DESC, name').all()

  const stats = db.prepare(`
    SELECT dex_id, COUNT(*) AS total, SUM(caught) AS caught
    FROM pokemon GROUP BY dex_id
  `).all()
  const statsMap = Object.fromEntries(stats.map(s => [s.dex_id, s]))

  const result = games.map(g => ({
    ...g,
    dexes: db.prepare('SELECT * FROM dexes WHERE game_id = ? ORDER BY id').all(g.id).map(d => ({
      ...d,
      total:  statsMap[d.id]?.total  ?? 0,
      caught: statsMap[d.id]?.caught ?? 0,
    })),
  }))

  res.json(result)
})

// Get all Pokémon for a dex
app.get('/api/dexes/:id/pokemon', (req, res) => {
  const rows = db.prepare(
    'SELECT * FROM pokemon WHERE dex_id = ? ORDER BY CAST(dex_num AS INTEGER)'
  ).all(Number(req.params.id))
  res.json(rows)
})

// Toggle caught status
app.put('/api/pokemon/:id/caught', (req, res) => {
  const { caught } = req.body
  db.prepare('UPDATE pokemon SET caught = ? WHERE id = ?').run(caught ? 1 : 0, Number(req.params.id))
  res.json({ ok: true })
})

// ── Start ──────────────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 3000
app.listen(PORT, () => console.log(`API running on http://localhost:${PORT}`))
