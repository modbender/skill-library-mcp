import json
import os
import subprocess
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PARSER = os.path.join(SCRIPT_DIR, "parse-stream.py")


class ParseStreamResultFullTextTests(unittest.TestCase):
    def test_result_text_is_not_truncated(self):
        # Guard against regressions where the parser clips completion/result text.
        long_result = "RESULT_BEGIN\n" + ("x" * 5000) + "\nRESULT_END"
        evt = {
            "type": "result",
            "is_error": False,
            "duration_ms": 1234,
            "total_cost_usd": 0,
            "result": long_result,
            "num_turns": 1,
        }

        env = dict(os.environ)
        env["PLATFORM"] = "test"
        env["CODEFLOW_SAFE_MODE"] = "false"
        env.pop("RELAY_DIR", None)

        proc = subprocess.run(
            ["python3", PARSER],
            input=json.dumps(evt) + "\n",
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

        self.assertTrue(posts, msg="No posts captured from parse-stream.py")
        joined = "\n".join(posts)
        self.assertIn("RESULT_BEGIN", joined)
        self.assertIn("RESULT_END", joined)
        self.assertIn(long_result, joined)


if __name__ == "__main__":
    unittest.main()
