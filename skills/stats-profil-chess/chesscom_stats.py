#!/usr/bin/env python3
import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_URL = "https://api.chess.com/pub/player/{username}/stats"

def to_date(ts: int | None) -> str:
    if not ts:
        return "N/A"
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")

def safe_get(d: dict, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def print_mode(title: str, block: dict):
    if not isinstance(block, dict):
        return

    last_rating = safe_get(block, "last", "rating")
    best_rating = safe_get(block, "best", "rating")
    best_date = to_date(safe_get(block, "best", "date"))
    rec = safe_get(block, "record") or {}

    win = rec.get("win", "N/A")
    loss = rec.get("loss", "N/A")
    draw = rec.get("draw", "N/A")
    last_date = to_date(safe_get(block, "last", "date"))

    if last_rating is None and best_rating is None and not rec:
        return

    print(f"\n{title}")
    print(f"- Rating actuel : {last_rating if last_rating is not None else 'N/A'} (last: {last_date})")
    print(f"- Best          : {best_rating if best_rating is not None else 'N/A'} (date: {best_date})")
    print(f"- Record        : W {win} / L {loss} / D {draw}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 chesscom_stats.py <username>", file=sys.stderr)
        sys.exit(2)

    username = sys.argv[1].strip()
    if not username or not re.fullmatch(r"[A-Za-z0-9_-]+", username):
        print("Erreur: username invalide (lettres/chiffres/_- uniquement).", file=sys.stderr)
        sys.exit(2)

    url = API_URL.format(username=username.lower())
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "openclaw-skill-chesscom-stats/1.0 (contact: you@example.com)"
        },
        method="GET"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Erreur 404: joueur '{username}' introuvable (ou profil non public).", file=sys.stderr)
            sys.exit(4)
        print(f"HTTP error {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Erreur réseau/parsing: {e}", file=sys.stderr)
        sys.exit(3)

    print(f"Stats Chess.com — {username}")

    # Modes principaux
    print_mode("Rapid", data.get("chess_rapid"))
    print_mode("Blitz", data.get("chess_blitz"))
    print_mode("Bullet", data.get("chess_bullet"))

    # Puzzles
    puzzles = data.get("tactics")
    if isinstance(puzzles, dict):
        print("\nPuzzles")
        print(f"- Rating actuel : {safe_get(puzzles, 'highest', 'rating', default='N/A') if safe_get(puzzles,'highest','rating') is None else safe_get(puzzles,'highest','rating')}")
        # La structure tactics varie parfois; on affiche ce qu'on trouve
        last = safe_get(puzzles, "lowest", "rating")
        highest = safe_get(puzzles, "highest", "rating")
        if highest is not None:
            print(f"- Best          : {highest}")
        if last is not None:
            print(f"- Lowest        : {last}")

    # (Optionnel) Pour debug: afficher un extrait du JSON
    # print("\n--- JSON brut (debug) ---")
    # print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()