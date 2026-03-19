# Cómo agregar una nueva Pokédex

Cada juego de Pokémon se representa con un archivo JSON en `backend/data/games/<slug>.json`.
El backend escanea esa carpeta al arrancar y carga automáticamente los juegos que no estén
ya en la base de datos.

---

## 1. Formato del archivo JSON

```json
{
  "game": {
    "slug": "legends-za",
    "name": "Pokémon Legends: Z-A",
    "year": 2025
  },
  "dexes": [
    {
      "slug":      "luminalia",
      "name":      "Pokédex de Ciudad Luminalia",
      "col_label": "LUM",
      "pokemon": [
        {
          "nac":      "0152",
          "dex_num":  "001",
          "name":     "Chikorita",
          "tipo1":    "Planta",
          "tipo2":    "",
          "icon_url": "https://images.wikidexcdn.net/..."
        }
      ]
    },
    {
      "slug":      "dimensional",
      "name":      "Pokédex Dimensional",
      "col_label": "DIM",
      "pokemon": [ ... ]
    }
  ]
}
```

### Campos obligatorios

| Campo | Descripción |
|---|---|
| `game.slug` | Identificador único del juego, kebab-case. Ej: `scarlet-violet`, `sword-shield` |
| `game.name` | Nombre completo para mostrar en la UI |
| `game.year` | Año de lanzamiento (determina el orden en el selector) |
| `dexes[].slug` | Identificador único de la dex dentro del juego |
| `dexes[].name` | Nombre completo de la dex para mostrar en la tab |
| `dexes[].col_label` | Etiqueta corta para la columna de número de dex. Ej: `LUM`, `DIM`, `PAL`, `KIT` |
| `pokemon[].nac` | Número de la Pokédex Nacional, con ceros iniciales. Ej: `"0025"` |
| `pokemon[].dex_num` | Número en esta dex específica. Ej: `"053"` |
| `pokemon[].name` | Nombre del Pokémon o de la forma/variante. Ej: `"Raichu de Alola"` |
| `pokemon[].tipo1` | Tipo principal en español. Ver tabla de tipos abajo |
| `pokemon[].tipo2` | Tipo secundario en español, o `""` si no tiene |
| `pokemon[].icon_url` | URL directa al sprite PNG. Puede ser `null` si no hay imagen |

### Tipos válidos (español)

`Normal` `Fuego` `Agua` `Planta` `Eléctrico` `Hielo` `Pelea` `Veneno` `Tierra`
`Volador` `Psíquico` `Bicho` `Roca` `Fantasma` `Dragón` `Siniestro` `Acero` `Hada`

> **Nota:** WikiDex a veces usa "Lucha" como sinónimo de "Pelea". El scraper base ya
> maneja este alias, pero si escribes tu propio scraper tenlo en cuenta.

---

## 2. Scrapers existentes

### `pokedex_luminalia_img.py` — Pokémon Legends: Z-A

Scraper completo para Z-A. Genera también el archivo Excel.

```bash
python3 pokedex_luminalia_img.py
# Salida: backend/data/games/legends-za.json
#         pokedex_luminalia.xlsx
```

