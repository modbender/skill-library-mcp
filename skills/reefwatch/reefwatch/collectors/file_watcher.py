"""
reefwatch.collectors.file_watcher
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Monitors critical paths for changes using polling (cross-platform).
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from reefwatch._common import expand, get_os_key, logger


class FileWatcher:
    """Monitors critical paths for changes using polling (cross-platform)."""

    def __init__(self, config: dict):
        self.enabled = (
            config.get("collectors", {}).get("files", {}).get("enabled", True)
        )
        paths_cfg = config.get("collectors", {}).get("files", {}).get("watched_paths", {})
        os_key = get_os_key()
        raw_paths = paths_cfg.get("common", []) + paths_cfg.get(os_key, [])
        self.watched_paths = [expand(p) for p in raw_paths]
        self.scan_extensions = set(
            config.get("collectors", {}).get("files", {}).get("scan_extensions", [])
        )
        # Files smaller than this threshold get SHA256 integrity checks
        self.hash_threshold = (
            config.get("collectors", {}).get("files", {}).get("hash_threshold_kb", 512)
            * 1024
        )
        self._snapshots: dict[str, tuple[float, int, str]] = {}  # path -> (mtime, size, hash)
        self._dir_mtimes: dict[str, float] = {}  # dir path -> last known mtime
        self._take_snapshot()
        logger.info(f"FileWatcher initialized: {len(self.watched_paths)} paths")

    @staticmethod
    def _hash_file(path: Path, max_bytes: int) -> str:
        """Compute SHA256 for files under the size threshold, else return empty."""
        try:
            if path.is_symlink() or path.stat().st_size > max_bytes:
                return ""
            h = hashlib.sha256()
            with open(path, "rb") as fh:
                for chunk in iter(lambda: fh.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def _take_snapshot(self):
        for wp in self.watched_paths:
            if not wp.exists() or wp.is_symlink():
                continue
            if wp.is_file():
                try:
                    st = wp.stat()
                    file_hash = self._hash_file(wp, self.hash_threshold)
                    self._snapshots[str(wp)] = (st.st_mtime, st.st_size, file_hash)
                except Exception as e:
                    logger.debug(f"Cannot stat {wp}: {e}")
            else:
                self._scan_directory(wp, self._snapshots, force=True)

    def _scan_directory(self, d: Path, current: dict, force: bool = False):
        """Scan a directory, skipping iterdir() on unchanged directories."""
        try:
            dir_mtime = d.stat().st_mtime
        except Exception:
            return

        cached = self._dir_mtimes.get(str(d))
        self._dir_mtimes[str(d)] = dir_mtime

        if not force and cached is not None and dir_mtime == cached:
            # Dir structure unchanged (no creates/deletes) — skip iterdir().
            # Re-stat known files to detect content modifications.
            # Compare Path objects to avoid trailing-slash mismatches.
            for path in list(self._snapshots.keys()):
                p = Path(path)
                if p.parent != d:
                    continue
                if p.is_file():
                    try:
                        st = p.stat()
                        fh = self._hash_file(p, self.hash_threshold)
                        current[path] = (st.st_mtime, st.st_size, fh)
                    except Exception:
                        pass  # File deleted — will appear as deletion
            # Recurse into known subdirectories
            for sub_d in list(self._dir_mtimes.keys()):
                sub_p = Path(sub_d)
                if sub_p.parent == d and sub_p.is_dir():
                    self._scan_directory(sub_p, current)
            return

        try:
            children = list(d.iterdir())
        except (PermissionError, OSError) as e:
            logger.debug(f"Cannot iterate {d}: {e}")
            return
        for child in children:
            if child.is_symlink():
                continue
            if child.is_file():
                try:
                    st = child.stat()
                    file_hash = self._hash_file(child, self.hash_threshold)
                    current[str(child)] = (st.st_mtime, st.st_size, file_hash)
                except Exception as e:
                    logger.debug(f"Cannot stat {child}: {e}")
            elif child.is_dir():
                self._scan_directory(child, current)

    def check_changes(self) -> list[dict]:
        """Returns list of changed/new/deleted files."""
        changes = []
        current: dict[str, tuple[float, int, str]] = {}

        for wp in self.watched_paths:
            if not wp.exists() or wp.is_symlink():
                continue
            if wp.is_file():
                try:
                    st = wp.stat()
                    file_hash = self._hash_file(wp, self.hash_threshold)
                    current[str(wp)] = (st.st_mtime, st.st_size, file_hash)
                except Exception as e:
                    logger.debug(f"Cannot stat {wp}: {e}")
            else:
                self._scan_directory(wp, current)

        # New or modified files
        for path, (mtime, size, fhash) in current.items():
            old = self._snapshots.get(path)
            if old is None:
                changes.append(
                    {
                        "type": "file_created",
                        "path": path,
                        "size": size,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
            elif old != (mtime, size, fhash):
                change_type = "file_modified"
                severity_bump = False
                # Hash mismatch on a hashed file = integrity violation
                if old[2] and fhash and old[2] != fhash:
                    change_type = "file_integrity_violation"
                    severity_bump = True

                change = {
                    "type": change_type,
                    "path": path,
                    "old_size": old[1],
                    "new_size": size,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                if severity_bump:
                    change["integrity"] = True
                changes.append(change)

        # Deleted files
        for path in set(self._snapshots.keys()) - set(current.keys()):
            changes.append(
                {
                    "type": "file_deleted",
                    "path": path,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        self._snapshots = current
        # Prune stale directory mtimes
        self._dir_mtimes = {
            d: mt for d, mt in self._dir_mtimes.items()
            if Path(d).exists()
        }
        return changes
