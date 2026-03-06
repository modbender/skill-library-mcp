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


class ParseStreamOutputModeAndWindowTests(unittest.TestCase):
    def test_state_card_is_strict_snapshot_overwrite_not_cumulative(self):
        events = [
            {"type": "thread.started", "thread_id": "t123"},
            {"type": "turn.started"},
        ]
        for i in range(5):
            events.append(
                {
                    "type": "item.completed",
                    "item": {
                        "type": "file_change",
                        "file_path": f"f{i}.txt",
                        "change_type": "created",
                    },
                }
            )
        events.append(
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2},
            }
        )

        out = _run_parser(
            events,
            env_overrides={
                "PLATFORM": "test",
                "CODEFLOW_SAFE_MODE": "false",
                "CODEFLOW_COMPACT": "true",
                "CODEFLOW_OUTPUT_MODE": "balanced",
            },
        )

        # Two anchors (thinking/cmd) then multiple edits to cmd anchor (message_id=2).
        edits = [o for o in out if o.get("op") == "edit_single" and int(o.get("message_id") or 0) == 2]
        self.assertTrue(edits, msg="Expected edit_single outputs for cmd state card")

        last = edits[-1].get("text", "")
        self.assertIn("🖥️ Round 1 commands / results", last)
        # Under platform=test, no truncation should happen.
        self.assertNotIn("…(truncated)", last)
        # Strict snapshot overwrite: only the latest update should be displayed.
        self.assertNotIn("📝 Created `f0.txt`", last)
        self.assertNotIn("📝 Created `f1.txt`", last)
        self.assertNotIn("📝 Created `f2.txt`", last)
        self.assertNotIn("📝 Created `f3.txt`", last)
        self.assertIn("📝 Created `f4.txt`", last)

    def test_nonzero_exit_code_warning_includes_cmd_and_code_with_redaction(self):
        secret = "ghp_abcdefghijklmnopqrstuvwxyz0123456789"
        cmd = f"do --token={secret} --flag=x"
        events = [
            {"type": "thread.started", "thread_id": "t123"},
            {"type": "turn.started"},
            {"type": "item.started", "item": {"type": "command_execution", "command": cmd}},
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": cmd,
                    "output": "",
                    "exit_code": 7,
                },
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2},
            },
        ]

        out = _run_parser(
            events,
            env_overrides={
                "PLATFORM": "test",
                "CODEFLOW_SAFE_MODE": "true",
                "CODEFLOW_COMPACT": "true",
                "CODEFLOW_OUTPUT_MODE": "balanced",
            },
        )

        warnings = [o for o in out if o.get("op") == "post" and "⚠️cmd:" in (o.get("text") or "")]
        self.assertTrue(warnings, msg="Expected a warning post containing cmd + exit code")
        text = warnings[-1].get("text") or ""

        self.assertIn("⚠️cmd:", text)
        self.assertIn("⚠️Exit code: 7", text)
        self.assertLess(text.find("⚠️cmd:"), text.find("⚠️Exit code:"))

        # Safe mode uses strict redaction: secret flag values must be redacted.
        self.assertNotIn(secret, text)
        self.assertIn("[REDACTED]", text)

    def test_probe_exit_code_is_downgraded_to_debug_and_not_warned_in_balanced(self):
        cmd = "cd repo && rg -n needle file.txt"
        events = [
            {"type": "thread.started", "thread_id": "t123"},
            {"type": "turn.started"},
            {"type": "item.started", "item": {"type": "command_execution", "command": cmd}},
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": cmd,
                    "output": "",
                    "exit_code": 1,
                },
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2},
            },
        ]

        out = _run_parser(
            events,
            env_overrides={
                "PLATFORM": "test",
                "CODEFLOW_SAFE_MODE": "false",
                "CODEFLOW_COMPACT": "true",
                "CODEFLOW_OUTPUT_MODE": "balanced",
            },
        )

        warnings = [o for o in out if o.get("op") == "post" and "⚠️Exit code:" in (o.get("text") or "")]
        self.assertFalse(warnings, msg="Probe-style exit=1 should not emit warning in balanced mode")

    def test_probe_exit_code_is_downgraded_when_wrapped_in_bash_lc(self):
        cmd = 'bash -lc "cd repo && rg -n needle file.txt"'
        events = [
            {"type": "thread.started", "thread_id": "t123"},
            {"type": "turn.started"},
            {"type": "item.started", "item": {"type": "command_execution", "command": cmd}},
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": cmd,
                    "output": "",
                    "exit_code": 1,
                },
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2},
            },
        ]

        out = _run_parser(
            events,
            env_overrides={
                "PLATFORM": "test",
                "CODEFLOW_SAFE_MODE": "false",
                "CODEFLOW_COMPACT": "true",
                "CODEFLOW_OUTPUT_MODE": "balanced",
            },
        )

        warnings = [o for o in out if o.get("op") == "post" and "⚠️Exit code:" in (o.get("text") or "")]
        self.assertFalse(warnings, msg="Wrapped probe cmd exit=1 should not emit warning in balanced mode")

    def test_probe_exit_code_debug_is_visible_in_verbose(self):
        cmd = "rg -n needle file.txt"
        events = [
            {"type": "thread.started", "thread_id": "t123"},
            {"type": "turn.started"},
            {"type": "item.started", "item": {"type": "command_execution", "command": cmd}},
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": cmd,
                    "output": "",
                    "exit_code": 1,
                },
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2},
            },
        ]

        out = _run_parser(
            events,
            env_overrides={
                "PLATFORM": "test",
                "CODEFLOW_SAFE_MODE": "false",
                "CODEFLOW_COMPACT": "true",
                "CODEFLOW_OUTPUT_MODE": "verbose",
            },
        )

        debugs = [o for o in out if o.get("op") == "post" and "🔎 probe cmd:" in (o.get("text") or "")]
        self.assertTrue(debugs, msg="Expected downgraded debug post in verbose mode")
        self.assertIn("exit code: 1", (debugs[-1].get("text") or ""))

    def test_wrapped_probe_exit_code_debug_is_visible_in_verbose(self):
        cmd = "sh -c 'test -f missing.txt'"
        events = [
            {"type": "thread.started", "thread_id": "t123"},
            {"type": "turn.started"},
            {"type": "item.started", "item": {"type": "command_execution", "command": cmd}},
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": cmd,
                    "output": "",
                    "exit_code": 1,
                },
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2},
            },
        ]

        out = _run_parser(
            events,
            env_overrides={
                "PLATFORM": "test",
                "CODEFLOW_SAFE_MODE": "false",
                "CODEFLOW_COMPACT": "true",
                "CODEFLOW_OUTPUT_MODE": "verbose",
            },
        )

        debugs = [o for o in out if o.get("op") == "post" and "🔎 probe cmd:" in (o.get("text") or "")]
        self.assertTrue(debugs, msg="Expected downgraded debug post for wrapped probe cmd in verbose mode")
        self.assertIn("exit code: 1", (debugs[-1].get("text") or ""))

    def test_wrapped_non_probe_nonzero_still_warns(self):
        cmd = 'bash -lc "do --flag=x"'
        events = [
            {"type": "thread.started", "thread_id": "t123"},
            {"type": "turn.started"},
            {"type": "item.started", "item": {"type": "command_execution", "command": cmd}},
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": cmd,
                    "output": "",
                    "exit_code": 7,
                },
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2},
            },
        ]

        out = _run_parser(
            events,
            env_overrides={
                "PLATFORM": "test",
                "CODEFLOW_SAFE_MODE": "false",
                "CODEFLOW_COMPACT": "true",
                "CODEFLOW_OUTPUT_MODE": "balanced",
            },
        )

        warnings = [o for o in out if o.get("op") == "post" and "⚠️Exit code: 7" in (o.get("text") or "")]
        self.assertTrue(warnings, msg="Non-probe nonzero exit must still emit warning when wrapped")

    def test_diff_exit_1_with_output_is_downgraded_in_balanced(self):
        cmd = "diff -u a b"
        events = [
            {"type": "thread.started", "thread_id": "t123"},
            {"type": "turn.started"},
            {"type": "item.started", "item": {"type": "command_execution", "command": cmd}},
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": cmd,
                    "output": "--- a\\n+++ b\\n@@\\n-1\\n+2\\n",
                    "exit_code": 1,
                },
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2},
            },
        ]

        out = _run_parser(
            events,
            env_overrides={
                "PLATFORM": "test",
                "CODEFLOW_SAFE_MODE": "false",
                "CODEFLOW_COMPACT": "true",
                "CODEFLOW_OUTPUT_MODE": "balanced",
            },
        )

        warnings = [o for o in out if o.get("op") == "post" and "⚠️Exit code:" in (o.get("text") or "")]
        self.assertFalse(warnings, msg="diff exit=1 (differences) should not emit warning in balanced mode")

    def test_output_modes_minimal_balanced_verbose(self):
        events = [
            {"type": "thread.started", "thread_id": "t123"},
            {"type": "turn.started"},
            {
                "type": "item.completed",
                "item": {"type": "file_change", "file_path": "a.txt", "change_type": "created"},
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2},
            },
        ]

        base_env = {
            "PLATFORM": "test",
            "CODEFLOW_SAFE_MODE": "false",
            "CODEFLOW_COMPACT": "true",
        }

        out_min = _run_parser(events, env_overrides={**base_env, "CODEFLOW_OUTPUT_MODE": "minimal"})
        out_bal = _run_parser(events, env_overrides={**base_env, "CODEFLOW_OUTPUT_MODE": "balanced"})
        out_ver = _run_parser(events, env_overrides={**base_env, "CODEFLOW_OUTPUT_MODE": "verbose"})

        # minimal: no state anchors/edits, only the final post.
        self.assertFalse(any(o.get("op") in {"post_single", "edit_single"} for o in out_min))
        self.assertTrue(any("✅ Round" in (o.get("text") or "") for o in out_min if o.get("op") == "post"))

        # balanced: has state anchors/edits and final.
        self.assertTrue(any(o.get("op") == "post_single" for o in out_bal))
        self.assertTrue(any(o.get("op") == "edit_single" for o in out_bal))
        self.assertTrue(any("✅ Round" in (o.get("text") or "") for o in out_bal if o.get("op") == "post"))

        # verbose: includes extra per-update posts (in addition to balanced).
        posts_bal = [o for o in out_bal if o.get("op") == "post"]
        posts_ver = [o for o in out_ver if o.get("op") == "post"]
        self.assertGreater(len(posts_ver), len(posts_bal))


if __name__ == "__main__":
    unittest.main()