Fuente: [WikiDex — Lista por Pokédex de Ciudad Luminalia](https://www.wikidex.net/wiki/Lista_de_Pok%C3%A9mon_seg%C3%BAn_la_Pok%C3%A9dex_de_Ciudad_Luminalia)

---

## 3. Crear un scraper para un nuevo juego

### 3.1 Estructura de la página en WikiDex

La mayoría de las listas de Pokémon en WikiDex usan una tabla con clase `sortable tabpokemon`.

```
URL patrón: https://www.wikidex.net/wiki/Lista_de_Pokémon_según_la_Pokédex_de_<Nombre>
```

Estructura HTML típica de la tabla:

```html
<table class="sortable tabpokemon" ...>
  <!-- Fila normal (Pokémon sin variantes) -->
  <tr>
    <td>0152</td>          <!-- #NAC -->
    <td>001</td>           <!-- número en esta dex -->
    <td><img alt="Chikorita" src="..."></td>   <!-- icono -->
    <td>Chikorita</td>     <!-- nombre -->
    <td colspan="2"><img alt="Tipo planta" ...></td>  <!-- tipo único -->
  </tr>

  <!-- Pokémon con variantes: NAC/LUM tienen rowspan -->
  <tr>
    <td rowspan="2">0026</td>   <!-- NAC cubre 2 filas -->
    <td rowspan="2">054</td>    <!-- dex_num cubre 2 filas -->
    <td><img alt="Raichu" ...></td>
    <td>Raichu</td>
    <td colspan="2"><img alt="Tipo eléctrico" ...></td>
  </tr>
  <!-- Fila de variante (solo 3 celdas: icono, nombre, tipo) -->
  <tr>
    <td><img alt="Raichu de Alola" ...></td>
    <td>Raichu de Alola</td>
    <td><img alt="Tipo eléctrico" ...><img alt="Tipo psíquico" ...></td>
  </tr>

  <!-- Variante con nombre rowspanned (Mega evoluciones con tipos diferentes) -->
  <tr>
    <td rowspan="3">0150</td>
    <td rowspan="3">232</td>
    <td><img alt="Mewtwo" ...></td>
    <td rowspan="3">Mewtwo</td>     <!-- nombre abarca las 3 filas -->
    <td colspan="2"><img alt="Tipo psíquico" ...></td>
  </tr>
  <!-- Fila de variante: solo 2 celdas (icono + tipo), nombre del alt del icono -->
  <tr>
    <td><img alt="Mega-Mewtwo X" ...></td>
    <td><img alt="Tipo psíquico" ...></td>
    <td><img alt="Tipo pelea" ...></td>
  </tr>
```

### 3.2 Plantilla de scraper

Copia y adapta este esqueleto para un nuevo juego:

```python
#!/usr/bin/env python3
"""
Scraper para Pokémon <NombreJuego>.
Genera: backend/data/games/<slug>.json
Fuente: <URL de WikiDex>
"""

import json
import os
import re
import urllib.request


# ── Configuración del juego ────────────────────────────────────────────────────
GAME = {
    "slug": "scarlet-violet",          # kebab-case único
    "name": "Pokémon Escarlata y Violeta",
    "year": 2022,
}

# Una entrada por cada Pokédex regional del juego.
# La URL debe apuntar a la página de WikiDex que contiene la tabla tabpokemon.
# Si todas las dexes están en la misma página, usa la misma URL y ajusta
# el índice de tabla (TABLE_INDEX).
DEXES = [
    {
        "slug":      "paldea",
        "name":      "Pokédex de Paldea",
        "col_label": "PAL",
        "url":       "https://www.wikidex.net/wiki/Lista_de_Pokémon_...",
        "table_index": 0,             # índice de la tabla tabpokemon en la página
    },
    # {
    #     "slug":      "kitakami",
    #     "name":      "Pokédex de Kitakami",
    #     "col_label": "KIT",
    #     "url":       "https://www.wikidex.net/wiki/...",
    #     "table_index": 0,
    # },
]

OUTPUT_PATH = "backend/data/games/scarlet-violet.json"

# ── Funciones de parsing (igual para todas las páginas de WikiDex) ─────────────

def download(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (compatible; PokedexScraper/1.0)"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")

def get_icon_url(cell_html):
    img = re.search(r'<img([^>]+)>', cell_html)
    if not img:
        return None
    attrs = img.group(1)
    srcset = re.search(r'srcset="([^"]+)"', attrs)
    if srcset:
        last = srcset.group(1).split(",")[-1].strip().split(" ")[0]
        if last:
            return last
    src = re.search(r'src="([^"]+)"', attrs)
    return src.group(1) if src else None

def get_icon_name(cell_html):
    m = re.search(r'<img[^>]+alt="([^"]+)"', cell_html)
    return m.group(1) if m else ""

def cell_text(html):
    return re.sub(r'<[^>]+>', '', html).strip()

def get_types(cells_html):
    combined = " ".join(cells_html)
    alts = re.findall(r'alt="(Tipo [^"]+)"', combined)
    types = [t.replace("Tipo ", "").capitalize() for t in alts]
    # "Lucha" es alias de "Pelea"
    types = ["Pelea" if t == "Lucha" else t for t in types]
    return types[0] if types else "", types[1] if len(types) > 1 else ""

def parse_table(table_html):
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
    entries = []
    pending_nac = pending_dex_num = pending_name = None

    for row in rows:
        cells = re.findall(r'(<t[dh][^>]*>)(.*?)</t[dh]>', row, re.DOTALL)
        if not cells:
            continue
        n = len(cells)
        first = cell_text(cells[0][1])

        if re.match(r'^\d+$', first) and n >= 4:
            nac     = first
            dex_num = cell_text(cells[1][1])
            name    = cell_text(cells[3][1])

            rowspan = re.search(r'rowspan="(\d+)"', cells[0][0])
            if rowspan and int(rowspan.group(1)) > 1:
                pending_nac, pending_dex_num = nac, dex_num
            else:
                pending_nac = pending_dex_num = pending_name = None

            name_rs = re.search(r'rowspan="(\d+)"', cells[3][0])
            pending_name = name if (name_rs and int(name_rs.group(1)) > 1) else None

            entries.append({
                "nac": nac, "dex_num": dex_num, "name": name,
                "tipo1": get_types([c[1] for c in cells[3:]])[0],
                "tipo2": get_types([c[1] for c in cells[3:]])[1],
                "icon_url": get_icon_url(cells[2][1]),
            })

        elif n <= 4 and pending_nac:
            icon_url = get_icon_url(cells[0][1])
            if n >= 3 and 'alt="Tipo ' not in cells[1][1]:
                name = cell_text(cells[1][1])
                tipo1, tipo2 = get_types([c[1] for c in cells[1:]])
            else:
                name = get_icon_name(cells[0][1]) or pending_name
                tipo1, tipo2 = get_types([c[1] for c in cells])

            entries.append({
                "nac": pending_nac, "dex_num": pending_dex_num, "name": name,
                "tipo1": tipo1, "tipo2": tipo2, "icon_url": icon_url,
            })

    return entries

def scrape_dex(dex_config):
    print(f"  Descargando {dex_config['name']}...")
    html = download(dex_config["url"])
    tables = re.findall(
        r'<table class="sortable tabpokemon"[^>]*>(.*?)</table>', html, re.DOTALL
    )
    if not tables:
        raise ValueError(f"No se encontró tabla tabpokemon en {dex_config['url']}")
    idx = dex_config.get("table_index", 0)
    pokemon = parse_table(tables[idx])
    print(f"    → {len(pokemon)} entradas (incluye variantes)")
    return pokemon

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"Scrapeando {GAME['name']}...")
    dexes_data = []
    for dex_cfg in DEXES:
        pokemon = scrape_dex(dex_cfg)
        dexes_data.append({
            "slug":      dex_cfg["slug"],
            "name":      dex_cfg["name"],
            "col_label": dex_cfg["col_label"],
            "pokemon":   pokemon,
        })

    output = {"game": GAME, "dexes": dexes_data}
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Guardado: {OUTPUT_PATH}")
    print("  Reinicia el backend para cargar el nuevo juego.")


if __name__ == "__main__":
    main()
```

### 3.3 Pasos para agregar un juego nuevo

1. **Copia la plantilla** anterior a `scrapers/<slug>.py`
2. **Ajusta** `GAME`, `DEXES` y `OUTPUT_PATH`
3. **Ejecuta** el scraper:
   ```bash
   python3 scrapers/<slug>.py
   ```
4. **Verifica** el JSON generado en `backend/data/games/<slug>.json`
5. **Elimina** `backend/data/pokemon.db` para forzar re-seed (o reinicia el backend si es la primera vez que se agrega ese juego — el backend detecta slugs nuevos automáticamente sin borrar la DB)
6. **Reinicia** el backend:
   ```bash
   # Local
   cd backend && node server.js
   # Docker
   docker-compose restart backend
   ```
7. El nuevo juego aparecerá automáticamente en el selector de la app

---

## 4. Notas y casos especiales

### Múltiples dexes en la misma página
Si WikiDex tiene varias Pokédex en la misma URL (como Z-A, que tiene Luminalia y Dimensional
en la misma página), usa el mismo `url` con diferente `table_index`:

```python
DEXES = [
    { ..., "url": "https://...", "table_index": 0 },  # primera tabla
    { ..., "url": "https://...", "table_index": 1 },  # segunda tabla
]
```

### Pokémon con múltiples formas en el mismo icono
Algunos Pokémon tienen sus variantes (Mega X/Y, formas Alola, etc.) en la misma celda
de icono con múltiples `<img>`. En ese caso el scraper toma solo la primera imagen
(la forma base). Esto es intencionado — las variantes con tipos distintos tienen
su propia fila en la tabla.

### La URL tiene caracteres especiales
Si la URL de WikiDex tiene tildes o caracteres no ASCII, encódalos con `urllib.parse.quote`:
```python
from urllib.parse import quote
url = "https://www.wikidex.net/wiki/" + quote("Lista_de_Pokémon_según_...")
```

### Juegos con Pokédex de otras fuentes (no WikiDex)
Si los datos vienen de otra fuente, puedes generar el JSON a mano o con tu propio parser,
siempre que respete el esquema documentado en la sección 1.
