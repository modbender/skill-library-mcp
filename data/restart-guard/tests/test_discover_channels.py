import json
import os
import tempfile
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in os.sys.path:
    os.sys.path.insert(0, SCRIPT_DIR)

import discover_channels  # noqa: E402


class DiscoverChannelsTests(unittest.TestCase):
    def test_discovers_openclaw_and_notification_channels(self):
        with tempfile.TemporaryDirectory() as td:
            oc_path = os.path.join(td, "openclaw.json")
            with open(oc_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "channels": {
                            "telegram": {"enabled": True, "allowFrom": ["726647436"]},
                            "feishu": {"enabled": True},
                            "disabled_ch": {"enabled": False},
                        },
                        "bindings": [{"agentId": "main", "match": {"channel": "telegram"}}],
                    },
                    f,
                    ensure_ascii=False,
                )

            cfg = {
                "paths": {"openclaw_config": oc_path},
                "notification": {
                    "channels": ["telegram", "webhook", "feishu"],
                    "fallback": "slack",
                    "primary": "openclaw",
                    "openclaw": {"channel": "telegram", "target": "726647436"},
                },
            }
            payload = discover_channels.discover_channels(cfg)

        ids = [item.get("id") for item in payload.get("choices", [])]
        self.assertIn("webui", ids)
        self.assertIn("telegram", ids)
        self.assertIn("feishu", ids)
        self.assertIn("webhook", ids)
        self.assertIn("slack", ids)
        self.assertEqual(len(ids), len(set(ids)))

        external = payload.get("externalChannels", [])
        self.assertIn("telegram", external)
        self.assertIn("feishu", external)
        self.assertIn("webhook", external)
        self.assertIn("slack", external)


if __name__ == "__main__":
    unittest.main()
