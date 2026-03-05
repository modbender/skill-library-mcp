from __future__ import annotations

from pathlib import Path


def resolve_db_path(profile: str | None, *, data_dir: str | Path | None = None) -> str:
    """Resolve sqlite DB path for a given profile.

    Profiles:
    - work (default)
    - family

    data_dir defaults to ~/.openclaw/data/workcrm
    """

    p = (profile or "work").strip().lower() or "work"
    if p not in {"work", "family"}:
        raise ValueError(f"unknown profile: {profile}")

    base = Path(data_dir).expanduser() if data_dir is not None else Path.home() / ".openclaw" / "data" / "workcrm"
    base.mkdir(parents=True, exist_ok=True)

    fname = "workcrm_work.sqlite" if p == "work" else "workcrm_family.sqlite"
    return str(base / fname)
