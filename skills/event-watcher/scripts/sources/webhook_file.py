from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple


def read_events(path: str, offset: int, max_lines: int) -> Tuple[List[Dict], int]:
    if not os.path.exists(path):
        return [], offset
    events: List[Dict] = []
    with open(path, "r") as f:
        f.seek(offset)
        for _ in range(max_lines):
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except Exception:
                continue
        new_offset = f.tell()
    return events, new_offset
