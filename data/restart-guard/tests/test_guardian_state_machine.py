import os
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


class GuardianStateMachineTests(unittest.TestCase):
    def test_success_invariant(self):
        self.assertTrue(guardian.is_restart_successful(True, True, True))
        self.assertFalse(guardian.is_restart_successful(False, True, True))
        self.assertFalse(guardian.is_restart_successful(True, False, True))
        self.assertFalse(guardian.is_restart_successful(True, True, False))

    def test_wait_for_down_detects_transition(self):
        seq = [True, True, False]
        original = guardian.check_health

        def fake_health(_oc_bin, _host, _port):
            return seq.pop(0) if seq else False

        guardian.check_health = fake_health
        try:
            clock = _FakeClock()
            ok, note = guardian.wait_for_down(
                oc_bin="openclaw",
                host="127.0.0.1",
                port="18789",
                timeout_ms=5000,
                poll_interval_s=0.1,
                now_fn=clock.now,
                sleep_fn=clock.sleep,
            )
        finally:
            guardian.check_health = original
        self.assertTrue(ok)
        self.assertIn("down observed", note)

    def test_wait_for_up_requires_streak(self):
        seq = [True, False, True, True]
        original = guardian.check_health

        def fake_health(_oc_bin, _host, _port):
            return seq.pop(0) if seq else True

        guardian.check_health = fake_health
        try:
            clock = _FakeClock()
            ok, note = guardian.wait_for_up_healthy(
                oc_bin="openclaw",
                host="127.0.0.1",
                port="18789",
                timeout_ms=5000,
                poll_interval_s=0.1,
                success_streak=2,
                now_fn=clock.now,
                sleep_fn=clock.sleep,
            )
        finally:
            guardian.check_health = original
        self.assertTrue(ok)
        self.assertIn("streak=2", note)

    def test_wait_for_up_timeout(self):
        original = guardian.check_health
        guardian.check_health = lambda _oc_bin, _host, _port: False
        try:
            clock = _FakeClock()
            ok, note = guardian.wait_for_up_healthy(
                oc_bin="openclaw",
                host="127.0.0.1",
                port="18789",
                timeout_ms=1000,
                poll_interval_s=0.1,
                success_streak=2,
                now_fn=clock.now,
                sleep_fn=clock.sleep,
            )
        finally:
            guardian.check_health = original
        self.assertFalse(ok)
        self.assertIn("timeout", note)


if __name__ == "__main__":
    unittest.main()
