#!/usr/bin/env python3
"""
Scraper for Pokémon Legends: Arceus (WikiDex).
Downloads the Hisui Pokédex including regional variants and alternate forms.
Output: backend/data/games/legends-arceus.json  (see scrapers/README.md)
"""

import json
import os
import re
import urllib.request


SOURCE_URL = "https://www.wikidex.net/wiki/Lista_de_Pok%C3%A9mon_seg%C3%BAn_la_Pok%C3%A9dex_de_Hisui"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "backend", "data", "games", "legends-arceus.json")


def download(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (compatible; PokédexScraper/1.0)"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read()


def get_all_icons(cell_html):
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


def parse_table(table_html):
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)

    entries = []
    pending_nac  = None
    pending_his  = None
    pending_name = None

    for row in rows:
        cells = re.findall(r'(<t[dh][^>]*>)(.*?)</t[dh]>', row, re.DOTALL)
        if not cells:
            continue

        n = len(cells)
        first_content = cell_text(cells[0][1])

        if re.match(r'^\d+$', first_content) and n >= 4:
            nac = first_content
            his = cell_text(cells[1][1])

            rowspan_match = re.search(r'rowspan="(\d+)"', cells[0][0])
            if rowspan_match and int(rowspan_match.group(1)) > 1:
                pending_nac, pending_his = nac, his
            else:
                pending_nac = pending_his = pending_name = None

            name = cell_text(cells[3][1])
            name_rowspan = re.search(r'rowspan="(\d+)"', cells[3][0])
            pending_name = name if (name_rowspan and int(name_rowspan.group(1)) > 1) else None

            tipo1, tipo2 = get_types([c[1] for c in cells[3:]])
            icons = get_all_icons(cells[2][1])

            if len(icons) > 1:
                for form_name, icon_url in icons:
                    entries.append({
                        "nac": nac, "dex_num": his,
                        "name": form_name or name,
                        "tipo1": tipo1, "tipo2": tipo2 or "", "icon_url": icon_url,
                    })
            else:
                icon_url = icons[0][1] if icons else None
                entries.append({
                    "nac": nac, "dex_num": his, "name": name,
                    "tipo1": tipo1, "tipo2": tipo2 or "", "icon_url": icon_url,
                })

        elif n <= 4 and pending_nac:
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
                        "nac": pending_nac, "dex_num": pending_his,
                        "name": form_name or name,
                        "tipo1": tipo1, "tipo2": tipo2 or "", "icon_url": icon_url,
                    })
            else:
                icon_url = icons[0][1] if icons else None
                entries.append({
                    "nac": pending_nac, "dex_num": pending_his, "name": name,
                    "tipo1": tipo1, "tipo2": tipo2 or "", "icon_url": icon_url,
                })

    return [e for e in entries if not e['name'].startswith('Tipo ')]


def main():
    print("Downloading page...")
    html = download(SOURCE_URL).decode("utf-8")

    print("Parsing table...")
    tables = re.findall(
        r'<table class="sortable tabpokemon"[^>]*>(.*?)</table>',
        html, re.DOTALL
    )
    if not tables:
        print("Error: table not found.")
        return

    hisui = parse_table(tables[0])
    print(f"  Hisui: {len(hisui)} entries (including variants)")

    data = {
        "game": {
            "slug": "legends-arceus",
            "name": "Pokémon Legends: Arceus",
            "year": 2022,
        },
        "dexes": [
            {
                "slug":      "hisui",
                "name":      "Pokédex de Hisui",
                "col_label": "HIS",
                "pokemon":   hisui,
            },
        ],
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
