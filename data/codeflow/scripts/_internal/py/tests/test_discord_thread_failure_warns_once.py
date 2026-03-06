import importlib
import os
import sys
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


class DiscordThreadFailureWarnsOnceTests(unittest.TestCase):
    def setUp(self):
        self._env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)

    def test_thread_creation_failure_warns_once_and_disables_retries(self):
        os.environ["WEBHOOK_URL"] = "https://example.invalid/webhook"
        os.environ["THREAD_MODE"] = "true"
        os.environ["BOT_TOKEN"] = "bot-token"
        os.environ.pop("CODEFLOW_DISCORD_ALLOW_MENTIONS", None)

        from platforms import discord as dc

        dc = importlib.reload(dc)

        calls: list[tuple[str, dict, object]] = []

        def fake_http_post_json(url: str, payload: dict, headers=None) -> dict:
            calls.append((url, payload, headers))
            if "wait=true" in url:
                return {"id": "m1", "channel_id": "c1"}
            if url.endswith("/threads") or "/threads" in url:
                dc.DELIVERY_STATS["last_error"] = "HTTP 403"
                return {}
            return {}

        dc._http_post_json = fake_http_post_json

        dc.post("hello", name="Agent")

        self.assertEqual(sum("wait=true" in u for u, _, _ in calls), 1)
        warns = [
            p
            for _, p, _ in calls
            if isinstance(p, dict) and str(p.get("content") or "").startswith("⚠️ Codeflow:")
        ]
        self.assertEqual(len(warns), 1)

        calls.clear()
        dc.post("hello2", name="Agent")
        self.assertEqual(sum("wait=true" in u for u, _, _ in calls), 0)
        warns2 = [
            p
            for _, p, _ in calls
            if isinstance(p, dict) and str(p.get("content") or "").startswith("⚠️ Codeflow:")
        ]
        self.assertEqual(len(warns2), 0)


if __name__ == "__main__":
    unittest.main()

