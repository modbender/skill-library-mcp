from pathlib import Path

import orjson


def save_checkpoint(path: Path, queue, seen):
    path.write_bytes(orjson.dumps({"queue": list(queue), "seen": list(seen)}))


def load_checkpoint(path: Path):
    if not path.exists():
        return None, None
    try:
        data = orjson.loads(path.read_bytes())
    except Exception:
        return None, None
    return data.get("queue", []), set(data.get("seen", []))
