#!/usr/bin/env python3
"""
Scraper for Pokémon Scarlet & Violet (WikiDex).
Downloads the Paldea, Noroteo, Arándano, and Otros Pokédexes.
Output: backend/data/games/scarlet-violet.json  (see scrapers/README.md)
"""

import json
import os
import re
import urllib.request


SOURCE_URL = "https://www.wikidex.net/wiki/Lista_de_Pok%C3%A9mon_seg%C3%BAn_la_Pok%C3%A9dex_de_Paldea"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "backend", "data", "games", "scarlet-violet.json")


def download(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (compatible; PokédexScraper/1.0)"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read()


def get_all_icons(cell_html):
    """Returns list of (alt_name, url) for every <img> in the cell."""
    results = []
    for img_match in re.finditer(r'<img([^>]+)>', cell_html):
        attrs = img_match.group(1)
        alt = re.search(r'alt="([^"]+)"', attrs)
        name = alt.group(1) if alt else ""
        srcset = re.search(r'srcset="([^"]+)"', attrs)
        if srcset:
            url = srcset.group(1).split(",")[-1].strip().split(" ")[0]
        else:
            src = re.search(r'src="([^"]+)"', attrs)
            url = src.group(1) if src else None
        results.append((name, url))
    return results


def get_icon_name(cell_html):
    m = re.search(r'<img[^>]+alt="([^"]+)"', cell_html)
    return m.group(1) if m else ""


def cell_text(html):
    return re.sub(r'<[^>]+>', '', html).strip()


def get_types(cells_html):
    combined = " ".join(cells_html)
    alts = re.findall(r'alt="(Tipo [^"]+)"', combined)
    types = [t.replace("Tipo ", "").capitalize() for t in alts]
    return types[0] if types else "", types[1] if len(types) > 1 else ""


def parse_table(table_html, has_dex_num=True):
    """
    has_dex_num=True:  columns are NAC, DEX, icon, name, tipo...
    has_dex_num=False: columns are NAC, icon, name, tipo...  (Otros table)
    """
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)

    entries = []
    pending_nac  = None
    pending_dex  = None
    pending_name = None

    # Column offsets depending on table layout
    icon_idx = 2 if has_dex_num else 1
    name_idx = 3 if has_dex_num else 2

    for row in rows:
        cells = re.findall(r'(<t[dh][^>]*>)(.*?)</t[dh]>', row, re.DOTALL)
        if not cells:
            continue

        n = len(cells)
        first_content = cell_text(cells[0][1])

        if re.match(r'^\d+$', first_content) and n >= (4 if has_dex_num else 3):
            nac = first_content
            dex = cell_text(cells[1][1]) if has_dex_num else ""

            rowspan_match = re.search(r'rowspan="(\d+)"', cells[0][0])
            if rowspan_match and int(rowspan_match.group(1)) > 1:
                pending_nac, pending_dex = nac, dex
            else:
                pending_nac = pending_dex = pending_name = None

            name = cell_text(cells[name_idx][1])
            name_rowspan = re.search(r'rowspan="(\d+)"', cells[name_idx][0])
            pending_name = name if (name_rowspan and int(name_rowspan.group(1)) > 1) else None

            tipo1, tipo2 = get_types([c[1] for c in cells[name_idx:]])
            icons = get_all_icons(cells[icon_idx][1])

            if len(icons) > 1:
                for form_name, icon_url in icons:
                    entries.append({
                        "nac": nac, "dex_num": dex,
                        "name": form_name or name,
                        "tipo1": tipo1, "tipo2": tipo2 or "", "icon_url": icon_url,
                    })
            else:
                icon_url = icons[0][1] if icons else None
                entries.append({
                    "nac": nac, "dex_num": dex, "name": name,
                    "tipo1": tipo1, "tipo2": tipo2 or "", "icon_url": icon_url,
                })

        elif n <= (4 if has_dex_num else 3) and pending_nac:
            icons = get_all_icons(cells[0][1])

            if n >= 3 and 'alt="Tipo ' not in cells[1][1]:
                name = cell_text(cells[1][1])
                tipo1, tipo2 = get_types([c[1] for c in cells[1:]])
            else:
                name = get_icon_name(cells[0][1]) or pending_name
                tipo1, tipo2 = get_types([c[1] for c in cells])

            if len(icons) > 1:
                for form_name, icon_url in icons:
                    entries.append({
                        "nac": pending_nac, "dex_num": pending_dex,
                        "name": form_name or name,
                        "tipo1": tipo1, "tipo2": tipo2 or "", "icon_url": icon_url,
                    })
            else:
                icon_url = icons[0][1] if icons else None
                entries.append({
                    "nac": pending_nac, "dex_num": pending_dex, "name": name,
                    "tipo1": tipo1, "tipo2": tipo2 or "", "icon_url": icon_url,
                })

    return entries


def main():
    print("Downloading page...")
    html = download(SOURCE_URL).decode("utf-8")

    print("Parsing tables...")
    tables = re.findall(
        r'<table class="sortable tabpokemon"[^>]*>(.*?)</table>',
        html, re.DOTALL
    )
    if len(tables) < 4:
        print(f"Error: expected 4 tables, found {len(tables)}.")
        return

    paldea  = parse_table(tables[0], has_dex_num=True)
    noroteo = parse_table(tables[1], has_dex_num=True)
    arandano = parse_table(tables[2], has_dex_num=True)
    otros   = parse_table(tables[3], has_dex_num=False)

    print(f"  Paldea:   {len(paldea)} entries")
    print(f"  Noroteo:  {len(noroteo)} entries")
    print(f"  Arándano: {len(arandano)} entries")
    print(f"  Otros:    {len(otros)} entries")

    data = {
        "game": {
            "slug": "scarlet-violet",
            "name": "Pokémon Scarlet & Violet",
            "year": 2022,
        },
        "dexes": [
            {"slug": "paldea",   "name": "Pokédex de Paldea",   "col_label": "PAL", "pokemon": paldea},
            {"slug": "noroteo",  "name": "Pokédex de Noroteo",  "col_label": "NOR", "pokemon": noroteo},
            {"slug": "arandano", "name": "Pokédex de Arándano", "col_label": "ARÁ", "pokemon": arandano},
            {"slug": "otros",    "name": "Otros Pokémon",       "col_label": "NAC", "pokemon": otros},
        ],
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
