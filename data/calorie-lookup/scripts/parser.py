from dataclasses import dataclass
from typing import List, Optional
import re
from units import AMOUNT_RE, normalize_unit

SPLIT_RE = re.compile(r"[+\n,，;；]|(?:\s+and\s+)|(?:\s*\+\s*)")

@dataclass
class ParsedItem:
    name: str
    qty: Optional[float] = None
    unit: Optional[str] = None

def split_items(text: str) -> List[str]:
    parts = [p.strip() for p in SPLIT_RE.split(text) if p and p.strip()]
    return parts

def parse_one(part: str) -> ParsedItem:
    m = AMOUNT_RE.search(part)
    if not m:
        return ParsedItem(name=part.strip())

    qty = float(m.group("qty"))
    unit = normalize_unit(m.group("unit"))
    name = (part[:m.start()] + part[m.end():]).strip()
    if not name:
        name = part[:m.start()].strip() or part[m.end():].strip() or part.strip()
    return ParsedItem(name=name, qty=qty, unit=unit)

def parse_meal_text(text: str) -> List[ParsedItem]:
    return [parse_one(p) for p in split_items(text)]
