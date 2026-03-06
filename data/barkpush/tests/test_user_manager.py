import json
import tempfile
import unittest
from pathlib import Path

from bark_push.config_manager import ConfigManager
from bark_push.user_manager import UserManager, UserError


class TestUserManager(unittest.TestCase):
    def test_resolve_all_requires_users(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            config_path = state_dir / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "default_push_url": "https://api.day.app",
                        "users": {},
                        "defaults": {"group": "default"},
                        "groups": ["default"],
                        "history_limit": 10,
                        "enable_update": True,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            mgr = ConfigManager(config_path=config_path, state_dir=state_dir)
            um = UserManager(mgr)
            with self.assertRaises(UserError):
                um.resolve("all")

    def test_resolve_multiple(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            config_path = state_dir / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "default_push_url": "https://api.day.app",
                        "users": {"alice": "k1", "bob": "k2"},
                        "defaults": {"group": "default"},
                        "groups": ["default"],
                        "history_limit": 10,
                        "enable_update": True,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            mgr = ConfigManager(config_path=config_path, state_dir=state_dir)
            um = UserManager(mgr)
            resolved = um.resolve("alice,bob")
            self.assertEqual(resolved.aliases, ["alice", "bob"])
            self.assertEqual(resolved.device_keys, ["k1", "k2"])

    def test_reject_device_key_input(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td)
            config_path = state_dir / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "default_push_url": "https://api.day.app",
                        "users": {"alice": "k1"},
                        "defaults": {"group": "default"},
                        "groups": ["default"],
                        "history_limit": 10,
                        "enable_update": True,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            mgr = ConfigManager(config_path=config_path, state_dir=state_dir)
            um = UserManager(mgr)
            with self.assertRaises(UserError):
                um.resolve("k1")


if __name__ == "__main__":
    unittest.main()
