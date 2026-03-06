#!/usr/bin/env python3
"""
seen_store.py - Historique des URLs deja presentees dans les digests veille.

Maintient un store JSON local :
  - seen_urls.json : URLs d'articles (TTL 14j)

Structure JSON : { "https://...": "2026-02-24T07:12:34" }

Usage (import) :
    from seen_store import veille_seen_store

    # Filtre avant presentation
    articles, skipped = veille_seen_store.filter_unseen(articles, key_fn=lambda a: a["url"])

    # Marque apres presentation
    veille_seen_store.mark_seen([a["url"] for a in selected])
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# ---- Paths ------------------------------------------------------------------

SKILL_DIR   = Path(__file__).resolve().parent.parent
_DATA_DIR   = Path.home() / ".openclaw" / "data" / "veille"
SEEN_URL_FILE = _DATA_DIR / "seen_urls.json"

# ---- Helpers ----------------------------------------------------------------


def _load(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _purge(data: dict, ttl_days: int) -> dict:
    """Supprime les entrees plus vieilles que ttl_days."""
    cutoff = (datetime.now() - timedelta(days=ttl_days)).isoformat()
    return {k: v for k, v in data.items() if v >= cutoff}


# ---- SeenStore --------------------------------------------------------------


class SeenStore:
    def __init__(self, path: Path, ttl_days: int = 14):
        self.path = path
        self.ttl_days = ttl_days
        self._data: dict | None = None
        # Ensure data directory exists
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _ensure_loaded(self):
        if self._data is None:
            raw = _load(self.path)
            self._data = _purge(raw, self.ttl_days)

    def is_seen(self, key: str) -> bool:
        self._ensure_loaded()
        return key in self._data

    def mark_seen(self, keys: list):
        """Enregistre les cles comme vues maintenant. Ecrit le fichier."""
        self._ensure_loaded()
        now = datetime.now().isoformat(timespec="seconds")
        for k in keys:
            if k:
                self._data[k] = now
        _save(self.path, self._data)

    def filter_unseen(self, items: list, key_fn) -> tuple:
        """
        Retourne (items_non_vus, nb_filtres).
        key_fn : callable(item) -> str (cle a tester dans le store)
        """
        self._ensure_loaded()
        unseen = [i for i in items if not self.is_seen(key_fn(i))]
        skipped = len(items) - len(unseen)
        return unseen, skipped

    def stats(self) -> dict:
        self._ensure_loaded()
        return {"total": len(self._data), "ttl_days": self.ttl_days, "file": str(self.path)}


# ---- Shared instance --------------------------------------------------------

veille_seen_store = SeenStore(SEEN_URL_FILE, ttl_days=14)


# ---- CLI minimal (debug) ----------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Inspecte le store seen URLs")
    parser.add_argument("--list", action="store_true", help="Liste toutes les entrees")
    args = parser.parse_args()

    s = veille_seen_store.stats()
    print(f"Store : {s['file']}")
    print(f"TTL   : {s['ttl_days']} jours")
    print(f"Total : {s['total']} entrees")
    if args.list:
        veille_seen_store._ensure_loaded()
        for k, v in sorted(veille_seen_store._data.items(), key=lambda x: x[1], reverse=True):
            print(f"  {v}  {k}")
