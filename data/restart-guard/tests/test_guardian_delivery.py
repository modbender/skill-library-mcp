import os
import tempfile
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in os.sys.path:
    os.sys.path.insert(0, SCRIPT_DIR)

import guardian  # noqa: E402


class _FakeClock:
    def __init__(self):
        self.t = 0.0

    def now(self):
        return self.t

    def sleep(self, sec):
        self.t += max(0.01, sec)


class GuardianDeliveryTests(unittest.TestCase):
    def test_delivery_prefers_origin(self):
        original_send = guardian.send_agent_message
        original_notify = guardian.notify_with_result

        calls = []

        def fake_send(_oc_bin, session_key, _message):
            calls.append(session_key)
            return True, "ok"

        guardian.send_agent_message = fake_send
        guardian.notify_with_result = lambda *_args, **_kwargs: {"ok": False, "attempted": [], "succeeded": []}
        try:
            event = {
                "event_type": "restart_guard.result.v1",
                "status": "ok",
                "severity": "info",
                "restart_id": "rg-x",
                "note": "ok",
            }
            result = guardian.deliver_result_with_budget(
                oc_bin="openclaw",
                origin_session_key="agent:main:webui:1",
                event=event,
                runtime_notif={},
                full_config={},
                retry_budget_ms=2000,
                retry_interval_ms=100,
                now_fn=_FakeClock().now,
                sleep_fn=_FakeClock().sleep,
            )
        finally:
            guardian.send_agent_message = original_send
            guardian.notify_with_result = original_notify

        self.assertTrue(result["ok"])
        self.assertEqual(result["via"], "agent")
        self.assertEqual(calls, ["agent:main:webui:1"])
        self.assertEqual(result["attempts"], 1)

    def test_delivery_falls_back_to_external(self):
        original_send = guardian.send_agent_message
        original_notify = guardian.notify_with_result
        send_calls = []

        def fake_send(_oc_bin, session_key, _message):
            send_calls.append(session_key)
            return False, "down"

        guardian.send_agent_message = fake_send
        guardian.notify_with_result = lambda *_args, **_kwargs: {
            "ok": True,
            "attempted": ["telegram", "feishu"],
            "succeeded": ["telegram"],
        }
        try:
            event = {
                "event_type": "restart_guard.result.v1",
                "status": "fail",
                "severity": "critical",
                "restart_id": "rg-y",
                "note": "fail",
            }
            result = guardian.deliver_result_with_budget(
                oc_bin="openclaw",
                origin_session_key="agent:main:webui:1",
                event=event,
                runtime_notif={"channels": ["telegram"]},
                full_config={"notification": {"channels": ["telegram", "feishu"]}},
                retry_budget_ms=2000,
                retry_interval_ms=100,
                now_fn=_FakeClock().now,
                sleep_fn=_FakeClock().sleep,
            )
        finally:
            guardian.send_agent_message = original_send
            guardian.notify_with_result = original_notify

        self.assertTrue(result["ok"])
        self.assertEqual(result["via"], "external_fallback")
        self.assertEqual(send_calls, ["agent:main:webui:1", "agent:main:main"])

    def test_delivery_budget_exhausted(self):
        original_send = guardian.send_agent_message
        original_notify = guardian.notify_with_result
        clock = _FakeClock()

        guardian.send_agent_message = lambda *_args, **_kwargs: (False, "down")
        guardian.notify_with_result = lambda *_args, **_kwargs: {
            "ok": False,
            "attempted": ["telegram"],
            "succeeded": [],
        }
        try:
            event = {
                "event_type": "restart_guard.result.v1",
                "status": "fail",
                "severity": "critical",
                "restart_id": "rg-z",
                "note": "fail",
            }
            result = guardian.deliver_result_with_budget(
                oc_bin="openclaw",
                origin_session_key="agent:main:webui:1",
                event=event,
                runtime_notif={"channels": ["telegram"]},
                full_config={"notification": {"channels": ["telegram"]}},
                retry_budget_ms=300,
                retry_interval_ms=100,
                now_fn=clock.now,
                sleep_fn=clock.sleep,
            )
        finally:
            guardian.send_agent_message = original_send
            guardian.notify_with_result = original_notify

        self.assertFalse(result["ok"])
        self.assertTrue(result["delivery_exhausted"])
        self.assertGreaterEqual(result["attempts"], 2)

    def test_resolve_external_channels_supports_legacy_string(self):
        channels = guardian.resolve_external_channels(
            runtime_notif={},
            full_config={"notification": {"channels": "telegram, feishu", "fallback": "telegram"}},
        )
        self.assertEqual(channels, ["telegram", "feishu"])

    def test_diagnostics_summary_redacts_secret_and_writes_file(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = {
                "generated_at": "2026-02-27T10:00:00+00:00",
                "failure_phase": "WAIT_UP_HEALTHY",
                "error_code": "WAIT_UP_TIMEOUT",
                "note": "token=abc123456",
                "health_summary": "probes=3 up=1 down=2",
                "commands": [
                    {
                        "command": "openclaw doctor --non-interactive",
                        "returncode": 1,
                        "summary": "api_key=abcdef",
                        "output": "api_key=abcdef",
                    }
                ],
            }
            context_path = os.path.join(td, "restart-context.md")
            md_path = guardian.write_diagnostics_bundle(context_path, "rg-diag", bundle)
            self.assertTrue(os.path.isfile(md_path))
            summary = guardian.summarize_diagnostics_bundle(bundle, md_path)
            self.assertIn("error_code=WAIT_UP_TIMEOUT", summary)
            self.assertIn("diagnostics_file=", summary)
            self.assertNotIn("abcdef", summary)
            self.assertIn("[REDACTED]", summary)


if __name__ == "__main__":
    unittest.main()
