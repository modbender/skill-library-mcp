# Card data loading: read from data/cards.json (exported from tarot_game)

import json
import random
from pathlib import Path
from typing import List, Optional, Union

from .types import Card

_PACKAGE_DIR = Path(__file__).resolve().parent
_DEFAULT_CARDS_PATH = _PACKAGE_DIR.parent / "data" / "cards.json"

_all_cards: Optional[List[Card]] = None


def load_cards(path: Optional[Union[Path, str]] = None) -> List[Card]:
    """Load 78 cards; path defaults to data/cards.json (run export script from tarot_game first)."""
    global _all_cards
    if _all_cards is not None:
        return _all_cards
    p = Path(path) if path else _DEFAULT_CARDS_PATH
    if not p.exists():
        raise FileNotFoundError(
            f"Card data file not found: {p}\n"
            "Run first: npm run export-cards or npx tsx scripts/export_cards_from_tarot_game.ts\n"
            "(from repo root with tarot_game alongside)"
        )
    with open(p, "r", encoding="utf-8") as f:
        _all_cards = json.load(f)
    return _all_cards


def draw_cards(deck: List[Card], n: int) -> List[Card]:
    """Draw n cards from deck without replacement."""
    copy = list(deck)
    out: List[Card] = []
    for _ in range(min(n, len(copy))):
        idx = random.randint(0, len(copy) - 1)
        out.append(copy.pop(idx))
    return out
