import json
import os
import subprocess
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PARSER = os.path.join(SCRIPT_DIR, "parse-stream.py")


class DeliverySummaryIncludesExtraMetricsTests(unittest.TestCase):
    def test_summary_appends_drops_rate_limit_and_last_error_when_present(self):
        evt = {
            "type": "result",
            "is_error": False,
            "duration_ms": 1,
            "total_cost_usd": 0,
            "result": "ok",
            "num_turns": 1,
        }

        env = dict(os.environ)
        env.update(
            {
                "PLATFORM": "test",
                "CODEFLOW_SAFE_MODE": "false",
                "CODEFLOW_OUTPUT_MODE": "minimal",
                "CODEFLOW_TEST_DELIVERY_STATS": json.dumps(
                    {"drops": 2, "rate_limit_count": 5, "last_error": "HTTP 429"},
                    ensure_ascii=False,
                ),
            }
        )
        env.pop("RELAY_DIR", None)

        proc = subprocess.run(
            ["python3", PARSER],
            input=json.dumps(evt, ensure_ascii=False) + "\n",
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
        self.assertIn("Delivery:", joined)
        self.assertIn("drops=2", joined)
        self.assertIn("429=5", joined)
        self.assertIn("Last error: HTTP 429", joined)


if __name__ == "__main__":
    unittest.main()

