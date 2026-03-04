import os
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in os.sys.path:
    os.sys.path.insert(0, SCRIPT_DIR)

import restart  # noqa: E402


class RestartRuntimeHelperTests(unittest.TestCase):
    def test_find_lsof_bin_prefers_shutil_which(self):
        original_which = restart.shutil.which
        original_isfile = restart.os.path.isfile
        original_access = restart.os.access
        try:
            restart.shutil.which = lambda name: "/mock/lsof" if name == "lsof" else None
            restart.os.path.isfile = lambda p: p == "/mock/lsof"
            restart.os.access = lambda p, _mode: p == "/mock/lsof"
            got = restart.find_lsof_bin()
        finally:
            restart.shutil.which = original_which
            restart.os.path.isfile = original_isfile
            restart.os.access = original_access
        self.assertEqual(got, "/mock/lsof")

    def test_find_lsof_bin_falls_back_to_system_path(self):
        original_which = restart.shutil.which
        original_isfile = restart.os.path.isfile
        original_access = restart.os.access
        try:
            restart.shutil.which = lambda _name: None

            def fake_isfile(path):
                return path == "/usr/sbin/lsof"

            restart.os.path.isfile = fake_isfile
            restart.os.access = lambda p, _mode: p == "/usr/sbin/lsof"
            got = restart.find_lsof_bin()
        finally:
            restart.shutil.which = original_which
            restart.os.path.isfile = original_isfile
            restart.os.access = original_access
        self.assertEqual(got, "/usr/sbin/lsof")

    def test_report_trigger_failure_uses_origin_or_main_session(self):
        original_send = restart.send_agent_message
        calls = []

        def fake_send(_oc_bin, session_key, message):
            calls.append((session_key, message))
            return True, "accepted"

        restart.send_agent_message = fake_send
        try:
            ok, note = restart.report_trigger_failure_to_origin(
                oc_bin="openclaw",
                origin_session_key="",
                restart_id="rg-unit",
                detail="cli failed",
            )
        finally:
            restart.send_agent_message = original_send

        self.assertTrue(ok)
        self.assertEqual(note, "accepted")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], restart.DEFAULT_MAIN_SESSION)
        self.assertIn("restart_id: rg-unit", calls[0][1])
        self.assertIn("error_code: TRIGGER_FAILED", calls[0][1])


if __name__ == "__main__":
    unittest.main()
