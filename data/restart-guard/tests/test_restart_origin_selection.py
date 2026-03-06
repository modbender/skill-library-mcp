import os
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in os.sys.path:
    os.sys.path.insert(0, SCRIPT_DIR)

import restart  # noqa: E402


class RestartOriginSelectionTests(unittest.TestCase):
    def test_prefers_non_system_non_cron_latest(self):
        payload = {
            "sessions": {
                "recent": [
                    {
                        "key": "agent:main:cron:job-1",
                        "updatedAt": 100,
                        "flags": ["system"],
                    },
                    {
                        "key": "agent:main:main",
                        "updatedAt": 200,
                        "flags": ["system"],
                    },
                    {
                        "key": "agent:main:telegram:726647436",
                        "updatedAt": 300,
                        "flags": [],
                    },
                ]
            }
        }
        got = restart.select_origin_session_key_from_payload(payload)
        self.assertEqual(got, "agent:main:telegram:726647436")

    def test_falls_back_to_main_when_only_main_exists(self):
        payload = {
            "sessions": {
                "recent": [
                    {
                        "key": "agent:main:main",
                        "updatedAt": 200,
                        "flags": ["system"],
                    }
                ]
            }
        }
        got = restart.select_origin_session_key_from_payload(payload)
        self.assertEqual(got, "agent:main:main")

    def test_empty_payload_returns_empty(self):
        self.assertEqual(restart.select_origin_session_key_from_payload({}), "")

    def test_supports_agent_scoped_sessions_shape(self):
        payload = {
            "path": "/tmp/sessions.json",
            "count": 2,
            "sessions": [
                {"key": "agent:main:cron:job-x", "updatedAt": 999, "flags": ["system"]},
                {"key": "agent:main:main", "updatedAt": 1000, "flags": ["system"]},
            ],
        }
        got = restart.select_origin_session_key_from_payload(payload)
        self.assertEqual(got, "agent:main:main")


if __name__ == "__main__":
    unittest.main()
