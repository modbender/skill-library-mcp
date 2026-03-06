"""
Tests for discover, backup, and migrate.
Uses a temporary directory with fake moltbot/clawdbot layout.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure package is importable when run from repo root (parent of clawd_migrate)
_repo_root = Path(__file__).resolve().parent.parent
_parent = _repo_root.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

from clawd_migrate import discover_source_assets, create_backup, run_migration, verify_migration
from clawd_migrate.config import (
    OPENCLAW_MEMORY_DIR,
    OPENCLAW_CONFIG_DIR,
    OPENCLAW_CLAWDBOOK_DIR,
)


def make_fake_source(root: Path) -> None:
    """Create a fake source layout (memory, config, clawdbook, extra)."""
    (root / "SOUL.md").write_text("soul", encoding="utf-8")
    (root / "USER.md").write_text("user", encoding="utf-8")
    (root / "TOOLS.md").write_text("tools", encoding="utf-8")
    (root / ".config" / "moltbook").mkdir(parents=True)
    (root / ".config" / "moltbook" / "credentials.json").write_text(
        '{"key":"x"}', encoding="utf-8"
    )
    (root / "projects").mkdir(parents=True)
    (root / "projects" / "readme.txt").write_text("project", encoding="utf-8")


class TestDiscover(unittest.TestCase):
    def test_discover_finds_memory_config_extra(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fake_source(root)

            assets = discover_source_assets(root)

            self.assertEqual(assets["root"], str(root))
            self.assertGreaterEqual(len(assets["memory"]), 3)
            memory_names = [Path(p).name for p in assets["memory"]]
            self.assertIn("SOUL.md", memory_names)
            self.assertIn("USER.md", memory_names)
            self.assertIn("TOOLS.md", memory_names)

            self.assertGreater(len(assets["config"]), 0)
            self.assertGreater(len(assets["clawdbook"]), 0)
            self.assertGreater(len(assets["extra"]), 0)
            self.assertTrue(
                any("projects" in p for p in assets["extra"]),
                "extra should include projects/",
            )


class TestBackup(unittest.TestCase):
    def test_backup_creates_dir_and_copies_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fake_source(root)

            backup_path = create_backup(root=root)

            self.assertTrue(backup_path.is_dir())
            self.assertTrue((backup_path / "SOUL.md").is_file())
            self.assertTrue((backup_path / "USER.md").is_file())
            self.assertTrue((backup_path / ".config" / "moltbook" / "credentials.json").is_file())
            self.assertTrue((backup_path / "projects" / "readme.txt").is_file())
            self.assertTrue((backup_path / "_manifest.txt").is_file())


class TestMigrate(unittest.TestCase):
    def test_migrate_creates_openclaw_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fake_source(root)

            result = run_migration(root=root, backup_first=True, output_root=root)

            self.assertIsNotNone(result["backup_path"])
            self.assertEqual(result["errors"], [])

            memory_dir = root / OPENCLAW_MEMORY_DIR
            config_dir = root / OPENCLAW_CONFIG_DIR
            clawdbook_dir = root / OPENCLAW_CLAWDBOOK_DIR

            self.assertTrue(memory_dir.is_dir(), "memory/ should exist")
            self.assertTrue(config_dir.is_dir(), ".config/openclaw should exist")
            self.assertTrue(clawdbook_dir.is_dir(), ".config/clawdbook should exist")

            self.assertTrue((memory_dir / "SOUL.md").is_file())
            self.assertTrue((memory_dir / "USER.md").is_file())
            self.assertTrue((memory_dir / "TOOLS.md").is_file())

            self.assertGreater(len(result["memory_copied"]), 0)
            self.assertGreater(len(result["clawdbook_copied"]), 0)

            projects_dir = root / "projects"
            self.assertTrue(projects_dir.is_dir())
            self.assertTrue((projects_dir / "readme.txt").is_file())


class TestVerify(unittest.TestCase):
    def test_verify_passes_after_migration(self):
        """Verification should pass when all files are migrated."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fake_source(root)

            result = run_migration(root=root, backup_first=True, output_root=root, verify=True)

            self.assertEqual(result["errors"], [])
            verification = result["verification"]
            self.assertIsNotNone(verification)
            self.assertTrue(verification["passed"], "Verification should pass after successful migration")
            self.assertEqual(verification["total_expected"], verification["total_verified"])
            self.assertEqual(len(verification["missing"]), 0)

    def test_verify_detects_missing_files(self):
        """Verification should detect missing files after a partial migration."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fake_source(root)

            # Run migration without verification first
            result = run_migration(root=root, backup_first=False, output_root=root, verify=False)
            self.assertEqual(result["errors"], [])

            # Remove one of the migrated memory files
            memory_dir = root / OPENCLAW_MEMORY_DIR
            soul_dest = memory_dir / "SOUL.md"
            if soul_dest.is_file():
                soul_dest.unlink()

            # Now verify - should detect the missing file
            verification = verify_migration(root=root, output_root=root)
            self.assertFalse(verification["passed"], "Verification should fail when a file is missing")
            self.assertGreater(len(verification["missing"]), 0)
            missing_names = [Path(m["source"]).name for m in verification["missing"]]
            self.assertIn("SOUL.md", missing_names)

    def test_verify_standalone(self):
        """Verification can run independently of migration."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fake_source(root)

            # Before migration: verification should fail (no openclaw dirs)
            verification = verify_migration(root=root, output_root=root)
            self.assertFalse(verification["passed"], "Verification should fail before migration")

            # After migration: verification should pass
            run_migration(root=root, backup_first=False, output_root=root, verify=False)
            verification = verify_migration(root=root, output_root=root)
            self.assertTrue(verification["passed"], "Verification should pass after migration")


if __name__ == "__main__":
    unittest.main()
