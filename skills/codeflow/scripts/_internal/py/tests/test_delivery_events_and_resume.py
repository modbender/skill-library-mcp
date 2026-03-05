import io
import json
import os
import subprocess
import sys
import tempfile
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from delivery_errors import DeliveryRateLimited
from delivery_governor import DeliveryGovernor

PARSER = os.path.join(SCRIPT_DIR, "parse-stream.py")


class _FakeClock:
    def __init__(self):
        self.t = 0.0
        self.sleeps: list[float] = []

    def now(self) -> float:
        return float(self.t)

    def sleep(self, seconds: float) -> None:
        sec = float(seconds)
        self.sleeps.append(sec)
        self.t += sec


class _RateLimitOncePlatform:
    MAX_TEXT = 50
    SUPPORTS_EDIT = True

    def __init__(self, *, retry_after: float):
        self.retry_after = float(retry_after)
        self.calls: list[tuple[str, str]] = []
        self._rate_limit_next = True

    def post_single_governed(self, text: str, name=None) -> int:
        self.calls.append(("post_single", text))
        if self._rate_limit_next:
            self._rate_limit_next = False
            raise DeliveryRateLimited(
                platform="telegram",
                op="post_single",
                code=429,
                retry_after=self.retry_after,
                reason="Too Many Requests",
            )
        return 1

    def edit_single_governed(self, message_id: int, text: str) -> bool:
        self.calls.append(("edit_single", text))
        return True


class DeliveryEventsAndResumeTests(unittest.TestCase):
    def test_delivery_events_written_to_stream_jsonl(self):
        clock = _FakeClock()
        plat = _RateLimitOncePlatform(retry_after=7.0)
        stats: dict = {}

        with tempfile.TemporaryDirectory() as td:
            stream_path = os.path.join(td, "stream.jsonl")
            with open(stream_path, "a", encoding="utf-8") as f:
                gov = DeliveryGovernor(
                    plat,
                    platform_name="telegram",
                    stream_log=f,
                    delivery_stats=stats,
                    clock=clock.now,
                    sleeper=clock.sleep,
                )
                gov.submit_final("FINAL")
                gov.tick(max_ops=1)  # 429 -> write events

            with open(stream_path, "r", encoding="utf-8") as rf:
                raw = rf.read().strip().splitlines()
            self.assertGreaterEqual(len(raw), 2)
            events = [json.loads(line) for line in raw]

            types = {e.get("type") for e in events}
            self.assertIn("codeflow.delivery.rate_limited", types)
            self.assertIn("codeflow.delivery.retry_scheduled", types)

            for e in events:
                # Meta only: no message bodies.
                self.assertNotIn("text", e)
                self.assertTrue(str(e.get("type", "")).startswith("codeflow.delivery."))
                self.assertIn("ts", e)
                self.assertIn("platform", e)
                self.assertIn("op", e)

    def test_resume_ignores_delivery_events_and_detects_codex_format(self):
        # First line is a delivery event; format detection must ignore it.
        stream_lines = [
            {
                "ts": "2026-02-27T00:00:00Z",
                "type": "codeflow.delivery.rate_limited",
                "platform": "telegram",
                "op": "post_single",
                "code": 429,
                "retry_after": 3,
                "attempt": 0,
                "reason": "Too Many Requests",
            },
            {"type": "thread.started", "thread_id": "t123"},
            {"type": "turn.started"},
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2},
            },
        ]
        inp = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in stream_lines)

        env = dict(os.environ)
        env["PLATFORM"] = "test"
        env["CODEFLOW_SAFE_MODE"] = "false"
        env["CODEFLOW_OUTPUT_MODE"] = "minimal"
        env["REPLAY_MODE"] = "true"
        env.pop("RELAY_DIR", None)

        proc = subprocess.run(
            ["python3", PARSER],
            input=inp,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)

        posts: list[str] = []
        for line in proc.stdout.splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("op") == "post":
                posts.append(obj.get("text", ""))

        joined = "\n".join(posts)
        self.assertIn("✅ Round", joined)


if __name__ == "__main__":
    unittest.main()
