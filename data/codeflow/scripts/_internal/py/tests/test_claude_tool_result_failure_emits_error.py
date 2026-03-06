import json
import os
import subprocess
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PARSER = os.path.join(SCRIPT_DIR, "parse-stream.py")


def _run_parser(events: list[dict], *, env_overrides: dict[str, str]) -> list[dict]:
    env = dict(os.environ)
    env.update(env_overrides)
    env.pop("RELAY_DIR", None)

    inp = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events)
    proc = subprocess.run(
        ["python3", PARSER],
        input=inp,
        capture_output=True,
        text=True,
        env=env,
    )
    if proc.returncode != 0:
        raise AssertionError(proc.stderr)

    out: list[dict] = []
    for line in proc.stdout.splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


class ClaudeToolResultFailureEmitsErrorTests(unittest.TestCase):
    def test_bash_tool_result_is_error_emits_error_post(self):
        events = [
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {"type": "tool_use", "name": "Bash", "input": {"command": "false"}}
                    ]
                },
            },
            {
                "type": "user",
                "message": {
                    "content": [
                        {
                            "type": "tool_result",
                            "is_error": True,
                            "content": [{"type": "text", "text": "exit status 1"}],
                        }
                    ]
                },
            },
        ]

        out = _run_parser(
            events,
            env_overrides={
                "PLATFORM": "test",
                "CODEFLOW_SAFE_MODE": "false",
                "CODEFLOW_OUTPUT_MODE": "minimal",
            },
        )

        errors = [
            o
            for o in out
            if o.get("op") == "post"
            and "❌" in (o.get("text") or "")
            and "Bash failed" in (o.get("text") or "")
        ]
        self.assertTrue(errors, msg="Expected an explicit error post for is_error tool_result")

    def test_safe_mode_suppresses_failure_details(self):
        events = [
            {
                "type": "assistant",
                "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "false"}}]},
            },
            {
                "type": "user",
                "message": {
                    "content": [
                        {
                            "type": "tool_result",
                            "is_error": True,
                            "content": [{"type": "text", "text": "SENSITIVE TOKEN=abc"}],
                        }
                    ]
                },
            },
        ]

        out = _run_parser(
            events,
            env_overrides={
                "PLATFORM": "test",
                "CODEFLOW_SAFE_MODE": "true",
                "CODEFLOW_OUTPUT_MODE": "minimal",
            },
        )

        text = "\n".join((o.get("text") or "") for o in out if o.get("op") == "post")
        self.assertIn("Bash failed", text)
        self.assertIn("details suppressed", text)
        self.assertNotIn("SENSITIVE", text)


if __name__ == "__main__":
    unittest.main()

