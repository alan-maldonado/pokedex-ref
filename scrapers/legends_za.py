#!/usr/bin/env python3
"""
Scraper for Pokémon Legends: Z-A (WikiDex).
Downloads the Ciudad Luminalia and Dimensional Pokédexes, including regional
variants and alternate forms.
Output: backend/data/games/legends-za.json  (see scrapers/README.md)
"""

import json
import os
import re
import urllib.request


SOURCE_URL = "https://www.wikidex.net/wiki/Lista_de_Pok%C3%A9mon_seg%C3%BAn_la_Pok%C3%A9dex_de_Ciudad_Luminalia"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "backend", "data", "games", "legends-za.json")


def download(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (compatible; PokédexScraper/1.0)"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read()


def get_icon_url(cell_html):
    """Returns the highest-res URL from the FIRST <img> in the cell."""
    img_match = re.search(r'<img([^>]+)>', cell_html)
    if not img_match:
        return None
    attrs = img_match.group(1)
    srcset = re.search(r'srcset="([^"]+)"', attrs)
    if srcset:
        last = srcset.group(1).split(",")[-1].strip().split(" ")[0]
        if last:
            return last
    src = re.search(r'src="([^"]+)"', attrs)
    return src.group(1) if src else None


def get_icon_name(cell_html):
    """Returns the alt text of the first <img> (name fallback for rowspanned name cells)."""
    m = re.search(r'<img[^>]+alt="([^"]+)"', cell_html)
    return m.group(1) if m else ""


def cell_text(html):
    return re.sub(r'<[^>]+>', '', html).strip()


def get_types(cells_html):
    combined = " ".join(cells_html)
    alts = re.findall(r'alt="(Tipo [^"]+)"', combined)
    types = [t.replace("Tipo ", "").capitalize() for t in alts]
    return types[0] if types else "", types[1] if len(types) > 1 else ""


def parse_table(table_html):
    # Keep full cell tags so we can read rowspan attributes
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)

    entries = []
    pending_nac  = None
    pending_lum  = None
    pending_name = None  # set when the name cell itself has rowspan

    for row in rows:
        # Capture (opening_tag, inner_content) for each cell
        cells = re.findall(r'(<t[dh][^>]*>)(.*?)</t[dh]>', row, re.DOTALL)
        if not cells:
            continue

        n = len(cells)
        first_content = cell_text(cells[0][1])

        if re.match(r'^\d+$', first_content) and n >= 4:
            # Normal row: has national number and dex number
            nac = first_content
            lum = cell_text(cells[1][1])

            rowspan_match = re.search(r'rowspan="(\d+)"', cells[0][0])
            if rowspan_match and int(rowspan_match.group(1)) > 1:
                pending_nac, pending_lum = nac, lum
            else:
                pending_nac = pending_lum = pending_name = None

            # If the name cell also has rowspan, save it for upcoming variant rows
            name = cell_text(cells[3][1])
            name_rowspan = re.search(r'rowspan="(\d+)"', cells[3][0])
            pending_name = name if (name_rowspan and int(name_rowspan.group(1)) > 1) else None

            icon_url = get_icon_url(cells[2][1])
            tipo1, tipo2 = get_types([c[1] for c in cells[3:]])

            entries.append({
                "nac": nac, "dex_num": lum, "name": name,
                "tipo1": tipo1, "tipo2": tipo2 or "", "icon_url": icon_url,
            })

        elif n <= 4 and pending_nac:
            # Variant row: national/dex numbers come from the rowspan above
            icon_url = get_icon_url(cells[0][1])

            if n >= 3 and 'alt="Tipo ' not in cells[1][1]:
                # [icon, name, type] — e.g. Raichu de Alola
                name = cell_text(cells[1][1])
                tipo1, tipo2 = get_types([c[1] for c in cells[1:]])
            else:
                # [icon, type] or [icon, type1, type2] — name lives in the icon alt
                name = get_icon_name(cells[0][1]) or pending_name
                tipo1, tipo2 = get_types([c[1] for c in cells])

            entries.append({
                "nac": pending_nac, "dex_num": pending_lum, "name": name,
                "tipo1": tipo1, "tipo2": tipo2 or "", "icon_url": icon_url,
            })

    return entries


def parse_all_tables(html):
    tables = re.findall(
        r'<table class="sortable tabpokemon"[^>]*>(.*?)</table>',
        html, re.DOTALL
    )
    return [parse_table(t) for t in tables]


def main():
    print("Downloading page...")
    html = download(SOURCE_URL).decode("utf-8")

    print("Parsing tables...")
    all_entries = parse_all_tables(html)
    if len(all_entries) < 2:
        print(f"Error: expected 2 tables, found {len(all_entries)}.")
        return

    luminalia, dimensional = all_entries[0], all_entries[1]
    print(f"  Luminalia:   {len(luminalia)} entries (including variants)")
    print(f"  Dimensional: {len(dimensional)} entries (including variants)")

    data = {
        "game": {
            "slug": "legends-za",
            "name": "Pokémon Legends: Z-A",
            "year": 2025,
        },
        "dexes": [
            {
                "slug":      "luminalia",
                "name":      "Pokédex de Ciudad Luminalia",
                "col_label": "LUM",
                "pokemon":   luminalia,
            },
            {
                "slug":      "dimensional",
                "name":      "Pokédex Dimensional",
                "col_label": "DIM",
                "pokemon":   dimensional,
            },
        ],
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
