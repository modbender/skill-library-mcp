import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_PATH = os.path.expanduser("~/.openclaw/secrets/health_tokens.json")


def _path() -> Path:
    return Path(os.getenv("OPENCLAW_LOCAL_SECRETS_PATH") or DEFAULT_PATH)


def _read() -> Dict[str, Any]:
    p = _path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text()) if p.read_text().strip() else {}
    except Exception:
        return {}


def get_local_secret(namespace: str, key: str) -> Optional[str]:
    """Read a secret value from a local JSON file.

    Format:
      {
        "whoop": {"refresh_token": "...", "access_token": "..."},
        "withings": {"refresh_token": "..."}
      }

    Returns None if missing.
    """

    data = _read()
    ns = data.get(namespace) if isinstance(data, dict) else None
    if not isinstance(ns, dict):
        return None
    v = ns.get(key)
    return v if isinstance(v, str) and v.strip() else None


def set_local_secret(namespace: str, key: str, value: str) -> bool:
    """Atomically write a secret value to the local JSON file.

    This is intended for rotated refresh tokens when 1Password writeback is not available.

    Returns True on success.
    """

    try:
        p = _path()
        p.parent.mkdir(parents=True, exist_ok=True)
        data = _read()
        if not isinstance(data, dict):
            data = {}
        ns = data.get(namespace)
        if not isinstance(ns, dict):
            ns = {}
        ns[key] = value
        data[namespace] = ns

        # Atomic write
        tmp_dir = str(p.parent)
        fd, tmp_path = tempfile.mkstemp(prefix=p.name + ".", dir=tmp_dir)
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2, sort_keys=True)
                f.write("\n")
            os.replace(tmp_path, p)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

        # Best-effort permissions hardening
        try:
            os.chmod(p, 0o600)
        except Exception:
            pass

        return True
    except Exception:
        return False
