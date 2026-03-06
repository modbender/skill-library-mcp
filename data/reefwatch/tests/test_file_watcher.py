"""Tests for FileWatcher collector."""

import hashlib
import time

from reefwatch.collectors.file_watcher import FileWatcher


def _make_config(tmp_path, watched=None, extensions=None, hash_kb=512):
    """Build a minimal config dict for FileWatcher."""
    return {
        "collectors": {
            "files": {
                "enabled": True,
                "watched_paths": {
                    "common": watched or [],
                    "linux": [],
                    "darwin": [],
                },
                "scan_extensions": extensions or [],
                "hash_threshold_kb": hash_kb,
            },
        },
    }


class TestFileWatcherBasic:
    def test_detects_new_file(self, tmp_path):
        watched = tmp_path / "data"
        watched.mkdir()
        config = _make_config(tmp_path, watched=[str(watched)])
        fw = FileWatcher(config)

        # Create a file after init
        (watched / "new.txt").write_text("hello")
        changes = fw.check_changes()

        types = [c["type"] for c in changes]
        assert "file_created" in types

    def test_detects_modified_file(self, tmp_path):
        watched = tmp_path / "data"
        watched.mkdir()
        f = watched / "file.txt"
        f.write_text("original")

        config = _make_config(tmp_path, watched=[str(watched)])
        fw = FileWatcher(config)

        time.sleep(0.01)
        f.write_text("modified content")
        changes = fw.check_changes()

        types = [c["type"] for c in changes]
        assert "file_modified" in types or "file_integrity_violation" in types

    def test_detects_deleted_file(self, tmp_path):
        watched = tmp_path / "data"
        watched.mkdir()
        f = watched / "file.txt"
        f.write_text("content")

        config = _make_config(tmp_path, watched=[str(watched)])
        fw = FileWatcher(config)

        f.unlink()
        changes = fw.check_changes()

        types = [c["type"] for c in changes]
        assert "file_deleted" in types

    def test_no_changes_on_stable_dir(self, tmp_path):
        watched = tmp_path / "data"
        watched.mkdir()
        (watched / "stable.txt").write_text("no change")

        config = _make_config(tmp_path, watched=[str(watched)])
        fw = FileWatcher(config)

        changes = fw.check_changes()
        assert changes == []


class TestSHA256Integrity:
    def test_hash_computed_for_small_files(self, tmp_path):
        watched = tmp_path / "data"
        watched.mkdir()
        f = watched / "small.txt"
        f.write_text("tiny file")

        config = _make_config(tmp_path, watched=[str(watched)], hash_kb=1)
        fw = FileWatcher(config)

        # Snapshot should have a hash
        snap = fw._snapshots.get(str(f))
        assert snap is not None
        assert snap[2] != ""  # hash present
        expected = hashlib.sha256(b"tiny file").hexdigest()
        assert snap[2] == expected

    def test_no_hash_for_large_files(self, tmp_path):
        watched = tmp_path / "data"
        watched.mkdir()
        f = watched / "big.bin"
        f.write_bytes(b"x" * 2048)

        # Threshold is 1 KB = 1024 bytes, file is 2048
        config = _make_config(tmp_path, watched=[str(watched)], hash_kb=1)
        fw = FileWatcher(config)

        snap = fw._snapshots.get(str(f))
        assert snap is not None
        assert snap[2] == ""  # no hash for large file

    def test_integrity_violation_on_hash_change(self, tmp_path):
        watched = tmp_path / "data"
        watched.mkdir()
        f = watched / "critical.conf"
        f.write_text("original content")

        config = _make_config(tmp_path, watched=[str(watched)], hash_kb=512)
        fw = FileWatcher(config)

        # Modify content (keep same mtime to simulate stealthy change)
        time.sleep(0.01)
        f.write_text("tampered content!")
        changes = fw.check_changes()

        violations = [c for c in changes if c["type"] == "file_integrity_violation"]
        assert len(violations) == 1
        assert violations[0]["integrity"] is True

    def test_hash_file_static_method(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("test data")
        result = FileWatcher._hash_file(f, 1024 * 1024)
        expected = hashlib.sha256(b"test data").hexdigest()
        assert result == expected

    def test_hash_file_returns_empty_on_missing(self, tmp_path):
        missing = tmp_path / "nonexistent"
        result = FileWatcher._hash_file(missing, 1024)
        assert result == ""


class TestDirMtimeCaching:
    def test_unchanged_dir_uses_cache(self, tmp_path):
        watched = tmp_path / "data"
        watched.mkdir()
        (watched / "file.txt").write_text("stable")

        config = _make_config(tmp_path, watched=[str(watched)])
        fw = FileWatcher(config)

        # First check — populates cache
        changes1 = fw.check_changes()
        assert changes1 == []

        # Second check — dir unchanged, should still return no changes
        changes2 = fw.check_changes()
        assert changes2 == []

    def test_stale_dir_pruned(self, tmp_path):
        watched = tmp_path / "data"
        watched.mkdir()
        sub = watched / "sub"
        sub.mkdir()
        (sub / "file.txt").write_text("in sub")

        config = _make_config(tmp_path, watched=[str(watched)])
        fw = FileWatcher(config)

        assert str(sub) in fw._dir_mtimes

        # Delete the subdirectory
        (sub / "file.txt").unlink()
        sub.rmdir()
        fw.check_changes()

        # Stale dir should be pruned
        assert str(sub) not in fw._dir_mtimes


class TestScanExtensions:
    def test_scan_extensions_stored(self, tmp_path):
        config = _make_config(tmp_path, extensions=[".py", ".sh"])
        fw = FileWatcher(config)
        assert fw.scan_extensions == {".py", ".sh"}

    def test_empty_scan_extensions(self, tmp_path):
        config = _make_config(tmp_path, extensions=[])
        fw = FileWatcher(config)
        assert fw.scan_extensions == set()
