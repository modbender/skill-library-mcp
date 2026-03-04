"""
_storage.py - Storage abstraction for the work-application skill.
Supports local filesystem and Nextcloud backends.

The backend is selected by the 'storage' config key:
    storage.backend = "local"     (default)
    storage.backend = "nextcloud"
    storage.path    = "/OpenClaw/work-application"  (Nextcloud remote path)

Config is always read/written locally (never on Nextcloud).

Usage:
    from _storage import get_storage
    store = get_storage()
    data = store.read_json("profile-master.json")
    store.write_json("profile.json", data)
    store.append_text("candidatures.md", new_row)
"""

import json
import posixpath
from pathlib import Path, PurePosixPath


# ---------------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------------

def _validate_name(name: str) -> str:
    """Validate a storage name against path traversal attacks.

    Rejects:
    - absolute paths (/etc/passwd, C:\\...)
    - traversal sequences (../, ..\\ or bare ..)
    - null bytes
    Allows subdirectories like "reports/report-acme-2026-01-01.md".

    Returns the sanitised name (forward slashes, no leading slash).
    """
    if not name or not isinstance(name, str):
        raise ValueError("Storage name must be a non-empty string")

    # Reject null bytes (can bypass checks on some OS)
    if "\x00" in name:
        raise ValueError(f"Invalid storage name (null byte): {name!r}")

    # Normalise to forward slashes
    name = name.replace("\\", "/")

    # Reject absolute paths (Unix and Windows-style)
    if name.startswith("/") or (len(name) >= 2 and name[1] == ":"):
        raise ValueError(f"Absolute paths are not allowed: {name!r}")

    # Reject any ".." component (covers ../, ..\, and bare "..")
    parts = PurePosixPath(name).parts
    if ".." in parts:
        raise ValueError(f"Path traversal detected: {name!r}")

    # Normalise (collapse redundant slashes, /./ etc.)
    clean = posixpath.normpath(name)
    # normpath might produce ".." if input was crafted - double check
    if clean.startswith("..") or "/.." in clean:
        raise ValueError(f"Path traversal detected: {name!r}")

    return clean


class StorageBackend:
    """Base class for storage backends."""

    def read_text(self, name: str) -> str:
        raise NotImplementedError

    def write_text(self, name: str, content: str) -> None:
        raise NotImplementedError

    def append_text(self, name: str, content: str) -> None:
        raise NotImplementedError

    def read_json(self, name: str) -> dict:
        raw = self.read_text(name)
        data = json.loads(raw)
        if not isinstance(data, (dict, list)):
            raise ValueError(f"Expected dict or list from {name}, got {type(data).__name__}")
        return data

    def write_json(self, name: str, data, indent: int = 2) -> None:
        self.write_text(name, json.dumps(data, indent=indent, ensure_ascii=False) + "\n")

    def exists(self, name: str) -> bool:
        raise NotImplementedError

    def ensure_dir(self) -> None:
        """Ensure the storage root exists (no-op for some backends)."""
        pass


class LocalStorage(StorageBackend):
    """Store files on the local filesystem."""

    def __init__(self, base_dir: Path):
        self._base = base_dir.resolve()

    def _path(self, name: str) -> Path:
        safe_name = _validate_name(name)
        target = (self._base / safe_name).resolve()
        # Final guard: resolved path must be inside base dir
        if not str(target).startswith(str(self._base)):
            raise ValueError(f"Path escapes storage directory: {name!r}")
        return target

    def read_text(self, name: str) -> str:
        return self._path(name).read_text(encoding="utf-8")

    def write_text(self, name: str, content: str) -> None:
        target = self._path(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def append_text(self, name: str, content: str) -> None:
        target = self._path(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as f:
            f.write(content)

    def exists(self, name: str) -> bool:
        return self._path(name).exists()

    def ensure_dir(self) -> None:
        self._base.mkdir(parents=True, exist_ok=True)


class NextcloudStorage(StorageBackend):
    """Store files on Nextcloud via the nextcloud skill's client."""

    def __init__(self, remote_path: str):
        self._remote = remote_path.rstrip("/")
        self._client = None

    def _nc(self):
        """Lazy-load the NextcloudClient to avoid import errors when not configured."""
        if self._client is None:
            import importlib.util
            # Find the nextcloud skill's client
            nc_script = (
                Path(__file__).resolve().parent.parent.parent
                / "nextcloud-files" / "scripts" / "nextcloud.py"
            )
            if not nc_script.exists():
                raise RuntimeError(
                    f"Nextcloud skill not found at {nc_script}\n"
                    "  Install it first: clawhub install nextcloud-files"
                )
            spec = importlib.util.spec_from_file_location("nextcloud", str(nc_script))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self._client = mod.NextcloudClient()
        return self._client

    def _rpath(self, name: str) -> str:
        safe_name = _validate_name(name)
        return f"{self._remote}/{safe_name}"

    def read_text(self, name: str) -> str:
        return self._nc().read_file(self._rpath(name))

    def write_text(self, name: str, content: str) -> None:
        self._nc().write_file(self._rpath(name), content)

    def append_text(self, name: str, content: str) -> None:
        self._nc().append_to_file(self._rpath(name), content)

    def read_json(self, name: str) -> dict:
        return self._nc().read_json(self._rpath(name))

    def write_json(self, name: str, data, indent: int = 2) -> None:
        self._nc().write_json(self._rpath(name), data, indent=indent)

    def exists(self, name: str) -> bool:
        return self._nc().exists(self._rpath(name))

    def ensure_dir(self) -> None:
        nc = self._nc()
        if not nc.exists(self._remote):
            nc.mkdir(self._remote)


# ── Factory ──────────────────────────────────────────────────────────────────

_DATA_DIR = Path.home() / ".openclaw" / "data" / "work-application"
_CONFIG_DIR = Path.home() / ".openclaw" / "config" / "work-application"
_CONFIG_FILE = _CONFIG_DIR / "config.json"

_instance = None


def get_storage(cfg: dict = None) -> StorageBackend:
    """Return the configured storage backend (cached)."""
    global _instance
    if _instance is not None:
        return _instance

    if cfg is None:
        if _CONFIG_FILE.exists():
            try:
                cfg = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
            except Exception:
                cfg = {}
        else:
            cfg = {}

    storage_cfg = cfg.get("storage", {})
    backend = storage_cfg.get("backend", "local")

    if backend == "nextcloud":
        remote_path = storage_cfg.get("path", "/OpenClaw/work-application")
        _instance = NextcloudStorage(remote_path)
    else:
        _instance = LocalStorage(_DATA_DIR)

    return _instance


def reset_storage() -> None:
    """Reset cached instance (useful after config change in setup)."""
    global _instance
    _instance = None
